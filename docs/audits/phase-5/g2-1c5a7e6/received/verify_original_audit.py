from pathlib import Path
import hashlib,json,zipfile,subprocess
O=Path(__file__).parent;OLD=O.parent/'p5-g2-003-recheck-bf5e5a8-independent';C=Path('E:/WORK/AQRP-audits/p5-1c5a7e6/src');R=C/'docs/audits/phase-5/g2-bf5e5a8';PREV='bf5e5a89209f2dd24042cd806626f832b531de52';FIX='1c5a7e62cace7c3e66b7cc7f12fd564cb0013654'
H=lambda b:hashlib.sha256(b).hexdigest();git=lambda *a:subprocess.check_output(['git','-C',str(C),*a])
p=OLD/'EVIDENCE.zip'
with p.open('rb') as f:oldsha=hashlib.file_digest(f,'sha256').hexdigest()
assert p.stat().st_size==589653932 and oldsha=='2b7b547a3e8b80e28d72160efb65aa485999af487febba442c88b579d788cc29'
with zipfile.ZipFile(p) as z:
 assert z.testzip() is None
 m=json.loads(z.read('EVIDENCE_MANIFEST.json'));assert len(m['files'])==176 and len(z.namelist())==177
 for e in m['files']:
  with z.open(e['path']) as f:assert hashlib.file_digest(f,'sha256').hexdigest()==e['sha256']
  assert z.getinfo(e['path']).file_size==e['bytes']
 matched=[]
 for p in (R/'received').rglob('*'):
  if p.is_file():
   rel=p.relative_to(R/'received').as_posix();original=z.read(rel) if rel in z.namelist() else (OLD/rel).read_bytes();assert p.read_bytes()==original,rel;matched.append(rel)
 assert {'REPORT.md','FINDINGS.json','settled_short_backing_probe.py','SETTLED_SHORT_BACKING_PROBE.json','RECEIPT.json'}<=set(matched)
assert (R/'PRE_REPAIR_IDENTITY.json').read_bytes()==git('show',PREV+':docs/audits/phase-5/IMPLEMENTATION_IDENTITY.json')
diff=git('diff','--name-only',PREV,FIX,'--','src/aqrp').decode().splitlines();assert set(diff)=={'src/aqrp/__init__.py','src/aqrp/backtest/ledger.py','src/aqrp/backtest/transactions.py','src/aqrp/factors/reviewed_code.json','src/aqrp/services/backtest.py'}
for e in json.loads((R/'REPAIR_IDENTITY.json').read_bytes())['financial_code_changes']:
 assert H((C/e['path']).read_bytes())==e['new_sha256'] and H(git('show',PREV+':'+e['path']))==e['old_sha256']
D=O.parent/'p5-g2-backing-recheck-1c5a7e6';err=json.loads((D/'POST_SEAL_PUBLISH_HELPER_ERRATA.json').read_bytes());assert H((D/'publish_final.actual.py').read_bytes())==err['actual_script_sha256']
with zipfile.ZipFile(D/'Evidence.zip') as z:assert H(z.read(err['unexecuted_draft_inside_archive']))==err['draft_sha256']
report=dict(fixed_sha=FIX,original_audit_sha256=oldsha,original_bytes=589653932,original_members_verified=177,received_original_files_byte_identical=matched,parent_identity_original_bytes_preserved=True,business_module_changes=diff,post_seal_helper_sidecars_hashes_verified=True,sidecars_claimed_inside_original_manifest=False,result='PASS')
(O/'ORIGINAL_AUDIT_PRESERVATION.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(dict(original_members=177,received_files_compared=len(matched),originals_unchanged='PASS')))
