"""Immutable preregistered engineering campaigns, before any result is observed."""

import re
import sqlite3
from contextlib import closing
from copy import deepcopy

from aqrp.backtest.transactions import guard_path
from aqrp.core.canonical import canonical, digest
from aqrp.core.errors import ContractError
from aqrp.experiments.ledger import append_chain, immutable_write, mutex, read_chain
from aqrp.portfolio.contracts import load
from aqrp.services.research import hypotheses, hypothesis_definition

DEFAULT_CAMPAIGN = "engineering-default"
BUDGET = 12


def variant_key(config):
    return digest({k: v for k, v in config.items() if k != "family"})


def _paths(root, name):
    if type(name) is not str or not re.fullmatch(r"[a-z][a-z0-9_-]{0,63}", name):
        raise ContractError("INVALID_RESEARCH_CAMPAIGN_ID")
    directory = guard_path(root / "research-campaigns")
    return directory, directory / (digest(name) + ".json"), directory / "index.jsonl"


def history(root, data_hash):
    from aqrp.experiments.admission import BudgetAuthority

    authority = BudgetAuthority(root)
    if not authority.anchor.is_file() and (root / "catalog.json").exists():
        raise ContractError("ADMISSION_HISTORY_UNVERIFIED")
    if authority.anchor.is_file():
        # A single connection owns one stable authority snapshot. Registration
        # reads committed claims, including pending projections; it never mutates
        # or repairs the research history. The write-intent lock prevents a newer
        # projection from racing this snapshot's exact frozen-prefix validation.
        with closing(sqlite3.connect(authority.db, timeout=30, isolation_level=None)) as c:
            c.row_factory = sqlite3.Row
            c.execute("BEGIN IMMEDIATE")
            try:
                try:
                    shared = authority.history(c, data_hash)
                    registered_trials = c.execute(
                        "SELECT count(*) FROM trial_claims JOIN admissions ON trial_claims.admission_id=admissions.id WHERE admissions.data_hash=?",
                        (data_hash,),
                    ).fetchone()[0]
                except ContractError as exc:
                    if isinstance(exc.__cause__, sqlite3.DatabaseError):
                        raise exc.__cause__
                    raise
            finally:
                c.rollback()
        result = {
            "prior_research_trials": registered_trials,
            "prior_reserved_task_attempts": sum(
                a["owner_kind"] == "TASK" and bool(a["units"]) for a in shared["admissions"]
            ),
            "prior_legacy_admission_units": sum(
                len(a["units"]) for a in shared["admissions"] if a["owner_kind"] == "LEGACY"
            ),
            "prior_admitted_units": shared["admitted_units"],
            "prior_rejected_units": shared["rejected_units"],
        }
        result["contaminated_before_registration"] = any(result.values())
        return result
    rows = read_chain(guard_path(root / "research-runs/trials.jsonl"))
    result = {
        "prior_research_trials": sum(x["payload"].get("data_hash") == data_hash for x in rows),
        "prior_reserved_task_attempts": 0,
    }
    db = guard_path(root / "task-control/tasks.sqlite")
    if db.is_file():
        with closing(sqlite3.connect("file:" + db.as_posix() + "?mode=ro", uri=True)) as c:
            if c.execute("SELECT 1 FROM sqlite_master WHERE name='campaign_attempts'").fetchone():
                result["prior_reserved_task_attempts"] = c.execute(
                    "SELECT count(*) FROM campaign_attempts WHERE data_hash=?", (data_hash,)
                ).fetchone()[0]
    result["contaminated_before_registration"] = any(result.values())
    return result


def get_campaign(root, name, cat):
    _, path, index = _paths(root, name)
    entries = [x["payload"] for x in read_chain(index) if x["payload"]["id"] == name]
    if len(entries) != 1:
        raise ContractError("RESEARCH_CAMPAIGN_NOT_REGISTERED")
    raw = guard_path(path).read_bytes()
    record = load(raw)
    if (
        canonical(record) != raw
        or digest({k: v for k, v in record.items() if k != "campaign_hash"})
        != record["campaign_hash"]
        or entries[0] != {k: record[k] for k in ("id", "campaign_hash", "data_hash", "family_id")}
        or record["catalogue_revision"] != cat["revision"]
        or record["data_hash"] != cat["snapshot"]["manifest_hash"]
        or record["budget"] != BUDGET
    ):
        raise ContractError("RESEARCH_CAMPAIGN_IDENTITY_CHANGED")
    return record


def campaigns(root, cat):
    _, _, index = _paths(root, DEFAULT_CAMPAIGN)
    entries = read_chain(index)
    names = [x["payload"]["id"] for x in entries]
    if len(names) != len(set(names)):
        raise ContractError("DUPLICATE_RESEARCH_CAMPAIGN")
    return [get_campaign(root, name, cat) for name in names]


def register(root, name, configs, cat, *, automatic=False):
    directory, path, index = _paths(root, name)
    if not configs or len(configs) > 64:
        raise ContractError("INVALID_CAMPAIGN_VARIANTS")
    choices = {variant_key(c): deepcopy(c) for c in configs}
    if len(choices) != len(configs):
        raise ContractError("DUPLICATE_CAMPAIGN_VARIANT")
    directory.mkdir(exist_ok=True)
    with mutex(directory / ".registration-lock"):
        entries = read_chain(index)
        if any(x["payload"]["id"] == name for x in entries):
            old = get_campaign(root, name, cat)
            if set(old["variants"]) != set(choices):
                raise ContractError("FAMILY_REDEFINED_AFTER_REGISTRATION")
            return old
        if path.exists():
            raise ContractError("CAMPAIGN_REGISTRATION_INCOMPLETE")
        data_hash = cat["snapshot"]["manifest_hash"]
        prior = history(root, data_hash)
        if automatic and prior["contaminated_before_registration"]:
            raise ContractError("EXPLICIT_CAMPAIGN_REQUIRED_AFTER_DATA_ACCESS")
        identity = digest(
            {
                "id": name,
                "catalogue": cat["revision"],
                "variants": sorted(choices),
                "budget": BUDGET,
                "history": prior,
            }
        )
        family_id = "ui-campaign-" + identity
        declarations = []
        for key, c in sorted(choices.items()):
            originals = hypotheses({**c, "family": {}})
            aliases = {h["hypothesis"]: key + "::" + h["hypothesis"] for h in originals}
            declarations.extend(aliases.values())
            c["family"] = {
                "id": family_id,
                "budget": BUDGET,
                "method": "holm",
                "campaign": {
                    "id": name,
                    "identity": identity,
                    "data_hash": data_hash,
                    "registration_history": prior,
                },
                "hypothesis_aliases": aliases,
            }
        declarations = sorted(declarations)
        definitions = {}
        for c in choices.values():
            c["family"]["hypotheses"] = declarations
            for h in hypotheses(c):
                definitions[h["hypothesis"]] = hypothesis_definition(
                    h, c, data_hash, cat["exposures"]["manifest_hash"], cat["coverage"]["checksum"]
                )
        for c in choices.values():
            c["family"]["definitions"] = definitions
        record = {
            "schema": "engineering-research-campaign/1",
            "id": name,
            "catalogue_revision": cat["revision"],
            "data_hash": data_hash,
            "family_id": family_id,
            "budget": BUDGET,
            "budget_scope": "Shared data identity within this workspace, all campaigns and reserved failed/cancelled tasks; no refunds",
            "registration_history": prior,
            "variants": choices,
            "registration": "FIRST_USE_PREREGISTRATION"
            if automatic
            else "EXPLICIT_PREREGISTRATION",
        }
        record["campaign_hash"] = digest(record)
        immutable_write(path, canonical(record))
        append_chain(
            index,
            "CAMPAIGN_PREREGISTERED",
            {k: record[k] for k in ("id", "campaign_hash", "data_hash", "family_id")},
        )
    return get_campaign(root, name, cat)


def default_variants(config, cat):
    """Finite, disclosed catalogue variants, frozen once; never inferred from later edits."""
    from dataclasses import asdict

    from aqrp.factors.admission import builtin_spec

    result = {}
    selections = [[c["ref"]["factor_id"] for c in config["candidates"]]]
    selections += [[s["factor_id"]] for s in cat["factor_specs"]]
    for names in selections:
        for horizons in (config["horizons"], [1], [1, 2]):
            for pool in cat["universes"].values():
                c = deepcopy(config)
                first = c["candidates"][0]
                c["candidates"] = [
                    {
                        "ref": asdict(builtin_spec(n).ref),
                        "parameters": deepcopy(first["parameters"]),
                        "direction": first["direction"],
                        "hypothesis": n,
                    }
                    for n in names
                ]
                c["horizons"] = horizons
                c["universe_id"] = pool["universe_id"]
                c["universe_ref"] = pool
                result[variant_key(c)] = c
    return list(result.values())


def resolve(root, name, config, cat):
    name = DEFAULT_CAMPAIGN if name is None else name
    _, path, index = _paths(root, name)
    if (
        name == DEFAULT_CAMPAIGN
        and not path.exists()
        and not any(x["payload"]["id"] == name for x in read_chain(index))
    ):
        register(root, name, default_variants(config, cat), cat, automatic=True)
    record = get_campaign(root, name, cat)
    key = variant_key(config)
    if key not in record["variants"]:
        raise ContractError("UNREGISTERED_CAMPAIGN_VARIANT")
    return deepcopy(record["variants"][key]), {
        "id": name,
        "campaign_hash": record["campaign_hash"],
        "variant_key": key,
        "data_hash": record["data_hash"],
        "budget": record["budget"],
    }
