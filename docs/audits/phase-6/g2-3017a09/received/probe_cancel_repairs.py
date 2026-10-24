"""Original late-cancel counterexample plus independent source/replay/anchor controls."""
from pathlib import Path
import json,sys,hashlib
from aqrp.services.task_requests import initialize
from aqrp.services.tasks import TaskService
from aqrp.backtest.transactions import TransactionStore
O=Path(__file__).parent;ROOT=Path('E:/WORK/AQRP-runs/gpt-p6-independent-3017a09-20261024')
FIX='3017a097b49ecdae68228ca9a417fcd03c313200'
DRAFT={'kind':'engineering_pipeline','start':'2024-01-06','end':'2024-01-06','horizons':[1]}
records=[]
for label,damage,cancel,replay,targetsource in [
 ('valid',None,True,False,False),('original-commit-corrupt','commit',True,False,False),
 ('initial-missing','initial',True,False,False),('extra-file','extra',True,False,False),
 ('replay-child-corrupt','commit',True,True,False),('replay-source-corrupt','commit',True,True,True),
 ('success-corrupt','commit',False,False,False),('valid-replay',None,True,True,False)]:
 p=ROOT/('cancel-'+label);assert not p.exists();initialize(p,FIX);s=TaskService(p)
 first=s.submit(s.freeze(DRAFT),'pipeline')['task_id']
 task=first
 if replay:
  assert s.work(first)['status']=='SUCCEEDED'
  task=s.submit(s.freeze({'kind':'replay','source_task':first}),'replay')['task_id']
 observed={}
 def fault(point):
  if point!='COMPLETION_BEFORE_SQL':return
  b=s.state.slots(first if targetsource else task)['B' if targetsource or not replay else 'E']['binding']
  root=Path(b['physical_ledger_root'])/b['child_run_id'];tx=root/'transactions'
  state,rows,files=TransactionStore(tx).verified_snapshot()
  observed.update(before_transactions=len(rows),before_account=s.financial_result(first)['account'])
  assert observed['before_account']['cash_total']=='98.1'
  if damage:
   path=sorted(tx.glob('commit-*.json'))[-1] if damage=='commit' else tx/('initial.json' if damage=='initial' else 'unexpected-unlisted.json')
   if path.exists():
    raw=path.read_bytes();(O/(label+'-original.json')).write_bytes(raw)
    observed['original_sha256']=hashlib.sha256(raw).hexdigest()
   if damage=='initial':path.unlink()
   elif damage=='commit':path.write_bytes(raw+b' ')
   else:path.write_bytes(b'{}')
   observed['damaged_path']=str(path)
  if cancel:observed['cancel_ack']=s.cancel(task)
 r=TaskService(p,fault=fault).work(task);db=s.state.get(task)
 if damage:
  assert r['status']==('FAILED' if cancel else 'INTEGRITY_ERROR'),r
  if cancel:
   assert r['error']=='COMMITTED_STATE_UNVERIFIED' and db['status']=='FAILED'
   end=s.logs(task)[-1];assert end['payload']['cancellation_intent'] and end['payload']['financial_verification_error']
  else:assert db['status']=='SUCCEEDED' and r['usable'] is False
  assert 'result' not in r
 else:
  assert r['status']=='CANCELLED' and db['status']=='CANCELLED'
  if not replay:
   b=s.state.slots(task)['B']['binding'];f=Path(b['physical_ledger_root'])/b['child_run_id']/'transactions'
   path=sorted(f.glob('commit-*.json'))[-1];path.write_bytes(path.read_bytes()+b' ')
   later=s.status(task);assert later['status']=='INTEGRITY_ERROR' and later['original_terminal_status']=='CANCELLED'
   assert s.state.get(task)['status']=='CANCELLED';observed['post_terminal_corruption']=later
 records.append(dict(case=label,workspace=str(p),task=task,observed=observed,result=r,db_status=db['status'],logs=s.logs(task)))
 (O/'INDEPENDENT_CANCELLATION_RECHECK.json').write_text(json.dumps(dict(fixed_sha=FIX,executor='GPT Work',python=sys.executable,records=records),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(label,r['status'],flush=True)
print('Cancellation challenges PASS')
