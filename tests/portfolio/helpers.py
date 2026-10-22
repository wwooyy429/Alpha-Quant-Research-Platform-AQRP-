import json
from pathlib import Path

from aqrp.core.canonical import digest
from aqrp.portfolio.contracts import PortfolioRequest

FIXTURES = Path(__file__).parent / "fixtures"


def fixture(name="base"):
    return json.loads((FIXTURES / (name + ".json")).read_bytes())


def reseal(x):
    entries = [v for k, v in x["inputs"].items() if k != "scores"] + x["inputs"]["scores"]
    for e in entries:
        e["content_sha256"] = digest({k: v for k, v in e.items() if k != "content_sha256"})
    x["source"]["fixture_manifest"] = {e["ref"]: e["content_sha256"] for e in entries}
    return PortfolioRequest.create(x)


def change(x, path, value):
    keys = path.split(".")
    o = x
    for k in keys[:-1]:
        o = o[int(k)] if isinstance(o, list) else o[k]
    if isinstance(o, list):
        o[int(keys[-1])] = value
    else:
        o[keys[-1]] = value
    return x
