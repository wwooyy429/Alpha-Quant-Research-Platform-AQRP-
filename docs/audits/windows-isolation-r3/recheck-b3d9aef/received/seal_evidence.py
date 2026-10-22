import pathlib,json,hashlib,zipfile,datetime
O=pathlib.Path(__file__).parent;exclude={'EVIDENCE.zip','EVIDENCE_MANIFEST.json','RECEIPT.json','seal.stdout.log','seal.stderr.log'}
def H(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
files={p.name:p for p in O.iterdir() if p.is_file() and p.name not in exclude}
for name in ['fixed-source','evidence-extracts','received-developer','failed-sdk-extracts','new-nine-inputs','independent-factor-runs','model-tree','model-probe']:
 for p in (O/name).rglob('*'):
  if p.is_file():files[p.relative_to(O).as_posix()]=p
sdk=pathlib.Path(json.loads((O/'SDK_LOCATION.json').read_bytes())['sdk_root']);selection=json.loads((sdk/'upload-selection.json').read_bytes())
for e in selection['files']:
 p=sdk/e['path'];assert H(p)==e['sha256'];files['local-sdk/'+e['path']]=p
files['local-sdk/upload-selection.json']=sdk/'upload-selection.json'
state=json.loads((O/'REVIEW_EXECUTION.json').read_text(encoding='utf-8-sig'));assert state['porcelain']==[] and all(not a['Enabled'] for a in state['accounts'])
for step in ['scope','clean-sdk-short','counterexamples','nine-inputs','archives','prepare-seal']:assert json.loads((O/(step+'.command.json')).read_bytes())['exit_code']==0
assert json.loads((O/'clean-sdk.command.json').read_bytes())['exit_code']==1
entries=[{'path':n,'bytes':p.stat().st_size,'sha256':H(p)} for n,p in sorted(files.items())];manifest={'schema':'aqrp-gpt-work-windows-r3-review/1','reviewer':'GPT Work supplemental reviewer','fixed_sha':'b3d9aef79396db948d326f5ce247131f96739d9d','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'candidate_verdict':'REQUEST CHANGES / BLOCKED','overall_windows_isolation':'NOT VERIFIED','files':entries,'local_sdk_selected_files':len(selection['files']),'omitted':['SDK venvs, package/bytecode caches and expanded source trees','pytest temporary/cache directories','failed first SDK dependency environments and tools; original parent logs/environment and additional reproduction diagnosis are included','developer329420052-byte original archive is external, all103members independently verified; reference in ARCHIVE_VERIFICATION.json'],'external_developer_archive_sha256':'a27ef6ca5e899cda4baee3a1c212eaafc9555d1566adb41ec613f88597c049fd','self_excluded':True,'not_claimed':'New real three-principal execution, formal Test, deployment or full host snapshot'};save(O/'EVIDENCE_MANIFEST.json',manifest)
with zipfile.ZipFile(O/'EVIDENCE.zip','w',compression=zipfile.ZIP_DEFLATED,compresslevel=6,allowZip64=True) as z:
 for e in entries:
  p=files[e['path']];z.write(p,e['path'],compress_type=zipfile.ZIP_STORED if p.suffix in ['.zip','.whl'] else zipfile.ZIP_DEFLATED)
 z.write(O/'EVIDENCE_MANIFEST.json','EVIDENCE_MANIFEST.json')
with zipfile.ZipFile(O/'EVIDENCE.zip') as z:
 assert z.testzip() is None and len(z.namelist())==len(entries)+1
 for e in entries:
  b=z.read(e['path']);assert len(b)==e['bytes'] and hashlib.sha256(b).hexdigest()==e['sha256']
 assert z.read('EVIDENCE_MANIFEST.json')==(O/'EVIDENCE_MANIFEST.json').read_bytes()
 listing=[{'path':i.filename,'bytes':i.file_size,'crc32':format(i.CRC,'08x')} for i in z.infolist()]
receipt={'fixed_sha':manifest['fixed_sha'],'candidate_verdict':manifest['candidate_verdict'],'overall_windows_isolation':'NOT VERIFIED','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'zip':'EVIDENCE.zip','bytes':(O/'EVIDENCE.zip').stat().st_size,'sha256':H(O/'EVIDENCE.zip'),'manifest_sha256':H(O/'EVIDENCE_MANIFEST.json'),'manifest_files':len(entries),'zip_members':len(listing),'all_members_rehashed_and_crc_verified':True,'listing':listing,'not_digital_signature':True};save(O/'RECEIPT.json',receipt);print(json.dumps({k:v for k,v in receipt.items() if k!='listing'}))
