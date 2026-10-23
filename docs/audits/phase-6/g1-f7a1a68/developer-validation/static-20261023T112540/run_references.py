from pathlib import Path
from datetime import datetime, UTC
import hashlib,json,os,subprocess,sys

O=Path(__file__).resolve().parent
R=Path(r'C:/Users/11638/AppData/Local/AQRP/checkouts/phase1-57461d5d-5de2-4c78-9b4e-5fad2b5ccb29')
D=R/'docs/audits/phase-6';V=D/'g1-f7a1a68/developer-validation'
attempt=V/('candidate-'+datetime.now(UTC).strftime('%Y%m%dT%H%M%S'));attempt.mkdir()
commands=[('original32',[sys.executable,'-I',str(D/'reference_check.py'),str(attempt/'ORIGINAL32_RESULTS.json')]),('supplemental95',[sys.executable,'-I',str(D/'revision_reference.py'),str(attempt/'SUPPLEMENTAL_RESULTS.json')]),('original-counterexamples-after',[sys.executable,'-I',str(O/'numeric_probe.py'),str(D/'reference_check.py'),str(attempt/'AFTER_NUMERIC_COUNTEREXAMPLES.json')]),('numeric-context-Fraction',[sys.executable,'-I',str(O/'property_reference.py'),str(D),str(attempt/'NUMERIC_PROPERTIES.json')])]
env=os.environ.copy();env['PYTHONUTF8']='1';records=[]
diff=subprocess.check_output(['git','diff','--binary','f7a1a68c5f747090f8c8a0e934f2fea859aec998'],cwd=R);(attempt/'WORKING_DESIGN_DIFF.patch').write_bytes(diff)
for name,args in commands:
 start=datetime.now(UTC).isoformat();p=subprocess.run(args,cwd=R,env=env,capture_output=True)
 (attempt/(name+'.stdout.log')).write_bytes(p.stdout);(attempt/(name+'.stderr.log')).write_bytes(p.stderr)
 record={'executor':'Codex developer G1 design reference; not independent review or P6 implementation test','source_parent_commit':'f7a1a68c5f747090f8c8a0e934f2fea859aec998','source_dirty_design':True,'tracked_design_diff_sha256':hashlib.sha256(diff).hexdigest(),'source_files':{n:hashlib.sha256((D/n).read_bytes()).hexdigest() for n in ['reference_check.py','revision_reference.py','GOLDEN_CANDIDATES.json','SUPPLEMENTAL_CANDIDATES.json']},'argv':args,'cwd':str(R),'started_utc':start,'finished_utc':datetime.now(UTC).isoformat(),'exit_code':p.returncode}
 (attempt/(name+'.command.json')).write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8',newline='\n');records.append(record)
 print(name+': '+p.stdout.decode('utf-8',errors='replace')[-1500:],flush=True)
 if p.returncode:
  print(p.stderr.decode('utf-8',errors='replace')[-2500:]);raise SystemExit(p.returncode)
(O/'REFERENCE_RUN.json').write_text(json.dumps({'attempt':str(attempt),'all_exit_zero':True,'commands':records},indent=2)+'\n',encoding='utf-8',newline='\n')
print(json.dumps({'reference_attempt':str(attempt),'result':'PASS_DESIGN_REFERENCES_ONLY'}))
