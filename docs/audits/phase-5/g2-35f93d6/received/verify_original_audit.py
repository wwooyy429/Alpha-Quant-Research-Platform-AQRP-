from pathlib import Path
import hashlib,json,zipfile,subprocess
O=Path(__file__).parent;OLD=O.parent/'p5-g2-bfdcf30-independent';C=Path('E:/WORK/AQRP-audits/p5-35f93d6/src');R=C/'docs/audits/phase-5/g2-bfdcf30'
H=lambda b:hashlib.sha256(b).hexdigest()
zpath=OLD/'EVIDENCE.zip'
with zpath.open('rb') as f:oldsha=hashlib.file_digest(f,'sha256').hexdigest()
assert oldsha=='e68d2c5ad5b410b19a85e2159ae63b5a134130a335a6a3d43e3a1c439b542adf' and zpath.stat().st_size==585712844
with zipfile.ZipFile(zpath) as z:
 assert z.testzip() is None
 manifest=json.loads(z.read('EVIDENCE_MANIFEST.json'));assert len(manifest['files'])==124 and len(z.namelist())==125
 for e in manifest['files']:assert H(z.read(e['path']))==e['sha256'] and len(z.read(e['path']))==e['bytes'],e['path']
 matched=[]
 for p in (R/'received').rglob('*'):
  if p.is_file():
   rel=p.relative_to(R/'received').as_posix()
   if rel in z.namelist():assert p.read_bytes()==z.read(rel),rel;matched.append(rel)
 assert {'REPORT.md','FINDINGS.json','cancellation_boundary_probe.py','production_probes.py'}<=set(matched)
assert (R/'PRE_REPAIR_IDENTITY.json').read_bytes()==subprocess.check_output(['git','-C',str(C),'show','bfdcf30e525ff802ea483974f58163eedc029ce8:docs/audits/phase-5/IMPLEMENTATION_IDENTITY.json'])
diff=subprocess.check_output(['git','-C',str(C),'diff','--name-only','bfdcf30e525ff802ea483974f58163eedc029ce8','35f93d640a2304121131d947a465f57a951cf63f','--','src/aqrp']).decode().splitlines()
assert set(diff)=={'src/aqrp/__init__.py','src/aqrp/backtest/ledger.py','src/aqrp/backtest/transactions.py','src/aqrp/factors/reviewed_code.json','src/aqrp/services/backtest.py'}
repair=json.loads((R/'REPAIR_IDENTITY.json').read_bytes())
for e in repair['financial_code_changes']:
 assert H((C/e['path']).read_bytes())==e['new_sha256']
 assert H(subprocess.check_output(['git','-C',str(C),'show','bfdcf30e525ff802ea483974f58163eedc029ce8:'+e['path']]))==e['old_sha256']
report={'fixed_sha':'35f93d640a2304121131d947a465f57a951cf63f','original_audit_sha256':oldsha,'original_bytes':585712844,'original_members_verified':125,'received_original_files_byte_identical':matched,'parent_identity_original_bytes_preserved':True,'business_module_changes':diff,'result':'PASS'}
(O/'ORIGINAL_AUDIT_PRESERVATION.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({'original_members':125,'received_files_compared':len(matched),'originals_unchanged':'PASS'}))
