from pathlib import Path
import hashlib,json,subprocess,zipfile,shutil,datetime,sys
O=Path(__file__).parent;C=Path('E:/WORK/AQRP-audits/p6-e71f6f0/src');P=C/'docs/audits/phase-6'
D=O.parent/'p6-g1-recheck-e71f6f0-20261023';old=O.parent/'p6-g1-f7a1a68-independent'
FIX='e71f6f090b102e4abfd70a5999e495f49546a1b5'
H=lambda b:hashlib.sha256(b).hexdigest()
def fh(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(n,x):(O/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
git=lambda *a:subprocess.check_output(['git','-C',str(C),*a])
assert git('rev-parse','HEAD').decode().strip()==FIX and git('status','--porcelain')==b''
pr=json.loads((O/'PR9_FINAL.json').read_bytes())
assert pr['head_sha']==FIX and 'AQRP_FIXED_REVIEW_SHA: '+FIX in pr['body'] and pr['merged'] is False
assert (O/'remote-final.stdout.log').read_bytes()==(O/'REMOTE_REFS_START.txt').read_bytes()
identity=git('cat-file','commit',FIX);assert hashlib.sha1(b'commit '+str(len(identity)).encode()+b'\0'+identity).hexdigest()==FIX
(O/'FIXED_COMMIT_OBJECT.bin').write_bytes(identity);(O/'FIXED_TREE_NUL.bin').write_bytes(git('ls-tree','-r','-z',FIX))
# All input originals copied, not rewritten. Prior independent zip already contains P5 prerequisite originals.
inputs=O/'inputs';inputs.mkdir(exist_ok=False)
for src,dst in [(D/'Evidence.zip','Developer-Evidence.zip'),(D/'EVIDENCE_MANIFEST.json','Developer-EVIDENCE_MANIFEST.json'),(D/'RECEIPT.json','Developer-RECEIPT.json'),(D/'GPT-Work-Phase6-G1-Recheck-Instructions.txt','Developer-Instructions.txt'),(D/'COMMITTED_MODEL_BINDING.json','Developer-COMMITTED_MODEL_BINDING.json'),(old/'EVIDENCE.zip','Prior-Independent-EVIDENCE.zip'),(old/'RECEIPT.json','Prior-Independent-RECEIPT.json')]:
 target=inputs/dst;shutil.copyfile(src,target)
 assert target.stat().st_size==src.stat().st_size and fh(target)==fh(src)
reviewed=O/'reviewed-source/docs/audits/phase-6';reviewed.mkdir(parents=True)
for src in P.iterdir():
 if src.is_file() and src.suffix in {'.md','.py','.json','.in','.lock','.txt'}:shutil.copyfile(src,reviewed/src.name)
save('FINAL_IDENTITY.json',dict(fixed_sha=FIX,PR_head=pr['head_sha'],PR_description_lock=FIX,PR_unmerged=True,detached_clean=True,main_phase5_baseline_v0_5_0='59246f9fd391c1713b6bed65dd22280f4d248493',old_tags_unchanged=True,commit_object_SHA1_verified=True,utc=datetime.datetime.now(datetime.timezone.utc).isoformat()))
scripts={p.name:fh(p) for p in O.glob('*.py')}
save('AUDIT_SCRIPTS_FINAL_HASHES.json',scripts)
# The running wrapper outputs and receipt are external, self-excluded by construction.
excluded={'EVIDENCE.zip','EVIDENCE_MANIFEST.json','RECEIPT.json','seal.stdout.log','seal.stderr.log','seal.command.json'}
files=[]
for p in sorted(O.rglob('*')):
 if not p.is_file() or '__pycache__' in p.parts or (p.parent==O and p.name in excluded):continue
 files.append(dict(path=p.relative_to(O).as_posix(),bytes=p.stat().st_size,sha256=fh(p)))
manifest=dict(fixed_sha=FIX,verdict='PLAN PASS WITH CONDITIONS',executor='GPT Work supplemental reviewer',scope='Independent G1 plan/numeric evidence only; no P6 implementation or UI execution',files=files,self_excluded=['EVIDENCE_MANIFEST.json','EVIDENCE.zip','RECEIPT.json','seal.command.json','seal.stdout.log','seal.stderr.log','__pycache__'])
save('EVIDENCE_MANIFEST.json',manifest)
archive=O/'EVIDENCE.zip';assert not archive.exists()
with zipfile.ZipFile(archive,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=6,allowZip64=True) as z:
 for e in files:z.write(O/e['path'],e['path'],compress_type=zipfile.ZIP_STORED if e['path'].endswith('.zip') else zipfile.ZIP_DEFLATED)
 z.write(O/'EVIDENCE_MANIFEST.json','EVIDENCE_MANIFEST.json')
with zipfile.ZipFile(archive) as z:
 assert z.testzip() is None and len(z.namelist())==len(set(z.namelist()))==len(files)+1
 assert set(z.namelist())=={e['path'] for e in files}|{'EVIDENCE_MANIFEST.json'}
 assert z.read('EVIDENCE_MANIFEST.json')==(O/'EVIDENCE_MANIFEST.json').read_bytes()
 for e in files:
  assert z.getinfo(e['path']).file_size==e['bytes']
  with z.open(e['path']) as f:assert hashlib.file_digest(f,'sha256').hexdigest()==e['sha256']
save('RECEIPT.json',dict(fixed_sha=FIX,verdict='PLAN PASS WITH CONDITIONS',findings={'WORK-P6-G1-001':'CLOSED_DESIGN','WORK-P6-G1-002':'CLOSED_DESIGN','WORK-P6-G1-003':'CLOSED_DESIGN'},new_blocking_findings=0,archive='EVIDENCE.zip',bytes=archive.stat().st_size,sha256=fh(archive),manifest_sha256=fh(O/'EVIDENCE_MANIFEST.json'),manifest_files=len(files),zip_members=len(files)+1,CRC_exact_members_all_sizes_hashes_verified=True,executor='GPT Work supplemental reviewer',not_a_digital_signature=True,conditions=['User acceptance C-P6-001 strict all-required-P4 success','User acceptance C-P6-002 N>=1 for new pipeline','User acceptance C-P6-003 ordinary ASCII decimal4096digits/4098text','Separate P6 implementation authorization'],P6_business_implementation=False,UI_install_AppTest_browser_tests=0,formal_Test=False,financial_approval='NONE',Windows_R2='DEFERRED / NOT VERIFIED',merge_tag_deploy_live_P7=False,created_utc=datetime.datetime.now(datetime.timezone.utc).isoformat()))
print((O/'RECEIPT.json').read_text(encoding='utf-8'))

