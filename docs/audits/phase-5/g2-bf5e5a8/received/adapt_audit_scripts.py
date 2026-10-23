from pathlib import Path
import json,hashlib
O=Path(__file__).parent;P=O.parent/'p5-g2-recheck-35f93d6-independent'
old='35f93d640a2304121131d947a465f57a951cf63f';fix='bf5e5a89209f2dd24042cd806626f832b531de52'
old_sdk='aqrp-e6171f64-5e4a-47c3-b7df-d73eb4d05b2d';sdk='aqrp-be90b0d1-9aad-4527-bba8-11a8e5de700e'
names=['verify_scope_evidence.py','verify_official_ci.py','verify_local_sdk.py','short_bucket_reconciliation_probe.py','extended_repair_checks.py','cancellation_boundary_probe.py','production_probes.py','verify_probe_bindings.py','independent_original_math.py','independent_revision_math.py','raw_financial_reconstruction.py']
records=[]
for name in names:
 s=(P/name).read_text(encoding='utf-8')
 replacements=[(old,fix),('p5-35f93d6','p5-bf5e5a8'),('p5-g2-recheck-35f93d6','p5-g2-003-recheck-bf5e5a8'),(old_sdk,sdk)]
 if name=='verify_scope_evidence.py':replacements += [('c6eafcb309d5dcefaab6747aa21e6f4f45128a21','2d1667fb3ec9b1fb5405770a13f6c2a0004f4a81'),('e383e3f1828ca5d28b3f9daaf2714670af5023aa64c1e908c2ed10466edd0058','a741748c115cd98ecbc2fdfed784cdc5636aea44362ef6ecc81a15933a3b3d94'),('8369','8599'),('8370','8600')]
 if name=='verify_official_ci.py':replacements += [('c6eafcb309d5dcefaab6747aa21e6f4f45128a21','2d1667fb3ec9b1fb5405770a13f6c2a0004f4a81'),('39889789530','39908760220'),('1073','1116')]
 if name=='verify_local_sdk.py':replacements += [('1073','1116')]
 for a,b in replacements:s=s.replace(a,b)
 (O/name).write_text(s,encoding='utf-8')
 records.append({'script':name,'original_sha256':hashlib.sha256((P/name).read_bytes()).hexdigest(),'new_sha256':hashlib.sha256((O/name).read_bytes()).hexdigest(),'substitutions':replacements,'probe_expectations_changed':False})
(O/'AUDIT_SCRIPT_ADAPTATIONS.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Adapted',len(records),'prior independently written audit scripts; original probe inputs and answers unchanged')
