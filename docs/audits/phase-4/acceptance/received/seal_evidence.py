import pathlib,json,hashlib,zipfile,datetime,shutil
O=pathlib.Path(__file__).parent;SDK=pathlib.Path((O/'SDK_LOCATION.txt').read_text(encoding='utf-8'));FIX='3c8757949b0fd5c97953b06a74ebc2d0e56676e4'
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
assert not (O/'transient-download.json').exists()
assert json.loads((O/'FINDINGS.json').read_bytes())['verdict']=='G2 PASS — RESTRICTED ENGINEERING SCOPE'
assert json.loads((O/'prepare-seal.command.json').read_bytes())['exit_code']==0
D=O.parent/'work-p4-g2-repair-3c87579';received=O/'developer-received';received.mkdir(exist_ok=True)
for n in ['Developer-GPT-Work-Recheck-Request.txt','Developer-Evidence-Seal.json','EVIDENCE_MANIFEST.json','VALIDATION.json','PR6-Final-Receipt.json','REMOTE_REFS.txt']:shutil.copyfile(D/n,received/n)
exclude={'EVIDENCE.zip','RECEIPT.json','EVIDENCE_MANIFEST.json','seal.stdout.log','seal.stderr.log','seal.command.json'}
files={p.name:p for p in O.iterdir() if p.is_file() and p.name not in exclude}
for d in ['fixed-source','evidence-extracts','independent-runs','repair-runs','publication-controls','parent-copies','parent-original','old-draft-rejection-runs','original-probes','scanner-controls','developer-received']:
 for p in (O/d).rglob('*'):
  if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc':files[p.relative_to(O).as_posix()]=p
selection=json.loads((SDK/'upload-selection.json').read_bytes())
for e in selection['files']:
 p=SDK/e['path'];assert sha(p)==e['sha256'];files['local-sdk/'+e['path']]=p
files['local-sdk/upload-selection.json']=SDK/'upload-selection.json'
entries=[{'path':n,'bytes':p.stat().st_size,'sha256':sha(p)} for n,p in sorted(files.items())]
manifest={'schema':'aqrp-gpt-work-phase4-g2-recheck-evidence/1','fixed_sha':FIX,'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'verdict':'G2 PASS — RESTRICTED ENGINEERING SCOPE','reviewer':'GPT Work supplemental reviewer','files':entries,'local_sdk_selected_files':len(selection['files']),'self_excluded':True,'omitted':['SDK venv and reproduction venv, caches/bytecode, tools binary (hash in actual scan evidence), expanded SDK source copy','pytest temporary/cache directories; required script bytes, outputs and receipts retained','Developer 401144916-byte original ZIP retained externally with SHA256 cafad304d48d62c85134938835f76c1bfb75b696d66975c0af71d97512014850','Previous independent 332130266-byte original ZIP retained externally with SHA256 6ee677b012669dc2cd9f47598386baeef2da453d40767447497abe571d86a170'],'not_claimed':'Digital signature, OS isolation, formal Test, financial approval, full historical host image'}
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
receipt={'fixed_sha':FIX,'verdict':manifest['verdict'],'archive':'EVIDENCE.zip','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'bytes':(O/'EVIDENCE.zip').stat().st_size,'sha256':sha(O/'EVIDENCE.zip'),'manifest_sha256':sha(O/'EVIDENCE_MANIFEST.json'),'manifest_files':len(entries),'zip_members':len(listing),'CRC_and_all_member_hashes_verified':True,'not_digital_signature':True,'listing':listing}
save(O/'RECEIPT.json',receipt);print(json.dumps({k:v for k,v in receipt.items() if k!='listing'}))
