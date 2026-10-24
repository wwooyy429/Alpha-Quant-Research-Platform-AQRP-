"""Independent repair challenges; installed wheel is the SUT, literal policy is the oracle."""
from pathlib import Path
import json,sys,hashlib,concurrent.futures,subprocess,time
from aqrp.services.task_requests import initialize,catalogue,references
from aqrp.services.tasks import TaskService
from aqrp.experiments.ledger import read_chain
from aqrp.core.canonical import canonical,digest
from aqrp.core.errors import ContractError
from aqrp.backtest.transactions import TransactionStore
from aqrp.data.query import universe_at
O=Path(__file__).parent;ROOT=Path('E:/WORK/AQRP-runs/gpt-p6-independent-3017a09-20261024')
ROOT.mkdir(exist_ok=True)
FIX='3017a097b49ecdae68228ca9a417fcd03c313200'
BASE={'kind':'research','start':'2024-01-06','end':'2024-01-06','horizons':[1]}
save=lambda n,v:(O/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def fresh(name):
 p=ROOT/name;assert not p.exists();initialize(p,FIX);return TaskService(p)
def err(call):
 try:call();return None
 except Exception as e:return getattr(e,'code',type(e).__name__)
def byteset(p):
 return {str(x.relative_to(p)):hashlib.sha256(x.read_bytes()).hexdigest() for x in p.rglob('*') if x.is_file() and not x.name.startswith('tasks.sqlite')}
records=[]
s=fresh('old-unregistered-variation')
f=s.freeze({**BASE,'lookback':1});prior=byteset(s.root)
for i in range(2,15):
 error=err(lambda:s.freeze({**BASE,'lookback':i}))
 assert error=='UNREGISTERED_CAMPAIGN_VARIANT',(i,error)
 assert byteset(s.root)==prior
records.append(dict(case='original14lookbacks_without_preregistration',allowed=1,refused=13,code='UNREGISTERED_CAMPAIGN_VARIANT',side_effects=False,workspace=str(s.root)))
s=fresh('registered14-execution')
variants=[{**BASE,'lookback':i} for i in range(1,15)]
plan=s.register_campaign('fixed14',variants)
results=[]
for i,d in enumerate(variants):
 f=s.freeze({**d,'campaign_id':'fixed14'});q=s.submit(f,'v'+str(i));assert s.submit(f,'v'+str(i))['task_id']==q['task_id']
 r=s.work(q['task_id'])
 assert r['research_control']['prior_reserved_units']==i
 assert r['status']==('SUCCEEDED' if i<12 else 'FAILED'),r
 if i>=12:assert r['error']=='EXPERIMENT_BUDGET_EXCEEDED'
 else:
  mult=json.loads(s.artifact(q['task_id'],'R','multiplicity.json'))
  assert mult['m']==14 and len(mult['hypotheses'])==14
 results.append(dict(lookback=i+1,task=q['task_id'],status=r['status'],control=r['research_control'],multiplicity=None if i>=12 else mult))
late=s.register_campaign('renamed-after-results',[BASE])
q=s.submit(s.freeze({**BASE,'campaign_id':late['id']}),'renamed')
assert q['status']=='FAILED' and q['research_control']['prior_reserved_units']==14 and late['registration_history']['contaminated_before_registration']
trials=[x['payload'] for x in read_chain(s.root/'research-runs/trials.jsonl')]
assert len(trials)==12 and len({t['family'] for t in trials})==1
records.append(dict(case='preregistered14_real_core_and_rename',workspace=str(s.root),plan=plan,results=results,late_plan=late,late_refused=q,trials=trials))
s=fresh('cross-plan-contamination')
for name,lookback in [('before',2),('after',3)]:
 p=s.register_campaign(name,[{**BASE,'lookback':lookback}])
 q=s.submit(s.freeze({**BASE,'lookback':lookback,'campaign_id':name}),name);r=s.work(q['task_id']);assert r['status']=='SUCCEEDED'
 if name=='after':
  m=json.loads(s.artifact(q['task_id'],'R','multiplicity.json'))
  assert m['contaminated'] is True and p['registration_history']['prior_research_trials']==1 and q['research_control']['prior_reserved_units']==1
  records.append(dict(case='cross_plan_actual_contamination',workspace=str(s.root),plan=p,task=r,multiplicity=m))
s=fresh('concurrent-no-refunds')
drafts=[{**BASE,'factor_ids':['momentum','reversal'],'horizons':[1,2]},BASE]
p=s.register_campaign('multi',drafts)
f=s.freeze({**drafts[0],'campaign_id':'multi'})
hyp=json.loads(f.raw)['payload']['research']['family']['hypotheses']
# two single factors plus their composite, each at two horizons = six units per Task.
assert len(hyp)==7 # six in first variant plus one in second variant
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:rows=list(pool.map(lambda i:s.submit(f,'parallel-'+str(i)),range(4)))
assert sorted(r['research_control']['prior_reserved_units'] for r in rows)==[0,6,12,18]
assert sum(r['status']=='QUEUED' for r in rows)==2 and sum(r['status']=='FAILED' for r in rows)==2
for r in rows:
 if r['status']=='QUEUED':assert s.cancel(r['task_id'])=='CANCELLED'
late=s.register_campaign('no-refund',[BASE]);q=s.submit(s.freeze({**BASE,'campaign_id':'no-refund'}),'after-cancel')
assert q['status']=='FAILED' and q['research_control']['prior_reserved_units']==24
records.append(dict(case='concurrent6unit_reservations_failed_cancelled_no_refund',workspace=str(s.root),rows=rows,after_cancel=q))
save('INDEPENDENT_CAMPAIGN_RECHECK.json',dict(fixed_sha=FIX,executor='GPT Work',python=sys.executable,records=records,result='PASS'))
print('Campaign challenges PASS',flush=True)
