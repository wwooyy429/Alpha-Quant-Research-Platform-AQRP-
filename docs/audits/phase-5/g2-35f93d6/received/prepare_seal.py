from pathlib import Path
import json,subprocess,hashlib,shutil,zipfile,datetime
O=Path(__file__).parent;C=Path('E:/WORK/AQRP-audits/p5-35f93d6/src');D=O.parent/'p5-g2-recheck-35f93d6';S=Path('E:/WORK/AQRP-runs/gpt-p5-35f93d6-20261023/aqrp-e6171f64-5e4a-47c3-b7df-d73eb4d05b2d');A=C.parent
FIX='35f93d640a2304121131d947a465f57a951cf63f'
def H(b):return hashlib.sha256(b).hexdigest()
def sh(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(n,v):(O/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
assert json.loads((O/'FINDINGS.json').read_bytes())['verdict']=='G2 BLOCKED / REQUEST CHANGES'
for n in ['SCOPE_VERIFICATION.json','DEVELOPER_ARCHIVE_VERIFICATION.json','INDEPENDENT_SDK_VERIFICATION.json','RAW_FINANCIAL_RECONSTRUCTION.json','ORIGINAL_MATH_RESULTS.json','REVISION_MATH_RESULTS.json']:
 assert json.loads((O/n).read_bytes())['result']=='PASS',n
assert json.loads((O/'CANCELLATION_BOUNDARY_PROBE.json').read_bytes())['result']=='PASS'
assert json.loads((O/'SHORT_BUCKET_RECONCILIATION_PROBE.json').read_bytes())['result']=='REPRODUCED_MISMATCH'
assert json.loads((O/'REPAIR_PROBE_BINDINGS.json').read_bytes())['result']=='PASS'
pr=json.loads((O/'PR8_FINAL.json').read_bytes());assert pr['head_sha']==FIX and ('AQRP_FIXED_REVIEW_SHA: '+FIX) in pr['body'] and not pr['merged']
records=[]
for args in [('rev-parse','HEAD'),('status','--porcelain'),('symbolic-ref','-q','HEAD'),('diff','--check','32ea5d6b75c84c07017d87377eeabd2f78207c5c',FIX),('ls-remote','origin','refs/heads/main','refs/tags/*')]:
 argv=['git','-C',str(C),*args];p=subprocess.run(argv,capture_output=True);records.append({'argv':argv,'exit_code':p.returncode,'stdout':p.stdout.decode('utf-8'),'stderr':p.stderr.decode('utf-8')})
assert records[0]['stdout'].strip()==FIX and not records[1]['stdout'] and records[2]['exit_code']==1 and records[3]['exit_code']==0
assert records[-1]['stdout']==(O/'REMOTE_REFS_START.txt').read_text(encoding='utf-8')
save('FINAL_IDENTITY.json',{'fixed_sha':FIX,'reviewer':'GPT Work supplemental reviewer','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'PR_head_description_lock_stable':True,'main_old_tags_unchanged':True,'clean_detached':True,'git_records':records,'no_external_messages_merge_tags_deploy':True})
# Self-produced SDK evidence archive: no claim that this is an official GitHub ZIP.
selection=json.loads((S/'upload-selection.json').read_bytes());entries=selection['files']
with zipfile.ZipFile(O/'independent-sdk-artifacts.zip','w',compression=zipfile.ZIP_DEFLATED,compresslevel=6,allowZip64=True) as z:
 for e in entries:
  p=S/e['path'];assert H(p.read_bytes())==e['sha256'];z.write(p,e['path'],compress_type=zipfile.ZIP_STORED if p.suffix.lower() in ['.zip','.whl'] else zipfile.ZIP_DEFLATED)
 z.write(S/'upload-selection.json','upload-selection.json')
with zipfile.ZipFile(O/'independent-sdk-artifacts.zip') as z:
 assert z.testzip() is None and set(z.namelist())=={e['path'] for e in entries}|{'upload-selection.json'}
 for e in entries:assert H(z.read(e['path']))==e['sha256']
proof=[]
with zipfile.ZipFile(O/'reviewer-production-artifacts.zip','w',compression=zipfile.ZIP_DEFLATED,compresslevel=6,allowZip64=True) as z:
 for name in ['probes','cancellation-boundary','extended-repair','short-bucket-reconciliation']:
  for p in sorted((A/name).rglob('*')):
   if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc':
    n=p.relative_to(A).as_posix();proof.append({'path':n,'bytes':p.stat().st_size,'sha256':sh(p)});z.write(p,n)
 z.writestr('ARTIFACT_MANIFEST.json',json.dumps({'files':proof,'scope':'Actual GPT Work production/commit/recovery probes; not official CI or native OS isolation'},ensure_ascii=False,indent=2))
with zipfile.ZipFile(O/'reviewer-production-artifacts.zip') as z:
 assert z.testzip() is None
 for e in proof:assert H(z.read(e['path']))==e['sha256'] and len(z.read(e['path']))==e['bytes']
received=O/'developer-received';received.mkdir(exist_ok=True)
for n in ['Evidence.zip','RECEIPT.json','EVIDENCE_MANIFEST.json','FAILURE_AND_OMISSION_INDEX.json','GPT-Work-G2-Recheck-Instructions.txt']:
 shutil.copyfile(D/n,received/n)
assert sh(received/'Evidence.zip')=='773ab0d9e7485aebd107fbd3f092cdd1a0381fbfb412ba4a1a8b2f0b08bd7134'
source=O/'reviewed-source';source.mkdir()
for n in ['src/aqrp/services/backtest.py','src/aqrp/backtest/transactions.py','src/aqrp/backtest/ledger.py','src/aqrp/backtest/engine.py','src/aqrp/backtest/provider.py','src/aqrp/backtest/risk.py','src/aqrp/performance/metrics.py','src/aqrp/execution/model.py','docs/audits/phase-5/IMPLEMENTATION_AUTHORIZATION.json','docs/audits/phase-5/IMPLEMENTATION_CONTRACT.md','docs/audits/phase-5/IMPLEMENTATION_TRACEABILITY.md','docs/audits/phase-5/COMPATIBILITY_IMPACT.md','docs/audits/phase-5/IMPLEMENTATION_IDENTITY.json','AGENTS.md','docs/audits/phase-5/g2-bfdcf30/OUTPUT_CONTRACT_ERRATA.md','docs/audits/phase-5/g2-bfdcf30/REPAIR_IDENTITY.json','docs/audits/phase-5/g2-bfdcf30/DEVELOPER_RESPONSE.md']:
 p=source/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(C/n,p)
save('NESTED_ARCHIVE_BINDINGS.json',{'independent_sdk':{'archive':'independent-sdk-artifacts.zip','bytes':(O/'independent-sdk-artifacts.zip').stat().st_size,'sha256':sh(O/'independent-sdk-artifacts.zip'),'selected_files':len(entries),'scope':'GPT Work actual SDK selected raw artifacts; excludes regenerable venv/caches/source build, not official CI ZIP'},'production_probes':{'archive':'reviewer-production-artifacts.zip','bytes':(O/'reviewer-production-artifacts.zip').stat().st_size,'sha256':sh(O/'reviewer-production-artifacts.zip'),'files':len(proof)},'developer_original':{'archive':'developer-received/Evidence.zip','sha256':sh(received/'Evidence.zip'),'nested_original_official_ZIPs_preserved':True},'all_nested_CRC_members_hashes_reverified':True})
print(json.dumps({'fixed_sha':FIX,'clean_detached':True,'independent_SDK_selected':len(entries),'production_probe_files':len(proof),'all_originals_preserved':'PASS'}))
