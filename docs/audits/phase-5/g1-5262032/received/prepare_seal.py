from pathlib import Path
import json,shutil,subprocess,hashlib,datetime
O=Path(__file__).parent;C=O.parent/'p5-g1-review-5262032';D=O.parent/'p5-g1-repair-5262032'
FIX='5262032bee4f631f68763e57510e1878945f6b8c'
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(n,v):(O/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
assert json.loads((O/'SCOPE_VERIFICATION.json').read_bytes())['result']=='PASS'
assert json.loads((O/'ORIGINAL_MATH_RESULTS.json').read_bytes())['assertions']==70
assert json.loads((O/'REVISION_MATH_RESULTS.json').read_bytes())['leaf_assertions']==209
findings=json.loads((O/'FINDINGS.json').read_bytes());assert len(findings['findings'])==4 and all(f['status']=='CLOSED_DESIGN' for f in findings['findings'])
assert not findings['implementation_authorized']
records=[]
for args in [('rev-parse','HEAD'),('status','--porcelain'),('diff','--stat','32ea5d6b75c84c07017d87377eeabd2f78207c5c',FIX),('log','-5','--format=%H %s'),('symbolic-ref','-q','HEAD')]:
 argv=['git','-C',str(C),*args];p=subprocess.run(argv,capture_output=True)
 records.append({'argv':argv,'exit_code':p.returncode,'stdout':p.stdout.decode('utf-8'),'stderr':p.stderr.decode('utf-8')})
assert records[0]['stdout'].strip()==FIX and not records[1]['stdout'] and records[-1]['exit_code']==1
save('REVIEW_EXECUTION.json',{'fixed_sha':FIX,'executor':'GPT Work supplemental reviewer','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'porcelain':[],'detached':True,'git_records':records,'runtime_sha256':sha(Path(__import__('sys').executable)),'validation_commands':'*.command.json with full argv/cwd/UTC start/end/exit','bootstrap_note':'Detached review clone/fetch was performed through the session tool trace before validation runner creation; current identity independently rechecked. No invented historical command receipts.'})
shutil.copytree(C/'docs/audits/phase-5',O/'fixed-plan')
support=O/'supporting-documents';support.mkdir()
for path in ['AGENTS.md','README.md','docs/BACKTEST_CONTRACT.md','docs/REVIEW_PROTOCOL.md','docs/requirements.csv','docs/audits/windows-isolation-deferral/DEFERRAL_POLICY.md','docs/audits/phase-4/BASELINE.md','docs/audits/phase-4/g2-18439f3/IDENTITY.json','docs/audits/phase-4/FROZEN_INPUTS.json']:
 p=support/path;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(C/path,p)
received=O/'developer-received';received.mkdir()
for name in ['Evidence.zip','RECEIPT.json','EVIDENCE_MANIFEST.json','GPT-Work-G1-Recheck-Instructions.txt']:
 shutil.copyfile(D/name,received/name)
assert sha(received/'Evidence.zip')=='131f02b58473c01bb96e9fb32f59965fe6d72f3a516331984b61614d9addbadc'
print(json.dumps({'fixed_sha':FIX,'clean':True,'reviewed_plan_copied':True,'full_original_developer_handoff_copied':True,'result':'PASS'}))
