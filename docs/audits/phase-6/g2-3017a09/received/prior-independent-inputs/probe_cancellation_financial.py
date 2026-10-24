"""Installed-wheel task finalization/cancellation controls with literal independent expectations."""
from pathlib import Path
import json,hashlib,sys
from aqrp.services.task_requests import initialize
from aqrp.services.tasks import TaskService
from aqrp.backtest.transactions import TransactionStore
O=Path(__file__).parent;root=Path('E:/WORK/AQRP-runs/gpt-p6-independent-probes-20261024')
DRAFT={'kind':'engineering_pipeline','start':'2024-01-06','end':'2024-01-06','horizons':[1]}
records=[]
for label,corrupt,cancel in [('cancel-valid',False,True),('cancel-corrupt',True,True),('success-corrupt',True,False)]:
 workspace=root/(label+'-retry');assert not workspace.exists();initialize(workspace,'eae807f957f178d19bc55dcfbd668caff5470c6e')
 base=TaskService(workspace);t=base.submit(base.freeze(DRAFT),label)['task_id']
 observed={}
 def fault(point):
  if point!='COMPLETION_BEFORE_SQL':return
  slots=base.state.slots(t);b=slots['B']['binding'];directory=Path(b['physical_ledger_root'])/b['child_run_id']
  _,txns,_=TransactionStore(directory/'transactions').verified_snapshot()
  observed['before_transactions']=len(txns);observed['before_financial']=base.financial_result(t)['account']
  assert observed['before_financial']['cash_total']=='98.1' and len(txns)>0
  if corrupt:
   path=sorted((directory/'transactions').glob('commit-*.json'))[-1]
   raw=path.read_bytes();(O/(label+'-original-transaction.json')).write_bytes(raw)
   path.write_bytes(raw+b' ')
   observed.update(corrupted_file=str(path),original_sha256=hashlib.sha256(raw).hexdigest(),corrupted_sha256=hashlib.sha256(path.read_bytes()).hexdigest())
   try:TransactionStore(directory/'transactions').verified_snapshot();observed['durable_prefix_error']=None
   except Exception as e:observed['durable_prefix_error']=getattr(e,'code',type(e).__name__)
   assert observed['durable_prefix_error']=='TRANSACTION_CHAIN_CORRUPTED'
  if cancel:observed['cancel_ack']=base.cancel(t)
 result=TaskService(workspace,fault=fault).work(t)
 try:finance=base.financial_result(t);finance_error=None
 except Exception as e:finance=None;finance_error=getattr(e,'code',type(e).__name__)
 record=dict(case=label,workspace=str(workspace),task=t,observed=observed,task_result=result,database_status=base.state.get(t)['status'],financial_result=finance,financial_error=finance_error,expected=('FAILED / COMMITTED_STATE_UNVERIFIED' if corrupt and cancel else ('INTEGRITY_ERROR / unusable' if corrupt else 'CANCELLED with valid retained core account98.1')))
 records.append(record)
(O/'CANCELLATION_FINANCIAL_PROBE.json').write_text(json.dumps(dict(executor='GPT Work supplemental reviewer',scope='Synthetic installed-wheel real services/SQLite/disk fault control; no formal Test',python=sys.executable,records=records),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps([dict(case=r['case'],actual_status=r['task_result']['status'],database_status=r['database_status'],finance_error=r['financial_error'],expected=r['expected']) for r in records]))

