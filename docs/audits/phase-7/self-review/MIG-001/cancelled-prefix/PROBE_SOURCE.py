"""Preregistered developer counterexample: cancelled original physical finance prefix."""
from pathlib import Path
from datetime import UTC,datetime
from contextlib import closing
import hashlib,importlib.metadata,json,sqlite3,traceback,uuid
from aqrp.core.canonical import canonical
from aqrp.core.errors import ContractError
from aqrp.factors.admission import bundle_hash
from aqrp.services.task_requests import initialize
from aqrp.services.task_state import TaskState
from aqrp.services.tasks import TaskService
O=Path(__file__).resolve().parent;D=O/('migration-cancelled-prefix-probe-'+str(uuid.uuid4()));D.mkdir();W=D/'workspace'
S='872c05b14513644cbf8031dfbb6be8faa8a7a926'
def sha(raw):return hashlib.sha256(raw).hexdigest()
def save(name,value):
 raw=value if isinstance(value,bytes) else canonical(value)
 with (D/name).open('xb') as f:f.write(raw)
def backup(name,state):
 with closing(sqlite3.connect(state.db)) as source,closing(sqlite3.connect(D/name)) as target:source.backup(target)
def history(state):
 with state.budget.transaction() as c:return state.budget.history(c)
def strip(state):
 with state.transaction() as c:
  for name, in c.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall():
   if name.startswith(('admission_','execution_plan')) or name in {'budget_domains','admissions','trial_claims','legacy_execution_owners'}:c.execute('DROP TABLE "'+name+'"')
 state.budget.anchor.unlink()
def protected():return {str(p):p.read_bytes() for p in W.rglob('*') if p.is_file() and p.suffix in ('.json','.jsonl','.html')}
report={'scope':'Developer exact old installed-package negative, not independent GPT Work G2 or new fixed-source validation','candidate_sha':S,'actual_bundle':bundle_hash(),'expected_bundle':'d9d020a80111e2f679e3bb00b1151d6961e28e9bf0569c80cd03169352e77f4a','package_version':importlib.metadata.version('aqrp'),'declared_setup':'Actual one-decision engineering pipeline is safely cancelled at COMPLETION_BEFORE_SQL after completed original P5; healthy complete same-bundle migration must remain valid.','declared_single_fault':'Append one ASCII space to the actual last committed transaction JSON after valid cancellation; preserve original manifest/cache and all original Task rows. Convert only new control schema to the declared old-history fixture, then import.','independent_literal_expected':{'live_status_after_fault':'INTEGRITY_ERROR','import':'ADMISSION_HISTORY_UNVERIFIED','new_admission':False,'no_original_file_repair':True},'started_utc':datetime.now(UTC).isoformat(),'formal_Test':'NOT RUN','financial_approval':'NONE','Windows_R2':'DEFERRED / NOT VERIFIED'}
assert report['actual_bundle']==report['expected_bundle']
save('PREREGISTRATION.json',report);save('PROBE_SOURCE.py',Path(__file__).read_bytes());print(str(D),flush=True)
try:
 initialize(W,S);service=TaskService(W);frozen=service.freeze({'kind':'engineering_pipeline','factor_ids':['momentum'],'horizons':[1],'start':'2024-01-06','end':'2024-01-06'})
 task=service.submit(frozen,'original-cancelled-source')['task_id']
 def cancel(point):
  if point=='COMPLETION_BEFORE_SQL':assert service.cancel(task)=='CANCEL_REQUESTED'
 done=TaskService(W,fault=cancel).work(task);assert done['status']=='CANCELLED',done
 save('ORIGINAL_CANCELLED_STATUS.json',done);save('ORIGINAL_HISTORY.json',history(service.state));backup('ORIGINAL_AUTHORITY.sqlite',service.state)
 strip(service.state);healthy=TaskState(W);healthy_status=TaskService(W).status(task);assert healthy_status['status']=='CANCELLED'
 save('HEALTHY_MIGRATION_CONTROL.json',{'status':healthy_status,'history':history(healthy)})
 b=healthy_status['slots']['B']['binding'];transactions=Path(b['physical_ledger_root'])/b['child_run_id']/'transactions';target=sorted(transactions.glob('commit-*.json'))[-1]
 original=target.read_bytes();save('ORIGINAL_LAST_COMMIT.json',original);target.write_bytes(original+b' ')
 save('SINGLE_PHYSICAL_MUTATION.json',{'path':str(target),'original_sha256':sha(original),'corrupt_sha256':sha(target.read_bytes()),'original_bytes':len(original),'corrupt_bytes':len(target.read_bytes()),'mutation':'append one ASCII space'})
 live=TaskService(W).status(task);assert live['status']=='INTEGRITY_ERROR' and live['original_terminal_status']=='CANCELLED';save('LIVE_REFUSAL_BEFORE_IMPORT.json',live)
 strip(healthy);backup('CORRUPTED_PRE_SCHEMA.sqlite',healthy);before=protected()
 try:restored=TaskState(W)
 except ContractError as exc:report.update(actual_import='REFUSED',actual_code=exc.code,new_admission=False)
 else:
  report.update(actual_import='ACCEPTED',original_status_after_import=TaskService(W).status(task),history_after_import=history(restored));backup('ACCEPTED_MIGRATION.sqlite',restored)
  new=TaskService(W).submit(frozen,'after-corrupt-cancelled-prefix');report.update(new_task=new,new_admission=new['status']=='QUEUED',history_after_new_submit=history(restored));backup('AFTER_NEW_SUBMIT.sqlite',restored)
 report['all_original_corrupted_bytes_preserved']=all(Path(p).read_bytes()==raw for p,raw in before.items())
 report['expected_refusal_observed']=report['actual_import']=='REFUSED' and report.get('actual_code')=='ADMISSION_HISTORY_UNVERIFIED' and report['new_admission'] is False
except BaseException:report['unexpected_probe_error']=traceback.format_exc()
finally:
 report['finished_utc']=datetime.now(UTC).isoformat();save('RESULT.json',report)
 save('FILE_MANIFEST.json',{'self_excluded':True,'files':[{'path':p.relative_to(D).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p.read_bytes())} for p in sorted(D.rglob('*')) if p.is_file()]})
 print(json.dumps({k:report.get(k) for k in ('actual_import','actual_code','new_admission','expected_refusal_observed','unexpected_probe_error')}),flush=True)
raise SystemExit(0 if report.get('expected_refusal_observed') else 1)
