from pathlib import Path
import json,zipfile,hashlib,xml.etree.ElementTree as ET,sys
O=Path(__file__).parent;C=Path('E:/WORK/AQRP-audits/p5-35f93d6/src');R=Path('E:/WORK/AQRP-runs/gpt-p5-35f93d6-20261023/aqrp-e6171f64-5e4a-47c3-b7df-d73eb4d05b2d')
H=lambda b:hashlib.sha256(b).hexdigest()
env=json.loads((R/'environment.json').read_bytes());assert env['complete'] and not env['dirty'] and env['code_commit']=='35f93d640a2304121131d947a465f57a951cf63f'
assert env['lock_sha256']==H((C/'requirements.lock').read_bytes())
junit=ET.fromstring((R/'junit.xml').read_bytes());tests=junit.findall('.//testcase');assert len(tests)==1073 and all(not junit.findall('.//'+s) for s in ['failure','error','skipped'])
selection=json.loads((R/'upload-selection.json').read_bytes())
for e in selection['files']:assert H((R/e['path']).read_bytes())==e['sha256'],e['path']
wheel=next((R/'wheel').glob('aqrp-*.whl'));assert H(wheel.read_bytes())==env['wheel_sha256']
with zipfile.ZipFile(wheel) as z:
 modules=[n for n in z.namelist() if n.startswith('aqrp/') and n.endswith('.py')];assert len(modules)==69
 for n in modules:assert z.read(n)==(C/'src'/n).read_bytes(),n
 assert z.read('aqrp/factors/reviewed_code.json')==(C/'src/aqrp/factors/reviewed_code.json').read_bytes()
coverage=json.loads((R/'coverage.json').read_bytes());rows=[]
critical_names={'time.py','units.py','pit.py','actions.py','snapshot.py','environment.py','exposures.py','numerics.py','pipeline.py','ledger.py','reproduction.py'}
for n,d in coverage['files'].items():
 path=n.replace('\\','/');s=d['summary'];line=100*s['covered_lines']/max(s['num_statements'],1);branch=100*s['covered_branches']/s['num_branches'] if s['num_branches'] else 100
 critical=path.rsplit('/',1)[-1] in critical_names or any('/'+p+'/' in path for p in ['core/security','validation','portfolio','risk','backtest','execution','performance']) or path.endswith(('/services/backtest.py','/services/research.py')) or ('/factors/' in path and path.rsplit('/',1)[-1] in {'contracts.py','input.py','admission.py','builtins.py','engine.py'})
 target=(95,90) if critical else (90,85)
 assert not s['num_statements'] or (line>=target[0] and branch>=target[1]),(path,line,branch,target)
 rows.append({'path':path,'statements':s['num_statements'],'line':line,'branch':branch,'minimum':target})
for name in ['original_replay_smoke.py','independent_reference.py','backtest_reference.py','secret_scan.py','check_coverage.py']:
 assert name in (R/'commands.log').read_text(encoding='utf-8'),name
report={'executor':'GPT Work supplemental reviewer','fixed_sha':env['code_commit'],'run_root':str(R),'environment':env,'tests':1073,'failed':0,'errors':0,'skipped':0,'selected_files_hashed':len(selection['files']),'installed_wheel_modules_equal_fixed_source':69,'coverage_all_modules':rows,'original_Refs_20_4_91_and_smokes':'Actually executed in complete captured SDK; command-by-command output retained, not inferred from a developer prior run','formal_gate':'Only approval-refusal unit/smoke gate executed; no real formal Test','result':'PASS'}
(O/'INDEPENDENT_SDK_VERIFICATION.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:report[k] for k in ['fixed_sha','tests','failed','errors','skipped','selected_files_hashed','result']}))
