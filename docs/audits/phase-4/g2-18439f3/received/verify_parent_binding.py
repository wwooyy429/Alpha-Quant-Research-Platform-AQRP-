import pathlib,json,hashlib
from aqrp.portfolio.contracts import PortfolioRequest
from aqrp.portfolio.service import construct_engineering
O=pathlib.Path(__file__).parent;C=O.parent/'p4-g2-18439f3-review';FIX='18439f31536295aea42e57e566d07cce345a35cf';OUT=O/'parent-binding-runs';OUT.mkdir(exist_ok=True)
def canon(x):return json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()
# Reuse original valid binding frozen by the prior positive control, not a regenerated score.
a=json.loads((O/'ADVERSARIAL_RESULTS.json').read_bytes())['records'];positive=next(x for x in a if x['case']=='original-snapshot-id');cfg=json.loads((O/'adversarial-runs'/positive['run_id']/'config.json').read_bytes());original=json.loads(bytes.fromhex(cfg['raw_request_hex']));sid=original['context']['snapshot_id'];src=C/'docs/audits/phase-3/publication/sdk/research/inputs/dataset'/sid/'manifest.json';manifest=json.loads(src.read_bytes());hash_value=hashlib.sha256(canon({k:v for k,v in manifest.items() if k not in ['snapshot_id','manifest_hash']})).hexdigest();assert hash_value==manifest['manifest_hash']==original['context']['snapshot_sha256']
for t in manifest['tables'].values():assert hashlib.sha256((src.parent/t['path']).read_bytes()).hexdigest()==t['sha256']
newid='00000000-0000-4000-8000-000000000001';original['context']['snapshot_id']=newid
entries=[e for k,e in original['inputs'].items() if k!='scores']+original['inputs']['scores']
for e in entries:
 e['context']['snapshot_id']=newid;e['content_sha256']=hashlib.sha256(canon({k:v for k,v in e.items() if k!='content_sha256'})).hexdigest()
original['source']['fixture_manifest']={e['ref']:e['content_sha256'] for e in entries};r=construct_engineering(PortfolioRequest(canon(original)),OUT,FIX).read()
proof={'fixed_sha':FIX,'source_manifest_file':str(src),'source_snapshot_id':sid,'source_snapshot_hash':hash_value,'source_table_hashes_independently_verified':8,'mutated_id_is_valid_uuid':newid,'source_p3_artifact_bytes_unchanged':True,'status':r['status'],'run_id':r['run_id'],'published_context':r.get('context'),'expected':'Reject mismatching actual parent snapshot ID, or carry and verify an explicit distinct projection identity without claiming it is the source parent ID.'};(O/'PARENT_BINDING_PROOF.json').write_text(json.dumps(proof,indent=2)+'\n',encoding='utf-8');(O/'original-p3-snapshot-manifest.json').write_bytes(src.read_bytes());print(json.dumps(proof))
