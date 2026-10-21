"""User-authorized substitute execution; no formal repository mutations."""
import hashlib
import importlib.metadata as metadata
import io
import json
import os
import platform
import re
import stat
import struct
import subprocess
import sys
import sysconfig
import zipfile
from datetime import date, datetime
from pathlib import Path, PurePosixPath, PureWindowsPath
from xml.etree import ElementTree as ET

from packaging.requirements import Requirement
import aqrp
from aqrp.core.canonical import canonical
from aqrp.core.contracts import QuerySpec, SnapshotRef
from aqrp.data.query import query
from aqrp.data.snapshot import verify_snapshot

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent / 'p1-31a548b'
RUN = next((ROOT/'runs').iterdir())
SOURCE = RUN/'source'
TARGET = '31a548b8790bc1abe0f5ffbe3c55e10917a9503e'
BASE = 'f579b2c99e762085772de6e70ba1fa98792a7add'
MERGE = 'fa1d53620be60d683538b428a2a9cd29035b0127'
sha = lambda data: hashlib.sha256(data).hexdigest()
result = {'executor':'GPT Work / user-designated substitute, not Gemini', 'target_sha':TARGET,
          'started_at':datetime.now().astimezone().isoformat(), 'checks':{}}

def load(path):
    return json.loads(Path(path).read_bytes())

def command(name, args, cwd=ROOT, expected=0):
    runenv=os.environ.copy()
    runenv.pop('PYTHONPATH',None)
    runenv.update(PYTHONPYCACHEPREFIX=str(ROOT/'extra-bytecode'),
                  HYPOTHESIS_STORAGE_DIRECTORY=str(ROOT/'extra-hypothesis'),
                  PYTHONUTF8='1')
    with (ROOT/(name+'.stdout.log')).open('wb') as stdout, (ROOT/(name+'.stderr.log')).open('wb') as stderr:
        r=subprocess.run([str(x) for x in args],cwd=cwd,env=runenv,stdout=stdout,stderr=stderr)
    (ROOT/(name+'.exit.txt')).write_text(str(r.returncode)+'\n')
    with (ROOT/'verification-commands.jsonl').open('a',encoding='utf-8') as log:
        log.write(json.dumps({'name':name,'argv':[str(x) for x in args],'cwd':str(cwd),
                              'exit_code':r.returncode,'expected_exit':expected},ensure_ascii=False)+'\n')
    assert r.returncode==expected, (name,r.returncode)

def junit(path):
    root=ET.fromstring(Path(path).read_bytes())
    suites=[root] if root.tag=='testsuite' else root.findall('testsuite')
    return {k:sum(int(s.get(k,0)) for s in suites) for k in ('tests','failures','errors','skipped')}

def safe(name):
    assert name and '\\' not in name and not PureWindowsPath(name).drive
    assert not PurePosixPath(name).is_absolute() and '..' not in PurePosixPath(name).parts
    return name

def snapshot_and_replay(base):
    config=load(base/'smoke-config.json'); receipt=load(base/'smoke-run.json')
    assert sha(canonical(config))==receipt['config_hash']
    reference=SnapshotRef(base/'dataset',config['snapshot_id'],config['manifest_hash'])
    manifest,tables=verify_snapshot(reference)
    assert len(tables)==8
    projection={k:v for k,v in manifest.items() if k not in ('snapshot_id','manifest_hash')}
    independent_digest=sha(json.dumps(projection,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode())
    assert independent_digest==config['manifest_hash']==manifest['manifest_hash']
    for item in manifest['tables'].values():
        assert sha((base/'dataset'/config['snapshot_id']/safe(item['path'])).read_bytes())==item['sha256']
    spec=QuerySpec(tuple(config['security_ids']),config['market_id'],config['calendar_id'],
                   tuple(date.fromisoformat(d) for d in config['session_range']))
    rows=query(spec,config['as_of'],reference).table.to_pylist()
    assert canonical(rows)==(base/'smoke-result.json').read_bytes()
    assert sha(canonical(rows))==receipt['result_hash']
    logical=canonical({name:[{k:v for k,v in row.items() if k!='snapshot_id'}
                              for row in table.to_pylist()] for name,table in tables.items()})
    comparable_config=canonical({k:v for k,v in config.items() if k not in ('snapshot_id','manifest_hash')})
    return (logical,canonical(rows),comparable_config), {'tables':len(tables),'rows':{k:len(v) for k,v in tables.items()},
                                                      'manifest_digest':independent_digest,'query_result_hash':receipt['result_hash']}

try:
    assert sys.version_info[:3]==(3,13,16) and struct.calcsize('P')*8==64
    assert not sysconfig.get_config_var('Py_GIL_DISABLED')
    assert 'site-packages' in aqrp.__file__ and Path(aqrp.__file__).resolve().is_relative_to(RUN.resolve())
    env=load(RUN/'environment.json')
    assert env['code_commit']==TARGET and env['complete'] and not env['dirty']
    assert (ROOT/'sdk.exit.txt').read_text().strip()=='0'
    command('fixed-git-status',['git','--no-optional-locks','status','--porcelain=v1'],cwd=REPO)
    assert not (ROOT/'fixed-git-status.stdout.log').read_text().strip()
    assert env['lock_sha256']==sha((SOURCE/'requirements.lock').read_bytes())
    assert junit(RUN/'junit.xml')==dict(tests=234,failures=0,errors=0,skipped=0)
    installed=Path(aqrp.__file__).resolve().parent
    modules=list((SOURCE/'src/aqrp').rglob('*.py'))
    wheel=next((RUN/'wheel').glob('aqrp-*.whl'))
    assert sha(wheel.read_bytes())==env['wheel_sha256']
    with zipfile.ZipFile(wheel) as z:
        for p in modules:
            assert p.read_bytes()==(installed/p.relative_to(SOURCE/'src/aqrp')).read_bytes()
            assert p.read_bytes()==z.read(p.relative_to(SOURCE/'src').as_posix())
    assert len(modules)==17
    active=[]
    for line in (SOURCE/'requirements.lock').read_text().splitlines():
        if line and not line[0].isspace() and not line.startswith('#'):
            req=Requirement(line.rstrip('\\').strip())
            if req.marker is None or req.marker.evaluate():
                actual=metadata.version(req.name)
                assert req.specifier.contains(actual), (req.name,actual)
                active.append({'name':req.name,'version':actual})
    assert len(active)==22
    for entry in load(RUN/'artifacts.json'):
        assert sha((RUN/safe(entry['path'])).read_bytes())==entry['sha256']
    for entry in load(RUN/'upload-selection.json')['files']:
        assert sha((RUN/safe(entry['path'])).read_bytes())==entry['sha256']
    local_logical,local_snapshot=snapshot_and_replay(RUN)
    result['checks']['new_local_sdk']={'environment':env,'junit':junit(RUN/'junit.xml'),
        'active_locked_packages':active,'installed_module_matches':17,'wheel_matches_source':True,
        'runtime':sys.version,'executable':sys.executable,'sdk_file':aqrp.__file__,
        'standard_gil':True,'pointer_bits':64,'snapshot_replay':local_snapshot}

    prior=load(ROOT.parent/'work-p1-recheck-3ab93b3/verification-summary.json')
    for item in prior['original_unchanged_test_hashes']:
        assert sha(Path(item['path']).read_bytes())==item['sha256']
    test_paths=[Path(item['path']) for item in prior['original_unchanged_test_hashes']]
    fixture_paths=[test_paths[0].parent/'phase1/tests/golden/phase1_input.json',
                   test_paths[1].parent/'source/tests/golden/phase1_input.json']
    for p in fixture_paths: assert p.read_bytes()==(SOURCE/'tests/golden/phase1_input.json').read_bytes()
    command('original16',[sys.executable,'-m','pytest','-q','-o',f'cache_dir={ROOT/"extra-pytest-cache"}',
                         '--basetemp',ROOT/'extra-tmp',f'--junitxml={ROOT/"original16-junit.xml"}',*test_paths])
    assert junit(ROOT/'original16-junit.xml')==dict(tests=16,failures=0,errors=0,skipped=0)
    result['checks']['original16']={'junit':junit(ROOT/'original16-junit.xml'),
        'original_unchanged_test_hashes':prior['original_unchanged_test_hashes'],
        'golden_fixtures_equal_target':True}

    command('git-ci-topology',['git','--no-optional-locks','show','-s','--format=%H%n%P%n%T',MERGE],cwd=REPO)
    topology=(ROOT/'git-ci-topology.stdout.log').read_text().strip().splitlines()
    command('git-target-tree',['git','--no-optional-locks','rev-parse',TARGET+'^{tree}'],cwd=REPO)
    assert topology[0]==MERGE and topology[1].split()==[BASE,TARGET]
    assert topology[2]==(ROOT/'git-target-tree.stdout.log').read_text().strip()
    result['checks']['actual_git_topology']={'commit':MERGE,'parents':topology[1].split(),'tree':topology[2],
                                           'equals_target_tree':True,'not_a_main_merge':True}

    comparisons=[];zipchecks=[]
    for item in load(ROOT/'github-target-artifacts.json')['structuredContent']['artifacts']:
        assert item['workflow_run']['head_sha']==TARGET and item['workflow_run']['id']==39620574953
        aid=item['id']; archive=ROOT/f'{aid}.zip'; raw=archive.read_bytes()
        assert len(raw)==item['size_in_bytes'] and 'sha256:'+sha(raw)==item['digest']
        output=ROOT/'zip-replay'/str(aid); output.mkdir(parents=True)
        with zipfile.ZipFile(io.BytesIO(raw)) as z:
            assert z.testzip() is None and len(z.infolist())<500
            assert sum(i.file_size for i in z.infolist())<30_000_000
            names=set()
            for entry in z.infolist():
                name=safe(entry.filename)
                assert name not in names and not stat.S_ISLNK(entry.external_attr>>16)
                names.add(name)
                p=(output/name).resolve(); assert p.is_relative_to(output.resolve())
                if not entry.is_dir():
                    p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(z.read(entry))
        base=next(output.glob('*/environment.json')).parent
        cenv=load(base/'environment.json')
        assert cenv['complete'] and not cenv['dirty'] and cenv['code_commit']==MERGE
        assert cenv['github_sha']==MERGE and cenv['github_run_id']=='39620574953' and cenv['github_run_attempt']=='1'
        assert cenv['python'].startswith('3.13.16 ') and cenv['lock_sha256']==env['lock_sha256']
        selection=load(base/'upload-selection.json')
        listed={safe(i['path']):i['sha256'] for i in selection['files']}
        assert len(listed)==len(selection['files'])==23
        actual={p.relative_to(base).as_posix() for p in base.rglob('*') if p.is_file()}
        assert actual==set(listed)|{'upload-selection.json'}
        for p,h in listed.items(): assert sha((base/p).read_bytes())==h
        rootmatched=0;omitted=[]
        for entry in load(base/'artifacts.json'):
            p=base/safe(entry['path'])
            if entry['uploaded']:
                assert p.is_file() and sha(p.read_bytes())==entry['sha256'];rootmatched+=1
            else:
                assert not p.exists();omitted.append(entry['path'])
        assert rootmatched==12 and set(omitted)==set(selection['omitted_local_tools']) and len(omitted)==2
        assert (base/'.coverage').read_bytes().startswith(b'SQLite format 3')
        ciwheel=next((base/'wheel').glob('aqrp-*.whl'))
        assert sha(ciwheel.read_bytes())==cenv['wheel_sha256']
        with zipfile.ZipFile(ciwheel) as z:
            for p in modules: assert z.read(p.relative_to(SOURCE/'src').as_posix())==p.read_bytes()
        assert junit(base/'junit.xml')==dict(tests=234,failures=0,errors=0,skipped=0)
        command('coverage-'+str(aid),[sys.executable,SOURCE/'tools/check_coverage.py',base/'coverage.json'])
        assert load(base/'scan-findings.json')==[]
        comparable,snapshot=snapshot_and_replay(base);comparisons.append(comparable)
        zipchecks.append({'artifact_id':aid,'name':item['name'],'sha256':sha(raw),'bytes':len(raw),
            'environment':cenv,'zip_files':len(actual),'selected_hashes_matched':23,'root_hashes_matched':12,
            'explicit_omitted_tools':omitted,'wheel_source_modules_matched':17,'wheel_hash':sha(ciwheel.read_bytes()),
            'coverage_raw_sqlite':True,'coverage_gate':'PASS','junit':junit(base/'junit.xml'),'snapshot_replay':snapshot})
        print('Original ZIP',aid,'hash/internal files/wheel/coverage/8 tables/query PASS',flush=True)
    assert len(comparisons)==2 and comparisons[0]==comparisons[1]==local_logical
    result['checks']['current_raw_ci_zip']=zipchecks
    result['checks']['cross_os_and_new_local_match']={'status':'PASS',
        'compared':'all eight logical tables, query rows and config',
        'exclusions':'snapshot_id in table rows; snapshot_id and manifest_hash in config only',
        'scope':'Windows and Ubuntu original CI evidence replayed using newly installed Windows SDK; not a new Linux installation'}
    command('final-git-status',['git','--no-optional-locks','status','--porcelain=v1'],cwd=REPO)
    assert not (ROOT/'final-git-status.stdout.log').read_text().strip()
    result['status']='PASS'
except BaseException as exc:
    result['status']='FAIL';result['error']=repr(exc)
    raise
finally:
    result['finished_at']=datetime.now().astimezone().isoformat()
    (ROOT/'execution-verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'status':result.get('status'),'checks':list(result['checks']),'error':result.get('error')},ensure_ascii=False),flush=True)
