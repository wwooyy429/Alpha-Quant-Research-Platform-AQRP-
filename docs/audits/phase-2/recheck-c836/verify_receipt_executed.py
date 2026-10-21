"""Developer receipt validation. This does not create or impersonate a new audit SDK run."""
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
from dataclasses import asdict
from datetime import date

from aqrp.core.canonical import canonical, digest
from aqrp.core.contracts import QuerySpec, SnapshotRef
from aqrp.core.time import utc
from aqrp.data.query import query
from aqrp.data.snapshot import verify_snapshot
from aqrp.factors import FactorEngine, FactorRegistry, builtin_spec

ROOT=pathlib.Path(r'C:\Users\11638\AppData\Local\AQRP\checkouts\phase1-57461d5d-5de2-4c78-9b4e-5fad2b5ccb29')
SRC=pathlib.Path(r'C:\Users\11638\AppData\Local\AQRP\reviews\work-p2-c836295')
OUT=pathlib.Path(__file__).parent
DEST=ROOT/'docs/audits/phase-2/recheck-c836'
TARGET='c8362953f555606795b6804cdfe28ff690c2364d'
MAIN='fb1ba4fd51202a303115e4449ee49db09ccc071c'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
git=lambda *a:subprocess.check_output(['git',*a],cwd=ROOT,text=True).strip()
def dump(p,obj):
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
def junit(p,count):
 s=ET.parse(p).getroot().find('testsuite')
 actual={k:int(s.attrib[k]) for k in ['tests','failures','errors','skipped']}
 assert actual=={'tests':count,'failures':0,'errors':0,'skipped':0},actual
 return actual

assert git('rev-parse','HEAD')==TARGET and not git('status','--porcelain')
manifest=json.loads((SRC/'REVIEW_EVIDENCE_MANIFEST.json').read_bytes())
assert manifest['target_sha']==TARGET
for e in manifest['files']:
 p=SRC/e['path'];assert p.stat().st_size==e['bytes'] and sha(p)==e['sha256'],p
for e in json.loads((ROOT/'docs/audits/phase-1/implementation/CORE_PRESERVATION.json').read_bytes())['files']:assert sha(ROOT/e['path'])==e['sha256']
for e in json.loads((ROOT/'docs/audits/phase-2/lineage-fix/FILE_MANIFEST.json').read_bytes())['files']:assert sha(ROOT/'docs/audits/phase-2/lineage-fix'/e['path'])==e['sha256']
old_index=json.loads((ROOT/'docs/audits/phase-2/lineage-fix/RECEIPT_INDEX.json').read_bytes())
oldsrc=pathlib.Path(r'C:\Users\11638\AppData\Local\AQRP\reviews\work-p2-c70727c')
for e in old_index['files']+old_index['omitted_files']:assert sha(oldsrc/e['path'])==e['sha256']
assert (SRC/'test_work_p2_regressions.py').read_bytes()==(oldsrc/'test_work_p2_regressions.py').read_bytes()
api=json.loads((OUT/'live-artifacts.json').read_bytes())
roots=[next((SRC/'runs').glob('aqrp-*'))]
for a in api['artifacts']:
 p=SRC/f"{a['id']}.zip";assert p.stat().st_size==a['size_in_bytes'] and sha(p)==a['digest'].removeprefix('sha256:')
 extract=next((SRC/'zip-replay'/str(a['id'])).glob('aqrp-*'))
 with zipfile.ZipFile(p) as z:
  assert z.testzip() is None and len(z.namelist())==len(set(z.namelist()))
  for i in z.infolist():
   path=pathlib.PurePosixPath(i.filename)
   assert not path.is_absolute() and '..' not in path.parts and '\\' not in i.filename and ':' not in i.filename and not stat.S_ISLNK(i.external_attr>>16)
   assert z.read(i.filename)==(extract.parent/i.filename).read_bytes()
 roots.append(extract)
ids=json.loads((SRC/'original-query-identity.json').read_bytes())['checks']
results=[];identity_checks=0
for run in roots:
 env=json.loads((run/'environment.json').read_bytes())
 assert env['complete'] and not env['dirty'] and env['python'].startswith('3.13.16')
 assert env['lock_sha256']==sha(ROOT/'requirements.lock')
 if run==roots[0]:assert env['code_commit']==TARGET
 else:
  assert env['github_run_id']=='39637043080' and env['github_run_attempt']=='1'
  assert git('show','-s','--format=%P',env['code_commit']).split()==[MAIN,TARGET]
 assert git('rev-parse',env['code_commit']+'^{tree}')==git('rev-parse',TARGET+'^{tree}')
 counts=junit(run/'junit.xml',417)
 selected=json.loads((run/'upload-selection.json').read_bytes())
 assert len(selected['files'])==46
 if run!=roots[0]:assert {p.relative_to(run).as_posix() for p in run.rglob('*') if p.is_file()}=={e['path'] for e in selected['files']}|{'upload-selection.json'}
 for e in selected['files']:assert sha(run/e['path'])==e['sha256']
 for e in json.loads((run/'artifacts.json').read_bytes()):
  if e['uploaded']:assert sha(run/e['path'])==e['sha256']
 wheel=next((run/'wheel').glob('aqrp-*.whl'));assert sha(wheel)==env['wheel_sha256']
 with zipfile.ZipFile(wheel) as z:
  for p in (ROOT/'src/aqrp').rglob('*.py'):assert z.read(p.relative_to(ROOT/'src').as_posix())==p.read_bytes()
  assert z.read('aqrp/factors/reviewed_code.json')==(ROOT/'src/aqrp/factors/reviewed_code.json').read_bytes()
 assert json.loads((run/'scan-findings.json').read_bytes())==[]
 cov=subprocess.run([sys.executable,str(ROOT/'tools/check_coverage.py'),str(run/'coverage.json')],capture_output=True,text=True);assert cov.returncode==0
 refs={};manifests={}
 for kind in ['dataset','factor-dataset']:
  m=next((run/kind).glob('*/manifest.json'));info=json.loads(m.read_bytes());ref=SnapshotRef(m.parent.parent,info['snapshot_id'],info['manifest_hash']);_,tables=verify_snapshot(ref);assert len(tables)==8;refs[kind]=ref;manifests[kind]=info
 c=json.loads((run/'smoke-config.json').read_bytes());s=QuerySpec(tuple(c['security_ids']),c['market_id'],c['calendar_id'],tuple(date.fromisoformat(d) for d in c['session_range']),tuple(c['fields']),c['price_basis']);v=query(s,c['as_of'],refs['dataset'])
 assert canonical(v.table.to_pylist())==(run/'smoke-result.json').read_bytes()
 smoke=json.loads((run/'smoke-run.json').read_bytes());item=next(x for x in ids if x['run_id']==env['run_id'] and x['kind']=='data');assert item['recorded_root']==smoke['dataset'];sc=asdict(s);del sc['request_id']
 expected=digest({'snapshot':asdict(refs['dataset'])|{'root':item['recorded_root']},'cutoff':utc(c['as_of']),'spec':sc,'rule_version':'pit/1.0.0','provenance':manifests['dataset']['provenance']});assert expected==item['query_hash']==smoke['query_hash'];identity_checks+=1
 registry=FactorRegistry();replayed=0
 for m in (run/'factor-runs').glob('*/manifest.json'):
  receipt=json.loads(m.read_bytes());assert receipt['status']=='SUCCEEDED' and receipt['financial_approval']=='NONE'
  for e in receipt['artifacts']:assert sha(m.parent/e['path'])==e['sha256']
  config=json.loads((m.parent/'config.json').read_bytes());name=config['spec']['factor_id'];spec=builtin_spec(name);registry.register(spec.implementation_version,spec,actor='developer-receipt',reason='fixed reviewed evidence replay',evidence=spec.review_ref)
  request=QuerySpec(tuple(config['security_ids']),config['market_id'],config['calendar_id'],(date(2024,1,2),date(2024,1,4)),('close','volume'),'split_adjusted')
  b=FactorEngine(registry).run(spec.ref,request,config['decision_time'],refs['factor-dataset'],parameters=dict(config['params']),run_id=config['run_id'],computation_id=config['computation_id'])
  assert canonical([asdict(row) for row in b.rows])==(m.parent/'signals.json').read_bytes()
  original=next(x for x in ids if x['run_id']==env['run_id'] and x['kind']==name);sc=asdict(request);del sc['request_id']
  expected=digest({'snapshot':asdict(refs['factor-dataset'])|{'root':original['recorded_root']},'cutoff':utc(config['decision_time']),'spec':sc,'rule_version':'pit/1.0.0','provenance':manifests['factor-dataset']['provenance']});assert expected==original['query_hash']==config['query_hash'];identity_checks+=1;replayed+=1
 assert replayed==3
 results.append({'run_id':env['run_id'],'code_commit':env['code_commit'],'junit':counts,'selected_hashes':46,'wheel_sha256':sha(wheel),'tables_each_dataset':8,'replayed_signals':3,'coverage_gate':'PASS'})
junit(SRC/'original16-junit.xml',16);junit(SRC/'new-probe-junit.xml',4)
assert identity_checks==12
DEST.mkdir(parents=True,exist_ok=False)
mapping=[];omitted=[]
for e in manifest['files']:
 p=SRC/e['path'];parts=pathlib.PurePosixPath(e['path']).parts
 if e['path']=='fixed-source.zip' or (parts[0]=='runs' and (p.name=='gitleaks.exe' or p.name.startswith('pip-'))):omitted.append(e|{'reason':'Hash/size verified; redundant fixed-source ZIP or pinned local tool remains outside repo, not claimed uploaded'});continue
 if parts[0]=='runs':rel=pathlib.Path('sdk').joinpath(*parts[2:])
 elif parts[0]=='zip-replay':rel=pathlib.Path('ci')/('win' if parts[1]=='12363130787' else 'linux')/pathlib.Path(*parts[3:])
 elif parts[0]=='new-probe-tmp':rel=pathlib.Path('roundtrip-run')/p.name
 else:rel=pathlib.Path('raw')/p.name
 dest=DEST/rel;assert not dest.exists();dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest);mapping.append(e|{'archive_path':rel.as_posix()})
shutil.copy2(SRC/'REVIEW_EVIDENCE_MANIFEST.json',DEST/'REVIEW_EVIDENCE_MANIFEST.json')
shutil.copy2(OUT/'live-artifacts.json',DEST/'LIVE_OFFICIAL_ARTIFACTS.json')
dump(DEST/'RECEIPT_INDEX.json',{'review_target':TARGET,'actual_reviewer':'GPT Work supplemental review, not Gemini','original_entries_verified':len(manifest['files']),'archived_files':len(mapping),'explicit_omissions':omitted,'files':mapping})
dump(DEST/'RECEIPT_VERIFICATION.json',{'scope':'Developer validates receipt/raw evidence and replays received datasets, not a new SDK audit execution','review_target':TARGET,'provided_manifest_entries_verified':len(manifest['files']),'provided_sdk_and_two_ci_runs':results,'original16':16,'original4':4,'original_query_identities_recomputed':12,'protected_assets':50,'previous_lineage_manifest_entries_verified':335,'previous_review_inputs_hash_verified':248,'original_probes_unchanged':True,'current_official_ci_artifact_digests':'MATCH both IDs','full_sdk_newly_run_by_receiver':False,'actual_report_reviewer':'GPT Work; external conversation identity not independently authenticated','conclusion':'Receipt supports supplemental technical PASS on fixed target; 001/002/003 closure scoped to this report; no human acceptance/release'})
print(json.dumps({'received':len(manifest['files']),'archived':len(mapping),'omitted':len(omitted),'sdk_and_ci_each':417,'external16_and4':'PASS','three_signal_replays_each':'PASS','original_query_hashes':identity_checks},indent=2))
