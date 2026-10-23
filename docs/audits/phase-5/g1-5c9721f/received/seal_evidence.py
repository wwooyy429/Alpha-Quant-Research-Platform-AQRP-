import pathlib,json,hashlib,zipfile,datetime
O=pathlib.Path(__file__).parent;FIX='5c9721f96679f4d495b7b3b93af3e2e31e66ae62'
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
assert json.loads((O/'prepare-seal.command.json').read_bytes())['exit_code']==0
f=json.loads((O/'FINDINGS.json').read_bytes());assert f['verdict']=='PLAN BLOCKED / REQUEST CHANGES' and len(f['findings'])==4
assert json.loads((O/'REVIEW_EXECUTION.json').read_bytes())['porcelain']==[]
excluded={'EVIDENCE.zip','RECEIPT.json','EVIDENCE_MANIFEST.json','seal.stdout.log','seal.stderr.log','seal.command.json'}
files={p.name:p for p in O.iterdir() if p.is_file() and p.name not in excluded}
for d in ['fixed-plan','frozen-source','supporting-documents','developer-received','P4-baseline-evidence']:
 for p in (O/d).rglob('*'):
  if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc':files[p.relative_to(O).as_posix()]=p
entries=[{'path':n,'bytes':p.stat().st_size,'sha256':sha(p)} for n,p in sorted(files.items())]
manifest={'schema':'aqrp-gpt-work-phase5-g1-evidence/1','fixed_sha':FIX,'verdict':f['verdict'],'PR_final_head_not_reviewed':f['PR_head_at_end'],'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'reviewer':'GPT Work supplemental reviewer','files':entries,'self_excluded':True,'omitted':['Python/venv/cache/bytecode and full historical host image','Developer167126343-byte original Evidence.zip retained externally SHA256 58149088fd6f1e2ca7b77abfc4226489cae1fe5c06f4d94dc6e742e2f743b789','Full Fixed-Source.zip inside developer original verified to fixed Git bytes, not duplicated; current plan and131 frozen files included','Previous independent/developer P4 archives retained externally with rehashed bindings'],'not_claimed':'P5 business tests/implementation, G1 PASS, review of bd18d1b, real isolation, formal Test, financial approval, digital signature'}
save(O/'EVIDENCE_MANIFEST.json',manifest)
with zipfile.ZipFile(O/'EVIDENCE.zip','w',compression=zipfile.ZIP_DEFLATED,compresslevel=6,allowZip64=True) as z:
 for e in entries:
  p=files[e['path']];z.write(p,e['path'],compress_type=zipfile.ZIP_STORED if p.suffix.lower() in ('.zip','.whl') else zipfile.ZIP_DEFLATED)
 z.write(O/'EVIDENCE_MANIFEST.json','EVIDENCE_MANIFEST.json')
with zipfile.ZipFile(O/'EVIDENCE.zip') as z:
 assert z.testzip() is None and len(z.namelist())==len(entries)+1 and len(set(z.namelist()))==len(z.namelist())
 for e in entries:
  b=z.read(e['path']);assert len(b)==e['bytes'] and hashlib.sha256(b).hexdigest()==e['sha256'],e['path']
 assert z.read('EVIDENCE_MANIFEST.json')==(O/'EVIDENCE_MANIFEST.json').read_bytes()
 listing=[{'path':i.filename,'bytes':i.file_size,'crc32':format(i.CRC,'08x')} for i in z.infolist()]
receipt={'fixed_sha':FIX,'verdict':f['verdict'],'PR_final_head_not_reviewed':f['PR_head_at_end'],'archive':'EVIDENCE.zip','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'bytes':(O/'EVIDENCE.zip').stat().st_size,'sha256':sha(O/'EVIDENCE.zip'),'manifest_sha256':sha(O/'EVIDENCE_MANIFEST.json'),'manifest_files':len(entries),'zip_members':len(listing),'CRC_and_all_member_hashes_verified':True,'not_digital_signature':True,'listing':listing}
save(O/'RECEIPT.json',receipt);print(json.dumps({k:v for k,v in receipt.items() if k!='listing'}))
