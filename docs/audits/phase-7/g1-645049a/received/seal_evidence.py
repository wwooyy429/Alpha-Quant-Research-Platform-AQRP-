import json,hashlib,zipfile,datetime,sys,os,platform,subprocess
from pathlib import Path
O=Path(__file__).parent.resolve();start=datetime.datetime.now(datetime.timezone.utc).isoformat();H='645049ae9b08710ed93189b80547d14c87d80584';excluded={'EVIDENCE_MANIFEST.json','EVIDENCE.zip','RECEIPT.json','SEAL_EXECUTION.json'}
assert not (O/'EVIDENCE.zip').exists()
C=Path('E:/WORK/AQRP-audits/p7-645049a/src');assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=C).decode().strip()==H and not subprocess.check_output(['git','status','--porcelain'],cwd=C)
files=sorted(p for p in O.rglob('*') if p.is_file() and p.relative_to(O).as_posix() not in excluded)
rows=[{'path':p.relative_to(O).as_posix(),'bytes':p.stat().st_size,'sha256':hashlib.file_digest(p.open('rb'),'sha256').hexdigest()} for p in files]
manifest={'scope':'Independent Phase7 G1 incremental design recheck. Primary actual/supplemental/developer execution distinguished. Full received developer199866661-byte ZIP included, containing original previous G audit archive and fixed H source.','fixed_sha':H,'self_excluded':True,'external_seal_files':sorted(excluded),'files':rows}
mp=O/'EVIDENCE_MANIFEST.json';mp.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');z=O/'EVIDENCE.zip'
with zipfile.ZipFile(z,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6,allowZip64=True) as f:
 for p in files:f.write(p,p.relative_to(O).as_posix(),compress_type=zipfile.ZIP_STORED if p.suffix.lower()=='.zip' else zipfile.ZIP_DEFLATED)
 f.write(mp,mp.name)
with zipfile.ZipFile(z) as f:
 assert len(f.namelist())==len(rows)+1 and set(f.namelist())=={r['path'] for r in rows}|{mp.name}
 for r in rows:
  with f.open(r['path']) as b:h=hashlib.file_digest(b,'sha256').hexdigest()
  assert h==r['sha256'] and f.getinfo(r['path']).file_size==r['bytes']
 assert f.read(mp.name)==mp.read_bytes()
execution={'argv':[sys.executable,*sys.argv],'cwd':os.getcwd(),'started_utc':start,'ended_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'exit_code':0,'executor':'Primary GPT Work','fixed_sha':H,'environment':{'python':sys.version,'platform':platform.platform(),'machine':platform.machine(),'GIL_enabled':sys._is_gil_enabled()}}
ep=O/'SEAL_EXECUTION.json';ep.write_text(json.dumps(execution,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
receipt={'reviewed_sha':H,'previous_reviewed_sha':'3c34e3ca75c9799307b8a98b34f045b40988bbca','verdict':'PLAN PASS WITH CONDITIONS','findings':{'WORK-P7-G1-001':'CLOSED_DESIGN','WORK-P7-G1-002':'CLOSED_DESIGN'},'new_blocking_findings':0,'archive':'EVIDENCE.zip','bytes':z.stat().st_size,'sha256':hashlib.file_digest(z.open('rb'),'sha256').hexdigest(),'manifest_sha256':hashlib.sha256(mp.read_bytes()).hexdigest(),'manifest_files':len(rows),'zip_members':len(rows)+1,'all_CRC_exact_members_sizes_hashes_verified':True,'seal_execution_sha256':hashlib.sha256(ep.read_bytes()).hexdigest(),'report_sha256':hashlib.sha256((O/'REPORT.txt').read_bytes()).hexdigest(),'not_a_digital_signature':True,'pending_user_conditions':['C-P7-001','C-P7-002','C-P7-003 revised','C-P7-004'],'primary_static_candidates':36,'primary_abstract_assertions':394,'product_tests_executed':0,'implementation_authorized':False,'G2':'NOT PERFORMED','Windows_R2':'DEFERRED / NOT VERIFIED','formal_Test':'NOT RUN','financial_approval':'NONE','merge_tag_deploy_live':False,'created_utc':execution['ended_utc']}
(O/'RECEIPT.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(receipt,ensure_ascii=False))
