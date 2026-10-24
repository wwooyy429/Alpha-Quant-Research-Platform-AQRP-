"""Seal complete raw audit evidence, self excluded; no remote writes."""
from pathlib import Path
import os,stat,json,hashlib,zipfile,datetime,subprocess
O=Path(__file__).parent;C=Path('E:/WORK/AQRP-audits/p6-3017a09/src')
FIX='3017a097b49ecdae68228ca9a417fcd03c313200'
H=lambda b:hashlib.sha256(b).hexdigest()
def fh(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def get(n):return json.loads((O/n).read_text(encoding='utf-8-sig'))
def save(n,v):(O/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
assert subprocess.check_output(['git','-C',str(C),'rev-parse','HEAD'],text=True).strip()==FIX
assert subprocess.check_output(['git','-C',str(C),'status','--porcelain'])==b''
pr=get('PR9_FINAL.json');assert pr['head_sha']==FIX and 'AQRP_FIXED_REVIEW_SHA: '+FIX in pr['body'] and not pr['merged']
assert get('SDK_COMPLETION.json')['exit_code']==0 and get('BROWSER_STOP.json')['remaining']==0
assert get('FINDINGS.json')['verdict']=='G2 PASS — restricted engineering scope'
assert not get('FINDINGS.json')['new_open_findings']
refs=subprocess.check_output(['git','-C',str(C),'ls-remote','origin','refs/heads/main','refs/tags/*'],text=True)
parse=lambda s:dict(l.split()[::-1] for l in s.splitlines())
assert parse(refs)==parse((O/'REMOTE_REFS_START.txt').read_text())
(O/'REMOTE_REFS_AT_SEAL.txt').write_text(refs,encoding='utf-8')
save('AUDIT_SCRIPTS_FINAL_HASHES.json',{p.relative_to(O).as_posix():fh(p) for p in O.glob('*') if p.suffix in ('.py','.ps1')})
save('EXECUTION_DISPOSITIONS.json',dict(actual_executor='GPT Work supplemental reviewer; no delegation or Gemini execution claimed',product_candidate_edited=False,helper_failures=['Archive suffix matching selected nested browser manifest; corrected to exact root. First failure retained.','Git source ZIP includes580 directory entries in addition to5108 files; file-only set and all sizes/hashes verified; second original failure retained.','Campaign probe initially assumed a composite absent from its actual declared config and stopped before concurrency submissions. Independent literal expected units corrected4 for two factors/two horizons; fresh roots reran all controls; first source/log/workspaces retained.','One PowerShell quoting attempt to edit the report generator failed at shell parse; structured apply_patch then used. No candidate edit occurred.','Initial browser navigation preceded server readiness and failed connection. A read-only attempt to bind that error dataURL was denied; new tab after loopback readiness succeeded, no barrier bypass.'],warnings='Two known same-process runpy entry test RuntimeWarnings retained; no zero-warning claim',CI='Official original ZIP bytes matched fresh API size/digest/head; not reviewer remote runner execution or a new download claim',browser='Reviewer actual2 pool submissions,17 observations4JPEG; developer57main observations27main JPEG and controls separately labelled. Own loopback stopped.',developer_stress='120 process dirty/editable preflight not final fixed-SHA SDK; reviewer40 processes use current fixed installed wheel',old_native_cause='NOT VERIFIED; historical failures retained; strict six-point engineering termination/recovery verified',formal_Test=False,financial_approval='NONE',Windows_R2='DEFERRED / NOT VERIFIED'))
excluded={'EVIDENCE.zip','EVIDENCE_MANIFEST.json','RECEIPT.json','seal.command.json','seal.stdout.log','seal.stderr.log'}
rows=[]
def denied(error):raise error
for parent,dirs,files in os.walk(O,onerror=denied,followlinks=False):
 dirs[:]=[d for d in dirs if d!='__pycache__']
 for name in dirs+files:
  p=Path(parent)/name;assert not p.is_symlink() and not p.is_junction(),str(p)
 for name in files:
  p=Path(parent)/name
  if p.parent==O and name in excluded:continue
  rows.append(dict(path=p.relative_to(O).as_posix(),bytes=p.stat().st_size,sha256=fh(p)))
rows.sort(key=lambda x:x['path'])
manifest=dict(fixed_sha=FIX,verdict='G2 PASS — restricted engineering scope',executor='GPT Work supplemental reviewer',files=rows,self_excluded=sorted(excluded|{'__pycache__'}),scope='Own exact fixed installed SDK, fresh repair challenges, actual CUA stock-pool submissions, official original/developer/previous independent packages preserved with distinct provenance; no formal Test or actual OS isolation.')
save('EVIDENCE_MANIFEST.json',manifest)
out=O/'EVIDENCE.zip';assert not out.exists()
with zipfile.ZipFile(out,'x',zipfile.ZIP_DEFLATED,compresslevel=6,allowZip64=True) as z:
 for r in rows:z.write(O/r['path'],r['path'],compress_type=zipfile.ZIP_STORED if r['path'].endswith('.zip') else zipfile.ZIP_DEFLATED)
 z.write(O/'EVIDENCE_MANIFEST.json','EVIDENCE_MANIFEST.json')
with zipfile.ZipFile(out) as z:
 assert z.testzip() is None
 assert len(z.namelist())==len(set(z.namelist()))==len(rows)+1
 assert set(z.namelist())=={r['path'] for r in rows}|{'EVIDENCE_MANIFEST.json'}
 assert z.read('EVIDENCE_MANIFEST.json')==(O/'EVIDENCE_MANIFEST.json').read_bytes()
 for r in rows:
  assert z.getinfo(r['path']).file_size==r['bytes']
  with z.open(r['path']) as f:assert hashlib.file_digest(f,'sha256').hexdigest()==r['sha256'],r['path']
receipt=dict(fixed_sha=FIX,verdict='G2 PASS — restricted engineering scope',findings={x['id']:x['status'] for x in get('FINDINGS.json')['findings']},archive='EVIDENCE.zip',bytes=out.stat().st_size,sha256=fh(out),manifest_sha256=fh(O/'EVIDENCE_MANIFEST.json'),manifest_files=len(rows),zip_members=len(rows)+1,CRC_exact_members_all_sizes_hashes_verified=True,executor='GPT Work supplemental reviewer',not_a_digital_signature=True,independent_SDK_tests=1567,official_CI_tests_per_OS=1567,original_extra_regressions='20 + 4',independent_math_checks=91,installed_numeric_context_observations=5112,reviewer_additional_real_processes=40,reviewer_browser_AX=17,reviewer_browser_screenshots=4,developer_browser_main_AX=57,developer_browser_main_screenshots=27,user_phase6_acceptance=False,formal_Test=False,financial_approval='NONE',Windows_R2='DEFERRED / NOT VERIFIED',full_historical_host='NOT VERIFIED beyond accepted package/lock/oldRef/result projection',merge_tag_deploy_live_P7=False,created_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
save('RECEIPT.json',receipt);print(json.dumps(receipt,ensure_ascii=False))
