from pathlib import Path
from datetime import datetime,UTC
import os,subprocess,sys,json,uuid
O=Path(__file__).parent;C=Path('E:/WORK/AQRP-audits/p6-3017a09/src')
FIX='3017a097b49ecdae68228ca9a417fcd03c313200'
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=C,text=True).strip()==FIX
assert subprocess.check_output(['git','status','--porcelain'],cwd=C)==b''
run=Path('E:/WORK/AQRP-runs')/('gpt-p6-3017a09-20261024-'+str(uuid.uuid4()));run.mkdir()
old=Path('E:/WORK/AQRP-runs/p6-sdk-eae807f-400d50e0-73d4-45b5-a807-7b2d01497ce2/aqrp-68070ecf-5f28-4e1c-8483-334b98631cfc')
links=[old/'reproduction/wheelhouse',old/'ui-wheelhouse']
assert all(p.is_dir() for p in links)
env=dict(os.environ);env['AQRP_RUN_ROOT']=str(run);env['PIP_FIND_LINKS']=' '.join(str(p) for p in links);env['PYTHONUTF8']='1'
cmd=[sys.executable,'-X','utf8',str(C/'tools/ci.py')]
record=dict(actual_executor='GPT Work supplemental reviewer',fixed_sha=FIX,cwd=str(C),argv=cmd,started_utc=datetime.now(UTC).isoformat(),artifacts_parent=str(run),cache_scope='Original retained wheel bytes only, exact hashed new clean venv installation; no installed environment reuse',PIP_FIND_LINKS=[str(p) for p in links],scope='Restricted engineering SDK validation only; no deployment or real formal Test')
(O/'SDK_START.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
print(json.dumps(record),flush=True)
with (O/'SDK.stdout.log').open('wb') as out,(O/'SDK.stderr.log').open('wb') as err:p=subprocess.run(cmd,cwd=C,env=env,stdout=out,stderr=err)
record.update(exit_code=p.returncode,ended_utc=datetime.now(UTC).isoformat())
(O/'SDK_COMPLETION.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8');print(json.dumps(record));sys.exit(p.returncode)

