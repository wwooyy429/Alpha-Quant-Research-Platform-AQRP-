from pathlib import Path
import zipfile,json,hashlib,subprocess,shutil,datetime,sys
O=Path(__file__).parent;C=Path('E:/WORK/AQRP-audits/p6-3017a09/src')
ROOT=Path('E:/WORK/AQRP-runs/gpt-p6-independent-3017a09-20261024')
BROWSER=Path('E:/WORK/AQRP-runs/gpt-p6-browser-3017a09-independent-20261024')
H=lambda b:hashlib.sha256(b).hexdigest()
def fh(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
git=lambda *a:subprocess.check_output(['git','-C',str(C),*a])
import os,stat
def strict_tree(root):
 def refused(error):raise error
 for parent,dirs,files in os.walk(root,onerror=refused,followlinks=False):
  for name in dirs+files:
   p=Path(parent)/name
   mode=p.lstat().st_mode
   assert not stat.S_ISLNK(mode) and not p.is_junction(),str(p)
  for name in files:yield Path(parent)/name

# Only capture own dedicated validation directories. No original permissions/symlink identity claim.
archive=O/'reviewer-probes-artifacts.zip';assert not archive.exists()
entries=[]
for source,prefix in [(ROOT,'first-attempt-probes'),(Path(str(ROOT)+'-retry'),'repair-probes'),(BROWSER,'browser-runtime'),(Path('E:/WORK/AQRP-runs/gpt-p6-independent-wal-3017a09-20261024'),'wal')]:
 assert source.is_dir()
 for p in sorted(strict_tree(source)):
  assert not p.is_symlink() and not p.is_junction(),str(p)
  if not p.is_file():continue
  n=prefix+'/'+p.relative_to(source).as_posix()
  entries.append((n,p,p.stat().st_size,fh(p)))
with zipfile.ZipFile(archive,'x',zipfile.ZIP_DEFLATED,compresslevel=6,allowZip64=True) as z:
 for n,p,_,_ in entries:z.write(p,n)
with zipfile.ZipFile(archive) as z:
 assert z.testzip() is None and len(z.namelist())==len(set(z.namelist()))==len(entries)
 for n,_,size,h in entries:
  assert z.getinfo(n).file_size==size
  with z.open(n) as f:assert hashlib.file_digest(f,'sha256').hexdigest()==h
(O/'REVIEWER_PROBE_MANIFEST.json').write_text(json.dumps(dict(archive=archive.name,bytes=archive.stat().st_size,sha256=fh(archive),files=[dict(path=n,bytes=s,sha256=h) for n,_,s,h in entries],scope='Own installed-wheel positive/negative synthetic workspaces and loopback runtime; raw corrupt test copies intentionally retained'),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
# Retain exact independently derived inputs used by installed numeric observation.
prior=O.parent/'p6-g1-recheck-e71f6f0-independent'
folder=O/'prior-independent-numeric-inputs';folder.mkdir()
for name in ['NUMERIC_EXTENSION_INPUTS.json','INDEPENDENT_127_ANSWERS.json']:
 shutil.copyfile(prior/name,folder/name);assert fh(folder/name)==fh(prior/name)
# Snapshot reviewed source and original fixed documentation, never modify candidate branch.
reviewed=O/'reviewed-source'
paths=['src/aqrp/services/task_campaigns.py','src/aqrp/services/task_inputs.py','src/aqrp/services/tasks.py','src/aqrp/services/task_requests.py','src/aqrp/services/task_context.py','src/aqrp/services/task_state.py','src/aqrp/ui/app.py','src/aqrp/ui/numbers.py','src/aqrp/experiments/ledger.py','src/aqrp/services/research.py','docs/audits/phase-6/IMPLEMENTATION_AUTHORIZATION.json','docs/audits/phase-6/IMPLEMENTATION_TRACEABILITY.md','docs/audits/phase-6/IMPLEMENTATION.md','docs/audits/phase-6/COMPATIBILITY_IMPACT.md','docs/audits/phase-6/IMPLEMENTATION_IDENTITY.json','docs/audits/phase-6/REQUIREMENTS_SNAPSHOT.json','docs/audits/phase-6/DEVELOPER_FINDINGS.md','docs/audits/phase-6/C1_BROWSER_FINDING_EVIDENCE.json','docs/audits/phase-6/TASK_COMPLETION_CONTRACT.md','docs/audits/phase-6/NESTED_CONTEXT_CONTRACT.md','docs/audits/phase-6/PAGE_SPECIFICATIONS.md','docs/audits/phase-3/STATISTICAL_CONVENTIONS.md']
for name in paths:
 p=reviewed/name;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(C/name,p)
refs=git('ls-remote','origin','refs/heads/main','refs/tags/*').decode()
(O/'REMOTE_REFS_FINAL.txt').write_text(refs,encoding='utf-8')
parsed=lambda s:dict(line.split()[::-1] for line in s.splitlines())
assert parsed(refs)==parsed((O/'REMOTE_REFS_START.txt').read_text(encoding='utf-8'))
assert git('rev-parse','HEAD').decode().strip()=='3017a097b49ecdae68228ca9a417fcd03c313200' and git('status','--porcelain')==b''
raw=git('cat-file','commit','HEAD')
assert hashlib.sha1(b'commit '+str(len(raw)).encode()+b'\0'+raw).hexdigest()=='3017a097b49ecdae68228ca9a417fcd03c313200'
(O/'FIXED_COMMIT_OBJECT.bin').write_bytes(raw);(O/'FIXED_TREE_NUL.bin').write_bytes(git('ls-tree','-r','-z','HEAD'))
(O/'FINAL_LOCAL_IDENTITY.json').write_text(json.dumps(dict(fixed_sha='3017a097b49ecdae68228ca9a417fcd03c313200',detached_clean=True,main_and_all_old_tags_unchanged=True,commit_object_SHA1_verified=True,utc=datetime.datetime.now(datetime.timezone.utc).isoformat()),indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(probe_archive=archive.name,bytes=archive.stat().st_size,sha256=fh(archive),files=len(entries),fixed_checkout_clean=True)))

