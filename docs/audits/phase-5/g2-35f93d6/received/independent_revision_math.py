"""Reviewer-written independent G1 model. Fraction cash state and lot-pool models;
does not import AQRP, the developer checker, or developer expected computation.
Candidate inputs are read first; expected literals are used only for comparison.
These models do NOT execute the future queue, ledger, recovery or OS controls.
"""
from fractions import Fraction as F
from dataclasses import dataclass, field
from copy import deepcopy
from pathlib import Path
import json, hashlib, random
O=Path(__file__).parent; P=Path('E:/WORK/AQRP-audits/p5-35f93d6/src/docs/audits/phase-5')
FIX='35f93d640a2304121131d947a465f57a951cf63f'
def cent(x): return F((x*100+F(1,2))//1,100)
def up(x): return F(-((-x*100)//1),100)
def down(x): return F((x*100)//1,100)
def fee(q,p): return cent(max(F(1),q*p/1000))
def bound(q,u): return q*up(max(F(1),u/1000))

@dataclass
class Cash:
 settled:F
 q:F=F(0)
 free:F=F(0)
 short:F=F(0)
 restricted:F=F(0)
 mark:F=F(0)
 payable:F=F(0)
 receivable:F=F(0)
 orders:F=F(0)
 other:F=F(0)
 def total(self): return self.settled+self.free+self.short
 def margin(self): return max(-self.q,0)*self.mark
 def equity(self): return self.total()+self.q*self.mark+self.receivable-self.payable
 def available(self): return self.settled-self.restricted-self.margin()-self.orders-self.payable-self.other
 def settle(self):
  self.settled+=self.free+self.short; self.restricted+=self.short; self.free=self.short=F(0)
 def sell(self,n,p,commission):
  closing=min(max(self.q,0),n); self.free+=closing*p; self.short+=(n-closing)*p
  self.settled-=commission; self.q-=n
 def buy(self,n,p,commission,entry_price):
  closing=min(max(-self.q,0),n); released=closing*entry_price
  # In these one-opening-cashlot cases, the lot is wholly settled or wholly unsettled.
  if self.short: self.short-=released; self.free+=released
  else: self.restricted-=released
  self.settled-=n*p+commission; self.q+=n
 def projection(self,unused):
  c=self.total()-(self.free+self.short+self.orders+self.payable+unused)
  v=self.margin(); z=self.other+max(self.restricted-v,0)
  return c-2*v-z,max(v-self.restricted,0)

@dataclass
class Lot:
 qty:F
 price:F
 pools:dict=field(default_factory=dict)
 def consume(self,n):
  assert 0<n<=self.qty
  take={k:v*n/self.qty for k,v in self.pools.items()}
  self.qty-=n; self.pools={k:v-take[k] for k,v in self.pools.items()}; return take

def close_fifo(lots,n,price,commission,side=1):
 left=n; output=[]
 for lot in lots:
  if not left: break
  if not lot.qty: continue
  qty=min(lot.qty,left); costs=lot.consume(qty)
  net=side*qty*(price-lot.price)-commission*qty/n
  net-=costs.get('entry_fee',0)+costs.get('borrow',0)+costs.get('short_div',0)
  net+=costs.get('long_div',0); output.append(net); left-=qty
 assert left==0
 return output

def stat(nets):
 positive=[v for v in nets if v>0]; negative=[v for v in nets if v<0]
 win=F(len(positive),len(nets)) if nets else 'UNDEFINED'
 reason=('NO_CLOSED_FRAGMENTS' if not nets else 'NO_NONZERO_OUTCOMES' if not positive and not negative else 'NO_WINNERS' if not positive else 'NO_LOSERS' if not negative else None)
 ratio=reason or (sum(positive)/len(positive))/(-sum(negative)/len(negative))
 return win,ratio

def compute(i,x):
 q=lambda k:F(x[k])
 if i=='N01':
  c=q('cash');p=q('price');f=q('fee');ca=c-p-f;cb=ca-p-f;ea=ca+p;eb=cb+2*p;aa=p/ea<=q('limit');bb=2*p/eb<=q('limit')
  return dict(after_A_cash=ca,after_A_equity=ea,A_weight=p/ea,B_candidate_cash=cb,B_candidate_equity=eb,B_weight=2*p/eb,A_pass=aa,B_pass=bb,actual_fills=int(aa)+int(bb),final_cash=ca if not bb else cb,final_qty=1+int(bb),capacity_left=q('capacity')-1-int(bb))
 if i=='N02':
  outer=sorted(x['envelopes'],key=lambda a:tuple(a[:3])); trace=[e[3] for e in outer]
  # Derive versions from committed parents, never put 80/90 back into outer sorting.
  v=0;children=[];keys=[];bread=None
  for _,stage,_,name in outer:
   if stage==65: v+=1
   if stage==70:
    if name.startswith('A:'): v+=1;children=[80,90];keys=[(v,j) for j in [1,2]]
    elif name.startswith('B:'): bread=v;v+=1
  return dict(outer_trace=trace,A_child_local_stages=children,A_replay_keys=keys,B_reads_version=bread)
 if i=='N03':
  pre=dict(cash=q('cash_before'),reserved=q('reserved_before_A'),capacity=q('capacity'))
  post=deepcopy(pre);cost=q('qty')*q('price')+q('fee');post['cash']-=cost;post['reserved']-=cost;post['capacity']-=q('qty')
  seen=set();applied=[]
  for identity in ['fill_A','fill_A']:
   if identity not in seen: seen.add(identity);applied.append(post)
  return dict(before_commit_cash=pre['cash'],before_commit_reserved=pre['reserved'],before_commit_capacity=pre['capacity'],after_commit_cash=post['cash'],after_commit_reserved=post['reserved'],after_commit_capacity=post['capacity'],retry_additional_cash_debit=0,retry_total_fills=len(applied))
 if i=='N04':
  s=Cash(q('cash'),mark=q('mark'));s.sell(q('qty'),q('price'),q('fee'));b=deepcopy(s);s.settle();bf,bh=b.projection(q('fee_unused'));af,ah=s.projection(q('fee_unused'))
  return dict(C_total=s.total(),equity=s.equity(),before_C_set=b.settled,before_U_short=b.short,before_S_set=b.restricted,before_available=b.available(),after_C_set=s.settled,after_U_short=s.short,after_S_set=s.restricted,after_available=s.available(),P4_before_free=bf,P4_after_free=af,H_before=bh,H_after=ah)
 if i in ['N05','N06']:
  initial=q('initial_cash') if i=='N05' else q('cash');n=q('short_qty') if i=='N05' else q('qty');s=Cash(initial,mark=q('mark') if i=='N05' else q('cover_price'));s.sell(n,q('entry_price'),q('entry_fee'));before=s.available();settled_first=deepcopy(s);settled_first.settle()
  cover=q('cover_qty') if i=='N05' else n;s.buy(cover,q('cover_price'),q('cover_fee'),q('entry_price'));b=deepcopy(s);s.settle();settled_first.buy(cover,q('cover_price'),q('cover_fee'),q('entry_price'))
  if i=='N06': return dict(before_settlement_C_set=b.settled,U_free=b.free,U_short=b.short,S_set=b.restricted,equity=b.equity(),before_available=b.available(),after_settlement_available=s.available())
  return dict(before_available=before,after_cover_C_set=b.settled,after_cover_U_short=b.short,after_cover_U_free=b.free,after_cover_total_cash=b.total(),after_cover_equity=b.equity(),after_cover_available=b.available(),after_settlement_C_set=s.settled,after_settlement_S_set=s.restricted,after_settlement_available=s.available(),settle_then_cover_available=settled_first.available())
 if i=='N07':
  s=Cash(q('cash'),q('old_long_qty'),mark=q('price'));s.sell(q('sell_qty'),q('price'),q('fee'));b=deepcopy(s);s.settle()
  return dict(qty=b.q,C_set=b.settled,U_free=b.free,U_short=b.short,total_cash=b.total(),equity=b.equity(),available_before=b.available(),available_after_settlement=s.available())
 if i=='N08':
  s=Cash(q('initial_cash'),mark=q('price'));s.sell(q('old_short_qty'),q('entry_price'),q('entry_fee'));s.buy(q('buy_qty'),q('price'),q('fee'),q('entry_price'));b=deepcopy(s);s.settle()
  return dict(qty=b.q,C_set=b.settled,U_free=b.free,U_short=b.short,total_cash=b.total(),equity=b.equity(),available_before=b.available(),available_after_settlement=s.available(),long_sellable_before=0,long_sellable_after=s.q)
 if i=='N09':
  s=Cash(q('C_set'),q=-1,mark=q('V'),restricted=q('S_set'),payable=q('payable'),receivable=q('receivable'));a=s.available();e=s.equity();f=s.projection(q('fee_unused'))[0];s.settled-=s.payable;s.payable=F(0);a2=s.available();e2=s.equity();f2=s.projection(q('fee_unused'))[0];s.settled+=s.receivable;s.receivable=F(0)
  return dict(available_before=a,available_after_payable_payment=a2,equity_before=e,equity_after_payable_payment=e2,P4_free_before=f,P4_free_after_payable_payment=f2,available_after_receivable_payment=s.available())
 if i=='N10':
  e=q('initial_cash')-q('fee_unused');v=q('target_short_qty')*q('price');c=e+v
  return dict(P4_equity_alloc=e,P4_target_cash=c,V=v,P4_target_free=c-2*v,**{'pass':c>=2*v})
 if i=='N11':
  unused=q('F_total')-q('F_paid')-q('O_F');reserved=q('O_N')+q('O_F');s=Cash(q('C_set'),orders=reserved);c=s.settled-reserved-unused
  return dict(F_unused=unused,O_total=reserved,available=s.available(),C_alloc=c,P4_free=s.projection(unused)[0],cash_excluded_for_budget=s.settled-c)
 if i in ['N12','N13','N14']:
  lo=up(q('p0')*F(95,100));hi=down(q('p0')*F(105,100));buy=x['side']=='BUY';actual=up(q('raw')*F(1001,1000)) if buy else down(q('raw')*F(999,1000));eligible=lo<=q('raw')<=hi and lo<=actual<=hi;u=hi
  if x['type']=='LIMIT':
   if buy: u=min(hi,q('limit'));eligible=eligible and max(q('raw'),actual)<=q('limit')
   else: eligible=eligible and min(q('raw'),actual)>=q('limit')
  f=fee(q('qty'),actual)
  return dict(L=lo,U=hi,actual_price=actual,U_eff=u,H=bound(q('qty'),u),counterfactual_fee=f,eligible=eligible,charged_fee=f if eligible else 0)
 if i=='N15':
  paid=F(0);r=q('quantity');pp=[];hh=[]
  for p in map(F,x['actual_prices']): paid+=fee(F(1),p);r-=1;pp.append(paid);hh.append(bound(r,q('U_eff')))
  return dict(paid=pp,H_remaining=hh,paid_plus_H=[a+b for a,b in zip(pp,hh)],total_charged=paid,fee_unused=q('F_total')-paid-hh[-1])
 if i=='N16':
  h=bound(q('quantity'),q('U_eff'));first=q('first_fill_fee');new=bound(q('quantity')-1,q('U_eff'))
  return dict(initial_H=h,insufficient_submission_accepted=h<=q('insufficient_F'),insufficient_fills=0,after_first_paid=first,H_before_cancel=new,H_after_cancel=0,unused_after_cancel=q('F_total')-first,fee_paid_after_cancel=first)
 if i=='N17':
  ok=q('paid')+q('candidate_fee')+q('new_H')<=q('F_total')
  return dict(accepted=ok,paid_after=q('paid')+(q('candidate_fee') if ok else 0),H_after=q('new_H') if ok else q('old_H'),charged_now=q('candidate_fee') if ok else 0)
 if i=='N18':
  lots=[Lot(q('entry_qty'),q('entry_price'),{'entry_fee':q('entry_fee')})];nets=[]
  for n,p,f in zip(map(F,x['exit_quantities']),map(F,x['exit_prices']),map(F,x['exit_fees'])): nets.extend(close_fifo(lots,n,p,f))
  w,r=stat(nets)
  return dict(nets=nets,closed_fragments=len(nets),wins=sum(v>0 for v in nets),losses=sum(v<0 for v in nets),win_rate=w,profit_loss_ratio=r,sum_net=sum(nets))
 if i=='N19':
  a=Lot(q('A_qty'),q('A_entry'),{'entry_fee':q('A_entry_fee'),'borrow':q('day1_fee')});b=Lot(q('B_qty'),F(0),{'borrow':F(0)})
  for l in [a,b]: l.pools['borrow']+=q('day2_fee')*l.qty/(a.qty+b.qty)
  ab=a.pools['borrow'];bb=b.pools['borrow'];nets=close_fifo([a],a.qty,q('A_exit'),q('A_exit_fee'),-1)
  return dict(A_borrow=ab,B_unclosed_borrow=bb,A_closed_net=nets[0],wins=sum(v>0 for v in nets),closed_fragments=len(nets),ratio_reason=stat(nets)[1])
 if i=='N20':
  l=Lot(q('initial_qty'),F(0),{'borrow':q('day1_fee')});first=l.consume(q('first_close_qty'))['borrow'];l.pools['borrow']+=q('day2_fee');last=l.consume(l.qty)['borrow']
  return dict(first_fragment_borrow=first,second_fragment_borrow=last,sum_borrow=first+last)
 if i=='N21':
  total=q('close_qty')+q('open_qty');cf=q('total_fill_fee')*q('close_qty')/total;of=q('total_fill_fee')-cf;lots=[Lot(F(1),F(p),{'entry_fee':F(f)}) for p,f in zip(x['entry_prices'],x['entry_fees'])];nets=close_fifo(lots,q('close_qty'),q('fill_price'),cf,-1)
  return dict(exit_fee_closed=cf,new_open_entry_fee=of,fragment_nets=nets,closed_net_sum=sum(nets),all_including_open_fee=sum(nets)-of,allocated_fill_fee_sum=cf+of)
 if i=='N22':
  l=Lot(q('entry_qty'),q('entry_price'),{'entry_fee':q('entry_fee'),'long_div':q('dividend_total')});nets=[];div=[]
  for p,f in zip(map(F,x['exit_prices']),map(F,x['exit_fees'])): div.append(l.pools['long_div']/l.qty);nets.extend(close_fifo([l],F(1),p,f))
  w,r=stat(nets)
  return dict(fragment_nets=nets,dividend_allocated=div,win_rate=w,profit_loss_ratio=r,sum_net=sum(nets),pay_date_incremental_income=0)
 if i=='N23':
  l=Lot(F(1),q('entry_price'),{'entry_fee':q('entry_fee'),'short_div':q('dividend_payable')});net=close_fifo([l],F(1),q('exit_price'),q('exit_fee'),-1)[0];c=q('cash_after_entry')-q('exit_price')-q('exit_fee');e=c-q('dividend_payable');paid=c-q('dividend_payable')
  return dict(closed_net=net,cash_before_pay=c,equity_before_pay=e,cash_after_pay=paid,equity_after_pay=paid,net_change_at_pay=paid-e)
 if i=='N24':
  sets=[list(map(F,n)) for n in x['net_sets']];stats=[stat(n) for n in sets]
  return dict(closed_counts=list(map(len,sets)),win_rates=[s[0] for s in stats],ratio_results=[s[1] for s in stats])
 if i=='N25':
  whole=cent(q('qty')*q('mark')*q('annual_rate')/q('A'));parts=[whole*F(n)/q('qty') for n in x['lot_quantities']]
  return dict(actual_cash_fee=whole,lot_allocations=parts,allocation_sum=sum(parts),round_each_lot_first_allowed=sum(cent(v) for v in parts)==whole)
 raise AssertionError(i)

raw=(P/'SUPPLEMENTAL_CANDIDATES.json').read_bytes();cases=json.loads(raw)['cases'];records=[];count=0
def compare(a,b,path,tol):
 global count
 if isinstance(b,dict):
  assert set(a)==set(b),(path,set(a),set(b))
  for k in b: compare(a[k],b[k],path+'.'+k,tol)
 elif isinstance(b,list):
  assert len(a)==len(b),path
  for j,(v,w) in enumerate(zip(a,b)): compare(v,w,path+f'[{j}]',tol)
 else:
  if isinstance(b,bool): assert type(a) is bool and a==b,(path,a,b)
  else:
   try: target=F(b)
   except (ValueError,TypeError): assert a==b,(path,a,b)
   else: assert abs(F(a)-target)<=tol,(path,str(a),b)
  count+=1
def serial(v):
 if isinstance(v,F): return str(v)
 if isinstance(v,dict): return {k:serial(x) for k,x in v.items()}
 if isinstance(v,(list,tuple)): return [serial(x) for x in v]
 return v
for case in cases:
 actual=compute(case['id'],case['inputs']);compare(actual,case['expected'],case['id'],F(case['absolute_tolerance']))
 records.append({'id':case['id'],'actual_exact':serial(actual),'tolerance':case['absolute_tolerance'],'result':'PASS'})

# Additional independent invariants across states, prices, fee partitions and FIFO pools.
extension=[]
def add(name,n,scope): extension.append({'name':name,'scenarios':n,'result':'PASS','scope':scope})
rng=random.Random(5262032)
for _ in range(500):
 initial=F(rng.randrange(100000,1000000));n=F(rng.randrange(2,100));entry=F(rng.randrange(1,10000),100);mark=F(rng.randrange(1,10000),100);cover=F(rng.randrange(1,int(n)));unused=F(rng.randrange(0,100));s=Cash(initial,mark=mark);s.sell(n,entry,F(1));a=s.available();e=s.equity();p,h=s.projection(unused);assert p==a-unused-h
 b=deepcopy(s);b.settle();assert b.available()==a and b.equity()==e
 s.buy(cover,mark,F(1),entry);s.settle();b.buy(cover,mark,F(1),entry);assert s==b
add('short settlement invariant, cover order commutation, projection identity',500,'One opening cashlot with variable prices and quantities')
for _ in range(1000):
 v=F(rng.randrange(0,100000),100);restricted=F(rng.randrange(0,100000),100);s=Cash(F(10000),q=-1,mark=v,restricted=restricted,orders=F(rng.randrange(0,100)),payable=F(rng.randrange(0,100)),other=F(rng.randrange(0,10)));u=F(rng.randrange(0,50));p,h=s.projection(u);assert p==s.available()-u-h
 before=s.available();eq=s.equity();s.settled-=s.payable;s.payable=F(0);assert s.available()==before and s.equity()==eq
add('general S_set versus margin cases and payable payment',1000,'Arithmetic incl S<V, S=V, S>V; H is not real cash')
fee_cases=0
for u in map(F,['0.01','1','105','1000','1000.01','99999.99']):
 for quantity in range(1,31):
  left=quantity;paid=F(0);budget=bound(F(quantity),u)
  while left:
   n=rng.randint(1,left);price=u*F(rng.randint(1,1000),1000);paid+=fee(F(n),price);left-=n;assert paid+bound(F(left),u)<=budget;fee_cases+=1
add('fee ceiling across partial-fill partitions',fee_cases,'Any positive integer fill qty and actual price<=U_eff; cent rounding/minimum fee')
for _ in range(300):
 n=F(rng.randrange(2,40));pools={'entry_fee':F(rng.randrange(1,100),100),'borrow':F(rng.randrange(1,100),100),'long_div':F(rng.randrange(1,100),100)};l=Lot(n,F(100),pools.copy());taken={k:F(0) for k in pools}
 while l.qty:
  take=l.consume(F(rng.randint(1,int(l.qty))))
  for k in pools: taken[k]+=take[k]; assert taken[k]+l.pools[k]==pools[k]
 assert taken==pools
add('historical FIFO pool conservation under partial closes',300,'Exact fee/borrow/dividend pools consumed without cent loss')
# Split changes remaining qty and price but never resets accrued pool amounts.
l=Lot(F(3),F(100),{'entry_fee':F(1),'borrow':F(1,100)});l.qty*=2;l.price/=2
first=l.consume(F(1));last=l.consume(F(5));assert all(first[k]+last[k]==v for k,v in {'entry_fee':F(1),'borrow':F(1,100)}.items())
add('split and partial attribution',1,'Accrued pools remain amounts; share units alone change')
for sign in [1,-1]:
 lots=[Lot(F(2),F(100),{'entry_fee':F(1)}),Lot(F(3),F(110),{'entry_fee':F(2)})];nets=close_fifo(lots,F(4),F(105),F(1),sign);assert len(nets)==2;assert lots[0].qty==0 and lots[1].qty==1;assert lots[1].pools['entry_fee']==F(2,3)
 assert sum(nets)==sign*(F(2)*(105-100)+F(2)*(105-110))-F(1)-F(4,3)-1
add('multi-entry one-close FIFO fragment denominator and residual fee',2,'Two intersections count twice for either direction')
result={'fixed_sha':FIX,'executor':'GPT Work supplemental reviewer','scope':'Independent G1 design arithmetic/models only; not P5 product, crash recovery or native permission tests','candidate_sha256':hashlib.sha256(raw).hexdigest(),'cases':len(records),'leaf_assertions':count,'results':records,'extensions':extension,'result':'PASS'}
(O/'REVISION_MATH_RESULTS.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'cases':len(records),'leaf_assertions':count,'extension_groups':len(extension),'extension_scenarios':sum(e['scenarios'] for e in extension),'result':'PASS'}))
