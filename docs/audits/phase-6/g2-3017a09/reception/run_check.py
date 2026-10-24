import hashlib,json,subprocess,sys
from pathlib import Path
from datetime import datetime,timezone
O=Path('C:/Users/11638/AppData/Local/AQRP/runs/p6-g2-pass-3017a09-20261024/receipt-check')
cmd=[sys.executable,'-X','utf8',str(O/'verify_received.py')]
m={'argv':cmd,'cwd':str(O),'started_utc':datetime.now(timezone.utc).isoformat(),'script_sha256':hashlib.sha256((O/'verify_received.py').read_bytes()).hexdigest()}
(O/'command.json').write_text(json.dumps(m,indent=2)+'\n',encoding='utf-8')
with (O/'stdout.log').open('wb') as out,(O/'stderr.log').open('wb') as err:
    p=subprocess.run(cmd,cwd=O,stdout=out,stderr=err)
m.update(exit_code=p.returncode,completed_utc=datetime.now(timezone.utc).isoformat())
(O/'command.json').write_text(json.dumps(m,indent=2)+'\n',encoding='utf-8')
print((O/'stdout.log').read_text(encoding='utf-8'))
if p.returncode:
    print((O/'stderr.log').read_text(encoding='utf-8'),file=sys.stderr)
sys.exit(p.returncode)
