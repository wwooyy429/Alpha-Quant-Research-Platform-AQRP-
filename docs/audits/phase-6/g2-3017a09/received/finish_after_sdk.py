"""Bounded current-turn final verification after the already running required SDK."""
from pathlib import Path
import time,subprocess,sys,json
O=Path(__file__).parent;start=time.monotonic()
while not (O/'SDK_COMPLETION.json').is_file():
 if time.monotonic()-start>3600:raise TimeoutError('Required SDK has not completed; no PASS')
 time.sleep(2)
done=json.loads((O/'SDK_COMPLETION.json').read_bytes());assert done['exit_code']==0,done
for label,script in [('independent-sdk-verification','verify_independent_sdk.py'),('coverage-verification','verify_coverage.py')]:
 subprocess.run([sys.executable,str(O/'run_capture.py'),label,str(O),sys.executable,str(O/script)],check=True)
print('Required SDK and independent artifact/coverage checks completed; ready for final decision')
