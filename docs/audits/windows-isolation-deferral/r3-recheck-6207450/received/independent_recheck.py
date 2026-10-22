"""Independent regression and orchestration audit; modeled ACLs/tokens, ordinary real files."""
import pathlib,json,hashlib,uuid,copy,os,importlib.util,zipfile,stat
from unittest.mock import patch
from aqrp.validation import windows_acl as acl
from aqrp.validation import evaluator
from aqrp.validation.engineering_input import publish_engineering_input
from aqrp.core.contracts import SnapshotRef
from aqrp.core.errors import ContractError
O=pathlib.Path(__file__).parent;C=O.parent/'wi-recheck-6207450';FIX='62074502aa4c32556b5e690bac10bd8054bd9178'
canon=lambda x:json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode();H=lambda b:hashlib.sha256(b).hexdigest()
def save(name,x):(O/name).write_bytes(canon(x))
roles={'owner':'MODEL-OPERATOR','evaluator':'MODEL-EVALUATOR','research':'MODEL-RESEARCH','auditor':'MODEL-AUDITOR'}
root=O/'independent-model/sealed';(root/'inputs').mkdir(parents=True);(root/'work').mkdir();key=root/'key';key.write_bytes(b'PUBLIC ENGINEERING MODEL MATERIAL ONLY')
p=acl.WindowsTreePolicy(root,**roles,inherited_roots=(root,),readonly_roots=(root/'inputs',),key_file=key)
def descriptors(paths):
 rows=[]
 for path in paths:
  directory=path.is_dir();external=not path.is_relative_to(root);protected=external or path in (root,root/'inputs',key);readonly=external or p.is_readonly(path) or path==key;flags=3 if directory else 0
  triples=[('S-1-3-4','Deny',0xC0000),(roles['owner'],'Allow',0x1F01FF),('S-1-5-18','Allow',0x1F01FF),('S-1-5-32-544','Allow',0x1F01FF),(roles['evaluator'],'Allow',0x1200A9 if readonly else 0x1301BF)]
  if path!=key:triples.append((roles['auditor'],'Allow',0x1200A9))
  rows.append({'path':str(path),'owner':roles['owner'] if protected or readonly else roles['evaluator'],'protected':protected,'entries':[{'sid':s,'type':t,'mask':m,'inheritance':flags,'propagation':0,'inherited':not protected} for s,t,m in triples]})
 return rows
work=root/'work';(work/'unseen.json').write_bytes(b'cannot be skipped')
enum_records=[];scan=os.scandir
class Scan:
 def __init__(self,path,*,mode,active):self.path=path;self.mode=mode;self.active=active;self.native=scan(path)
 def __enter__(self):self.native.__enter__();return self
 def __exit__(self,*a):return self.native.__exit__(*a)
 def __iter__(self):return self
 def __next__(self):
  if self.active and self.mode=='iteration':raise OSError(5,'MODEL iterator I/O error',str(self.path))
  e=next(self.native)
  if self.active and self.mode=='entry_stat':
   class Entry:
    name=e.name
    def stat(self,**kw):raise PermissionError(13,'MODEL DirEntry metadata failure',e.path)
   return Entry()
  return e
with patch.object(acl,'read_descriptors',descriptors):
 positive=p.verify();assert positive['objects']==5 and positive['enumeration_complete']
 for phase in ('before','after'):
  for mode in ('open_permission','open_missing','open_io','iteration','entry_stat'):
   count=[0];cause=[]
   def wrapped(path):
    active=False
    if pathlib.Path(path)==work:count[0]+=1;active=count[0]==(1 if phase=='before' else 2)
    if active and mode.startswith('open_'):
     cls,num={'open_permission':(PermissionError,13),'open_missing':(FileNotFoundError,2),'open_io':(OSError,5)}[mode];e=cls(num,'MODEL native enumeration fault',str(path));cause.append(e);raise e
    return Scan(path,mode=mode,active=active)
   try:
    with patch.object(os,'scandir',wrapped):p.verify()
    raise AssertionError('incomplete tree accepted')
   except ContractError as e:
    assert e.code=='ACL_ENUMERATION_FAILED';detail=json.loads(e.field);assert detail['phase']==phase and str(work) in detail['path'] and e.__cause__ is not None
    enum_records.append({'phase':phase,'fault':mode,'code':e.code,'detail':detail,'cause_type':type(e.__cause__).__name__})
 # Target the separate identity capture pass, not just DirEntry classification.
 lstat=pathlib.Path.lstat
 for phase in ('before','after'):
  count=[0]
  def missing(path,*a,**kw):
   if path==work/'unseen.json':
    count[0]+=1
    if count[0]==(1 if phase=='before' else 2):raise FileNotFoundError(2,'MODEL lstat failure',str(path))
   return lstat(path,*a,**kw)
  try:
   with patch.object(pathlib.Path,'lstat',missing):p.verify()
   raise AssertionError('metadata missing accepted')
  except ContractError as e:assert e.code=='ACL_TREE_METADATA_FAILED';enum_records.append({'phase':phase,'fault':'lstat','detail':json.loads(e.field),'code':e.code})
 # Complete new-protocol positive control built without repository test helpers.
 source=O/'independent-source';source.mkdir();export=json.loads((O/'Engineering-inputs-manifest-received.json').read_bytes());sid=export['snapshot_id'];(source/sid).mkdir()
 with zipfile.ZipFile(O/'Nine-engineering-inputs-original.zip') as z:
  assert z.testzip() is None and set(z.namelist())=={e['path'] for e in export['files']}
  for e in export['files']:
   b=z.read(e['path']);assert len(b)==e['bytes'] and H(b)==e['sha256'];(source/sid/e['path']).write_bytes(b)
 source_ref=SnapshotRef(source,sid,export['snapshot_manifest_hash'])
 with patch.object(evaluator,'identity',lambda:roles['owner']):ref=publish_engineering_input(source_ref,root/'inputs',tree_policy=p)
 spec=importlib.util.spec_from_file_location('audited_probe',C/'tools/windows_access_probe.py');probe=importlib.util.module_from_spec(spec);spec.loader.exec_module(probe)
 owner=lambda:{'sid':roles['owner'],'elevated':False,'source':'MODEL_ADAPTER'}
 attempt=str(uuid.uuid4());before=probe.freeze_inventory(p,ref,attempt,'before',get_token=owner);before_sha=H(before);save('independent-before-inventory.json',json.loads(before))
 def expected(item,role):
  directory=item['object_type']=='directory';rd=role!='research' and not(role=='auditor' and item['path']==str(key));wr=role=='evaluator' and not pathlib.Path(item['path']).is_relative_to(root/'inputs') and item['path']!=str(key)
  masks={'list_directory' if directory else 'read':(1,rd),'create_file' if directory else 'write_data':(2,wr),'create_directory' if directory else 'append':(4,wr),'change_dacl':(0x40000,False),'take_ownership':(0x80000,False),'delete':(0x10000,wr)}
  if directory:masks['delete_child']=(0x40,False)
  return masks
 def perform(raw,cfg,role,override=None):
  inv=json.loads(raw);items={r['path']:r for r in inv['objects']}
  def opened(path,mask):
   item=items[str(path)];want={m:v for m,v in expected(item,role).values()}[mask]
   return {'opened':want,'winerror':0 if want else 5,'mask':mask,'disposition':'MODEL_OPEN_EXISTING'}
  result=probe.probe(cfg,role,inventory_raw=raw,inventory_sha256=H(raw),get_token=lambda:{'sid':cfg['principals'][role],'elevated':False,'source':'MODEL_ADAPTER'},open_access=override or opened)
  return result
 negatives=[];phases=[]
 def reject(name,fn):
  try:fn();raise AssertionError('accepted '+name)
  except (ValueError,ContractError,OSError,KeyError) as e:negatives.append({'case':name,'exception':type(e).__name__,'reason':str(e)})
 for phase in ('before','after'):
  if phase=='after':
   directory=work/'new';directory.mkdir();(directory/'actual-result.json').write_bytes(b'public new dynamic product');(work/'unseen.json').unlink()
  raw=before if phase=='before' else probe.freeze_inventory(p,ref,attempt,'after',get_token=owner,before_raw=before,before_sha256=before_sha)
  inv=json.loads(raw);cfg=probe.probe_config(raw,H(raw));save('independent-'+phase+'-inventory.json',inv);save('independent-'+phase+'-config.json',cfg)
  if phase=='after':assert inv['added_paths']==sorted([str(directory),str(directory/'actual-result.json')]) and inv['removed_paths']==[str(work/'unseen.json')] and inv['predecessor_sha256']==before_sha
  results=[]
  for role in ('research','evaluator','auditor'):
   r=perform(raw,cfg,role);assert r['listed_checks_pass'] and not r['all_pass'] and not r['coverage_verified'] and r['execution_mode']=='MODEL_ADAPTER'
   for item in inv['objects']:
    observed={c['operation']:c for c in r['checks'] if c['path']==item['path']}
    for op,(mask,want) in expected(item,role).items():assert observed[op]['observed']['mask']==mask and observed[op]['expected_open']==want
    if item['object_type']=='directory':assert 'actual_bytes' not in observed and 'delete_child' in observed
   save('independent-'+phase+'-'+role+'.json',r);results.append(r)
   for omitted in ('dynamic_product','directory_boundary'):
    bad=copy.deepcopy(cfg);target=next(x for x in bad['objects'] if x['kind']==omitted and x['path']!=str(root));bad['objects'].remove(target);assert bad['operator_inventory_sha256']==H(raw);reject(phase+'-'+role+'-omit-'+omitted,lambda:perform(raw,bad,role))
  kw={'get_token':owner,**({'before_raw':before,'before_sha256':before_sha} if phase=='after' else {})}
  good=probe.reconcile(cfg,raw,H(raw),results,**kw);assert good['coverage_verified'] and good['all_pass'] and not good['real_token_claims'] and good['overall_windows_isolation']=='NOT_VERIFIED';save('independent-'+phase+'-reconciled.json',good);phases.append({'phase':phase,'objects':len(inv['objects']),'checks':{r['role']:len(r['checks']) for r in results},'receipt':good})
  for mutation in ('missing_role','duplicate_role','missing_check','extra_check','wrong_mask','native_error_2','wrong_context','wrong_sid','elevated','wrong_content','wrong_members'):
   bad=copy.deepcopy(results)
   if mutation=='missing_role':bad.pop()
   if mutation=='duplicate_role':bad[2]=copy.deepcopy(bad[1])
   if mutation=='missing_check':bad[0]['checks'].pop()
   if mutation=='extra_check':bad[0]['checks'].append(copy.deepcopy(bad[0]['checks'][0]))
   if mutation=='wrong_mask':bad[0]['checks'][0]['observed']['mask']=0x40
   if mutation=='native_error_2':bad[0]['checks'][0]['observed']['winerror']=2
   if mutation=='wrong_context':bad[0]['attempt_id']=str(uuid.uuid4())
   if mutation=='wrong_sid':bad[0]['token']['sid']='MODEL-WRONG-SID'
   if mutation=='elevated':bad[0]['token']['elevated']=True
   if mutation=='wrong_content':next(c for c in bad[1]['checks'] if c['operation']=='actual_bytes')['sha256']='0'*64
   if mutation=='wrong_members':next(c for c in bad[1]['checks'] if c['operation']=='actual_members')['members']=[]
   reject(phase+'-reconcile-'+mutation,lambda:probe.reconcile(cfg,raw,H(raw),bad,**kw))
  extra=work/'unlisted-drift.json';extra.write_bytes(b'must be seen by mandatory fresh collection');reject(phase+'-fresh-extra-path',lambda:probe.reconcile(cfg,raw,H(raw),results,**kw));extra.unlink()
  existing=next(pathlib.Path(r['path']) for r in inv['objects'] if r['kind']=='dynamic_product');original=existing.read_bytes();existing.write_bytes(original+b'changed');reject(phase+'-fresh-changed-bytes',lambda:probe.reconcile(cfg,raw,H(raw),results,**kw));existing.write_bytes(original)
  reject(phase+'-wrong-inventory-hash',lambda:probe.probe_config(raw,'0'*64))
  # Recollection errors must reject rather than treat a subset as unchanged.
  def denied(path):
   if pathlib.Path(path)==work:raise PermissionError(13,'MODEL fresh recapture denied',str(path))
   return scan(path)
  with patch.object(os,'scandir',denied):reject(phase+'-fresh-enumeration-denied',lambda:probe.reconcile(cfg,raw,H(raw),results,**kw))
 reject('after-missing-predecessor',lambda:probe.freeze_inventory(p,ref,attempt,'after',get_token=owner))
 reject('after-cross-attempt',lambda:probe.freeze_inventory(p,ref,str(uuid.uuid4()),'after',get_token=owner,before_raw=before,before_sha256=before_sha))
 # Directory content probe rejects actual listing errors even with modeled open rights.
 iterdir=pathlib.Path.iterdir
 def listing(path):
  if path==work:raise PermissionError(13,'MODEL listing denied',str(path))
  return iterdir(path)
 with patch.object(pathlib.Path,'iterdir',listing):bad=perform(raw,cfg,'auditor')
 assert not bad['listed_checks_pass'];save('independent-directory-list-failure.json',bad)
summary={'fixed_sha':FIX,'scope':'MODEL ADAPTERS with real ordinary engineering file operations only; no real ACL writes or three-subject execution','strict_collection_controls':enum_records,'phases':phases,'negative_controls':negatives,'actual_directory_listing_failure_rejected':True,'installed_gate_module':acl.__file__,'probe_source_sha256':H((C/'tools/windows_access_probe.py').read_bytes()),'overall_windows_isolation':'NOT_VERIFIED','formal_Test':False,'financial_approval':'NONE','result':'PASS'}
save('INDEPENDENT_RECHECK_RESULTS.json',summary);print(json.dumps({'strict_collection_rejections':len(enum_records),'phase_complete_positives':len(phases),'negative_controls':len(negatives),'directory_listing_failure_rejected':True,'result':'PASS'}))
