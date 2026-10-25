import json,hashlib,subprocess,shutil,re
from pathlib import Path
O=Path(__file__).parent;C=Path('E:/WORK/AQRP-audits/p7-3c34e3c/src');P=C/'docs/audits/phase-7'; dest=O/'received';dest.mkdir(exist_ok=True)
G='3c34e3ca75c9799307b8a98b34f045b40988bbca'
pr=json.loads((O/'PR10_FINAL.json').read_bytes())['structuredContent'];assert pr['head_sha']==G and pr['draft'] and not pr['merged']
assert re.findall(r'AQRP_FIXED_REVIEW_SHA:\s*([0-9a-f]{40})',pr['body'])==[G]
jobs=json.loads((O/'P7_CI_FINAL_JOBS.json').read_bytes())['structuredContent']['jobs'];assert len(jobs)==2 and all(x['conclusion']=='success' for x in jobs)
external=json.loads((C/'docs/audits/phase-6/g2-3017a09/EXTERNAL_ORIGINALS.json').read_bytes());orig=dest/'p6-original-seven';orig.mkdir(exist_ok=True);verified=[]
for r in external['external_files']:
 b=Path(r['direct_read_path']).read_bytes();assert len(b)==r['bytes'] and hashlib.sha256(b).hexdigest()==r['sha256']
 assert b==subprocess.check_output(['git','show',r['also_retained_in_git_history']],cwd=C)
 old=Path('C:/Users/11638/AppData/Local/AQRP/reviews/p6-g2-recheck-3017a09-independent-20261024')/r['original_zip_member'];assert b==old.read_bytes()
 (orig/r['path']).write_bytes(b);verified.append({'path':r['path'],'bytes':len(b),'sha256':r['sha256'],'matches_direct_H1Git_primary_original':True})
(O/'PRIMARY_ORIGINAL_SEVEN.json').write_text(json.dumps(verified,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
D7=Path('C:/Users/11638/AppData/Local/AQRP/reviews/p7-g1-plan-3c34e3c-20261024')
for n in ['Evidence.zip','EVIDENCE_MANIFEST.json']:
 t=dest/('Developer-P7-'+n);assert not t.exists();shutil.copyfile(D7/n,t)
 assert hashlib.file_digest(t.open('rb'),'sha256').hexdigest()==hashlib.file_digest((D7/n).open('rb'),'sha256').hexdigest()
root=Path('C:/Users/11638/AppData/Local/Packages/OpenAI.Codex_2p2nqsd0c76g0/LocalCache/Local/AQRP/runs/p6-release-p7-plan-20261024')
for n in ['P7-G1-GPT-WORK-HANDOFF.md','FINAL_DELIVERY_RECEIPT.json','Handoff-CI-Supplement.zip']:
 shutil.copyfile(root/n,dest/n)
inputs=json.loads((O/'PRIMARY_SCOPE.json').read_bytes())['archives']
(O/'EXTERNAL_EVIDENCE_INPUTS.json').write_text(json.dumps({'scope':'Original D7 byte copy included; original D6 1.16GB archive remains an explicit external prerequisite, independently hashed/read, not duplicated into new ZIP. Original prior3GB independent P6 archive preserved separately.','archives':inputs,'prior_primary_receipt':external['original_archive_receipt']},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'PR_fixed_sha':G,'draft_unmerged':True,'official_plan_CI_success':True,'seven_originals_verified':len(verified),'received_byte_copies':'complete'}))
