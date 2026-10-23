from pathlib import Path
import json,hashlib
O=Path(__file__).parent;P=O.parent/'p5-g2-003-recheck-bf5e5a8-independent'
old='bf5e5a89209f2dd24042cd806626f832b531de52';new='1c5a7e62cace7c3e66b7cc7f12fd564cb0013654'
old_sdk='aqrp-be90b0d1-9aad-4527-bba8-11a8e5de700e';sdk='aqrp-87d64547-3922-4678-b3a4-a5cf51d4da00'
names=['verify_scope_evidence.py','verify_official_ci.py','verify_local_sdk.py','short_bucket_reconciliation_probe.py','extended_repair_checks.py','cancellation_boundary_probe.py','production_probes.py','verify_probe_bindings.py','independent_original_math.py','independent_revision_math.py','raw_financial_reconstruction.py','settled_short_backing_probe.py']
records=[]
for name in names:
 s=(P/name).read_text(encoding='utf-8')
 reps=[(old,new),('p5-bf5e5a8','p5-1c5a7e6'),('p5-g2-003-recheck-bf5e5a8','p5-g2-backing-recheck-1c5a7e6'),(old_sdk,sdk)]
 if name=='verify_scope_evidence.py':reps += [('2d1667fb3ec9b1fb5405770a13f6c2a0004f4a81','db8c9776007dc2e13a0ebd0aa2e6d7045d7a301f'),('a741748c115cd98ecbc2fdfed784cdc5636aea44362ef6ecc81a15933a3b3d94','68d723fd865a59ad843d0be096e841d1e56005907bb8783037a784c8159eda3e'),('8599','10048'),('8600','10049')]
 if name=='verify_official_ci.py':reps += [('2d1667fb3ec9b1fb5405770a13f6c2a0004f4a81','db8c9776007dc2e13a0ebd0aa2e6d7045d7a301f'),('39908760220','39920156761'),('1116','1158'),('3757','3795'),('196','198')]
 if name=='verify_local_sdk.py':reps += [('1116','1158')]
 for a,b in reps:s=s.replace(a,b)
 if name=='settled_short_backing_probe.py':
  s=s.replace('from aqrp.backtest.engine import Simulator','from aqrp.backtest.engine import Simulator\nfrom aqrp.backtest.transactions import TransactionStore')
  s=s.replace("recon,_=service._reconciled_account(after)\n try:service.projection(after);normal='ACCEPTED'", "durable,source_records,_=TransactionStore(root/'transactions').verified_snapshot()\n assert durable==after\n try:service._reconciled_account(after,source_records);core='ACCEPTED'\n except ContractError as exc:core=exc.code\n try:service.projection(after,source_records);normal='ACCEPTED'")
  s=s.replace('core_gate_accepted=True','core_gate_accepted=core==\'ACCEPTED\',core_gate_result=core')
 (O/name).write_text(s,encoding='utf-8')
 records.append(dict(script=name,old_sha256=hashlib.sha256((P/name).read_bytes()).hexdigest(),new_sha256=hashlib.sha256((O/name).read_bytes()).hexdigest(),substitutions=reps,private_context_change='settled probe private gate now receives independently reread verified durable records and captures rejection; financial input/expected known/amount unchanged' if name=='settled_short_backing_probe.py' else None))
(O/'AUDIT_SCRIPT_ADAPTATIONS.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print('Adapted',len(records),'independent scripts; original public probes financial expectations retained')
