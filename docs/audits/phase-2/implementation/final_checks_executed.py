import csv,hashlib,json,pathlib,shutil,subprocess,xml.etree.ElementTree as ET
from datetime import datetime,timezone
repo=pathlib.Path(r'C:\Users\11638\AppData\Local\AQRP\checkouts\phase1-57461d5d-5de2-4c78-9b4e-5fad2b5ccb29')
run=pathlib.Path(__file__).resolve().parent
audit=repo/'docs/audits/phase-2/implementation'
sha=lambda b:hashlib.sha256(b).hexdigest()
def git(*args): return subprocess.check_output(['git',*args],cwd=repo)
for name in git('diff','--name-only').decode().splitlines():
    old=git('show','HEAD:'+name)
    if b'\r\n' in old:
        p=repo/name
        p.write_bytes(p.read_bytes().replace(b'\r\n',b'\n').replace(b'\n',b'\r\n'))
protected=json.loads((repo/'docs/audits/phase-1/implementation/CORE_PRESERVATION.json').read_bytes())['files']
for item in protected: assert sha((repo/item['path']).read_bytes())==item['sha256'],item['path']
assert len(protected)==50
assert not git('diff','8183b3762b56c466b989d9062a720b5f0d31172a','--','src','tests','tools','.github','pyproject.toml','requirements.lock')
old_audit_files=git('ls-tree','-r','--name-only','f579b2c','--','docs/audits/phase-0','docs/audits/phase-1').decode().splitlines()
for p in old_audit_files: assert (repo/p).read_bytes()==git('show','f579b2c:'+p),p
# Separate immutable catalog/design from current progress documents.
for p in ('docs/requirements.csv','docs/REQUIREMENTS.md','docs/TRACEABILITY.md','docs/ARCHITECTURE.md','docs/INTERFACES.md','docs/DATA_CONTRACT.md','docs/BACKTEST_CONTRACT.md','docs/PROJECT_CHARTER.md','requirements.lock'):
    assert (repo/p).read_bytes()==git('show','4f8b0de:'+p),p
for p in ('docs/audits/phase-2/PLAN.md','docs/audits/phase-2/SELF_CHECK.json','docs/audits/phase-2/MANIFEST.json','docs/audits/phase-2/golden_cases.json','docs/audits/phase-2/FACTOR_IMPLEMENTATION_SPEC.md'):
    assert (repo/p).read_bytes()==git('show','4f8b0de:'+p),p
golden=git('show','4f8b0de:docs/audits/phase-2/golden_cases.json')
assert (repo/'tests/golden/phase2_answers.json').read_bytes()==golden
rows=list(csv.DictReader((repo/'docs/requirements.csv').read_text(encoding='utf-8').splitlines()))
assert len(rows)==106 and len({r['id'].split('-')[0] for r in rows})==16
actual=list(ET.parse(audit/'local/junit.xml').getroot().iter('testcase'))
p2=sum('factors' in x.attrib.get('classname','') for x in actual)
assert len(actual)==254 and p2==152
raw=repo/'docs/audits/phase-2/gemini/aqrp_phase2_plan_pre_review_report.md'
assert sha(raw.read_bytes())=='5b6abe40bc78d088b40f19f883ddd0cfe551c52c6b625c8f6606c28a590aa35e'
remote=git('ls-remote','origin','refs/heads/main','refs/tags/phase0-baseline','refs/tags/phase0-baseline^{}','refs/tags/phase1-baseline','refs/tags/phase1-baseline^{}').decode().splitlines()
refs={x.split()[1]:x.split()[0] for x in remote}
assert refs=={
'refs/heads/main':'f579b2c99e762085772de6e70ba1fa98792a7add',
'refs/tags/phase0-baseline':'0b2230cd4861ca3b47fa30fc30dae9f4dc4109d0',
'refs/tags/phase0-baseline^{}':'7de1d0e81385ae97f98ea673fe05dd726f0b577b',
'refs/tags/phase1-baseline':'1a8e47ee4be910aa7eeeefa430015e683a8aa6f5',
'refs/tags/phase1-baseline^{}':'f579b2c99e762085772de6e70ba1fa98792a7add'}
assert not git('ls-remote','--tags','origin','*phase2*')
conflicts=[str(p.relative_to(repo)) for p in repo.rglob('*冲突文件*') if p.is_file() and '.git' not in p.parts]
assert not conflicts,conflicts
result={'generated_at_utc':datetime.now(timezone.utc).isoformat(),'performed_by':'Codex developer','implementation_commit':'8183b3762b56c466b989d9062a720b5f0d31172a','src_tests_tools_ci_metadata_lock_unchanged_since_implementation':True,'phase0_protected_asset_hashes_verified':len(protected),'phase0_phase1_audit_files_byte_preserved':len(old_audit_files),'requirements':106,'prefix_groups':16,'p2_requirements':10,'canonical_and_frozen_contracts_unchanged':True,'original_plan_snapshot_preserved':True,'golden_source_commit':'4f8b0de01b5991ef172f52f6a81e64b855a32d68','golden_answer_sha256':sha(golden),'golden_answers_unchanged':True,'junit_total':254,'p1_regression':102,'new_factor_tests':152,'report_original_sha256':sha(raw.read_bytes()),'auto_sync_conflicts_found':conflicts,'remote_refs':refs,'phase2_tag_exists':False,'human_accepted':False,'merge_authorized':False,'tag_authorized':False,'phase3_authorized':False,'stage':'IMPLEMENTATION REVIEW REQUIRED','secret_scan':'See secret-scan.log and scan-findings.json from final archive scan'}
(audit/'FINAL_CHECKS.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result,ensure_ascii=False,indent=2))

