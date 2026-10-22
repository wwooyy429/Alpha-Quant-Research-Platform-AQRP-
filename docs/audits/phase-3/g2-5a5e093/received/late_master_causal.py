"""Causal late-master PIT counterexample on fully validated P1 snapshot."""
import json,hashlib,sys
from pathlib import Path
from copy import deepcopy
from datetime import date
from decimal import Decimal
from aqrp.core.time import utc
from aqrp.core.canonical import canonical
from aqrp.data.synthetic import load_synthetic,PROVENANCE
from aqrp.data.snapshot import publish_snapshot
from aqrp.validation.labels import CoverageRef,make_labels
out=Path(__file__).resolve().parent
tables=load_synthetic(sessions=[(date(2024,1,d),"12:00:00") for d in (2,3,4,5)])
for r in tables["bars_daily"]:
 p=Decimal(100 if r["session_date"].day==3 else 110)
 r.update({k:p for k in ("open","high","low","close")})
 r.update(amount=p*r["volume"],source_amount=str(p*r["volume"]))
old=tables["security_master"][0];old["delisting_at"]=utc("2024-01-04T08:00:00Z")
new=deepcopy(old);new.update(revision_id=2,delisting_at=None,event_time=utc("2024-01-05T00:00:00Z"),available_at=utc("2024-01-05T00:00:00Z"),known_at=utc("2024-01-05T00:00:00Z"),source_record_id="late-delisting-correction")
tables["security_master"].append(new)
s=publish_snapshot(tables,PROVENANCE,out/"adversarial-data/late-master-causal")
cov=CoverageRef.create(s.manifest_hash,[dict(coverage_id="jan4",event_time="2024-01-04T12:00:00Z",available_at="2024-01-04T12:05:00Z",complete_through="2024-01-04T12:00:00Z",revision_id=1)],authority="reviewer-public-input",scope="PUBLIC_ENGINEERING")
def at(cutoff):return make_labels(s,[dict(session=date(2024,1,2),decision_time="2024-01-02T12:05:00Z")],["SYN_A:001"],[1],cutoff,cov)[0]
before=at("2024-01-04T12:10:00Z");after=at("2024-01-05T12:10:00Z")
assert before["label"] is None and before["reason"]=="FORWARD_STATUS_UNTRADABLE_OR_UNKNOWN"
assert after["label"]==.1 and after["available_at"]<new["available_at"]
r=dict(reviewed_sha="5a5e093c2e9b39abe1332e49d1df40d20f9fd33f",executor="GPT Work independent installed-wheel counterexample",script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),valid_p1_snapshot=str(s.root),old_master=old,late_master=new,before=before,after=after,fit_cutoff="2024-01-04T12:10:00Z",implementation_would_accept_after_label_at_fit=after["available_at"]<=utc("2024-01-04T12:10:00Z"),expected_earliest_after_label_availability=str(new["available_at"]),observed_future_leak=True,formal_test_or_deployment=False)
(out/"late-master-causal-results.json").write_bytes(canonical(r))
print(json.dumps({k:v for k,v in json.loads(canonical(r)).items() if k not in ("old_master","late_master")},ensure_ascii=False,indent=2))

