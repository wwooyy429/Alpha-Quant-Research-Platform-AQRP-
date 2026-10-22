import json, platform, subprocess, sys, uuid
from datetime import datetime, timezone
from pathlib import Path
O=Path(__file__).resolve().parent; R=Path(sys.argv[1]); records=[]; run_id=str(uuid.uuid4())
jobs=[('scope',[sys.executable,'-I','-B',str(O/'verify_revision_scope.py'),str(R)]),('math',[sys.executable,'-I','-B',str(O/'independent_revision_math.py')]),('developer-plan-check-replay',[sys.executable,'-I','-B',str(R/'docs/audits/phase-4/check_plan.py')]),('developer-rounding-replay',[sys.executable,'-I','-B',str(R/'docs/audits/phase-4/rounding_reference.py')])]
for name,argv in jobs:
    start=datetime.now(timezone.utc).isoformat();p=subprocess.run(argv,cwd=R,capture_output=True)
    (O/(name+'.stdout.log')).write_bytes(p.stdout);(O/(name+'.stderr.log')).write_bytes(p.stderr)
    record=dict(actual_executor='GPT Work primary reviewer',run_id=run_id,name=name,argv=argv,cwd=str(R),start_UTC=start,end_UTC=datetime.now(timezone.utc).isoformat(),exit_code=p.returncode,stdout=name+'.stdout.log',stderr=name+'.stderr.log',authorship='Developer script hardcoded executor kept; this replay is not reviewer independent math' if name.startswith('developer') else 'Reviewer-authored independent verification')
    records.append(record);(O/(name+'.command.json')).write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(name,'exit',p.returncode,p.stdout.decode('utf-8','replace')[:340])
    if p.returncode: print(p.stderr.decode('utf-8','replace')[:2100])
(O/'execution-environment.json').write_text(json.dumps(dict(actual_executor='GPT Work primary reviewer',run_id=run_id,python=sys.version,executable=sys.executable,OS=platform.platform(),commands=records,installs_account_ACL_or_repository_edits=False),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
sys.exit(any(r['exit_code'] for r in records))
