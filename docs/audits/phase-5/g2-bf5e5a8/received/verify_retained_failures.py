from pathlib import Path
import json,zipfile,hashlib
O=Path(__file__).parent;D=O.parent/'p5-g2-003-recheck-bf5e5a8';F=D/'retained-failures';H=lambda b:hashlib.sha256(b).hexdigest()
art=json.loads((O/'FAILED_CI_ARTIFACTS_API.json').read_bytes())['artifacts'];jobs=json.loads((O/'FAILED_CI_JOBS_API.json').read_bytes())['jobs'];assert len(jobs)==2 and all(j['conclusion']=='failure' for j in jobs)
results=[]
for a in art:
 p=F/'official-run39908508825'/(a['name']+'-official-original.zip');raw=p.read_bytes();assert len(raw)==a['size_in_bytes'] and H(raw)==a['digest'].removeprefix('sha256:')
 assert a['workflow_run']['head_sha']=='daf055157bde1ba95ef2d1d8706bedde0301901f'
 with zipfile.ZipFile(p) as z:
  assert z.testzip() is None and len(set(z.namelist()))==len(z.namelist())
  logname=next(n for n in z.namelist() if n.endswith('commands.log'));log=z.read(logname).decode('utf-8');assert 'check_phase5_package.py' in log and ('PRESERVED_FILE_CHANGED' in log or 'COMMAND_LOG.txt' in log),log[-2000:]
  env=json.loads(z.read(next(n for n in z.namelist() if n.endswith('environment.json'))));assert not env['complete']
 results.append(dict(artifact=a,sha256=H(raw),CRC='PASS',failure_log_retained=True,environment_complete=False))
correction=json.loads((Path('E:/WORK/AQRP-audits/p5-bf5e5a8/src')/'docs/audits/phase-5/g2-35f93d6/PRESERVATION_CORRECTION.json').read_bytes())
for e in correction['restored']:assert H((F/'misapplied-phase0-script-output'/Path(e['path']).name).read_bytes())==e['erroneous_output_sha256']
env=json.loads((F/'daf0551-SDK/environment.json').read_bytes());assert not env['complete'];assert 'check_phase5_package.py' in (F/'daf0551-SDK/commands.log').read_text(encoding='utf-8')
(O/'RETAINED_FAILURE_VERIFICATION.json').write_text(json.dumps(dict(result='PASS',scope='Preserved failures remain failures; not new execution of old failed candidate',official=results,three_erroneous_original_outputs_preserved=True,local_failed_sdk_incomplete=True),ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print('Preserved local/dual-OS failure ZIP/API/CRC/logs and three erroneous originals PASS')
