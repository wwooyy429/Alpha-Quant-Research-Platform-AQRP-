"""Independent literal/edge-case probes against the clean installed wheel.
Inputs are synthetic only; no production function generates expected values.
"""
from pathlib import Path
from fractions import Fraction as Q
import json,sys,os,uuid,subprocess,hashlib
from copy import deepcopy
from aqrp.backtest import ledger as L
from aqrp.backtest.exact import present
from aqrp.backtest.contracts import EngineeringBacktestRequest
from aqrp.backtest.synthetic import fixture_request,seal_sidecar
from aqrp.services.backtest import simulate_engineering,resume_engineering,result_engineering,replay_engineering
from aqrp.core.errors import ContractError
from aqrp.execution.model import commission,fee_upper,bounds,execute_price
from aqrp.performance.metrics import fifo_statistics

O=Path(__file__).parent;R=Path('E:/WORK/AQRP-audits/p5-1c5a7e6/probes');R.mkdir(exist_ok=False)
FIX='1c5a7e62cace7c3e66b7cc7f12fd564cb0013654';records=[]
def serial(x):
 if isinstance(x,Q):return str(x)
 if isinstance(x,dict):return {k:serial(v) for k,v in x.items()}
 if isinstance(x,(tuple,list)):return [serial(v) for v in x]
 return x
def record(name,actual,expected):
 ok=actual==expected;records.append({'id':name,'actual':serial(actual),'expected':serial(expected),'status':'PASS' if ok else 'MISMATCH'})
def book(cash=1000,mark=100):
 s=L.initial_state(Q(cash),[{'security_id':'A','lot':'1','industry':'I','beta':'1','short_permission':True,'borrow_limit':'1000000'}]);s['session']=0;s['assets']['A'].update(mark=Q(mark),tradable=True,in_universe=True);return s
def fill(s,q,p=100,fee=1,session=0):
 return L.trade(s,fill_id=str(uuid.uuid4()),sid='A',signed_qty=Q(q),p=Q(p),fee=Q(fee),session=session,at=f'2024-02-{session+1:02}T09:00:00+00:00')
s=book();fill(s,-1);before=L.account(s);L.settle(s,1,'settle');after=L.account(s)
record('P01_short_settlement_no_phantom_cash',[before['available'],after['available'],after['equity']],[Q(899),Q(899),Q(999)])
s=book(mark=90);fill(s,-2);fill(s,1,90);a=L.account(s);L.settle(s,1,'settle');b=L.account(s)
record('P02_partial_cover_original_unsettled_proceeds',[a['cash_set'],a['U_short'],a['U_free'],a['available'],b['available'],b['S_set']],[Q(908),Q(100),Q(100),Q(818),Q(918),Q(100)])
s=book();fill(s,2);L.settle(s,1,'settle');fill(s,-1,104,session=1);fill(s,-1,97,session=1);stats=fifo_statistics(s['fragments'])
record('P03_FIFO_observations_and_fees',[v['net'] for v in s['fragments']]+[stats['win_rate']['value'],stats['profit_loss_ratio']['value']],[Q('2.5'),Q('-4.5'),Q(1,2),Q(5,9)])
s=book(cash=10000,mark=1000);fill(s,-1,1000);L.accrue(s,'borrow1','A',Q('.04'),kind='BORROW');fill(s,-1,1000,session=1);L.accrue(s,'borrow2','A',Q('.08'),kind='BORROW');fill(s,1,Q('997.93'),session=2)
record('P04_history_specific_borrow',[s['fragments'][0]['net'],s['assets']['A']['lots'][1]['borrow']],[Q('-.01'),Q('.04')])
s=book();fill(s,2);L.accrue(s,'div','A',Q(2),kind='DIVIDEND_EX',pay_at='later');fill(s,-1,101,session=1);fill(s,-1,100,session=2);nets=[v['net'] for v in s['fragments']];e=L.account(s)['equity'];L.pay(s,'div','pay')
record('P05_long_dividend_lot_attribution_pay_once',[*nets,L.account(s)['equity']-e],[Q('.5'),Q('-.5'),Q(0)])
s=book(cash=10000);fill(s,-1,100);fill(s,-1,110);fill(s,3,100);nets=[f['net'] for f in s['fragments']]
record('P06_cross_zero_fee_allocated_once',nets+[s['assets']['A']['lots'][-1]['entry_fee'],sum(f['exit_fee'] for f in s['fragments'])],[Q(-4,3),Q(26,3),Q(1,3),Q(2,3)])
s=book(cash=10**90);fill(s,10**70,100,fee=Q('1.005'));raw=present(L.account(s))
record('P07_wide_exact_financial_output',raw['cash_total'],str(Q(10**90)-Q(10**72)-Q('1.005')) if False else str(10**90-10**72-2)+'.995')
# 1.005 is a direct internal fee input: test no unrequested second rounding in output.
assert Q(raw['cash_total'])==Q(10**90)-Q(10**72)-Q('1.005')
fee_checks=0
for u in map(Q,['.01','105','1000.01','200000']):
 for n in range(1,21):
  for p in [u,u*Q(99,100),u/2]:
   actual=commission(Q(n),p);upper=fee_upper(Q(n),u);assert actual<=upper;fee_checks+=1
record('P08_partial_commission_ceiling',fee_checks,240)
for side in ['BUY','SELL']:
 for kind in ['MARKET','LIMIT']:
  lo,hi=bounds(Q(100),side,kind,Q(100) if kind=='LIMIT' else None);o={'side':side,'low':lo,'high':hi}
  record('P09_'+side+'_'+kind+'_favorable_or_adverse_extreme_refused',execute_price(o,Q('200400.41')),None)

# Public service: independently retain the entire request, actual wire and source directory.
request=fixture_request();(R/'basic-request.json').write_bytes(request.raw)
wire=simulate_engineering(request,R/'basic-runs',FIX);out=wire.read();(R/'basic-return.json').write_bytes(wire.raw)
record('P10_public_basic_account',[out['status'],out['account']['cash_total'],out['account']['equity'],len(out['fills'])],['SUCCEEDED','98.1','998.1',1])
record('OBS_OPENING_LONG_FILL_DIRECTION',out['fills'][0]['direction'],'LONG')
record('P11_original_public_numerical_replay',replay_engineering(R/'basic-runs',out['run_id'],R/'basic-replay')['status'],'NUMERICAL_REPLAY_VERIFIED')
record('P12_result_read_wire_binding',result_engineering(R/'basic-runs',out['run_id'])['state_sha256'],out['state_sha256'])

# Combined true abrupt-process death + resume original *service* run, not only exceptions/model recovery.
child=R/'crash_service.py';child.write_text('''import os,sys,json
from pathlib import Path
from aqrp.backtest.synthetic import fixture_request
import aqrp.services.backtest as service
from aqrp.backtest.engine import Simulator
class CrashSimulator(Simulator):
 def __init__(self,config,root,commit):
  def fault(stage):
   if stage!=sys.argv[2]: return
   paths=list((root/'transactions').glob('prepared-*.json' if stage=='BEFORE_COMMIT' else 'commit-*.json'))
   if paths:
    x=json.loads(max(paths,key=lambda p:p.stat().st_mtime_ns).read_bytes())
    if any(v['kind']=='Fill' for v in x['children']):os._exit(71)
  super().__init__(config,root,commit,fault=fault)
service.Simulator=CrashSimulator
service.simulate_engineering(fixture_request(),Path(sys.argv[1]),sys.argv[3])
''',encoding='utf-8')
for stage in ['BEFORE_COMMIT','AFTER_COMMIT']:
 root=R/('service-crash-'+stage);p=subprocess.run([sys.executable,'-B',str(child),str(root),stage,FIX],capture_output=True)
 (R/(stage+'.stdout.log')).write_bytes(p.stdout);(R/(stage+'.stderr.log')).write_bytes(p.stderr)
 ids=[v.name for v in root.iterdir() if v.is_dir()];assert len(ids)==1
 record('P13_'+stage+'_real_exit',p.returncode,71)
 resumed=resume_engineering(root,ids[0]).read()
 record('P13_'+stage+'_same_original_service_resume',[resumed['run_id'],resumed['status'],len(resumed['fills']),resumed['account']['cash_total'],resumed['performance']['commission']],[ids[0],'SUCCEEDED',1,'98.1','1'])
 (R/(stage+'-resumed-return.json')).write_text(json.dumps(resumed,ensure_ascii=False),encoding='utf-8')

report={'fixed_sha':FIX,'executor':'GPT Work supplemental reviewer','installed_aqrp':__import__('aqrp').__file__,'scope':'Actual engineering production functions/services with independent literal expected values; no formal Test or native account operations','probes':records,'PASS':sum(r['status']=='PASS' for r in records),'MISMATCH':sum(r['status']=='MISMATCH' for r in records),'artifact_root':str(R)}
(O/'PRODUCTION_PROBES.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:report[k] for k in ['fixed_sha','PASS','MISMATCH','artifact_root']}))
