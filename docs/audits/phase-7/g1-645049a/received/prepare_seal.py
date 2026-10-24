import json,shutil,hashlib,re
from pathlib import Path
O=Path(__file__).parent;D=Path('C:/Users/11638/AppData/Local/AQRP/reviews/p7-g1-revision-645049a-20261024');R=O/'received';R.mkdir(exist_ok=False)
for n in ['Evidence.zip','EVIDENCE_MANIFEST.json','RECEIPT.json']:
 t=R/('Developer-'+n);shutil.copyfile(D/n,t);assert hashlib.file_digest(t.open('rb'),'sha256').hexdigest()==hashlib.file_digest((D/n).open('rb'),'sha256').hexdigest()
h=Path('C:/Users/11638/AppData/Local/AQRP/runs/p7-g1-revision-3c34e3c-20261024/P7-G1-GPT-WORK-HANDOFF.md');shutil.copyfile(h,R/h.name)
p=json.loads((O/'PR10_FINAL.json').read_bytes())['structuredContent'];assert p['head_sha']=='645049ae9b08710ed93189b80547d14c87d80584' and p['draft'] and not p['merged'];assert re.findall(r'AQRP_FIXED_REVIEW_SHA:\s*([0-9a-f]{40})',p['body'])==[p['head_sha']]
j=json.loads((O/'CI_FINAL_JOBS.json').read_bytes())['structuredContent']['jobs'];assert len(j)==2 and all(x['status']=='completed' and x['conclusion']=='success' for x in j)
print(json.dumps({'fixed_head':p['head_sha'],'draft_unmerged':True,'both_CI_jobs_success':True,'developer_original_copies_verified':4}))
