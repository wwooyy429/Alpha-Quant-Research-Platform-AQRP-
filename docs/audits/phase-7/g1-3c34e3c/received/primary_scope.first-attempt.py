"""Primary read-only Git scope, frozen files, release refs and outer raw archive verification."""
import json,subprocess,hashlib,zipfile,io,csv,sys,platform,datetime
from pathlib import Path
O=Path(__file__).parent;C=Path('E:/WORK/AQRP-audits/p7-3c34e3c/src');P=C/'docs/audits/phase-7'
G='3c34e3ca75c9799307b8a98b34f045b40988bbca';B='d563347ad11e1f26e131dc06e343250282c05c33'
H2='a4d650d5d15e814600fde0bb6858fe97f14e5229';M='7b4864f4d750fa96b5b5634c4bba0cd84b5b077f';C6='3017a097b49ecdae68228ca9a417fcd03c313200'
commands=[]
def git(*args):
 p=subprocess.run(['git',*args],cwd=C,stdout=subprocess.PIPE,stderr=subprocess.PIPE);commands.append({'argv':['git',*args],'cwd':str(C),'exit':p.returncode,'stderr':p.stderr.decode('utf-8',errors='replace')});assert p.returncode==0;return p.stdout
assert git('rev-parse','HEAD').decode().strip()==G
assert git('rev-list','--parents','-n','1',G).decode().strip().split()==[G,B]
assert not git('status','--porcelain')
assert git('rev-parse',H2+'^{tree}')==git('rev-parse',M+'^{tree}')
changes={}
for old,new in [(C6,H2),(H2,M),(M,B),(B,G)]:
 names=git('diff','--name-only',old,new).decode().splitlines();changes[old+'..'+new]=names
 assert all(x.startswith('docs/') or x in ['AGENTS.md','README.md'] for x in names)
frozen=json.loads((P/'FROZEN_BASELINE_FILES.json').read_bytes());rows=frozen['files'];files=git('ls-tree','-r','--name-only',B).decode().splitlines()
assert {x['path'] for x in rows}==set(files)-set(frozen['excluded_changed_metadata'])
# Read all frozen baseline Git objects in one binary batch; independently check the actual checkout bytes.
batch=subprocess.run(['git','cat-file','--batch'],cwd=C,input=''.join(B+':'+r['path']+'\n' for r in rows).encode(),stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True)
commands.append({'argv':['git','cat-file','--batch'],'input_count':len(rows),'cwd':str(C),'exit':0})
s=io.BytesIO(batch.stdout)
for r in rows:
 header=s.readline().split();assert header[1]==b'blob';blob=s.read(int(header[2]));assert s.read(1)==b'\n'
 assert len(blob)==r['bytes'] and hashlib.sha256(blob).hexdigest()==r['sha256'];assert (C/r['path']).read_bytes()==blob
assert not s.read()
fm=json.loads((P/'FILE_MANIFEST.json').read_bytes());actual={x.relative_to(P).as_posix() for x in P.rglob('*') if x.is_file()}
assert actual=={r['path'] for r in fm['files']}|{'FILE_MANIFEST.json'}
for r in fm['files']:
 raw=(P/r['path']).read_bytes();assert len(raw)==r['bytes'] and hashlib.sha256(raw).hexdigest()==r['sha256']
base_id=json.loads(git('show',B+':docs/audits/phase-6/IMPLEMENTATION_IDENTITY.json'));current=json.loads((C/'docs/audits/phase-6/IMPLEMENTATION_IDENTITY.json').read_bytes())
assert base_id==json.loads((P/'PHASE6_IMPLEMENTATION_IDENTITY.json').read_bytes())
update=json.loads((P/'P6_PLAN_DOCUMENT_IDENTITY_UPDATE.json').read_bytes());before={x['path']:x for x in base_id['current_files']};after={x['path']:x for x in current['current_files']}
assert {k for k in before if before[k]!=after[k]}=={x['path'] for x in update['changed_rows']}
temp=dict(current);temp['current_files']=base_id['current_files'];assert temp==base_id
for x in update['changed_rows']:assert before[x['path']]==x['before'] and after[x['path']]==x['after']
req=list(csv.DictReader(io.StringIO((C/'docs/requirements.csv').read_text(encoding='utf-8-sig'))));rs=json.loads((P/'REQUIREMENTS_SNAPSHOT.json').read_bytes());p7=[x for x in req if x['phase']=='7']
assert len(req)==106 and len(p7)==5 and p7==rs['requirements'] and sum(x['tier']=='MVP' for x in p7)==3
remote=git('ls-remote','origin','refs/heads/main','refs/tags/*','refs/heads/phase6-baseline').decode();(O/'REMOTE_REFS_PRIMARY.txt').write_text(remote,encoding='utf-8')
refmap={line.split()[1]:line.split()[0] for line in remote.splitlines()};assert refmap['refs/heads/main']==B
for name in ['refs/tags/phase6-baseline','refs/tags/v0.6.0']:assert refmap.get(name+'^{}',refmap.get(name))==B
old=Path('C:/Users/11638/AppData/Local/AQRP/reviews/p6-g2-recheck-3017a09-independent-20261024/REMOTE_REFS_FINAL.txt').read_text(encoding='utf-8')
oldrefs={line.split()[1]:line.split()[0] for line in old.splitlines() if len(line.split())==2}
oldtags={k:v for k,v in oldrefs.items() if k.startswith('refs/tags/')};assert oldtags and all(refmap[k]==v for k,v in oldtags.items())
archives=[]
for directory,sha,msha in [
 ('C:/Users/11638/AppData/Local/AQRP/reviews/p7-g1-plan-3c34e3c-20261024','0a8c761b0b6d62abf7dfa342c6d702dff47666c1ae5b0b482dcd8ea828349ca2','a2b6c258dcf437492e953b6e9d81bf7c1f66674b8e2cfba5599148dc0ca780ed'),
 ('C:/Users/11638/AppData/Local/Packages/OpenAI.Codex_2p2nqsd0c76g0/LocalCache/Local/AQRP/reviews/p6-release-d563347-20261024','1eb89bf2f9c1cea1bc53909a990f377c4fc93d6e6d6c56d322b2da24e638c794','c36939379af53fe1320e8f0a09d0d3fa6238864b5c69a9eefe7117b9333efd67')]:
 d=Path(directory);z=d/'Evidence.zip';h=hashlib.file_digest(z.open('rb'),'sha256').hexdigest();assert h==sha
 manifest=(d/'EVIDENCE_MANIFEST.json').read_bytes();assert hashlib.sha256(manifest).hexdigest()==msha
 declared=json.loads(manifest)['files']; members=[]
 with zipfile.ZipFile(z) as f:
  assert set(f.namelist())=={x['path'] for x in declared}|{'EVIDENCE_MANIFEST.json'} and len(f.namelist())==len(declared)+1
  assert f.read('EVIDENCE_MANIFEST.json')==manifest
  for r in declared:
   with f.open(r['path']) as src:
    digest=hashlib.file_digest(src,'sha256').hexdigest()
   assert digest==r['sha256'] and f.getinfo(r['path']).file_size==r['bytes'];members.append(r)
 archives.append({'path':str(z),'bytes':z.stat().st_size,'sha256':h,'manifest_sha256':msha,'declared':len(declared),'exact_members_crc_sha256':True})
report={'executor':'Primary GPT Work independent read-only verification','fixed_sha':G,'released_baseline':B,'git_changes':changes,'frozen_files':len(rows),'plan_manifest_members':len(actual),'original_requirements':106,'p7_requirements':[x['id'] for x in p7],'old_tags_unchanged':oldtags,'bundle':base_id['bundle_sha256'],'core_lock':base_id['core_lock_sha256'],'archives':archives,'commands':commands,'environment':{'python':sys.version,'platform':platform.platform(),'os_build':platform.win32_ver(),'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'python_sha256':hashlib.file_digest(Path(sys.executable).open('rb'),'sha256').hexdigest()}}
(O/'PRIMARY_SCOPE.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({'frozen_files':len(rows),'plan_files':len(actual),'archives':archives},ensure_ascii=False))
