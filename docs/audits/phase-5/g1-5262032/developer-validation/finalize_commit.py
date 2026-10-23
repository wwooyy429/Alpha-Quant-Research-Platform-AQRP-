from pathlib import Path
from datetime import datetime,UTC
import hashlib,json,shutil,subprocess
R=Path(r'C:\Users\11638\AppData\Local\AQRP\checkouts\phase1-57461d5d-5de2-4c78-9b4e-5fad2b5ccb29');O=Path(__file__).parent;P=R/'docs/audits/phase-5';D=P/'g1-5262032';V=D/'developer-validation'
FIXED='5262032bee4f631f68763e57510e1878945f6b8c'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
def git(*a):return subprocess.check_output(['git',*a],cwd=R).decode().strip()
assert git('rev-parse','HEAD')==FIXED
for ext in ('.stdout.log','.stderr.log'):shutil.copyfile(O/('final-staged-check'+ext),V/('first-staged-check'+ext))
assert (V/'first-staged-check.stdout.log').read_text().count('new blank line at EOF.')==2
assert (D/'.gitattributes').read_text().strip()=='* whitespace=cr-at-eol'
(D/'.gitattributes').write_text('* whitespace=cr-at-eol\n# Received raw HTTP metadata: preserve original bytes and terminal blank lines.\nreceived/CI_RUNS_FINAL.json whitespace=cr-at-eol,-blank-at-eof\nreceived/PR8_FINAL.json whitespace=cr-at-eol,-blank-at-eof\n',encoding='utf-8',newline='\n')
dump(V/'RAW_EVIDENCE_WHITESPACE_DISPOSITION.json',{'initial_staged_check':'FAILED: two received JSON metadata files contain original terminal blank lines','initial_failure_stdout':'first-staged-check.stdout.log','initial_failure_stderr':'first-staged-check.stderr.log','raw_files':['received/CI_RUNS_FINAL.json','received/PR8_FINAL.json'],'disposition':'Keep original independently sealed bytes; exempt blank-at-eof only for these exact two raw metadata files, retaining other whitespace checks. No product/security guard or expected hash changed.','initial_failed_command':['git','diff','--cached','--check'],'author':'Codex developer','at_utc':datetime.now(UTC).isoformat()})
receipt=json.loads((D/'RECEIVED.json').read_bytes())
for e in receipt['git_copied_files']:assert sha(D/'received'/e['path'])==e['sha256'],e['path']
for p in (Path(__file__),O/'commit.py'):shutil.copyfile(p,V/p.name)
validation=json.loads((V/'VALIDATION.json').read_bytes())
validation['initial_staged_check']='FAILED: two raw evidence EOF blank-line warnings; preserved unchanged with two-path formatting-only exception'
validation['whitespace_disposition']='RAW_EVIDENCE_WHITESPACE_DISPOSITION.json'
dump(V/'VALIDATION.json',validation)
for base in (D,P):
    target=base/'FILE_MANIFEST.json'
    dump(target,{'scope':'G1 conditional-pass receipt/status; reviewed526 design unchanged; not implementation authorization','self_excluded':True,'files':[{'path':p.relative_to(base).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(base.rglob('*')) if p.is_file() and p!=target]})
allowed=['AGENTS.md','docs/PROGRESS.md','docs/ROADMAP.md','docs/DECISIONS.md','docs/TRACEABILITY.md','docs/CHANGELOG.md','docs/audits/phase-5/REVIEW_PACKAGE.md','docs/audits/phase-5/REVIEW_PACKAGE_CURRENT.md','docs/audits/phase-5/STATUS.json','docs/audits/phase-5/FILE_MANIFEST.json','docs/audits/phase-5/g1-5262032']
subprocess.run(['git','add','--',*allowed],cwd=R,check=True)
paths=git('diff','--cached','--name-only').splitlines()
assert all(p in allowed or p.startswith(allowed[-1]+'/') for p in paths)
cp=subprocess.run(['git','diff','--cached','--check'],cwd=R,capture_output=True)
(O/'final-staged-check-rerun.stdout.log').write_bytes(cp.stdout);(O/'final-staged-check-rerun.stderr.log').write_bytes(cp.stderr)
dump(O/'final-staged-check-rerun.command.json',{'argv':['git','diff','--cached','--check'],'cwd':str(R),'at_utc':datetime.now(UTC).isoformat(),'exit_code':cp.returncode,'executor':'Codex developer','scope':'Receipt only, two raw JSON EOF formatting exceptions disclosed'})
assert cp.returncode==0
for base in (D,P):
    for e in json.loads((base/'FILE_MANIFEST.json').read_bytes())['files']:assert sha(base/e['path'])==e['sha256'],e['path']
assert not git('diff','--name-only')
subprocess.run(['git','-c','user.name=Codex','-c','user.email=codex@localhost','commit','-q','-m','docs: archive Phase5 G1 conditional pass and pending human decisions'],cwd=R,check=True)
new=git('rev-parse','HEAD')
assert git('rev-parse','HEAD^')==FIXED and not git('status','--porcelain')
dump(O/'COMMIT_RECEIPT.json',{'archive_status_commit':new,'independently_reviewed_design_commit':FIXED,'reviewed_design_unchanged':True,'scope':'Report/archive/status only; not new independent audit, human acceptance or implementation authorization','staged_files':paths,'initial_staged_check':'FAILED_PRESERVED','final_staged_diff_check_exit':0,'main_tags_unchanged_locally':True,'at_utc':datetime.now(UTC).isoformat()})
print(json.dumps({'archive_status_commit':new,'independently_reviewed_design_commit':FIXED,'files':len(paths),'implementation':'NOT_AUTHORIZED_NOT_STARTED'}))
