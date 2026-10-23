from pathlib import Path
import json,hashlib,zipfile,datetime,subprocess
O=Path(__file__).parent;FIX='1c5a7e62cace7c3e66b7cc7f12fd564cb0013654';C=Path('E:/WORK/AQRP-audits/p5-1c5a7e6/src')
def H(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
for name in ['PR8_START.json','PR8_FINAL.json','PR8_SEAL.json']:
 p=json.loads((O/name).read_bytes());assert p['head_sha']==FIX and p['body'].splitlines()[0]=='AQRP_FIXED_REVIEW_SHA: '+FIX and not p['merged']
findings=json.loads((O/'FINDINGS.json').read_bytes());assert findings['G2']=='PASS — RESTRICTED ENGINEERING SCOPE' and not findings['open_blocking_findings']
for f in findings['findings']:assert f['status']=='CLOSED — FIX VERIFIED'
assert subprocess.check_output(['git','-C',str(C),'status','--porcelain'])==b''
assert subprocess.check_output(['git','-C',str(C),'ls-remote','origin','refs/heads/main','refs/tags/*']).decode()==(O/'REMOTE_REFS_START.txt').read_text(encoding='utf-8')
(O/'AUDIT_SCRIPTS_FINAL_HASHES.json').write_text(json.dumps(dict(files=[dict(path=p.name,sha256=H(p)) for p in sorted(O.glob('*.py'))],note='Original adaptation log retained; final hashes include added independent context/source/anchor/proof checks and final report/sealing scripts'),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
excluded={'EVIDENCE.zip','EVIDENCE_MANIFEST.json','RECEIPT.json','seal.command.json','seal.stdout.log','seal.stderr.log'}
files=[p for p in sorted(O.rglob('*')) if p.is_file() and p.relative_to(O).as_posix() not in excluded and '__pycache__' not in p.parts]
entries=[dict(path=p.relative_to(O).as_posix(),bytes=p.stat().st_size,sha256=H(p)) for p in files]
manifest=(json.dumps(dict(fixed_sha=FIX,executor='GPT Work supplemental reviewer',G2='PASS — RESTRICTED ENGINEERING SCOPE',finding003='CLOSED — FIX VERIFIED',created_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),files=entries,self_excluded=True,excluded_finalization=sorted(excluded),not_a_digital_signature=True),ensure_ascii=False,indent=2)+'\n').encode();(O/'EVIDENCE_MANIFEST.json').write_bytes(manifest)
archive=O/'EVIDENCE.zip';assert not archive.exists()
with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6,allowZip64=True) as z:
 for p,e in zip(files,entries):z.write(p,e['path'],compress_type=zipfile.ZIP_STORED if p.suffix=='.zip' else zipfile.ZIP_DEFLATED)
 z.writestr('EVIDENCE_MANIFEST.json',manifest)
with zipfile.ZipFile(archive) as z:
 assert z.testzip() is None and len(z.namelist())==len(set(z.namelist()))==len(entries)+1 and set(z.namelist())=={e['path'] for e in entries}|{'EVIDENCE_MANIFEST.json'}
 assert z.read('EVIDENCE_MANIFEST.json')==manifest
 for e in entries:
  assert z.getinfo(e['path']).file_size==e['bytes']
  with z.open(e['path']) as f:assert hashlib.file_digest(f,'sha256').hexdigest()==e['sha256'],e['path']
r=dict(fixed_sha=FIX,verdict='G2 PASS — RESTRICTED ENGINEERING SCOPE',requirements=12,finding003='CLOSED — FIX VERIFIED',finding001='CLOSED — FIX VERIFIED; regression PASS',finding002='CLOSED — FIX VERIFIED; regression PASS',archive='EVIDENCE.zip',bytes=archive.stat().st_size,sha256=H(archive),manifest_sha256=H(O/'EVIDENCE_MANIFEST.json'),manifest_files=len(entries),zip_members=len(entries)+1,CRC_exact_members_all_sizes_and_hashes_verified=True,executor='GPT Work supplemental reviewer',not_a_digital_signature=True,user_phase_acceptance=False,formal_Test=False,financial_approval='NONE',Windows_R2='DEFERRED / NOT VERIFIED',full_historical_host='NOT VERIFIED beyond accepted package/lock/oldRef/result replay scope',merge_tag_deploy_live_P6=False,created_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
(O/'RECEIPT.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(r,ensure_ascii=False))
