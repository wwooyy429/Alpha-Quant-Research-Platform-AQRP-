"""Independent installed-wheel public service source/anchor/cache/attribution controls."""
from pathlib import Path
from fractions import Fraction as Q
from copy import deepcopy
import json,uuid,hashlib
from aqrp.backtest.engine import Simulator
from aqrp.backtest.synthetic import fixture_request
from aqrp.backtest.contracts import EngineeringBacktestRequest
from aqrp.backtest.transactions import TransactionStore
from aqrp.backtest.ledger import initial_state
from aqrp.core.errors import ContractError
import aqrp.services.backtest as service
O=Path(__file__).parent;R=Path('E:/WORK/AQRP-audits/p5-1c5a7e6/public-backing-controls');R.mkdir(exist_ok=False)
FIX='1c5a7e62cace7c3e66b7cc7f12fd564cb0013654';records=[]
canon=lambda v:json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode();H=lambda b:hashlib.sha256(b).hexdigest()
def dec(v):
 if isinstance(v,dict):
  if set(v)=={'$fraction'}:return Q(*map(int,v['$fraction']))
  return {k:dec(x) for k,x in v.items()}
 if isinstance(v,list):return [dec(x) for x in v]
 return v
def enc(v):
 if isinstance(v,Q):return {'$fraction':[str(v.numerator),str(v.denominator)]}
 if isinstance(v,dict):return {k:enc(x) for k,x in v.items()}
 if isinstance(v,list):return [enc(x) for x in v]
 return v
def rec(name,a,e,detail=None):records.append(dict(id=name,actual=a,expected=e,status='PASS' if a==e else 'MISMATCH',detail=detail))
def rehash(item):item['post_hash']=H(canon(item['post_state']));item['sha256']=H(canon({k:v for k,v in item.items() if k!='sha256'}));return canon(item)
def outcome(wire,root):
 out=wire.read();run=root/out['run_id'];assert service.result_engineering(root,out['run_id'])=={k:v for k,v in out.items() if k!='manifest'}
 for e in out['manifest']['files']:assert H((run/e['path']).read_bytes())==e['sha256']
 return out,run
x=json.loads(fixture_request().raw);p=json.loads(x['decisions'][0]['portfolio_request_utf8']);p['policy'].update(mode='LONG_SHORT',gross='0.4',net='0');x['decisions'][0]['portfolio_request_utf8']=canon(p).decode();request=EngineeringBacktestRequest.create(x)
(R/'request.json').write_bytes(request.raw);original=service.Simulator
for mode in ['none','pair-and-copy','attribution-pool','initial-anchor','restriction-anchor']:
 for typ in [ContractError,KeyboardInterrupt]:
  case=R/(mode+'-'+typ.__name__);case.mkdir()
  class Fault(Simulator):
   def __init__(self,config,root,commit):
    def fault(stage):
     if stage!='AFTER_COMMIT':return
     path=sorted((root/'transactions').glob('commit-*.json'))[-1];item=json.loads(path.read_bytes())
     if item['payload']!={'session':2}:return
     s=dec(item['post_state']);short=next(c for c in s['cashlots'] if c['kind']=='SHORT' and c['settled']);lot=next(l for a in s['assets'].values() for l in a['lots'] if l['id']==short['entry_id'])
     (case/'valid-commit.json').write_bytes(path.read_bytes())
     if mode=='pair-and-copy':
      lot['price']-=1;short['amount']-=1;next(f for f in s['fills'] if f['fill_id']==lot['id'])['price']-=1
     elif mode=='attribution-pool':lot['borrow']+=1
     elif mode=='initial-anchor':s['initial_cash']+=1;s['cash_set']+=1
     elif mode=='restriction-anchor':s['other_restriction']-=1
     item['post_state']=enc(s);path.write_bytes(rehash(item));(case/'commit-at-fault.json').write_bytes(path.read_bytes());raise typ('INDEPENDENT_SOURCE_ANCHOR_FAULT')
    super().__init__(config,root,commit,fault=fault)
  service.Simulator=Fault
  try:wire=service.simulate_engineering(request,case/'runs',FIX)
  finally:service.Simulator=original
  (case/'actual-return.json').write_bytes(wire.raw);out,run=outcome(wire,case/'runs');good=mode=='none'
  expected=dict(status=('CANCELLED' if typ is KeyboardInterrupt else 'FAILED') if good else 'FAILED',known=good,account=good,verification='VERIFIED_COMMITTED_PREFIX' if good else 'UNVERIFIED_COMMITTED_STATE',known_snapshot=good)
  actual=dict(status=out['status'],known=out['committed_state_verification']['financial_state_known'],account='last_committed_account' in out,verification=out['committed_state_verification']['status'],known_snapshot=(run/'failed-state.json').exists())
  assert out['reasons'][0]==('KeyboardInterrupt' if typ is KeyboardInterrupt else 'INDEPENDENT_SOURCE_ANCHOR_FAULT')
  assert sorted((run/'transactions').glob('commit-*.json'))[-1].read_bytes()==(case/'commit-at-fault.json').read_bytes()
  if good:assert out['last_committed_account']['available']=='797.9'
  else:assert 'COMMITTED_STATE_UNVERIFIED' in out['reasons'] and not (run/'transactions.json').exists()
  rec(case.name,actual,expected,dict(error=out['committed_state_verification'].get('error'),original_fault_preserved=True))

for mode in ['return-cache-only','disk-paired-price']:
 case=R/mode;case.mkdir()
 class Divergent(Simulator):
  def run(self):
   s=super().run()
   if mode=='return-cache-only':s=deepcopy(s);s['cash_set']+=1;s['initial_cash']+=1
   else:
    path=sorted((self.root/'transactions').glob('commit-*.json'))[-1];item=json.loads(path.read_bytes());post=dec(item['post_state']);c=next(c for c in post['cashlots'] if c['kind']=='SHORT');lot=next(l for a in post['assets'].values() for l in a['lots'] if l['id']==c['entry_id']);c['amount']-=1;lot['price']-=1;item['post_state']=enc(post);(case/'valid-commit.json').write_bytes(path.read_bytes());path.write_bytes(rehash(item));(case/'commit-at-fault.json').write_bytes(path.read_bytes())
   return s
 service.Simulator=Divergent
 try:wire=service.simulate_engineering(request,case/'runs',FIX)
 finally:service.Simulator=original
 (case/'actual-return.json').write_bytes(wire.raw);out,_=outcome(wire,case/'runs');rec(mode,dict(status=out['status'],reason=out['reasons'][0],known=out['committed_state_verification']['financial_state_known']),dict(status='FAILED',reason='FINAL_COMMITTED_STATE_DIVERGED',known=mode=='return-cache-only'))

wire=service.simulate_engineering(request,R/'replay-source',FIX);out,_=outcome(wire,R/'replay-source');assert out['status']=='SUCCEEDED';(R/'replay-source-return.json').write_bytes(wire.raw)
class CacheReplay(Simulator):
 def run(self):s=deepcopy(super().run());s['cash_set']+=1;s['initial_cash']+=1;return s
service.Simulator=CacheReplay
try:
 try:service.replay_engineering(R/'replay-source',out['run_id'],R/'replay-cache-fault');code='ACCEPTED'
 except ContractError as exc:code=exc.code
finally:service.Simulator=original
rec('replay-cache-disk-divergence',code,'REPLAY_COMMITTED_STATE_DIVERGED')

for field in ['initial_cash','other_restriction']:
 store=TransactionStore(R/('anchor-restored-'+field),initial_state(Q(1000),[]));value=store.initial[field]
 def change(s):s[field]+=1;return []
 def restore(s):s[field]=value;return []
 store.commit(str(uuid.uuid4()),{},['2024-02-01T09:00:00Z',10,1],change);store.commit(str(uuid.uuid4()),{},['2024-02-01T09:00:01Z',10,2],restore)
 assert store.state[field]==value
 before={p.name:H(p.read_bytes()) for p in store.root.iterdir() if p.name!='.lock'}
 try:store.verified_snapshot();code='ACCEPTED'
 except ContractError as exc:code=exc.code
 assert before=={p.name:H(p.read_bytes()) for p in store.root.iterdir() if p.name!='.lock'}
 rec('transient-anchor-restored-'+field,code,'IMMUTABLE_ACCOUNT_ANCHOR_CHANGED')
report=dict(fixed_sha=FIX,executor='GPT Work supplemental reviewer',scope='Actual installed-wheel public service and durable on-disk anchor/cache/source checks; synthetic engineering only',records=records,PASS=sum(r['status']=='PASS' for r in records),MISMATCH=sum(r['status']=='MISMATCH' for r in records),artifact_root=str(R))
(O/'PUBLIC_BACKING_FAULT_CONTROLS.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:report[k] for k in ['fixed_sha','PASS','MISMATCH','artifact_root']}))
