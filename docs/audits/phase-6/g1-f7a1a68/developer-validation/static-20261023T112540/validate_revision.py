from pathlib import Path
from datetime import datetime, UTC
import hashlib,json,os,re,shutil,subprocess,sys,platform

O=Path(__file__).resolve().parent
R=Path(r'C:/Users/11638/AppData/Local/AQRP/checkouts/phase1-57461d5d-5de2-4c78-9b4e-5fad2b5ccb29')
D=R/'docs/audits/phase-6'; A=D/'g1-f7a1a68'
C='f7a1a68c5f747090f8c8a0e934f2fea859aec998'
SDK=Path(r'E:/WORK/AQRP-runs/p5-release-36c2691-20261023/aqrp-3e03b1bf-328f-40d0-be58-99efb33d4d51')
V=A/'developer-validation'/('static-'+datetime.now(UTC).strftime('%Y%m%dT%H%M%S'));V.mkdir()
def git(*args):return subprocess.check_output(['git',*args],cwd=R)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,obj):p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
assert git('rev-parse','HEAD').decode().strip()==C
assert git('branch','--show-current').decode().strip()=='codex/phase-6-ui-plan'
frozen=json.loads((D/'FROZEN_INPUTS.json').read_bytes())
for e in frozen['files']:
 p=R/e['path'];assert p.stat().st_size==e['bytes'] and sha(p)==e['sha256'],e['path']
assert len(frozen['files'])==4738
identity=json.loads((A/'DESIGN_REVISION_IDENTITY.json').read_bytes())
for e in identity['unchanged_prior_G1_assets']:
 p=D/e['path'];assert sha(p)==e['sha256'] and p.stat().st_size==e['bytes']
 assert p.read_bytes()==git('show',C+':docs/audits/phase-6/'+e['path']),e['path']
received=json.loads((A/'RECEIVED_IDENTITY.json').read_bytes())
for e in received['copied_originals']:
 p=A/'received'/e['path'];assert sha(p)==e['sha256'] and p.stat().st_size==e['bytes'],e['path']
 assert p.read_bytes()==(Path(received['original_source'])/e['path']).read_bytes(),e['path']
assert len(received['copied_originals'])==70
refs=json.loads((O/'REFERENCE_RUN.json').read_bytes())
for command in refs['commands']:
 assert command['exit_code']==0 and command['source_parent_commit']==C
 for name,h in command['source_files'].items():assert sha(D/name)==h,name
for name in ['numeric_probe.py','property_reference.py','run_references.py','reproduce_before.py','validate_revision.py']:
 shutil.copyfile(O/name,V/name)
save(V/'EXECUTION_ENVIRONMENT.json',{'executable':sys.executable,'version':sys.version,'platform':platform.platform(),'architecture':platform.machine(),'scope':'Developer documentation/design reference, not independent review or P6 product SDK/UI tests','base_sdk_environment':str(SDK),'core_lock_sha256':sha(R/'requirements.lock'),'helper_scripts':[{'path':p.name,'sha256':sha(p)} for p in V.glob('*.py')]})
env=os.environ.copy();env.pop('PYTHONPATH',None);env['PYTHONUTF8']='1'
for name,args in [
 ('existing-P5-package',[str(SDK/'venv/Scripts/python.exe'),'-I',str(R/'tools/check_phase5_package.py')]),
 ('secret-scan',[str(SDK/'gitleaks.exe'),'dir',str(R),'--config',str(R/'.gitleaks.toml'),'--redact=100','--no-banner','--report-format','json','--report-path',str(V/'scan-findings.json')])]:
 start=datetime.now(UTC).isoformat();p=subprocess.run(args,cwd=R,env=env,capture_output=True)
 (V/(name+'.stdout.log')).write_bytes(p.stdout);(V/(name+'.stderr.log')).write_bytes(p.stderr)
 save(V/(name+'.command.json'),{'executor':'Codex developer read-only G1 static check; inherited P5 code, no P6 product runtime tests','argv':args,'cwd':str(R),'started_utc':start,'finished_utc':datetime.now(UTC).isoformat(),'exit_code':p.returncode,'parent_commit':C,'source_dirty_design':True})
 assert p.returncode==0,(name,p.stderr.decode(errors='replace')[-2500:])
changed=set(filter(None,git('diff','--name-only','-z',C).decode().split('\0')))
changed.update(filter(None,git('ls-files','--others','--exclude-standard','-z').decode().split('\0')))
allowed=frozen['allowed_existing_status_documents'];prefix='docs/audits/phase-6/'
assert all(n in allowed or n.startswith(prefix) for n in changed),sorted(changed)
assert not git('diff',C,'--','src','tests','tools','.github','pyproject.toml','requirements.lock','.gitleaks.toml','docs/requirements.csv','docs/audits/phase-5')
rows=json.loads((D/'REQUIREMENTS_SNAPSHOT.json').read_bytes())['requirements']
assert [r['id'] for r in rows]==[f'UI-{i:03d}' for i in range(1,9)]
for row in rows:assert row['id'] in (D/'REQUIREMENTS_TRACEABILITY.md').read_text(encoding='utf-8')
for p in D.rglob('*.json'):json.loads(p.read_bytes())
links=[]
for p in D.rglob('*.md'):
 if 'received' in p.relative_to(D).parts:continue # immutable reviewer originals may link to external evidence
 for target in re.findall(r'\]\(([^)]+)\)',p.read_text(encoding='utf-8')):
  if target.startswith(('https://','http://','#')):continue
  assert (p.parent/target.split('#')[0]).exists(),(str(p),target)
  links.append({'source':p.relative_to(D).as_posix(),'target':target})
save(V/'STATIC_VERIFICATION.json',{'executor':'Codex developer static G1 revision check','checked_utc':datetime.now(UTC).isoformat(),'parent_reviewed_sha':C,'frozen_baseline':frozen['baseline'],'requirements':8,'MVP':5,'Competition Ready':3,'frozen_files_verified':4738,'original_received_files_verified':70,'original32_and_candidate_dependencies_unchanged':True,'reference_run_model_and_input_hashes_match':True,'src_tests_tools_CI_build_core_lock_P5_docs_unchanged':True,'local_document_links_verified':links,'scope_changes':sorted(changed),'actual_reference':{'original32':32,'supplemental':95,'ambient_decimal_observations':270,'fraction_oracle_cases':35},'independent_G1':'BLOCKED_AT_F7; CANDIDATE_PENDING_RECHECK','P6_product_browser_concurrency_tests':0,'UI_install':'NOT_EXECUTED','result':'PASS_STATIC_DESIGN_ONLY'})
save(D/'FILE_MANIFEST.json',{'self_excluded':True,'scope':'Phase6 G1 revised design/reference/candidate metadata and developer static evidence; no P6 implementation','files':[{'path':p.relative_to(D).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(D.rglob('*')) if p.is_file() and p!=D/'FILE_MANIFEST.json']})
subprocess.run(['git','add','--',*allowed,prefix],cwd=R,check=True)
p=subprocess.run(['git','diff','--cached','--check'],cwd=R,capture_output=True)
(O/'STAGED_CHECK.stdout.log').write_bytes(p.stdout);(O/'STAGED_CHECK.stderr.log').write_bytes(p.stderr)
assert p.returncode==0,p.stdout.decode(errors='replace')[:4000]
save(O/'STATIC_RUN.json',{'attempt':str(V),'staged_diff_check_exit':p.returncode,'manifest_files':len(json.loads((D/'FILE_MANIFEST.json').read_bytes())['files']),'all_checks':'PASS_DESIGN_ONLY'})
print(json.dumps({'static_attempt':str(V),'frozen':4738,'received_originals':70,'core_unchanged':True,'staged_diff_check':'PASS','G1':'BLOCKED_AT_F7; REVISED_CANDIDATE_PENDING_INDEPENDENT_RECHECK','P6_implementation':False}))
