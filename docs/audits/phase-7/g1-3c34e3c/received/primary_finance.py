"""Independent exact event simulator for the finite engineering design; no AQRP imports."""
import json,hashlib,itertools
from pathlib import Path
from fractions import Fraction as F
O=Path(__file__).parent; P=Path('E:/WORK/AQRP-audits/p7-3c34e3c/src/docs/audits/phase-7')
src=Path('C:/Users/11638/AppData/Local/Packages/OpenAI.Codex_2p2nqsd0c76g0/LocalCache/Local/AQRP/runs/p6-release-p7-plan-20261024/p7-draft/FINANCIAL_MODEL_ALL_PATHS.json')
raw=src.read_bytes(); sh=hashlib.sha256(raw).hexdigest(); assert sh=='74d968f318172afa21df2def55a393bcf00efb22531f5c47ee60420364153980'
paths=json.loads(raw)['paths']; ref=json.loads((P/'FINANCIAL_FEASIBILITY_CANDIDATES.json').read_bytes()); math=json.loads((O/'PRIMARY_MATH.json').read_bytes())
assets=[f'SYN_A:{a:03}' for a in range(1,7)]
seqs={f:[s['top'][f] for s in math['sections'][::2]] for f in ['momentum','reversal']};seqs['adversarial_nine_switches']=[assets[i%2] for i in range(10)]
checks=0;snapshots=0;minima={};maxturn=F(0);seen=set()
def chk(v,msg):
 global checks
 checks+=1
 if not v:raise AssertionError(msg)
def equal(a,b,msg):
 if type(a)is dict:
  chk(set(a)==set(b),msg+'keys')
  for k in a:equal(a[k],b[k],msg+'/'+k)
 elif type(a)is list:
  chk(len(a)==len(b),msg+'len')
  for x,y in zip(a,b):equal(x,y,msg)
 elif isinstance(a,F):chk(a==F(b),msg)
 else:chk(a==b,msg)
def risk(target,old,eq,cash):
 vals={a:target[a]*100 for a in assets}; marked=sum(vals.values())
 return dict(passed=True,errors=[],equity_alloc=eq,free_cash=cash-marked,max_asset_weight=max(vals.values())/eq,gross=marked/eq,turnover=sum(abs(target[a]-old[a])*100 for a in assets)/eq)
for path in paths:
 name=path['sequence']; choices=tuple(path['choices']); seq=seqs[name]; res=path['result']; switches=sum(a!=b for a,b in zip(seq,seq[1:])); chk(len(choices)==switches,'choice length')
 key=(name,choices);chk(key not in seen,'duplicate path');seen.add(key)
 cash=F(1000); pos=dict.fromkeys(assets,F(0)); lots=[]; orders=[]; budget=None; paid=F(0); fees=F(0);slip=F(0);trace_i=0;fill_i=0;decision_i=0;choice_i=0;queue=[];decision_eq=F(1000);turn=F(0)
 def account():
  un=sum((x['amount'] for x in lots),F(0)); market=sum(pos.values())*100
  on=sum((x['quantity']*105 for x in orders if x['side']=='BUY'),F(0));of=sum((x['quantity'] for x in orders),F(0))
  unused=F(0) if budget is None else max(F(0),budget-paid-of);available=cash-on-of;alloc=available-unused
  return dict(cash_set=cash,U_free=un,U_short=F(0),S_set=F(0),cash_total=cash+un,marked_value=market,O_N=on,O_F=of,F_unused=unused,short_value=F(0),P_res=F(0),Z=F(0),available=available,cash_alloc=alloc,equity_alloc=alloc+market,equity=cash+un+market)
 def snapshot(day,stage):
  global snapshots,trace_i
  t=res['trace'][trace_i]; trace_i+=1; snapshots+=1
  chk(t['day_index']==day and t['stage']==stage,'stage schedule');a=account()
  equal(a,t['account'],'account');equal(pos,t['positions'],'positions');equal(lots,t['cashlots'],'cashlots')
  equal(orders,t['live_orders'],'orders');equal(budget,t['budget'],'budget');equal(paid,t['paid_this_decision'],'paid');equal(fees,t['cumulative_fees'],'fees');equal(slip,t['cumulative_slippage'],'slip')
  for k,v in a.items():minima[k]=min(v,minima.get(k,v))
  chk(a['cash_set']>=0 and a['available']>=0 and a['cash_alloc']>=0,'no unavailable cash')
  chk(a['equity']>=F('973.4'),'true equity bound')
 for day in range(1,23):
  cash+=sum((x['amount'] for x in lots if x['due']<=day),F(0));lots=[x for x in lots if x['due']>day]
  snapshot(day,'SETTLEMENT_OPEN')
  if queue:
   for order in queue:
    old=pos.copy(); side=order['side']; sid=order['sid'];qty=order['quantity'];chk(qty==4 and qty<=10,'capacity/full lot')
    price=F('100.1') if side=='BUY' else F('99.9');notional=price*qty
    if side=='BUY':cash-=notional+1;pos[sid]+=qty
    else:
     cash-=1;pos[sid]-=qty;lots.append({'amount':notional,'due':day+1})
    orders.remove(order);paid+=1;fees+=1;slip+=F(2,5);turn+=notional
    a=account(); r=risk(pos,old,a['equity_alloc'],a['cash_alloc']+a['marked_value'])
    equal(r,res['fills'][fill_i]['P4_post'],'postfill P4')
    chk(r['gross']<=1 and r['max_asset_weight']<=1 and r['turnover']<=4,'P4 admissibility')
    maxturn=max(maxturn,r['turnover'])
    f=dict(day_index=day,sid=sid,side=side,quantity=qty,actual_price=price,fee=F(1),sell_tax=F(0),slippage=F(2,5),P4_post=r,P5_post=dict(passed=True,errors=[],account=a,decision_turnover=turn,decision_equity=decision_eq))
    equal(f,res['fills'][fill_i],'full fill');fill_i+=1
    chk(turn/decision_eq<1,'true turnover bound')
    snapshot(day,'CANDIDATE_FILL')
   queue=[]
  snapshot(day,'CLOSE_VALUATION')
  if day in range(2,21,2):
   a=account(); eq=cash+sum(pos.values())*100-50; target=dict.fromkeys(assets,F(0));target[seq[decision_i]]=F(4)
   ideal=dict.fromkeys(assets,F(0));ideal[seq[decision_i]]=eq/200
   chk(ideal[seq[decision_i]]//1==4,'rounded target4')
   row=res['P4'][decision_i]; equal(ideal,row['ideal'],'ideal');equal(target,row['target'],'target')
   equal(risk(ideal,pos,eq,eq),row['P4_pre'],'preP4');equal(risk(target,pos,eq,eq),row['P4_post_rounding'],'rounded P4')
   chk(row['unavailable_long_sales']=={} and row['decision']==decision_i and row['selected']==seq[decision_i],'sellability/identity')
   budget=F(50);paid=F(0);turn=F(0);decision_eq=cash+sum(pos.values())*100
   orders=[dict(sid=a,side='BUY' if target[a]>pos[a] else 'SELL',quantity=abs(target[a]-pos[a])) for a in assets if target[a]!=pos[a]]
   # Developer orders are asset-ordered; actual fill order is independently enumerated.
   if len(orders)==2:
    c=choices[choice_i];choice_i+=1;queue=sorted(orders,key=lambda x:x['side']!=('BUY' if c=='BUY_FIRST' else 'SELL'))
   else:queue=orders.copy()
   snapshot(day,'ORDERS_ACCEPTED');decision_i+=1
 chk(trace_i==len(res['trace']) and fill_i==len(res['fills']) and choice_i==switches,'complete exact trace')
 equal(account(),res['final'],'final');equal(pos,res['positions'],'final positions')
 chk(fees==1+2*switches and slip==F(2,5)*fees,'closed form commission/slippage')
 chk(cash==F('598.6')-F('2.8')*switches,'closed form final cash')
 chk(res['required_P4']==10 and res['choices_used']==switches,'ten P4 slots')
for name,seq in seqs.items():
 n=sum(a!=b for a,b in zip(seq,seq[1:]));actual={c for k,c in seen if k==name};chk(actual==set(itertools.product(['BUY_FIRST','SELL_FIRST'],repeat=n)),'all permutations')
 sm=next(x for x in ref['summaries'] if x['name']==name);chk(sm['selected_sequence']==seq and sm['permutations']==2**n and sm['switches']==n,'summary')
bound=json.loads((P/'FINANCIAL_MODEL_BOUNDS.json').read_bytes())
for k,v in bound['minimum_exact'].items():
 if k.startswith('post_P4_'):continue
 equal(minima[k],v,'min '+k)
equal(maxturn,bound['maximum_exact']['post_P4_turnover'],'max postP4turn')
chk(F(400)/F('103.4')<4 and F('573.4')-420-8>0,'conservative analytic bound')
report={'executor':'Primary GPT Work independent exact event simulator','scope':'Design arithmetic only; not AQRP runtime or formal Test','source_bytes':len(raw),'source_sha256':sh,'paths':len(paths),'trace_snapshots':snapshots,'assertions':checks,'selected_sequences':seqs,'minima':{k:str(v) for k,v in minima.items()},'max_post_P4_turnover':str(maxturn),'main_final_cash':'579','main_final_equity':'979','adversarial_final_cash':'573.4','adversarial_equity':'973.4'}
(O/'PRIMARY_FINANCE.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(report))
