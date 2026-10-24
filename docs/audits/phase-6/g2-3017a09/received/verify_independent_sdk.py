from pathlib import Path
import json,hashlib,zipfile,subprocess,xml.etree.ElementTree as ET
O=Path(__file__).parent;C=Path('E:/WORK/AQRP-audits/p6-3017a09/src')
R=Path('E:/WORK/AQRP-runs/gpt-p6-3017a09-20261024-05b3298b-ecfc-49e7-bd8d-5827f1354391/aqrp-4353a1a2-3dae-4db1-aa5d-ff6f56ba351c')
H=lambda b:hashlib.sha256(b).hexdigest()
def fh(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
env=json.loads((R/'environment.json').read_bytes());done=json.loads((O/'SDK_COMPLETION.json').read_bytes())
assert env['complete'] and not env['dirty'] and env['code_commit']=='3017a097b49ecdae68228ca9a417fcd03c313200' and done['exit_code']==0
cases=ET.fromstring((R/'junit.xml').read_bytes()).findall('.//testcase');assert len(cases)==1567 and not any(c.find(n) is not None for c in cases for n in ['failure','error','skipped'])
selection=json.loads((R/'upload-selection.json').read_bytes())['files'];assert len(selection)==len({e['path'] for e in selection})
for e in selection:assert fh(R/e['path'])==e['sha256'],e['path']
coverage=json.loads((R/'coverage.json').read_bytes())
# The fixed gate classifies exact installed file paths and enforces all prior thresholds.
commands=[json.loads(l) for l in (R/'commands.jsonl').read_bytes().splitlines()]
assert all(c['exit']==0 for c in commands)
assert any('check_coverage.py' in ' '.join(c['argv']) for c in commands)
wheel,=(R/'wheel').glob('aqrp-*.whl')
assert fh(wheel)==env['wheel_sha256']
with zipfile.ZipFile(wheel) as z:
 mods=[n for n in z.namelist() if n.startswith('aqrp/') and n.endswith('.py')];assert len(mods)==83
 installed=R/'venv/Lib/site-packages'
 for n in mods:assert z.read(n)==(C/'src'/n).read_bytes()==(installed/n).read_bytes()
 assert z.read('aqrp/factors/reviewed_code.json')==(C/'src/aqrp/factors/reviewed_code.json').read_bytes()
u=json.loads((R/'ui/summary.json').read_bytes())
assert u['real_browser_executed_here'] is False and u['formal_Test'] is False and u['financial_approval']=='NONE'
for factor in ['momentum','reversal']:
 assert all(c['research_equal'] and c['financial_exact_equal'] for c in u['comparisons'][factor].values())
 assert u['records'][factor]['sdk']['config_hash']==u['records'][factor]['task_cli']['config_hash']==u['records'][factor]['component']['config_hash']
assert u['registered_original_Ref_replay']['status']=='SUCCEEDED'
archive=O/'independent-sdk-artifacts.zip';assert not archive.exists()
with zipfile.ZipFile(archive,'x',zipfile.ZIP_DEFLATED,compresslevel=6,allowZip64=True) as z:
 for e in selection:z.write(R/e['path'],e['path'])
 z.write(R/'upload-selection.json','upload-selection.json')
with zipfile.ZipFile(archive) as z:
 assert z.testzip() is None and len(z.namelist())==len(selection)+1 and set(z.namelist())=={e['path'] for e in selection}|{'upload-selection.json'}
 for e in selection:
  with z.open(e['path']) as f:assert hashlib.file_digest(f,'sha256').hexdigest()==e['sha256']
out=dict(executor='GPT Work supplemental reviewer',fixed_sha=env['code_commit'],run_root=str(R),environment=env,SDK_exit=0,pytest_tests=1567,failed=0,errors=0,skipped=0,coverage_gate_passed=True,coverage_modules=len(coverage['files']),selected_files=len(selection),wheel_installed_source_exact_modules=83,wheel_sha256=fh(wheel),four_entry_two_factor_and_old_Ref_parity=True,original20_plus4_and_math91='Separately executed, see ORIGINAL_EXTRA_RESULTS.json',archive=dict(path=archive.name,bytes=archive.stat().st_size,sha256=fh(archive),members=len(selection)+1,CRC_exact_members_all_hashes=True),additional_independent_adversarial_findings='Independent repair challenges recorded separately in INDEPENDENT_CAMPAIGN_RECHECK, INDEPENDENT_CANCELLATION_RECHECK, INDEPENDENT_UNIVERSE_RECHECK and INDEPENDENT_WAL_RECHECK')
(O/'INDEPENDENT_SDK_VERIFICATION.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(tests=1567,failed=0,complete=True,archive=out['archive'])))

