import pathlib,json,hashlib,subprocess,shutil,sys,platform,datetime
O=pathlib.Path(__file__).parent;C=O.parent/'p4-g2-recheck-3c87579';SDK=pathlib.Path((O/'SDK_LOCATION.txt').read_text(encoding='utf-8'));FIX='3c8757949b0fd5c97953b06a74ebc2d0e56676e4'
def H(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(name,x):(O/name).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def git(*a):return subprocess.check_output(['git','-C',str(C),*a]).decode().strip()
assert git('rev-parse','HEAD')==FIX and git('status','--porcelain')==''
names=['scope','clean-sdk','independent-repairs','independent-behavior','original-four','original20','original91','scanner-controls-ready','evidence-official','evidence-local','developer-archive','old-replay','official-download']
commands={name:json.loads((O/(name+'.command.json')).read_bytes()) for name in names}
assert all(v['exit_code']==0 for v in commands.values())
expected=json.loads((O/'previous-INDEPENDENT_EXPECTED_RESULTS.json').read_bytes());actual=json.loads((O/'INDEPENDENT_BEHAVIOR_RESULTS.json').read_bytes());byname={e['case']:e for e in expected['cases']};assert len(byname)==174
for r in actual['records']:assert byname[r['case']]['request_sha256']==r['request_hash']
save('EXPECTED_REQUEST_BINDING.json',{'fixed_sha':FIX,'previous_expected_file_sha256':H(O/'previous-INDEPENDENT_EXPECTED_RESULTS.json'),'current_174_requests_exact_hash_matches':True,'expected_source':'Prior GPT Work independent Fraction reference and saved rational answers; no implementation-generated expectations'})
received=C/'docs/audits/phase-3/g2-5a5e093/received';originals=[]
for n in ['test_review_regressions.py','independent_implementation_math.py','verify_scanner_controls.py']:
 assert (O/n).read_bytes()==(received/n).read_bytes();originals.append({'path':n,'sha256':H(O/n)})
assert json.loads((O/'independent-implementation-math.json').read_bytes())['passed']==91
save('LEGACY_REEXECUTION.json',{'fixed_sha':FIX,'actual_executor':'GPT Work supplemental reviewer','actual_python':str(SDK/'venv/Scripts/python.exe'),'package_version':'0.4.1.dev1','scripts_byte_unchanged':originals,'passed':{'original_four':4,'old16_plus4':20,'math':91,'scanner':3},'harness_first_failure':'legacy-wrapper/scanner-controls started before clean SDK secret-scan stage had produced gitleaks.exe. FileNotFoundError, not product test failure. Original logs retained. Only scanner was repeated with scanner-controls-ready after hashed executable existed.','old_labels':'Immutable scripts retain historical reviewed_sha/executor text; current command receipts bind this actual target/interpreter. No claim of Gemini execution or formal approval.'})
paths=list((C/'src/aqrp').rglob('*.py'))+[C/'src/aqrp/factors/reviewed_code.json',C/'requirements.lock',C/'pyproject.toml']+list((C/'tests/portfolio').rglob('*.py'))+list((C/'tests/portfolio/fixtures').rglob('*'))
paths += [C/'docs/audits/phase-4'/n for n in ['FROZEN_INPUTS.json','IMPLEMENTATION_TRACEABILITY.md','IMPLEMENTATION_AUTHORIZATION.json']]
paths += [C/'docs/audits/phase-4/g2-18439f3'/n for n in ['IDENTITY.json','REVIEW_PACKAGE.md','DEVELOPER_RESPONSE.md','CODE_REVIEW.md']]
for p in paths:
 if not p.is_file():continue
 dst=O/'fixed-source'/p.relative_to(C);dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,dst)
# Include immutable source anchors and all nine actual files, with their original path relationships.
P=C/'docs/audits/phase-3/publication/sdk/research';SID='9e3a5971-d66e-4aee-bdb4-1082c6907e02';RID='0c902a7a-6e21-4003-9e18-365bf8bc3b68'
for folder in [P/'inputs/dataset'/SID,P/'runs'/RID]:
 for p in folder.iterdir():
  if p.is_file():dst=O/'parent-original'/p.relative_to(P);dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,dst)
save('REVIEW_EXECUTION.json',{'fixed_sha':FIX,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'actual_executor':'GPT Work supplemental reviewer','checkout':str(C.resolve()),'HEAD':git('rev-parse','HEAD'),'porcelain':git('status','--porcelain').splitlines(),'tree':git('rev-parse','HEAD^{tree}'),'base':'0a57dccb5618ba08cd3572d6d6b78fec963a3041','review_runtime':{'python':sys.version,'executable':sys.executable,'platform':platform.platform(),'machine':platform.machine(),'GIL':sys._is_gil_enabled()},'commands':commands,'preparation_commands':['git clone --no-checkout --shared C:/Users/11638/AppData/Local/AQRP/reviews/p4-g2-18439f3-review C:/Users/11638/AppData/Local/AQRP/reviews/p4-g2-recheck-3c87579','git config core.longpaths true','git remote set-url origin https://github.com/wwooyy429/Alpha-Quant-Research-Platform-AQRP-','git fetch --no-tags origin '+FIX+' 354c931ef05d8d16237efac5826ae47302175f4f','git -c core.autocrlf=false checkout --detach '+FIX],'limits':['No account/ACL/service/deployment changes','No real formal Test or financial approval','No merge/tag/P5','Ubuntu ran on GitHub, independently verified raw evidence on Windows'],'original_source_unchanged':True})
print(json.dumps({'fixed_sha':FIX,'all_required_commands_success':True,'source_clean':True,'expected_request_hashes':174,'fixed_source_files':len([p for p in (O/'fixed-source').rglob('*') if p.is_file()])}))
