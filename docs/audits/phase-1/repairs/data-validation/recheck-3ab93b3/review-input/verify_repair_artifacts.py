import json,hashlib,zipfile,stat,sys,subprocess
from pathlib import Path,PureWindowsPath
from datetime import date,datetime,timezone
from xml.etree import ElementTree as ET
from aqrp.core.canonical import canonical
from aqrp.core.contracts import QuerySpec,SnapshotRef
from aqrp.data.snapshot import verify_snapshot
from aqrp.data.query import query
R=Path(__file__).resolve().parent;S=R/'source';B=S/'docs/audits/phase-1/repairs/data-validation/execution';REPO=Path(r'C:\Users\11638\AppData\Local\AQRP\reviews\p1-3ab93b3')
meta=json.loads((R/'github-business-artifacts.json').read_bytes())['structuredContent']['artifacts']
def sha(x):return hashlib.sha256(x).hexdigest()
checks=[];logical=[]
for item in meta:
    aid=item['id'];path=B/f'{aid}.zip';raw=path.read_bytes();assert len(raw)==item['size_in_bytes'] and 'sha256:'+sha(raw)==item['digest']
    out=R/'zip-replay'/str(aid);out.mkdir(parents=True)
    with zipfile.ZipFile(path) as z:
        assert z.testzip() is None
        assert len(z.infolist())<500 and sum(i.file_size for i in z.infolist())<30_000_000
        names=set()
        for i in z.infolist():
            n=i.filename;part=Path(n);assert n not in names and '\\' not in n and not part.is_absolute() and not PureWindowsPath(n).drive and '..' not in part.parts and not stat.S_ISLNK(i.external_attr>>16)
            names.add(n);target=(out/part).resolve();assert target.is_relative_to(out.resolve())
            if not i.is_dir():target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(z.read(i))
    base=next(out.glob('*/environment.json')).parent;env=json.loads((base/'environment.json').read_bytes())
    assert env['complete'] and not env['dirty'] and env['github_run_id']=='39612329694' and env['github_run_attempt']=='1'
    assert env['python'].startswith('3.13.16 ') and env['lock_sha256']==sha((S/'requirements.lock').read_bytes())
    topo=subprocess.check_output(['git','show','-s','--format=%H%n%P%n%T',env['code_commit']],cwd=REPO,text=True).strip().splitlines()
    assert topo[1].split()==['f579b2c99e762085772de6e70ba1fa98792a7add','cdb11cd913e965a43572ceb86efb0a39d1f618df']
    assert topo[2]==subprocess.check_output(['git','rev-parse','cdb11cd913e965a43572ceb86efb0a39d1f618df^{tree}'],cwd=REPO,text=True).strip()
    selection=json.loads((base/'upload-selection.json').read_bytes());listed={x['path']:x['sha256'] for x in selection['files']}
    assert len(listed)==len(selection['files'])
    actual={p.relative_to(base).as_posix() for p in base.rglob('*') if p.is_file()}
    assert actual==set(listed)|{'upload-selection.json'}
    for n,h in listed.items():assert sha((base/n).read_bytes())==h
    omitted=[];rootmatched=0
    for entry in json.loads((base/'artifacts.json').read_bytes()):
        p=base/entry['path']
        if entry['uploaded']:assert p.is_file() and sha(p.read_bytes())==entry['sha256'];rootmatched+=1
        else:assert not p.exists();omitted.append(entry['path'])
    assert set(omitted)==set(selection['omitted_local_tools'])
    assert (base/'.coverage').read_bytes().startswith(b'SQLite format 3')
    wheel=next((base/'wheel').glob('aqrp-*.whl'));assert sha(wheel.read_bytes())==env['wheel_sha256']
    source_code=list((S/'src').rglob('*.py'))
    with zipfile.ZipFile(wheel) as z:
        for p in source_code:assert z.read(p.relative_to(S/'src').as_posix())==p.read_bytes()
    suites=list(ET.fromstring((base/'junit.xml').read_bytes()).iter('testsuite'))
    junit={k:sum(int(s.attrib.get(k,0)) for s in suites) for k in ('tests','failures','errors','skipped')};assert junit==dict(tests=148,failures=0,errors=0,skipped=0)
    cov=subprocess.run([sys.executable,str(S/'tools/check_coverage.py'),str(base/'coverage.json')],capture_output=True,text=True);assert cov.returncode==0
    assert json.loads((base/'scan-findings.json').read_bytes())==[]
    config=json.loads((base/'smoke-config.json').read_bytes());receipt=json.loads((base/'smoke-run.json').read_bytes());assert sha(canonical(config))==receipt['config_hash']
    ref=SnapshotRef(base/'dataset',config['snapshot_id'],config['manifest_hash']);m,tables=verify_snapshot(ref);assert len(tables)==8
    assert sha(canonical({k:v for k,v in m.items() if k not in ('snapshot_id','manifest_hash')}))==config['manifest_hash']
    for _,entry in m['tables'].items():assert sha((base/'dataset'/config['snapshot_id']/entry['path']).read_bytes())==entry['sha256']
    spec=QuerySpec(tuple(config['security_ids']),config['market_id'],config['calendar_id'],tuple(date.fromisoformat(x) for x in config['session_range']))
    rows=query(spec,config['as_of'],ref).table.to_pylist();assert canonical(rows)==(base/'smoke-result.json').read_bytes() and sha(canonical(rows))==receipt['result_hash']
    logical.append((canonical({n:[{k:v for k,v in r.items() if k!='snapshot_id'} for r in t.to_pylist()] for n,t in tables.items()}),canonical(rows),canonical({k:v for k,v in config.items() if k not in ('snapshot_id','manifest_hash')})))
    checks.append(dict(artifact_id=aid,sha256=sha(raw),size=len(raw),environment=env,topology=topo,selected_file_hashes_matched=len(listed),root_uploaded_matched=rootmatched,omitted=omitted,wheel_hash=sha(wheel.read_bytes()),wheel_source_modules_matched=len(source_code),coverage_raw_bytes=True,junit=junit,module_coverage_gate=cov.stdout.strip(),eight_tables_and_sdk_replay='PASS'))
    print(aid,'PASS','selected',len(listed),'root',rootmatched,'JUnit',junit)
assert len(logical)==2 and logical[0]==logical[1]
(R/'zip-verification.json').write_text(json.dumps(dict(audit='GPT Work 补充审核',target_sha='3ab93b35c0b5e4e7b5e85c27f641748aa86cb24f',evidence_business_sha='cdb11cd913e965a43572ceb86efb0a39d1f618df',runtime=sys.version,executable=sys.executable,sdk_file=__import__('aqrp').__file__,time_utc=datetime.now(timezone.utc).isoformat(),results=checks,cross_os='PASS: eight logical tables, smoke bytes/config; snapshot_id and config manifest_hash exclusions explicit',gemini_execution='NOT VERIFIED; this is GPT Work execution',historical_missing_bytes='Remain NOT VERIFIED'),ensure_ascii=False,indent=2),encoding='utf-8')
print('Cross-OS logical data/config/result MATCH; original wheel and .coverage verified')
