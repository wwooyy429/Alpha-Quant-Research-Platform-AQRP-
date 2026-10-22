"""GPT Work read-only independent scope/archive check for fixed P4 plan revision."""
import csv, hashlib, io, json, platform, subprocess, sys, zipfile
from datetime import datetime, timezone
from pathlib import Path
R=Path(sys.argv[1]); O=Path(__file__).resolve().parent; D=R/'docs/audits/phase-4'
FIX='265af16353d85ce8c2d229a7517809d707498da8'; OLD='e40ddd0009cc30664c3a0fe0b74c4a497a541d77'; BASE='0a57dccb5618ba08cd3572d6d6b78fec963a3041'
checks=[]; commands=[]
def sha(b): return hashlib.sha256(b).hexdigest()
def load(p): return json.loads(p.read_bytes())
def ck(n,a,e=True):
    checks.append(dict(name=n,actual=a,expected=e,pass_=a==e)); assert a==e,checks[-1]
def git(*args):
    p=subprocess.run(['git',*args],cwd=R,capture_output=True)
    commands.append(dict(argv=['git',*args],cwd=str(R),exit_code=p.returncode,stdout=p.stdout.decode('utf-8','replace'),stderr=p.stderr.decode('utf-8','replace')))
    assert p.returncode==0,commands[-1]
    return p.stdout
def gt(*a): return git(*a).decode().strip()
ck('fixed_HEAD',gt('rev-parse','HEAD'),FIX); ck('clean_start',gt('status','--porcelain'),'')
tree=gt('rev-parse',FIX+'^{tree}'); ck('fixed_tree',tree,'f6faa305c3084dd027d607615cc146f7908e5034')
changes=gt('diff','--name-only',OLD,FIX).splitlines(); allchanges=gt('diff','--name-only',BASE,FIX).splitlines()
allowed={'AGENTS.md','README.md','docs/CHANGELOG.md','docs/DECISIONS.md','docs/PROGRESS.md','docs/ROADMAP.md','docs/TRACEABILITY.md'}
ck('only_plan_and_docs',all(x in allowed or x.startswith('docs/audits/phase-4/') for x in allchanges)); ck('incremental_changed_files',len(changes),100)
for ref in [BASE,OLD,'9ac5db069287a6e4a095e25ae8c3cc8fa229cded']:
    ck('business_unchanged:'+ref,gt('diff','--name-only',ref,FIX,'--','src','tests','tools','.github','requirements.lock','pyproject.toml','.gitleaks.toml','.python-version','.pre-commit-config.yaml','Makefile'),'')
for p in ['docs/audits/phase-0','docs/audits/phase-1','docs/audits/phase-2','docs/audits/phase-3','docs/sources','docs/requirements.csv','docs/INTERFACES.md','docs/DATA_CONTRACT.md','docs/BACKTEST_CONTRACT.md','.gitattributes']:
    ck('published_baseline_unchanged:'+p,gt('diff','--name-only',BASE,FIX,'--',p),'')
for p in ['GOLDEN_REFERENCE.md','golden_reference.py','SCOPE_AND_DEPENDENCIES.md','AUTHORIZATION.json','REQUIREMENTS_SNAPSHOT.json']:
    ck('prior_plan_input_preserved:'+p,sha((D/p).read_bytes()),sha(git('show',OLD+':docs/audits/phase-4/'+p)))
rows=list(csv.DictReader(io.StringIO((R/'docs/requirements.csv').read_text(encoding='utf-8')))); selected=[r for r in rows if r['phase']=='4']; snap=load(D/'REQUIREMENTS_SNAPSHOT.json')
ck('canonical_count',len(rows),106); ck('unique_ids',len({r['id'] for r in rows}),106); ck('ID_prefixes',len({r['id'].split('-')[0] for r in rows}),16)
ck('canonical_hash',sha((R/'docs/requirements.csv').read_bytes()),'20dd4e6be7188d3121f3cb361faf8901bc91815a6e9752beb14054a12183f0c1')
ck('selected_rows_exact',selected,snap['rows']); ck('seven_requirements',len(selected),7)
ck('4MVP_3CR',[sum(r['tier']==t for r in selected) for t in ['MVP','Competition Ready']],[4,3])
identity=load(R/'docs/audits/phase-3/IMPLEMENTATION_IDENTITY.json')
ck('frozen_count',len(identity['frozen_files']),1957); ck('all_frozen_hashes',all(sha((R/e['path']).read_bytes())==e['sha256'] for e in identity['frozen_files']))
bundle=identity['code_bundle_manifest']; modules=bundle['files']; ck('45_modules',len(modules),45)
ck('all_module_hashes',all(sha((R/'src/aqrp'/e['path']).read_bytes())==e['sha256'] for e in modules))
ck('no_extra_python_modules',sorted(e['path'] for e in modules),sorted(p.relative_to(R/'src/aqrp').as_posix() for p in (R/'src/aqrp').rglob('*.py')))
ck('canonical_bundle_hash',sha(json.dumps(bundle,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()),'3cec8a9da49a49a93010d7fa6a2012dded25185e2cdca49144cf4d719d56876e')
ck('dependency_lock_hash',sha((R/'requirements.lock').read_bytes()),'86c7bf65c9a9690036006360062c8cd10a91279705b4070af7033d7699abffeb')
ck('22_locked_distributions',sum('==' in s and not s.startswith((' ','#','-','\\')) for s in (R/'requirements.lock').read_text().splitlines()),22)
ck('no_p4_P5_UI_business_dirs',any((R/'src/aqrp'/p).exists() for p in ['portfolio','risk','backtest','execution','ui']),False)
manifest_counts={}
for folder in [D,D/'g1-e40ddd0']:
    fm=load(folder/'FILE_MANIFEST.json'); manifest_counts[folder.relative_to(R).as_posix()]=len(fm['files'])
    ck('manifest_hashes:'+folder.name,all((folder/e['path']).stat().st_size==e['bytes'] and sha((folder/e['path']).read_bytes())==e['sha256'] for e in fm['files']))
    actual={p.relative_to(folder).as_posix() for p in folder.rglob('*') if p.is_file()}
    ck('manifest_exact_coverage:'+folder.name,sorted(actual),sorted({e['path'] for e in fm['files']}|{'FILE_MANIFEST.json'}))
oldout=O.parent/'work-p4-g1-e40ddd0'; G=D/'g1-e40ddd0'; oldfm=load(oldout/'REVIEW_EVIDENCE_MANIFEST.json')
ck('old_manifest_65',len(oldfm['files']),65)
for src,dest in [('REVIEW_EVIDENCE_MANIFEST.json',G/'received/REVIEW_EVIDENCE_MANIFEST.json'),('RECEIPT.json',G/'ORIGINAL_RECEIPT.json'),('GPT-Work-P4-G1-e40ddd0-Evidence.zip',G/'GPT-Work-P4-G1-e40ddd0-Evidence.zip')]:
    ck('original_byte_identity:'+src,sha(dest.read_bytes()),sha((oldout/src).read_bytes()))
ck('original_zip_known_hash',sha((G/'GPT-Work-P4-G1-e40ddd0-Evidence.zip').read_bytes()),'2e81fcfb77e83a51c802acc662edb6ed58d6cb25e2612bf540c47f38745c5d4d')
ck('all_65_original_received_hashes',all(sha((G/'received'/e['path']).read_bytes())==e['sha256'] and (G/'received'/e['path']).stat().st_size==e['bytes'] for e in oldfm['files']))
ck('original_received_exact_set',sorted(p.relative_to(G/'received').as_posix() for p in (G/'received').rglob('*') if p.is_file()),sorted({e['path'] for e in oldfm['files']}|{'REVIEW_EVIDENCE_MANIFEST.json'}))
with zipfile.ZipFile(G/'GPT-Work-P4-G1-e40ddd0-Evidence.zip') as z:
    ck('original_zip_CRC',z.testzip(),None); ck('original_zip_exact_members',sorted(z.namelist()),sorted({e['path'] for e in oldfm['files']}|{'REVIEW_EVIDENCE_MANIFEST.json'}))
    ck('original_zip_all_65_member_hashes',all(len(z.read(e['path']))==e['bytes'] and sha(z.read(e['path']))==e['sha256'] for e in oldfm['files']))
devseal=load(O/'DEVELOPER-SEAL.json')
ck('new_developer_received_files',all((O/e['path']).stat().st_size==e['bytes'] and sha((O/e['path']).read_bytes())==e['sha256'] for e in devseal['files']))
with zipfile.ZipFile(O/'AQRP-P4-G1-265af16-Developer-Plan.zip') as z:
    ck('new_developer_archive_CRC',z.testzip(),None)
    prefix=next(n for n in z.namelist() if n.endswith('docs/audits/phase-4/FILE_MANIFEST.json')).removesuffix('FILE_MANIFEST.json')
    fm=load(D/'FILE_MANIFEST.json'); ck('developer_archive_103_files',len(fm['files']),103)
    ck('developer_archive_current_manifest',z.read(prefix+'FILE_MANIFEST.json'),(D/'FILE_MANIFEST.json').read_bytes())
    ck('developer_archive_all103',all(len(z.read(prefix+e['path']))==e['bytes'] and sha(z.read(prefix+e['path']))==e['sha256'] for e in fm['files']))
lines=gt('ls-remote','https://github.com/wwooyy429/Alpha-Quant-Research-Platform-AQRP-.git','refs/heads/main','refs/tags/phase*-baseline*','refs/tags/v0.*').splitlines(); refs={v:k for k,v in (s.split() for s in lines)}
ck('all_remote_release_refs_unchanged',refs,load(D/'PHASE3_RELEASE_RECEIPT.json')['remote_refs'])
profile=load(D/'SYNTHETIC_PROFILE.json'); oldprofile=json.loads(git('show',OLD+':docs/audits/phase-4/SYNTHETIC_PROFILE.json'))
ck('all_old_profile_parameters_unchanged',{k:profile[k] for k in oldprofile},oldprofile)
ck('only_explicit_quantity_and_funding_profile_additions',sorted(set(profile)-set(oldprofile)),['funding_identity','quantity_policy'])
ck('two_findings_OPEN_on_submission',set(load(D/'STATUS.json')['findings'].values()),{'OPEN'})
ck('implementation_not_authorized',load(D/'STATUS.json')['P4_implementation_authorized'],False)
git('diff','--stat',OLD,FIX); ck('clean_end',gt('status','--porcelain'),'')
def safe(x):
    if isinstance(x,bytes): return '<byte-exact equality checked; sha256='+sha(x)+'>'
    if isinstance(x,set): return sorted(x)
    raise TypeError(type(x).__name__)
result=dict(actual_executor='GPT Work primary reviewer',utc=datetime.now(timezone.utc).isoformat(),fixed_sha=FIX,previous_sha=OLD,base_sha=BASE,tree=tree,incremental_changed_files=changes,total_changed_files=allchanges,checks=checks,manifest_counts=manifest_counts,requirements=selected,remote_refs=refs,result='PASS')
(O/'scope-results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2,default=safe)+'\n',encoding='utf-8')
(O/'scope-raw-git-commands.json').write_text(json.dumps(commands,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(result='PASS',checks=len(checks),incremental_files=len(changes),total_files=len(allchanges),original_evidence_members=65,original_zip_members=66,plan_manifest=manifest_counts),indent=2))
