from pathlib import Path
import json,hashlib,zipfile,subprocess,csv,datetime,platform,sys,xml.etree.ElementTree as ET,io
O=Path(__file__).parent;C=Path('E:/WORK/AQRP-audits/p6-e71f6f0/src');P=C/'docs/audits/phase-6';D=O.parent/'p6-g1-recheck-e71f6f0-20261023';FIX='e71f6f090b102e4abfd70a5999e495f49546a1b5';PARENT='f7a1a68c5f747090f8c8a0e934f2fea859aec998';BASE='59246f9fd391c1713b6bed65dd22280f4d248493';ACCEPTED='1c5a7e62cace7c3e66b7cc7f12fd564cb0013654'
H=lambda b:hashlib.sha256(b).hexdigest();git=lambda *a:subprocess.check_output(['git','-C',str(C),*a])
def fh(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(n,v):(O/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
assert git('rev-parse','HEAD').decode().strip()==FIX and git('status','--porcelain')==b''
assert git('show','-s','--format=%P',FIX).decode().strip()==PARENT
frozen=json.loads((P/'FROZEN_INPUTS.json').read_bytes());assert len(frozen['files'])==4738
tree=git('ls-tree','-r','-z',BASE);(O/'BASELINE_TREE_NUL.bin').write_bytes(tree);blob_ids={}
for record in tree.rstrip(b'\0').split(b'\0'):
 meta,path=record.split(b'\t',1);mode,kind,oid=meta.split();assert kind==b'blob';blob_ids[path.decode('utf-8')]=oid.decode()
for e in frozen['files']:
 raw=(C/e['path']).read_bytes();assert H(raw)==e['sha256'] and hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==blob_ids[e['path']],e['path']
changes=git('diff','--name-only',BASE,FIX).decode().splitlines();allowed=set(frozen['allowed_existing_status_documents']);assert len(allowed)==7 and len(changes)==171
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
 assert z.testzip() is None and len(z.namelist())==len(set(z.namelist()))==207 and len(m['files'])==206
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

ident=json.loads((P/'g1-f7a1a68/DESIGN_REVISION_IDENTITY.json').read_bytes())
for entry in ident['unchanged_prior_G1_assets']:
 raw=(P/entry['path']).read_bytes()
 assert len(raw)==entry['bytes'] and H(raw)==entry['sha256']
 assert raw==git('show',PARENT+':docs/audits/phase-6/'+entry['path']),entry['path']
assert len(ident['unchanged_prior_G1_assets'])==13
for e in ident['model_files']:assert H((P/e['path']).read_bytes())==e['sha256']
old=O.parent/'p6-g1-f7a1a68-independent'
rr=json.loads((old/'RECEIPT.json').read_bytes());oldz=old/'EVIDENCE.zip'
assert oldz.stat().st_size==rr['bytes']==584855382 and fh(oldz)==rr['sha256']=='22cc883e7bd46f2b83ce4e5251505776862dedde3c532e15eddb5a8e07854273'
with zipfile.ZipFile(oldz) as z:
 assert z.testzip() is None
 mmraw=z.read('EVIDENCE_MANIFEST.json');assert H(mmraw)==rr['manifest_sha256']
 mm=json.loads(mmraw)
 assert len(mm['files'])==105 and len(z.namelist())==len(set(z.namelist()))==106
 assert set(z.namelist())=={e['path'] for e in mm['files']}|{'EVIDENCE_MANIFEST.json'}
 for e in mm['files']:
  with z.open(e['path']) as f:assert hashlib.file_digest(f,'sha256').hexdigest()==e['sha256']
 received=json.loads((P/'g1-f7a1a68/RECEIVED_IDENTITY.json').read_bytes())
 assert len(received['copied_originals'])==70
 for e in received['copied_originals']:
  raw=(P/'g1-f7a1a68/received'/e['path']).read_bytes()
  assert len(raw)==e['bytes'] and H(raw)==e['sha256'] and raw==(old/e['path']).read_bytes(),e['path']
# Capture exact changed files and numbered current contract/source context.
(O/'REVISION_DIFF.patch').write_bytes(git('diff','--binary',PARENT,FIX))
(O/'FULL_PLAN_DIFF.patch').write_bytes(git('diff','--binary',BASE,FIX))
context_names=['AGENTS.md']+['docs/'+n+'.md' for n in ['PROJECT_CHARTER','ARCHITECTURE','INTERFACES','REQUIREMENTS','TRACEABILITY','ROADMAP','PROGRESS','DECISIONS']]
context_names += [p.relative_to(C).as_posix() for p in P.glob('*.md')]
context_names += ['src/aqrp/'+n for n in ['services/backtest.py','backtest/engine.py','backtest/provider.py','portfolio/service.py','experiments/ledger.py']]
with (O/'REVIEWED_SOURCE_CONTEXT.txt').open('w',encoding='utf-8') as out:
 for name in context_names:
  f=C/name
  if f.exists():
   out.write('\n===== '+name+' sha256='+fh(f)+' =====\n')
   for i,line in enumerate(f.read_text(encoding='utf-8-sig').splitlines(),1):out.write(str(i)+': '+line+'\n')
save('INHERITANCE_AND_ARCHIVE.json',dict(prior_13_assets_exact=True,old_reference_32_bytes_exact=True,old_independent_zip_crc_member_hashes=rr,received_original_files=70,developer_models_bound=ident['model_files'],prior_dependency_evidence='Same thirteen input/lock/metadata assets; prior metadata-only independent resolution retained, no fresh install/runtime or resolver claimed',new_developer_source_all_tracked=True))

save('SCOPE_RELEASE_VERIFICATION.json',dict(fixed_sha=FIX,baseline=BASE,accepted_implementation=ACCEPTED,detached_clean=True,changed_files=changes,frozen_files=4738,canonical_count=106,phase6_requirements=phase,source_tests_tools_CI_lock_exactly_accepted_P5=True,old_tags_unchanged=True,P5_merge_archival_whole_tree_identical=True,developer_plan_archive=dict(bytes=receipt['bytes'],sha256=receipt['sha256'],members=207,source_files=len(names)),P5_release_archive=dict(bytes=seal['bytes'],sha256=seal['sha256'],members=1125),postmerge_SDK_archive=dict(bytes=sdk['bytes'],sha256=sdk['sha256'],tests=1158,members=8009,scope='Developer actual postmerge execution bytes independently verified; not a new reviewer SDK run'),P6_business_runtime_or_browser_tests=0,result='PASS'))
save('ENVIRONMENT.json',dict(executor='GPT Work supplemental reviewer',utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),python=sys.version,executable=sys.executable,runtime_sha256=fh(Path(sys.executable)),platform=platform.platform(),standard_GIL_enabled=sys._is_gil_enabled(),fixed_sha=FIX))
print(json.dumps(dict(scope='PASS',frozen=4738,requirements=8,plan_archive_members=207,source_files=len(names),P5_release_members=1125,postmerge_tests=1158,P6_product_tests=0)))
