import pathlib,json,zipfile,io,hashlib,subprocess,xml.etree.ElementTree as ET,datetime
O=pathlib.Path(__file__).parent;C=O.parent/'wi-r3-b3d9aef-review';D=O.parent/'windows-isolation-r3-b3d9aef';FIX='b3d9aef79396db948d326f5ce247131f96739d9d';MERGE='b7ed8fbd6538f3edc3d99d7251cb2d6d3c83628e'
def H(b):return hashlib.sha256(b).hexdigest()
def canon(x):return json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()
def git(*args):return subprocess.check_output(['git','-C',str(C),*args]).decode().strip()
assert git('rev-parse',FIX+'^{tree}')==git('rev-parse',MERGE+'^{tree}');assert git('show','-s','--format=%P',MERGE).split()==['0a57dccb5618ba08cd3572d6d6b78fec963a3041',FIX]
class Z:
 def __init__(self,path):
  self.z=zipfile.ZipFile(path);assert self.z.testzip() is None;self.prefix=self.z.namelist()[0].split('/')[0]+'/';self.names={n[len(self.prefix):] for n in self.z.namelist()};assert len(self.names)==len(self.z.namelist())
 def read(self,n):return self.z.read(self.prefix+n)
class Dir:
 def __init__(self,p):self.p=p
 def read(self,n):return (self.p/n).read_bytes()
def verify(label,r,commit):
 J=lambda n:json.loads(r.read(n));sel=J('upload-selection.json');expected={e['path'] for e in sel['files']}
 if isinstance(r,Z):assert r.names==expected|{'upload-selection.json'}
 for e in sel['files']:assert H(r.read(e['path']))==e['sha256'],e['path']
 env=J('environment.json');assert env['complete'] and not env['dirty'] and env['code_commit']==commit and env['lock_sha256']=='86c7bf65c9a9690036006360062c8cd10a91279705b4070af7033d7699abffeb'
 xml=ET.fromstring(r.read('junit.xml'));assert len(xml.findall('.//testcase'))==628 and not xml.findall('.//failure') and not xml.findall('.//error') and not xml.findall('.//skipped')
 cov=J('coverage.json');assert len(cov['files'])==47;critical=[]
 for p,d in cov['files'].items():
  if p.endswith(('windows_acl.py','engineering_input.py')):
   s=d['summary'];line=s['covered_lines']/s['num_statements'];branch=s['covered_branches']/s['num_branches'];assert line>=.95 and branch>=.9;critical.append({'file':p,'line':line,'branch':branch})
 wheel=next(n for n in expected if n.startswith('wheel/') and n.endswith('.whl'));raw=r.read(wheel);assert H(raw)==env['wheel_sha256']
 with zipfile.ZipFile(io.BytesIO(raw)) as wh:
  py=[n for n in wh.namelist() if n.startswith('aqrp/') and n.endswith('.py')];assert len(py)==47
  for n in py:assert wh.read(n)==(C/'src'/n).read_bytes(),n
  assert wh.read('aqrp/factors/reviewed_code.json')==(C/'src/aqrp/factors/reviewed_code.json').read_bytes()
 snapshots=[];chains=[]
 for n in sorted(x for x in expected if x.endswith('/manifest.json')):
  m=J(n);parent=str(pathlib.PurePosixPath(n).parent)
  if 'tables'in m:
   assert H(canon({k:v for k,v in m.items() if k not in ['manifest_hash','snapshot_id']}))==m['manifest_hash'] and len(m['tables'])==8
   for e in m['tables'].values():assert H(r.read(parent+'/'+e['path']))==e['sha256']
   snapshots.append({'path':n,'hash':m['manifest_hash']})
  if 'event_prefix_hash'in m:
   for e in m['files']:assert H(r.read(parent+'/'+e['path']))==e['sha256']
   events=[json.loads(l) for l in r.read(parent+'/events.jsonl').splitlines()];prev='0'*64
   for i,e in enumerate(events):assert e['seq']==i and e['previous']==prev and H(canon({k:v for k,v in e.items() if k!='hash'}))==e['hash'];prev=e['hash']
   assert events[-1]['kind']==m['status'] and events[-1]['payload']['manifest_sha256']==H(r.read(n)) and events[-2]['hash']==m['event_prefix_hash'];chains.append({'path':n,'records':len(events),'status':m['status']})
  if 'artifacts'in m:
   for e in m['artifacts']:assert H(r.read(parent+'/'+e['path']))==e['sha256']
 export=J('windows-engineering-input/MANIFEST.json');assert len(export['files'])==9 and export['actual_three_token_access']=='NOT_EXECUTED' and export['deployment']=='NOT_DEPLOYED';assert export['snapshot_manifest_hash']=='edd5bc05cc2ddd29740db95c95270e0c3004217712feb2421234107c2f7c9031'
 with zipfile.ZipFile(io.BytesIO(r.read('windows-engineering-input/nine-input-files-original.zip'))) as z:
  assert z.testzip() is None and set(z.namelist())=={e['path'] for e in export['files']}
  for e in export['files']:
   b=z.read(e['path']);assert len(b)==e['bytes'] and H(b)==e['sha256'];assert b==r.read('windows-engineering-input/private-source/'+export['snapshot_id']+'/'+e['path'])
 repro=J('reproduction/result.json');assert repro['status']=='THREE_ORIGINAL_REFS_EXECUTED'
 for factor,v in [('momentum',.21),('reversal',-.21),('volume',.6)]:assert repro['results'][factor]['result']['rows'][0]['factor_value']==v
 replay=J('reproduction/published-original-replay.json');assert len(replay['runs'])==3
 dest=O/'evidence-extracts'/label;dest.mkdir(parents=True,exist_ok=True)
 for n in ['environment.json','junit.xml','coverage.json','commands.log','upload-selection.json','artifacts.json','windows-engineering-input/MANIFEST.json','reproduction/result.json','reproduction/environment-archive.json','reproduction/published-original-replay.json']:
  p=dest/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(r.read(n))
 return {'label':label,'executed_commit':commit,'tests_passed':628,'selection_members_rehashed':len(sel['files']),'zip_members':len(r.names) if isinstance(r,Z) else None,'wheel_modules_byte_identical':47,'wheel_hash':H(raw),'critical_coverage':critical,'snapshots':snapshots,'terminal_chains':chains,'new_nine_inputs_hash':export['snapshot_manifest_hash'],'three_original_refs_verified':True,'environment':env,'result':'PASS'}
results=[verify(os,Z(O/(os+'-original.zip')),MERGE) for os in ['Windows','Ubuntu']]
# Add local SDK only if it actually reached complete success.
log=(O/'clean-sdk-short.stdout.log').read_text(encoding='utf-8-sig');sdk=pathlib.Path(log.split('Artifacts: ',1)[1].splitlines()[0]);assert (sdk/'environment.json').exists();env=json.loads((sdk/'environment.json').read_bytes());assert env['complete'],'local SDK not yet complete';results.append(verify('GPT-Work-local',Dir(sdk),FIX));(O/'SDK_LOCATION.json').write_text(json.dumps({'sdk_root':str(sdk),'failed_first_sdk_retained':str(next((O/'sdk').iterdir()))},indent=2)+'\n',encoding='utf-8')
seal=json.loads((D/'Developer-Evidence-Seal.json').read_bytes())
for e in seal['files']:
 p=D/e['path'];assert p.stat().st_size==e['bytes']
 with p.open('rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()==e['sha256']
archive=D/'Developer-Windows-Isolation-R3-Evidence.zip';manifest=seal['manifest']
with zipfile.ZipFile(archive) as z:
 assert z.testzip() is None
 for e in manifest['files']:
  b=z.read(e['path']);assert len(b)==e['bytes'] and H(b)==e['sha256']
 extra=set(z.namelist())-{e['path'] for e in manifest['files']};assert len(extra)==1 and json.loads(z.read(next(iter(extra))))==manifest
(O/'Developer-Evidence-Seal-received.json').write_bytes((D/'Developer-Evidence-Seal.json').read_bytes())
result={'actual_executor':'GPT Work supplemental reviewer','fixed_sha':FIX,'merge_tree_equal':True,'merge_sha':MERGE,'results':results,'developer_archive':{'path':str(archive),'bytes':archive.stat().st_size,'sha256':'a27ef6ca5e899cda4baee3a1c212eaafc9555d1566adb41ec613f88597c049fd','manifest_members':len(manifest['files']),'zip_members':len(manifest['files'])+1,'all_hashes_and_crc_verified':True},'note':'Linux was executed by GitHub runner; its raw artifacts were independently verified on Windows, not a new GPT Work Linux OS isolation run.'};(O/'ARCHIVE_VERIFICATION.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps([{k:d[k] for k in ['label','tests_passed','selection_members_rehashed','wheel_modules_byte_identical','result']} for d in results]))
