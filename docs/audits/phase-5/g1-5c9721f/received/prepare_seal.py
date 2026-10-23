import pathlib,json,hashlib,shutil,subprocess,sys,platform,datetime
O=pathlib.Path(__file__).parent;C=O.parent/'p5-g1-review-5c9721f';D=O.parent/'p5-g1-5c9721f';P=C/'docs/audits/phase-5';FIX='5c9721f96679f4d495b7b3b93af3e2e31e66ae62'
def H(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(n,x):(O/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def git(*a):return subprocess.check_output(['git','-C',str(C),*a]).decode().strip()
assert git('rev-parse','HEAD')==FIX and not git('status','--porcelain')
names=['scope-evidence','independent-math','design-cases','design-cases-final','developer-reference','release-details'];commands={n:json.loads((O/(n+'.command.json')).read_bytes()) for n in names};assert all(c['exit_code']==0 for c in commands.values())
for p in P.rglob('*'):
 if p.is_file():dst=O/'fixed-plan'/p.relative_to(P);dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,dst)
for e in json.loads((P/'FROZEN_INPUTS.json').read_bytes())['files']:
 p=C/e['path'];dst=O/'frozen-source'/e['path'];dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,dst)
for rel in ['AGENTS.md','docs/PROJECT_CHARTER.md','docs/ARCHITECTURE.md','docs/INTERFACES.md','docs/BACKTEST_CONTRACT.md','docs/TESTING.md','docs/REQUIREMENTS.md','docs/TRACEABILITY.md','docs/ROADMAP.md','docs/PROGRESS.md','docs/DECISIONS.md','docs/audits/phase-4/STATUS.json','docs/audits/phase-4/publication/VALIDATION.json']:
 p=C/rel;dst=O/'supporting-documents'/rel;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,dst)
recv=O/'developer-received';recv.mkdir(exist_ok=True)
for n in ['GPT-Work-G1-Review-Instructions.txt','RECEIPT.json','EVIDENCE_MANIFEST.json','EXTERNAL_ARCHIVES.json','SDK_VERIFICATION.json','P5_CI_SNAPSHOT.json','RELEASE_RECEIPT.json','OLD_REMOTE_TAGS.txt','FINAL_REMOTE_REFS.txt']:shutil.copyfile(D/n,recv/n)
old=json.loads((D/'EXTERNAL_ARCHIVES.json').read_bytes());ext=[]
for e in old['omitted_from_outer_ZIP_to_avoid_duplication']:
 p=pathlib.Path(e['path']);assert H(p)==e['sha256'];ext.append({'path':str(p),'bytes':p.stat().st_size,'sha256':e['sha256'],'result':'UNCHANGED'})
save('EXTERNAL_PREVIOUS_ARCHIVES_VERIFIED.json',ext)
blocking={'BT-001':['001'],'BT-002':[],'BT-003':['001','003'],'BT-004':['003'],'BT-005':['001','002'],'BT-006':['002'],'BT-007':['002','004'],'BT-008':['002'],'BT-009':['004'],'BT-010':['001','002','003'],'QA-003':['001','002','003','004'],'INT-002':['001','002','003','004']}
requirements=json.loads((P/'REQUIREMENTS_SNAPSHOT.json').read_bytes())['requirements']
save('REQUIREMENT_REVIEW.json',{'fixed_sha':FIX,'scope':'12 planned requirements, no implementation approval','requirements':[{**r,'independent_mapping_review':'PRESENT','related_findings':['WORK-P5-G1-'+s for s in blocking[r['id']]],'acceptance_state':'PLANNED_NOT_EXECUTED'} for r in requirements]})
end=json.loads((O/'PR8_FINAL.json').read_bytes());start=json.loads((O/'PR8_START.json').read_bytes())
save('REVIEW_EXECUTION.json',{'reviewer':'GPT Work supplemental reviewer','fixed_sha':FIX,'checkout':str(C.resolve()),'HEAD':git('rev-parse','HEAD'),'tree':git('rev-parse','HEAD^{tree}'),'porcelain':git('status','--porcelain').splitlines(),'UTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'python':sys.version,'executable':sys.executable,'GIL':sys._is_gil_enabled(),'platform':platform.platform(),'machine':platform.machine(),'commands':commands,'PR_initial_head':start['head_sha'],'PR_final_head':end['head_sha'],'drift':'New PR8 description/head bd18d1b not checked out/reviewed; report scoped to originally specified fixed5c9721f','preparation_commands':['git clone --no-checkout --shared C:/Users/11638/AppData/Local/AQRP/reviews/p4-g2-recheck-3c87579 C:/Users/11638/AppData/Local/AQRP/reviews/p5-g1-review-5c9721f','git config core.longpaths true','git remote set-url origin https://github.com/wwooyy429/Alpha-Quant-Research-Platform-AQRP-','git fetch --no-tags origin '+FIX+' 32ea5d6b75c84c07017d87377eeabd2f78207c5c d3993d07e5df1b5c2f7acd30cb628226f7b1fc09','git -c core.autocrlf=false checkout --detach '+FIX],'not_executed':['New P5 business SDK (not implemented)','New P5 implementation tests','Real accounts/ACL/admin lifecycle','Formal Test/financial approval','Merge/tag/deployment/live/P6'],'limits':['No independent rerun of844 product SDK this turn; raw postmerge archive verified as developer P4 execution','PR8 CI status verified by direct run API after filtered connector empty result; new CI artifacts not downloaded','Initial helper C03 raw-open illustrative literal corrected from.40 to.41 and tick formula assertion added; initial script/JSON and both command logs retained']})
print(json.dumps({'fixed_sha':FIX,'clean':True,'plan_files':len([p for p in P.rglob('*') if p.is_file()]),'frozen_files':131,'external_old_archives':len(ext),'PR_drift_to':end['head_sha']}))
