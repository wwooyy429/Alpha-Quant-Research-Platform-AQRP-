from pathlib import Path
import json,hashlib,zipfile,datetime,subprocess,shutil
O=Path(__file__).parent;C=Path('E:/WORK/AQRP-audits/p6-f7a1a68/src');P=C/'docs/audits/phase-6';D=O.parent/'p6-g1-f7a1a68-20261023';FIX='f7a1a68c5f747090f8c8a0e934f2fea859aec998'
def H(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def J(p):return json.loads(p.read_bytes())
assert J(O/'SCOPE_RELEASE_VERIFICATION.json')['result']==J(O/'DEPENDENCY_VERIFICATION.json')['result']=='PASS'
assert J(O/'FINDINGS.json')['verdict']=='PLAN BLOCKED / REQUEST CHANGES'
for n in ['PR9_START.json','PR9_FINAL.json']:
 pr=J(O/n);assert pr['head_sha']==FIX and pr['body'].startswith('AQRP_FIXED_REVIEW_SHA: '+FIX) and not pr['merged']
assert subprocess.check_output(['git','-C',str(C),'rev-parse','HEAD']).decode().strip()==FIX and subprocess.check_output(['git','-C',str(C),'status','--porcelain'])==b''
refs=subprocess.check_output(['git','-C',str(C),'ls-remote','origin','refs/heads/main','refs/tags/*']).decode();assert refs==(O/'REMOTE_REFS_START.txt').read_text(encoding='utf-8');(O/'REMOTE_REFS_FINAL.txt').write_text(refs,encoding='utf-8')
(O/'FINAL_IDENTITY.json').write_text(json.dumps(dict(fixed_sha=FIX,baseline='59246f9fd391c1713b6bed65dd22280f4d248493',PR_head_description_lock_start_end=True,detached_clean=True,main_old_tags_unchanged=True,verdict='PLAN BLOCKED / REQUEST CHANGES',P6_business_implementation=False,P6_UI_install_runtime_browser_tests=0),indent=2)+'\n',encoding='utf-8')
(O/'EXECUTION_DISPOSITIONS.json').write_text(json.dumps(dict(reviewer_execution=[dict(label='scope-release',exit_code=4294967295,scope='Read-only auditor helper, not AQRP product',reason='Per-file git show repeatedly spawning processes was too slow; verified exact child command identity and stopped only that helper',original_script='verify_scope_release.first-attempt.py',replacement='scope-release-batch completed PASS with one ls-tree and all4738 file SHA256/Git blob identity checks',expected_answers_or_guards_weakened=False)],read_only_lookup_errors=['initial rg no matching workspace files returned1','one read-only attempt used nonexistent docs/audits/phase-6/resolve_candidates.py; actual developer helper is external'],design_findings='1High/2Medium OPEN; design-model traces are not product execution',CI_plan_run_raw_zip='NOT VERIFIED; metadata only',UI_install_AppTest_browser='NOT EXECUTED',formal_Test=False,financial_approval='NONE',Windows_R2='DEFERRED / NOT VERIFIED',merge_tag_deploy_live_P7=False),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
received=O/'developer-received';received.mkdir()
for n in ['Evidence.zip','EVIDENCE_MANIFEST.json','RECEIPT.json','GPT-Work-Phase6-G1-Instructions.txt']:shutil.copyfile(D/n,received/n)
prereq=O/'prerequisite-received';prereq.mkdir();release=J(P/'PHASE5_SEALED_EVIDENCE.json');shutil.copyfile(release['archive'],prereq/'P5-release-Evidence.zip')
sdk=J(P/'PHASE5_RELEASE_RECEIPT.json')['SDK_archive'];sdk_inside=[]
with zipfile.ZipFile(release['archive']) as z:
 for n in z.namelist():
  if n.endswith('.zip') and z.getinfo(n).file_size==sdk['bytes']:
   with z.open(n) as f:
    if hashlib.file_digest(f,'sha256').hexdigest()==sdk['sha256']:sdk_inside.append(n)
if not sdk_inside:shutil.copyfile(sdk['archive'],prereq/'P5-postmerge-SDK.zip')
(O/'PREREQUISITE_BINDINGS.json').write_text(json.dumps(dict(P5_release_bytes=release['bytes'],P5_release_sha256=release['sha256'],P5_postmerge_SDK_bytes=sdk['bytes'],P5_postmerge_SDK_sha256=sdk['sha256'],SDK_inside_received_P5_release=sdk_inside,not_new_reviewer_execution=True),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
source=O/'reviewed-source'
for p in P.glob('*'):
 if p.suffix in ['.md','.py','.json','.in','.lock']:
  q=source/'docs/audits/phase-6'/p.name;q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,q)
for n in ['src/aqrp/backtest/engine.py','src/aqrp/backtest/provider.py','src/aqrp/services/backtest.py','src/aqrp/experiments/ledger.py','docs/requirements.csv','docs/audits/phase-5/BASELINE.md']:
 q=source/n;q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(C/n,q)
(O/'AUDIT_SCRIPTS_FINAL_HASHES.json').write_text(json.dumps([dict(path=p.name,sha256=H(p)) for p in sorted(O.glob('*.py'))],indent=2)+'\n',encoding='utf-8')
excluded={'EVIDENCE.zip','EVIDENCE_MANIFEST.json','RECEIPT.json','seal.command.json','seal.stdout.log','seal.stderr.log'}
files=[p for p in sorted(O.rglob('*')) if p.is_file() and p.relative_to(O).as_posix() not in excluded and '__pycache__' not in p.parts]
entries=[dict(path=p.relative_to(O).as_posix(),bytes=p.stat().st_size,sha256=H(p)) for p in files]
manifest=(json.dumps(dict(fixed_sha=FIX,executor='GPT Work supplemental reviewer',verdict='PLAN BLOCKED / REQUEST CHANGES',counts=dict(High=1,Medium=2),created_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),files=entries,self_excluded=True,excluded_finalization=sorted(excluded),not_a_digital_signature=True),ensure_ascii=False,indent=2)+'\n').encode();(O/'EVIDENCE_MANIFEST.json').write_bytes(manifest)
archive=O/'EVIDENCE.zip';assert not archive.exists()
with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6,allowZip64=True) as z:
 for p,e in zip(files,entries):z.write(p,e['path'],compress_type=zipfile.ZIP_STORED if p.suffix=='.zip' else zipfile.ZIP_DEFLATED)
 z.writestr('EVIDENCE_MANIFEST.json',manifest)
with zipfile.ZipFile(archive) as z:
 assert z.testzip() is None and len(z.namelist())==len(set(z.namelist()))==len(entries)+1 and set(z.namelist())=={e['path'] for e in entries}|{'EVIDENCE_MANIFEST.json'}
 assert z.read('EVIDENCE_MANIFEST.json')==manifest
 for e in entries:
  assert z.getinfo(e['path']).file_size==e['bytes']
  with z.open(e['path']) as f:assert hashlib.file_digest(f,'sha256').hexdigest()==e['sha256'],e['path']
r=dict(fixed_sha=FIX,verdict='PLAN BLOCKED / REQUEST CHANGES',findings=dict(High=1,Medium=2),archive='EVIDENCE.zip',bytes=archive.stat().st_size,sha256=H(archive),manifest_sha256=H(O/'EVIDENCE_MANIFEST.json'),manifest_files=len(entries),zip_members=len(entries)+1,CRC_exact_members_all_sizes_hashes_verified=True,executor='GPT Work supplemental reviewer',not_a_digital_signature=True,P6_business_implementation=False,UI_install_AppTest_browser_tests=0,formal_Test=False,financial_approval='NONE',Windows_R2='DEFERRED / NOT VERIFIED',merge_tag_deploy_live_P7=False,created_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
(O/'RECEIPT.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(r,ensure_ascii=False))
