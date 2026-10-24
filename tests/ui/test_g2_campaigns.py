"""Preregistered search control: literal quotas, immutable hypotheses, no refunds."""

import json
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy

import pytest

from aqrp.core.canonical import canonical, digest
from aqrp.core.errors import ContractError
from aqrp.experiments.ledger import read_chain
from aqrp.services.task_campaigns import get_campaign
from aqrp.services.task_requests import catalogue, initialize
from aqrp.services.tasks import TaskService

SINGLE = {"start": "2024-01-06", "end": "2024-01-06", "horizons": [1]}


def service(root):
    initialize(root, "a" * 40)
    return TaskService(root)


def test_parameter_search_preregistered_once_and_shared_twelve_unit_budget(tmp_path):
    s = service(tmp_path)
    variants = [{**SINGLE, "lookback": i} for i in range(1, 15)]
    plan = s.register_campaign("fourteen-variants", variants)
    assert len(plan["variants"]) == 14 and plan["budget"] == 12
    assert not plan["registration_history"]["contaminated_before_registration"]
    configs = [s.freeze({**d, "campaign_id": plan["id"]}) for d in variants]
    families = [json.loads(x.raw)["payload"]["research"]["family"] for x in configs]
    assert len({x["id"] for x in families}) == 1
    assert all(x["definitions"] == families[0]["definitions"] for x in families)
    assert len(families[0]["hypotheses"]) == 14
    assert len(set(families[0]["hypotheses"])) == 14
    for i, frozen in enumerate(configs):
        r = s.submit(frozen, str(i))
        assert r["research_control"]["prior_reserved_units"] == i
        assert r["research_control"]["over_budget"] is (i >= 12)
        if i < 12:
            assert r["status"] == "QUEUED"
            assert s.cancel(r["task_id"]) == "CANCELLED"
        else:
            assert r["status"] == "FAILED" and r["error"] == "EXPERIMENT_BUDGET_EXCEEDED"
        assert s.submit(frozen, str(i))["task_id"] == r["task_id"]
    # A new plan does not replenish quota, and retains all14 prior reservations.
    late = s.register_campaign("late-plan", [SINGLE])
    assert late["registration_history"]["prior_reserved_task_attempts"] == 14
    assert late["registration_history"]["contaminated_before_registration"]
    refused = s.submit(s.freeze({**SINGLE, "campaign_id": "late-plan"}), "late")
    assert refused["status"] == "FAILED"
    assert refused["research_control"]["prior_reserved_units"] == 14
    assert refused["research_control"]["prior_other_campaign_attempts"] == 14
    assert len(s.list()) == 15
    assert not (tmp_path / "research-runs/trials.jsonl").exists()  # no invented core trials


@pytest.mark.parametrize(
    "change",
    [
        {"lookback": 3},
        {"direction": -1},
        {"neutralize": False},
        {"horizons": [3]},
        {"start": "2024-01-07", "end": "2024-01-07"},
    ],
)
def test_edit_cannot_automatically_open_another_family(tmp_path, change):
    s = service(tmp_path)
    old = s.freeze(SINGLE)
    plan = s.campaigns()[0]
    with pytest.raises(ContractError, match="UNREGISTERED_CAMPAIGN_VARIANT"):
        s.freeze({**SINGLE, **change})
    assert s.campaigns() == [plan]
    assert s.freeze(SINGLE).raw == old.raw


@pytest.mark.parametrize("name", [None, "../escape", "Upper", "", "x" * 65, 1])
def test_untrusted_plan_identifiers_refused(tmp_path, name):
    s = service(tmp_path)
    with pytest.raises(ContractError, match="INVALID_RESEARCH_CAMPAIGN_ID"):
        s.register_campaign(name, [SINGLE])


@pytest.mark.parametrize(
    "variants",
    [
        None,
        [],
        {},
        [SINGLE] * 65,
        [SINGLE, SINGLE],
        [{"source_task": "x"}],
        [{"kind": "replay"}],
        [{"campaign_id": "x"}],
    ],
)
def test_invalid_or_duplicate_candidate_sets_refused(tmp_path, variants):
    s = service(tmp_path)
    with pytest.raises(ContractError):
        s.register_campaign("study", variants)


def test_immutable_registration_tamper_partial_publication_and_missing_history(tmp_path):
    s = service(tmp_path)
    plan = s.register_campaign("study", [SINGLE])
    assert s.register_campaign("study", [SINGLE]) == plan
    with pytest.raises(ContractError, match="FAMILY_REDEFINED_AFTER_REGISTRATION"):
        s.register_campaign("study", [{**SINGLE, "lookback": 3}])
    cat = catalogue(tmp_path)
    path = tmp_path / "research-campaigns" / (digest("study") + ".json")
    original = path.read_bytes()
    changed = deepcopy(plan)
    changed["budget"] = 13
    changed["campaign_hash"] = digest({k: v for k, v in changed.items() if k != "campaign_hash"})
    path.write_bytes(canonical(changed))
    with pytest.raises(ContractError, match="RESEARCH_CAMPAIGN_IDENTITY_CHANGED"):
        get_campaign(tmp_path, "study", cat)
    path.write_bytes(original)
    index = tmp_path / "research-campaigns/index.jsonl"
    saved = index.read_bytes()
    index.write_bytes(b"")
    with pytest.raises(ContractError, match="RESEARCH_CAMPAIGN_NOT_REGISTERED"):
        s.freeze({**SINGLE, "campaign_id": "study"})
    with pytest.raises(ContractError, match="CAMPAIGN_REGISTRATION_INCOMPLETE"):
        s.register_campaign("study", [SINGLE])
    index.write_bytes(saved)
    frozen = s.freeze({**SINGLE, "campaign_id": "study"})
    task = s.submit(frozen, "attempt")["task_id"]
    with s.state.transaction() as c:
        c.execute("DELETE FROM campaign_attempts WHERE task=?", (task,))
    with pytest.raises(ContractError, match="CAMPAIGN_ATTEMPT_HISTORY_INCOMPLETE"):
        s.submit(frozen, "after-delete")


def test_actual_cross_campaign_trials_keep_history_and_contamination(tmp_path):
    s = service(tmp_path)
    early = s.register_campaign("early", [SINGLE])
    d = {**SINGLE, "campaign_id": early["id"]}
    one = s.submit(s.freeze(d), "one")
    assert s.work(one["task_id"])["status"] == "SUCCEEDED"
    late = s.register_campaign("late", [{**SINGLE, "lookback": 3}])
    assert late["registration_history"]["prior_research_trials"] == 1
    two = s.submit(s.freeze({**SINGLE, "lookback": 3, "campaign_id": "late"}), "two")
    assert two["research_control"]["prior_reserved_units"] == 1  # no double count of owned R
    assert s.work(two["task_id"])["status"] == "SUCCEEDED"
    multiplicity = json.loads(s.artifact(two["task_id"], "R", "multiplicity.json"))
    assert multiplicity["contaminated"]
    trials = read_chain(tmp_path / "research-runs/trials.jsonl")
    assert len(trials) == 2
    assert trials[1]["payload"]["cross_campaign_data_access"]
    assert trials[1]["payload"]["prior_data_attempts"] == 1
    assert trials[1]["payload"]["campaign_control"] == two["research_control"]


def test_all_declared_transformations_have_fixed_distinct_hypotheses(tmp_path):
    s = service(tmp_path)
    variants = [
        SINGLE,
        {**SINGLE, "direction": -1},
        {**SINGLE, "neutralize": False},
        {**SINGLE, "horizons": [1, 2]},
        {**SINGLE, "universe_id": "SYN_CORE4"},
    ]
    p = s.register_campaign("transformations", variants)
    families = [
        json.loads(s.freeze({**v, "campaign_id": p["id"]}).raw)["payload"]["research"]["family"]
        for v in variants
    ]
    assert len(families[0]["hypotheses"]) == 6  # 1+1+1+2+1
    assert all(x["definitions"] == families[0]["definitions"] for x in families)
    assert len(set(families[0]["definitions"].values())) == 6


def test_distinct_concurrent_submissions_cannot_overspend_data_quota(tmp_path):
    s = service(tmp_path)
    frozen = s.freeze(SINGLE)

    # A shared, already verified request; SQLite must serialize all16 reservations.
    def submit(i):
        return s.state.submit(
            frozen.raw, str(i), campaign=json.loads(frozen.raw)["payload"]["campaign"]
        )

    with ThreadPoolExecutor(max_workers=10) as pool:
        ids = list(pool.map(submit, range(16)))
    rows = [s.status(t) for t in ids]
    assert sum(r["status"] == "QUEUED" for r in rows) == 12
    assert sum(r["status"] == "FAILED" for r in rows) == 4
    assert sorted(r["research_control"]["prior_reserved_units"] for r in rows) == list(range(16))
    assert len(set(ids)) == 16


@pytest.mark.parametrize("damage", ["bytes", "missing", "sql-units", "sql-task-missing"])
def test_reserved_attempt_evidence_cannot_be_changed_or_forgiven(tmp_path, damage):
    s = service(tmp_path)
    f = s.freeze(SINGLE)
    task = s.submit(f, "one")["task_id"]
    path = tmp_path / "tasks" / task / "campaign-attempt.json"
    if damage == "bytes":
        path.write_bytes(path.read_bytes() + b" ")
    elif damage == "missing":
        path.unlink()
    else:
        with s.state.transaction() as c:
            if damage == "sql-units":
                c.execute("UPDATE campaign_attempts SET units=0 WHERE task=?", (task,))
            else:
                c.execute("DELETE FROM tasks WHERE id=?", (task,))
    with pytest.raises((ContractError, FileNotFoundError)):
        s.submit(f, "after-corruption")


def test_unknown_campaign_and_duplicate_index_are_refused(tmp_path):
    from aqrp.experiments.ledger import append_chain

    s = service(tmp_path)
    with pytest.raises(ContractError, match="RESEARCH_CAMPAIGN_NOT_REGISTERED"):
        s.freeze({**SINGLE, "campaign_id": "unknown"})
    p = s.register_campaign("study", [SINGLE])
    append_chain(
        tmp_path / "research-campaigns/index.jsonl",
        "CAMPAIGN_PREREGISTERED",
        {k: p[k] for k in ("id", "campaign_hash", "data_hash", "family_id")},
    )
    with pytest.raises(ContractError, match="DUPLICATE_RESEARCH_CAMPAIGN"):
        s.campaigns()
    with pytest.raises(ContractError, match="RESEARCH_CAMPAIGN_NOT_REGISTERED"):
        s.freeze({**SINGLE, "campaign_id": "study"})
