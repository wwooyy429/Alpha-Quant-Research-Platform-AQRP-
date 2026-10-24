"""Independent readback of developer before/after source and immutable Task records."""
from pathlib import Path
import json,hashlib,sqlite3,os
from contextlib import closing
O=Path(__file__).parent;B=Path('C:/Users/11638/AppData/Local/AQRP/reviews/p6-g2-3017a09-developer-20261024T092710Z')/'payload/browser';W=B/'ui/workspace'
H=lambda b:hashlib.sha256(b).hexdigest()
before=json.loads((B/'browser/REPLAY_SOURCE_BEFORE.json').read_bytes());after=json.loads((B/'browser/REPLAY_SOURCE_AFTER.json').read_bytes())
assert before['files']==after['files'] and len(before['files'])==42
source=W/'backtest-runs'/Path(before['root']).name
actual=[]
for parent,dirs,files in os.walk(source,onerror=lambda e:(_ for _ in ()).throw(e),followlinks=False):
 for name in dirs+files:assert not (Path(parent)/name).is_symlink() and not (Path(parent)/name).is_junction()
 for name in files:
  p=Path(parent)/name;actual.append(dict(path=p.relative_to(source).as_posix(),bytes=p.stat().st_size,sha256=H(p.read_bytes())))
assert {x['path']:(x['bytes'],x['sha256']) for x in actual}=={x['path']:(x['bytes'],x['sha256']) for x in before['files']}
old=json.loads((B/'browser/IMMUTABLE_TASK_REQUESTS_BEFORE_DEFAULT_EDITS.json').read_bytes());assert len(old)==12
db=W/'task-control/tasks.sqlite';wal=db.with_name(db.name+'-wal');assert not wal.exists() or wal.stat().st_size==0
dbhash=H(db.read_bytes())
with closing(sqlite3.connect('file:'+db.as_posix()+'?mode=ro&immutable=1',uri=True)) as c:
 for row in old:
  raw=(W/'tasks'/row['id']/'request.json').read_bytes()
  sql=c.execute('SELECT raw,hash FROM tasks WHERE id=?',(row['id'],)).fetchone()
  assert raw==row['raw'].encode()==sql[0].encode()
  assert H(raw)==row['raw_sha256']==row['stored_hash']==sql[1]
 defaults=[(r,json.loads(p),h) for r,p,h in c.execute('SELECT revision,payload,hash FROM defaults ORDER BY revision')]
 assert [x[1]['lookback'] for x in defaults]==[3,2,4,3]
 assert all(H(json.dumps(x[1],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode())==x[2] for x in defaults)
assert H(db.read_bytes())==dbhash
(O/'DEVELOPER_SOURCE_AND_DEFAULTS_READBACK.json').write_text(json.dumps(dict(result='PASS',source_files42=actual,source_before_after_equal=True,old_task_requests12_byte_identical_disk_and_SQL=True,default_lookbacks=[3,2,4,3],readonly_immutable_SQL_no_write=True,database_sha256=dbhash),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Developer actual42 source files +12 old request disk/SQL +literal defaults independently checked')
