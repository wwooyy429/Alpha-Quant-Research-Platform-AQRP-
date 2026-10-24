"""Independent fresh-process WAL contention; fixed installed wheel, not editable preflight."""
from pathlib import Path
import sqlite3,subprocess,sys,time,json,threading,concurrent.futures
from aqrp.services import task_state
from aqrp.services.task_state import TaskState
O=Path(__file__).parent;ROOT=Path('E:/WORK/AQRP-runs/gpt-p6-independent-wal-3017a09-20261024');assert not ROOT.exists();ROOT.mkdir()
records=[]
child="from aqrp.services.task_state import TaskState;from aqrp.core.canonical import canonical;import sys,json;s=TaskState(sys.argv[1]);print(json.dumps([s.workspace_id,s.submit(canonical({'kind':'research'}),'same-key')]))"
for iteration in range(4):
 root=ROOT/str(iteration);root.mkdir()
 ps=[subprocess.Popen([sys.executable,'-I','-c',child,str(root)],stdout=subprocess.PIPE,stderr=subprocess.PIPE) for _ in range(10)]
 items=[]
 for i,p in enumerate(ps):
  out,err=p.communicate(timeout=90);(root/(str(i)+'.stdout.log')).write_bytes(out);(root/(str(i)+'.stderr.log')).write_bytes(err)
  items.append(dict(pid=p.pid,exit=p.returncode,stdout=out.decode(errors='replace'),stderr=err.decode(errors='replace')))
 assert [x['exit'] for x in items]==[0]*10,items
 assert len({tuple(json.loads(x['stdout'])) for x in items})==1
 with TaskState(root).transaction() as c:assert c.execute('SELECT count(*) FROM tasks').fetchone()[0]==c.execute('SELECT count(*) FROM workspace').fetchone()[0]==1
 records.append(dict(case='ten-real-processes',iteration=iteration,workspace=str(root),workers=items))
def holder(name):
 root=ROOT/name;db=root/'task-control/tasks.sqlite';db.parent.mkdir(parents=True)
 c=sqlite3.connect(db,timeout=0,isolation_level=None);c.execute('CREATE TABLE sentinel (value INTEGER)');c.execute('INSERT INTO sentinel VALUES (17)');c.execute('BEGIN');c.execute('SELECT * FROM sentinel').fetchone();return root,db,c
root,db,c=holder('native-held-reader-release')
with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
 start=time.monotonic();f=pool.submit(TaskState,root);time.sleep(.15);assert not f.done();c.rollback();c.close();state=f.result(timeout=5);elapsed=time.monotonic()-start
with state.transaction() as c:assert c.execute('SELECT value FROM sentinel').fetchone()[0]==17 and c.execute('PRAGMA synchronous').fetchone()[0]==2
records.append(dict(case='actual-default-connection-held-reader-release',elapsed=elapsed,success=True))
root,db,c=holder('finite-deadline');original=task_state.SETUP_TIMEOUT_SECONDS;task_state.SETUP_TIMEOUT_SECONDS=.08
try:
 start=time.monotonic()
 try:TaskState(root);raise AssertionError('Expected native BUSY')
 except sqlite3.OperationalError as e:
  elapsed=time.monotonic()-start;assert e.sqlite_errorcode&255 in (sqlite3.SQLITE_BUSY,sqlite3.SQLITE_LOCKED);assert .06<=elapsed<2
  records.append(dict(case='deadline-exhaustion',elapsed=elapsed,native_errorcode=e.sqlite_errorcode))
finally:task_state.SETUP_TIMEOUT_SECONDS=original;c.rollback();c.close()
with sqlite3.connect(db) as c:assert c.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()==[('sentinel',)]
state=TaskState(ROOT/'body-rollback');calls=[]
try:
 with state.transaction() as c:
  calls.append(1);c.execute("INSERT INTO defaults VALUES(1,'{}','bad')")
  e=sqlite3.OperationalError('independent body BUSY');e.sqlite_errorcode=sqlite3.SQLITE_BUSY;raise e
except sqlite3.OperationalError:pass
with state.transaction() as c:assert c.execute('SELECT count(*) FROM defaults').fetchone()[0]==0
assert calls==[1];records.append(dict(case='body-busy-executed-once-and-rolled-back',calls=1))
(O/'INDEPENDENT_WAL_RECHECK.json').write_text(json.dumps(dict(fixed_sha='3017a097b49ecdae68228ca9a417fcd03c313200',python=sys.executable,executor='GPT Work',actual_processes=40,editable=False,result='PASS',records=records),indent=2)+'\n',encoding='utf-8')
print('Independent WAL: 40 real processes + held reader + finite deadline + body once PASS')
