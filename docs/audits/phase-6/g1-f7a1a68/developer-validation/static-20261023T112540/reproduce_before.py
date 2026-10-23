from pathlib import Path
from datetime import datetime, UTC
import json,subprocess,sys
O=Path(__file__).resolve().parent
R=Path(r'C:/Users/11638/AppData/Local/AQRP/checkouts/phase1-57461d5d-5de2-4c78-9b4e-5fad2b5ccb29')
V=R/'docs/audits/phase-6/g1-f7a1a68/developer-validation';V.mkdir(exist_ok=False)
argv=[sys.executable,'-I',str(O/'numeric_probe.py'),str(O/'original-reference_check.py'),str(V/'BEFORE_NUMERIC_COUNTEREXAMPLES.json')]
start=datetime.now(UTC).isoformat();p=subprocess.run(argv,cwd=O,capture_output=True)
(V/'before-numeric.stdout.log').write_bytes(p.stdout);(V/'before-numeric.stderr.log').write_bytes(p.stderr)
(V/'before-numeric.command.json').write_text(json.dumps({'executor':'Codex developer reproducing reviewer-reported defects in original design reference','reviewed_source_sha':'f7a1a68c5f747090f8c8a0e934f2fea859aec998','argv':argv,'cwd':str(O),'started_utc':start,'finished_utc':datetime.now(UTC).isoformat(),'exit_code':p.returncode,'expected_failure':True,'P6_business_tests':False},indent=2)+'\n',encoding='utf-8',newline='\n')
assert p.returncode==1 and json.loads((V/'BEFORE_NUMERIC_COUNTEREXAMPLES.json').read_bytes())['mismatched']==2
print('Original two numeric counterexamples reproduced; nonzero exit and raw logs preserved')
