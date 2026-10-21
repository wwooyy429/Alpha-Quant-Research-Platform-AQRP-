"""Developer receipt checks for the Phase2 Gemini report; not Gemini execution."""
import csv, hashlib, json, pathlib, stat, subprocess, uuid, xml.etree.ElementTree as ET, zipfile
from datetime import datetime, timezone
from fractions import Fraction
ROOT=pathlib.Path(r'C:\Users\11638\AppData\Local\AQRP\checkouts\phase1-57461d5d-5de2-4c78-9b4e-5fad2b5ccb29')
OUT=pathlib.Path(__file__).resolve().parent/'phase2-audit-receipt'
OUT.mkdir(exist_ok=True)
REVIEW='2a70dc6251ce2e7d014d76f3c1bd26cdddb3aac1'
SOURCE=pathlib.Path(r'B:\BaiduSyncdisk\学习\投资\量化\量化交易比赛\审查\aqrp_phase2_implementation_audit_report.md')
sha=lambda b:hashlib.sha256(b).hexdigest()
def git(*args): return subprocess.check_output(['git',*args],cwd=ROOT)
def write(name,obj): (OUT/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
report=SOURCE.read_bytes()
assert sha(report)=='395eadf04145e5a23b624687c3576def8a9b23260cb75a53037c7218e30a3d0f'
assert git('rev-parse','HEAD').decode().strip()==REVIEW
assert not git('status','--porcelain')
original_manifest=json.loads((ROOT/'docs/audits/phase-2/implementation/FILE_MANIFEST.json').read_bytes())
for item in original_manifest['files']:
    assert sha((ROOT/item['path']).read_bytes())==item['sha256'],item['path']
assert not git('diff','8183b37',REVIEW,'--','src','tests','tools','.github','pyproject.toml','requirements.lock')
assert not git('diff','f579b2c','--','docs/audits/phase-0','docs/audits/phase-1')
protected=json.loads((ROOT/'docs/audits/phase-1/implementation/CORE_PRESERVATION.json').read_bytes())['files']
assert len(protected)==50
for item in protected: assert sha((ROOT/item['path']).read_bytes())==item['sha256']
rows=list(csv.DictReader((ROOT/'docs/requirements.csv').read_text(encoding='utf-8').splitlines()))
assert len(rows)==106 and len({x['id'].split('-')[0] for x in rows})==16
assert next(x for x in rows if x['id']=='FACTOR-008')['phase']=='POST7'
golden=json.loads((ROOT/'tests/golden/phase2_answers.json').read_bytes())
case=next(x for x in golden['cases'] if x['id']=='G-P2-A')
assert list(map(Fraction,case['volumes']))==[100,150,200]
mean=sum(map(Fraction,case['volumes'][:-1]))/2
value=Fraction(case['volumes'][-1])/mean-1
assert value==Fraction(3,5) and mean==125
math=[]
for text in ('21/100','-21/100','3/5','-1/5','1/5','0','-1/100'):
    q=Fraction(text); val=float(q); err=abs(Fraction.from_float(val)-q)
    assert err<=Fraction('1e-12')
    math.append({'rational':text,'float':val,'exact_binary64_error':str(err),'absolute_error':float(err),'within_abs_1e_12':True})
write('developer-math-recheck.json',{'performed_by':'Codex developer, new receipt check, not Gemini or replacement for missing raw reviewer execution','golden_volume':{'input':case['volumes'],'historical_mean':str(mean),'formula':'200 / ((100+150)/2) - 1','exact_result':str(value)},'precision':math})
archive=ROOT/'docs/audits/phase-2/implementation'
cov=json.loads((archive/'local/coverage.json').read_bytes())
protocol=[{'path':p,'excluded_lines':d['excluded_lines']} for p,d in cov['files'].items() if p.replace('\\','/').endswith('/factors/contracts.py')]
assert len(protocol)==1 and protocol[0]['excluded_lines']==[289,290,291],protocol
assert not (ROOT/'src/aqrp/factors/protocols.py').exists()
assert not (ROOT/'src/aqrp/core/security.py').exists()
assert (ROOT/'src/aqrp/core/security/__init__.py').exists()
assert b'input_data_hash' not in (ROOT/'src/aqrp/factors/contracts.py').read_bytes()
commands=(archive/'local/commands.log').read_text(encoding='utf-8')
assert '254 passed' in commands and 'mypy' not in commands and 'pyright' not in commands
api=json.loads((OUT.parent/'phase2-audit-receipt-api-artifacts.json').read_bytes())
zip_results=[]
for file,aid in [('12342621298-ubuntu.zip',12342621298),('12342066424-windows.zip',12342066424)]:
    blob=(archive/'ci'/file).read_bytes()
    meta=next(x for x in api['artifacts'] if x['id']==aid)
    assert sha(blob)==meta['digest'].removeprefix('sha256:') and len(blob)==meta['size_in_bytes']
    with zipfile.ZipFile(archive/'ci'/file) as z:
        assert z.testzip() is None
        assert len(z.namelist())==len(set(z.namelist()))
        roots={p.split('/')[0] for p in z.namelist()}
        assert len(roots)==1
        prefix=roots.pop()+'/'
        for member in z.infolist():
            p=pathlib.PurePosixPath(member.filename)
            assert not p.is_absolute() and '..' not in p.parts and '\\' not in member.filename and ':' not in member.filename and not stat.S_ISLNK(member.external_attr>>16)
        selection=json.loads(z.read(prefix+'upload-selection.json'))
        actual={x.removeprefix(prefix) for x in z.namelist() if not x.endswith('/')}
        assert actual=={x['path'] for x in selection['files']}|{'upload-selection.json'}
        for item in selection['files']: assert sha(z.read(prefix+item['path']))==item['sha256']
        suites=ET.fromstring(z.read(prefix+'junit.xml')).findall('testsuite')
        tests={k:sum(int(x.attrib.get(k,0)) for x in suites) for k in ('tests','failures','errors','skipped')}
        assert tests==dict(tests=254,failures=0,errors=0,skipped=0)
        env=json.loads(z.read(prefix+'environment.json'))
        assert env['code_commit']=='6ff410928a34df1696fb1bf36072adb3e9312147'
    zip_results.append({'file':file,'id':aid,'sha256':sha(blob),'bytes':len(blob),'fresh_remote_api_metadata_match':True,'safe_paths_crc':True,'selection_member_hashes_verified':len(selection['files']),'junit':tests})
refs={line.split()[1]:line.split()[0] for line in git('ls-remote','origin','refs/heads/main','refs/heads/feature/phase-2-factor-registry','refs/tags/phase0-baseline','refs/tags/phase0-baseline^{}','refs/tags/phase1-baseline','refs/tags/phase1-baseline^{}').decode().splitlines()}
assert refs['refs/heads/main']=='f579b2c99e762085772de6e70ba1fa98792a7add'
assert refs['refs/heads/feature/phase-2-factor-registry']==REVIEW
assert refs['refs/tags/phase1-baseline^{}']==refs['refs/heads/main']
assert refs['refs/tags/phase0-baseline^{}']=='7de1d0e81385ae97f98ea673fe05dd726f0b577b'
assert not git('ls-remote','--tags','origin','*phase2*')
named=[SOURCE.parent/'aqrp_phase2_implementation_math_and_hash_audit.py',SOURCE.parent/'aqrp_phase2_implementation_math_and_hash_audit.log']
assert not any(x.exists() for x in named),'New supplied evidence detected; inspect before recording absent'
sync=[p.relative_to(ROOT).as_posix() for p in ROOT.rglob('*冲突文件*') if p.is_file() and '.git' not in p.parts]
assert not sync
result={'run_id':'p2-audit-receipt-'+str(uuid.uuid4()),'time_utc':datetime.now(timezone.utc).isoformat(),'performed_by':'Codex developer, not Gemini','reviewed_commit':REVIEW,'report_source':str(SOURCE),'report_sha256':sha(report),'report_bytes':len(report),'prior_current_manifest_files_verified':len(original_manifest['files']),'phase0_protected_files_verified':len(protected),'old_audit_files_preserved':448,'requirements':106,'groups':16,'business_source_tests_tools_ci_lock_unchanged':True,'protocol_excluded_lines_actual':protocol,'volume_and_exact_float_recheck':'developer-math-recheck.json','archive_and_fresh_remote_metadata_checks':zip_results,'remote_refs':refs,'phase2_tag_exists':False,'gemini_named_new_math_files_found':[str(x) for x in named if x.exists()],'gemini_new_math_raw_evidence_received':False,'gemini_full_sdk_independent_execution':'NOT VERIFIED; reviewer explicitly did not execute exact runtime','new_full_sdk_run_this_receipt':False,'reason_no_sdk_rerun':'Only report/status/evidence reconciliation, no business or test changes; preserve original local and CI evidence; new head CI will run after push','sync_conflicts':sync}
write('checks.json',result)
print(json.dumps({'report_sha256':result['report_sha256'],'zip_checks':'PASS','prior_manifest':len(original_manifest['files']),'protected':len(protected),'raw_gemini_math_files_found':0,'math':'PASS, exact float errors nonzero except zero'},ensure_ascii=False))

