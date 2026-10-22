"""G1 design arithmetic ONLY; standard-library reference, no AQRP imports."""
from fractions import Fraction as F
from decimal import Decimal as D,localcontext,ROUND_HALF_UP,ROUND_CEILING,ROUND_FLOOR
from pathlib import Path
import json,hashlib,sys,platform
from datetime import datetime,UTC
BASE=Path(__file__).parent
raw=(BASE/'GOLDEN_CANDIDATES.json').read_bytes();cases=json.loads(raw)['cases'];results=[];count=0
def dec(f):return D(f.numerator)/D(f.denominator)
def evaluate(c):
 x=c['inputs'];k=c['kind'];v={a:F(b) for a,b in x.items() if isinstance(b,str) and b not in ('BUY','SELL')}
 if k=='fill':
  cash=v['cash']-v['fill_qty']*v['price']-v['fee'];qty=v['qty']+v['fill_qty'];return dict(cash=cash,qty=qty,equity=cash+qty*v['mark'])
 if k=='partial':
  qty=sum(map(F,x['fills']));fees=F(len(x['fills']))*v['fee_per_fill'];return dict(cash=v['cash']-qty*v['price']-fees,qty=qty,fees=fees)
 if k=='average':
  total=v['old_qty']+v['added_qty'];cost=(v['old_qty']*v['old_cost']+v['added_qty']*v['price'])/total;return dict(average_cost=cost,remaining_qty=total-v['closed_qty'],realized_gross=v['closed_qty']*(v['exit_price']-cost))
 if k=='restriction':return dict(available_cash=v['settled_cash']-v['order_reserved']-v['short_proceeds']-v['short_mark_value']-v['other'])
 if k=='fee':return dict(fee=dec(max(v['minimum'],abs(v['quantity']*v['price'])*v['rate'])).quantize(D('.01'),rounding=ROUND_HALF_UP))
 if k=='slippage':
  sign=1 if x['side']=='BUY' else -1;ideal=v['raw_open']*(1+sign*v['bps']/10000);units=ideal/v['tick'];ticks=-(-units.numerator//units.denominator) if sign==1 else units.numerator//units.denominator;price=ticks*v['tick'];return dict(price=price,slippage_cost=sign*v['qty']*(price-v['raw_open']))
 if k=='split':return dict(qty=v['qty']*v['ratio'],cost=v['cost']/v['ratio'],equity=v['cash']+v['qty']*v['ratio']*v['post_mark'])
 if k in ('dividend','pay'):
  cash=v['cash'];r=v['receivable'];p=v['payable']
  if k=='dividend':r+=max(v['qty'],0)*v['cash_per_share'];p+=max(-v['qty'],0)*v['cash_per_share']
  else:cash+=r-p;r=p=F(0)
  return dict(cash=cash,receivable=r,payable=p,equity=cash+v['qty']*v['mark']+r-p)
 if k=='borrow':return dict(fee=dec(v['short_qty']*v['raw_mark']*v['annual_rate']/v['A']).quantize(D('.01'),rounding=ROUND_HALF_UP))
 if k=='capacity':
  left=v['capacity'];fills=[]
  for q in map(F,x['orders']):
   limit=min(q,left)/v['lot'];fill=(limit.numerator//limit.denominator)*v['lot'];fills.append(str(fill));left-=fill
  return dict(fills=fills,remaining_capacity=left)
 if k=='projection':return dict(equity_trade=v['cash']+v['positions_value'],equity_total=v['cash']+v['positions_value']+v['receivable']-v['payable'],payable_reserve=v['payable'])
 if k=='budget_projection':
  B=v['unsettled']+v['order_reserved']+v['payable']+v['fee_budget'];cash=v['cash']-B;nonshort=v['other']+max(v['short_proceeds']-v['short_mark'],0);p5=v['cash']-v['unsettled']-v['order_reserved']-v['payable']-v['short_proceeds']-v['short_mark']-v['other']
  return dict(B=B,cash_alloc=cash,equity_alloc=cash+v['positions_value'],equity_total=v['cash']+v['positions_value']+v['receivable']-v['payable'],P4_nonshort_restriction=nonshort,P4_budget_free=cash-v['short_mark']*2-nonshort,P5_actual_free=p5,after_fee_budget=p5-v['fee_budget'])
 if k=='external_flow':
  assert v['after_flow']==v['before_flow']+v['flow'];a=v['before_flow']/v['initial']-1;b=v['final']/v['after_flow']-1;return dict(return_first=a,return_second=b,twr=(1+a)*(1+b)-1)
 if k=='performance':
  e=list(map(F,x['equity']));r=[b/a-1 for a,b in zip(e,e[1:])];mean=sum(r)/len(r);var=sum((a-mean)**2 for a in r)/(len(r)-1);peak=e[0];mdd=F(0)
  for value in e:peak=max(peak,value);mdd=max(mdd,1-value/peak)
  return dict(cumulative_return=e[-1]/e[0]-1,maximum_drawdown=mdd,sample_variance=var,sharpe=dec(mean)/dec(var).sqrt()*D(x['A']).sqrt())
 if k=='turnover':
  full=sum(abs(F(n)) for n in x['notionals'])/v['decision_equity'];return dict(full=full,half=full/2)
 if k=='large_exact':
  units=v['E']/v['price']/v['lot'];q=(units.numerator//units.denominator)*v['lot'];return dict(qty=q,cash=v['E']-q*v['price'])
 raise AssertionError(k)
with localcontext() as ctx:
 ctx.prec=100
 for c in cases:
  result=evaluate(c);assert set(result)==set(c['expected'])
  for key,exp in c['expected'].items():
   if isinstance(exp,list):assert result[key]==exp,(c['id'],key,result[key],exp)
   else:
    actual=dec(result[key]) if isinstance(result[key],F) else result[key];assert abs(actual-D(exp))<=D(c['absolute_tolerance']),(c['id'],key,str(actual),exp)
   count+=1
  results.append({'id':c['id'],'status':'PASS','actual':{k:str(v) for k,v in result.items()},'basis':c['calculation_basis']})
record={'scope':'Developer G1 design arithmetic; NOT P5 implementation tests or independent GPT Work review','executor':'Codex developer','UTC':datetime.now(UTC).isoformat(),'python':sys.version,'platform':platform.platform(),'candidates_sha256':hashlib.sha256(raw).hexdigest(),'cases':len(results),'assertions':count,'failed':0,'results':results}
out=Path(sys.argv[1]) if len(sys.argv)>1 else BASE/'REFERENCE_CHECK.json';out.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n');print(json.dumps({k:record[k] for k in ('scope','cases','assertions','failed')}))
