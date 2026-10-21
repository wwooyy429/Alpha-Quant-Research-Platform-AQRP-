import csv, hashlib, io, json, os, stat, struct, subprocess, sys, sysconfig, zipfile
import importlib.metadata as metadata
from dataclasses import asdict
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path, PurePosixPath, PureWindowsPath
from xml.etree import ElementTree as ET
from packaging.requirements import Requirement
import aqrp
from aqrp.core.canonical import canonical, digest
from aqrp.core.contracts import QuerySpec, SnapshotRef
from aqrp.data.snapshot import verify_snapshot
from aqrp.data.query import query
from aqrp.factors import FactorEngine, FactorRegistry, Signal, SignalBatch, builtin_spec
from aqrp.factors.admission import bundle_hash, reviewed_policy

ROOT=Path(__file__).resolve().parent
REPO=ROOT.parent/'p2-c836295'
RUN=next((ROOT/'runs').iterdir()); SOURCE=RUN/'source'
TARGET='c8362953f555606795b6804cdfe28ff690c2364d'
BASE='fb1ba4fd51202a303115e4449ee49db09ccc071c'
MERGE='d1feaae218b25741e57fdfa024c0072f87f32e67'
sha=lambda b:hashlib.sha256(b).hexdigest()
load=lambda p:json.loads(Path(p).read_bytes())
summary={'audit':'GPT Work 补充审核','target_sha':TARGET,'started_at':datetime.now().astimezone().isoformat(),'checks':{}}

def command(name,args,cwd=ROOT):
    with (ROOT/(name+'.stdout.log')).open('wb') as stdout,(ROOT/(name+'.stderr.log')).open('wb') as stderr:
        p=subprocess.run([str(x) for x in args],cwd=cwd,stdout=stdout,stderr=stderr)
    (ROOT/(name+'.exit.txt')).write_text(str(p.returncode)+'\n')
    with (ROOT/'verification-commands.jsonl').open('a',encoding='utf-8') as log:
        log.write(json.dumps({'name':name,'argv':[str(x) for x in args],'cwd':str(cwd),'exit_code':p.returncode},ensure_ascii=False)+'\n')
    assert p.returncode==0,(name,p.returncode)
    return (ROOT/(name+'.stdout.log')).read_bytes()

def junit(path):
    r=ET.fromstring(Path(path).read_bytes()); suites=[r] if r.tag=='testsuite' else r.findall('testsuite')
    return {k:sum(int(s.get(k,0)) for s in suites) for k in ('tests','failures','errors','skipped')}

def safe(p):
    assert p and '\\' not in p and not PurePosixPath(p).is_absolute() and not PureWindowsPath(p).drive
    assert '..' not in PurePosixPath(p).parts
    return p

def verify_run(base,remote=False):
    env=load(base/'environment.json')
    assert env['complete'] and not env['dirty'] and env['python'].startswith('3.13.16 ')
    assert env['lock_sha256']==sha((SOURCE/'requirements.lock').read_bytes())
    if remote:
        assert env['code_commit']==MERGE and env['github_sha']==MERGE
        assert env['github_run_id']=='39637043080' and env['github_run_attempt']=='1'
    else: assert env['code_commit']==TARGET
    selected=load(base/'upload-selection.json')
    listed={safe(i['path']):i['sha256'] for i in selected['files']}
    assert len(listed)==len(selected['files'])
    for name,h in listed.items(): assert sha((base/name).read_bytes())==h,name
    if remote:
        actual={p.relative_to(base).as_posix() for p in base.rglob('*') if p.is_file()}
        assert actual==set(listed)|{'upload-selection.json'}
    omitted=[]; rootmatched=0
    for item in load(base/'artifacts.json'):
        p=base/safe(item['path'])
        if not remote or item['uploaded']: assert sha(p.read_bytes())==item['sha256']
        if item['uploaded']:rootmatched+=1
        else:
            omitted.append(item['path'])
            if remote:assert not p.exists()
    assert set(omitted)==set(selected['omitted_local_tools']) and len(omitted)==2
    wheel=next((base/'wheel').glob('aqrp-*.whl'))
    assert sha(wheel.read_bytes())==env['wheel_sha256']
    with zipfile.ZipFile(wheel) as z:
        for p in (SOURCE/'src/aqrp').rglob('*.py'):
            assert z.read(p.relative_to(SOURCE/'src').as_posix())==p.read_bytes()
        assert z.read('aqrp/factors/reviewed_code.json')==(SOURCE/'src/aqrp/factors/reviewed_code.json').read_bytes()
    assert (base/'.coverage').read_bytes().startswith(b'SQLite format 3')
    assert junit(base/'junit.xml')==dict(tests=417,failures=0,errors=0,skipped=0)
    assert load(base/'scan-findings.json')==[]
    command('coverage-'+base.parent.name,[sys.executable,SOURCE/'tools/check_coverage.py',base/'coverage.json'])
    snapshots={};logical=[]
    for kind in ('dataset','factor-dataset'):
        mp=next((base/kind).glob('*/manifest.json')); m=load(mp)
        ref=SnapshotRef(base/kind,m['snapshot_id'],m['manifest_hash'])
        verified,tables=verify_snapshot(ref);assert len(tables)==8
        projection={k:v for k,v in m.items() if k not in ('snapshot_id','manifest_hash')}
        assert sha(json.dumps(projection,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode())==m['manifest_hash']
        for item in m['tables'].values():assert sha((mp.parent/safe(item['path'])).read_bytes())==item['sha256']
        logical.append(canonical({name:[{k:v for k,v in row.items() if k!='snapshot_id'} for row in table.to_pylist()] for name,table in tables.items()}))
        snapshots[kind]={'snapshot_id':m['snapshot_id'],'manifest_hash':m['manifest_hash'],'tables':8,'rows':{k:len(v) for k,v in tables.items()}}
    config=load(base/'smoke-config.json'); receipt=load(base/'smoke-run.json')
    assert sha(canonical(config))==receipt['config_hash']
    request=QuerySpec(tuple(config['security_ids']),config['market_id'],config['calendar_id'],tuple(date.fromisoformat(d) for d in config['session_range']))
    values=query(request,config['as_of'],SnapshotRef(base/'dataset',config['snapshot_id'],config['manifest_hash'])).table.to_pylist()
    assert canonical(values)==(base/'smoke-result.json').read_bytes() and sha(canonical(values))==receipt['result_hash']
    logical.append(canonical(values))
    logical.append(canonical({k:v for k,v in config.items() if k not in ('snapshot_id','manifest_hash')}))
    factor_checks=[]
    for manifest_path in sorted((base/'factor-runs').glob('*/manifest.json')):
        info=load(manifest_path); folder=manifest_path.parent
        assert info['status']=='SUCCEEDED' and info['mode']=='TEST_ONLY' and info['financial_approval']=='NONE'
        for item in info['artifacts']: assert sha((folder/safe(item['path'])).read_bytes())==item['sha256']
        cfg=load(folder/'config.json'); rows=load(folder/'signals.json')
        original=SignalBatch(tuple(Signal(**row) for row in rows),(folder/'config.json').read_bytes())
        assert original.logical_hash==info['logical_hash'] and original.content_hash==info['content_hash']
        spec=builtin_spec(cfg['spec']['factor_id'],cfg['spec']['factor_version'],api_compatibility=cfg['spec']['api_compatibility'])
        registry=FactorRegistry();registry.register(spec.implementation_version,spec,actor='GPT Work audit',reason='replay current original CI',evidence=spec.review_ref)
        qs=QuerySpec(tuple(cfg['security_ids']),cfg['market_id'],cfg['calendar_id'],(date.fromisoformat(cfg['sessions'][0][0]),date.fromisoformat(cfg['target_session'])),('close','volume'),'split_adjusted')
        ref=SnapshotRef(base/'factor-dataset',cfg['snapshot_id'],cfg['manifest_hash'])
        batch=FactorEngine(registry).run(spec.ref,qs,cfg['decision_time'],ref,parameters=dict(cfg['params']),run_id=cfg['run_id'],computation_id=cfg['computation_id'],seed=cfg['seed'],requested_weight=None if cfg['requested_weight'] is None else Decimal(cfg['requested_weight']))
        assert canonical([asdict(row) for row in batch.rows])==(folder/'signals.json').read_bytes()
        expected={'momentum':0.21,'reversal':-0.21,'volume':0.6}[spec.factor_id]
        assert batch.rows[0].factor_value==expected and batch.rows[0].validity=='VALID'
        factor_checks.append({'factor':spec.factor_id,'value':expected,'logical_hash':batch.logical_hash,'exact_signal_rows_replayed':True})
    assert len(factor_checks)==3
    factor_result=load(base/'factor-result.json')
    assert {k:v['value'] for k,v in factor_result.items()}=={'momentum':0.21,'reversal':-0.21,'volume':0.6}
    logical.append(canonical(factor_result))
    return logical,{'environment':env,'junit':junit(base/'junit.xml'),'selected_hashes':len(listed),'root_hashes':rootmatched,'omitted_tools':omitted,'wheel_sha256':sha(wheel.read_bytes()),'coverage_gate':'PASS','snapshots':snapshots,'factors_replayed':factor_checks,'scan_findings':0}

try:
    assert sys.version_info[:3]==(3,13,16) and struct.calcsize('P')*8==64 and not sysconfig.get_config_var('Py_GIL_DISABLED')
    assert Path(aqrp.__file__).resolve().is_relative_to(RUN.resolve()) and 'site-packages' in aqrp.__file__
    assert (ROOT/'sdk.exit.txt').read_text().strip()=='0'
    modules=list((SOURCE/'src/aqrp').rglob('*.py')); installed=Path(aqrp.__file__).resolve().parent
    for p in modules:assert p.read_bytes()==(installed/p.relative_to(SOURCE/'src/aqrp')).read_bytes()
    packages=[]
    for line in (SOURCE/'requirements.lock').read_text().splitlines():
        if line and not line[0].isspace() and not line.startswith('#'):
            req=Requirement(line.rstrip('\\').strip())
            if req.marker is None or req.marker.evaluate():
                v=metadata.version(req.name);assert req.specifier.contains(v);packages.append({'name':req.name,'version':v})
    policy=reviewed_policy();assert policy['bundle_sha256']==bundle_hash()
    summary['checks']['runtime']={'python':sys.version,'executable':sys.executable,'sdk_file':aqrp.__file__,'installed_modules':len(modules),'active_locked_packages':packages,'policy':policy}
    sourcezip=zipfile.ZipFile(ROOT/'fixed-source.zip')
    for n in sourcezip.namelist():
        if not n.endswith('/'):assert sourcezip.read(n)==(SOURCE/n).read_bytes()
    integration='docs/audits/phase-2/lineage-fix/'
    latest=load(SOURCE/integration/'FILE_MANIFEST.json')
    for i in latest['files']:
        b=sourcezip.read(integration+safe(i['path']));assert sha(b)==i['sha256'] and len(b)==i['bytes'],i['path']
    frozen=load(SOURCE/'docs/audits/phase-1/implementation/CORE_PRESERVATION.json')
    for i in frozen['files']:assert sha(sourcezip.read(i['path']))==i['sha256']
    assert (SOURCE/'tests/golden/phase2_answers.json').read_bytes()==(SOURCE/'docs/audits/phase-2/golden_cases.json').read_bytes()
    reqs=list(csv.DictReader((SOURCE/'docs/requirements.csv').read_text(encoding='utf-8-sig').splitlines()))
    assert len(reqs)==106
    summary['checks']['preservation']={'latest_manifest_files':len(latest['files']),'frozen_files':len(frozen['files']),'canonical_requirements':106,'phase2_requirements':len([r for r in reqs if r['phase']=='2']),'golden_answers_equal_preimplementation':True}
    change=command('inherited-data-diff',['git','--no-optional-locks','diff','--name-only',BASE,TARGET,'--','src/aqrp/data','src/aqrp/core/time.py','src/aqrp/core/units.py','requirements.lock'],cwd=REPO)
    assert not change.strip()
    summary['checks']['shared_data_equals_released_main']=True
    reviewed='8902ba00a818150bf00af8d051a3837bc79e6bfc'
    shared=['src/aqrp/core/time.py','src/aqrp/data/pit.py','src/aqrp/data/quality.py']
    for path in shared:
        blob=command('reviewed-source-'+Path(path).stem,['git','--no-optional-locks','show',reviewed+':'+path],cwd=REPO)
        assert blob==sourcezip.read(path),path
    changed=command('source-delta-from-previous-p2',['git','--no-optional-locks','diff','--name-only','947467b9d094905cab0af37ec5cc53f1d187e755',TARGET,'--','src'],cwd=REPO).decode().splitlines()
    assert set(changed)==set(shared)|{'src/aqrp/factors/reviewed_code.json','src/aqrp/factors/contracts.py','src/aqrp/factors/engine.py'}
    merge_parents=command('integration-merge-parents',['git','--no-optional-locks','show','-s','--format=%P','566f0ece4175fddb2703daab3b5b26ff0e4e245f'],cwd=REPO).decode().split()
    assert merge_parents==['947467b9d094905cab0af37ec5cc53f1d187e755',BASE]
    assert not command('implementation-to-target-protected-diff',['git','--no-optional-locks','diff','--name-only','708b83be1dd597395b41f2ff6e10702749175bbf',TARGET,'--','src','tests','tools','.github','pyproject.toml','requirements.lock'],cwd=REPO).strip()
    summary['checks']['controlled_integration']={'merge_parents':merge_parents,'changed_source':changed,'shared_files_equal_previously_reviewed_business':True,'factor_formulas_and_input_unchanged':True,'implementation_to_target_protected_diff':[]}
    for name,expected in [('original16',dict(tests=16,failures=0,errors=0,skipped=0)),('new-probe',dict(tests=4,failures=0,errors=0,skipped=0))]:
        actual=junit(ROOT/(name+'-junit.xml'));assert actual==expected
        expected_exit=0
        assert (ROOT/(name+'.exit.txt')).read_text().strip()==str(expected_exit)
        summary['checks'][name]={'junit':actual,'exit':expected_exit,'classification':'all original16 and unchanged original4 probes PASS on newly installed fixed target'}
    old=load(ROOT.parent/'work-p1-recheck-3ab93b3/verification-summary.json')
    for i in old['original_unchanged_test_hashes']:assert sha(Path(i['path']).read_bytes())==i['sha256']
    summary['checks']['original16_scripts_unchanged']=old['original_unchanged_test_hashes']
    assert (ROOT/'test_work_p2_regressions.py').read_bytes()==(ROOT.parent/'work-p2-947467b/test_work_p2_regressions.py').read_bytes()
    summary['checks']['original4_p2_probes_unchanged']=sha((ROOT/'test_work_p2_regressions.py').read_bytes())
    prior=ROOT.parent/'work-p2-c70727c'
    original_manifest=load(prior/'REVIEW_EVIDENCE_MANIFEST.json')
    originals={i['path']:i for i in original_manifest['files']}
    receipt=load(SOURCE/integration/'RECEIPT_INDEX.json')
    assert len(originals)==receipt['original_entries_hash_verified']==248
    mapped={i['path'] for i in receipt['files']}
    omitted={i['path'] for i in receipt['omitted_files']}
    assert len(mapped)==245 and len(omitted)==3 and not mapped&omitted and mapped|omitted==set(originals)
    for i in receipt['files']+receipt['omitted_files']:
        old=(prior/safe(i['path'])).read_bytes()
        expected=originals[i['path']]
        assert sha(old)==i['sha256']==expected['sha256'] and len(old)==i['bytes']==expected['bytes']
        if i['path'] in mapped:
            assert (SOURCE/integration/safe(i['archive_path'])).read_bytes()==old
    assert (SOURCE/integration/'received/REVIEW_EVIDENCE_MANIFEST.json').read_bytes()==(prior/'REVIEW_EVIDENCE_MANIFEST.json').read_bytes()
    summary['checks']['received_prior_evidence']={'source_entries_verified':248,'copies_matching_original_bytes':245,'explicit_verified_omissions':3,'original_manifest_unchanged':True}
    delta=command('repair-source-delta',['git','--no-optional-locks','diff','--name-only','c70727c39182f81ee142730da9a9833a51581cd1',TARGET,'--','src'],cwd=REPO).decode().splitlines()
    assert set(delta)=={'src/aqrp/factors/contracts.py','src/aqrp/factors/engine.py','src/aqrp/factors/reviewed_code.json'}
    summary['checks']['repair_scope']={'changed_source':delta,'candidate_version':'0.2.0','shared_P1_source_preserved':True}
    mathfile=SOURCE/'docs/audits/phase-2/gemini/revised-math/aqrp_phase2_math_verification_revised.py'
    assert sha(mathfile.read_bytes())=='a4d6ab561cf81040411a9980adc4d72dbd69b79661cebaaf395da2312baae92c'
    assert (ROOT/'revised-math.exit.txt').read_text().strip()=='0'
    command('preimplementation-reference',[sys.executable,'-I','-S',SOURCE/'docs/audits/phase-2/reference_arithmetic.py'])
    summary['checks']['math_scripts']={'revised_raw_sha256':sha(mathfile.read_bytes()),'revised_exit':0,'scope':'arithmetic only; not SDK correctness proof; execution provenance GPT Work'}
    topo=command('ci-topology',['git','--no-optional-locks','show','-s','--format=%H%n%P%n%T',MERGE],cwd=REPO).decode().strip().splitlines()
    tree=command('target-tree',['git','--no-optional-locks','rev-parse',TARGET+'^{tree}'],cwd=REPO).decode().strip()
    assert topo[0]==MERGE and topo[1].split()==[BASE,TARGET] and topo[2]==tree
    summary['checks']['ci_topology']={'commit':MERGE,'parents':topo[1].split(),'tree':tree,'equals_target_tree':True}
    local_logical,local_check=verify_run(RUN);summary['checks']['new_local_sdk']=local_check
    remote_logical=[];remote_checks=[]
    for item in load(ROOT/'github-target-artifacts.json')['structuredContent']['artifacts']:
        aid=item['id'];path=ROOT/f'{aid}.zip';raw=path.read_bytes()
        assert len(raw)==item['size_in_bytes'] and 'sha256:'+sha(raw)==item['digest']
        assert item['workflow_run']['head_sha']==TARGET
        output=ROOT/'zip-replay'/str(aid);output.mkdir(parents=True)
        with zipfile.ZipFile(io.BytesIO(raw)) as z:
            assert z.testzip() is None and sum(i.file_size for i in z.infolist())<30_000_000
            names=set()
            for i in z.infolist():
                name=safe(i.filename);assert name not in names and not stat.S_ISLNK(i.external_attr>>16)
                names.add(name);p=(output/name).resolve();assert p.is_relative_to(output.resolve())
                if not i.is_dir():p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(z.read(i))
        base=next(output.glob('*/environment.json')).parent
        logical,checked=verify_run(base,True);remote_logical.append(logical)
        checked.update(artifact_id=aid,zip_sha256=sha(raw),zip_bytes=len(raw),name=item['name'])
        remote_checks.append(checked);print(aid,'original ZIP/internal hashes/2 snapshots/3 factor replays PASS',flush=True)
    assert len(remote_logical)==2 and remote_logical[0]==remote_logical[1]==local_logical
    summary['checks']['raw_current_ci_zip']=remote_checks
    summary['checks']['cross_os_and_local']='PASS: both eight-table datasets, data query/config, and three factors; exclude snapshot_id in table rows and snapshot_id/manifest_hash in data config; exact original signal rows replayed with original UUIDs; no comparison of path-sensitive query/config hashes'
    assert not command('final-review-status',['git','--no-optional-locks','status','--porcelain=v1'],cwd=REPO).strip()
    summary['status']='EVIDENCE VERIFIED; NO BLOCKING FINDING IN REVIEWED SCOPE'
except BaseException as e:
    summary['status']='VERIFIER INCOMPLETE';summary['error']=repr(e);raise
finally:
    summary['finished_at']=datetime.now().astimezone().isoformat()
    (ROOT/'evidence-verification.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'status':summary.get('status'),'checks':list(summary['checks']),'error':summary.get('error')},ensure_ascii=False),flush=True)
