"""Independent rehashed inconsistent-bucket fault, same class as existing economic-state control.
Not an OS isolation exploit: test whether VERIFIED_COMMITTED_PREFIX verifies Journal buckets.
"""
from pathlib import Path
from fractions import Fraction as Q
import json,hashlib
from aqrp.backtest.engine import Simulator
from aqrp.backtest.synthetic import fixture_request
from aqrp.backtest.contracts import EngineeringBacktestRequest
from aqrp.core.errors import ContractError
import aqrp.services.backtest as service
O=Path(__file__).parent;R=Path('E:/WORK/AQRP-audits/p5-1c5a7e6/short-bucket-reconciliation');R.mkdir(exist_ok=False)
FIX='1c5a7e62cace7c3e66b7cc7f12fd564cb0013654'
canonical=lambda v:json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()
H=lambda b:hashlib.sha256(b).hexdigest()
def decode(v):
 if isinstance(v,dict):
  if set(v)=={'$fraction'}:return Q(*map(int,v['$fraction']))
  return {k:decode(x) for k,x in v.items()}
 if isinstance(v,list):return [decode(x) for x in v]
 return v
def f(v):return {'$fraction':[str(v.numerator),str(v.denominator)]}
x=json.loads(fixture_request().raw);p=json.loads(x['decisions'][0]['portfolio_request_utf8']);p['policy'].update(mode='LONG_SHORT',gross='0.4',net='0');x['decisions'][0]['portfolio_request_utf8']=canonical(p).decode();request=EngineeringBacktestRequest.create(x)
(R/'request.json').write_bytes(request.raw);original=service.Simulator
class Fault(Simulator):
 def __init__(self,config,root,commit):
  def fault(stage):
   if stage!='AFTER_COMMIT':return
   path=sorted((root/'transactions').glob('commit-*.json'))[-1];raw=path.read_bytes();item=json.loads(raw)
   fills=[c['fill'] for c in item['children'] if c['kind']=='Fill']
   if not fills or decode(fills[0]['signed_qty'])>=0:return
   state=item['post_state'];cashlot=next(c for c in state['cashlots'] if c['kind']=='SHORT' and not c['settled'] and decode(c['amount'])>1)
   (R/'valid-commit-before-fault.json').write_bytes(raw)
   state['cash_set']=f(decode(state['cash_set'])+1);cashlot['amount']=f(decode(cashlot['amount'])-1)
   item['post_hash']=H(canonical(state));item['sha256']=H(canonical({k:v for k,v in item.items() if k!='sha256'}));path.write_bytes(canonical(item));(R/'inconsistent-but-rehashed-commit.json').write_bytes(path.read_bytes())
   raise ContractError('INDEPENDENT_BUCKET_FAULT')
  super().__init__(config,root,commit,fault=fault)
service.Simulator=Fault
wire=service.simulate_engineering(request,R/'runs',FIX);service.Simulator=original;result=wire.read();(R/'actual-return.json').write_bytes(wire.raw)
assert result['status']=='FAILED' and result['reasons'][0]=='INDEPENDENT_BUCKET_FAULT','Short fill/fault was not reached'
state=decode(json.loads((R/'inconsistent-but-rehashed-commit.json').read_bytes())['post_state']);balances={'cash_set':Q(1000),'U_free':Q(0),'U_short':Q(0)}
for entry in state['journal']:
 for line in entry['entries']:
  if line['unit']=='CCY' and line['account'] in balances:balances[line['account']]+=line['amount']
c=result.get('last_committed_account');detail={'journal_cash_buckets':{k:str(v) for k,v in balances.items()},'post_state_cash_set':str(state['cash_set']),'post_state_U_short':str(sum(t['amount'] for t in state['cashlots'] if t['kind']=='SHORT' and not t['settled'])),'aggregate_cash_unchanged':sum(balances.values())==state['cash_set']+sum(t['amount'] for t in state['cashlots'] if not t['settled']),'last_committed_account':c}
if c:
 correct_available=balances['cash_set']-sum(Q(c[k]) for k in ['S_set','short_value','O_N','O_F','P_res','Z'])
 detail.update({'available_from_raw_Journal_and_unchanged_restrictions':str(correct_available),'claimed_available':c['available'],'excess_available':str(Q(c['available'])-correct_available)})
report={'fixed_sha':FIX,'executor':'GPT Work supplemental reviewer','scope':'Recomputed-hash financial inconsistency fault; no native permission/ACL operation or trading','status':result['status'],'verification':result['committed_state_verification']['status'],'expected_verification':'UNVERIFIED_COMMITTED_STATE','last_committed_account_expected_absent':True,'detail':detail,'result':'PASS' if result['committed_state_verification']['status']=='UNVERIFIED_COMMITTED_STATE' and c is None else 'REPRODUCED_MISMATCH','artifact_root':str(R)}
(O/'SHORT_BUCKET_RECONCILIATION_PROBE.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(report,ensure_ascii=False))
