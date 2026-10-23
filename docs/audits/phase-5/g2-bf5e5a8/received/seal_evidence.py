from pathlib import Path
import json,hashlib,zipfile,datetime,subprocess
O=Path(__file__).parent;FIX='bf5e5a89209f2dd24042cd806626f832b531de52';C=Path('E:/WORK/AQRP-audits/p5-bf5e5a8/src')
def H(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
for name in ['PR8_START.json','PR8_FINAL.json','PR8_SEAL.json']:
 p=json.loads((O/name).read_bytes());assert p['head_sha']==FIX and p['body'].splitlines()[0]=='AQRP_FIXED_REVIEW_SHA: '+FIX and not p['merged']
assert subprocess.check_output(['git','-C',str(C),'status','--porcelain'])==b''
assert subprocess.check_output(['git','-C',str(C),'ls-remote','origin','refs/heads/main','refs/tags/*']).decode()==(O/'REMOTE_REFS_START.txt').read_text(encoding='utf-8')
scripts=[dict(path=p.name,sha256=H(p)) for p in sorted(O.glob('*.py'))]
(O/'AUDIT_SCRIPTS_FINAL_HASHES.json').write_text(json.dumps(dict(files=scripts,note='Initial adaptation log retained; current hashes include later verifier bindings and new independent probes/sealing scripts'),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
excluded={'EVIDENCE.zip','EVIDENCE_MANIFEST.json','RECEIPT.json','seal.command.json','seal.stdout.log','seal.stderr.log'}
files=[p for p in sorted(O.rglob('*')) if p.is_file() and p.relative_to(O).as_posix() not in excluded and '__pycache__' not in p.parts]
entries=[dict(path=p.relative_to(O).as_posix(),bytes=p.stat().st_size,sha256=H(p)) for p in files]
m=dict(fixed_sha=FIX,executor='GPT Work supplemental reviewer',G2='BLOCKED / REQUEST CHANGES',created_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),files=entries,self_excluded=True,excluded_finalization=list(sorted(excluded)),not_a_digital_signature=True)
manifest=(json.dumps(m,ensure_ascii=False,indent=2)+'\n').encode();(O/'EVIDENCE_MANIFEST.json').write_bytes(manifest)
archive=O/'EVIDENCE.zip';assert not archive.exists()
with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6,allowZip64=True) as z:
 for p,e in zip(files,entries):z.write(p,e['path'],compress_type=zipfile.ZIP_STORED if p.suffix=='.zip' else zipfile.ZIP_DEFLATED)
 z.writestr('EVIDENCE_MANIFEST.json',manifest)
with zipfile.ZipFile(archive) as z:
 assert z.testzip() is None and len(z.namelist())==len(set(z.namelist()))==len(entries)+1
 assert set(z.namelist())=={e['path'] for e in entries}|{'EVIDENCE_MANIFEST.json'}
 assert z.read('EVIDENCE_MANIFEST.json')==manifest
 for e in entries:
  assert z.getinfo(e['path']).file_size==e['bytes']
  with z.open(e['path']) as f:assert hashlib.file_digest(f,'sha256').hexdigest()==e['sha256'],e['path']
r=dict(fixed_sha=FIX,verdict='G2 BLOCKED / REQUEST CHANGES',finding003='High OPEN / PARTIAL FIX',finding001='CLOSED — FIX VERIFIED; regression PASS',finding002='CLOSED — FIX VERIFIED; regression PASS',archive='EVIDENCE.zip',bytes=archive.stat().st_size,sha256=H(archive),manifest_sha256=H(O/'EVIDENCE_MANIFEST.json'),manifest_files=len(entries),zip_members=len(entries)+1,CRC_exact_members_all_sizes_and_hashes_verified=True,executor='GPT Work supplemental reviewer',not_a_digital_signature=True,formal_Test=False,financial_approval='NONE',Windows_R2='DEFERRED / NOT VERIFIED',merge_tag_deploy_live_P6=False,created_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
(O/'RECEIPT.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(r,ensure_ascii=False))
