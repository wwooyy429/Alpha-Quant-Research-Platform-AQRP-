"""Reviewer's independent commit/cancellation boundary reproducer; synthetic data only."""
from pathlib import Path
import json,hashlib
from aqrp.backtest.engine import Simulator
from aqrp.backtest.transactions import TransactionStore
from aqrp.backtest.ledger import account
from aqrp.backtest.synthetic import fixture_request
from aqrp.backtest.exact import present
from aqrp.core.errors import ContractError
import aqrp.services.backtest as service
O=Path(__file__).parent;R=Path('E:/WORK/AQRP-audits/p5-bf5e5a8/cancellation-boundary');R.mkdir(exist_ok=False)
FIX='bf5e5a89209f2dd24042cd806626f832b531de52';records=[];original=service.Simulator
for stage,error_type in [('BEFORE_COMMIT','KeyboardInterrupt'),('AFTER_COMMIT','KeyboardInterrupt'),('AFTER_COMMIT','ContractError')]:
 label=stage+'-'+error_type;root=R/label;request=fixture_request();(R/(label+'-request.json')).write_bytes(request.raw)
 class BoundarySimulator(Simulator):
  def __init__(self,config,runroot,commit):
   def fault(current):
    if current!=stage:return
    paths=list((runroot/'transactions').glob('prepared-*.json' if current=='BEFORE_COMMIT' else 'commit-*.json'))
    if not paths:return
    newest=max(paths,key=lambda p:p.stat().st_mtime_ns);item=json.loads(newest.read_bytes())
    if any(x['kind']=='Fill' for x in item['children']):
     if error_type=='KeyboardInterrupt':raise KeyboardInterrupt('reviewer interruption at actual '+current)
     raise ContractError('REVIEWER_AFTER_COMMIT_ERROR')
   super().__init__(config,runroot,commit,fault=fault)
 service.Simulator=BoundarySimulator
 result=service.simulate_engineering(request,root,FIX)
 returned=result.read();(R/(label+'-return.json')).write_bytes(result.raw)
 runroot=root/returned['run_id'];disk=TransactionStore(runroot/'transactions');actual=present(account(disk.state))
 expected_cash='1000' if stage=='BEFORE_COMMIT' else '98.1'
 assert actual['cash_total']==expected_cash
 m=service.ExperimentLedger(root).verify(returned['run_id'])
 assert m['status']==returned['status']
 record={'id':label,'run_id':returned['run_id'],'terminal_status':returned['status'],'reported_last_committed_cash':returned['last_committed_account']['cash_total'],'independently_recovered_committed_cash':actual['cash_total'],'actual_disk_committed_fills':len(disk.state['fills']),'actual_disk_committed_fee':present(disk.state['fees']),'reported_committed_transactions':len(json.loads((runroot/'transactions.json').read_bytes())),'actual_committed_transactions':len(disk.records),'expected_cash_from_literal_1000_minus_9_times_100_1_minus_1':expected_cash,'matches_durable_commit':returned['last_committed_account']['cash_total']==actual['cash_total'],'run_root':str(runroot)}
 records.append(record)
 (R/(label+'-recovered-account.json')).write_text(json.dumps(actual,indent=2),encoding='utf-8')
service.Simulator=original
report={'fixed_sha':FIX,'actual_executor':'GPT Work supplemental reviewer','scope':'Actual installed wheel service and immutable commit file boundary; no real trading, Test or ACL changes','records':records,'result':'REPRODUCED_MISMATCH' if any(not r['matches_durable_commit'] for r in records) else 'PASS','artifact_root':str(R)}
(O/'CANCELLATION_BOUNDARY_PROBE.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report,ensure_ascii=False))
