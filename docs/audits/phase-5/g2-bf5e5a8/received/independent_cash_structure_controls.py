"""Reviewer-authored exact controls. AQRP is the subject; expected values are literals/Fraction.
No developer test helpers/checker imported; no real ACL, account or formal Test operations.
"""
from pathlib import Path
from fractions import Fraction as Q
from copy import deepcopy
from itertools import permutations
import json,hashlib,uuid
from aqrp.backtest import ledger as L
from aqrp.backtest.engine import Simulator
from aqrp.backtest.synthetic import fixture_request
from aqrp.backtest.contracts import EngineeringBacktestRequest
from aqrp.core.errors import ContractError
import aqrp.services.backtest as service
O=Path(__file__).parent;R=Path('E:/WORK/AQRP-audits/p5-bf5e5a8/cash-structure-controls-rerun1');R.mkdir(exist_ok=False)
FIX='bf5e5a89209f2dd24042cd806626f832b531de52';records=[]
canonical=lambda x:json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()
H=lambda b:hashlib.sha256(b).hexdigest()
def enc(v):
 if isinstance(v,Q):return {'$fraction':[str(v.numerator),str(v.denominator)]}
 if isinstance(v,dict):return {k:enc(x) for k,x in v.items()}
 if isinstance(v,list):return [enc(x) for x in v]
 return v
def dec(v):
 if isinstance(v,dict):
  if set(v)=={'$fraction'}:return Q(*map(int,v['$fraction']))
  return {k:dec(x) for k,x in v.items()}
 if isinstance(v,list):return [dec(x) for x in v]
 return v
def rec(name,actual,expected,detail=None):records.append(dict(id=name,actual=enc(actual),expected=enc(expected),status='PASS' if actual==expected else 'MISMATCH',detail=detail))
def book():
 s=L.initial_state(Q(1000),[dict(security_id='A',lot='1',industry='I',beta='1',short_permission=True,borrow_limit='1000000')]);s['session']=0;s['assets']['A']['mark']=Q(100);return s
def fill(s,n,p=100,name=None,session=0):return L.trade(s,fill_id=name or str(uuid.uuid4()),sid='A',signed_qty=Q(n),p=Q(p),fee=Q(1),session=session,at='2024-02-01T09:00:00Z')
def projection_rejection(s):
 try:service.projection(s)
 except ContractError as exc:return exc.code
 return 'ACCEPTED'
def save_state(name,s):(R/(name+'.json')).write_bytes(canonical(enc(s)))
def transfer(s,source,dest):
 for key,amount in [(source,Q(-1)),(dest,Q(1))]:
  if key=='cash_set':s[key]+=amount
  else:
   kind='FREE' if key=='U_free' else 'SHORT';next(c for c in s['cashlots'] if c['kind']==kind and not c['settled'])['amount']+=amount

for source,dest in permutations(['cash_set','U_free','U_short'],2):
 s=book();fill(s,2,name='long');fill(s,-3,name='cross');valid=service.projection(s)
 assert [Q(valid['account'][k]) for k in ['cash_set','U_free','U_short']]==[798,200,100]
 transfer(s,source,dest);assert min(L.cash_values(s)[k] for k in ['cash_set','U_free','U_short'])>=0
 name='nonnegative-'+source+'-to-'+dest;save_state(name,s)
 rec(name,projection_rejection(s),'RAW_JOURNAL_ACCOUNT_RECONCILIATION_FAILED')
s=book();s['assets']['B']=deepcopy(s['assets']['A']);fill(s,1,name='long-r')
L.trade(s,fill_id='short-p',sid='B',signed_qty=Q(-1),p=Q(100),fee=Q(1),session=0,at='2024-02-01T09:00:00Z')
L.accrue(s,'r','A',Q(7),kind='DIVIDEND_EX');L.accrue(s,'p','B',Q(-3),kind='DIVIDEND_EX')
valid=service.projection(s);rec('legal-RP-separately',[Q(valid['account'][k]) for k in ['receivable','payable','equity']],[Q(7),Q(3),Q(1002)])
s['rights']['r']['amount']+=1;s['rights']['p']['amount']-=1;save_state('RP-netting-fault',s)
rec('RP-netting-fault',projection_rejection(s),'RAW_JOURNAL_ACCOUNT_RECONCILIATION_FAILED')

for settled in [False,True]:
 for ratio in [1,2]:
  s=book();fill(s,-2,name='short')
  if ratio==2:L.split(s,'split','A',Q(2))
  if settled:L.settle(s,1,'first-settle')
  fill(s,ratio,Q(90,ratio),name='cover')
  r=service.projection(s);c=r['account'];expected=[1108,0,0,100] if settled else [908,100,100,0]
  rec('legal-partial-cover-'+str(settled)+'-split-'+str(ratio),[Q(c[k]) for k in ['cash_set','U_free','U_short','S_set']],list(map(Q,expected)))
  L.settle(s,1,'settle-final');c=service.projection(s)['account']
  rec('after-settle-'+str(settled)+'-'+str(ratio),[Q(c[k]) for k in ['cash_set','U_free','U_short','S_set']],[Q(1108),Q(0),Q(0),Q(100)])
  fill(s,ratio,Q(90,ratio),name='cover-rest',session=1);c=service.projection(s)['account'];rec('complete-cover-'+str(settled)+'-'+str(ratio),Q(c['S_set']),Q(0))
s=book();fill(s,-2,name='margin-short');s['assets']['A']['mark']=Q(1000);L.record_valuation(s,'A','mark-loss');r=service.projection(s)
rec('legitimate-marked-margin-loss',Q(r['account']['available']),Q(-1001))

for mode in ['price-only','amount-only','paired-price-and-amount']:
 s=book();fill(s,-2,name='original-short');L.settle(s,1,'settled');before=deepcopy(s)
 if mode!='amount-only':s['assets']['A']['lots'][0]['price']-=Q(1,2)
 if mode!='price-only':s['cashlots'][0]['amount']-=1
 name='settled-SHORT-'+mode;save_state(name+'-before',before);save_state(name+'-fault',s)
 code=projection_rejection(s);rec(name,code!='ACCEPTED',True,dict(code=code,original_fill_price='100',original_short_proceeds='200',expected_available='799',altered_S_set='199' if mode!='price-only' else '200',raw_Journal_unchanged=s['journal']==before['journal']))

for mode in ['missing-session','backward','bool-session','early-lot','late-lot','negative-lot','orphan','duplicate','missing-backing','due','negative-remainder','negative-price','S_set-subset']:
 s=book();fill(s,-2,name='short');L.settle(s,1,'settlement')
 c=s['cashlots'][0]
 if mode=='missing-session':s['journal'][-1].pop('settlement_session')
 elif mode=='backward':L.settle(s,0,'backwards')
 elif mode=='bool-session':s['journal'][-1]['settlement_session']=True
 elif mode=='early-lot':s['journal'][-1]['settlement_session']=0
 elif mode=='late-lot':c['settled']=False;s['cash_set']-=200
 elif mode=='negative-lot':c['amount']=-1
 elif mode=='orphan':c['entry_id']='orphan'
 elif mode=='duplicate':s['cashlots'].append({**c,'id':'duplicate'})
 elif mode=='missing-backing':s['cashlots']=[]
 elif mode=='due':c['due']=2
 elif mode=='negative-remainder':s['assets']['A']['lots'][0]['remaining']=-1
 elif mode=='negative-price':s['assets']['A']['lots'][0]['price']=-1
 elif mode=='S_set-subset':
  s['cash_set']-=1000;s['external_flows']-=1000
  s['journal'].append(dict(event_id='withdraw',kind='EXTERNAL_FLOW',entries=[dict(account='cash_set',unit='CCY',amount=Q(-1000)),dict(account='external_capital',unit='CCY',amount=Q(1000))]))
 code=projection_rejection(s);save_state(mode,s);rec(mode,code!='ACCEPTED',True,dict(code=code))

# Actual service, not a manually published fake result. All original Journal/Fills remain unchanged.
x=json.loads(fixture_request().raw);p=json.loads(x['decisions'][0]['portfolio_request_utf8']);p['policy'].update(mode='LONG_SHORT',gross='0.4',net='0');x['decisions'][0]['portfolio_request_utf8']=canonical(p).decode();request=EngineeringBacktestRequest.create(x)
(R/'request.json').write_bytes(request.raw);original=service.Simulator
for mode in ['settled-valid-fault','settled-price-only','settled-amount-only','settled-paired-price-and-amount']:
 case=R/mode;case.mkdir()
 class Fault(Simulator):
  def __init__(self,config,root,commit):
   def fault(stage):
    if stage!='AFTER_COMMIT':return
    path=sorted((root/'transactions').glob('commit-*.json'))[-1];raw=path.read_bytes();item=json.loads(raw);state=dec(item['post_state'])
    if not state['journal'] or state['journal'][-1]['kind']!='SETTLEMENT':return
    lots=[c for c in state['cashlots'] if c['kind']=='SHORT' and c['settled'] and c['amount']>1]
    if not lots:return
    cashlot=lots[0];assetlot=next(l for a in state['assets'].values() for l in a['lots'] if l['id']==cashlot['entry_id']);fill_original=next(f for f in state['fills'] if f['fill_id']==assetlot['id'])
    assert fill_original['price']==Q('99.9') and assetlot['remaining']==1 and cashlot['amount']==Q('99.9')
    (case/'valid-commit-before.json').write_bytes(raw)
    if mode in ['settled-price-only','settled-paired-price-and-amount']:assetlot['price']-=Q(1)/assetlot['remaining']
    if mode in ['settled-amount-only','settled-paired-price-and-amount']:cashlot['amount']-=1
    item['post_state']=enc(state);item['post_hash']=H(canonical(item['post_state']));item['sha256']=H(canonical({k:v for k,v in item.items() if k!='sha256'}));path.write_bytes(canonical(item));(case/'commit-at-fault.json').write_bytes(path.read_bytes())
    raise ContractError('INDEPENDENT_SETTLED_SHORT_BACKING_FAULT')
   super().__init__(config,root,commit,fault=fault)
 service.Simulator=Fault
 try:wire=service.simulate_engineering(request,case/'runs',FIX)
 finally:service.Simulator=original
 out=wire.read();(case/'actual-return.json').write_bytes(wire.raw);run=case/'runs'/out['run_id']
 before=dec(json.loads((case/'valid-commit-before.json').read_bytes())['post_state']);after=dec(json.loads((case/'commit-at-fault.json').read_bytes())['post_state'])
 balances={'cash_set':Q(1000),'U_free':Q(0),'U_short':Q(0)}
 for e in before['journal']:
  for line in e['entries']:
   if line['unit']=='CCY' and line['account'] in balances:balances[line['account']]+=line['amount']
 short_value=sum(max(-a['quantity']*a['mark'],Q(0)) for a in before['assets'].values())
 original_S_set=sum(c['amount'] for c in before['cashlots'] if c['kind']=='SHORT' and c['settled'])
 correct_A=balances['cash_set']-original_S_set-short_value
 assert correct_A==Q('797.9')
 expected_known=mode=='settled-valid-fault';known=out['committed_state_verification'].get('financial_state_known')
 actual={'status':out['status'],'known':known,'verification':out['committed_state_verification']['status'],'account_present':'last_committed_account' in out}
 expected={'status':'FAILED','known':expected_known,'verification':'VERIFIED_COMMITTED_PREFIX' if expected_known else 'UNVERIFIED_COMMITTED_STATE','account_present':expected_known}
 durable=sorted((run/'transactions').glob('commit-*.json'))[-1]
 assert durable.read_bytes()==(case/'commit-at-fault.json').read_bytes()
 assert before['journal']==after['journal'] and before['fills']==after['fills'] and out['reasons'][0]=='INDEPENDENT_SETTLED_SHORT_BACKING_FAULT'
 rec(mode,actual,expected,dict(original_Journal_buckets=enc(balances),original_S_set=str(original_S_set),original_fill_price='99.9',correct_available=str(correct_A),claimed_account=out.get('last_committed_account'),preserved_original_Journal_and_fills=True,preserved_commit_bytes=True,artifact_root=str(case)))
report=dict(fixed_sha=FIX,executor='GPT Work supplemental reviewer',scope='Installed wheel, synthetic cash/settlement fault controls; independently derived literal/Fraction expectations',records=records,PASS=sum(x['status']=='PASS' for x in records),MISMATCH=sum(x['status']=='MISMATCH' for x in records),artifact_root=str(R))
(O/'INDEPENDENT_CASH_STRUCTURE_CONTROLS.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:report[k] for k in ['fixed_sha','PASS','MISMATCH','artifact_root']}))
