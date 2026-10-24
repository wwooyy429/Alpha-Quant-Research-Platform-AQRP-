"""Probe P6's existing admission boundary only: no worker, signal, simulation or formal Test."""
import json,sys,hashlib,importlib.metadata
from pathlib import Path
from aqrp.services.task_requests import initialize
from aqrp.services.tasks import TaskService
from aqrp.services.research import hypotheses
from aqrp.experiments.ledger import ExperimentLedger,read_chain
import aqrp
O=Path(__file__).parent.resolve();C=Path('E:/WORK/AQRP-audits/p7-3c34e3c/src');root=O/'budget-probe-fixture-resolved'
assert not root.exists()
installed=Path(aqrp.__file__).parent
files=[]
for p in sorted(installed.rglob('*.py')):
 rel=p.relative_to(installed);h=hashlib.sha256(p.read_bytes()).hexdigest()
 assert h==hashlib.sha256((C/'src/aqrp'/rel).read_bytes()).hexdigest()
 files.append({'path':rel.as_posix(),'sha256':h})
cat=initialize(root,'3017a097b49ecdae68228ca9a417fcd03c313200');s=TaskService(root)
variant={'start':'2024-01-06','end':'2024-01-06','horizons':[1],'factor_ids':['momentum']}
plan=s.register_campaign('primary-g1-admission-probe',[variant]);frozen=s.freeze({**variant,'campaign_id':plan['id']})
rows=[]
for i in range(12):
 r=s.submit(frozen,'primary-cancel-'+str(i));assert r['status']=='QUEUED';assert s.cancel(r['task_id'])=='CANCELLED';rows.append(r)
assert rows[-1]['research_control']['prior_reserved_units']==11
assert not (root/'research-runs/trials.jsonl').exists()
# Exactly the unchanged no-TaskContext admission used at research.py:205-220,282-289.
# This stops after registration and does not invoke research() or CLI numerical work.
c=json.loads(frozen.raw)['payload']['research'];h=hypotheses(c)[0]
lineage={'code_commit':cat['code_commit'],'code_bundle':cat['code_bundle'],'data_hash':cat['snapshot']['manifest_hash'],'environment':cat['core_environment'],'protocol_hash':'primary-boundary-probe','permission_domain':'ENGINEERING_DEMO','seed':c['seed']}
l=ExperimentLedger(root/'research-runs');run=l.start(c,lineage)
admission=l.register_trial(run,c['family']['id'],h['hypothesis'],budget=c['family']['budget'],hypothesis_spec=h)
assert admission['over_budget'] is False
terminal=l.finish(run,'CANCELLED')
after=s.submit(frozen,'primary-task-after-legacy')
assert after['status']=='FAILED' and after['error']=='EXPERIMENT_BUDGET_EXCEEDED'
report={'executor':'Primary GPT Work; existing P6 installed SDK boundary probe','scope':'No Task.work/research()/simulation/CLI numerical invocation; no P7 implementation or product-test claim','installed_python':sys.executable,'installed_version':importlib.metadata.version('aqrp'),'package_root':str(installed),'source_matches_fixed_G_all_python_files':files,'workspace':str(root),'twelve_tasks':[{'task_id':x['task_id'],'reservation':x['research_control']} for x in rows],'after_12_cancelled_task_reserved_units':12,'legacy_trials_before':0,'unowned_legacy_admission':admission,'probe_run_terminal':terminal,'actual_trials_after':len(read_chain(root/'research-runs/trials.jsonl')),'next_task':after,'finding':'Existing legacy admission ignores already consumed Task reservations; proposed shared12 actor campaign needs explicit bridge or enforceable ordering.'}
(O/'PRIMARY_BUDGET_COUNTEREXAMPLE.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({'cancelled_tasks':12,'legacy_admitted_after_full_budget':not admission['over_budget'],'legacy_trials':1,'next_Task_error':after['error']}))
