"""Independent repair boundary and financial-leg checks; installed wheel, synthetic inputs."""
from pathlib import Path
from fractions import Fraction as Q
from copy import deepcopy
import json,hashlib,uuid
from aqrp.backtest.engine import Simulator
from aqrp.backtest.synthetic import fixture_request
from aqrp.backtest import ledger as L
from aqrp.backtest.transactions import TransactionStore
from aqrp.core.errors import ContractError
from aqrp.performance.metrics import performance
import aqrp.services.backtest as service
O=Path(__file__).parent;R=Path('E:/WORK/AQRP-audits/p5-1c5a7e6/extended-repair');R.mkdir(exist_ok=False)
FIX='1c5a7e62cace7c3e66b7cc7f12fd564cb0013654';records=[]
H=lambda b:hashlib.sha256(b).hexdigest()
canonical=lambda x:json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()
def decode(v):
 if isinstance(v,dict):
  if set(v)=={'$fraction'}:return Q(*map(int,v['$fraction']))
  return {k:decode(x) for k,x in v.items()}
 if isinstance(v,list):return [decode(x) for x in v]
 return v
def serial(v):
 if isinstance(v,Q):return str(v)
 if isinstance(v,dict):return {k:serial(x) for k,x in v.items()}
 if isinstance(v,(list,tuple)):return [serial(x) for x in v]
 return v
def record(name,actual,expected,detail=None):
 records.append({'id':name,'actual':serial(actual),'expected':serial(expected),'status':'PASS' if actual==expected else 'MISMATCH','detail':detail})
original_sim=service.Simulator;original_recover=TransactionStore.recover
for stage in ['BEFORE_COMMIT','AFTER_COMMIT']:
 for typ in [KeyboardInterrupt,ContractError,RuntimeError]:
  label=stage+'-'+typ.__name__;root=R/label;request=fixture_request()
  (R/(label+'-request.json')).write_bytes(request.raw)
  class Boundary(Simulator):
   def __init__(self,config,runroot,commit):
    def fault(current):
     if current!=stage:return
     paths=sorted((runroot/'transactions').glob('prepared-*.json' if current=='BEFORE_COMMIT' else 'commit-*.json'))
     if not paths:return
     raw=max(paths,key=lambda p:p.stat().st_mtime_ns).read_bytes();x=json.loads(raw)
     if any(c['kind']=='Fill' for c in x['children']):raise typ('INDEPENDENT_REPAIR_BOUNDARY')
    super().__init__(config,runroot,commit,fault=fault)
  service.Simulator=Boundary;returned=None;raised=None
  try:returned=service.simulate_engineering(request,root,FIX)
  except RuntimeError as e:raised=type(e).__name__
  keys=[p.name for p in root.iterdir() if p.is_dir()];assert len(keys)==1
  rid=keys[0];run=root/rid;result=service.result_engineering(root,rid)
  if returned:
   (R/(label+'-return.json')).write_bytes(returned.raw)
   assert {k:v for k,v in returned.read().items() if k!='manifest'}==result
  after=stage=='AFTER_COMMIT';cash='98.1' if after else '1000';n=9 if after else 8
  durable=sorted((run/'transactions').glob('commit-*.json'));latest=json.loads(durable[-1].read_bytes());state=decode(latest['post_state'])
  tx=json.loads((run/'transactions.json').read_bytes());trace=json.loads((run/'committed-trace.json').read_bytes());failed=json.loads((run/'failed-state.json').read_bytes())
  checks={'status':result['status'],'cash':result['last_committed_account']['cash_total'],'commits':len(durable),'transactions':len(tx),'committed_trace':len(trace),'cash_from_raw_commit':state['cash_set'],'qty':state['assets']['SYNTH:0']['quantity'],'fees':state['fees'],'fills':len(state['fills']),'remaining_capacity':sum(state['capacity'].values()),'failed_state_equals_latest_commit':failed==latest['post_state'],'verification':result['committed_state_verification']['status'],'runtime_error_reraised':raised=='RuntimeError'}
  expected={'status':'CANCELLED' if typ is KeyboardInterrupt else 'FAILED','cash':cash,'commits':n,'transactions':n,'committed_trace':n,'cash_from_raw_commit':Q(cash),'qty':Q(9 if after else 0),'fees':Q(int(after)),'fills':int(after),'remaining_capacity':Q(11 if after else 20),'failed_state_equals_latest_commit':True,'verification':'VERIFIED_COMMITTED_PREFIX','runtime_error_reraised':typ is RuntimeError}
  for e in json.loads((run/'transaction-files.json').read_bytes()):assert H((run/e['path']).read_bytes())==e['sha256']
  for t in tx:assert H(canonical({k:v for k,v in t.items() if k!='sha256'}))==t['sha256']
  before={p.name:H(p.read_bytes()) for p in durable}
  try:service.resume_engineering(root,rid)
  except ContractError as exc:assert exc.code=='NONRUNNING_SIMULATION_CANNOT_RESUME'
  else:raise AssertionError('Terminal run resumed')
  assert before=={p.name:H(p.read_bytes()) for p in durable}
  record(label,checks,expected,str(run))
service.Simulator=original_sim

# Explicit corruption/IO controls. A bucket transfer keeps total cash/equity unchanged,
# so this independently challenges exact cash-bucket reconciliation, not hash integrity.
for damage in ['chain','read_denied','total_cash','bucket_reclassification']:
 root=R/('UNKNOWN-'+damage);armed=False
 def recover(store):
  if armed and damage=='read_denied':raise PermissionError('INDEPENDENT_READ_DENIED')
  return original_recover(store)
 TransactionStore.recover=recover
 class Damaged(Simulator):
  def __init__(self,config,runroot,commit):
   def fault(current):
    global armed
    if current!='AFTER_COMMIT':return
    paths=sorted((runroot/'transactions').glob('commit-*.json'));p=paths[-1];x=json.loads(p.read_bytes())
    if not any(c['kind']=='Fill' for c in x['children']):return
    (R/(damage+'-valid-commit-before.json')).write_bytes(p.read_bytes())
    if damage=='chain':x['post_hash']='0'*64
    if damage in ['total_cash','bucket_reclassification']:
     cash=decode(x['post_state']['cash_set'])+Q(1 if damage=='total_cash' else -1)
     x['post_state']['cash_set']={'$fraction':[str(cash.numerator),str(cash.denominator)]}
     if damage=='bucket_reclassification':
      x['post_state']['cashlots'].append({'id':'independent-unbacked-cashlot','entry_id':None,'kind':'FREE','amount':{'$fraction':['1','1']},'settled':False,'due':2})
     x['post_hash']=H(canonical(x['post_state']));x['sha256']=H(canonical({k:v for k,v in x.items() if k!='sha256'}))
    if damage!='read_denied':p.write_bytes(canonical(x))
    armed=True;raise ContractError('INDEPENDENT_CAPTURED_FAULT')
   super().__init__(config,runroot,commit,fault=fault)
 service.Simulator=Damaged
 wire=service.simulate_engineering(fixture_request(),root,FIX);result=wire.read();(R/(damage+'-return.json')).write_bytes(wire.raw);run=root/result['run_id']
 actual={'status':result['status'],'verification':result['committed_state_verification']['status'],'last_committed_account_present':'last_committed_account' in result,'failed_state_present':(run/'failed-state.json').exists(),'transactions_present':(run/'transactions.json').exists()}
 expected={'status':'FAILED','verification':'UNVERIFIED_COMMITTED_STATE','last_committed_account_present':False,'failed_state_present':False,'transactions_present':False}
 detail={'run':str(run),'reasons':result['reasons'],'claimed_account':result.get('last_committed_account')}
 if damage=='bucket_reclassification':
  state=decode(json.loads((run/'transactions/commit-000000000009.json').read_bytes())['post_state']);bal={'cash_set':Q(1000),'U_free':Q(0),'U_short':Q(0)}
  for entry in state['journal']:
   for line in entry['entries']:
    if line['unit']=='CCY' and line['account'] in bal:bal[line['account']]+=line['amount']
  detail.update({'raw_Journal_cash_buckets':serial(bal),'post_state_cash_set':str(state['cash_set']),'post_state_U_free':str(sum(c['amount'] for c in state['cashlots'] if not c['settled'] and c['kind']=='FREE')),'aggregate_cash_matches':sum(bal.values())==state['cash_set']+sum(c['amount'] for c in state['cashlots'] if not c['settled'])})
 record('UNKNOWN_'+damage,actual,expected,detail)
 TransactionStore.recover=original_recover;service.Simulator=original_sim

for old,delta in [(0,3),(0,-3),(2,3),(-2,-3),(3,-2),(-3,2),(3,-3),(-3,3),(2,-5),(-2,5)]:
 s=L.initial_state(Q(10000),[{'security_id':'A','lot':'1','industry':'I','beta':'1','short_permission':True,'borrow_limit':'1000000'}]);s['assets']['A']['mark']=Q(100);s['session']=0
 def fill(qty,p):return L.trade(s,fill_id=str(uuid.uuid4()),sid='A',signed_qty=Q(qty),p=Q(p),fee=Q(1),session=0,at='2024-02-01T09:00:00Z')
 if old:fill(old,100)
 prior=len(s['fills']);f=fill(delta,101);closed=min(abs(old),abs(delta)) if old*delta<0 else 0;opened=abs(delta)-closed;legs=[]
 for effect,n,direction in [('CLOSE',closed,'LONG' if old>0 else 'SHORT'),('OPEN',opened,'LONG' if delta>0 else 'SHORT')]:
  if n:legs.append({'effect':effect,'direction':direction,'quantity':Q(n),'signed_qty':Q(n if delta>0 else -n),'fee':Q(n,abs(delta)),'realized_gross':Q((1 if old>0 else -1)*n) if effect=='CLOSE' else Q(0)})
 expected={'direction':legs[0]['direction'] if len(legs)==1 else 'MIXED','execution_side':'BUY' if delta>0 else 'SELL','position_before':Q(old),'position_after':Q(old+delta),'position_legs':legs}
 record('LEGS_'+str(old)+'_'+str(delta),{k:f[k] for k in expected},expected)
 assert len(s['fills'])==prior+1 and s['fees']==prior+1 and sum(l['fee'] for l in f['position_legs'])==1
 assert sum(performance(s)['contribution'].values())==Q(-prior-1-delta)
report={'fixed_sha':FIX,'executor':'GPT Work supplemental reviewer','scope':'Actual installed-wheel service/commit and financial direction/leg controls, synthetic data only','records':records,'PASS':sum(x['status']=='PASS' for x in records),'MISMATCH':sum(x['status']=='MISMATCH' for x in records),'artifact_root':str(R)}
(O/'EXTENDED_REPAIR_CHECKS.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:report[k] for k in ['fixed_sha','PASS','MISMATCH','artifact_root']}))
