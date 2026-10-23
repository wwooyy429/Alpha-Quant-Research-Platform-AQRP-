from pathlib import Path
import json,hashlib,zipfile,datetime
O=Path(__file__).parent;FIX='5262032bee4f631f68763e57510e1878945f6b8c'
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
assert json.loads((O/'prepare-seal.command.json').read_bytes())['exit_code']==0
f=json.loads((O/'FINDINGS.json').read_bytes());assert f['verdict']=='PLAN PASS WITH CONDITIONS'
assert json.loads((O/'REVIEW_EXECUTION.json').read_bytes())['porcelain']==[]
excluded={'EVIDENCE.zip','RECEIPT.json','EVIDENCE_MANIFEST.json','seal.stdout.log','seal.stderr.log','seal.command.json'}
files={p.relative_to(O).as_posix():p for p in O.rglob('*') if p.is_file() and p.relative_to(O).as_posix() not in excluded and '__pycache__' not in p.parts and p.suffix!='.pyc'}
entries=[{'path':n,'bytes':p.stat().st_size,'sha256':sha(p)} for n,p in sorted(files.items())]
m={'schema':'aqrp-gpt-work-phase5-g1-recheck-evidence/1','fixed_sha':FIX,'verdict':f['verdict'],'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'reviewer':'GPT Work supplemental reviewer','files':entries,'self_excluded':True,'full_developer_original_archive_included':True,'full_original_prior_independent_archive_nested_inside_developer_original':True,'excluded':['Manifest self; outer receipt/archive; seal stdout/stderr/command finalization receipts kept beside archive to avoid circular hash','Python runtime/venv/caches and full historical host image'],'not_claimed':['P5 implementation or real crash-recovery tests','Unconditional G1/human acceptance/implementation authorization','Real Windows isolation or formal Test or financial approval','Digital signature']}
save(O/'EVIDENCE_MANIFEST.json',m)
with zipfile.ZipFile(O/'EVIDENCE.zip','w',compression=zipfile.ZIP_DEFLATED,compresslevel=6,allowZip64=True) as z:
 for e in entries:
  p=files[e['path']];z.write(p,e['path'],compress_type=zipfile.ZIP_STORED if p.suffix.lower() in ('.zip','.whl') else zipfile.ZIP_DEFLATED)
 z.write(O/'EVIDENCE_MANIFEST.json','EVIDENCE_MANIFEST.json')
with zipfile.ZipFile(O/'EVIDENCE.zip') as z:
 assert z.testzip() is None and len(z.namelist())==len(set(z.namelist()))==len(entries)+1
 assert set(z.namelist())=={e['path'] for e in entries}|{'EVIDENCE_MANIFEST.json'}
 for e in entries:
  b=z.read(e['path']);assert len(b)==e['bytes'] and hashlib.sha256(b).hexdigest()==e['sha256'],e['path']
 assert z.read('EVIDENCE_MANIFEST.json')==(O/'EVIDENCE_MANIFEST.json').read_bytes()
receipt={'fixed_sha':FIX,'verdict':f['verdict'],'archive':'EVIDENCE.zip','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'bytes':(O/'EVIDENCE.zip').stat().st_size,'sha256':sha(O/'EVIDENCE.zip'),'manifest_sha256':sha(O/'EVIDENCE_MANIFEST.json'),'manifest_files':len(entries),'zip_members':len(entries)+1,'CRC_exact_members_all_hashes_verified':True,'not_digital_signature':True,'implementation_authorized':False}
save(O/'RECEIPT.json',receipt);print(json.dumps(receipt))
