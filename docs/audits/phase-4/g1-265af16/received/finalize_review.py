import hashlib, json, re, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path
O=Path(__file__).resolve().parent; R=Path(sys.argv[1]); FIX='265af16353d85ce8c2d229a7517809d707498da8'; BASE='0a57dccb5618ba08cd3572d6d6b78fec963a3041'
def load(p): return json.loads((O/p).read_bytes())
def put(p,x): (O/p).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(b): return hashlib.sha256(b).hexdigest()
commands=[]
def git(*a,cwd=R):
    p=subprocess.run(['git',*a],cwd=cwd,capture_output=True,text=True,encoding='utf-8');commands.append(dict(argv=['git',*a],cwd=str(cwd),exit_code=p.returncode,stdout=p.stdout,stderr=p.stderr));assert p.returncode==0
    return p.stdout.strip()
pr=load('pr6-end.json');marker=re.search(r'AQRP_FIXED_REVIEW_SHA:\s*([0-9a-f]{40})',pr['body']).group(1)
assert marker==pr['head']['sha']==FIX and pr['base']['sha']==BASE and pr['state']=='open'
assert git('rev-parse','HEAD')==FIX and not git('status','--porcelain')
developer=Path('C:/Users/11638/AppData/Local/AQRP/checkouts/phase1-57461d5d-5de2-4c78-9b4e-5fad2b5ccb29')
devhead=git('rev-parse','HEAD',cwd=developer);devstatus=git('status','--porcelain',cwd=developer)
remote=git('ls-remote','https://github.com/wwooyy429/Alpha-Quant-Research-Platform-AQRP-.git','refs/heads/main','refs/tags/phase*-baseline*','refs/tags/v0.*')
refs={v:k for k,v in (line.split() for line in remote.splitlines())};assert refs==json.loads((R/'docs/audits/phase-4/PHASE3_RELEASE_RECEIPT.json').read_bytes())['remote_refs']
run=load('ci-run.json');jobs=load('ci-jobs.json')['jobs'];merge=load('ci-merge-commit.json');artifacts=load('ci-artifact-metadata.json')['artifacts']
assert run['conclusion']=='success' and run['head_sha']==FIX and run['event']=='pull_request' and run['run_attempt']==1
assert merge['sha']==pr['merge_commit_sha'] and merge['commit']['tree']['sha']==git('rev-parse',FIX+'^{tree}') and [x['sha'] for x in merge['parents']]==[BASE,FIX]
job_summary=[]
for j in jobs:
    assert j['conclusion']=='success'
    content=load(f"ci-job-{j['id']}.tool-response.json")['content'];assert merge['sha'] in content
    (O/f"ci-job-{j['id']}.log").write_bytes(content.encode('utf-8'))
    job_summary.append(dict(id=j['id'],name=j['name'],conclusion=j['conclusion'],decoded_log_sha256=sha(content.encode('utf-8'))))
for a in artifacts:
    assert not a['expired'] and a['workflow_run']['head_sha']==FIX
    assert any(a['digest'].removeprefix('sha256:') in load(f"ci-job-{j['id']}.tool-response.json")['content'] for j in jobs)
put('ci-review-summary.json',dict(actual_executor='GPT Work primary reviewer',run_id=run['id'],attempt=run['run_attempt'],workflow=run['name'],event=run['event'],head=FIX,base=BASE,actual_integration_sha=merge['sha'],tree=merge['commit']['tree']['sha'],fixed_tree_equal=True,jobs=job_summary,artifacts=[dict(id=a['id'],name=a['name'],bytes=a['size_in_bytes'],official_digest=a['digest']) for a in artifacts],actual_scope='Official API metadata, connector-decoded logs, integration commit parents/tree and upload digest text only',raw_CI_ZIPs_downloaded_or_independently_hashed=False,internal_JUnit_coverage_wheel_and_test_count_rechecked=False,P4_implementation_tests=False))
put('end-state.json',dict(actual_executor='GPT Work primary reviewer',utc=datetime.now(timezone.utc).isoformat(),fixed_sha=FIX,PR_head=pr['head']['sha'],PR_marker=marker,base=BASE,review_checkout_clean=True,developer_checkout_head=devhead,developer_checkout_porcelain=devstatus,remote_refs=refs,remote_release_refs_unchanged=True,commands=commands,mutations='Only external review files and independent detached clone; no tracked file edits, installed dependencies, account/ACL/services, remote writes, merge/tag/deploy/live trading or P5'))
put('finding-disposition.json',dict(actual_reviewer='GPT Work primary reviewer',fixed_sha=FIX,previous_sha='e40ddd0009cc30664c3a0fe0b74c4a497a541d77',verdict='PLAN PASS',scope='Restricted engineering design G1 only; no implementation or financial acceptance',new_blocking_findings=[],findings=[dict(id='P4-G1-001',original_severity='High',previous_status='OPEN',status='CLOSED_DESIGN',location='docs/audits/phase-4/INTERFACE_DRAFT.md:25,29,33-39,47,53; ROUNDING_REFERENCE.md:11-28; SYNTHETIC_PROFILE.json quantity_policy',basis='Exact ideal=current hold; separate changed target and nonzero delta lot gates; full-close-only flag with no other risk waiver; original X01 now rejected at delta gate. 14 quantity groups and reviewer edge cases independently verified.',runtime_implementation_verified=False),dict(id='P4-G1-002',original_severity='Medium',previous_status='OPEN',status='CLOSED_DESIGN',location='docs/audits/phase-4/TEST_AND_EVIDENCE_PLAN.md:5,20-24; ROUNDING_REFERENCE.md:30-51; INTERFACE_DRAFT.md:39,43,45',basis='Monotonicity limited to absolute target quantities/notionals and gross/sector gross at fixed positive prices/equity/mapping. X03/X04 independently frozen as pre-pass/post-reject, with all risk checks retained.',runtime_implementation_verified=False)],implementation_authorized=False,remaining='Real isolation, formal Test, financial approval and complete historical host remain NOT VERIFIED under accepted Phase3 scope; exact fixtures, real P4 service tests and new bundle receipt review required during authorized implementation/G2'))
print(json.dumps(dict(fixed_sha=FIX,head_and_marker_match=True,review_and_developer_checkout_clean=not devstatus,official_CI='SUCCESS: metadata/log/tree only',findings_closed_design=2,new_blocking_findings=0,verdict='PLAN PASS',implementation_authorized=False),indent=2))
