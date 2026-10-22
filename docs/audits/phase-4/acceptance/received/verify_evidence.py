import pathlib,json,hashlib,zipfile,io,subprocess,sys,xml.etree.ElementTree as ET
from fractions import Fraction as Q
from decimal import Decimal,localcontext,Context,ROUND_HALF_EVEN
from independent_reference import reference
O=pathlib.Path(__file__).parent;C=O.parent/'p4-g2-recheck-3c87579';FIX='3c8757949b0fd5c97953b06a74ebc2d0e56676e4';MERGE='354c931ef05d8d16237efac5826ae47302175f4f'
def canon(x):return json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()
def H(b):return hashlib.sha256(b).hexdigest()
def projected(q):
 d=q.denominator
 for p in (2,5):
  while d%p==0:d//=p
 if d==1:return q
 with localcontext(Context(prec=34,rounding=ROUND_HALF_EVEN)):return Q(Decimal(q.numerator)/Decimal(q.denominator))
def compare(a,e):
 if isinstance(e,dict):
  for k,v in e.items():compare(a[k],v)
 else:assert Q(a)==projected(e),(a,str(e))
def git(*a):return subprocess.check_output(['git','-C',str(C),*a]).decode().strip()
assert git('rev-parse',FIX+'^{tree}')==git('rev-parse',MERGE+'^{tree}')
parents=git('show','-s','--format=%P',MERGE).split();assert parents==['0a57dccb5618ba08cd3572d6d6b78fec963a3041',FIX]
class ZipReader:
 def __init__(self,p):self.z=zipfile.ZipFile(p);assert self.z.testzip() is None;self.prefix=self.z.namelist()[0].split('/')[0]+'/';self.names={n[len(self.prefix):] for n in self.z.namelist() if not n.endswith('/')};assert len(self.z.namelist())==len(self.names)
 def read(self,n):return self.z.read(self.prefix+n)
class DirReader:
 def __init__(self,p):self.root=p;self.names={x.relative_to(p).as_posix() for x in p.rglob('*') if x.is_file()}
 def read(self,n):return (self.root/n).read_bytes()
def verify(label,r,executed):
 J=lambda n:json.loads(r.read(n));sel=J('upload-selection.json');selected={e['path'] for e in sel['files']}
 if isinstance(r,ZipReader):assert r.names==selected|{'upload-selection.json'}
 for e in sel['files']:assert H(r.read(e['path']))==e['sha256'],(label,e['path'])
 env=J('environment.json');assert env['complete'] and not env['dirty'] and env['code_commit']==executed and env['lock_sha256']=='86c7bf65c9a9690036006360062c8cd10a91279705b4070af7033d7699abffeb'
 root=ET.fromstring(r.read('junit.xml'));tests=root.findall('.//testcase');assert len(tests)==844 and not root.findall('.//failure') and not root.findall('.//error') and not root.findall('.//skipped')
 coverage=J('coverage.json');assert len(coverage['files'])==53
 modules=[]
 for path,d in coverage['files'].items():
  path=path.replace('\\','/');s=d['summary'];line=s['covered_lines']/max(1,s['num_statements']);branch=s['covered_branches']/s['num_branches'] if s['num_branches'] else 1
  if '/portfolio/' in path or '/risk/' in path:assert not s['num_statements'] or line>=.95 and branch>=.90;modules.append({'path':path,'line':line,'branch':branch})
 wheel=next(n for n in selected if n.startswith('wheel/') and n.endswith('.whl'));raw=r.read(wheel);assert H(raw)==env['wheel_sha256']
 with zipfile.ZipFile(io.BytesIO(raw)) as wh:
  pyfiles=[n for n in wh.namelist() if n.endswith('.py') and n.startswith('aqrp/')];assert len(pyfiles)==53
  for p in pyfiles:assert wh.read(p)==(C/'src'/p).read_bytes(),p
  assert wh.read('aqrp/factors/reviewed_code.json')==(C/'src/aqrp/factors/reviewed_code.json').read_bytes()
 snapshots=[];experiments=[];factors=[]
 for p in sorted(n for n in selected if n.endswith('/manifest.json')):
  m=J(p);parent=str(pathlib.PurePosixPath(p).parent)
  if 'tables' in m:
   assert H(canon({k:v for k,v in m.items() if k not in ('snapshot_id','manifest_hash')}))==m['manifest_hash'];assert len(m['tables'])==8
   for e in m['tables'].values():assert H(r.read(parent+'/'+e['path']))==e['sha256']
   snapshots.append({'path':p,'hash':m['manifest_hash']})
  if 'event_prefix_hash' in m:
   for e in m['files']:assert H(r.read(parent+'/'+e['path']))==e['sha256']
   events=[json.loads(l) for l in r.read(parent+'/events.jsonl').splitlines()];prev='0'*64
   for i,event in enumerate(events):
    assert event['seq']==i and event['previous']==prev and H(canon({k:v for k,v in event.items() if k!='hash'}))==event['hash'];prev=event['hash']
   assert events[-1]['kind']==m['status'] and events[-1]['payload']['manifest_sha256']==H(r.read(p)) and events[-2]['hash']==m['event_prefix_hash'];experiments.append({'path':p,'status':m['status'],'event_records':len(events)})
  if 'artifacts' in m:
   for e in m['artifacts']:assert H(r.read(parent+'/'+e['path']))==e['sha256']
   factors.append({'path':p,'logical_hash':m['logical_hash']})
 portfolio=J('portfolio/summary.json');assert portfolio['orders_submitted']==0 and not portfolio['account_ledger_written'] and portfolio['financial_approval']=='NONE';assert portfolio['formal_gate']['reasons']==['APPROVAL_REQUIRED']
 for case in portfolio['outcomes']:
  x=J('portfolio/inputs/'+case['name']+'.json');expect=reference(x);assert case['status']==expect['status'];assert case['replay']=='IMMUTABLE_ORIGINAL_RESULT_VERIFIED'
  matches=[p for p in selected if p.startswith('portfolio/') and p.endswith('/'+case['run_id']+'/result.json')];assert len(matches)==1;result=J(matches[0]);assert result['status']==expect['status'] and ('target'in result)==(expect['status']=='SUCCEEDED')
  directory=str(pathlib.PurePosixPath(matches[0]).parent)
  assert J(directory+'/risk.json')==result['risk']
  for phase in ('pre','post'):compare(result['risk'][phase]['metrics'],expect[phase]['metrics'])
  if result['status']=='SUCCEEDED':
   compare(result['target'],expect['post']['metrics']);audit=J(directory+'/published-byte-audit.json');assert audit['result_sha256']==H(r.read(matches[0]))
   assert audit['risk_sha256']==result['risk']['content_sha256']
 repro=J('reproduction/result.json');assert repro['status']=='THREE_ORIGINAL_REFS_EXECUTED'
 for factor,expected in [('momentum',.21),('reversal',-.21),('volume',.6)]:assert repro['results'][factor]['result']['rows'][0]['factor_value']==expected
 # Store compact selected raw logs and receipts outside the immutable upstream ZIP.
 dest=O/'evidence-extracts'/label;dest.mkdir(parents=True,exist_ok=True)
 for name in ['environment.json','junit.xml','coverage.json','commands.log','upload-selection.json','artifacts.json','portfolio/summary.json','reproduction/result.json','reproduction/published-original-replay.json','reproduction/environment-archive.json']:
  if name in selected or name=='upload-selection.json':p=dest/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(r.read(name))
 return {'label':label,'executed_sha':executed,'official_head_sha':FIX,'source_tree':git('rev-parse',executed+'^{tree}'),'junit_passed':len(tests),'selection_hashes_verified':len(sel['files']),'zip_members':len(r.names) if isinstance(r,ZipReader) else None,'wheel_sha256':H(raw),'wheel_modules_byte_identical':53,'p4_coverage':modules,'snapshot_manifests':snapshots,'terminal_experiment_manifests':experiments,'factor_manifests':factors,'six_portfolio_cases_independently_recomputed':True,'original_three_refs_values_verified':True,'environment':env,'result':'PASS'}
results=[]
if '--local-only' not in sys.argv:
 for label in ['Windows','Ubuntu']:results.append(verify(label,ZipReader(O/(label+'-original.zip')),MERGE))
if '--official-only' not in sys.argv:
 sdk=pathlib.Path((O/'SDK_LOCATION.txt').read_text(encoding='utf-8'));results.append(verify('GPT-Work-local',DirReader(sdk),FIX))
if '--official-only' in sys.argv:
 (O/'CI_RAW_EVIDENCE_VERIFICATION.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
elif '--local-only' in sys.argv:results=json.loads((O/'CI_RAW_EVIDENCE_VERIFICATION.json').read_bytes())+results
(O/'RAW_EVIDENCE_VERIFICATION.json').write_text(json.dumps({'fixed_sha':FIX,'merge_tree_equal':True,'merge_parents':parents,'results':results,'note':'Ubuntu actions was executed by GitHub runner, raw bytes independently verified here on Windows; not a GPT Work Linux execution.'},ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps([{k:d[k] for k in ['label','junit_passed','selection_hashes_verified','wheel_modules_byte_identical','result']} for d in results]))

