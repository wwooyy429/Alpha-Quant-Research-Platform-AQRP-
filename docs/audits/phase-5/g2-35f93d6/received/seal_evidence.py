from pathlib import Path
import hashlib,json,zipfile,datetime
O=Path(__file__).parent;FIX='35f93d640a2304121131d947a465f57a951cf63f'
def sh(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
assert json.loads((O/'prepare-seal-rerun-1.command.json').read_bytes())['exit_code']==0
f=json.loads((O/'FINDINGS.json').read_bytes());assert f['verdict']=='G2 BLOCKED / REQUEST CHANGES'
excluded={'EVIDENCE.zip','RECEIPT.json','EVIDENCE_MANIFEST.json','seal.stdout.log','seal.stderr.log','seal.command.json'}
files={p.relative_to(O).as_posix():p for p in O.rglob('*') if p.is_file() and p.relative_to(O).as_posix() not in excluded and '__pycache__' not in p.parts and p.suffix!='.pyc'}
entries=[{'path':n,'bytes':p.stat().st_size,'sha256':sh(p)} for n,p in sorted(files.items())]
m={'schema':'aqrp-gpt-work-phase5-g2-evidence/1','fixed_sha':FIX,'verdict':f['verdict'],'reviewer':'GPT Work supplemental reviewer','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'files':entries,'self_excluded':True,'omissions':['Manifest self, archive/receipt and sealing finalization logs are beside archive to avoid circular hashing','Regenerable new SDK venv/cache/build-source directories omitted; selected7229 actual files and selection included in nested SDK archive','Full historical host image and deferred real isolation/formal Test/financial approval not executed','Developer exploratory roots not bundled by developer remain expressly external per received omission index'],'not_claimed':['G2 PASS or human acceptance','Digital signature or native OS sandbox','Formal Test/financial approval/merge/tags/deployment/live/P6']}
save(O/'EVIDENCE_MANIFEST.json',m)
with zipfile.ZipFile(O/'EVIDENCE.zip','w',compression=zipfile.ZIP_DEFLATED,compresslevel=6,allowZip64=True) as z:
 for e in entries:
  p=files[e['path']];z.write(p,e['path'],compress_type=zipfile.ZIP_STORED if p.suffix.lower() in ['.zip','.whl'] else zipfile.ZIP_DEFLATED)
 z.write(O/'EVIDENCE_MANIFEST.json','EVIDENCE_MANIFEST.json')
with zipfile.ZipFile(O/'EVIDENCE.zip') as z:
 assert z.testzip() is None and len(z.namelist())==len(set(z.namelist()))==len(entries)+1
 assert set(z.namelist())=={e['path'] for e in entries}|{'EVIDENCE_MANIFEST.json'}
 for e in entries:
  b=z.read(e['path']);assert len(b)==e['bytes'] and hashlib.sha256(b).hexdigest()==e['sha256'],e['path']
 assert z.read('EVIDENCE_MANIFEST.json')==(O/'EVIDENCE_MANIFEST.json').read_bytes()
r={'fixed_sha':FIX,'verdict':f['verdict'],'archive':'EVIDENCE.zip','bytes':(O/'EVIDENCE.zip').stat().st_size,'sha256':sh(O/'EVIDENCE.zip'),'manifest_sha256':sh(O/'EVIDENCE_MANIFEST.json'),'manifest_files':len(entries),'zip_members':len(entries)+1,'CRC_exact_members_all_hashes_verified':True,'findings':{'original001':'CLOSED','original002':'CLOSED','new003':'High OPEN'},'not_digital_signature':True,'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
save(O/'RECEIPT.json',r);print(json.dumps(r))
