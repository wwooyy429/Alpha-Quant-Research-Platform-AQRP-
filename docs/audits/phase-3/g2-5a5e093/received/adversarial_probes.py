"""Reviewer-owned adversarial API probes; installed wheel only. No deployment/ACL changes."""
import hashlib,json,sys
from pathlib import Path
from copy import deepcopy
from datetime import date
from decimal import Decimal
import pandas as pd
from aqrp.core.canonical import canonical,digest
from aqrp.core.time import utc
from aqrp.data.synthetic import load_synthetic,PROVENANCE
from aqrp.data.snapshot import publish_snapshot
from aqrp.experiments.ledger import ExperimentLedger
from aqrp.research.pipeline import compose
from aqrp.validation.approvals import propose,record_decision
from aqrp.validation.evaluator import seal
from aqrp.validation.labels import CoverageRef,make_labels
OUT=Path(__file__).resolve().parent;RUN=OUT/"adversarial-data";RUN.mkdir(exist_ok=True)
results=[]
# Public compose accepts clocks, refs and eligibility fields; expected contract disallows future/unmatched input.
spec=dict(factor_keys=["a","b"],weights=[1,1],directions=[1,1],direction_applied=False,normalization="cross_sectional_sample_z",input_stage="final",min_n=3,redundancy=None)
frame=pd.DataFrame([dict(factor_key=k,security_id=f"SYN_A:{i:03}",session="2024-01-04",stage="final",score=v,decision_time="2024-01-04T12:05:00Z",available_at="2024-01-04T12:00:00Z") for k,vs in (("a",[1,2,3]),("b",[3,1,2])) for i,v in enumerate(vs,1)])
control=compose(frame,spec);assert len(control["scores"])==3
late=frame.copy();late.loc[late.factor_key=="b","available_at"]="2024-01-05T12:00:00Z"
mismatch=frame.copy();mismatch.loc[mismatch.factor_key=="b","decision_time"]="2024-01-05T12:05:00Z"
for name,f in (("COMPOSE_FUTURE_AVAILABLE",late),("COMPOSE_MIXED_DECISION_CUTOFF",mismatch)):
 try:
  r=compose(f,spec);results.append(dict(case=name,expected="REJECT future or mixed-cutoff input before synthesis",actual="ACCEPTED",scores=r["scores"],contract_violation=bool(r["scores"])))
 except Exception as exc:results.append(dict(case=name,actual="REJECTED",error=repr(exc),contract_violation=False))
# Terminal proposal must be in the signed immutable manifest, not just a later file at that path.
ledger=ExperimentLedger(RUN/"terminal-proposal")
lineage=dict(code_commit="5a5e093c2e9b39abe1332e49d1df40d20f9fd33f",code_bundle="b"*64,data_hash="c"*64,environment={"lock":"d"*64},protocol_hash="e"*64,permission_domain="ENGINEERING_ONLY",seed=17)
run=ledger.start({"fixture":"no original approval proposal"},lineage);manifest=ledger.finish(run,"SUCCEEDED")
candidate={"hypothesis":"fixture-A"}
protocol=dict(human_approval_record="UNIT_NOT_REAL_APPROVAL",frozen_at="2024-01-01T00:00:00Z",candidate_hash=digest(candidate),standards=dict(min_mean_ic=.1,min_days=252,max_adjusted_p=.05,min_positive_fraction=.5))
evidence=dict(all_candidates_recorded=True,contaminated=False,validation_first_access_at="2024-01-02T00:00:00Z",**{k:"f"*64 for k in ("independent_golden_ref","implementation_review_ref","code_hash","data_hash","environment_hash","frozen_protocol_hash")})
proposal=propose(candidate,protocol,dict(mean=.2,n=300,positive_fraction=.6),dict(complete=True,adjusted=[.01]),dict(purpose="FINAL_TEST",independence_verified=True),evidence)
assert proposal["eligible"]
key=b"reviewer-unit-fixture-not-real-secret-material"
envelope=seal(dict(proposal_hash=digest(proposal),human_actor="UNIT_NOT_REAL_HUMAN_APPROVAL",state="ResearchValidated"),key)
try:record_decision(ledger,run,proposal,envelope,key)
except Exception as exc:no_file_error=repr(exc)
else:raise AssertionError("negative control missing proposal must reject")
(ledger.path(run)/"approvals.json").write_bytes(canonical({"fixture-A":proposal}))
verify_after=ledger.verify(run)
decision=record_decision(ledger,run,proposal,envelope,key)
results.append(dict(case="POST_TERMINAL_UNMANIFESTED_PROPOSAL",expected="REJECT unmanifested approvals.json injected after finish",negative_control=no_file_error,original_manifest_files=[x["path"] for x in manifest["files"]],manifest_unchanged=manifest==verify_after,actual=decision,contract_violation=decision["state"]=="ResearchValidated",note="Public unit-fixture ledger/key only; no actual financial approval, deployment or private data."))
# Real valid P1 snapshot with a later visible master revision used by eligibility.
tables=load_synthetic(sessions=[(date(2024,1,d),"12:00:00") for d in (2,3,4,5)])
for b in tables["bars_daily"]:
 price=Decimal(100 if b["session_date"].day==3 else 110)
 b.update({k:price for k in ("open","high","low","close")})
 b.update(amount=price*b["volume"],source_amount=str(price*b["volume"]))
revision=deepcopy(tables["security_master"][0]);revision.update(revision_id=2,event_time=utc("2024-01-05T00:00:00Z"),available_at=utc("2024-01-05T00:00:00Z"),known_at=utc("2024-01-05T00:00:00Z"),listing_at=utc("2024-01-03T08:00:00Z"),source_record_id="explicit-late-master-revision")
tables["security_master"].append(revision)
try:
 s=publish_snapshot(tables,PROVENANCE,RUN/"late-master")
 cov=CoverageRef.create(s.manifest_hash,[dict(coverage_id="jan4",event_time="2024-01-04T12:00:00Z",available_at="2024-01-04T12:05:00Z",complete_through="2024-01-04T12:00:00Z",revision_id=1)],authority="reviewer-public-fixture",scope="PUBLIC_ENGINEERING")
 r=make_labels(s,[dict(session=date(2024,1,2),decision_time="2024-01-02T12:05:00Z")],["SYN_A:001"],[1],"2024-01-05T12:10:00Z",cov)[0]
 results.append(dict(case="LATE_MASTER_DEPENDENCY_CLOCK",expected="selected late master revision must be in dependency availability/lineage",selected_master_available_at=str(revision["available_at"]),actual=r,contract_violation=r["label"] is not None and r["available_at"]<revision["available_at"]))
except Exception as exc:results.append(dict(case="LATE_MASTER_DEPENDENCY_CLOCK",fixture_or_execution_error=repr(exc),contract_violation=None))
r=dict(executor="GPT Work independent installed-wheel probes",reviewed_sha="5a5e093c2e9b39abe1332e49d1df40d20f9fd33f",interpreter=sys.executable,script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),controls=dict(normal_compose_scores=len(control["scores"]),missing_proposal_rejected=True),results=results,deployment_performed=False,formal_test_executed=False)
(OUT/"adversarial-results.json").write_bytes(canonical(r))
print(json.dumps(json.loads(canonical(r)),ensure_ascii=False,indent=2))

