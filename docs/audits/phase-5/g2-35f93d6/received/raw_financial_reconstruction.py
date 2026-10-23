"""Reviewer stdlib raw-event + Journal reconstruction, separate from AQRP/checkers.
This independently checks the actual constant-price long-opening SDK scenarios;
short, FIFO and corporate lifecycle coverage is separately exercised by probes.
"""
from pathlib import Path
from fractions import Fraction as Q
from decimal import Decimal,localcontext
from datetime import datetime
import json,zipfile,hashlib
O=Path(__file__).parent;D=O.parent/'p5-g2-recheck-35f93d6';SDK=Path('E:/WORK/AQRP-runs/gpt-p5-35f93d6-20261023/aqrp-e6171f64-5e4a-47c3-b7df-d73eb4d05b2d')
def decode(v):
 if isinstance(v,dict):
  if set(v)=={'$fraction'}:return Q(*map(int,v['$fraction']))
  if set(v)=={'numerator','denominator','display'}:return Q(int(v['numerator']),int(v['denominator']))
  return {k:decode(x) for k,x in v.items()}
 if isinstance(v,list):return [decode(x) for x in v]
 return v
def q(v):return v if isinstance(v,Q) else Q(str(v))
def cent(v):return Q((v*100+Q(1,2))//1,100)
results=[];count=0
def same(a,b,where):
 global count
 assert a==b,(where,str(a),str(b));count+=1
def one(label,read,factor):
 start_count=count;request=json.loads(read('backtest/'+factor+'-request.json'));result=json.loads(read('backtest/'+factor+'-result.json'));rid=result['run_id'];prefix='backtest/'+factor+'-runs/'+rid+'/'
 txs=decode(json.loads(read(prefix+'transactions.json')));cash=Q(request['initial_cash']);qpos={a['security_id']:Q(0) for a in request['assets']};marks=qpos.copy();cost=qpos.copy();fees=Q(0);pending=[];session=-1;balances={'cash_set':cash,'U_free':Q(0),'U_short':Q(0)};jq=qpos.copy();seen=0
 for tx in txs:
  child=tx['children'][0]['kind'];p=tx['payload']
  if child=='AccountUpdated' and set(p)=={'session'}:
   session=p['session'];cash+=sum((a for a,due in pending if due<=session),Q(0));pending=[(a,due) for a,due in pending if due>session]
  elif child=='MarketConfirmed':
   for r in p['rows']:
    if r['price'] is not None:marks[r['security_id']]=q(r['price'])
  elif child=='Fill':
   f=tx['children'][0]['fill'];sid=f['security_id'];n=q(f['signed_qty']);price=q(f['price']);fee=q(f['fee']);raw=q(f['raw_price']);same(fee,cent(max(Q(1),abs(n)*price/1000)),label+' commission')
   ticks=raw*(Q(1001,1000) if n>0 else Q(999,1000))*100;expected=Q(-(-ticks//1) if n>0 else ticks//1,100);same(price,expected,label+' actual tick')
   assert n>0 and qpos[sid]>=0,'This independent SDK scenario oracle is scoped to actual long openings, not a generic product implementation'
   old=qpos[sid]
   same(f['position_before'],old,label+' actual before quantity');same(f['position_after'],old+n,label+' actual after quantity')
   same(f['execution_side'],'BUY',label+' execution side');same(f['direction'],'LONG',label+' exposure direction')
   same(f['position_legs'],[{'effect':'OPEN','direction':'LONG','quantity':n,'signed_qty':n,'fee':fee,'realized_gross':Q(0)}],label+' raw independently derived opening leg')
   cash-=n*price+fee;cost[sid]+=n*price;qpos[sid]+=n;fees+=fee
   order=tx['post_state']['orders'][p['order_id']];assert datetime.fromisoformat(order['submitted_at'])<datetime.fromisoformat(order['eligible_at'])<=datetime.fromisoformat(f['at'])
  elif child not in ['Valuation','CommissionBudgetRegistered','OrdersAccepted','OrdersRejected']:
   raise AssertionError(('Unexpected actual SDK scenario event',child))
  post=tx['post_state'];same(post['cash_set'],cash,label+' tx cash_set');same(post['fees'],fees,label+' tx fees');same(sum((c['amount'] for c in post['cashlots'] if not c['settled']),Q(0)),sum((a for a,due in pending),Q(0)),label+' tx pending')
  for sid in qpos:
   a=post['assets'][sid];same(a['quantity'],qpos[sid],label+' tx qty '+sid);same(a['quantity']*a['cost'],cost[sid],label+' tx cost '+sid);same(a['mark'],marks[sid],label+' tx mark '+sid)
  for event in post['journal'][seen:]:
   totals={}
   for e in event['entries']:
    totals[e['unit']]=totals.get(e['unit'],Q(0))+e['amount']
    if e['unit']=='CCY':balances[e['account']]=balances.get(e['account'],Q(0))+e['amount']
    elif e['account']=='position_quantity':jq[e['unit']]+=e['amount']
   assert all(v==0 for v in totals.values());count_before=count
  seen=len(post['journal']);same(balances['cash_set'],cash,label+' independent Journal cash');same(balances.get('commission_expense',Q(0)),fees,label+' independent Journal fees');same(jq,qpos,label+' independent Journal quantities');same(balances.get('positions_cost',Q(0)),sum(cost.values(),Q(0)),label+' independent Journal cost')
 equity=cash+sum((qpos[s]*marks[s] for s in qpos),Q(0));pnl=equity-Q(request['initial_cash']);perf=result['performance']
 same(q(result['account']['cash_total']),cash,label+' returned cash');same(q(result['account']['equity']),equity,label+' returned equity');same(q(perf['net_pnl']),pnl,label+' net PnL');same(q(perf['commission']),fees,label+' commission total')
 returns=[q(x) for x in perf['returns']];growth=Q(1)
 for r in returns:growth*=1+r
 same(growth,equity/Q(request['initial_cash']),label+' accumulated return');same(q(perf['cumulative_return']['value']),growth-1,label+' cumulative field')
 mean=sum(returns)/len(returns);var=sum((r-mean)**2 for r in returns)/(len(returns)-1);same(q(decode(perf['sample_variance']['value'])),var,label+' ddof1 variance')
 with localcontext() as ctx:
  ctx.prec=80;d=lambda v:Decimal(v.numerator)/Decimal(v.denominator)
  annual=(d(growth).ln()*Decimal(252)/len(returns)).exp()-1
  sharpe=d(mean)/d(var).sqrt()*Decimal(252).sqrt()
  assert abs(Decimal(str(perf['annual_return']['value']))-annual)<Decimal('1e-12')
  assert abs(Decimal(str(perf['sharpe']['value']))-sharpe)<Decimal('1e-12')
 same(q(perf['contribution']['LONG']),pnl,label+' LONG contribution');same(q(perf['contribution']['SHORT']),Q(0),label+' SHORT contribution');same(perf['fifo']['count'],0,label+' no closed fragments')
 results.append({'context':label,'factor':factor,'run_id':rid,'transactions':len(txs),'exact_comparisons':count-start_count,'cash_exact':str(cash),'equity_exact':str(equity),'net_pnl_exact':str(pnl),'sample_variance_exact':str(var),'annual_and_sharpe_decimal_precision':80,'stat_abs_tolerance':'1e-12','result':'PASS'})
for label,root in [('GPT_WORK_WINDOWS_SDK',SDK),('DEVELOPER_LOCAL_SDK',D/'clean-sdk')]:
 for factor in ['momentum','reversal']:one(label,lambda n,root=root:(root/n).read_bytes(),factor)
for name in ['phase5-ubuntu-24.04-1','phase5-windows-latest-1']:
 with zipfile.ZipFile(D/'official-ci'/(name+'-official-original.zip')) as z:
  prefix=next(n for n in z.namelist() if n.endswith('environment.json') and n.count('/')==1).rsplit('/',1)[0]+'/'
  for factor in ['momentum','reversal']:one('OFFICIAL_CI_'+name,lambda n:z.read(prefix+n),factor)
report={'fixed_sha':'35f93d640a2304121131d947a465f57a951cf63f','executor':'GPT Work supplemental reviewer','scope':'Independent stdlib derivation from actual Fill/Market/Settlement and raw Journal; constant-price long-opening SDK scenarios only; actual short/FIFO/actions covered separately','contexts':results,'exact_comparisons':count,'committed_transactions_checked':sum(r['transactions'] for r in results),'result':'PASS'}
(O/'RAW_FINANCIAL_RECONSTRUCTION.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:report[k] for k in ['exact_comparisons','committed_transactions_checked','result']}))
