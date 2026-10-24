from pathlib import Path
import subprocess,socket,json,sys,os,hashlib,datetime
from aqrp.services.task_requests import initialize
from aqrp.services.tasks import TaskService
import aqrp
O=Path(__file__).parent
root=Path('E:/WORK/AQRP-runs/gpt-p6-browser-3017a09-independent-20261024');assert not root.exists();root.mkdir()
workspace=root/'workspace'
cat=initialize(workspace,'3017a097b49ecdae68228ca9a417fcd03c313200')
with socket.socket() as sock:sock.bind(('127.0.0.1',0));port=sock.getsockname()[1]
argv=[sys.executable,'-m','aqrp.ui.launch','--workspace',str(workspace),'--commit','3017a097b49ecdae68228ca9a417fcd03c313200','--port',str(port)]
with (root/'server.stdout.log').open('wb') as out,(root/'server.stderr.log').open('wb') as err:
 p=subprocess.Popen(argv,cwd=root,stdin=subprocess.DEVNULL,stdout=out,stderr=err,creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0)
record=dict(actual_executor='GPT Work supplemental reviewer',fixed_sha=cat['code_commit'],argv=argv,pid=p.pid,workspace=str(workspace),root=str(root),url='http://127.0.0.1:'+str(port),installed_aqrp=str(Path(aqrp.__file__)),started_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),scope='Independent local loopback engineering UI validation only; no deployment/formal Test/financial approval')
(O/'BROWSER_START.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
print(json.dumps(record))


