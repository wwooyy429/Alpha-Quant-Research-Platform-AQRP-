from pathlib import Path
from datetime import datetime,UTC
import hashlib,importlib.util,json,os,platform,re,subprocess,sys

O=Path(__file__).resolve().parent
R=Path(r'C:/Users/11638/AppData/Local/AQRP/checkouts/phase1-57461d5d-5de2-4c78-9b4e-5fad2b5ccb29')
D=R/'docs/audits/phase-6';A=D/'g1-e71f6f0';C='e71f6f090b102e4abfd70a5999e495f49546a1b5';BASE='59246f9fd391c1713b6bed65dd22280f4d248493'
def git(*a):return subprocess.check_output(['git',*a],cwd=R)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,o):p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
assert git('rev-parse','HEAD').decode().strip()==C
assert git('branch','--show-current').decode().strip()=='codex/phase-6-ui-plan'
frozen=json.loads((D/'FROZEN_INPUTS.json').read_bytes())
for e in frozen['files']:
 p=R/e['path'];assert p.stat().st_size==e['bytes'] and sha(p)==e['sha256'],e['path']
continuity=json.loads((A/'DESIGN_CONTINUITY.json').read_bytes())
for e in continuity['protected_reviewed_files']:
 p=R/e['path'];assert p.stat().st_size==e['bytes'] and sha(p)==e['sha256'],e['path']
received=json.loads((A/'RECEIVED_IDENTITY.json').read_bytes())
for e in received['copied_originals']:
 p=A/'received'/e['path'];assert p.stat().st_size==e['bytes'] and sha(p)==e['sha256'],e['path']
 assert p.read_bytes()==(Path(received['original_source'])/e['path']).read_bytes(),e['path']
status=json.loads((D/'STATUS.json').read_bytes())
assert not status['implementation_authorized'] and not status['human_phase_acceptance']
assert status['last_independent_reviewed_sha']==C and all(v=='CLOSED_DESIGN' for v in status['findings'].values())
conditions=json.loads((A/'CONDITIONS_AND_AUTHORIZATION.json').read_bytes())
assert len(conditions['conditions'])==3 and all(not x['user_accepted'] for x in conditions['conditions'])
assert conditions['separate_implementation_authorization']=='NOT_AUTHORIZED'
for p in D.rglob('*.json'):json.loads(p.read_bytes())
links=[]
for p in [A/'DEVELOPER_RESPONSE.md',D/'REVIEW_PACKAGE.md']:
 for target in re.findall(r'\]\(([^)]+)\)',p.read_text(encoding='utf-8')):
  if target.startswith(('https://','http://','#')):continue
  assert (p.parent/target.split('#')[0]).is_file(),(p,target)
  links.append({'source':p.relative_to(D).as_posix(),'target':target})
V=A/'developer-validation'/('receipt-'+datetime.now(UTC).strftime('%Y%m%dT%H%M%S'));V.mkdir(parents=True)
args=[r'E:/WORK/AQRP-runs/p5-release-36c2691-20261023/aqrp-3e03b1bf-328f-40d0-be58-99efb33d4d51/gitleaks.exe','dir',str(R),'--config',str(R/'.gitleaks.toml'),'--redact=100','--no-banner','--report-format','json','--report-path',str(V/'scan-findings.json')]
start=datetime.now(UTC).isoformat();p=subprocess.run(args,cwd=R,capture_output=True)
(V/'secret-scan.stdout.log').write_bytes(p.stdout);(V/'secret-scan.stderr.log').write_bytes(p.stderr)
save(V/'secret-scan.command.json',{'argv':args,'cwd':str(R),'executor':'Codex developer archive-only secret scan','started_utc':start,'finished_utc':datetime.now(UTC).isoformat(),'exit_code':p.returncode,'parent_reviewed_sha':C})
assert p.returncode==0,p.stderr.decode(errors='replace')[-2500:]
save(V/'ARCHIVAL_STATIC_VERIFICATION.json',{'reviewed_sha':C,'checked_utc':datetime.now(UTC).isoformat(),'executor':'Codex developer read-only document identity/secret scan; not independent audit or test rerun','environment':{'executable':sys.executable,'version':sys.version,'platform':platform.platform()},'frozen_baseline_files':len(frozen['files']),'protected_reviewed_files':len(continuity['protected_reviewed_files']),'received_originals':len(received['copied_originals']),'all_sizes_hashes_match':True,'source_tests_tools_CI_build_core_lock_unchanged':True,'original_answers_models_dependencies_unchanged':True,'document_links_checked':links,'P6_product_tests_UI_install_or_start':0,'independent_tests_rerun_by_developer':False,'new_SDK_rerun':False,'result':'PASS_ARCHIVAL_CHECKS_ONLY'})
allowed_existing=frozen['allowed_existing_status_documents']+continuity['allowed_current_record_updates']
changed=set(filter(None,git('diff','--name-only','-z',C).decode().split('\0')))
changed.update(filter(None,git('ls-files','--others','--exclude-standard','-z').decode().split('\0')))
assert all(n in allowed_existing or n.startswith('docs/audits/phase-6/g1-e71f6f0/') for n in changed),sorted(changed)
assert not git('diff',C,'--','src','tests','tools','.github','pyproject.toml','requirements.lock','.gitleaks.toml','docs/requirements.csv','docs/audits/phase-5')
subprocess.run(['git','add','--',*allowed_existing,'docs/audits/phase-6/g1-e71f6f0/'],cwd=R,check=True)
prefix='docs/audits/phase-6/'
tracked=[n for n in git('ls-files','-z','--',prefix).decode().split('\0') if n and n!=prefix+'FILE_MANIFEST.json']
assert not any('/__pycache__/' in n for n in tracked)
save(D/'FILE_MANIFEST.json',{'self_excluded':True,'scope':'Exact tracked Phase6 G1 documents, historical original reviews and current archive/status only; no P6 implementation','files':[{'path':n[len(prefix):],'bytes':(R/n).stat().st_size,'sha256':sha(R/n)} for n in sorted(tracked)]})
subprocess.run(['git','add','--',prefix+'FILE_MANIFEST.json'],cwd=R,check=True)
p=subprocess.run(['git','diff','--cached','--check'],cwd=R,capture_output=True)
(O/'STAGED_CHECK.stdout.log').write_bytes(p.stdout);(O/'STAGED_CHECK.stderr.log').write_bytes(p.stderr)
assert p.returncode==0,p.stdout.decode(errors='replace')[:3000]
spec=importlib.util.spec_from_file_location('github_ops',O.parent/'p4-release-20261022/github_ops.py');ops=importlib.util.module_from_spec(spec);spec.loader.exec_module(ops)
before=json.loads((O/'PR9_BEFORE.json').read_bytes());pr=ops.api(f'repos/{ops.repo}/pulls/9')
assert pr['head']['sha']==C and pr['body']==before['body'] and pr['draft'] and not pr['merged']
refs=git('ls-remote','--heads','--tags','origin');(O/'REMOTE_REFS_PREPUBLISH.txt').write_bytes(refs)
current={x.split()[1]:x.split()[0] for x in refs.decode().splitlines()};original={x.split()[1]:x.split()[0] for x in (O/'REMOTE_REFS_BEFORE.txt').read_text().splitlines()}
assert current['refs/heads/main']==current['refs/tags/phase5-baseline^{}']==current['refs/tags/v0.5.0^{}']==BASE
assert current['refs/heads/codex/phase-6-ui-plan']==C
for key,value in original.items():
 if key.startswith('refs/tags/'):assert current[key]==value,key
names=[x for x in git('diff','--cached','--name-only','-z').decode().split('\0') if x]
assert names and all(n in allowed_existing or n.startswith('docs/audits/phase-6/g1-e71f6f0/') for n in names)
assert not git('diff','--name-only')
p=subprocess.run(['git','-c','user.name=Codex','-c','user.email=codex@localhost','commit','-m','docs: archive Phase6 G1 conditional pass and pending human choices'],cwd=R,capture_output=True)
(O/'commit.stdout.log').write_bytes(p.stdout);(O/'commit.stderr.log').write_bytes(p.stderr);assert p.returncode==0,p.stderr.decode(errors='replace')
H=git('rev-parse','HEAD').decode().strip();assert len(H)==40 and git('rev-parse','HEAD^').decode().strip()==C
save(O/'ARCHIVAL_COMMIT.json',{'reviewed_sha':C,'archival_head_sha':H,'parent':C,'changed_files':names,'protected_reviewed_design_files_unchanged':len(continuity['protected_reviewed_files']),'source_change':False,'G1':'PLAN PASS WITH CONDITIONS applies to reviewed SHA only','human_choices':'ALL_THREE_PENDING','P6_implementation_authorized':False,'created_utc':datetime.now(UTC).isoformat()})
p=subprocess.run(['git','push','origin','codex/phase-6-ui-plan'],cwd=R,capture_output=True)
(O/'push.stdout.log').write_bytes(p.stdout);(O/'push.stderr.log').write_bytes(p.stderr);assert p.returncode==0,p.stderr.decode(errors='replace')
pr=ops.api(f'repos/{ops.repo}/pulls/9');assert pr['head']['sha']==H and pr['body']==before['body'] and not pr['merged']
url=f'https://github.com/{ops.repo}'
body=f'''AQRP_FIXED_REVIEW_SHA: {C}
AQRP_ARCHIVAL_HEAD_SHA: {H}

## Current Phase6 G1 decision
GPT Work independently reviewed **only `{C}`**: **PLAN PASS WITH CONDITIONS**. WORK-P6-G1-001 High, 002/003 Medium are **CLOSED_DESIGN**, no new blocking technical findings. This is design review, not P6 implementation/G2, human phase acceptance or release permission.

The actual PR head above is a separate **documentation-only report archival descendant**. It does not automatically inherit independent review of a new SHA. Audited contracts, answers/models, dependencies and all prior review material are byte-identical; see DESIGN_CONTINUITY.json. Keep the review lock on the audited SHA, never substitute drifting HEAD.

## Human conditions still pending — no implementation authorization
1. **C-P6-001:** all required P4 stages must actually SUCCEEDED for Task success; legitimate risk rejection retains original P4/P5 results, Task FAILED/REQUIRED_STAGE_REJECTED; financial algorithms/orders unchanged.
2. **C-P6-002:** new engineering pipeline N>=1 decisions; explicit NO_REQUIRED_DECISIONS for an empty interval; existing P5 zero-decision SDK/API unchanged.
3. **C-P6-003:** new adapter accepts ordinary finite ASCII decimal strings <=4096 digits/4098 raw characters, preserves raw/hash, explicitly rejects range/syntax/type errors; HALF_EVEN is display-only and legacy financial APIs/domain checks remain unchanged.
4. Separate explicit user implementation authorization for the unchanged **8 requirements (5 MVP / 3 Competition Ready)**, after choices accepted. The user delivered the report but has not accepted these choices or authorized implementation. **NOT AUTHORIZED / NOT STARTED; no UI installation/start.**

## Archived independent evidence and current records
Entry: [REVIEW_PACKAGE.md]({url}/blob/{H}/docs/audits/phase-6/REVIEW_PACKAGE.md).
Original [report]({url}/blob/{H}/docs/audits/phase-6/g1-e71f6f0/received/REPORT.md), FINDINGS, RECEIPT and raw logs/scripts including first failed auxiliary attempts are preserved byte-for-byte under docs/audits/phase-6/g1-e71f6f0/received/.
[Developer response]({url}/blob/{H}/docs/audits/phase-6/g1-e71f6f0/DEVELOPER_RESPONSE.md), FINDING_DISPOSITION, CONDITIONS_AND_AUTHORIZATION, IMPLEMENTATION_GATE, RECEIVED_IDENTITY and DESIGN_CONTINUITY distinguish independent closure, pending user choices and archived versus reviewed SHA.

Independent ZIP675865677 bytes, SHA256 `eae0cd90c75e79c64ca1d06f0e7fc0ae367fbd91a1678af0632c933f0a72d31e`: developer verified CRC, exact142 unique members and all141 declared file sizes/hashes.103 top-level original files tracked; full large ZIP retained externally at the path in RECEIVED_IDENTITY. Old f7 BLOCKED and original numeric/auxiliary failure logs are retained as history, not rewritten into PASS.

GPT Work independently verified original32 + supplemental95 answers;852 numeric/refusal inputs ×6 contexts=5112 observations,3456 completion combinations and25 ownership extensions. Counts overlap and cover **design/finite models/reference helpers only**, not actual TaskService/SQLite/concurrency/authority/UI/OS tests. Developer did not rerun these tests or a full SDK during report archival.

Official API for prior run39946297503 reports both OS jobs success; the reviewer **did not download those two new raw CI ZIPs**, so original bytes/member/environment/test counts remain NOT VERIFIED in that audit. This is inherited P5 regression metadata, never P6 product evidence. Historical P5 SDK1158 and old20+4/91 keep their original execution scope. Future G2 must prove actual services/disk/SQLite/claim/cancel/recovery, both factors/three entry points/six real browser pages, full SDK and dual-OS original artifacts as planned.

## Scope and restrictions
All4738 frozen P5 files, audited P6 design/answers/reference/dependency assets, core source/tests/tools/CI/build/core lock and P5 evidence remain unchanged. main / phase5-baseline / v0.5.0 stay `{BASE}`; all existing tag objects and targets retained. Only current governance/status/index/manifest and new original-report archive changed.

WI-R2-001/002 and overall real Windows isolation remain **DEFERRED / NOT VERIFIED** until separately authorized final-integrated-SHA real validation. Formal Test not run, financial approval NONE; full historical host limited to accepted package/lock/oldRef/result replay. No real account/ACL/service/scheduler changes, deployment/live trading/formal Test/financial approval; no P6 implementation, merge, tags, release or P7. G1 conditions do not grant any of these permissions.
'''
(O/'PR_BODY.md').write_text(body,encoding='utf-8',newline='\n')
pr=ops.api(f'repos/{ops.repo}/pulls/9',method='PATCH',data={'title':'docs: Phase6 G1 conditional pass and pending implementation choices','body':body})
assert pr['head']['sha']==H and pr['body']==body and pr['draft'] and not pr['merged']
save(O/'PR9_UPDATED.json',pr)
print(json.dumps({'PR':9,'reviewed_fixed_sha':C,'archival_head_sha':H,'G1':'PLAN PASS WITH CONDITIONS','findings':'THREE_CLOSED_DESIGN','user_choices_pending':3,'implementation':'NOT_AUTHORIZED_NOT_STARTED','static_checks':'PASS_ARCHIVE_ONLY'}))
