"""Independent context-aware controls. Actual on-disk TransactionStore prefixes;
Fraction model/literal answers are independent of AQRP/its reference checker.
Low-level fixtures do not claim order-risk/native permission execution.
"""
from pathlib import Path
from fractions import Fraction as Q
from copy import deepcopy
from itertools import permutations
import json,uuid,hashlib
from aqrp.backtest import ledger as L
from aqrp.backtest.transactions import TransactionStore
from aqrp.backtest.exact import thaw
from aqrp.core.errors import ContractError
from aqrp.services.backtest import projection
O=Path(__file__).parent;R=Path('E:/WORK/AQRP-audits/p5-1c5a7e6/backing-controls');R.mkdir(exist_ok=False)
FIX='1c5a7e62cace7c3e66b7cc7f12fd564cb0013654';records=[];comparisons=0
def enc(v):
 if isinstance(v,Q):return str(v)
 if isinstance(v,dict):return {k:enc(x) for k,x in v.items()}
 if isinstance(v,(list,tuple)):return [enc(x) for x in v]
 return v
def record(name,a,e,detail=None):records.append(dict(id=name,actual=enc(a),expected=enc(e),status='PASS' if a==e else 'MISMATCH',detail=detail))
def save(name,v):(R/(name+'.json')).write_text(json.dumps(enc(v),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
class History:
 def __init__(self,name,cash=1000,sids=('A',)):
  self.root=R/name;self.session=-1;self.seq=0
  self.store=TransactionStore(self.root,L.initial_state(Q(cash),[dict(security_id=sid,lot='1',industry='I',beta='1',short_permission=True,borrow_limit='1000000') for sid in sids]))
  self.settle(0);self.market(100)
 def commit(self,kind,payload,fn,phase):
  self.seq+=1;at='2024-02-%02dT09:00:00Z'%(self.session+1);key=[at,phase,self.seq]
  self.store.commit(str(uuid.uuid4()),payload,key,fn)
 def settle(self,n):
  self.session=n
  def apply(s):s['session']=n;L.settle(s,n,'settle-'+str(self.seq));return [dict(kind='AccountUpdated')]
  self.commit('AccountUpdated',dict(session=n),apply,10)
 def market(self,p):
  rows=[dict(security_id=sid,price=str(p)) for sid in self.store.state['assets']]
  def apply(s):
   for sid in s['assets']:s['assets'][sid]['mark']=Q(p);L.record_valuation(s,sid,'market-'+str(self.seq)+'-'+sid)
   return [dict(kind='MarketConfirmed')]
  self.commit('MarketConfirmed',dict(rows=rows),apply,20)
 def fill(self,n,p=100,sid='A'):
  entry=str(uuid.uuid4());at='2024-02-%02dT09:00:00Z'%(self.session+1)
  def apply(s):return [dict(kind='Fill',fill=L.trade(s,fill_id=entry,sid=sid,signed_qty=Q(n),p=Q(p),fee=Q(1),session=self.session,at=at))]
  self.commit('Fill',{},apply,70)
 def split(self,ratio):
  def apply(s):L.split(s,'split-'+str(self.seq),'A',Q(ratio));return [dict(kind='SPLIT')]
  self.commit('SPLIT',dict(security_id='A',value=str(ratio)),apply,10)
 def recover(self,p):
  entry=str(uuid.uuid4());at='2024-02-%02dT09:00:00Z'%(self.session+1)
  def apply(s):L.liquidate(s,event_id=entry,sid='A',recovery_price=Q(p),session=self.session,at=at);return [dict(kind='DELIST')]
  self.commit('DELIST',dict(action_id=entry,security_id='A',value=str(p)),apply,10)
 def right(self,sid,amount):
  entry=str(uuid.uuid4())
  def apply(s):L.accrue(s,entry,sid,Q(amount),kind='DIVIDEND_EX');return [dict(kind='DIVIDEND_EX')]
  self.commit('DIVIDEND_EX',dict(security_id=sid,amount=str(amount)),apply,10);return entry
 def snapshot(self):
  s,rs,_=self.store.verified_snapshot()
  previous=hashlib.sha256((self.root/'initial.json').read_bytes()).hexdigest()
  for i,r in enumerate(rs,1):assert r['commit_seq']==i and r['previous']==previous;previous=r['sha256']
  return s,rs
 def output(self):s,rs=self.snapshot();return projection(s,rs)
def reject(s,rs):
 try:projection(s,rs)
 except ContractError as exc:return exc.code
 return 'ACCEPTED'
def same(name,a,b):
 global comparisons
 comparisons+=len(a) if isinstance(a,list) else 1
 record(name,a,b)

# Independent model: deferred free cash, original short gross, average cost and FIFO.
class Model:
 def __init__(self):self.cash=Q(10000);self.lots=[];self.free=[];self.session=0;self.mark=Q(100);self.cost=Q(0)
 def qty(self):return sum((l['sign']*l['n'] for l in self.lots),Q(0))
 def trade(self,n,p,fee=1):
  n,p=Q(n),Q(p);old=self.qty();closed=min(abs(old),abs(n)) if old*n<0 else Q(0);opened=abs(n)-closed
  self.cash-=n*p+fee if n>0 else fee
  if n<0 and closed:self.free.append([closed*p,self.session+1])
  todo=closed
  for l in self.lots:
   if not todo or l['sign']*n>0:continue
   k=min(todo,l['n'])
   if l['sign']<0 and l['due']>self.session:self.free.append([k*l['p'],l['due']])
   l['n']-=k;todo-=k
  assert todo==0
  if n<0 and opened:pass
  if opened:self.lots.append(dict(sign=1 if n>0 else -1,n=opened,p=p,due=self.session+1))
  new=old+n
  if not new:self.cost=Q(0)
  elif not old or old*new<0:self.cost=p
  elif old*n>0:self.cost=(abs(old)*self.cost+abs(n)*p)/abs(new)
 def split(self,r):
  for l in self.lots:l['n']*=r;l['p']/=r
  self.cost/=r;self.mark/=r
 def settle(self,n):
  old=self.session
  self.cash+=sum((l['n']*l['p'] for l in self.lots if l['sign']<0 and old<l['due']<=n),Q(0))
  self.cash+=sum((a for a,d in self.free if d<=n),Q(0));self.free=[(a,d) for a,d in self.free if d>n];self.session=n
 def account(self):
  us=sum((l['n']*l['p'] for l in self.lots if l['sign']<0 and l['due']>self.session),Q(0));ss=sum((l['n']*l['p'] for l in self.lots if l['sign']<0 and l['due']<=self.session),Q(0));uf=sum((a for a,d in self.free),Q(0));mv=self.qty()*self.mark
  return [self.cash,uf,us,ss,self.cash+uf+us,self.cash+uf+us+mv,self.cash-ss-max(-mv,Q(0))]
keys=['cash_set','U_free','U_short','S_set','cash_total','equity','available']
for seq in [(-2,-3,1,4),(2,3,-1,-6,2),(-2,5,-4)]:
 for settle_first in [False,True]:
  for ratio in [1,2]:
   for recovery in [0,80]:
    name='model-'+str(len(records));h=History(name,cash=10000);m=Model()
    for i,n in enumerate(seq):
     if i==1:
      if ratio==2:h.split(2);m.split(2)
      if settle_first:h.settle(1);m.settle(1)
     h.fill(n,100+i);m.trade(n,100+i);out=h.output();same(name+'-fill-'+str(i),[Q(out['account'][k]) for k in keys],m.account())
     s,_=h.snapshot();same(name+'-quantity-cost-'+str(i),[s['assets']['A']['quantity'],s['assets']['A']['cost']],[m.qty(),m.cost])
    h.settle(2);m.settle(2);same(name+'-settled',[Q(h.output()['account'][k]) for k in keys],m.account())
    q=m.qty();h.recover(recovery)
    if q:m.trade(-q,recovery,0)
    out=h.output();same(name+'-corporate-recovery',[Q(out['account'][k]) for k in keys],m.account())

for source,dest in permutations(['cash_set','U_free','U_short'],2):
 h=History('bucket-'+source+'-'+dest);h.fill(2);h.fill(-3);s,rs=h.snapshot();assert [Q(h.output()['account'][k]) for k in keys[:3]]==[798,200,100]
 for key,a in [(source,Q(-1)),(dest,Q(1))]:
  if key=='cash_set':s[key]+=a
  else:next(c for c in s['cashlots'] if c['kind']==('FREE' if key=='U_free' else 'SHORT') and not c['settled'])['amount']+=a
 save('bucket-'+source+'-'+dest,s);same('nonnegative-bucket-'+source+'-'+dest,reject(s,rs),'RAW_JOURNAL_ACCOUNT_RECONCILIATION_FAILED')
h=History('RP',sids=('A','B'));h.fill(1);h.fill(-1,sid='B');r=h.right('A',7);p=h.right('B',-3);out=h.output();same('legal-RP',[Q(out['account'][k]) for k in ['receivable','payable','equity']],[Q(7),Q(3),Q(1002)])
s,rs=h.snapshot();s['rights'][r]['amount']+=1;s['rights'][p]['amount']-=1;same('RP-offset',reject(s,rs),'RAW_JOURNAL_ACCOUNT_RECONCILIATION_FAILED')
h=History('margin');h.fill(-2);h.market(1000);same('legal-negative-available',Q(h.output()['account']['available']),Q(-1001))
for mode in ['missing','duplicate-source','copy-price','paired-price','pair-and-copy','borrow-pool','missing-session','backward','early-lot','late-lot','negative-lot','orphan','duplicate-lot','missing-backing','due','negative-remainder','negative-price']:
 h=History('fault-'+mode);h.fill(-2);h.settle(1);s,rs=h.snapshot()
 if mode=='missing':rs=None
 elif mode=='duplicate-source':rs.append(deepcopy(rs[-2]))
 elif mode=='copy-price':s['fills'][0]['price']-=1
 elif mode in ['paired-price','pair-and-copy']:
  s['assets']['A']['lots'][0]['price']-=Q(1,2);s['cashlots'][0]['amount']-=1
  if mode=='pair-and-copy':s['fills'][0]['price']-=Q(1,2)
 elif mode=='borrow-pool':s['assets']['A']['lots'][0]['borrow']+=1
 elif mode=='missing-session':s['journal'][-1].pop('settlement_session')
 elif mode=='backward':s['journal'][-1]['settlement_session']=-1
 elif mode=='early-lot':s['journal'][-1]['settlement_session']=0
 elif mode=='late-lot':s['cashlots'][0]['settled']=False;s['cash_set']-=200
 elif mode=='negative-lot':s['cashlots'][0]['amount']=-1
 elif mode=='orphan':s['cashlots'][0]['entry_id']='orphan'
 elif mode=='duplicate-lot':s['cashlots'].append({**s['cashlots'][0],'id':'dup'})
 elif mode=='missing-backing':s['cashlots']=[]
 elif mode=='due':s['cashlots'][0]['due']=2
 elif mode=='negative-remainder':s['assets']['A']['lots'][0]['remaining']=-1
 elif mode=='negative-price':s['assets']['A']['lots'][0]['price']=-1
 code=reject(s,rs);same(mode,code!='ACCEPTED',True);save('fault-'+mode,dict(state=s,rejection=code))
report=dict(fixed_sha=FIX,executor='GPT Work supplemental reviewer',scope='Context-aware low-level actual durable transactions and independent Fraction model; actual public-service fault tests separately executed',records=records,PASS=sum(x['status']=='PASS' for x in records),MISMATCH=sum(x['status']=='MISMATCH' for x in records),financial_scalar_comparisons=comparisons,artifact_root=str(R))
(O/'INDEPENDENT_BACKING_CONTROLS.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:report[k] for k in ['fixed_sha','PASS','MISMATCH','financial_scalar_comparisons','artifact_root']}))
