"""Primary incremental review integrity; read only candidate and original evidence."""
import json,hashlib,zipfile,subprocess,platform,sys,datetime,csv,io
from pathlib import Path
O=Path(__file__).parent;C=Path('E:/WORK/AQRP-audits/p7-645049a/src');P=C/'docs/audits/phase-7'
H='645049ae9b08710ed93189b80547d14c87d80584';G='3c34e3ca75c9799307b8a98b34f045b40988bbca';B='d563347ad11e1f26e131dc06e343250282c05c33'
commands=[]
def git(*a):
 p=subprocess.run(['git',*a],cwd=C,stdout=subprocess.PIPE,stderr=subprocess.PIPE);commands.append({'argv':['git',*a],'exit':p.returncode,'cwd':str(C),'stderr':p.stderr.decode('utf-8',errors='replace')});assert p.returncode==0;return p.stdout
assert git('rev-parse','HEAD').decode().strip()==H and not git('status','--porcelain')
assert git('rev-list','--parents','-n','1',H).decode().split()==[H,G]
changes=git('diff','--name-status',G,H).decode().splitlines();assert len(changes)==168
assert all(x.startswith(('A\t','M\t')) and (x.split('\t')[-1].startswith('docs/') or x.split('\t')[-1] in ['AGENTS.md','README.md']) for x in changes)
frozen=json.loads((P/'FROZEN_BASELINE_FILES.json').read_bytes())
for r in frozen['files']:
 raw=(C/r['path']).read_bytes();assert len(raw)==r['bytes'] and hashlib.sha256(raw).hexdigest()==r['sha256']
assert len(frozen['files'])==5552
manifest=json.loads((P/'FILE_MANIFEST.json').read_bytes());actual={p.relative_to(P).as_posix() for p in P.rglob('*') if p.is_file()}
assert actual=={r['path'] for r in manifest['files']}|{'FILE_MANIFEST.json'}
for r in manifest['files']:
 b=(P/r['path']).read_bytes();assert len(b)==r['bytes'] and hashlib.sha256(b).hexdigest()==r['sha256']
oldid=json.loads(git('show',G+':docs/audits/phase-6/IMPLEMENTATION_IDENTITY.json'));newid=json.loads((C/'docs/audits/phase-6/IMPLEMENTATION_IDENTITY.json').read_bytes())
assert (P/'g1-3c34e3c/REVIEWED_P6_IDENTITY.json').read_bytes()==git('show',G+':docs/audits/phase-6/IMPLEMENTATION_IDENTITY.json')
metadata=newid['g1_design_revision_metadata'];test=dict(newid);test.pop('g1_design_revision_metadata');test['current_files']=oldid['current_files'];assert test==oldid
oldrows={r['path']:r for r in oldid['current_files']};newrows={r['path']:r for r in newid['current_files']}
assert {k for k in oldrows if oldrows[k]!=newrows[k]}==set(metadata['changed_global_docs'])
for r in newid['current_files']+newid['preserved_files']:
 b=(C/r['path']).read_bytes();assert len(b)==r['bytes'] and hashlib.sha256(b).hexdigest()==r['sha256']
assert len(newid['preserved_files'])==5016
for r in newid['bundle_manifest']['files']:assert hashlib.sha256((C/'src/aqrp'/r['path']).read_bytes()).hexdigest()==r['sha256']
req=list(csv.DictReader(io.StringIO((C/'docs/requirements.csv').read_text(encoding='utf-8-sig'))));snap=json.loads((P/'REQUIREMENTS_SNAPSHOT.json').read_bytes());assert len(req)==106 and [x for x in req if x['phase']=='7']==snap['requirements']
# Check every previous G path omitted from the explicit21 modified paths is still byte-identical to G Git.
modified={x.split('\t')[-1] for x in changes if x.startswith('M\t')};oldfiles=git('ls-tree','-r','--name-only',G).decode().splitlines();unchanged=[p for p in oldfiles if p not in modified]
batch=subprocess.run(['git','cat-file','--batch'],cwd=C,input=''.join(G+':'+p+'\n' for p in unchanged).encode(),stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True)
s=io.BytesIO(batch.stdout)
for p in unchanged:
 h=s.readline().split();assert h[1]==b'blob';b=s.read(int(h[2]));assert s.read(1)==b'\n' and b==(C/p).read_bytes()
assert not s.read();commands.append({'argv':['git','cat-file','--batch'],'count':len(unchanged),'exit':0})
protocol=json.loads((P/'E2E_PROTOCOL_CANDIDATES.json').read_bytes());oldprotocol=json.loads(git('show',G+':docs/audits/phase-7/E2E_PROTOCOL_CANDIDATES.json'))
assert all(protocol[k]==v for k,v in oldprotocol.items())
mathfiles=['GOLDEN_CANDIDATES.json','MAIN_PIPELINE_CANDIDATES.json','MAIN_REFERENCE_METHOD.md','FINANCIAL_FEASIBILITY_CANDIDATES.json','FINANCIAL_FEASIBILITY.md','FINANCIAL_MODEL_BOUNDS.json','FINANCIAL_REFERENCE_METHOD.md','STATISTICAL_CONVENTIONS.md']
mathhashes={}
for n in mathfiles:
 p=P/n
 if p.exists():assert p.read_bytes()==git('show',G+':docs/audits/phase-7/'+n);mathhashes[n]=hashlib.sha256(p.read_bytes()).hexdigest()
large=Path('C:/Users/11638/AppData/Local/Packages/OpenAI.Codex_2p2nqsd0c76g0/LocalCache/Local/AQRP/runs/p6-release-p7-plan-20261024/p7-draft/FINANCIAL_MODEL_ALL_PATHS.json')
assert large.stat().st_size==115159679 and hashlib.file_digest(large.open('rb'),'sha256').hexdigest()=='74d968f318172afa21df2def55a393bcf00efb22531f5c47ee60420364153980'
D=Path('C:/Users/11638/AppData/Local/AQRP/reviews/p7-g1-revision-645049a-20261024');z=D/'Evidence.zip';mb=(D/'EVIDENCE_MANIFEST.json').read_bytes()
assert z.stat().st_size==199866661 and hashlib.file_digest(z.open('rb'),'sha256').hexdigest()=='39f029fb7b52a7d536d85d7a22ff5ab22aac94ed7a1996fb6ca17dfbc2e66b49'
assert hashlib.sha256(mb).hexdigest()=='b6d25c30ad1c625c6752b31094098e5a65bdbd5c457a31631f19d230bc350fd5'
entries=json.loads(mb)['files'];assert len(entries)==329
with zipfile.ZipFile(z) as f:
 assert len(f.namelist())==330 and set(f.namelist())=={r['path'] for r in entries}|{'EVIDENCE_MANIFEST.json'}
 assert f.read('EVIDENCE_MANIFEST.json')==mb
 for r in entries:
  with f.open(r['path']) as stream:h=hashlib.file_digest(stream,'sha256').hexdigest()
  assert h==r['sha256'] and f.getinfo(r['path']).file_size==r['bytes']
received=P/'g1-3c34e3c/received';previous=Path('C:/Users/11638/AppData/Local/AQRP/reviews/p7-g1-3c34e3c-independent-20261024');originals=[]
for p in received.rglob('*'):
 if not p.is_file() or p.name=='.gitattributes':continue
 rel=p.relative_to(received);b=p.read_bytes();assert b==(previous/rel).read_bytes();originals.append({'path':rel.as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()})
assert len(originals)==79
raw=git('ls-remote','origin','refs/heads/main','refs/tags/*').decode();(O/'REMOTE_REFS_FINAL.txt').write_text(raw,encoding='utf-8');refs={x.split()[1]:x.split()[0] for x in raw.splitlines()}
old=previous/'REMOTE_REFS_PRIMARY.txt';oldrefs={x.split()[1]:x.split()[0] for x in old.read_text(encoding='utf-8').splitlines()};assert all(refs[k]==v for k,v in oldrefs.items() if k.startswith('refs/tags/'))
assert refs['refs/heads/main']==B and refs.get('refs/tags/v0.6.0^{}',refs.get('refs/tags/v0.6.0'))==B and refs.get('refs/tags/phase6-baseline^{}',refs.get('refs/tags/phase6-baseline'))==B
pr=json.loads((O/'PR10_START.json').read_bytes())['structuredContent'];assert pr['head_sha']==H and not pr['merged'] and pr['draft']
report={'executor':'Primary GPT Work incremental verifier','fixed_sha':H,'parent':G,'baseline':B,'changed_paths':changes,'unchanged_G_paths_checked':len(unchanged),'frozen_baseline_files':5552,'protected':5016,'source_modules':len(newid['bundle_manifest']['files']),'plan_manifest_members':len(actual),'math_originals_unchanged':mathhashes,'large_math_original_unchanged':True,'MAIN_original_fields_all_unchanged':True,'original_received_copies':originals,'new_archive':{'bytes':199866661,'sha256':'39f029fb7b52a7d536d85d7a22ff5ab22aac94ed7a1996fb6ca17dfbc2e66b49','manifest_sha256':hashlib.sha256(mb).hexdigest(),'declared':329,'members':330,'CRC_all_sizes_hashes_exact_members':True},'commands':commands,'environment':{'python':sys.version,'executable':sys.executable,'platform':platform.platform(),'GIL':True,'python_sha256':hashlib.file_digest(Path(sys.executable).open('rb'),'sha256').hexdigest(),'utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}}
(O/'PRIMARY_INTEGRITY.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in report.items() if k in ['fixed_sha','unchanged_G_paths_checked','frozen_baseline_files','plan_manifest_members','new_archive','source_modules']}))
