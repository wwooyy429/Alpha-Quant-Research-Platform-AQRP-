from pathlib import Path
import json,zipfile,hashlib,shutil,subprocess
O=Path(__file__).parent;D=O.parent/'p5-g2-backing-recheck-1c5a7e6';C=Path('E:/WORK/AQRP-audits/p5-1c5a7e6/src');A=C.parent
SDK=Path('E:/WORK/AQRP-runs/gpt-p5-1c5a7e6-20261023/aqrp-87d64547-3922-4678-b3a4-a5cf51d4da00');FIX='1c5a7e62cace7c3e66b7cc7f12fd564cb0013654';J=lambda n:json.loads((O/n).read_bytes());H=lambda b:hashlib.sha256(b).hexdigest()
for n in ['SCOPE_VERIFICATION.json','DEVELOPER_ARCHIVE_VERIFICATION.json','ORIGINAL_AUDIT_PRESERVATION.json','INDEPENDENT_SDK_VERIFICATION.json','RAW_FINANCIAL_RECONSTRUCTION.json','RETAINED_FAILURE_VERIFICATION.json','SHORT_BUCKET_RECONCILIATION_PROBE.json','CANCELLATION_BOUNDARY_PROBE.json','SETTLED_SHORT_BACKING_PROBE.json']:assert J(n)['result']=='PASS'
assert J('FINDINGS.json')['G2']=='PASS — RESTRICTED ENGINEERING SCOPE'
for n in ['EXTENDED_REPAIR_CHECKS.json','PRODUCTION_PROBES.json','INDEPENDENT_BACKING_CONTROLS.json','PUBLIC_BACKING_FAULT_CONTROLS.json']:assert J(n)['MISMATCH']==0
assert subprocess.check_output(['git','-C',str(C),'status','--porcelain'])==b''
env=json.loads((SDK/'environment.json').read_bytes());assert env['complete'] and env['code_commit']==FIX
selection=json.loads((SDK/'upload-selection.json').read_bytes());assert len(selection['files'])==8008
sdkzip=O/'independent-sdk-artifacts.zip';assert not sdkzip.exists()
with zipfile.ZipFile(sdkzip,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for e in selection['files']:
  p=SDK/e['path'];assert H(p.read_bytes())==e['sha256'];z.write(p,e['path'])
 z.write(SDK/'upload-selection.json','upload-selection.json')
with zipfile.ZipFile(sdkzip) as z:
 assert z.testzip() is None and set(z.namelist())=={e['path'] for e in selection['files']}|{'upload-selection.json'}
 for e in selection['files']:assert H(z.read(e['path']))==e['sha256']
subdirs=['probes','cancellation-boundary','extended-repair','short-bucket-reconciliation','settled-short-backing-probe','backing-controls','public-backing-controls'];entries=[];prodzip=O/'reviewer-production-artifacts.zip';assert not prodzip.exists()
with zipfile.ZipFile(prodzip,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for name in subdirs:
  root=A/name;assert root.is_dir()
  for p in sorted(root.rglob('*')):
   if p.is_file():
    raw=p.read_bytes();rel=p.relative_to(A).as_posix();entries.append(dict(path=rel,bytes=len(raw),sha256=H(raw)));z.writestr(rel,raw)
 z.writestr('PROBE_ARTIFACT_MANIFEST.json',json.dumps(dict(executor='GPT Work supplemental reviewer',fixed_sha=FIX,files=entries),ensure_ascii=False,indent=2).encode())
with zipfile.ZipFile(prodzip) as z:
 assert z.testzip() is None and len(z.namelist())==len(entries)+1
 for e in entries:
  raw=z.read(e['path']);assert len(raw)==e['bytes'] and H(raw)==e['sha256']
received=O/'developer-received';received.mkdir()
for name in ['Evidence.zip','EVIDENCE_MANIFEST.json','RECEIPT.json','GPT-Work-G2-Recheck-Instructions.txt','FAILURE_AND_OMISSION_INDEX.json','POST_SEAL_PUBLISH_HELPER_ERRATA.json','publish_final.actual.py']:
 shutil.copyfile(D/name,received/name)
copied=[];source=O/'reviewed-source'
for name in ['AGENTS.md','src/aqrp/backtest/ledger.py','src/aqrp/backtest/transactions.py','src/aqrp/services/backtest.py','src/aqrp/performance/metrics.py','tests/backtest/test_g2_bucket_reconciliation.py','tests/backtest/test_g2_execution_backing.py','docs/BACKTEST_CONTRACT.md','docs/audits/phase-5/CASH_BUCKETS_AND_PROJECTION.md','docs/audits/phase-5/FIFO_ATTRIBUTION.md','docs/audits/phase-5/IMPLEMENTATION_TRACEABILITY.md','docs/audits/phase-5/g2-bf5e5a8/DEVELOPER_RESPONSE.md','docs/audits/phase-5/g2-bf5e5a8/OUTPUT_CONTRACT_ERRATA.md','docs/audits/phase-5/g2-bf5e5a8/REPAIR_IDENTITY.json','docs/audits/phase-5/IMPLEMENTATION_AUTHORIZATION.json']:
 p=source/name;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(C/name,p);copied.append(dict(path=name,sha256=H(p.read_bytes())))
(O/'REVIEWED_SOURCE_BINDINGS.json').write_text(json.dumps(copied,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def fh(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
bindings=[dict(path=p.relative_to(O).as_posix(),bytes=p.stat().st_size,sha256=fh(p)) for p in [sdkzip,prodzip,received/'Evidence.zip']]
(O/'NESTED_ARCHIVE_BINDINGS.json').write_text(json.dumps(dict(fixed_sha=FIX,archives=bindings,SDK_selected_files=8008,probe_files=len(entries),SDK_omissions='Venv/cache/bootstrap/gitleaks not selected uploaded evidence; exact pins/install logs/wheel and fixed Git source retained',developer_original_contains='Original dual-OS ZIPs, fixed source, developer SDK, prior audit and retained failures; separately hash/CRC verified; not reviewer execution'),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(SDK_files=8008,probe_files=len(entries),nested=bindings),ensure_ascii=False))
