import pathlib,json,subprocess,hashlib,zipfile,io,csv,xml.etree.ElementTree as ET,datetime
O=pathlib.Path(__file__).parent;C=O.parent/'p5-g1-review-5c9721f';D=O.parent/'p5-g1-5c9721f';P=C/'docs/audits/phase-5';FIX='5c9721f96679f4d495b7b3b93af3e2e31e66ae62';BASE='32ea5d6b75c84c07017d87377eeabd2f78207c5c';MERGE='d3993d07e5df1b5c2f7acd30cb628226f7b1fc09';APPROVED='3c8757949b0fd5c97953b06a74ebc2d0e56676e4'
H=lambda b:hashlib.sha256(b).hexdigest()
def save(n,x):(O/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def git(*a):return subprocess.check_output(['git','-C',str(C),*a])
assert git('rev-parse','HEAD').decode().strip()==FIX and git('status','--porcelain')==b''
assert git('rev-parse',MERGE+'^{tree}')==git('rev-parse',APPROVED+'^{tree}')
assert git('merge-base','--is-ancestor',BASE,FIX)==b''
changes=git('diff','--name-only',BASE,FIX).decode().splitlines();protected=('src/','tests/','tools/','.github/','requirements.lock','pyproject.toml','.gitleaks.toml')
assert not any(p.startswith(protected) for p in changes)
f=json.loads((P/'FROZEN_INPUTS.json').read_bytes());assert len(f['files'])==131
for e in f['files']:assert H((C/e['path']).read_bytes())==e['sha256'] and git('show',BASE+':'+e['path'])==(C/e['path']).read_bytes(),e['path']
fm=json.loads((P/'FILE_MANIFEST.json').read_bytes())
for e in fm['files']:b=(P/e['path']).read_bytes();assert len(b)==e['bytes'] and H(b)==e['sha256'],e['path']
rows=list(csv.DictReader((C/'docs/requirements.csv').read_text(encoding='utf-8-sig').splitlines()));r5=[r for r in rows if r['phase']=='5'];snap=json.loads((P/'REQUIREMENTS_SNAPSHOT.json').read_bytes())
assert len(rows)==106 and len(r5)==12 and sum(r['tier']=='MVP' for r in r5)==10 and snap['requirements']==r5
assert H((C/'docs/requirements.csv').read_bytes())==snap['catalog_sha256']
refs=git('ls-remote','origin','refs/heads/main','refs/tags/*').decode();(O/'REMOTE_REFS.txt').write_text(refs,encoding='utf-8');rd={line.split()[1]:line.split()[0] for line in refs.splitlines()}
assert rd['refs/heads/main']==BASE and rd['refs/tags/phase4-baseline^{}']==rd['refs/tags/v0.4.0^{}']==BASE
oldrefs={line.split()[1]:line.split()[0] for line in (D/'OLD_REMOTE_TAGS.txt').read_text(encoding='utf-8-sig').splitlines() if line.strip()}
for ref,v in oldrefs.items():assert rd[ref]==v,(ref,v,rd[ref])
status=json.loads((C/'docs/audits/phase-4/STATUS.json').read_bytes());oldstatus=json.loads(git('show',BASE+':docs/audits/phase-4/STATUS.json'));assert 'historical_status_fields' in status
save('SCOPE_VERIFICATION.json',{'fixed_sha':FIX,'baseline':BASE,'actual_merge':MERGE,'merge_tree_equals_approved':True,'clean':True,'canonical_count':106,'phase5':r5,'frozen_131_files_byte_identical':True,'plan_manifest_files':len(fm['files']),'all_changes':changes,'business_source_tests_tools_CI_lock_unchanged':True,'main_new_tags_same_commit':True,'old_tag_refs_unchanged':len(oldrefs),'status_errata':{'new_status':status,'old_status':oldstatus},'result':'PASS'})
receipt=json.loads((D/'RECEIPT.json').read_bytes());archive=D/receipt['archive'];assert archive.stat().st_size==receipt['bytes'] and H(archive.read_bytes())==receipt['sha256'];mr=(D/'EVIDENCE_MANIFEST.json').read_bytes();assert H(mr)==receipt['manifest_sha256'];manifest=json.loads(mr)
with zipfile.ZipFile(archive) as z:
 assert z.testzip() is None and set(z.namelist())=={e['path'] for e in manifest['files']}|{'EVIDENCE_MANIFEST.json'}
 for e in manifest['files']:
  b=z.read(e['path']);assert len(b)==e['bytes'] and H(b)==e['sha256'],e['path']
 source=zipfile.ZipFile(io.BytesIO(z.read('Fixed-Source.zip')));names=[n for n in source.namelist() if not n.endswith('/')]
 for n in names:assert source.read(n)==(C/n).read_bytes(),n
 sdkraw=z.read('Phase4-merged-main-SDK-d3993d0.zip');(O/'Phase4-merged-main-SDK-original.zip').write_bytes(sdkraw)
 with zipfile.ZipFile(io.BytesIO(sdkraw)) as sdk:
  assert sdk.testzip() is None;n=next(n for n in sdk.namelist() if n.endswith('upload-selection.json'));prefix=n[:-len('upload-selection.json')];sel=json.loads(sdk.read(n));J=lambda p:json.loads(sdk.read(prefix+p));assert {n[len(prefix):] for n in sdk.namelist()}=={e['path'] for e in sel['files']}|{'upload-selection.json'}
  for e in sel['files']:assert H(sdk.read(prefix+e['path']))==e['sha256'],e['path']
  env=J('environment.json');assert env['complete'] and not env['dirty'] and env['code_commit']==MERGE
  junit=ET.fromstring(sdk.read(prefix+'junit.xml'));assert len(junit.findall('.//testcase'))==844 and not any(junit.findall('.//'+x) for x in ['failure','error','skipped'])
  wheel=next(e['path'] for e in sel['files'] if e['path'].startswith('wheel/') and e['path'].endswith('.whl'));wr=sdk.read(prefix+wheel);assert H(wr)==env['wheel_sha256']
  with zipfile.ZipFile(io.BytesIO(wr)) as wh:
   py=[n for n in wh.namelist() if n.startswith('aqrp/') and n.endswith('.py')];assert len(py)==53
   for n in py:assert wh.read(n)==(C/'src'/n).read_bytes(),n
  dest=O/'P4-baseline-evidence';dest.mkdir()
  for n in ['environment.json','junit.xml','coverage.json','commands.log','upload-selection.json','reproduction/result.json','portfolio/summary.json']:
   p=dest/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(sdk.read(prefix+n))
  env_extract=env
save('DEVELOPER_EVIDENCE_VERIFICATION.json',{'fixed_sha':FIX,'archive':str(archive),'bytes':archive.stat().st_size,'sha256':receipt['sha256'],'manifest_files':len(manifest['files']),'CRC_all_member_hashes':'PASS','fixed_source_matches':len(names),'postmerge_SDK':{'executed_sha':MERGE,'tests':844,'selected_files':len(sel['files']),'wheel_modules_equal_fixed_source':53,'environment':env_extract,'archive_bytes':len(sdkraw),'archive_sha256':H(sdkraw),'scope':'Developer-executed P4 postmerge baseline SDK; independently checked raw bytes, not a new GPT Work execution or P5 tests'},'result':'PASS'})
print(json.dumps({'fixed_sha':FIX,'scope':'PASS','phase5_requirements':12,'frozen_files':131,'developer_manifest':len(manifest['files']),'source_files':len(names),'P4_postmerge_tests':844}))
