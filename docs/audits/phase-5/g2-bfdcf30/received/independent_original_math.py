"""GPT Work independent design arithmetic; stdlib only, no AQRP or developer checker import."""
import pathlib,json,hashlib,math,datetime,sys,platform
from fractions import Fraction as Q
from decimal import Decimal,localcontext
O=pathlib.Path(__file__).parent;C=pathlib.Path('E:/WORK/AQRP-audits/p5-bfdcf30/src');P=C/'docs/audits/phase-5';raw=(P/'GOLDEN_CANDIDATES.json').read_bytes();cases=json.loads(raw)['cases'];results=[];checks=0
def round_cent(q):return Q((q*100+Q(1,2)).numerator//(q*100+Q(1,2)).denominator,100)
def floor_lot(x,lot):return (x//lot)*lot
def compute(c):
 x=c['inputs'];q=lambda k:Q(x[k]);i=c['id']
 if i in ('G01','G02','G05','G06'):
  newcash=q('cash')-q('fill_qty')*q('price')-q('fee');newq=q('qty')+q('fill_qty');return {'cash':newcash,'qty':newq,'equity':newcash+newq*q('mark')}
 if i=='G03':
  cash=q('cash');quantity=Q(0);fees=Q(0)
  for amount in x['fills']:amount=Q(amount);cash-=amount*q('price')+q('fee_per_fill');quantity+=amount;fees+=q('fee_per_fill')
  return {'cash':cash,'qty':quantity,'fees':fees}
 if i=='G04':
  costsum=q('old_qty')*q('old_cost')+q('added_qty')*q('price');quantity=q('old_qty')+q('added_qty');cost=costsum/quantity;return {'average_cost':cost,'remaining_qty':quantity-q('closed_qty'),'realized_gross':q('closed_qty')*(q('exit_price')-cost)}
 if i in ('G07','G08'):return {'available_cash':q('settled_cash')-sum(q(k) for k in ['order_reserved','short_proceeds','short_mark_value','other'])}
 if i in ('G09','G10'):return {'fee':round_cent(max(q('minimum'),q('quantity')*q('price')*q('rate')))}
 if i in ('G11','G12'):
  signed=1 if x['side']=='BUY' else -1;ticks=q('raw_open')*(1+signed*q('bps')/10000)/q('tick');integer=-(-ticks//1) if signed>0 else ticks//1;px=integer*q('tick');return {'price':px,'slippage_cost':signed*q('qty')*(px-q('raw_open'))}
 if i=='G13':return {'qty':q('qty')*q('ratio'),'cost':q('cost')/q('ratio'),'equity':q('cash')+q('qty')*q('ratio')*q('post_mark')}
 if i in ('G14','G15','G16','G17'):
  cash=q('cash');r=q('receivable');p=q('payable')
  if i in ('G14','G16'):
   if q('qty')>=0:r+=q('qty')*q('cash_per_share')
   else:p-=q('qty')*q('cash_per_share')
  else:cash+=r-p;r=p=Q(0)
  return {'cash':cash,'receivable':r,'payable':p,'equity':cash+q('qty')*q('mark')+r-p}
 if i=='G18':return {'fee':round_cent(q('short_qty')*q('raw_mark')*q('annual_rate')/q('A'))}
 if i=='G19':
  left=q('capacity');filled=[]
  for amount in x['orders']:f=floor_lot(min(left,Q(amount)),q('lot'));left-=f;filled.append(f)
  return {'fills':filled,'remaining_capacity':left}
 if i=='G20':return {'equity_trade':q('cash')+q('positions_value'),'equity_total':q('cash')+q('positions_value')+q('receivable')-q('payable'),'payable_reserve':q('payable')}
 if i=='G21':
  assert q('after_flow')==q('before_flow')+q('flow');r1=q('before_flow')/q('initial')-1;r2=q('final')/q('after_flow')-1;return {'return_first':r1,'return_second':r2,'twr':(1+r1)*(1+r2)-1}
 if i=='G22':
  values=list(map(Q,x['equity']));rr=[values[j]/values[j-1]-1 for j in range(1,len(values))];mean=sum(rr)/len(rr);variance=(sum(v*v for v in rr)-sum(rr)**2/len(rr))/(len(rr)-1);peak=values[0];dd=Q(0)
  for value in values:peak=max(peak,value);dd=max(dd,(peak-value)/peak)
  with localcontext() as ctx:ctx.prec=90;sharpe=Decimal(mean.numerator)/Decimal(mean.denominator)/(Decimal(variance.numerator)/Decimal(variance.denominator)).sqrt()*Decimal(x['A']).sqrt()
  return {'cumulative_return':values[-1]/values[0]-1,'maximum_drawdown':dd,'sample_variance':variance,'sharpe':Q(sharpe)}
 if i=='G23':t=sum(abs(Q(a)) for a in x['notionals'])/q('decision_equity');return {'full':t,'half':t/2}
 if i=='G24':quantity=floor_lot(q('E')/q('price'),q('lot'));return {'qty':quantity,'cash':q('E')-quantity*q('price')}
 if i=='G25':
  B=sum(q(k) for k in ['unsettled','order_reserved','payable','fee_budget']);cash=q('cash')-B;extra=q('other')+max(q('short_proceeds')-q('short_mark'),0);free=q('cash')-sum(q(k) for k in ['unsettled','order_reserved','payable','short_proceeds','short_mark','other']);return {'B':B,'cash_alloc':cash,'equity_alloc':cash+q('positions_value'),'equity_total':q('cash')+q('positions_value')+q('receivable')-q('payable'),'P4_nonshort_restriction':extra,'P4_budget_free':cash-2*q('short_mark')-extra,'P5_actual_free':free,'after_fee_budget':free-q('fee_budget')}
 raise AssertionError(i)
for c in cases:
 actual=compute(c);assert set(actual)==set(c['expected']);tol=Q(c['absolute_tolerance'])
 for key,value in actual.items():
  if isinstance(value,list):assert value==list(map(Q,c['expected'][key]))
  else:assert abs(value-Q(c['expected'][key]))<=tol,(c['id'],key,str(value),c['expected'][key])
  checks+=1
 results.append({'id':c['id'],'expected_source':'literal candidate JSON','computed_by':'independent Fraction/integer formulas; Decimal90 sqrt only','actual_exact':{k:[str(a) for a in v] if isinstance(v,list) else str(v) for k,v in actual.items()},'tolerance':c['absolute_tolerance'],'result':'PASS'})

save={'fixed_sha':'bfdcf30e525ff802ea483974f58163eedc029ce8','scope':'Reexecuted independent original25/70 design arithmetic only; no historical ambiguity countermodels rerun as current findings','cases':len(results),'assertions':checks,'results':results,'golden_sha256':hashlib.sha256(raw).hexdigest(),'result':'PASS'}
(O/'ORIGINAL_MATH_RESULTS.json').write_text(json.dumps(save,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'cases':len(results),'assertions':checks,'result':'PASS'}))
