"""Independent minimal public-service counterexample for incomplete 003 repair.
Financial consistency injection only, not an OS isolation attack.
"""
from pathlib import Path
from fractions import Fraction as Q
import json,hashlib
from aqrp.backtest.engine import Simulator
from aqrp.backtest.synthetic import fixture_request
from aqrp.backtest.contracts import EngineeringBacktestRequest
from aqrp.core.errors import ContractError
import aqrp.services.backtest as service
O=Path(__file__).parent;R=Path('E:/WORK/AQRP-audits/p5-bf5e5a8/settled-short-backing-probe');R.mkdir(exist_ok=False)
FIX='bf5e5a89209f2dd24042cd806626f832b531de52'
canonical=lambda v:json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()
H=lambda b:hashlib.sha256(b).hexdigest()
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
def diffs(a,b,path=''):
 if isinstance(a,dict) and isinstance(b,dict):return sum((diffs(a[k],b[k],path+'/'+k) for k in a),[])
 if isinstance(a,list) and isinstance(b,list):return sum((diffs(x,y,path+'/'+str(i)) for i,(x,y) in enumerate(zip(a,b))),[])
 return [] if a==b else [path]
x=json.loads(fixture_request().raw);p=json.loads(x['decisions'][0]['portfolio_request_utf8']);p['policy'].update(mode='LONG_SHORT',gross='0.4',net='0');x['decisions'][0]['portfolio_request_utf8']=canonical(p).decode();request=EngineeringBacktestRequest.create(x)
(R/'request.json').write_bytes(request.raw);original=service.Simulator;records=[]
for kind in ['CONTROL','CONTRACT_ERROR','KEYBOARD_INTERRUPT']:
 case=R/kind;case.mkdir()
 class Fault(Simulator):
  def __init__(self,config,root,commit):
   def fault(stage):
    if stage!='AFTER_COMMIT':return
    path=sorted((root/'transactions').glob('commit-*.json'))[-1];raw=path.read_bytes();item=json.loads(raw);s=dec(item['post_state'])
    if item['payload']!={'session':2} or not s['cashlots']:return
    cashlot=next((c for c in s['cashlots'] if c['kind']=='SHORT' and c['settled'] and c['amount']>1),None)
    if cashlot is None:return
    (case/'valid-commit-before.json').write_bytes(raw)
    if kind!='CONTROL':
     entry=next(l for a in s['assets'].values() for l in a['lots'] if l['id']==cashlot['entry_id'])
     assert entry['remaining']==1 and entry['price']==Q('99.9')
     cashlot['amount']-=1;entry['price']-=1
    item['post_state']=enc(s);item['post_hash']=H(canonical(item['post_state']));item['sha256']=H(canonical({k:v for k,v in item.items() if k!='sha256'}));path.write_bytes(canonical(item));(case/'commit-at-fault.json').write_bytes(path.read_bytes())
    raise (KeyboardInterrupt if kind=='KEYBOARD_INTERRUPT' else ContractError)('INDEPENDENT_SETTLED_SHORT_BACKING_FAULT')
   super().__init__(config,root,commit,fault=fault)
 service.Simulator=Fault
 try:wire=service.simulate_engineering(request,case/'runs',FIX)
 finally:service.Simulator=original
 out=wire.read();(case/'actual-return.json').write_bytes(wire.raw);root=case/'runs'/out['run_id']
 before=dec(json.loads((case/'valid-commit-before.json').read_bytes())['post_state']);after=dec(json.loads((case/'commit-at-fault.json').read_bytes())['post_state'])
 changed=diffs(before,after)
 assert changed==([] if kind=='CONTROL' else ['/cashlots/0/amount','/assets/SYNTH:1/lots/0/price']) or set(changed)==({'/cashlots/0/amount','/assets/SYNTH:1/lots/0/price'} if kind!='CONTROL' else set()),changed
 assert before['journal']==after['journal'] and before['fills']==after['fills']
 fills=[f for f in before['fills'] if f['signed_qty']<0];assert len(fills)==1 and fills[0]['signed_qty']==-1 and fills[0]['price']==Q('99.9')
 # Original committed Fill and settlement/session prove 99.9 is restricted, not mutable lot price.
 balances={'cash_set':Q(1000),'U_free':Q(0),'U_short':Q(0)}
 for e in before['journal']:
  for line in e['entries']:
   if line['unit']=='CCY' and line['account'] in balances:balances[line['account']]+=line['amount']
 expected_set=-fills[0]['signed_qty']*fills[0]['price'];expected_available=balances['cash_set']-expected_set-Q(100)
 assert balances==dict(cash_set=Q('997.8'),U_free=0,U_short=0) and expected_set==Q('99.9') and expected_available==Q('797.9')
 previous=H((root/'transactions/initial.json').read_bytes());prestate=json.loads((root/'transactions/initial.json').read_bytes())
 for index,path in enumerate(sorted((root/'transactions').glob('commit-*.json')),1):
  raw=path.read_bytes();item=json.loads(raw);assert canonical(item)==raw and item['commit_seq']==index and item['previous']==previous and item['pre_hash']==H(canonical(prestate)) and item['post_hash']==H(canonical(item['post_state'])) and item['sha256']==H(canonical({k:v for k,v in item.items() if k!='sha256'}));previous=item['sha256'];prestate=item['post_state']
 assert sorted((root/'transactions').glob('commit-*.json'))[-1].read_bytes()==(case/'commit-at-fault.json').read_bytes()
 for e in out['manifest']['files']:assert H((root/e['path']).read_bytes())==e['sha256']
 getter=service.result_engineering(case/'runs',out['run_id']);assert getter=={k:v for k,v in out.items() if k!='manifest'}
 recon,_=service._reconciled_account(after)
 try:service.projection(after);normal='ACCEPTED'
 except ContractError as exc:normal=exc.code
 known=out['committed_state_verification']['financial_state_known'];expected_known=kind=='CONTROL'
 records.append(dict(case=kind,status=out['status'],verification=out['committed_state_verification']['status'],financial_state_known=known,expected_financial_state_known=expected_known,known_account_present='last_committed_account' in out,expected_known_account_present=expected_known,original_fill_price='99.9',original_Journal_cash_set='997.8',correct_S_set=str(expected_set),correct_available=str(expected_available),claimed_S_set=out.get('last_committed_account',{}).get('S_set'),claimed_available=out.get('last_committed_account',{}).get('available'),changed_state_fields=changed,raw_Journal_and_Fills_unchanged=True,hash_chain_manifest_getter_verified=True,core_gate_accepted=True,normal_full_projection=normal,artifact_root=str(case),result='PASS' if known==expected_known else 'REPRODUCED_MISMATCH'))
report=dict(fixed_sha=FIX,executor='GPT Work supplemental reviewer',installed_aqrp=__import__('aqrp').__file__,records=records,result='REPRODUCED_MISMATCH' if any(r['result']!='PASS' for r in records) else 'PASS',scope='Synthetic public service AFTER_COMMIT recovery financial consistency, no native privileges or formal Test')
(O/'SETTLED_SHORT_BACKING_PROBE.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(report,ensure_ascii=False))
