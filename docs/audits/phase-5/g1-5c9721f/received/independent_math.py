"""GPT Work independent design arithmetic; stdlib only, no AQRP or developer checker import."""
import pathlib,json,hashlib,math,datetime,sys,platform
from fractions import Fraction as Q
from decimal import Decimal,localcontext
O=pathlib.Path(__file__).parent;C=O.parent/'p5-g1-review-5c9721f';P=C/'docs/audits/phase-5';raw=(P/'GOLDEN_CANDIDATES.json').read_bytes();cases=json.loads(raw)['cases'];results=[];checks=0
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
# Independent extensions: these are design arithmetic/countermodels, NOT future product execution.
extra=[]
def add(name,**kw):extra.append({'name':name,**{k:str(v) for k,v in kw.items()}})
# 1. Simultaneously honoring the global priority tuple and an atomic Fill->Account pair.
events=[('A-Match',70,1),('B-Match',70,2),('A-Fill',80,3),('A-Account',90,4),('B-Fill',80,5),('B-Account',90,6)];global_order=[e[0] for e in sorted(events,key=lambda x:x[1:])];atomic_order=['A-Match','A-Fill','A-Account','B-Match','B-Fill','B-Account'];assert global_order!=atomic_order
add('global_priority_vs_atomic_child_events',global_order=global_order,atomic_order=atomic_order,classification='Scheduling design ambiguity, not an AQRP implementation failure')
# 2. New short proceeds remain economically restricted through settlement.
CASH=Q(1100);U=Q(100);S=Q(100);V=Q(100);literal_before=CASH-U-S-V;literal_after=CASH-S-V;disjoint_before=CASH-U-V # U is the same 100 units as restricted short proceeds.
assert (literal_before,literal_after,disjoint_before)==(800,900,900)
add('unsettled_short_proceeds_overlap',cash=CASH,unsettled_short=U,short_restricted_total=S,margin=V,literal_before=literal_before,literal_after=literal_after,disjoint_available=disjoint_before,classification='Requires bucket partition or an explicit additional temporary funding rule')
# 3. Upper-fee boundary on a favorable sell gap is not defined by a sell minimum.
decision=Q(100);sell_lower=Q(95);actual=Q(200000);maxfee=round_cent(actual*Q(1,1000));assumedfee=round_cent(max(Q(1),decision*Q(105,100)*Q(1,1000)));assert actual>=sell_lower and maxfee>assumedfee
add('sell_fee_upper_requires_upper_execution_bound',sell_lower=sell_lower,allowed_by_lower_bound=actual,actual_commission=maxfee,at_assumed_105percent_upper=assumedfee,classification='Requires explicit price upper bound or per-Fill fee-budget gate, not a product exploit')
# 4. Gross FIFO trade costs can have more than one attribution without accrual rules.
gross=Q(4,100);borrow_total=Q(8,100);by_lot=Q(2,100);fifo_all=Q(8,100)
add('FIFO_borrow_cost_attribution',gross=gross,pro_rata_lot_profit=gross-by_lot,all_charges_first_lot_profit=gross-fifo_all,classification='Two possible allocations produce different win/nonwin; policy needs freeze')
# Other boundary arithmetic (each pre-derived independent invariant).
for exponent in (34,35,40,100):
 E=Q(10**exponent);q=floor_lot(E,3);assert q==E-1 and E-q==1;add('large_exact_'+str(exponent),quantity=q,cash=E-q)
for numerator in (1005,1015,104999):
 x=Q(numerator,1000);rounded=round_cent(x);assert rounded*100==(x*100+Q(1,2))//1;add('cent_half_up_'+str(numerator),before=x,after=rounded)
# General budget identity and conservatism for disjoint inputs across S/V cases.
for C0,U0,O0,P0,F0,R0,S0,V0,Z0,MV in [(1200,50,0,2,10,4,200,180,0,-180),(1200,0,100,0,10,0,100,180,5,-180),(1000,0,0,10,10,30,0,0,0,200)]:
 B=U0+O0+P0+F0;Ea=C0-B+MV;Et=C0+MV+R0-P0;pa=C0-B-2*V0-Z0-max(S0-V0,0);pf=C0-U0-O0-P0-F0-S0-V0-Z0;assert Et==Ea+B+R0-P0 and pa<=pf;add('disjoint_budget_'+str(len(extra)),Ealloc=Ea,Etotal=Et,P4free=pa,P5_after_budget=pf)
# Cash-flow neutral subperiods, no trades and undefined statistics.
segments=[(Q(1000),Q(1000)),(Q(1500),Q(1500)),(Q(1200),Q(1200))];growth=Q(1)
for start,end in segments:growth*=end/start
assert growth==1;add('multiple_flow_zero_strategy_return',TWR=growth-1,conclusion='Flows +500 and -300 with no market change do not earn returns')
add('statistics_undefined_cases',sample0='sample insufficient',sample1='ddof1 insufficient',variance0='Sharpe undefined',equity_nonpositive='annual return undefined',closed_trades0='win_rate undefined')
save={'fixed_sha':'5c9721f96679f4d495b7b3b93af3e2e31e66ae62','actual_executor':'GPT Work supplemental reviewer','scope':'Independent G1 design math; no AQRP implementation executed','python':sys.version,'platform':platform.platform(),'golden_sha256':hashlib.sha256(raw).hexdigest(),'cases':len(results),'assertions':checks,'results':results,'independent_extensions':extra,'candidate_answers':'ALL_PASS','extensions_scope':'Countermodels identify places needing a single approved rule, not product test failures'}
(O/'INDEPENDENT_MATH_RESULTS.json').write_text(json.dumps(save,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({'candidate_cases':len(results),'literal_checks':checks,'independent_extensions':len(extra),'candidate_answers':'ALL_PASS'}))
