"""GPT Work independent, read-only fixed-commit scope verification. Standard library only."""
import csv, hashlib, io, json, platform, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path
R=Path(sys.argv[1]); O=Path(sys.argv[2]); D=R/'docs/audits/phase-4'
FIX='e40ddd0009cc30664c3a0fe0b74c4a497a541d77'; BASE='0a57dccb5618ba08cd3572d6d6b78fec963a3041'
commands=[]; checks=[]
def sha(b): return hashlib.sha256(b).hexdigest()
def git(*a):
    p=subprocess.run(['git',*a],cwd=R,capture_output=True)
    commands.append(dict(argv=['git',*a],cwd=str(R),exit_code=p.returncode,stdout=p.stdout.decode('utf-8','replace'),stderr=p.stderr.decode('utf-8','replace')))
    if p.returncode: raise RuntimeError(commands[-1])
    return p.stdout
def check(n,a,e=True):
    checks.append(dict(check=n,actual=a,expected=e,pass_=a==e))
    if a!=e: raise AssertionError(checks[-1])
def textgit(*a): return git(*a).decode().strip()
def load(p): return json.loads(p.read_bytes())
check('fixed_checkout',textgit('rev-parse','HEAD'),FIX)
check('clean_checkout_start',textgit('status','--porcelain'),'')
check('fixed_tree',textgit('rev-parse',FIX+'^{tree}'),'66ae3cce5f9d73271963e72aaaf3ec171c08c4c1')
refs={k:textgit('rev-parse',k+'^{}') for k in ['phase3-baseline','v0.3.0','phase2-baseline','v0.2.0']}
for k,v in refs.items(): check('ref_'+k,v,BASE if 'phase2' not in k and k!='v0.2.0' else 'f26255fc40a3080bfa883ad64938f60036a14759')
remote_lines=textgit('ls-remote','https://github.com/wwooyy429/Alpha-Quant-Research-Platform-AQRP-.git','refs/heads/main','refs/tags/phase3-baseline^{}','refs/tags/v0.3.0^{}','refs/tags/phase2-baseline^{}','refs/tags/v0.2.0^{}').splitlines()
remote_refs={v:k for k,v in (line.split() for line in remote_lines)}
check('official_remote_ref_count',len(remote_refs),5)
for ref,value in remote_refs.items(): check('official_remote_'+ref,value,'f26255fc40a3080bfa883ad64938f60036a14759' if 'phase2' in ref or 'v0.2.0' in ref else BASE)
changed=textgit('diff','--name-only',BASE,FIX).splitlines()
allowed={'AGENTS.md','README.md','docs/CHANGELOG.md','docs/DECISIONS.md','docs/PROGRESS.md','docs/ROADMAP.md','docs/TRACEABILITY.md'}
check('only_plan_docs',all(x in allowed or x.startswith('docs/audits/phase-4/') for x in changed))
check('changed_count',len(changed),28)
for p in ['src','tests','tools','.github','requirements.lock','pyproject.toml','docs/requirements.csv','docs/audits/phase-0','docs/audits/phase-1','docs/audits/phase-2','docs/audits/phase-3','docs/golden','docs/sources','docs/INTERFACES.md','docs/DATA_CONTRACT.md','docs/BACKTEST_CONTRACT.md']:
    check('baseline_identical:'+p,git('diff','--name-only',BASE,FIX,'--',p),b'')
check('reviewed_9ac_business_identity',git('diff','--name-only','9ac5db069287a6e4a095e25ae8c3cc8fa229cded',FIX,'--','src','tests','tools','.github','requirements.lock','pyproject.toml'),b'')
req=R/'docs/requirements.csv'; rows=list(csv.DictReader(io.StringIO(req.read_text(encoding='utf-8')))); snap=load(D/'REQUIREMENTS_SNAPSHOT.json')
check('canonical_sha256',sha(req.read_bytes()),snap['canonical_sha256']); check('canonical_count',len(rows),106)
check('unique_ids',len({x['id'] for x in rows}),106); check('id_prefix_count',len({x['id'].split('-')[0] for x in rows}),16)
sel=[x for x in rows if x['phase']=='4']; check('p4_rows',sel,snap['rows']); check('p4_count',len(sel),7)
check('p4_mvp',sum(x['tier']=='MVP' for x in sel),4); check('p4_cr',sum(x['tier']=='Competition Ready' for x in sel),3)
check('dependency_ids_exist',all(d in {x['id'] for x in rows} for r in sel for d in r['dependencies'].split(';')))
identity=load(R/'docs/audits/phase-3/IMPLEMENTATION_IDENTITY.json')
bad=[e['path'] for e in identity['frozen_files'] if sha((R/e['path']).read_bytes())!=e['sha256']]
check('frozen_file_count',len(identity['frozen_files']),1957); check('frozen_mismatches',bad,[])
manifest=identity['code_bundle_manifest']; modules=manifest['files']
check('source_module_count',len(modules),45)
check('source_module_hashes',all(sha((R/'src/aqrp'/e['path']).read_bytes())==e['sha256'] for e in modules))
check('no_unlisted_python_source',sorted(e['path'] for e in modules),sorted(p.relative_to(R/'src/aqrp').as_posix() for p in (R/'src/aqrp').rglob('*.py')))
check('bundle_identity',sha(json.dumps(manifest,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()),identity['code_bundle_sha256'])
lockhash=sha((R/'requirements.lock').read_bytes()); check('lock_hash',lockhash,manifest['dependency_lock_sha256'])
locked=[line for line in (R/'requirements.lock').read_text().splitlines() if line and not line.startswith(('#',' ','-','\\')) and '==' in line]
check('locked_distributions',len(locked),22)
fm=load(D/'FILE_MANIFEST.json'); check('plan_manifest_count',len(fm['files']),20)
check('plan_manifest_entries',all((D/e['path']).stat().st_size==e['bytes'] and sha((D/e['path']).read_bytes())==e['sha256'] for e in fm['files']))
check('no_p4_later_business_dirs',any((R/'src/aqrp'/p).exists() for p in ['portfolio','risk','backtest','execution','ui']),False)
archive=O/'fixed-plan-source.zip'
git('archive','--format=zip','--output='+str(archive),FIX,*changed)
git('diff','--stat',BASE,FIX); check('clean_checkout_end',textgit('status','--porcelain'),'')
def safe(v):
    if isinstance(v,bytes): return v.decode('utf-8','replace')
    raise TypeError(type(v).__name__)
result=dict(actual_executor='GPT Work primary reviewer',utc=datetime.now(timezone.utc).isoformat(),python=sys.version,executable=sys.executable,platform=platform.platform(),fixed_sha=FIX,base_sha=BASE,refs=refs,changed_files=changed,checks=checks,requirements=sel,source_bundle_sha256=identity['code_bundle_sha256'],lock_sha256=lockhash,partial_archive=dict(path=archive.name,scope='Only the 28 changed plan/document files; NOT full source archive or SDK evidence',bytes=archive.stat().st_size,sha256=sha(archive.read_bytes())),result='PASS')
(O/'scope-results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2,default=safe)+'\n',encoding='utf-8')
(O/'scope-raw-git-commands.json').write_text(json.dumps(commands,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(result='PASS',checks=len(checks),changed=len(changed),frozen=1957,modules=45,requirements=7),indent=2))
