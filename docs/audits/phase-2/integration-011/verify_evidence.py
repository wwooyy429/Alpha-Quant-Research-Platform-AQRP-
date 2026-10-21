"""Actual developer verification of the new integration SDK and original Actions bytes."""
import csv
import hashlib
import json
import pathlib
import shutil
import stat
import subprocess
import sys
import xml.etree.ElementTree as ET
import zipfile
from datetime import date
from dataclasses import asdict

from aqrp.core.canonical import canonical, digest
from aqrp.core.contracts import QuerySpec, SnapshotRef
from aqrp.core.time import utc
from aqrp.data.query import query
from aqrp.data.snapshot import verify_snapshot

ROOT=pathlib.Path(r'C:\Users\11638\AppData\Local\AQRP\checkouts\phase1-57461d5d-5de2-4c78-9b4e-5fad2b5ccb29')
OUT=pathlib.Path(__file__).parent
DEST=ROOT/'docs/audits/phase-2/integration-011'
CODE='566f0ece4175fddb2703daab3b5b26ff0e4e245f'
MAIN='fb1ba4fd51202a303115e4449ee49db09ccc071c'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
git=lambda *a:subprocess.check_output(['git',*a],cwd=ROOT,text=True).strip()
def write(path,data):
 path.parent.mkdir(parents=True,exist_ok=True)
 path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')

def verify_run(run,remote=False):
 env=json.loads((run/'environment.json').read_bytes())
 assert env['complete'] and not env['dirty']
 assert env['lock_sha256']==sha(ROOT/'requirements.lock')
 assert env['python'].startswith('3.13.16')
 actual=env['code_commit']
 assert git('rev-parse',actual+'^{tree}')==git('rev-parse',CODE+'^{tree}')
 parents=git('show','-s','--format=%P',actual).split()
 if remote:assert parents==[MAIN,CODE],parents
 else:assert actual==CODE
 suite=ET.parse(run/'junit.xml').getroot().find('testsuite')
 counts={k:int(suite.attrib[k]) for k in ['tests','failures','errors','skipped']}
 assert counts=={'tests':392,'failures':0,'errors':0,'skipped':0},counts
 selected=json.loads((run/'upload-selection.json').read_bytes())
 for item in selected['files']:
  assert sha(run/item['path'])==item['sha256'],item['path']
 if remote:
  assert {p.relative_to(run).as_posix() for p in run.rglob('*') if p.is_file()}=={e['path'] for e in selected['files']}|{'upload-selection.json'}
 for item in json.loads((run/'artifacts.json').read_bytes()):
  if item['uploaded']:assert sha(run/item['path'])==item['sha256']
  elif remote:assert not (run/item['path']).exists()
 wheel=next((run/'wheel').glob('aqrp-*.whl'))
 assert wheel.name=='aqrp-0.2.0-py3-none-any.whl' and sha(wheel)==env['wheel_sha256']
 with zipfile.ZipFile(wheel) as z:
  receipt=json.loads(z.read('aqrp/factors/reviewed_code.json'))
  assert receipt==json.loads((ROOT/'src/aqrp/factors/reviewed_code.json').read_bytes())
  for p in (ROOT/'src/aqrp').rglob('*.py'):
   assert z.read(p.relative_to(ROOT/'src').as_posix())==p.read_bytes()
 coverage=subprocess.run([sys.executable,str(ROOT/'tools/check_coverage.py'),str(run/'coverage.json')],capture_output=True,text=True)
 assert coverage.returncode==0,coverage.stdout+coverage.stderr
 assert json.loads((run/'scan-findings.json').read_bytes())==[]
 snapshots=[]
 for kind in ['dataset','factor-dataset']:
  m=next((run/kind).glob('*/manifest.json'));manifest=json.loads(m.read_bytes())
  ref=SnapshotRef(m.parent.parent,manifest['snapshot_id'],manifest['manifest_hash'])
  _,tables=verify_snapshot(ref)
  assert len(tables)==8
  snapshots.append({'kind':kind,'snapshot_id':ref.snapshot_id,'manifest_hash':ref.manifest_hash,'tables':8})
  if kind=='dataset':
   config=json.loads((run/'smoke-config.json').read_bytes())
   spec=QuerySpec(tuple(config['security_ids']),config['market_id'],config['calendar_id'],tuple(date.fromisoformat(x) for x in config['session_range']),tuple(config['fields']),config['price_basis'])
   view=query(spec,config['as_of'],ref)
   assert canonical(view.table.to_pylist())==(run/'smoke-result.json').read_bytes()
   # The existing query contract includes the original storage root. Replayed
   # rows must match, but relocation is allowed to change the query identity.
   smoke=json.loads((run/'smoke-run.json').read_bytes())
   spec_config=asdict(spec);del spec_config['request_id']
   original_snapshot=asdict(ref)|{'root':smoke['dataset']}
   recorded_hash=digest({'snapshot':original_snapshot,'cutoff':utc(config['as_of']),'spec':spec_config,'rule_version':'pit/1.0.0','provenance':manifest['provenance']})
   assert recorded_hash==smoke['query_hash']
   assert digest(view.table.to_pylist())==smoke['result_hash']
 factors=json.loads((run/'factor-result.json').read_bytes())
 assert {k:v['value'] for k,v in factors.items()}=={'momentum':.21,'reversal':-.21,'volume':.6}
 runs=[]
 for m in (run/'factor-runs').glob('*/manifest.json'):
  manifest=json.loads(m.read_bytes())
  assert manifest['status']=='SUCCEEDED' and manifest['mode']=='TEST_ONLY' and manifest['financial_approval']=='NONE'
  for entry in manifest['artifacts']:assert sha(m.parent/entry['path'])==entry['sha256']
  runs.append(manifest['logical_hash'])
 assert len(runs)==3
 approval=json.loads((run/'factor-code-approval.json').read_bytes())
 assert approval['implementation_hash']=='fc1b50110c02efbe4a53168c43d7fe4972e5ebab3edc3091aeaf58ac72a11fc7'
 return {'environment':env,'junit':counts,'selected_hashes_verified':len(selected['files']),'root_inventory_verified':True,'wheel_bytes_and_all_python_members_verified':True,'receipt':approval,'snapshot_and_query_replay':snapshots,'factor_results':factors,'factor_runs_manifest_hashes_verified':3,'coverage_gate':coverage.stdout.strip(),'checkout_parents':parents,'tree_equals_implementation':True,'omitted_local_tools':selected['omitted_local_tools'],'secret_findings':0,'executor':'Codex developer; remote Ubuntu bytes replayed on Windows SDK, not a fresh local Linux install or independent Gemini execution'}

local=next((OUT/'formal').glob('aqrp-*'))
assert (OUT/'sdk-exit.txt').read_text(encoding='utf-8-sig').strip()=='0'
local_result=verify_run(local)
artifacts=json.loads((OUT/'remote_artifacts.json').read_bytes())['artifacts']
remote_results=[]
for platform in ['windows','ubuntu']:
 meta=next(x for x in artifacts if platform in x['name'])
 zpath=OUT/'remote'/f'{platform}.zip'
 assert zpath.stat().st_size==meta['size_in_bytes']
 assert sha(zpath)==meta['digest'].removeprefix('sha256:')
 extract=OUT/'remote/extracted'/platform
 with zipfile.ZipFile(zpath) as z:
  assert z.testzip() is None
  assert len(z.namelist())==len(set(z.namelist()))
  for info in z.infolist():
   p=pathlib.PurePosixPath(info.filename)
   assert not p.is_absolute() and '..' not in p.parts and '\\' not in info.filename and ':' not in info.filename
   assert not stat.S_ISLNK(info.external_attr>>16) and info.file_size<10_000_000
  assert sum(i.file_size for i in z.infolist())<30_000_000
  extract.mkdir(parents=True,exist_ok=False);z.extractall(extract)
 run=next(p for p in extract.iterdir() if p.is_dir())
 verified=verify_run(run,remote=True)
 assert verified['factor_results']==local_result['factor_results']
 assert (run/'smoke-result.json').read_bytes()==(local/'smoke-result.json').read_bytes()
 verified.update(artifact_id=meta['id'],artifact_name=meta['name'],zip_sha256=sha(zpath),zip_bytes=zpath.stat().st_size,crc_and_safe_paths='PASS')
 (DEST/'ci').mkdir(exist_ok=True)
 shutil.copy2(zpath,DEST/'ci'/f'{platform}.zip')
 write(DEST/'ci'/f'{platform}-verification.json',verified)
 remote_results.append(verified)
for name in ['remote_artifacts.json','remote_run.json','remote_jobs.json']:
 shutil.copy2(OUT/name,DEST/'ci'/name)
for item in json.loads((local/'upload-selection.json').read_bytes())['files']+[{'path':'upload-selection.json'}]:
 p=DEST/'sdk'/item['path'];p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(local/item['path'],p)
for name in ['sdk-console.log','sdk-exit.txt','original16.log','original16.xml','original16-command.json','original16-exit.txt','wheel-origin.json','verify-first.py','archive-verification-first-failure.log']:
 shutil.copy2(OUT/name,DEST/name)
shutil.copy2(pathlib.Path(__file__),DEST/'verify_evidence.py')
write(DEST/'CHECKER_CORRECTION.json',{'first_check_failed':'Incorrect assumption that query_hash is invariant under storage-root relocation','existing_contract':'data/query.py digest explicitly includes SnapshotRef.root','correction':'Replay data rows/result hash; reconstruct original query hash using recorded original dataset root and fixed spec/provenance/cutoff','product_code_or_expected_financial_answers_changed':False,'original_failure_and_checker_retained':True})
write(DEST/'LOCAL_VERIFICATION.json',local_result)
assert git('show','-s','--format=%P',CODE).split()==['947467b9d094905cab0af37ec5cc53f1d187e755',MAIN]
write(DEST/'INTEGRATION_TOPOLOGY.json',{'previous_phase2_head':'947467b9d094905cab0af37ec5cc53f1d187e755','integrated_released_main':MAIN,'implementation_commit':CODE,'parents':git('show','-s','--format=%P',CODE).split(),'tree':git('rev-parse',CODE+'^{tree}'),'factor_code_bundle':local_result['receipt']['implementation_hash'],'package_version':'0.2.0 candidate; not released'})
write(DEST/'EVIDENCE_INDEX.json',{'performed_by':'Codex developer; not independent Gemini execution','implementation_sha':CODE,'integrated_main':MAIN,'local_run_id':local_result['environment']['run_id'],'tests_each':392,'original_external_regressions':16,'remote_run_id':json.loads((OUT/'remote_run.json').read_bytes())['id'],'artifacts':[{'id':r['artifact_id'],'sha256':r['zip_sha256'],'bytes':r['zip_bytes']} for r in remote_results],'local_windows_ubuntu_factor_results_and_data_query_match':True,'factor_code_approval':'ENGINEERING_APPROVED / TEST_ONLY / financial_approval NONE','gemini_new_sha_review':'REQUIRED','gemini_full_sdk_execution':'NOT VERIFIED','human_phase2_accepted':False,'phase2_main_merge_or_tag_authorized':False,'phase3_authorized':False})
print(json.dumps({'tests_each':392,'original_external':16,'raw_zips':'PASS','local_and_ci_data_and_factor_results':'PASS','selected_files_each':local_result['selected_hashes_verified']},indent=2))
