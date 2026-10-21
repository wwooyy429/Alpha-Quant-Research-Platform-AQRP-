"""Developer verification of received original CI bytes; not an independent Gemini audit."""
import csv, hashlib, json, pathlib, shutil, stat, subprocess, sys, xml.etree.ElementTree as ET, zipfile
from datetime import datetime, timezone
from aqrp.core.contracts import SnapshotRef
from aqrp.data.snapshot import verify_snapshot

ROOT=pathlib.Path(r'C:\Users\11638\AppData\Local\AQRP\checkouts\phase1-57461d5d-5de2-4c78-9b4e-5fad2b5ccb29')
RUN=pathlib.Path(__file__).resolve().parent
DEST=ROOT/'docs/audits/phase-2/implementation'
CODE='8183b3762b56c466b989d9062a720b5f0d31172a'
BASE='f579b2c99e762085772de6e70ba1fa98792a7add'
PLAN='4f8b0de01b5991ef172f52f6a81e64b855a32d68'
sha=lambda b:hashlib.sha256(b).hexdigest()
def write(path,obj):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(obj,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
def git(*args):
    return subprocess.check_output(['git',*args],cwd=ROOT)
def junit(path):
    r=ET.parse(path).getroot()
    suites=[r] if r.tag=='testsuite' else list(r.findall('testsuite'))
    result={k:sum(int(s.attrib.get(k,0)) for s in suites) for k in ('tests','failures','errors','skipped')}
    assert result==dict(tests=254,failures=0,errors=0,skipped=0),result
    return result
def verify_run(root,remote=False):
    env=json.loads((root/'environment.json').read_bytes())
    assert env['complete'] is True and env['dirty'] is False
    assert env['lock_sha256']==sha((ROOT/'requirements.lock').read_bytes())
    actual=env['code_commit']
    assert git('rev-parse',f'{actual}^{{tree}}')==git('rev-parse',f'{CODE}^{{tree}}')
    parents=git('show','-s','--format=%P',actual).decode().split()
    if remote: assert parents==[BASE,CODE],parents
    else: assert actual==CODE
    sel=json.loads((root/'upload-selection.json').read_bytes())
    inventory=json.loads((root/'artifacts.json').read_bytes())
    paths={p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file()}
    if remote:
        assert paths=={x['path'] for x in sel['files']}|{'upload-selection.json'},paths
    for item in sel['files']:
        assert sha((root/item['path']).read_bytes())==item['sha256'],item
    for item in inventory:
        if item['uploaded']:
            assert sha((root/item['path']).read_bytes())==item['sha256']
        elif remote: assert item['path'] not in paths
    wheel=next((root/'wheel').glob('aqrp-*.whl'))
    assert sha(wheel.read_bytes())==env['wheel_sha256']
    scan=json.loads((root/'scan-findings.json').read_bytes())
    assert scan==[]
    snapshots=[]
    for kind in ('dataset','factor-dataset'):
        m=next((root/kind).glob('*/manifest.json'))
        info=json.loads(m.read_bytes())
        ref=SnapshotRef(m.parent.parent,info['snapshot_id'],info['manifest_hash'])
        verify_snapshot(ref)
        snapshots.append({'kind':kind,'snapshot_id':info['snapshot_id'],'manifest_hash':info['manifest_hash'],'tables':len(info['tables']),'result':'PASS'})
    manifests=[]
    for m in sorted((root/'factor-runs').glob('*/manifest.json')):
        info=json.loads(m.read_bytes())
        assert info['mode']=='TEST_ONLY' and info['financial_approval']=='NONE' and info['status']=='SUCCEEDED'
        for item in info['artifacts']:
            assert sha((m.parent/item['path']).read_bytes())==item['sha256']
        manifests.append({'run_id':info['run_id'],'logical_hash':info['logical_hash'],'artifacts':len(info['artifacts'])})
    result=json.loads((root/'factor-result.json').read_bytes())
    assert {k:v['value'] for k,v in result.items()}=={'momentum':.21,'reversal':-.21,'volume':.6}
    cov=json.loads((root/'coverage.json').read_bytes())
    cp=subprocess.run([sys.executable,str(ROOT/'tools/check_coverage.py'),str(root/'coverage.json')],capture_output=True,text=True)
    assert cp.returncode==0,cp.stdout+cp.stderr
    return {'environment':env,'junit':junit(root/'junit.xml'),'coverage_totals':cov['totals'],'coverage_gate':cp.stdout.strip(),'checkout_parents':parents,'checkout_tree':git('rev-parse',f'{actual}^{{tree}}').decode().strip(),'implementation_tree':git('rev-parse',f'{CODE}^{{tree}}').decode().strip(),'checkout_tree_matches_implementation':True,'selected_files_verified':len(sel['files']),'explicit_omissions':sel['omitted_local_tools'],'snapshots':snapshots,'factor_runs':manifests,'factor_result':result,'root_inventory_verified':True,'wheel_sha256_verified':True,'secret_findings':0}
DEST.mkdir(parents=True,exist_ok=True)
api=json.loads((RUN/'remote/api-artifacts.json').read_bytes())
remote=[]
for name in ('ubuntu','windows'):
    src=RUN/'remote'/f'{name}.zip'
    meta=next(x for x in api['artifacts'] if name in x['name'])
    digest=sha(src.read_bytes())
    assert digest==meta['digest'].removeprefix('sha256:')
    assert src.stat().st_size==meta['size_in_bytes']
    with zipfile.ZipFile(src) as z:
        assert z.testzip() is None
        assert len(z.namelist())==len(set(z.namelist()))
        for item in z.infolist():
            p=pathlib.PurePosixPath(item.filename)
            assert not p.is_absolute() and '..' not in p.parts and '\\' not in item.filename and ':' not in item.filename
            assert not stat.S_ISLNK(item.external_attr>>16)
            assert item.file_size<10_000_000
        assert sum(x.file_size for x in z.infolist())<30_000_000
        extraction=RUN/'remote/extracted'/name
        extraction.mkdir(parents=True,exist_ok=True)
        z.extractall(extraction)
    rr=next(x for x in extraction.iterdir() if x.is_dir())
    evidence=verify_run(rr,True)
    evidence.update(artifact_id=meta['id'],artifact_name=meta['name'],raw_zip_sha256=digest,raw_zip_bytes=src.stat().st_size,zip_safe_paths_and_crc='PASS',performed_by='Codex developer; original GitHub hosted-runner evidence, not Gemini')
    out=DEST/'ci'
    out.mkdir(exist_ok=True)
    shutil.copyfile(src,out/f"{meta['id']}-{name}.zip")
    write(out/f'{name}-verification.json',evidence)
    remote.append(evidence)
for f in ('api-artifacts.json','api-jobs.json','download-result.json'):
    shutil.copyfile(RUN/'remote'/f,DEST/'ci'/f)
local=next((RUN/'formal').glob('aqrp-*'))
local_result=verify_run(local)
selected=json.loads((local/'upload-selection.json').read_bytes())['files']
copied=[]
for item in selected+[{'path':'upload-selection.json'}]:
    rel=item['path']
    rename={'.coverage':'coverage.sqlite','coverage.xml':'coverage-report.xml'}
    to=DEST/'local'/rename.get(rel,rel)
    to.parent.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(local/rel,to)
    copied.append({'source_relative_path':rel,'archive_relative_path':to.relative_to(DEST).as_posix(),'sha256':sha(to.read_bytes())})
write(DEST/'local-archive-map.json',{'source_run_id':local.name,'policy':'Exact selected raw files preserved; only two filenames renamed to avoid ignore rules. venv/cache/source/tool binaries omitted. Original formal run retained outside repository. Raw tool hashes and explicit omissions remain in artifacts.json.','files':copied})
shutil.copyfile(RUN/'formal-sdk.log',DEST/'local'/'driver.log')
write(DEST/'local-verification.json',local_result)
assert all(r['factor_result']==local_result['factor_result'] for r in remote)
development=DEST/'development'
development.mkdir(exist_ok=True)
for f in ('dev-tests.log','dev-junit.xml','dev-coverage.json','dev2-tests.log','dev2-junit.xml','dev2-coverage.json'):
    shutil.copyfile(RUN/f,development/f)
write(DEST/'EVIDENCE_INDEX.json',{
'generated_at_utc':datetime.now(timezone.utc).isoformat(),'performed_by':'Codex developer; not independent Gemini execution',
'status':'IMPLEMENTATION REVIEW REQUIRED','implementation_commit':CODE,'gemini_plan_review_commit':PLAN,'gemini_plan_verdict':'PLAN PASS','gemini_implementation_verdict':'NOT RECEIVED',
'raw_report_sha256':'5b6abe40bc78d088b40f19f883ddd0cfe551c52c6b625c8f6606c28a590aa35e','gemini_named_raw_math_script_log_received':False,
'local_formal_run':local.name,'local_formal_wheel_sha256':local_result['environment']['wheel_sha256'],'local_junit':local_result['junit'],'coverage_totals':local_result['coverage_totals'],
'remote_workflow_run_id':39590967220,'remote_run_attempt':1,'remote_jobs':{'ubuntu':119191513902,'windows':119191514330},'remote_original_zip_verification':'PASS','remote_junit_each':{'tests':254,'failures':0,'errors':0,'skipped':0},'cross_os_and_local_logical_results':'PASS',
'archive_policy':'local-archive-map.json; ci/*-verification.json. Scanner/bootstrap binaries intentionally omitted, no original bytes falsely claimed. Does not repair historical Phase1 missing bytes.',
'main_and_phase1_baseline':BASE,'human_accepted':False,'merge_authorized':False,'tag_authorized':False,'phase3_authorized':False})
print(json.dumps({'local':local_result['junit'],'remote_zip_checks':'PASS','cross_os_logical_results':'PASS','archive':str(DEST)},ensure_ascii=False))

