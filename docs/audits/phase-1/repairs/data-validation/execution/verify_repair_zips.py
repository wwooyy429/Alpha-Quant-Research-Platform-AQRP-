"""Developer execution: original GitHub ZIP bytes, exact selection, SDK replay."""
import hashlib
import io
import json
import stat
import subprocess
import sys
import zipfile
from datetime import date, datetime, timezone
from pathlib import Path, PurePosixPath, PureWindowsPath
from xml.etree import ElementTree as ET

from aqrp.core.canonical import canonical
from aqrp.core.contracts import QuerySpec, SnapshotRef
from aqrp.data.query import query
from aqrp.data.snapshot import verify_snapshot

ROOT = Path(__file__).resolve().parent
REPO = Path(r'C:\Users\11638\AppData\Local\AQRP\checkouts\p1-fix-20261021')
BUSINESS = 'cdb11cd913e965a43572ceb86efb0a39d1f618df'
BASE = 'f579b2c99e762085772de6e70ba1fa98792a7add'
meta = json.loads((ROOT/'github-metadata.json').read_bytes())
assert meta['run']['head_sha'] == BUSINESS and meta['run']['conclusion'] == 'success'
assert len(meta['jobs']['jobs']) == 2
assert all(j['conclusion']=='success' for j in meta['jobs']['jobs'])

def sha(data): return hashlib.sha256(data).hexdigest()
def git(*args): return subprocess.check_output(['git',*args],cwd=REPO).decode().strip()

results=[]; logical=[]
for artifact in meta['artifacts']:
    aid=artifact['id']; raw=(ROOT/f'{aid}.zip').read_bytes()
    assert len(raw)==artifact['size_in_bytes']
    assert 'sha256:'+sha(raw)==artifact['digest']
    assert artifact['workflow_run']['head_sha']==BUSINESS
    dest=(ROOT/'zip-replay'/str(aid)); dest.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        assert archive.testzip() is None
        assert len(archive.infolist()) < 500 and sum(x.file_size for x in archive.infolist())<30_000_000
        names=set()
        for item in archive.infolist():
            name=item.filename; part=PurePosixPath(name)
            assert name not in names and '\\' not in name and not part.is_absolute()
            assert not PureWindowsPath(name).drive and '..' not in part.parts
            assert not stat.S_ISLNK(item.external_attr>>16)
            names.add(name); target=(dest/Path(*part.parts)).resolve()
            assert target.is_relative_to(dest.resolve())
            if not item.is_dir(): target.parent.mkdir(parents=True,exist_ok=True); target.write_bytes(archive.read(item))
    environments=list(dest.glob('*/environment.json')); assert len(environments)==1
    base=environments[0].parent; env=json.loads(environments[0].read_bytes())
    assert env['complete'] and not env['dirty'] and env['python'].startswith('3.13.16 ')
    assert env['github_run_id']==str(meta['run']['id']) and env['github_run_attempt']=='1'
    checkout=env['code_commit']; topology=git('show','-s','--format=%H%n%P%n%T',checkout).splitlines()
    assert topology[1].split()==[BASE,BUSINESS]
    assert topology[2]==git('rev-parse',BUSINESS+'^{tree}')
    assert env['github_sha']==checkout
    assert env['lock_sha256']==sha((REPO/'requirements.lock').read_bytes())
    selection=json.loads((base/'upload-selection.json').read_bytes())
    assert selection['self_excluded'] is True
    listed={f['path']:f['sha256'] for f in selection['files']}
    actual={p.relative_to(base).as_posix() for p in base.rglob('*') if p.is_file()}
    assert actual == set(listed)|{'upload-selection.json'}
    assert len(listed)==len(selection['files'])
    for path,digest in listed.items(): assert sha((base/path).read_bytes())==digest,path
    inventory=json.loads((base/'artifacts.json').read_bytes()); omitted=[]; root_matched=0
    for entry in inventory:
        path=base/entry['path']
        if entry['uploaded']:
            assert path.is_file() and sha(path.read_bytes())==entry['sha256']
            root_matched+=1
        else:
            assert not path.exists(); omitted.append(entry['path'])
    assert set(omitted)==set(selection['omitted_local_tools'])
    assert set(omitted)=={'gitleaks.exe' if 'windows' in artifact['name'] else 'gitleaks','pip-26.2.1-py3-none-any.whl'}
    assert (base/'.coverage').read_bytes().startswith(b'SQLite format 3')
    wheels=list((base/'wheel').glob('aqrp-*.whl')); assert len(wheels)==1
    wheel=wheels[0]; assert wheel.name=='aqrp-0.1.1-py3-none-any.whl'
    assert sha(wheel.read_bytes())==env['wheel_sha256']
    with zipfile.ZipFile(wheel) as archive:
        assert b'Version: 0.1.1' in archive.read('aqrp-0.1.1.dist-info/METADATA')
        source_names=set(git('ls-tree','-r','--name-only',BUSINESS,'src/aqrp').splitlines())
        assert {n for n in archive.namelist() if n.startswith('aqrp/') and n.endswith('.py')}=={n[4:] for n in source_names if n.endswith('.py')}
        for path in source_names:
            if path.endswith('.py'):
                expected=subprocess.check_output(['git','show',f'{BUSINESS}:{path}'],cwd=REPO)
                assert archive.read(path[4:])==expected,path
    suites=list(ET.fromstring((base/'junit.xml').read_bytes()).iter('testsuite'))
    junit={k:sum(int(s.attrib.get(k,0)) for s in suites) for k in ('tests','failures','errors','skipped')}
    assert junit==dict(tests=148,failures=0,errors=0,skipped=0)
    coverage=subprocess.run([sys.executable,str(REPO/'tools/check_coverage.py'),str(base/'coverage.json')],capture_output=True,text=True)
    assert coverage.returncode==0,coverage.stdout+coverage.stderr
    assert json.loads((base/'scan-findings.json').read_bytes())==[]
    config=json.loads((base/'smoke-config.json').read_bytes()); receipt=json.loads((base/'smoke-run.json').read_bytes())
    assert sha(canonical(config))==receipt['config_hash']
    ref=SnapshotRef(base/'dataset',config['snapshot_id'],config['manifest_hash'])
    manifest,tables=verify_snapshot(ref)
    assert len(tables)==8
    sealed=base/'dataset'/config['snapshot_id']
    assert (sealed/'manifest.json').read_bytes()==(base/'smoke-snapshot.json').read_bytes()
    assert sha(canonical({k:v for k,v in manifest.items() if k not in ('snapshot_id','manifest_hash')}))==config['manifest_hash']
    for name,entry in manifest['tables'].items(): assert sha((sealed/entry['path']).read_bytes())==entry['sha256'],name
    spec=QuerySpec(tuple(config['security_ids']),config['market_id'],config['calendar_id'],tuple(date.fromisoformat(x) for x in config['session_range']))
    rows=query(spec,config['as_of'],ref).table.to_pylist()
    assert canonical(rows)==(base/'smoke-result.json').read_bytes()
    assert sha(canonical(rows))==receipt['result_hash']
    assert receipt['fixture_sha256']==sha((REPO/'tests/golden/phase1_input.json').read_bytes())
    logical.append((canonical({n:[{k:v for k,v in row.items() if k!='snapshot_id'} for row in table.to_pylist()] for n,table in tables.items()}),canonical(rows),canonical({k:v for k,v in config.items() if k not in ('snapshot_id','manifest_hash')})))
    result={'artifact_id':aid,'name':artifact['name'],'sha256':sha(raw),'bytes':len(raw),'environment':env,'checkout_topology':topology,'checkout_tree_matches_business':True,'selected_files_verified':len(listed),'unlisted_files':[],'root_inventory_uploaded_verified':root_matched,'root_inventory_omitted':omitted,'wheel_sha256_matches_installed_receipt':True,'wheel_code_bytes_match_business':True,'coverage_raw_bytes_present':True,'junit':junit,'module_coverage_gate':coverage.stdout.strip(),'tables_verified':len(tables),'independent_manifest_hash':'PASS','installed_SDK_query_replay':'PASS'}
    results.append(result); print(aid,'PASS',junit,'selection',len(listed),'root',root_matched,'omitted',omitted)
assert len(logical)==2 and logical[0]==logical[1]
result={'executor':'Codex developer; NOT Gemini independent execution','business_sha':BUSINESS,'time_utc':datetime.now(timezone.utc).isoformat(),'command':[sys.executable,str(Path(__file__))],'results':results,'cross_os':'MATCH: 8 logical tables, smoke rows/config; only snapshot_id and manifest_hash excluded where appropriate','historical_missing_bytes':'NOT VERIFIED; new evidence does not recreate old bytes'}
(ROOT/'zip-verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Both OS raw ZIPs and SDK replay PASS')
