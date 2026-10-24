"""Independent raw-byte provenance/CI verification. No AQRP imports."""
from pathlib import Path,PurePosixPath
import json,hashlib,zipfile,subprocess,io,tarfile,xml.etree.ElementTree as ET,re,datetime,platform,sys
O=Path(__file__).parent;C=Path('E:/WORK/AQRP-audits/p6-3017a09/src')
D=Path('C:/Users/11638/AppData/Local/AQRP/reviews/p6-g2-3017a09-developer-20261024T092710Z');P=D/'payload';FIX='3017a097b49ecdae68228ca9a417fcd03c313200'
H=lambda b:hashlib.sha256(b).hexdigest()
def fh(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(n,v):(O/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
git=lambda *a:subprocess.check_output(['git','-C',str(C),*a])
seal=json.loads((D/'SEAL.json').read_bytes());outer=D/'AQRP-P6-G2-3017a09-EVIDENCE.zip'
assert seal['fixed_sha']==FIX and seal['bytes']==outer.stat().st_size and fh(outer)==seal['sha256']
mr=(P/'FILES_SHA256.json').read_bytes();assert H(mr)==seal['files_manifest_sha256'];manifest=json.loads(mr)
with zipfile.ZipFile(outer) as z:
 names=z.namelist();assert len(names)==len(set(names)) and z.testzip() is None
 # Manifest paths are relative to payload, verify exact outer prefix/schema.
 prefix='';assert 'FILES_SHA256.json' in names
 expected={prefix+e['path'] for e in manifest['files']}|{prefix+'FILES_SHA256.json'}
 assert set(names)==expected
 for e in manifest['files']:
  name=prefix+e['path'];assert z.getinfo(name).file_size==e['bytes']
  with z.open(name) as f:assert hashlib.file_digest(f,'sha256').hexdigest()==e['sha256'],name
  assert fh(P/e['path'])==e['sha256'],name
 tracked=set(git('ls-files','-z').decode().rstrip('\0').split('\0'))
 sources=list((P/'execution-metadata').glob('SOURCE-3017a09.git.zip'));assert len(sources)==1
 assert sources[0].stat().st_size==88435541 and fh(sources[0])=='416501153449e423005274870e2ce3397d1108ce292319a381eb123450d6c4d9'
 with zipfile.ZipFile(sources[0]) as t:
  assert t.testzip() is None
  members=[n for n in t.namelist() if not n.endswith('/')];assert len(t.namelist())==len(set(t.namelist()));assert set(members)==tracked and len(members)==len(tracked)==5108
  for n in members:assert t.read(n)==(C/n).read_bytes(),n

core=(C/'requirements.lock').read_bytes()
api=json.loads((O/'CI_ARTIFACTS_START.json').read_bytes())['artifacts']
ci=[]
def verify_archive(path,official=None):
 with zipfile.ZipFile(path) as z:
  assert z.testzip() is None
  files=[n for n in z.namelist() if not n.endswith('/')]
  assert len(files)==len(set(files))
  for n in files:
   p=PurePosixPath(n);assert not p.is_absolute() and '..' not in p.parts and '\\' not in n and ':' not in n
  candidates=[n for n in files if n.endswith('environment.json')]
  depth=min(len(PurePosixPath(n).parts) for n in candidates)
  envname,= [n for n in candidates if len(PurePosixPath(n).parts)==depth]
  prefix=envname[:-len('environment.json')]
  assert all(n.startswith(prefix) for n in files)
  actual={n[len(prefix):] for n in files};read=lambda n:z.read(prefix+n)
  selected=json.loads(read('upload-selection.json'))['files']
  declared={e['path'] for e in selected};assert len(declared)==len(selected)
  for e in selected:assert H(read(e['path']))==e['sha256'],e['path']
  extras=actual-declared-{'upload-selection.json'}
  groups={}
  for n in extras:
   p=PurePosixPath(n).parts
   assert len(p)>=3 and p[0]=='tmp' and p[1].endswith('current')
   groups.setdefault(p[1],[]).append(n)
  alias_rows=[]
  for group,names in groups.items():
   suffixes={n.split('/',2)[2] for n in names}
   stub=group[:-7]
   targets={PurePosixPath(n).parts[1] for n in declared if n.startswith('tmp/'+stub) and len(PurePosixPath(n).parts)>2 and PurePosixPath(n).parts[1][len(stub):].isdigit()}
   matches=[]
   for target in targets:
    target_names={n for n in declared if n.startswith('tmp/'+target+'/')}
    if {n.split('/',2)[2] for n in target_names}!=suffixes:continue
    if all(read('tmp/'+target+'/'+n.split('/',2)[2])==read(n) for n in names):matches.append(target)
   assert matches,(group,'Incomplete or changed alias subtree')
   alias_rows.append(dict(group=group,whole_subtree_matches=sorted(matches),files=len(names)))
  env=json.loads(read('environment.json'))
  assert env['code_commit']==FIX and env['complete'] is True and env['dirty'] is False and env['python'].startswith('3.13.16')
  assert env['lock_sha256']==H(core)
  cases=ET.fromstring(read('junit.xml')).findall('.//testcase')
  assert len(cases)==1567 and not any([c.find(n) is not None for c in cases for n in ['failure','error','skipped']])
  commands=[json.loads(l) for l in read('commands.jsonl').splitlines()]
  assert commands and all(c['exit']==0 and c['started_utc']<=c['ended_utc'] for c in commands)
  for e in json.loads(read('artifacts.json')):
   if e['uploaded']:assert H(read(e['path']))==e['sha256']
  wheel,=[n for n in declared if n.startswith('wheel/aqrp-') and n.endswith('.whl')]
  wr=read(wheel);assert H(wr)==env['wheel_sha256']
  with zipfile.ZipFile(io.BytesIO(wr)) as w:
   modules=[n for n in w.namelist() if n.startswith('aqrp/') and n.endswith('.py')]
   assert len(modules)==83
   for n in modules:assert w.read(n)==(C/'src'/n).read_bytes(),n
   assert w.read('aqrp/factors/reviewed_code.json')==(C/'src/aqrp/factors/reviewed_code.json').read_bytes()
   for osname in ['windows','linux']:assert w.read('aqrp/ui/requirements-'+osname+'.lock')==(C/('requirements-ui-'+osname+'.lock')).read_bytes()
  ui=json.loads(read('ui-dependency-wheels.json'));osname='windows' if 'Windows' in env['os'] else 'linux'
  uilock=(C/('requirements-ui-'+osname+'.lock')).read_bytes()
  assert ui['lock_sha256']==env['ui_lock_sha256']==H(uilock) and len(ui['wheels'])==29
  allowed_ui=set(re.findall(rb'--hash=sha256:([0-9a-f]{64})',uilock))
  for e in ui['wheels']:assert len(read(e['path']))==e['bytes'] and H(read(e['path']))==e['sha256'] and e['sha256'].encode() in allowed_ui
  deps=[n for n in declared if n.startswith('reproduction/wheelhouse/') and n.endswith('.whl')]
  assert len(deps)==(22 if osname=='windows' else 21)
  allowed_core=set(re.findall(rb'--hash=sha256:([0-9a-f]{64})',core))
  for n in deps:assert H(read(n)).encode() in allowed_core
  original=json.loads(read('reproduction/published-original-replay.json'))
  assert original['status']=='ALL_ORIGINAL_BYTES_VERIFIED_AND_THREE_RUNS_REPLAYED' and len(original['verified_original_files'])==66 and len(original['runs'])==3 and all(r['status']=='DECLARED_PROJECTION_MATCH' for r in original['runs'])
  for name,count in [('p6-reference_check.json',32),('p6-revision_reference.json',95)]:
   r=json.loads(read(name));assert r['groups']==r['passed']==count and r['failed']==0
  snapshots=terminals=0
  for n in declared:
   if n.startswith('tmp/') or not n.endswith('/manifest.json'):continue
   raw=read(n);m=json.loads(raw);parent=n[:-len('manifest.json')]
   if m.get('schema_version')=='snapshot/1.0.0':
    assert len(m['tables'])==8
    assert H(json.dumps({k:v for k,v in m.items() if k not in ['snapshot_id','manifest_hash']},sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode())==m['manifest_hash']
    for e in m['tables'].values():assert H(read(parent+e['path']))==e['sha256']
    snapshots+=1
   elif 'event_prefix_hash' in m:
    chain=[json.loads(l) for l in read(parent+'events.jsonl').splitlines()];prev='0'*64
    for i,event in enumerate(chain):
     assert event['seq']==i and event['previous']==prev
     er=json.dumps({k:v for k,v in event.items() if k!='hash'},sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()
     assert H(er)==event['hash'];prev=event['hash']
    assert chain[-1]['kind']==m['status'] and chain[-1]['payload']['manifest_sha256']==H(raw) and m['event_prefix_hash']==chain[-2]['hash']
    assert len(m['files'])==len({e['path'] for e in m['files']})
    for e in m['files']:assert H(read(parent+e['path']))==e['sha256']
    terminals+=1
  record=dict(path=str(path),bytes=path.stat().st_size,sha256=fh(path),selected=len(selected),members=len(files),aliases=len(extras),alias_groups=len(groups),tests=1567,failures=0,errors=0,skipped=0,source_wheel_modules=83,core_dependency_wheels=len(deps),UI_dependency_wheels=29,environment=env,commands=len(commands),snapshot_manifests=snapshots,terminal_manifests=terminals,old_66_original_files_and_3_runs=True)
  if official:
   assert path.stat().st_size==official['size_in_bytes'] and fh(path)==official['digest'].removeprefix('sha256:')
   assert official['workflow_run']['head_sha']==FIX and official['workflow_run']['id']==40079197702
   assert record['aliases']>0 and record['alias_groups']>0
   save('CI_ALIAS_SUBTREES_'+osname+'.json',alias_rows)
   record['fresh_API_artifact_id']=official['id']
  else:assert not extras
  return record
for artifact in api:
 label='windows' if 'windows' in artifact['name'] else 'ubuntu'
 path=P/'official-ci'/('phase6-'+('windows-latest' if label=='windows' else 'ubuntu-24.04')+'-1-official-original.zip')
 ci.append(verify_archive(path,artifact))
sdk=verify_archive(P/'sdk/LOCAL_CLEAN_SDK-3017a09.zip')
save('DEVELOPER_ARCHIVE_VERIFICATION.json',dict(fixed_sha=FIX,outer_bytes=seal['bytes'],outer_sha256=seal['sha256'],outer_payload_files=len(manifest['files']),outer_members=len(expected),source_tracked_files=len(tracked),CI=ci,SDK=sdk,scope='Developer/official original bytes independently verified; independent reviewer SDK execution is separately recorded',result='PASS'))
save('ENVIRONMENT.json',dict(executor='GPT Work supplemental reviewer',fixed_sha=FIX,python=sys.version,executable=sys.executable,interpreter_sha256=fh(Path(sys.executable)),os=platform.platform(),standard_GIL=sys._is_gil_enabled(),utc=datetime.datetime.now(datetime.timezone.utc).isoformat()))
print(json.dumps(dict(outer_files=len(manifest['files']),source_files=len(tracked),CI_tests=[r['tests'] for r in ci],SDK_tests=sdk['tests'],result='PASS')))



