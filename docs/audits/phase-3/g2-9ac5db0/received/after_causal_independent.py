"""Reviewer causal recheck: real P1-published data, then actual training split."""
import json,hashlib
from pathlib import Path
from copy import deepcopy
from datetime import date
from decimal import Decimal
from aqrp.core.time import utc
from aqrp.core.canonical import canonical,digest
from aqrp.data.synthetic import load_synthetic,PROVENANCE
from aqrp.data.snapshot import publish_snapshot
from aqrp.data.store import read_snapshot
from aqrp.validation.labels import CoverageRef,make_labels
from aqrp.validation.splits import purged_train
out=Path(__file__).resolve().parent
tables=load_synthetic(sessions=[(date(2024,1,d),"12:00:00") for d in (2,3,4,5)])
for r in tables["bars_daily"]:
 p=Decimal(100 if r["session_date"].day==3 else 110)
 r.update({k:p for k in ("open","high","low","close")})
 r.update(amount=p*r["volume"],source_amount=str(p*r["volume"]))
old=tables["security_master"][0];old["delisting_at"]=utc("2024-01-04T08:00:00Z")
new=deepcopy(old);late=utc("2024-01-05T00:00:00Z")
new.update(revision_id=2,delisting_at=None,event_time=late,available_at=late,known_at=late,source_record_id="late-delisting-correction")
tables["security_master"].append(new)
s=publish_snapshot(tables,PROVENANCE,out/"adversarial-data/late-master-causal")
cov=CoverageRef.create(s.manifest_hash,[dict(coverage_id="jan4",event_time="2024-01-04T12:00:00Z",available_at="2024-01-04T12:05:00Z",complete_through="2024-01-04T12:00:00Z",revision_id=1)],authority="reviewer-public-input",scope="PUBLIC_ENGINEERING")
def at(cutoff):return make_labels(s,[dict(session=date(2024,1,2),decision_time="2024-01-02T12:05:00Z")],["SYN_A:001"],[1],cutoff,cov)[0]
before=at("2024-01-04T12:10:00Z");after=at("2024-01-05T12:10:00Z")
assert before["label"] is None and before["reason"]=="FORWARD_STATUS_UNTRADABLE_OR_UNKNOWN"
assert after["label"]==.1 and after["available_at"]==late and after["information_interval"][1]==late
_,published=read_snapshot(s)
master=next(r for r in published["security_master"].to_pylist() if r["security_id"]=="SYN_A:001" and r["revision_id"]==2)
assert after["security_master_ref"]["row_hash"]==digest(master)
assert after["security_master_ref"]["revision_id"]==2
results=[]
for cutoff,expected in (("2024-01-04T12:10:00Z",0),("2024-01-04T23:59:59.999999Z",0),("2024-01-05T00:00:00Z",1),("2024-01-05T00:00:00.000001Z",1)):
 split=purged_train([after],("2024-01-02","2024-01-03"),("2024-01-05","2024-01-06"),cutoff,[],0)
 assert len(split["train"])==expected
 if not expected: assert split["rejected"][0]["split_reason"]=="LABEL_NOT_AVAILABLE_AT_FIT"
 results.append(dict(cutoff=cutoff,expected_train_count=expected,actual_train_count=len(split["train"]),split=split))
r=dict(reviewed_sha="9ac5db069287a6e4a095e25ae8c3cc8fa229cded",executor="GPT Work independent current installed-wheel causal recheck",script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),basis="Original independent causal input retained; assertions now require fixed availability and actual split boundaries.",valid_p1_snapshot=str(s.root),snapshot_manifest_hash=s.manifest_hash,old_master=old,late_master=new,published_selected_master=master,before=before,after=after,fit_cutoff_results=results,observed_future_leak=False,formal_test_or_deployment=False)
(out/"after-causal-independent.json").write_bytes(canonical(r))
print(json.dumps(dict(reviewed_sha=r["reviewed_sha"],before_reason=before["reason"],after_label=after["label"],after_available=str(after["available_at"]),master_revision=2,cutoffs=[dict(cutoff=x["cutoff"],train_count=x["actual_train_count"]) for x in results],passed=True),indent=2))

