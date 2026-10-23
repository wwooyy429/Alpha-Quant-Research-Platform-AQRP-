"""Independent byte/scope audit. Does not import any AQRP module."""
import pathlib, json, hashlib, subprocess, zipfile, io, csv, platform, sys, datetime
O=pathlib.Path(__file__).parent
C=O.parent/'p5-g1-review-5262032'; P=C/'docs/audits/phase-5'
D=O.parent/'p5-g1-repair-5262032'; OLD=O.parent/'p5-g1-5c9721f-independent'
FIX='5262032bee4f631f68763e57510e1878945f6b8c'; BASE='32ea5d6b75c84c07017d87377eeabd2f78207c5c'; PREV='5c9721f96679f4d495b7b3b93af3e2e31e66ae62'
H=lambda b:hashlib.sha256(b).hexdigest()
def git(*a): return subprocess.check_output(['git','-C',str(C),*a])
def save(n,v): (O/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
assert git('rev-parse','HEAD').decode().strip()==FIX
assert git('status','--porcelain')==b''
git('merge-base','--is-ancestor',BASE,FIX)
changes=git('diff','--name-only','-z',BASE,FIX).decode().rstrip('\0').split('\0')
assert all(p in ('AGENTS.md','README.md') or p.startswith('docs/') for p in changes)
for prefix in ['src','tests','tools','.github','requirements.lock','pyproject.toml']:
 assert git('diff','--name-only',BASE,FIX,'--',prefix)==b'',prefix
frozen=json.loads((P/'FROZEN_INPUTS.json').read_bytes())['files']; assert len(frozen)==131
for e in frozen:
 b=(C/e['path']).read_bytes(); assert H(b)==e['sha256'] and b==git('show',BASE+':'+e['path']),e['path']
identity=json.loads((C/'docs/audits/phase-4/g2-18439f3/IDENTITY.json').read_bytes())
p4frozen=json.loads((C/'docs/audits/phase-4/FROZEN_INPUTS.json').read_bytes())['files']
for e in identity['preserved_files']+p4frozen: assert H((C/e['path']).read_bytes())==e['sha256'],e['path']
for name in ['FILE_MANIFEST.json','DESIGN_REVISION_IDENTITY.json']:
 m=json.loads((P/name).read_bytes())
 for e in m['files']:
  b=(P/e['path']).read_bytes(); assert len(b)==e['bytes'] and H(b)==e['sha256'],e['path']
for name in ['GOLDEN_CANDIDATES.json','reference_check.py']:
 assert (P/name).read_bytes()==git('show',PREV+':docs/audits/phase-5/'+name),name
rows=list(csv.DictReader((C/'docs/requirements.csv').read_text(encoding='utf-8-sig').splitlines()))
r5=[r for r in rows if r['phase']=='5']; snapshot=json.loads((P/'REQUIREMENTS_SNAPSHOT.json').read_bytes())
assert len(rows)==106 and len(r5)==12 and sum(r['tier']=='MVP' for r in r5)==10
assert r5==snapshot['requirements'] and H((C/'docs/requirements.csv').read_bytes())==snapshot['catalog_sha256']
protocol=(C/'docs/REVIEW_PROTOCOL.md').read_bytes()
assert protocol==git('show',BASE+':docs/REVIEW_PROTOCOL.md')
assert protocol!=git('show','bd18d1b98b5647f4f4b6345ffe73dca40acaf038:docs/REVIEW_PROTOCOL.md')
history=P/'g1-5c9721f/developer-validation'
disposition=json.loads((history/'PREEXISTING_REGRESSION_DISPOSITION.json').read_bytes())
failure_logs=[p for p in history.rglob('*.log') if b'REVIEW_PROTOCOL' in p.read_bytes()]
assert failure_logs,'Original failed check log not found'
refs=git('ls-remote','origin','refs/heads/main','refs/tags/*').decode()
(O/'REMOTE_REFS.txt').write_text(refs,encoding='utf-8')
rd={l.split()[1]:l.split()[0] for l in refs.splitlines()}
assert rd['refs/heads/main']==rd['refs/tags/phase4-baseline^{}']==rd['refs/tags/v0.4.0^{}']==BASE
oldrefs={l.split()[1]:l.split()[0] for l in (OLD/'REMOTE_REFS.txt').read_text(encoding='utf-8-sig').splitlines()}
assert all(rd[k]==v for k,v in oldrefs.items())
save('SCOPE_VERIFICATION.json',{'fixed_sha':FIX,'baseline':BASE,'clean_detached':True,'canonical_count':106,'phase5_requirements':r5,'frozen_identical':len(frozen),'P4_preserved_verified':len(identity['preserved_files']),'P4_frozen_verified':len(p4frozen),'source_tests_tools_CI_lock_unchanged':True,'all_changes':changes,'original_25_70_bytes_unchanged':True,'protected_protocol_restored_to_baseline':True,'failure_logs':[str(p.relative_to(C)) for p in failure_logs],'failure_disposition':disposition,'remote_refs_unchanged':len(oldrefs),'result':'PASS'})
receipt=json.loads((D/'RECEIPT.json').read_bytes()); zpath=D/receipt['archive']
assert zpath.stat().st_size==receipt['bytes'] and H(zpath.read_bytes())==receipt['sha256']
manifest_bytes=(D/'EVIDENCE_MANIFEST.json').read_bytes(); assert H(manifest_bytes)==receipt['manifest_sha256']
manifest=json.loads(manifest_bytes); assert len(manifest['files'])==132
with zipfile.ZipFile(zpath) as z:
 assert z.testzip() is None
 assert len(z.namelist())==len(set(z.namelist()))==133
 assert set(z.namelist())=={e['path'] for e in manifest['files']}|{'EVIDENCE_MANIFEST.json'}
 assert z.read('EVIDENCE_MANIFEST.json')==manifest_bytes
 for e in manifest['files']:
  b=z.read(e['path']); assert len(b)==e['bytes'] and H(b)==e['sha256'],e['path']
 with zipfile.ZipFile(io.BytesIO(z.read('Fixed-Source.zip'))) as source:
  assert source.testzip() is None
  names=[n for n in source.namelist() if not n.endswith('/')]
  tracked=set(git('ls-files','-z').decode().rstrip('\0').split('\0'))
  assert len(names)==len(set(names)) and set(names)==tracked
  for n in names: assert source.read(n)==(C/n).read_bytes(),n
 original=z.read('Original-Independent-G1-Evidence.zip')
 assert H(original)=='60d16ecfe7f7663282506b9c250878c2f3d6fc61e630dbcd656a950c93855075'
 assert original==(OLD/'EVIDENCE.zip').read_bytes()
 with zipfile.ZipFile(io.BytesIO(original)) as oz:
  assert oz.testzip() is None
  om=json.loads(oz.read('EVIDENCE_MANIFEST.json'))
  assert set(oz.namelist())=={e['path'] for e in om['files']}|{'EVIDENCE_MANIFEST.json'}
  for e in om['files']:
   b=oz.read(e['path']); assert H(b)==e['sha256'] and len(b)==e['bytes'],e['path']
 # Every received original reviewer artifact present in Git must retain old sealed bytes.
 received=P/'g1-5c9721f/received'; compared=[]
 with zipfile.ZipFile(io.BytesIO(original)) as oz:
  for p in received.rglob('*'):
   if p.is_file():
    n=p.relative_to(received).as_posix()
    if n in oz.namelist(): assert p.read_bytes()==oz.read(n),n; compared.append(n)
save('DEVELOPER_EVIDENCE_VERIFICATION.json',{'fixed_sha':FIX,'archive':str(zpath),'bytes':zpath.stat().st_size,'sha256':receipt['sha256'],'manifest_sha256':receipt['manifest_sha256'],'declared_members':132,'CRC_exact_members_all_hashes':'PASS','fixed_source_matches':len(names),'original_independent_evidence_identical':True,'original_members_checked':len(om['files']),'received_original_artifacts_byte_compared':compared,'result':'PASS'})
save('ENVIRONMENT.json',{'executor':'GPT Work supplemental reviewer','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'python':sys.version,'executable':sys.executable,'platform':platform.platform(),'machine':platform.machine(),'gil_enabled':sys._is_gil_enabled(),'fixed_sha':FIX,'scope':'G1 design/byte verification; no AQRP business implementation run'})
print(json.dumps({'scope':'PASS','frozen':131,'P4_preserved':len(identity['preserved_files']),'P4_frozen':len(p4frozen),'developer_evidence_members':132,'source_files':len(names),'old_evidence_members':len(om['files'])}))
