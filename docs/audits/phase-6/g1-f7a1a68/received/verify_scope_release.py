from pathlib import Path
import json,hashlib,zipfile,subprocess,csv,datetime,platform,sys,xml.etree.ElementTree as ET,io
O=Path(__file__).parent;C=Path('E:/WORK/AQRP-audits/p6-f7a1a68/src');P=C/'docs/audits/phase-6';D=O.parent/'p6-g1-f7a1a68-20261023';FIX='f7a1a68c5f747090f8c8a0e934f2fea859aec998';BASE='59246f9fd391c1713b6bed65dd22280f4d248493';ACCEPTED='1c5a7e62cace7c3e66b7cc7f12fd564cb0013654'
H=lambda b:hashlib.sha256(b).hexdigest();git=lambda *a:subprocess.check_output(['git','-C',str(C),*a])
def fh(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(n,v):(O/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
assert git('rev-parse','HEAD').decode().strip()==FIX and git('status','--porcelain')==b''
assert git('show','-s','--format=%P',FIX).decode().strip()==BASE
frozen=json.loads((P/'FROZEN_INPUTS.json').read_bytes());assert len(frozen['files'])==4738
tree=git('ls-tree','-r','-z',BASE);(O/'BASELINE_TREE_NUL.bin').write_bytes(tree);blob_ids={}
for record in tree.rstrip(b'\0').split(b'\0'):
 meta,path=record.split(b'\t',1);mode,kind,oid=meta.split();assert kind==b'blob';blob_ids[path.decode('utf-8')]=oid.decode()
for e in frozen['files']:
 raw=(C/e['path']).read_bytes();assert H(raw)==e['sha256'] and hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==blob_ids[e['path']],e['path']
changes=git('diff','--name-only',BASE,FIX).decode().splitlines();allowed=set(frozen['allowed_existing_status_documents']);assert len(allowed)==7 and len(changes)==55
assert all(n in allowed or n.startswith('docs/audits/phase-6/') for n in changes)
assert git('diff',ACCEPTED,FIX,'--','src','tests','tools','.github','requirements.lock','pyproject.toml')==b''
assert not (C/'src/aqrp/ui').exists()
reqraw=(C/'docs/requirements.csv').read_bytes();rows=list(csv.DictReader(reqraw.decode().splitlines()));phase=[r for r in rows if r['phase']=='6'];snap=json.loads((P/'REQUIREMENTS_SNAPSHOT.json').read_bytes());assert snap['requirements']==phase and len(rows)==106 and len(phase)==8 and sum(r['tier']=='MVP' for r in phase)==5
assert H(reqraw)==snap['catalog_sha256']
refs=git('ls-remote','origin','refs/heads/main','refs/tags/*').decode();(O/'REMOTE_REFS_START.txt').write_text(refs,encoding='utf-8');r={l.split()[1]:l.split()[0] for l in refs.splitlines()}
assert r['refs/heads/main']==r['refs/tags/phase5-baseline^{}']==r['refs/tags/v0.5.0^{}']==BASE
old=(O.parent/'p5-g2-backing-recheck-1c5a7e6-independent/REMOTE_REFS_FINAL.txt').read_text(encoding='utf-8')
for line in old.splitlines():
 sha,name=line.split()
 if name.startswith('refs/tags/'):assert r[name]==sha,name
release=json.loads((P/'PHASE5_RELEASE_RECEIPT.json').read_bytes());assert git('rev-parse',release['actual_merge_sha']+'^{tree}')==git('rev-parse',release['approved_archival_head']+'^{tree}')
assert git('merge-base','--is-ancestor',ACCEPTED,BASE)==b''
# Independent developer plan ZIP/source verification.
receipt=json.loads((D/'RECEIPT.json').read_bytes());assert (D/'Evidence.zip').stat().st_size==receipt['bytes'] and fh(D/'Evidence.zip')==receipt['sha256']
mr=(D/'EVIDENCE_MANIFEST.json').read_bytes();assert H(mr)==receipt['manifest_sha256'];m=json.loads(mr)
with zipfile.ZipFile(D/'Evidence.zip') as z:
 assert z.testzip() is None and len(z.namelist())==len(set(z.namelist()))==83 and len(m['files'])==82
 assert set(z.namelist())=={e['path'] for e in m['files']}|{'EVIDENCE_MANIFEST.json'}
 for e in m['files']:
  b=z.read(e['path']);assert len(b)==e['bytes'] and H(b)==e['sha256']
 assert z.read('EVIDENCE_MANIFEST.json')==mr
 with zipfile.ZipFile(io.BytesIO(z.read('Fixed-Source.zip'))) as source:
  tracked=set(git('ls-files','-z').decode().rstrip('\0').split('\0'));names={n for n in source.namelist() if not n.endswith('/')};assert names==tracked and source.testzip() is None
  for n in names:assert source.read(n)==(C/n).read_bytes(),n
# Release package and original postmerge SDK are prerequisites, not fresh reviewer execution.
seal=json.loads((P/'PHASE5_SEALED_EVIDENCE.json').read_bytes());zp=Path(seal['archive']);assert zp.stat().st_size==seal['bytes'] and fh(zp)==seal['sha256']
with zipfile.ZipFile(zp) as z:
 assert z.testzip() is None and len(z.namelist())==1125
 mm=json.loads(z.read('EVIDENCE_MANIFEST.json'));assert len(mm['files'])==1124
 for e in mm['files']:
  assert z.getinfo(e['path']).file_size==e['bytes']
  with z.open(e['path']) as f:assert hashlib.file_digest(f,'sha256').hexdigest()==e['sha256']
sdk=release['SDK_archive'];sp=Path(sdk['archive']);assert sp.stat().st_size==sdk['bytes'] and fh(sp)==sdk['sha256']
with zipfile.ZipFile(sp) as z:
 assert z.testzip() is None and len(z.namelist())==8009
 selected=json.loads(z.read('upload-selection.json'))['files'];assert len(selected)==8008 and set(z.namelist())=={e['path'] for e in selected}|{'upload-selection.json'}
 for e in selected:assert H(z.read(e['path']))==e['sha256']
 env=json.loads(z.read('environment.json'));assert env['complete'] and not env['dirty'] and env['code_commit']==release['actual_merge_sha']
 junit=ET.fromstring(z.read('junit.xml'));assert len(junit.findall('.//testcase'))==1158 and all(not junit.findall('.//'+n) for n in ['failure','error','skipped'])
 with zipfile.ZipFile(io.BytesIO(z.read('wheel/aqrp-0.5.0.dev5-py3-none-any.whl'))) as wheel:
  mods=[n for n in wheel.namelist() if n.startswith('aqrp/') and n.endswith('.py')];assert len(mods)==69
  for n in mods:assert wheel.read(n)==(C/'src'/n).read_bytes()
save('SCOPE_RELEASE_VERIFICATION.json',dict(fixed_sha=FIX,baseline=BASE,accepted_implementation=ACCEPTED,detached_clean=True,changed_files=changes,frozen_files=4738,canonical_count=106,phase6_requirements=phase,source_tests_tools_CI_lock_exactly_accepted_P5=True,old_tags_unchanged=True,P5_merge_archival_whole_tree_identical=True,developer_plan_archive=dict(bytes=receipt['bytes'],sha256=receipt['sha256'],members=83,source_files=len(names)),P5_release_archive=dict(bytes=seal['bytes'],sha256=seal['sha256'],members=1125),postmerge_SDK_archive=dict(bytes=sdk['bytes'],sha256=sdk['sha256'],tests=1158,members=8009,scope='Developer actual postmerge execution bytes independently verified; not a new reviewer SDK run'),P6_business_runtime_or_browser_tests=0,result='PASS'))
save('ENVIRONMENT.json',dict(executor='GPT Work supplemental reviewer',utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),python=sys.version,executable=sys.executable,runtime_sha256=fh(Path(sys.executable)),platform=platform.platform(),standard_GIL_enabled=sys._is_gil_enabled(),fixed_sha=FIX))
print(json.dumps(dict(scope='PASS',frozen=4738,requirements=8,plan_archive_members=83,source_files=len(names),P5_release_members=1125,postmerge_tests=1158,P6_product_tests=0)))
