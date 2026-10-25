import json,hashlib,zipfile,datetime,sys,os,subprocess
from pathlib import Path
O=Path(__file__).parent.resolve();started=datetime.datetime.now(datetime.timezone.utc).isoformat();G='3c34e3ca75c9799307b8a98b34f045b40988bbca'
excluded={'EVIDENCE_MANIFEST.json','EVIDENCE.zip','RECEIPT.json','SEAL_EXECUTION.json'}
assert not (O/'EVIDENCE.zip').exists() and not (O/'RECEIPT.json').exists()
C=Path('E:/WORK/AQRP-audits/p7-3c34e3c/src')
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=C).decode().strip()==G
assert not subprocess.check_output(['git','status','--porcelain'],cwd=C)
# Empty stdout from the three retained failed script attempts: no output preceded their exceptions.
for label in ['primary-math','primary-budget-probe','primary-scope']:
 p=O/(label+'-first-attempt.stdout.log')
 if not p.exists():p.write_bytes(b'')
files=sorted(p for p in O.rglob('*') if p.is_file() and p.relative_to(O).as_posix() not in excluded)
rows=[]
for p in files:rows.append({'path':p.relative_to(O).as_posix(),'bytes':p.stat().st_size,'sha256':hashlib.file_digest(p.open('rb'),'sha256').hexdigest()})
manifest={'scope':'Independent Phase7 G1 review at fixed G; primary and supplemental/developer execution explicitly separated; original P7 Evidence ZIP included. Original 1.16GB Phase6 release archive remains external and indexed.','reviewed_sha':G,'self_excluded':True,'external_seal_files':sorted(excluded),'files':rows}
mp=O/'EVIDENCE_MANIFEST.json';mp.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
z=O/'EVIDENCE.zip'
with zipfile.ZipFile(z,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6,allowZip64=True) as f:
 for p in files:f.write(p,p.relative_to(O).as_posix())
 f.write(mp,mp.name)
with zipfile.ZipFile(z) as f:
 assert len(f.namelist())==len(rows)+1 and set(f.namelist())=={r['path'] for r in rows}|{mp.name}
 for r in rows:
  with f.open(r['path']) as src:h=hashlib.file_digest(src,'sha256').hexdigest()
  assert h==r['sha256'] and f.getinfo(r['path']).file_size==r['bytes']
 assert f.read(mp.name)==mp.read_bytes()
execution={'argv':[sys.executable,*sys.argv],'cwd':os.getcwd(),'started_utc':started,'ended_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'exit_code':0,'fixed_sha':G,'executor':'Primary GPT Work'}
ep=O/'SEAL_EXECUTION.json';ep.write_text(json.dumps(execution,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
receipt={'reviewed_sha':G,'verdict':'PLAN BLOCKED / REQUEST CHANGES','findings':{'WORK-P7-G1-001':'High OPEN blocking','WORK-P7-G1-002':'Medium OPEN blocking'},'archive':'EVIDENCE.zip','bytes':z.stat().st_size,'sha256':hashlib.file_digest(z.open('rb'),'sha256').hexdigest(),'manifest_sha256':hashlib.sha256(mp.read_bytes()).hexdigest(),'manifest_files':len(rows),'zip_members':len(rows)+1,'all_CRC_exact_members_sizes_hashes_verified':True,'seal_execution_sha256':hashlib.sha256(ep.read_bytes()).hexdigest(),'report_sha256':hashlib.sha256((O/'REPORT.txt').read_bytes()).hexdigest(),'not_a_digital_signature':True,'external_P6_release_archive':json.loads((O/'PRIMARY_SCOPE.json').read_bytes())['archives'][1],'primary_math':'19sections/1007 assertions and768 financial model paths; design only','primary_budget_probe':'Existing P6 admission only,no worker/research()/simulation','implementation_authorized':False,'Windows_R2':'DEFERRED / NOT VERIFIED','formal_Test':'NOT RUN','financial_approval':'NONE','merge_tag_deploy_live':False,'created_utc':execution['ended_utc']}
(O/'RECEIPT.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(receipt,ensure_ascii=False))
