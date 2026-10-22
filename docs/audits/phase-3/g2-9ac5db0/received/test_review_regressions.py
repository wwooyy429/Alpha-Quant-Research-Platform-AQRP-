"""Four independent regression expectations; public fixtures only, no deployment."""
from copy import deepcopy
from datetime import date
from decimal import Decimal
import pandas as pd
import pytest
from aqrp.core.canonical import canonical,digest
from aqrp.core.errors import ContractError
from aqrp.core.time import utc
from aqrp.data.synthetic import load_synthetic,PROVENANCE
from aqrp.data.snapshot import publish_snapshot
from aqrp.experiments.ledger import ExperimentLedger
from aqrp.research.pipeline import compose
from aqrp.validation.approvals import propose,record_decision
from aqrp.validation.evaluator import seal
from aqrp.validation.labels import CoverageRef,make_labels

@pytest.mark.parametrize("field",["available_at","decision_time"])
def test_composite_rejects_future_or_mixed_clock(field):
 frame=pd.DataFrame([dict(factor_key=k,security_id=str(i),session="2024-01-04",stage="final",score=v,decision_time="2024-01-04T12:05:00Z",available_at="2024-01-04T12:00:00Z") for k,vs in (("a",[1,2,3]),("b",[3,1,2])) for i,v in enumerate(vs)])
 spec=dict(factor_keys=["a","b"],weights=[1,1],directions=[1,1],direction_applied=False,normalization="cross_sectional_sample_z",input_stage="final",min_n=3,redundancy=None)
 assert len(compose(frame,spec)["scores"])==3
 frame.loc[frame.factor_key=="b",field]="2024-01-05T12:05:00Z"
 with pytest.raises(ContractError):
  compose(frame,spec)

def test_decision_rejects_post_terminal_unmanifested_proposal(tmp_path):
 l=ExperimentLedger(tmp_path)
 lineage=dict(code_commit="5a5e093c2e9b39abe1332e49d1df40d20f9fd33f",code_bundle="b"*64,data_hash="c"*64,environment={"lock":"d"*64},protocol_hash="e"*64,permission_domain="PUBLIC_UNIT_FIXTURE",seed=17)
 run=l.start({},lineage);original=l.finish(run,"SUCCEEDED")
 candidate={"hypothesis":"public-fixture"}
 protocol=dict(human_approval_record="UNIT_NOT_REAL_APPROVAL",frozen_at="2024-01-01T00:00:00Z",candidate_hash=digest(candidate),standards=dict(min_mean_ic=.1,min_days=252,max_adjusted_p=.05,min_positive_fraction=.5))
 evidence=dict(all_candidates_recorded=True,contaminated=False,validation_first_access_at="2024-01-02T00:00:00Z",**{k:"f"*64 for k in ("independent_golden_ref","implementation_review_ref","code_hash","data_hash","environment_hash","frozen_protocol_hash")})
 p=propose(candidate,protocol,dict(mean=.2,n=300,positive_fraction=.6),dict(complete=True,adjusted=[.01]),dict(purpose="FINAL_TEST",independence_verified=True),evidence)
 assert p["eligible"] and not any(r["path"]=="approvals.json" for r in original["files"])
 key=b"reviewer-unit-key-not-a-real-operator-secret"
 envelope=seal(dict(proposal_hash=digest(p),human_actor="UNIT_NOT_REAL_APPROVER",state="ResearchValidated"),key)
 with pytest.raises(ContractError):
  record_decision(l,run,p,envelope,key)
 (l.path(run)/"approvals.json").write_bytes(canonical({"public-fixture":p}))
 with pytest.raises(ContractError):
  record_decision(l,run,p,envelope,key)

def test_label_clock_includes_causally_required_late_master(tmp_path):
 tables=load_synthetic(sessions=[(date(2024,1,d),"12:00:00") for d in (2,3,4,5)])
 for b in tables["bars_daily"]:
  price=Decimal(100 if b["session_date"].day==3 else 110)
  b.update({k:price for k in ("open","high","low","close")})
  b.update(amount=price*b["volume"],source_amount=str(price*b["volume"]))
 old=tables["security_master"][0];old["delisting_at"]=utc("2024-01-04T08:00:00Z")
 new=deepcopy(old);new.update(revision_id=2,delisting_at=None,event_time=utc("2024-01-05T00:00:00Z"),available_at=utc("2024-01-05T00:00:00Z"),known_at=utc("2024-01-05T00:00:00Z"))
 tables["security_master"].append(new)
 s=publish_snapshot(tables,PROVENANCE,tmp_path/"inputs")
 c=CoverageRef.create(s.manifest_hash,[dict(coverage_id="jan4",event_time="2024-01-04T12:00:00Z",available_at="2024-01-04T12:05:00Z",complete_through="2024-01-04T12:00:00Z",revision_id=1)],authority="reviewer-public-fixture",scope="PUBLIC_ENGINEERING")
 def at(cutoff):
  return make_labels(s,[dict(session=date(2024,1,2),decision_time="2024-01-02T12:05:00Z")],["SYN_A:001"],[1],cutoff,c)[0]
 assert at("2024-01-04T12:10:00Z")["label"] is None
 after=at("2024-01-05T12:10:00Z")
 assert after["label"]==.1
 assert after["available_at"]>=new["available_at"],"label cannot predate the revision which changes it from invalid to usable"

