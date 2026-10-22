"""Independent proof-orchestration and inventory counterexamples; NO real ACL changes.
Native token/open operations are intentionally modeled and never called here.
"""
import copy,hashlib,importlib.util,json,os,pathlib,sys
from unittest.mock import patch
from aqrp.validation.windows_acl import WindowsTreePolicy
import aqrp.validation.windows_acl as m
O=pathlib.Path(__file__).parent;C=O.parent/'wi-r3-b3d9aef-review';root=O/'model-tree';(root/'work').mkdir(parents=True,exist_ok=True);hidden=root/'work/unseen.json';hidden.write_bytes(b'public engineering file that must not be skipped')
roles={'owner':'operator','evaluator':'eval','research':'research','auditor':'audit'}
p=WindowsTreePolicy(root,**roles,inherited_roots=(root/'work',))
def acl(path,external=False):
 directory=path.is_dir();protected=external or path in (root,root/'work');f=3 if directory else 0
 triples=[('S-1-3-4','Deny',0xC0000),('operator','Allow',0x1F01FF),('S-1-5-18','Allow',0x1F01FF),('S-1-5-32-544','Allow',0x1F01FF),('eval','Allow',0x1200A9 if external else 0x1301BF),('audit','Allow',0x1200A9)]
 return {'path':str(path),'owner':'operator' if protected else 'eval','protected':protected,'entries':[{'sid':s,'type':t,'mask':v,'inheritance':f,'propagation':0,'inherited':not protected} for s,t,v in triples]}
def descriptors(paths):return [acl(path,external=not path.is_relative_to(root)) for path in paths]
scandir=os.scandir
with patch.object(m,'read_descriptors',descriptors):
 good=p.verify();assert good['objects']==3
 def denied(path):
  if pathlib.Path(path).absolute()==root/'work':raise PermissionError(13,'injected traversal error, not a real ACL mutation',str(path))
  return scandir(path)
 with patch.object(os,'scandir',denied):bad=p.verify()
assert bad['objects']==2 and hidden.exists()
# Standalone probe accepts valid real file bytes; access results are an explicit model.
spec=importlib.util.spec_from_file_location('reviewed_probe',C/'tools/windows_access_probe.py');probe=importlib.util.module_from_spec(spec);spec.loader.exec_module(probe)
P=O/'model-probe';P.mkdir(exist_ok=True);objs=[]
for i in range(11):
 path=P/f'actual-{i}.json';path.write_bytes(json.dumps({'public_engineering':i}).encode());objs.append({'path':str(path),'kind':'snapshot_input' if i<9 else ('publication_sidecar' if i==9 else 'dynamic_product'),'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
full_hash=hashlib.sha256(json.dumps(objs,sort_keys=True,separators=(',',':')).encode()).hexdigest();cfg={'scope':'ENGINEERING_DEMO_ONLY','principals':{'research':'r','evaluator':'e','auditor':'a','trusted_owner':'o'},'objects':objs,'operator_inventory_sha256':full_hash,'attempt_id':'engineering-model-only','phase':'after'};checks=[]
def perform(c,role):
 def opened(path,mask):
  allowed=role!='research' and mask==1 or role=='evaluator' and str(path)==objs[-1]['path'] and mask in (2,4,0x10000)
  return {'opened':allowed,'winerror':0 if allowed else 5,'mask':mask}
 return probe.probe(c,role,get_token=lambda:{'sid':c['principals'][role],'elevated':False},open_access=opened)
for role in ['research','auditor','evaluator']:
 baseline=perform(cfg,role);assert baseline['all_pass']
 truncated=copy.deepcopy(cfg);truncated['objects']=truncated['objects'][:10];result=perform(truncated,role);assert result['all_pass'];checks.append({'role':role,'full_object_count':11,'supplied_object_count':10,'omitted_existing_dynamic_file':objs[-1]['path'],'authoritative_full_inventory_hash':full_hash,'hash_field_unchanged':truncated['operator_inventory_sha256']==full_hash,'observed_all_pass':result['all_pass'],'checks_run':len(result['checks'])})
# All directory access outcomes are correct in the model, yet read_bytes cannot
# verify directory listing/membership and FILE_DELETE_CHILD(0x40) is never requested.
dirpath=P/'directory-boundary';dirpath.mkdir(exist_ok=True);dcfg=copy.deepcopy(cfg);dcfg['objects'].append({'path':str(dirpath),'kind':'directory_boundary','bytes':0,'sha256':hashlib.sha256(b'').hexdigest()});d=perform(dcfg,'auditor');dirchecks=[c for c in d['checks'] if c['path']==str(dirpath)]
record={'fixed_sha':'b3d9aef79396db948d326f5ce247131f96739d9d','actual_executor':'GPT Work supplemental reviewer','scope':'MODEL ADAPTER counterexamples only; all real accounts remain disabled, no ACL changes or token logons','tree_positive':{'objects':good['objects']},'tree_enumeration_error':{'observed_returned_success':True,'objects_checked':bad['objects'],'existing_omitted_file':str(hidden),'expected':'Fail closed on any directory enumeration error; never certify subset'},'truncated_inventory':checks,'directory_probe':{'observed_all_pass':d['all_pass'],'checks':dirchecks,'delete_child_mask_0x40_tested':any(c.get('observed',{}).get('mask')==0x40 for c in dirchecks)},'installed_module':m.__file__};(O/'INDEPENDENT_COUNTEREXAMPLES.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in record.items() if k not in ['truncated_inventory','directory_probe']}));print('truncated inventories accepted for 3 modeled roles; directory boundary unsupported as a byte file.')
