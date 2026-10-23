"""Only bind prior reviewer-owned checks to new fixed source/outputs and counts."""
from pathlib import Path
O=Path(__file__).parent;OLD=O.parent/'p5-g2-bfdcf30-independent'
mapping={
 'bfdcf30e525ff802ea483974f58163eedc029ce8':'35f93d640a2304121131d947a465f57a951cf63f',
 'b379a8f34b9d43859daaf4dd98cc46021304e7c0':'c6eafcb309d5dcefaab6747aa21e6f4f45128a21',
 'E:/WORK/AQRP-audits/p5-bfdcf30':'E:/WORK/AQRP-audits/p5-35f93d6',
 "O.parent/'p5-g2-bfdcf30'":"O.parent/'p5-g2-recheck-35f93d6'",
 'ba6b33df82b5142958a2cb6f7aa5a92109241e0f533dd56d436f32fe83358f07':'e383e3f1828ca5d28b3f9daaf2714670af5023aa64c1e908c2ed10466edd0058',
 'E:/WORK/AQRP-runs/gpt-p5-bfdcf30-20261023/aqrp-deda3946-8ba6-4c75-b20b-99e628268e2b':'E:/WORK/AQRP-runs/gpt-p5-35f93d6-20261023/aqrp-e6171f64-5e4a-47c3-b7df-d73eb4d05b2d',
 '39839529359':'39889789530'
}
names=['verify_scope_evidence.py','verify_official_ci.py','verify_local_sdk.py','independent_original_math.py','independent_revision_math.py','raw_financial_reconstruction.py','production_probes.py','cancellation_boundary_probe.py']
for name in names:
 s=(OLD/name).read_text(encoding='utf-8')
 for a,b in mapping.items():s=s.replace(a,b)
 if name=='verify_scope_evidence.py':s=s.replace('10920','8369').replace('10921','8370')
 if name in ['verify_official_ci.py','verify_local_sdk.py']:s=s.replace('1049','1073').replace('3429','3726').replace('189','195')
 if name=='verify_scope_evidence.py':s=s.replace("'union':3444","'union_paths':3451,'protected_unchanged_paths':3444")
 # Preserve reviewer literal expected amounts and fault logic; direction expected LONG unchanged.
 (O/name).write_text(s,encoding='utf-8')
print('Reviewer checks rebound to new fixed SHA; literal financial answers unchanged')
