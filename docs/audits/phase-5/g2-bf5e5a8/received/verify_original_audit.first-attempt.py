from pathlib import Path
import hashlib,json,zipfile,subprocess
O=Path(__file__).parent;OLD=O.parent/'p5-g2-recheck-35f93d6-independent';C=Path('E:/WORK/AQRP-audits/p5-bf5e5a8/src');R=C/'docs/audits/phase-5/g2-35f93d6'
FIX='bf5e5a89209f2dd24042cd806626f832b531de52';PREV='35f93d640a2304121131d947a465f57a951cf63f'
H=lambda b:hashlib.sha256(b).hexdigest()
git=lambda *a:subprocess.check_output(['git','-C',str(C),*a])
zpath=OLD/'EVIDENCE.zip'
with zpath.open('rb') as f:oldsha=hashlib.file_digest(f,'sha256').hexdigest()
assert oldsha=='11b354600fa80c8d806ebddf75bfbf3b1f976fca888a3d98a168ad345aadc51f' and zpath.stat().st_size==585039742
with zipfile.ZipFile(zpath) as z:
 assert z.testzip() is None
 manifest=json.loads(z.read('EVIDENCE_MANIFEST.json'));assert len(manifest['files'])==150 and len(z.namelist())==151
 for e in manifest['files']:
  b=z.read(e['path']);assert H(b)==e['sha256'] and len(b)==e['bytes'],e['path']
 matched=[]
 for p in (R/'received').rglob('*'):
  if p.is_file():
   rel=p.relative_to(R/'received').as_posix();assert rel in z.namelist(),rel
   assert p.read_bytes()==z.read(rel),rel;matched.append(rel)
 assert {'REPORT.md','FINDINGS.json','short_bucket_reconciliation_probe.py','extended_repair_checks.py','RECEIPT.json'}<=set(matched)
assert (R/'PRE_REPAIR_IDENTITY.json').read_bytes()==git('show',PREV+':docs/audits/phase-5/IMPLEMENTATION_IDENTITY.json')
diff=git('diff','--name-only',PREV,FIX,'--','src/aqrp').decode().splitlines()
assert set(diff)=={'src/aqrp/__init__.py','src/aqrp/backtest/ledger.py','src/aqrp/factors/reviewed_code.json','src/aqrp/services/backtest.py'}
repair=json.loads((R/'REPAIR_IDENTITY.json').read_bytes())
for e in repair['financial_code_changes']:
 assert H((C/e['path']).read_bytes())==e['new_sha256']
 assert H(git('show',PREV+':'+e['path']))==e['old_sha256']
correction=json.loads((R/'PRESERVATION_CORRECTION.json').read_bytes());restored=[]
for e in correction['restored']:
 raw=(C/e['path']).read_bytes();assert raw==git('show',PREV+':'+e['path']) and H(raw)==e['restored_sha256']
 bad=git('show',correction['failed_sha']+':'+e['path']);assert H(bad)==e['erroneous_output_sha256'] and raw!=bad
 restored.append(e)
assert git('diff',correction['failed_sha'],FIX,'--','src','tests','tools','requirements.lock','pyproject.toml','.github')==b''
report={'fixed_sha':FIX,'original_audit_sha256':oldsha,'original_bytes':585039742,'original_members_verified':151,'received_original_files_byte_identical':matched,'parent_identity_original_bytes_preserved':True,'business_module_changes':diff,'three_restored_historical_records':restored,'failed_candidate_business_tests_guard_unchanged':True,'result':'PASS'}
(O/'ORIGINAL_AUDIT_PRESERVATION.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({'original_members':151,'received_files_compared':len(matched),'three_restored':3,'originals_unchanged':'PASS'}))
