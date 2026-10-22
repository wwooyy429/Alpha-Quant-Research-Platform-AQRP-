"""Bind external report to fixed source and public CI metadata; do not mutate checkout."""
import hashlib, json, re, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path
O=Path(__file__).resolve().parent; R=Path(sys.argv[1]); FIX='e40ddd0009cc30664c3a0fe0b74c4a497a541d77'; BASE='0a57dccb5618ba08cd3572d6d6b78fec963a3041'
def load(p): return json.loads((O/p).read_bytes())
def put(p,x): (O/p).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
commands=[]
def git(*a,cwd=R):
    p=subprocess.run(['git',*a],cwd=cwd,capture_output=True,text=True,encoding='utf-8')
    commands.append(dict(argv=['git',*a],cwd=str(cwd),exit_code=p.returncode,stdout=p.stdout,stderr=p.stderr))
    assert p.returncode==0,commands[-1]
    return p.stdout.strip()
remote=git('ls-remote','https://github.com/wwooyy429/Alpha-Quant-Research-Platform-AQRP-.git','refs/heads/main','refs/tags/phase*-baseline*','refs/tags/v0.*')
actual={v:k for k,v in (line.split() for line in remote.splitlines())}
receipt=json.loads((R/'docs/audits/phase-4/PHASE3_RELEASE_RECEIPT.json').read_bytes())
assert actual==receipt['remote_refs'],(actual,receipt['remote_refs'])
pr=load('pr6-end.json'); marker=re.search(r'AQRP_FIXED_REVIEW_SHA:\s*`?([0-9a-f]{40})',pr['body']).group(1)
assert marker==pr['head']['sha']==FIX and pr['base']['sha']==BASE and pr['state']=='open'
assert git('rev-parse','HEAD')==FIX and not git('status','--porcelain')
original=Path('C:/Users/11638/AppData/Local/AQRP/checkouts/phase1-57461d5d-5de2-4c78-9b4e-5fad2b5ccb29')
original_status=git('status','--porcelain',cwd=original); original_head=git('rev-parse','HEAD',cwd=original)
run=load('ci-run.json'); jobs=load('ci-jobs.json')['jobs']; artifacts=load('ci-artifact-metadata.json')['artifacts']; merge=load('ci-merge-commit.json')
assert run['head_sha']==FIX and run['event']=='pull_request' and run['conclusion']=='success' and run['run_attempt']==1
assert merge['commit']['tree']['sha']==git('rev-parse',FIX+'^{tree}')
assert [p['sha'] for p in merge['parents']]==[BASE,FIX]
job_summary=[]
for j in jobs:
    assert j['conclusion']=='success'
    data=load(f"ci-job-{j['id']}.tool-response.json")['content']
    (O/f"ci-job-{j['id']}.log").write_bytes(data.encode('utf-8'))
    assert merge['sha'] in data
    job_summary.append(dict(id=j['id'],name=j['name'],conclusion=j['conclusion'],decoded_log_sha256=hashlib.sha256(data.encode('utf-8')).hexdigest(),evidence='Connector-decoded job log, preserved UTF-8 incl BOM/newlines; not downloaded raw artifact ZIP'))
for a in artifacts:
    assert not a['expired'] and a['workflow_run']['head_sha']==FIX
    assert any(a['digest'].removeprefix('sha256:') in load(f"ci-job-{j['id']}.tool-response.json")['content'] for j in jobs)
put('ci-review-summary.json',dict(actual_executor='GPT Work primary reviewer',run_id=run['id'],attempt=run['run_attempt'],event=run['event'],workflow=run['name'],head=FIX,base=BASE,actual_integration_sha=merge['sha'],tree=merge['commit']['tree']['sha'],fixed_tree_equal=True,jobs=job_summary,artifacts=[dict(id=a['id'],name=a['name'],bytes=a['size_in_bytes'],official_digest=a['digest']) for a in artifacts],verification_scope='API metadata, checkout logs, digest text agreement, actual merge parent/tree binding only',raw_zip_downloaded=False,raw_zip_independently_hashed=False,internal_manifest_JUnit_coverage_wheel_verified_this_round=False,test_count_independently_recounted_this_round=False,P4_implementation_tests=False))
put('end-state.json',dict(actual_executor='GPT Work primary reviewer',utc=datetime.now(timezone.utc).isoformat(),fixed_sha=FIX,marker=marker,base=BASE,pr_open=True,checkout_clean=True,developer_checkout_head=original_head,developer_checkout_porcelain=original_status,remote_refs=actual,all_release_receipt_refs_match=True,mutations='External review files and independent detached checkout only. No tracked source/docs changes, remote writes, merge/tag/deploy/accounts/ACL/services or P5.',commands=commands))
put('findings.json',[
 dict(id='P4-G1-001',severity='High',status='OPEN',blocks_G1=True,kind='Design contract gap; no P4 runtime implementation exists',requirements=['PORT-001','PORT-002','PORT-003','RISK-003','RISK-004'],location='docs/audits/phase-4/INTERFACE_DRAFT.md:25,33,39; SYNTHETIC_PROFILE.json:14; docs/BACKTEST_CONTRACT.md:49',title='Target lot alignment does not validate rebalance delta for existing odd-lot positions',evidence=['independent-math-results.json:X01-target-lot-does-not-protect-delta','independent-math-results.json:X02-no-trade-odd-holding-conflict'],disposition='Freeze whether lot applies to target and/or delta. With the declared trading-lot/full-close-only policy, reject non-full-close nonaligned delta explicitly before success; define delta=0 odd-lot hold separately. Keep q_target=q_current+delta. An alternative trade-lattice quantizer needs explicit design approval and all post-round checks; no silent partial-odd-lot permission or P5-only deferral.'),
 dict(id='P4-G1-002',severity='Medium',status='OPEN',blocks_G1=True,kind='Incorrect proposed test property; full pre/post risk recheck already required in interface',requirements=['RISK-001','RISK-002','QA-001','QA-002','QA-004'],location='docs/audits/phase-4/TEST_AND_EVIDENCE_PLAN.md:5; INTERFACE_DRAFT.md:25,29,31',title='Toward-zero target rounding may increase absolute Beta, industry net exposure and turnover',evidence=['independent-math-results.json:X03-rounding-increases-absolute-Beta-sector-net','independent-math-results.json:X04-rounding-increases-turnover'],disposition='Narrow monotonicity to each absolute target quantity, absolute target notional at fixed positive prices/equity, gross and sector gross. Preserve pre/post checks for signed net and interval limits, Beta, turnover, cash and permissions. Freeze new independent expected counterexamples and applicable regression properties; do not weaken existing risk checks.' )])
print(json.dumps(dict(fixed_sha=FIX,pr_open=True,ci='SUCCESS, metadata/log/tree verified only',all_old_and_new_tag_objects_and_targets_match=True,review_checkout_clean=True,developer_checkout_clean=not original_status,findings={'High':1,'Medium':1},verdict='PLAN BLOCKED'),indent=2))
