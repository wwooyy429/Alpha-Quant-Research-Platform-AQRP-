from pathlib import Path
from datetime import datetime, UTC
import csv, hashlib, json, platform, shutil, subprocess, sys
R=Path(r'C:\Users\11638\AppData\Local\AQRP\checkouts\phase1-57461d5d-5de2-4c78-9b4e-5fad2b5ccb29')
O=Path(__file__).parent
P=R/'docs/audits/phase-5';D=P/'g1-5262032';V=D/'developer-validation';V.mkdir(exist_ok=True)
FIXED='5262032bee4f631f68763e57510e1878945f6b8c'
SDK=Path(r'C:\Users\11638\AppData\Local\AQRP\runs\p4-release-20261022\sdk\aqrp-ab6cf214-4ca7-4ac0-810d-6fa745e5bc76')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
def git(*a):return subprocess.check_output(['git',*a],cwd=R).decode().strip()
def run(name,argv):
    started=datetime.now(UTC).isoformat()
    with (O/(name+'.stdout.log')).open('wb') as out,(O/(name+'.stderr.log')).open('wb') as err:
        cp=subprocess.run([str(x) for x in argv],cwd=R,stdout=out,stderr=err)
    dump(O/(name+'.command.json'),{'run_id':O.name+'/'+name,'executor':'Codex developer','scope':'Receipt-only static validation, not new SDK/product/independent/native-isolation tests',
         'argv':[str(x) for x in argv],'cwd':str(R),'start_utc':started,'end_utc':datetime.now(UTC).isoformat(),
         'exit_code':cp.returncode,'parent_and_reviewed_design_sha':FIXED,
         'environment':{'python':sys.version,'executable':sys.executable,'platform':platform.platform()},
         'validation_driver_sha256':sha(Path(__file__))})
    for ext in ('.stdout.log','.stderr.log','.command.json'):shutil.copyfile(O/(name+ext),V/(name+ext))
    assert cp.returncode==0,(name,cp.returncode)
    print(name,'PASS')

assert git('rev-parse','HEAD')==FIXED
allow={'AGENTS.md','docs/PROGRESS.md','docs/ROADMAP.md','docs/DECISIONS.md','docs/TRACEABILITY.md','docs/CHANGELOG.md','docs/audits/phase-5/REVIEW_PACKAGE.md','docs/audits/phase-5/REVIEW_PACKAGE_CURRENT.md','docs/audits/phase-5/STATUS.json','docs/audits/phase-5/FILE_MANIFEST.json'}
changed=set(git('diff','--name-only',FIXED).splitlines())
assert changed<=allow,changed-allow
new=git('ls-files','--others','--exclude-standard').splitlines()
assert all(n.startswith('docs/audits/phase-5/g1-5262032/') for n in new),new
frozen=json.loads((P/'FROZEN_INPUTS.json').read_bytes())['files']
for e in frozen:assert sha(R/e['path'])==e['sha256'],e['path']
identity=json.loads((P/'DESIGN_REVISION_IDENTITY.json').read_bytes())
for e in identity['files']:
    p=P/e['path']; raw=subprocess.check_output(['git','show',FIXED+':'+p.relative_to(R).as_posix()],cwd=R)
    assert p.read_bytes()==raw and sha(p)==e['sha256'] and len(raw)==e['bytes'],e['path']
assert sha(R/'docs/BACKTEST_CONTRACT.md')==identity['frozen_P0_contract_sha256']
rows=list(csv.DictReader((R/'docs/requirements.csv').read_text(encoding='utf-8').splitlines()))
selected=[r for r in rows if r['phase']=='5']
assert len(rows)==106 and len(selected)==12 and selected==json.loads((P/'REQUIREMENTS_SNAPSHOT.json').read_bytes())['requirements']
status=json.loads((P/'STATUS.json').read_bytes())
assert set(status['G1_findings'].values())=={'CLOSED_DESIGN'}
assert status['implementation']=='NOT_AUTHORIZED_NOT_STARTED' and not status['main_merge_tag_authorization']
assert all(s=='DEFERRED / NOT VERIFIED' for s in status['windows_isolation_legacy_findings'].values())
receipt=json.loads((D/'RECEIVED.json').read_bytes())
for e in receipt['git_copied_files']:assert sha(D/'received'/e['path'])==e['sha256']
assert not git('diff',FIXED,'--','src','tests','tools','.github','pyproject.toml','requirements.lock','.gitleaks.toml','docs/requirements.csv','docs/INTERFACES.md','docs/DATA_CONTRACT.md','docs/BACKTEST_CONTRACT.md','docs/REVIEW_PROTOCOL.md','docs/audits/phase-5/g1-5c9721f')
dump(D/'DESIGN_CONTINUITY.json',{'compared_to_reviewed_design_sha':FIXED,'verification_identity':'Codex developer byte-identity receipt, not independent audit of subsequent archival commit',
    'files_unchanged':identity['files'],'frozen_P0_contract_sha256':identity['frozen_P0_contract_sha256'],
    'identity_manifest_unchanged_sha256':sha(P/'DESIGN_REVISION_IDENTITY.json'),
    'frozen_inputs_verified':len(frozen),'canonical_requirements':106,'P5_requirements':12,
    'source_tests_tools_CI_build_lock_unchanged':True,'original_BLOCKED_report_and_all_raw_evidence_unchanged':True,
    'old_pending_labels_in_design_files_are_historical_pre_recheck_state':True,
    'independent_report_verdict_applies_only_to':FIXED,'new_archival_SHA_will_be_PR_metadata_lock_not_a_claim_of_new_independent_review':True})
run('existing-P4-frozen-package',[SDK/'venv/Scripts/python.exe','-I',R/'tools/check_phase4_package.py'])
run('receipt-secret-scan',[SDK/'gitleaks.exe','dir',R,'--config',R/'.gitleaks.toml','--redact=100','--no-banner','--report-format','json','--report-path',O/'scan-findings.json'])
shutil.copyfile(O/'scan-findings.json',V/'scan-findings.json')
dump(V/'VALIDATION.json',{'scope':'Receipt/status only','executor':'Codex developer','run_id':O.name,'reviewed_design_sha':FIXED,
 'archive_CRC_exact189_members_all188_file_hashes':'PASS','raw_top_level_files_copied':57,
 'design_identity_files_byte_unchanged':12,'frozen_inputs_hashes_verified':len(frozen),
 'P4_static_check_exit':0,'secret_scan_exit':0,'canonical_requirements':106,'P5_requirements':12,
 'new_full_SDK_or_business_math_or_CI_ZIP_verification':'NOT_RUN_RECEIPT_ONLY',
 'real_Windows_R2':'DEFERRED / NOT VERIFIED','implementation_authorization':'NOT_GRANTED_NOT_STARTED',
 'human_contract_and_profile_acceptance':'PENDING','merge_tag_deploy_formal_Test_financial_approval':False})
for p in (Path(__file__),O/'receive.py'):shutil.copyfile(p,V/p.name)
for base in (D,P):
    target=base/'FILE_MANIFEST.json'
    dump(target,{'scope':'G1 conditional-pass receipt/status; reviewed526 design unchanged; not implementation authorization',
     'self_excluded':True,'files':[{'path':p.relative_to(base).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(base.rglob('*')) if p.is_file() and p!=target]})
print(json.dumps({'scope':'RECEIPT_ONLY','frozen_inputs':len(frozen),'unchanged_design_files':12,'P5_product_tests':'NOT_RUN','implementation':'NOT_AUTHORIZED_NOT_STARTED'}))
