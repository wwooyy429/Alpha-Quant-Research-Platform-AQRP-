"""Reviewer byte/scope verification; only stdlib and git, no AQRP imports."""
from pathlib import Path
import json,hashlib,subprocess,zipfile,io,csv,datetime,platform,sys
O=Path(__file__).parent;C=Path('E:/WORK/AQRP-audits/p5-bfdcf30/src');D=O.parent/'p5-g2-bfdcf30';P=C/'docs/audits/phase-5'
FIX='bfdcf30e525ff802ea483974f58163eedc029ce8';BASE='32ea5d6b75c84c07017d87377eeabd2f78207c5c';G1='5262032bee4f631f68763e57510e1878945f6b8c';MERGE='b379a8f34b9d43859daaf4dd98cc46021304e7c0'
H=lambda b:hashlib.sha256(b).hexdigest()
def filehash(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def git(*a):return subprocess.check_output(['git','-C',str(C),*a])
def save(n,x):(O/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
assert git('rev-parse','HEAD').decode().strip()==FIX and git('status','--porcelain')==b''
assert git('rev-parse',MERGE+'^{tree}')==git('rev-parse',FIX+'^{tree}')
assert git('show','-s','--format=%P',MERGE).decode().strip().split()==[BASE,FIX]
identity=json.loads((P/'IMPLEMENTATION_IDENTITY.json').read_bytes());pack=identity['explicit_packaging_changes']
allowed={'.github/workflows/ci.yml','pyproject.toml','src/aqrp/__init__.py','src/aqrp/factors/reviewed_code.json','tests/environment/test_installation.py','tools/check_coverage.py','tools/ci.py'}
assert set(pack)==allowed and H((C/'requirements.lock').read_bytes())=='86c7bf65c9a9690036006360062c8cd10a91279705b4070af7033d7699abffeb'
frozen=json.loads((P/'FROZEN_INPUTS.json').read_bytes())['files'];oldp4=json.loads((C/'docs/audits/phase-4/g2-18439f3/IDENTITY.json').read_bytes())['preserved_files']
union={e['path']:e['sha256'] for e in frozen+oldp4};assert len(frozen)==131 and len(oldp4)==3440 and len(union)==3451
assert len(set(union)-allowed)==3444
for path,h in union.items():
 b=(C/path).read_bytes()
 if path in allowed: assert h==pack[path]['original_sha256'] and H(b)==pack[path]['current_sha256'],path
 else: assert H(b)==h,path
for e in identity['preserved_files']+identity['current_implementation_files']:
 assert H((C/e['path']).read_bytes())==e['sha256'],e['path']
design=json.loads((P/'DESIGN_REVISION_IDENTITY.json').read_bytes())
assert len(design['files'])==12
for e in design['files']:
 b=(P/e['path']).read_bytes();assert H(b)==e['sha256'] and b==git('show',G1+':docs/audits/phase-5/'+e['path']),e['path']
bundle=identity['bundle_manifest'];assert len(bundle['files'])==69
assert {e['path'] for e in bundle['files']}=={p.relative_to(C/'src/aqrp').as_posix() for p in (C/'src/aqrp').rglob('*.py')}
for e in bundle['files']:assert H((C/'src/aqrp'/e['path']).read_bytes())==e['sha256'],e['path']
canonical=lambda x:json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()
assert H(canonical(bundle))==identity['bundle_sha256']=='ba6b33df82b5142958a2cb6f7aa5a92109241e0f533dd56d436f32fe83358f07'
changes=git('diff','--name-status','-z',BASE,FIX).decode().rstrip('\0').split('\0');(O/'DIFF_NAME_STATUS_NUL.json').write_text(json.dumps(changes,ensure_ascii=False,indent=2),encoding='utf-8')
rows=list(csv.DictReader((C/'docs/requirements.csv').read_text(encoding='utf-8').splitlines()));phase=[r for r in rows if r['phase']=='5'];assert len(rows)==106 and len(phase)==12 and sum(r['tier']=='MVP' for r in phase)==10
assert phase==json.loads((P/'REQUIREMENTS_SNAPSHOT.json').read_bytes())['requirements']
auth=json.loads((P/'IMPLEMENTATION_AUTHORIZATION.json').read_bytes());assert auth['implementation_authorized'] and auth['C-P5-001']=='EXPLICITLY_ACCEPTED'
assert not auth['main_merge_tag_deployment_live_formal_Test_financial_approval_P6_authorized']
refs=git('ls-remote','origin','refs/heads/main','refs/tags/*').decode();(O/'REMOTE_REFS_START.txt').write_text(refs,encoding='utf-8')
previous=(O.parent/'p5-g1-recheck-5262032-independent/REMOTE_REFS.txt').read_text(encoding='utf-8')
rd={l.split()[1]:l.split()[0] for l in refs.splitlines()};assert all(rd[l.split()[1]]==l.split()[0] for l in previous.splitlines())
save('SCOPE_VERIFICATION.json',{'fixed_sha':FIX,'released_baseline':BASE,'G1':G1,'temporary_CI_merge':MERGE,'CI_merge_parents_and_whole_tree_verified':True,'clean':True,'original_frozen':131,'original_P4_preserved':3440,'union':3444,'packaging_exceptions':pack,'G1_design_files_identical':12,'bundle_modules':69,'bundle_sha256':identity['bundle_sha256'],'canonical_count':106,'phase5_requirements':phase,'authorization':auth,'main_old_tags_unchanged':True,'result':'PASS'})
r=json.loads((D/'RECEIPT.json').read_bytes());zpath=D/r['archive'];assert zpath.stat().st_size==r['bytes'] and filehash(zpath)==r['sha256']
mr=(D/'EVIDENCE_MANIFEST.json').read_bytes();assert H(mr)==r['manifest_sha256'];m=json.loads(mr);assert len(m['files'])==10920
with zipfile.ZipFile(zpath) as z:
 assert z.testzip() is None and len(z.namelist())==len(set(z.namelist()))==10921
 assert set(z.namelist())=={e['path'] for e in m['files']}|{'EVIDENCE_MANIFEST.json'}
 for e in m['files']:
  b=z.read(e['path']);assert len(b)==e['bytes'] and H(b)==e['sha256'],e['path']
 assert z.read('EVIDENCE_MANIFEST.json')==mr
 with zipfile.ZipFile(io.BytesIO(z.read('Fixed-Source.zip'))) as source:
  assert source.testzip() is None
  names=[n for n in source.namelist() if not n.endswith('/')];tracked=set(git('ls-files','-z').decode().rstrip('\0').split('\0'))
  assert set(names)==tracked and len(names)==len(set(names))
  for n in names:assert source.read(n)==(C/n).read_bytes(),n
save('DEVELOPER_ARCHIVE_VERIFICATION.json',{'fixed_sha':FIX,'archive':str(zpath),'bytes':r['bytes'],'sha256':r['sha256'],'manifest_files':10920,'members':10921,'CRC_exact_members_all_hashes':'PASS','source_files_exactly_matched':len(names),'result':'PASS'})
save('ENVIRONMENT.json',{'executor':'GPT Work supplemental reviewer','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'python':sys.version,'executable':sys.executable,'runtime_sha256':filehash(Path(sys.executable)),'platform':platform.platform(),'machine':platform.machine(),'standard_GIL_enabled':sys._is_gil_enabled(),'fixed_sha':FIX})
print(json.dumps({'scope':'PASS','developer_archive':'PASS','members':10921,'source_files':len(names),'preserved_union':3444,'G1_design_files':12,'modules':69}))
