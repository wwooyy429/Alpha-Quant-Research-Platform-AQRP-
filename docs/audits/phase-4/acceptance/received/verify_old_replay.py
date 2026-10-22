import pathlib,json,hashlib
from aqrp.portfolio.service import replay_engineering,construct_engineering
from aqrp.portfolio.contracts import PortfolioRequest
O=pathlib.Path(__file__).parent;OLD=O.parent/'work-p4-g2-18439f3-independent';FIX='3c8757949b0fd5c97953b06a74ebc2d0e56676e4'
H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
before={str(p.relative_to(OLD)):H(p) for d in ('adversarial-runs','parent-binding-runs') for p in (OLD/d).rglob('*') if p.is_file()}
records=[]
for r in json.loads((OLD/'ADVERSARIAL_RESULTS.json').read_bytes())['records']:
 original=OLD/'adversarial-runs'/r['run_id']/'result.json';actual=replay_engineering(OLD/'adversarial-runs',r['run_id']);assert actual['status']=='IMMUTABLE_ORIGINAL_RESULT_VERIFIED' and actual['financial_approval']=='NONE';assert actual['result']==json.loads(original.read_bytes())
 records.append({'run_id':r['run_id'],'old_case':r['case'],'raw_result_sha256':H(original),'new_replay_status':actual['status'],'historical_result_status_preserved':actual['result']['status'],'financial_reapproval':False})
positive=next(r for r in records if r['old_case']=='original-snapshot-id');cfg=json.loads((OLD/'adversarial-runs'/positive['run_id']/'config.json').read_bytes());request=PortfolioRequest(bytes.fromhex(cfg['raw_request_hex']));new=construct_engineering(request,O/'old-draft-rejection-runs',FIX).read();assert new['status']=='REJECTED' and 'target' not in new
assert before=={str(p.relative_to(OLD)):H(p) for d in ('adversarial-runs','parent-binding-runs') for p in (OLD/d).rglob('*') if p.is_file()}
result={'fixed_sha':FIX,'records':records,'old_draft_new_execution':{'status':new['status'],'reasons':new['reasons'],'run_id':new['run_id']},'old_files_byte_unchanged':len(before),'result':'PASS','limitation':'Historical defective SUCCEEDED results are retained as historical bytes. Replay asserts integrity only, not new risk/financial approval.'}
(O/'OLD_REPLAY_VERIFICATION.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps(result))
