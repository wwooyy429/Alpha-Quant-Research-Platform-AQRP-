"""Developer G1 design arithmetic only. No AQRP import, event engine or product test."""
from fractions import Fraction as F
from pathlib import Path
from datetime import datetime, UTC
import hashlib, json, sys, platform

BASE=Path(__file__).parent
def floor(x):return x.numerator//x.denominator
def ceil(x):return -floor(-x)
def money(x):return F(floor(x*100+F(1,2)),100)
def upcent(x):return F(ceil(x*100),100)
def stats(nets):
 wins=[x for x in nets if x>0];loss=[x for x in nets if x<0]
 reason='NO_CLOSED_FRAGMENTS' if not nets else 'NO_NONZERO_OUTCOMES' if not wins and not loss else 'NO_WINNERS' if not wins else 'NO_LOSERS' if not loss else None
 return {'wins':F(len(wins)),'losses':F(len(loss)),'closed_fragments':F(len(nets)),'win_rate':F(len(wins),len(nets)) if nets else 'UNDEFINED','profit_loss_ratio':(sum(wins)/len(wins))/abs(sum(loss)/len(loss)) if reason is None else reason}
def reference(c):
 x=c['inputs'];v={k:F(a) for k,a in x.items() if isinstance(a,str) and a not in ('BUY','SELL','LIMIT','MARKET')};k=c['kind']
 if k=='atomic_risk':
  p,f,C=v['price'],v['fee'],v['cash'];aC=C-p-f;aE=aC+p;bC=aC-p-f;bE=bC+2*p
  a=p/aE<=v['limit'];b=2*p/bE<=v['limit'];assert a and not b
  return dict(after_A_cash=aC,after_A_equity=aE,A_weight=p/aE,B_candidate_cash=bC,B_candidate_equity=bE,B_weight=2*p/bE,A_pass=a,B_pass=b,actual_fills=F(1),final_cash=aC,final_qty=F(1),capacity_left=v['capacity']-1)
 if k=='trace':
  envelopes=sorted(x['envelopes'],key=lambda r:tuple(r[:3]))
  return dict(outer_trace=[r[3] for r in envelopes],A_child_local_stages=[80,90],A_replay_keys=[[2,1],[2,2]],B_reads_version=F(2))
 if k=='recovery_arithmetic':
  spent=v['price']*v['qty']+v['fee']
  return dict(before_commit_cash=v['cash_before'],before_commit_reserved=v['reserved_before_A'],before_commit_capacity=v['capacity'],after_commit_cash=v['cash_before']-spent,after_commit_reserved=v['reserved_before_A']-spent,after_commit_capacity=v['capacity']-v['qty'],retry_additional_cash_debit=F(0),retry_total_fills=F(1))
 if k=='short_settlement':
  n=v['qty']*v['price'];cs=v['cash']-v['fee'];V=v['qty']*v['mark'];total=cs+n;A=cs-V;Aafter=total-n-V
  beforeAlloc=cs-v['fee_unused'];afterAlloc=total-v['fee_unused'];beforeH=V;afterH=max(V-n,0)
  return dict(C_total=total,equity=total-V,before_C_set=cs,before_U_short=n,before_S_set=F(0),before_available=A,after_C_set=total,after_U_short=F(0),after_S_set=n,after_available=Aafter,P4_before_free=beforeAlloc-2*V,P4_after_free=afterAlloc-2*V-max(n-V,0),H_before=beforeH,H_after=afterH)
 if k=='partial_cover':
  cs=v['initial_cash']-v['entry_fee'];n=v['short_qty']*v['entry_price'];V=v['short_qty']*v['mark'];remaining=v['short_qty']-v['cover_qty'];released=v['cover_qty']*v['entry_price'];cs1=cs-v['cover_qty']*v['cover_price']-v['cover_fee'];us=n-released;uf=released;v1=remaining*v['mark'];settled=cs1+us+uf
  return dict(before_available=cs-V,after_cover_C_set=cs1,after_cover_U_short=us,after_cover_U_free=uf,after_cover_total_cash=settled,after_cover_equity=settled-v1,after_cover_available=cs1-v1,after_settlement_C_set=settled,after_settlement_S_set=us,after_settlement_available=settled-us-v1,settle_then_cover_available=(cs+n-v['cover_qty']*v['cover_price']-v['cover_fee'])-(n-released)-v1)
 if k=='full_cover_before_settlement':
  cs=v['cash']-v['entry_fee']-v['qty']*v['cover_price']-v['cover_fee'];uf=v['qty']*v['entry_price']
  return dict(before_settlement_C_set=cs,U_free=uf,U_short=F(0),S_set=F(0),equity=cs+uf,before_available=cs,after_settlement_available=cs+uf)
 if k=='cross_long_short':
  short=v['sell_qty']-v['old_long_qty'];cs=v['cash']-v['fee'];uf=v['old_long_qty']*v['price'];us=short*v['price'];V=us
  return dict(qty=-short,C_set=cs,U_free=uf,U_short=us,total_cash=cs+uf+us,equity=cs+uf+us-V,available_before=cs-V,available_after_settlement=cs+uf+us-us-V)
 if k=='cross_short_long':
  cs=v['initial_cash']-v['entry_fee']-v['buy_qty']*v['price']-v['fee'];uf=v['old_short_qty']*v['entry_price'];q=v['buy_qty']-v['old_short_qty'];total=cs+uf
  return dict(qty=q,C_set=cs,U_free=uf,U_short=F(0),total_cash=total,equity=total+q*v['price'],available_before=cs,available_after_settlement=total,long_sellable_before=F(0),long_sellable_after=q)
 if k=='payable_projection':
  A=v['C_set']-v['S_set']-v['V']-v['payable'];Aafter=v['C_set']-v['payable']-v['S_set']-v['V'];E=v['C_set']-v['V']+v['receivable']-v['payable'];H=max(v['V']-v['S_set'],0)
  return dict(available_before=A,available_after_payable_payment=Aafter,equity_before=E,equity_after_payable_payment=v['C_set']-v['payable']-v['V']+v['receivable'],P4_free_before=A-v['fee_unused']-H,P4_free_after_payable_payment=Aafter-v['fee_unused']-H,available_after_receivable_payment=Aafter+v['receivable'])
 if k=='initial_legal_short_target':
  E=v['initial_cash']-v['fee_unused'];V=v['target_short_qty']*v['price'];cash=E+V;free=cash-2*V
  return dict(P4_equity_alloc=E,P4_target_cash=cash,V=V,P4_target_free=free,**{'pass':free>=0})
 if k=='budget_partition':
  unused=v['F_total']-v['F_paid']-v['O_F'];O=v['O_N']+v['O_F'];a=v['C_set']-O;alloc=a-unused
  return dict(F_unused=unused,O_total=O,available=a,C_alloc=alloc,P4_free=alloc,cash_excluded_for_budget=O+unused)
 if k=='price_domain':
  L=F(ceil(v['p0']*F(95,100)*100),100);U=F(floor(v['p0']*F(105,100)*100),100)
  buy=x['side']=='BUY';actual=F(ceil(v['raw']*F(1001,1000)*100) if buy else floor(v['raw']*F(999,1000)*100),100)
  Ueff=min(U,v['limit']) if x['type']=='LIMIT' and buy else U
  eligible=L<=v['raw']<=U and L<=actual<=U
  if x['type']=='LIMIT':eligible=eligible and (max(v['raw'],actual)<=v['limit'] if buy else min(v['raw'],actual)>=v['limit'])
  H=v['qty']*upcent(max(F(1),Ueff/1000));fee=money(max(F(1),v['qty']*actual/1000))
  return dict(L=L,U=U,actual_price=actual,U_eff=Ueff,H=H,counterfactual_fee=fee,eligible=eligible,charged_fee=fee if eligible else F(0))
 if k=='partial_fee_budget':
  b=upcent(max(F(1),v['U_eff']/1000));remaining=v['quantity'];paid=F(0);ps=[];hs=[];totals=[]
  for p in map(F,x['actual_prices']):
   remaining-=1;paid+=money(max(F(1),p/1000));H=remaining*b;assert paid+H<=v['F_total'];ps.append(paid);hs.append(H);totals.append(paid+H)
  return dict(paid=ps,H_remaining=hs,paid_plus_H=totals,total_charged=paid,fee_unused=v['F_total']-paid)
 if k=='fee_submission_cancel':
  b=upcent(max(F(1),v['U_eff']/1000));H=v['quantity']*b;paid=v['first_fill_fee']
  return dict(initial_H=H,insufficient_submission_accepted=H<=v['insufficient_F'],insufficient_fills=F(0),after_first_paid=paid,H_before_cancel=(v['quantity']-1)*b,H_after_cancel=F(0),unused_after_cancel=v['F_total']-paid,fee_paid_after_cancel=paid)
 if k=='fee_overrun_injection':
  good=v['paid']+v['candidate_fee']+v['new_H']<=v['F_total']
  return dict(accepted=good,paid_after=v['paid']+(v['candidate_fee'] if good else 0),H_after=v['new_H'] if good else v['old_H'],charged_now=v['candidate_fee'] if good else F(0))
 if k=='fifo_fragments':
  quantities=list(map(F,x['exit_quantities']));nets=[q*(F(p)-v['entry_price'])-v['entry_fee']*q/v['entry_qty']-F(f) for q,p,f in zip(quantities,x['exit_prices'],x['exit_fees'])];out=stats(nets)
  return dict(nets=nets,**out,sum_net=sum(nets))
 if k=='borrow_lot_timing':
  A=v['day1_fee']+v['day2_fee']*v['A_qty']/(v['A_qty']+v['B_qty']);B=v['day2_fee']-v['day2_fee']*v['A_qty']/(v['A_qty']+v['B_qty']);net=v['A_entry']-v['A_exit']-v['A_entry_fee']-v['A_exit_fee']-A;st=stats([net])
  return dict(A_borrow=A,B_unclosed_borrow=B,A_closed_net=net,wins=st['wins'],closed_fragments=st['closed_fragments'],ratio_reason=st['profit_loss_ratio'])
 if k=='partial_borrow_pool':
  first=v['day1_fee']*v['first_close_qty']/v['initial_qty'];last=v['day1_fee']-first+v['day2_fee']
  return dict(first_fragment_borrow=first,second_fragment_borrow=last,sum_borrow=first+last)
 if k=='cross_zero_fee_stats':
  total=v['close_qty']+v['open_qty'];closedFee=v['total_fill_fee']*v['close_qty']/total;newFee=v['total_fill_fee']-closedFee
  nets=[F(p)-v['fill_price']-F(f)-closedFee/len(x['entry_prices']) for p,f in zip(x['entry_prices'],x['entry_fees'])]
  return dict(exit_fee_closed=closedFee,new_open_entry_fee=newFee,fragment_nets=nets,closed_net_sum=sum(nets),all_including_open_fee=sum(nets)-newFee,allocated_fill_fee_sum=closedFee+newFee)
 if k=='long_dividend_stats':
  credit=v['dividend_total']/v['entry_qty'];nets=[F(p)-v['entry_price']-v['entry_fee']/v['entry_qty']-F(f)+credit for p,f in zip(x['exit_prices'],x['exit_fees'])];st=stats(nets)
  return dict(fragment_nets=nets,dividend_allocated=[credit for _ in nets],win_rate=st['win_rate'],profit_loss_ratio=st['profit_loss_ratio'],sum_net=sum(nets),pay_date_incremental_income=F(0))
 if k=='short_dividend_stats':
  net=v['entry_price']-v['exit_price']-v['entry_fee']-v['exit_fee']-v['dividend_payable'];cash=v['cash_after_entry']-v['exit_price']-v['exit_fee'];e=cash-v['dividend_payable'];after=cash-v['dividend_payable']
  return dict(closed_net=net,cash_before_pay=cash,equity_before_pay=e,cash_after_pay=after,equity_after_pay=after,net_change_at_pay=F(0))
 if k=='undefined_stats':
  outputs=[stats(list(map(F,z))) for z in x['net_sets']]
  return dict(closed_counts=[z['closed_fragments'] for z in outputs],win_rates=[z['win_rate'] for z in outputs],ratio_results=[z['profit_loss_ratio'] for z in outputs])
 if k=='borrow_rational_allocation':
  fee=money(v['qty']*v['mark']*v['annual_rate']/v['A']);alloc=[fee*F(q)/v['qty'] for q in x['lot_quantities']]
  return dict(actual_cash_fee=fee,lot_allocations=alloc,allocation_sum=sum(alloc),round_each_lot_first_allowed=sum(money(a) for a in alloc)==fee)
 raise AssertionError(k)

assertions=0
def compare(actual,expected,path):
 global assertions
 if isinstance(expected,dict):
  assert set(actual)==set(expected),(path,'fields')
  for k in expected:compare(actual[k],expected[k],path+'.'+k)
 elif isinstance(expected,list):
  assert len(actual)==len(expected),(path,'length')
  for i,(a,e) in enumerate(zip(actual,expected)):compare(a,e,path+f'[{i}]')
 else:
  if isinstance(expected,bool):assert type(actual) is bool and actual is expected,(path,actual,expected)
  elif isinstance(expected,(int,str)):
   try:want=F(expected)
   except (ValueError,ZeroDivisionError):assert actual==expected,(path,actual,expected)
   else:assert not isinstance(actual,bool) and F(actual)==want,(path,actual,expected)
  else:raise AssertionError((path,'unknown expected type'))
  assertions+=1
def serial(x):
 if isinstance(x,F):return str(x)
 if isinstance(x,dict):return {k:serial(v) for k,v in x.items()}
 if isinstance(x,list):return [serial(v) for v in x]
 return x
raw=(BASE/'SUPPLEMENTAL_CANDIDATES.json').read_bytes();cases=json.loads(raw)['cases'];results=[]
for c in cases:
 actual=reference(c);compare(actual,c['expected'],c['id']);results.append({'id':c['id'],'status':'PASS','actual':serial(actual)})
record={'scope':'Developer G1 DESIGN arithmetic/trace only; NOT P5 implementation, actual crash test, native isolation or independent GPT Work approval','executor':'Codex developer','UTC':datetime.now(UTC).isoformat(),'python':sys.version,'platform':platform.platform(),'candidate_sha256':hashlib.sha256(raw).hexdigest(),'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'cases':len(results),'assertions':assertions,'failed':0,'results':results}
assert len(sys.argv)==2,'Pass explicit external evidence output'
Path(sys.argv[1]).write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
print(json.dumps({k:record[k] for k in ('scope','cases','assertions','failed')}))
