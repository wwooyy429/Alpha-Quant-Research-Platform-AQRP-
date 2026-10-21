import json,subprocess,hashlib,csv
from pathlib import Path
from datetime import datetime,timezone
R=Path(__file__).resolve().parent
S=R/'source';repo=Path(r'C:\Users\11638\AppData\Local\AQRP\reviews\p1-3ab93b3')
records=[]
def git(name,args):
    p=subprocess.run(['git','--no-optional-locks',*args],cwd=repo,capture_output=True)
    (R/(name+'.stdout.log')).write_bytes(p.stdout);(R/(name+'.stderr.log')).write_bytes(p.stderr)
    records.append(dict(name=name,argv=['git',*args],cwd=str(repo),exit_code=p.returncode))
    return p.stdout.decode(errors='replace').strip()
assert git('head',['rev-parse','HEAD'])=='3ab93b35c0b5e4e7b5e85c27f641748aa86cb24f'
assert git('status',['status','--porcelain=v1','-b'])=='## HEAD (no branch)'
assert not git('business-equivalence',['diff','--stat','cdb11cd913e965a43572ceb86efb0a39d1f618df','3ab93b35c0b5e4e7b5e85c27f641748aa86cb24f','--','src','tests','tools','.github','requirements.lock','pyproject.toml','.python-version','.gitleaks.toml'])
git('current-head-drift',['diff','--name-status','3ab93b35c0b5e4e7b5e85c27f641748aa86cb24f','16083e151e3dadc11981c878f5aa90b7b09e9ac4','--','src','tests','tools','.github','requirements.lock','pyproject.toml'])
git('ci-business-object',['show','-s','--format=%H%n%P%n%T','ccf0e9f1861a83a6995be10149239737a85214ec'])
base=S/'docs/audits/phase-1/repairs/data-validation'
m=json.loads((base/'EVIDENCE_MANIFEST.json').read_bytes());checks=[]
for i in m['files']:
    p=base/i['path'];actual=hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else None
    assert actual==i['sha256'],i['path'];checks.append(dict(path=i['path'],sha256=actual))
frozen=json.loads((S/'docs/audits/phase-1/implementation/CORE_PRESERVATION.json').read_bytes())
for i in frozen['files']:assert hashlib.sha256((S/i['path']).read_bytes()).hexdigest()==i['sha256'],i['path']
# All four frozen Phase1 input/answer bytes still match their baseline objects.
for path in ['tests/golden/phase1_input.json','tests/golden/phase1_input_manifest.json','tests/golden/phase1_answers.json','tests/golden/phase1_answers_manifest.json','requirements.lock','docs/requirements.csv']:
    raw=subprocess.check_output(['git','show','f579b2c99e762085772de6e70ba1fa98792a7add:'+path],cwd=repo)
    assert raw==(S/path).read_bytes(),path
summary=dict(audit='GPT Work 补充审核',target_sha='3ab93b35c0b5e4e7b5e85c27f641748aa86cb24f',time_utc=datetime.now(timezone.utc).isoformat(),commands=records,evidence_manifest_matches=len(checks),protected_p0_matches=len(frozen['files']),golden_lock_requirement_bytes_unchanged=True,requirements=len(list(csv.DictReader((S/'docs/requirements.csv').open(encoding='utf-8')))),evidence_checks=checks)
(R/'facts.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
print('repair evidence',len(checks),'matched; protected P0',len(frozen['files']),'matched; Golden/lock/catalog unchanged')
