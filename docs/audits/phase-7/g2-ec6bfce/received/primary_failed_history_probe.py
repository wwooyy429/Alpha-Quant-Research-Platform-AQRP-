"""Primary single financial fault after genuine risk-rejected parent; same-bundle migration fixtures."""
import pathlib,json,uuid,hashlib,sqlite3,sys
O=pathlib.Path(__file__).parent.resolve();S='ec6bfcedc0c424b6fa3e817c9a094385bd971d6f'
from aqrp.services.task_requests import initialize
from aqrp.services.tasks import TaskService
from aqrp.services.task_state import TaskState
from aqrp.factors.admission import bundle_hash
assert bundle_hash()=='6045a40c9be937e9c953e2422b46227bfc6122053bc13bee9e7615c76bf7c79c'
root=pathlib.Path('E:/AQ7')/('primary-failed-history-'+uuid.uuid4().hex[:8]);root.mkdir(exist_ok=False);results=[]
draft={'kind':'engineering_pipeline','factor_ids':['momentum'],'horizons':[1],'start':'2024-01-06','end':'2024-01-06','policy':{'top_k':1},'constraints':{'gross_max':'0'}}
def rows(db):
 with sqlite3.connect(db) as c:
  c.row_factory=sqlite3.Row
  return {n:[dict(r) for r in c.execute('SELECT * FROM '+n+' ORDER BY rowid')] for n in ['workspace','tasks','slots','events','campaign_attempts','adapted_requests','defaults']}
def financial(service,task):
 try:return {'accepted':True,'value':service.financial_result(task)}
 except Exception as e:return {'accepted':False,'type':type(e).__name__,'code':getattr(e,'code',None),'message':str(e)}
for mode in ['healthy','corrupt_transaction']:
 w=root/mode;initialize(w,S);service=TaskService(w);t=service.submit(service.freeze(draft),'original-risk');done=service.work(t['task_id']);assert done['status']=='FAILED' and done['error']=='REQUIRED_STAGE_REJECTED'
 binding=done['slots']['B']['binding'];broot=pathlib.Path(binding['physical_ledger_root'])/binding['child_run_id'];assert broot.is_relative_to(w)
 result=json.loads((broot/'result.json').read_bytes());assert result['status']=='SUCCEEDED' and result['account']['cash_total']=='1000' and result['fills']==[]
 commits=sorted((broot/'transactions').glob('commit-*.json'));target=commits[-1];before=target.read_bytes();(O/(mode+'-original-last-transaction.json')).write_bytes(before)
 baseline=financial(service,t['task_id']);assert baseline['accepted']
 if mode=='corrupt_transaction':target.write_bytes(before+b' ')
 fault_read=financial(service,t['task_id']);assert fault_read['accepted']==(mode=='healthy')
 old_business=rows(service.state.db)
 # Same declared pre-control-schema fixture as the candidate's history tests.
 # Both controls perform this setup; the sole financial fault is the extra ASCII space.
 with service.state.transaction() as c:
  tables=[x[0] for x in c.execute("SELECT name FROM sqlite_master WHERE type='table'")]
  for name in tables:
   if name.startswith(('admission_','execution_plan')) or name in ['budget_domains','admissions','trial_claims','legacy_execution_owners']:
    c.execute('DROP TABLE "'+name+'"')
 anchor=service.state.budget.anchor;assert anchor.is_relative_to(w);anchor.unlink()
 assert rows(service.state.db)==old_business
 try:
  migrated=TaskState(w);accepted=True;error=None
  assert rows(migrated.db)==old_business
  after=TaskService(w);granted=after.submit(after.freeze({'factor_ids':['momentum'],'horizons':[1],'start':'2024-01-06','end':'2024-01-06'}),'after-history-import')
  final_read=financial(after,t['task_id'])
 except Exception as e:
  accepted=False;error={'type':type(e).__name__,'code':getattr(e,'code',None),'message':str(e)};granted=None;final_read=None
 results.append({'mode':mode,'workspace':str(w),'original_task':done,'original_B_result':result,'transaction_target':str(target),'original_transaction_sha256':hashlib.sha256(before).hexdigest(),'current_transaction_sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'financial_baseline':baseline,'financial_after_single_fault':fault_read,'business_rows_before_strip':old_business,'migration_accepted':accepted,'migration_error':error,'new_grant':granted,'financial_after_import':final_read})
out={'executor':'Primary GPT Work','fixed_sha':S,'executable':sys.executable,'scope':'Independent code-control fixtures only; no original developer evidence changed; same-bundle schema setup matches candidate tests','fixture_root':str(root),'single_fault':'one trailing ASCII space in a genuine successful B physical transaction under a genuinely FAILED risk parent; all manifested business bytes and SQL retained','results':results}
(O/'PRIMARY_FAILED_HISTORY_REPRODUCTION.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps([{'mode':r['mode'],'financial_fault_code':r['financial_after_single_fault'].get('code'),'migration_accepted':r['migration_accepted'],'new_task_status':(r['new_grant'] or {}).get('status')} for r in results]))
assert results[0]['migration_accepted'] and results[1]['migration_accepted'] and results[1]['new_grant']['status']=='QUEUED' and results[1]['financial_after_single_fault']['code']=='TRANSACTION_CHAIN_CORRUPTED'
