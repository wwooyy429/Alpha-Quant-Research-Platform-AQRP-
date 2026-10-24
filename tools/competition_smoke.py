"""Actual offline adapter denial matrix; reuses preregistered P7 inputs, no new trial."""

import json
import sys
from pathlib import Path

from e2e_smoke import counts, read, save

from aqrp.competition import (
    AdapterSpec,
    adapt_engineering,
    adapter_spec,
    capabilities,
    input_reference,
)
from aqrp.core.canonical import canonical
from aqrp.core.errors import ContractError


def main():
    run = Path(sys.argv[1]).resolve()
    protocol = read(run / "e2e/PROTOCOL.json")
    root = Path(protocol["main"]["workspace"])
    before = counts(root)
    spec = adapter_spec(root)
    source = input_reference(root)
    draft = read(run / "e2e/requests/main-momentum-draft.json")
    rules = json.loads(spec.raw)["rules"]
    checked = []
    report = capabilities(spec, rules)
    assert report.runnable
    receipt = adapt_engineering(root, spec, source, draft, rules)
    assert receipt.raw == (run / "e2e/adapter-receipts/sdk-main-momentum.json").read_bytes()
    for name in rules:
        missing = {key: value for key, value in rules.items() if key != name}
        assert not capabilities(spec, missing).runnable
        try:
            adapt_engineering(root, spec, source, draft, missing)
        except ContractError as exc:
            assert exc.code == "ADAPTER_REQUIRED_RULE_NOT_SUPPORTED"
            checked.append({"case": "missing-" + name, "rejected": exc.code})
        else:
            raise AssertionError("Missing rule silently defaulted")
    for name, value in (
        ("provider", "unknown-provider"),
        ("live_orders", True),
        ("settlement", "T+0"),
        ("network", True),
        ("currency", "USD"),
        ("unit_mapping", "MULTIPLY_100"),
    ):
        changed = {**rules, name: value}
        assert not capabilities(spec, changed).runnable
        try:
            adapt_engineering(root, spec, source, draft, changed)
        except ContractError as exc:
            assert exc.code == "ADAPTER_REQUIRED_RULE_NOT_SUPPORTED"
            checked.append({"case": "conflict-" + name, "rejected": exc.code})
        else:
            raise AssertionError("Unsupported provider/rule accepted")
    for name in (
        "source_manifest_hash",
        "source_authority",
        "catalogue_revision",
        "code_bundle",
        "license_statement",
    ):
        body = json.loads(spec.raw)
        body[name] = "unreviewed"
        try:
            adapt_engineering(root, AdapterSpec(canonical(body)), source, draft, rules)
        except ContractError as exc:
            assert exc.code == "ADAPTER_INPUT_OR_SPEC_CHANGED"
            checked.append({"case": "identity-" + name, "rejected": exc.code})
        else:
            raise AssertionError("Caller identity replaced trusted catalogue")
    assert counts(root) == before
    output = run / "competition"
    output.mkdir()
    save(output / "spec.json", spec.raw)
    save(output / "capabilities.json", report.raw)
    save(output / "input-reference.json", source)
    result = {
        "status": "OFFLINE_ADAPTER_MATRIX_VERIFIED",
        "cases": checked,
        "actual_new_research": 0,
        "before": before,
        "after": counts(root),
        "financial_approval": "NONE",
        "formal_Test": "NOT RUN",
        "real_provider": "EXTERNAL_DEPENDENCY_BLOCKED",
        "live_orders": "NOT AUTHORIZED",
        "independent_G2": "PENDING",
    }
    save(output / "result.json", result)
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
