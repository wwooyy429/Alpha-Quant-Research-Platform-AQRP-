"""Read-only Phase4 plan checks; no portfolio implementation or audit verdict."""
import csv
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[3]
D = Path(__file__).parent
ALLOWED = {'AGENTS.md','README.md','docs/CHANGELOG.md','docs/DECISIONS.md',
           'docs/PROGRESS.md','docs/ROADMAP.md','docs/TRACEABILITY.md'}

def git(*args):
    return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()

def main():
    a=json.loads((D/'AUTHORIZATION.json').read_bytes())
    base=a['phase3_released_main']
    assert git('rev-parse','phase3-baseline^{}')==base
    assert git('rev-parse','v0.3.0^{}')==base
    rows=list(csv.DictReader((ROOT/'docs/requirements.csv').read_text(encoding='utf-8').splitlines()))
    snap=json.loads((D/'REQUIREMENTS_SNAPSHOT.json').read_bytes())
    selected=[r for r in rows if r['phase']=='4']
    assert len(rows)==106 and selected==snap['rows'] and len(selected)==7
    assert sum(r['tier']=='MVP' for r in selected)==4
    assert sum(r['tier']=='Competition Ready' for r in selected)==3
    assert hashlib.sha256((ROOT/'docs/requirements.csv').read_bytes()).hexdigest()==snap['canonical_sha256']
    changes=git('diff','--name-only',base).splitlines()
    assert all(p in ALLOWED or p.startswith('docs/audits/phase-4/') for p in changes),changes
    assert not any((ROOT/'src/aqrp'/p).exists() for p in ('portfolio','risk','backtest','execution','ui'))
    frozen=json.loads((ROOT/'docs/audits/phase-3/IMPLEMENTATION_IDENTITY.json').read_bytes())
    for e in frozen['frozen_files']:
        assert hashlib.sha256((ROOT/e['path']).read_bytes()).hexdigest()==e['sha256'],e['path']
    required=['PLAN.md','INTERFACE_DRAFT.md','REQUIREMENTS_TRACEABILITY.md','SCOPE_AND_DEPENDENCIES.md',
              'GOLDEN_REFERENCE.md','golden_reference.py','SYNTHETIC_PROFILE.json','TEST_AND_EVIDENCE_PLAN.md','REVIEW_PACKAGE.md',
              'ROUNDING_REFERENCE.md','rounding_reference.py','DEVELOPER_RESPONSE.md','STATUS.json','g1-e40ddd0/RECEIPT.json','g1-265af16/RECEIPT.json','g1-265af16/CLOSURE_REGISTER.json']
    assert all((D/p).is_file() for p in required)
    status=json.loads((D/'STATUS.json').read_bytes())
    assert status['independent_verdict']=='PLAN PASS'
    assert status['reviewed_sha']=='265af16353d85ce8c2d229a7517809d707498da8'
    assert status['findings']=={'P4-G1-001':'CLOSED_DESIGN','P4-G1-002':'CLOSED_DESIGN'}
    closure=json.loads((D/'g1-265af16/CLOSURE_REGISTER.json').read_bytes())
    assert closure['verdict']=='PLAN PASS' and not closure['runtime_implementation_verified']
    assert {f['id']:f['status'] for f in closure['findings']}==status['findings']
    assert not status['P4_implementation_authorized']
    print(json.dumps({'actual_executor':'Codex developer','scope':'Read-only design consistency; not independent G1 review or P4 implementation test',
          'phase3_released_base':base,'requirements':7,'MVP':4,'Competition Ready':3,
          'frozen_files_verified':len(frozen['frozen_files']),'source_tests_tools_CI_lock_unchanged':True,'result':'PASS'},indent=2))

if __name__=='__main__': main()
