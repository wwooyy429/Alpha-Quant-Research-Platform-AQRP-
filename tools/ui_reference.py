"""Independent byte/lineage and parity projection reader: stdlib only, no AQRP imports."""

import hashlib
import json
from copy import deepcopy
from pathlib import Path


def canonical(value):
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False
    ).encode()


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def verify_run(directory):
    directory = Path(directory).absolute()
    assert not any(p.is_symlink() or p.is_junction() for p in [directory, *directory.parents])
    previous = "0" * 64
    events = []
    for line in (directory / "events.jsonl").read_bytes().splitlines():
        event = json.loads(line)
        body = {k: v for k, v in event.items() if k != "hash"}
        assert (
            event["seq"] == len(events)
            and event["previous"] == previous
            and sha(canonical(body)) == event["hash"]
        )
        previous = event["hash"]
        events.append(event)
    raw = (directory / "manifest.json").read_bytes()
    m = json.loads(raw)
    assert m["run_id"] == directory.name and m["status"] == events[-1]["kind"] == "SUCCEEDED"
    assert (
        sha(raw) == events[-1]["payload"]["manifest_sha256"]
        and m["event_prefix_hash"] == events[-2]["hash"]
    )
    assert len({e["path"] for e in m["files"]}) == len(m["files"])
    for e in m["files"]:
        path = directory / e["path"]
        assert (
            path.parent == directory
            and not path.is_symlink()
            and sha(path.read_bytes()) == e["sha256"]
        )
    return m


def portfolio_request(raw, research_root, research_id):
    value = json.loads(raw)
    x = deepcopy(value)
    r = Path(research_root) / research_id
    verify_run(r)
    for b in x["source"]["research_bindings"]:
        assert (
            b["run_id"] == research_id
            and Path(b["ledger_root"]).absolute() == Path(research_root).absolute()
        )
        assert b["manifest_sha256"] == sha((r / "manifest.json").read_bytes())
        assert b["artifact_sha256"] == sha((r / (b["stage"] + ".json")).read_bytes())
        b["run_id"] = "RESEARCH_RUN"
        b["ledger_root"] = "RESEARCH_ROOT"
        b["manifest_sha256"] = "VERIFIED_RESEARCH_MANIFEST"
    entries = [e for k, e in x["inputs"].items() if k != "scores"] + x["inputs"]["scores"]
    for envelope in entries:
        original_ref = envelope["ref"]
        old_hash = envelope["content_sha256"]
        assert old_hash == sha(
            canonical({k: v for k, v in envelope.items() if k != "content_sha256"})
        )
        assert value["source"]["fixture_manifest"][original_ref] == old_hash
        if envelope["kind"] == "scores":
            assert (
                original_ref
                == f"p3-{research_id}-{envelope['data']['stage']}-{envelope['data']['factor_key']}"
            )
            envelope["ref"] = f"SCORE:{envelope['data']['stage']}:{envelope['data']['factor_key']}"
        envelope["content_sha256"] = sha(
            canonical({k: v for k, v in envelope.items() if k != "content_sha256"})
        )
    x["source"]["fixture_manifest"] = {e["ref"]: e["content_sha256"] for e in entries}
    return x


def actor(research_root, research_id, backtest_root, backtest_id):
    """Only explicitly proven run/root-derived fields are mapped; numeric fields are exact."""
    r = Path(research_root) / research_id
    b = Path(backtest_root) / backtest_id
    rm, bm = verify_run(r), verify_run(b)
    result = json.loads((b / "result.json").read_bytes())
    config = json.loads((b / "config.json").read_bytes())
    raw = bytes.fromhex(config["raw_request_hex"])
    assert sha(raw) == config["request_sha256"] == result["request_sha256"]
    mappings = []
    risk_projections = []
    order_bindings = {}
    lineage = json.loads((b / "portfolio-lineage.json").read_bytes())
    expected_decisions = json.loads(raw)["decisions"]
    assert len(lineage) == len(expected_decisions)
    for entry in lineage:
        index = entry["index"]
        returned = entry["result"]
        p = b / "portfolio-runs" / returned["run_id"]
        pm = verify_run(p)
        original = json.loads((p / "result.json").read_bytes())
        assert {k: v for k, v in returned.items() if k != "manifest"} == original and returned[
            "manifest"
        ] == pm
        request_raw = entry["request_utf8"].encode()
        normalized = portfolio_request(request_raw, research_root, research_id)
        original_source = json.loads(expected_decisions[index]["portfolio_request_utf8"])
        assert all(
            v["run_id"] == research_id for v in original_source["source"]["research_bindings"]
        )
        request_hash = sha(request_raw)
        normalized_hash = sha(canonical(normalized))
        pconfig = json.loads((p / "config.json").read_bytes())
        assert (
            bytes.fromhex(pconfig["raw_request_hex"]) == request_raw
            and pconfig["request_sha256"] == request_hash == original["request_hash"]
        )
        candidate_raw = (p / "candidate.json").read_bytes()
        risk = json.loads((p / "risk.json").read_bytes())
        target = deepcopy(original["target"])
        assert (
            risk == original["risk"]
            and risk["request_hash"] == request_hash
            and risk["candidate_hash"] == sha(candidate_raw)
        )
        assert risk["content_sha256"] == sha(
            canonical({k: v for k, v in risk.items() if k != "content_sha256"})
        )
        assert (
            target["request_hash"] == request_hash and target["risk_hash"] == risk["content_sha256"]
        )
        assert target["content_sha256"] == sha(
            canonical({k: v for k, v in target.items() if k != "content_sha256"})
        )
        old_risk, old_target = risk["content_sha256"], target["content_sha256"]
        risk["request_hash"] = normalized_hash
        risk["content_sha256"] = sha(
            canonical({k: v for k, v in risk.items() if k != "content_sha256"})
        )
        target.update(request_hash=normalized_hash, risk_hash=risk["content_sha256"])
        target["content_sha256"] = sha(
            canonical({k: v for k, v in target.items() if k != "content_sha256"})
        )
        risk_projections.append(
            {
                "index": index,
                "request": normalized,
                "candidate": json.loads(candidate_raw),
                "risk": risk,
                "target": target,
                "selection": original["selection"],
                "rounding": original["rounding"],
                "status": original["status"],
                "scope": original["scope"],
                "financial_approval": original["financial_approval"],
                "executable": original["executable"],
            }
        )
        order_bindings[request_hash] = {
            "raw": request_raw.decode(),
            "risk": old_risk,
            "target": old_target,
            "normalized_request": canonical(normalized).decode(),
            "normalized_hash": normalized_hash,
            "normalized_risk": risk["content_sha256"],
            "normalized_target": target["content_sha256"],
        }
        mappings.append(
            {
                "index": index,
                "research_run": research_id,
                "research_manifest_sha256": sha((r / "manifest.json").read_bytes()),
                "backtest_run": backtest_id,
                "actual_P4_run": p.name,
                "actual_P4_manifest_sha256": sha((p / "manifest.json").read_bytes()),
                "original_adapted_hash": request_hash,
                "normalized_adapted_hash": normalized_hash,
            }
        )
    orders = deepcopy(result["orders"])
    for order in orders.values():
        bound = order_bindings[order["P4_request_sha256"]]
        assert (
            order["P4_request_utf8"] == bound["raw"]
            and order["P4_risk_sha256"] == bound["risk"]
            and order["P4_target_sha256"] == bound["target"]
        )
        order.update(
            P4_request_utf8=bound["normalized_request"],
            P4_request_sha256=bound["normalized_hash"],
            P4_risk_sha256=bound["normalized_risk"],
            P4_target_sha256=bound["normalized_target"],
        )
    projection = {
        k: result[k]
        for k in [
            "account",
            "positions",
            "fills",
            "journal",
            "liquidations",
            "valuations",
            "fragments",
            "reconciliation",
            "performance",
            "scope",
            "financial_approval",
            "executable",
            "status",
        ]
    }
    projection.update(orders=orders, portfolios=risk_projections)
    return {
        "research_metrics": json.loads((r / "metrics.json").read_bytes()),
        "research_oos": json.loads((r / "oos.json").read_bytes()),
        "financial": projection,
        "mapping_proofs": mappings,
        "manifest_proofs": {"research": sha(canonical(rm)), "backtest": sha(canonical(bm))},
    }


def compare(a, b):
    return {
        "research_equal": canonical(a["research_metrics"]) == canonical(b["research_metrics"])
        and canonical(a["research_oos"]) == canonical(b["research_oos"]),
        "financial_exact_equal": canonical(a["financial"]) == canonical(b["financial"]),
        "mapping_a": a["mapping_proofs"],
        "mapping_b": b["mapping_proofs"],
        "whitelist": "Only exact verified research UUID/root/manifest and consequential score-envelope/request/risk/target hashes are canonically mapped. All quantities/cash buckets/order/fill/risk checks/costs/flags/times/Refs/snapshot IDs retained. No generic hash/lineage/error exclusion.",
    }
