from pathlib import Path
import json,hashlib
O=Path(__file__).parent;R=Path('E:/WORK/AQRP-runs/gpt-p6-3017a09-20261024-05b3298b-ecfc-49e7-bd8d-5827f1354391/aqrp-4353a1a2-3dae-4db1-aa5d-ff6f56ba351c')
coverage=json.loads((R/'coverage.json').read_bytes());records=[]
critical_names={'time.py','units.py','pit.py','actions.py','snapshot.py','environment.py','exposures.py','numerics.py','pipeline.py','ledger.py','reproduction.py'}
critical_prefixes=['core/security/','validation/','portfolio/','risk/','backtest/','execution/','performance/']
for path,v in coverage['files'].items():
 n=path.replace('\\','/').split('/aqrp/')[-1];a,b=90,85
 if n.split('/')[-1] in critical_names or any(n.startswith(p) for p in critical_prefixes) or n in ['services/backtest.py','services/research.py','services/tasks.py','services/task_state.py','services/task_context.py'] or (n.startswith('factors/') and n.split('/')[-1] in {'contracts.py','input.py','admission.py','builtins.py','engine.py'}):a,b=95,90
 if n in ['ui/app.py','ui/launch.py','services/task_cli.py']:a,b=80,70
 x=v['summary'];line=100*x['covered_lines']/max(1,x['num_statements']);branch=100*x['covered_branches']/x['num_branches'] if x['num_branches'] else 100
 assert not x['num_statements'] or (line>=a and branch>=b),(path,line,branch,a,b)
 records.append(dict(path=n,line=line,branch=branch,gate=[a,b],passed=True))
C=Path('E:/WORK/AQRP-audits/p6-3017a09/src')
manifest=json.loads((C/'docs/audits/phase-6/IMPLEMENTATION_IDENTITY.json').read_bytes())['bundle_manifest']['files']
expected={e['path'] for e in manifest};observed={r['path'] for r in records}
assert expected<=observed,(expected-observed)

assert len(expected)==83
(O/'COVERAGE_VERIFICATION.json').write_text(json.dumps(dict(coverage=records,coverage_all_bundle_modules_present=len(expected),result='PASS'),indent=2)+'\n',encoding='utf-8')
print('All83 source modules covered and gates PASS')
