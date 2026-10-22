from copy import deepcopy
from datetime import date
from decimal import Decimal

import pandas as pd
import pytest

from aqrp.core.canonical import canonical, digest
from aqrp.core.errors import ContractError
from aqrp.core.time import utc
from aqrp.data.store import read_snapshot
from aqrp.data.synthetic import load_synthetic
from aqrp.experiments.ledger import ExperimentLedger
from aqrp.research.pipeline import compose, pipeline
from aqrp.validation.approvals import record_decision
from aqrp.validation.evaluator import seal
from aqrp.validation.labels import CoverageRef, make_labels
from aqrp.validation.splits import purged_train


def scores():
    return pd.DataFrame(
        [
            dict(
                factor_key=key,
                security_id=str(i),
                session="2024-01-04",
                stage="final",
                score=value,
                decision_time="2024-01-04T12:05:00Z",
                available_at="2024-01-04T12:00:00Z",
            )
            for key, values in (("a", [1, 2, 3]), ("b", [3, 1, 2]))
            for i, value in enumerate(values)
        ]
    )


def spec():
    return dict(
        factor_keys=["a", "b"],
        weights=[1, 1],
        directions=[1, -1],
        direction_applied=False,
        normalization="cross_sectional_sample_z",
        input_stage="final",
        min_n=3,
        redundancy=None,
    )


@pytest.mark.parametrize("field", ["decision_time", "available_at"])
@pytest.mark.parametrize("entry", ["compose", "pipeline"])
def test_stage_clocks_are_required_and_null_is_not_visibility(field, entry):
    f = scores()
    config = (
        spec()
        if entry == "compose"
        else dict(clean={"method": "none"}, standardized={"method": "none"}, neutralize=False)
    )
    call = compose if entry == "compose" else pipeline
    with pytest.raises(ContractError, match="STAGE_CLOCK_REQUIRED"):
        call(f.drop(columns=field), config)
    f.loc[0, field] = None
    with pytest.raises(ContractError, match="AWARE_TIMESTAMP_REQUIRED"):
        call(f, config)


def test_composite_normalizes_clocks_preserves_lineage_and_input():
    f = scores()
    # Different representations of the same UTC instant are compatible.
    f.loc[f.factor_key == "b", "decision_time"] = "2024-01-04T20:05:00+08:00"
    f.loc[f.factor_key == "b", "available_at"] = "2024-01-04T12:05:00Z"
    original = f.copy(deep=True)
    out = compose(f, spec())
    pd.testing.assert_frame_equal(f, original)
    assert len(out["scores"]) == 3
    assert all(r["decision_time"] == utc("2024-01-04T12:05:00Z") for r in out["scores"])
    assert all(r["available_at"] == utc("2024-01-04T12:05:00Z") for r in out["scores"])
    assert out["lineage"][0]["input_hash"] == out["scores"][0]["input_hash"]
    altered = f.copy(deep=True)
    altered["score"] *= 2
    other = compose(altered, spec())
    assert [r["score"] for r in other["scores"]] == pytest.approx(
        [r["score"] for r in out["scores"]]
    )
    assert other["lineage"][0]["input_hash"] != out["lineage"][0]["input_hash"]
    with pytest.raises(ContractError, match="DUPLICATE_STAGE_SCORE"):
        compose(pd.concat([f, f.iloc[:1]], ignore_index=True), spec())
    second = f.assign(session="2024-01-05", decision_time="2024-01-05T12:05:00Z")
    assert len(compose(pd.concat([f, second]), spec())["lineage"]) == 2


@pytest.mark.parametrize("field", ["listing_at", "delisting_at"])
def test_late_master_eligibility_and_fit_cutoff_boundary(make_snapshot, field):
    tables = load_synthetic(sessions=[(date(2024, 1, d), "12:00:00") for d in (2, 3, 4, 5)])
    for bar in tables["bars_daily"]:
        price = Decimal(100 if bar["session_date"].day == 3 else 110)
        bar.update({k: price for k in ("open", "high", "low", "close")})
        bar.update(amount=price * bar["volume"], source_amount=str(price * bar["volume"]))
    old = tables["security_master"][0]
    old[field] = utc("2024-01-04T08:00:00Z")
    revision = deepcopy(old)
    late = utc("2024-01-05T00:00:00Z")
    revision.update(revision_id=2, event_time=late, available_at=late, known_at=late)
    revision[field] = utc("2024-01-01T00:00:00Z") if field == "listing_at" else None
    tables["security_master"].append(revision)
    snapshot = make_snapshot(tables)
    coverage = CoverageRef.create(
        snapshot.manifest_hash,
        [
            dict(
                coverage_id="jan4",
                event_time="2024-01-04T12:00:00Z",
                available_at="2024-01-04T12:05:00Z",
                complete_through="2024-01-04T12:00:00Z",
                revision_id=1,
            )
        ],
        authority="public-unit-fixture",
        scope="PUBLIC_ENGINEERING",
    )
    decisions = [dict(session=date(2024, 1, 2), decision_time="2024-01-02T12:05:00Z")]
    early = make_labels(snapshot, decisions, ["SYN_A:001"], [1], "2024-01-04T12:10:00Z", coverage)[
        0
    ]
    after = make_labels(snapshot, decisions, ["SYN_A:001"], [1], "2024-01-05T12:10:00Z", coverage)[
        0
    ]
    assert early["label"] is None
    assert after["label"] == 0.1 and after["available_at"] == late
    assert after["information_interval"][1] == late
    assert after["security_master_ref"]["revision_id"] == 2
    # The reference binds the P1-published row (including normalized field
    # representation), not the pre-ingress Python fixture dictionary.
    _, published = read_snapshot(snapshot)
    selected = next(
        r
        for r in published["security_master"].to_pylist()
        if r["security_id"] == "SYN_A:001" and r["revision_id"] == 2
    )
    assert after["security_master_ref"]["row_hash"] == digest(selected)
    for cutoff in ("2024-01-04T12:10:00Z", "2024-01-04T23:59:59.999999Z"):
        split = purged_train(
            [after], ("2024-01-02", "2024-01-03"), ("2024-01-05", "2024-01-06"), cutoff, [], 0
        )
        assert not split["train"]
        assert split["rejected"][0]["split_reason"] == "LABEL_NOT_AVAILABLE_AT_FIT"
    assert (
        len(
            purged_train(
                [after], ("2024-01-02", "2024-01-03"), ("2024-01-05", "2024-01-06"), late, [], 0
            )["train"]
        )
        == 1
    )


@pytest.mark.parametrize("mode", ["list", "mismatch", "changed_after_verify"])
def test_approval_reads_only_manifest_bound_bytes(tmp_path, monkeypatch, mode):
    ledger = ExperimentLedger(tmp_path)
    # Synthetic proposal/signing fixture tests membership only, not real approval.
    p = {"eligible": True, "candidate": "PUBLIC_FIXTURE"}
    run = ledger.start(
        {},
        dict(
            code_commit="a" * 40,
            code_bundle="b" * 64,
            data_hash="c" * 64,
            environment={},
            protocol_hash="d" * 64,
            permission_domain="PUBLIC_UNIT_FIXTURE",
            seed=17,
        ),
    )
    content = [p] if mode == "list" else {"fixture": p if mode != "mismatch" else {}}
    ledger.artifact(run, "approvals.json", content)
    original = ledger.finish(run, "SUCCEEDED")
    key = b"public-unit-signing-key-not-a-real-credential"
    envelope = seal(
        dict(proposal_hash=digest(p), human_actor="UNIT_NOT_APPROVAL", state="ResearchValidated"),
        key,
    )
    if mode == "changed_after_verify":

        def changed(_):
            (ledger.path(run) / "approvals.json").write_bytes(
                canonical({"fixture": p, "extra": {}})
            )
            return original

        monkeypatch.setattr(ledger, "verify", changed)
    with pytest.raises(ContractError, match="PROPOSAL_NOT_IN_IMMUTABLE_RUN"):
        record_decision(ledger, run, p, envelope, key)
    assert not (tmp_path / "decisions.jsonl").exists()
