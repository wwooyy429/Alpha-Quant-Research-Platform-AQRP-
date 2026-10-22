"""External-only command recorder; no project code imported."""
import json, os, platform, subprocess, sys, uuid
from datetime import datetime, timezone
from pathlib import Path
O=Path(__file__).resolve().parent; R=Path(sys.argv[1]); run_id=str(uuid.uuid4())
records=[]
jobs=[('scope',[sys.executable,'-I','-B',str(O/'verify_scope.py'),str(R),str(O)]),
      ('math',[sys.executable,'-I','-B',str(O/'independent_plan_math.py'),str(O)]),
      ('developer-plan-check-replay',[sys.executable,'-I','-B',str(R/'docs/audits/phase-4/check_plan.py')]),
      ('developer-golden-replay',[sys.executable,'-I','-B',str(R/'docs/audits/phase-4/golden_reference.py')])]
for name,argv in jobs:
    start=datetime.now(timezone.utc).isoformat(); p=subprocess.run(argv,cwd=R,capture_output=True)
    (O/(name+'.stdout.log')).write_bytes(p.stdout); (O/(name+'.stderr.log')).write_bytes(p.stderr)
    rec=dict(actual_executor='GPT Work primary reviewer',run_id=run_id,name=name,argv=argv,cwd=str(R),start_utc=start,end_utc=datetime.now(timezone.utc).isoformat(),exit_code=p.returncode,stdout=name+'.stdout.log',stderr=name+'.stderr.log',note='Developer scripts retain hardcoded original authorship; rerun does NOT become independent mathematical derivation' if name.startswith('developer') else 'Independent reviewer-authored stdlib check')
    records.append(rec); (O/(name+'.command.json')).write_text(json.dumps(rec,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(name, 'exit',p.returncode, p.stdout.decode('utf-8','replace')[:400])
    if p.returncode: print(p.stderr.decode('utf-8','replace')[:2000])
(O/'execution-environment.json').write_text(json.dumps(dict(actual_executor='GPT Work primary reviewer',run_id=run_id,python=sys.version,executable=sys.executable,os=platform.platform(),environment_changes='NONE; no installs, accounts, ACL, services, deployment or business source changes',commands=records),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
sys.exit(any(r['exit_code'] for r in records))
