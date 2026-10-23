"""Read-only final identity, CI metadata and report-location capture."""
from pathlib import Path
import json, subprocess, urllib.request, hashlib
O=Path(__file__).parent;C=O.parent/'p5-g1-review-5262032';P=C/'docs/audits/phase-5'
FIX='5262032bee4f631f68763e57510e1878945f6b8c';BASE='32ea5d6b75c84c07017d87377eeabd2f78207c5c'
def git(*a):return subprocess.check_output(['git','-C',str(C),*a])
def save(n,v):(O/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
pr=json.loads((O/'PR8_FINAL.json').read_bytes())
assert pr['head_sha']==FIX and ('AQRP_FIXED_REVIEW_SHA: '+FIX) in pr['body'] and not pr['merged']
assert git('rev-parse','HEAD').decode().strip()==FIX and git('status','--porcelain')==b''
subprocess.run(['git','-C',str(C),'diff','--check',BASE,FIX],check=True)
url='https://api.github.com/repos/wwooyy429/Alpha-Quant-Research-Platform-AQRP-/actions/runs/39817052064'
with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'AQRP-independent-G1-audit','Accept':'application/vnd.github+json'}),timeout=40) as r:
 raw=r.read(); (O/'CI_RUN_PUBLIC_RAW.json').write_bytes(raw)
run=json.loads(raw);assert run['status']=='completed' and run['conclusion']=='success'
assert run['head_sha']==FIX
jobsurl=run['jobs_url']+'?per_page=100'
with urllib.request.urlopen(urllib.request.Request(jobsurl,headers={'User-Agent':'AQRP-independent-G1-audit','Accept':'application/vnd.github+json'}),timeout=40) as r:
 raw=r.read();(O/'CI_JOBS_PUBLIC_RAW.json').write_bytes(raw)
jobs=json.loads(raw)['jobs'];assert jobs and all(j['conclusion']=='success' for j in jobs)
locations={}
for name in ['EVENT_TRANSACTION_ADDENDUM.md','CASH_BUCKETS_AND_PROJECTION.md','EXECUTION_PRICE_AND_FEES.md','FIFO_ATTRIBUTION.md','CONTRACT_CHANGE_IMPACT.md','PROFILE_AND_DECISIONS.md','TEST_AND_EVIDENCE_PLAN.md','REQUIREMENTS_TRACEABILITY.md','INTERFACE_DRAFT.md','MATH_CONTRACT.md']:
 b=(P/name).read_bytes();lines=b.decode('utf-8').splitlines();locations[name]={'sha256':hashlib.sha256(b).hexdigest(),'lines':len(lines),'numbered_text':'\n'.join(f'{i}: {s}' for i,s in enumerate(lines,1))}
save('REVIEWED_LOCATIONS.json',locations)
save('FINAL_IDENTITY_CHECK.json',{'fixed_sha':FIX,'clean_detached':True,'PR_lock_and_head_stable':True,'PR_open_unmerged':True,'diff_check':'PASS','CI_run':run['id'],'CI_head_sha':run['head_sha'],'CI_status':run['status'],'CI_conclusion':run['conclusion'],'jobs':[{'id':j['id'],'name':j['name'],'conclusion':j['conclusion']} for j in jobs],'CI_scope':'Existing Phase4 regression only; current-run official artifact ZIP/JUnit/coverage NOT independently downloaded/verified this G1 round; no P5 implementation tests','result':'PASS'})
print(json.dumps({'fixed_sha':FIX,'clean':True,'CI_run':run['id'],'CI_status':run['status'],'CI_conclusion':run['conclusion'],'jobs':[j['name'] for j in jobs],'result':'PASS'}))
