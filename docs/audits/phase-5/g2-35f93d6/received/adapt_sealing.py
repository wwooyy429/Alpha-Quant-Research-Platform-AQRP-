from pathlib import Path
O=Path(__file__).parent;OLD=O.parent/'p5-g2-bfdcf30-independent'
mapping={
 'bfdcf30e525ff802ea483974f58163eedc029ce8':'35f93d640a2304121131d947a465f57a951cf63f',
 'E:/WORK/AQRP-audits/p5-bfdcf30':'E:/WORK/AQRP-audits/p5-35f93d6',
 "O.parent/'p5-g2-bfdcf30'":"O.parent/'p5-g2-recheck-35f93d6'",
 'E:/WORK/AQRP-runs/gpt-p5-bfdcf30-20261023/aqrp-deda3946-8ba6-4c75-b20b-99e628268e2b':'E:/WORK/AQRP-runs/gpt-p5-35f93d6-20261023/aqrp-e6171f64-5e4a-47c3-b7df-d73eb4d05b2d',
 'b6daf213c8182790ae5a8675efa131727f5a6689520b65f096efe87124b9c594':'773ab0d9e7485aebd107fbd3f092cdd1a0381fbfb412ba4a1a8b2f0b08bd7134',
 'selected6616':'selected7229'
}
for name in ['prepare_seal.py','seal_evidence.py']:
 s=(OLD/name).read_text(encoding='utf-8')
 for a,b in mapping.items():s=s.replace(a,b)
 if name=='prepare_seal.py':
  s=s.replace("assert json.loads((O/'CANCELLATION_BOUNDARY_PROBE.json').read_bytes())['result']=='REPRODUCED_MISMATCH'","assert json.loads((O/'CANCELLATION_BOUNDARY_PROBE.json').read_bytes())['result']=='PASS'\nassert json.loads((O/'SHORT_BUCKET_RECONCILIATION_PROBE.json').read_bytes())['result']=='REPRODUCED_MISMATCH'\nassert json.loads((O/'REPAIR_PROBE_BINDINGS.json').read_bytes())['result']=='PASS'")
  s=s.replace("for name in ['probes','cancellation-boundary']:","for name in ['probes','cancellation-boundary','extended-repair','short-bucket-reconciliation']:")
  s=s.replace("'AGENTS.md']:","'AGENTS.md','docs/audits/phase-5/g2-bfdcf30/OUTPUT_CONTRACT_ERRATA.md','docs/audits/phase-5/g2-bfdcf30/REPAIR_IDENTITY.json','docs/audits/phase-5/g2-bfdcf30/DEVELOPER_RESPONSE.md']:")
 if name=='seal_evidence.py':s=s.replace("'findings':{'High':1,'Medium':1,'status':'OPEN'}","'findings':{'original001':'CLOSED','original002':'CLOSED','new003':'High OPEN'}")
 (O/name).write_text(s,encoding='utf-8')
print('Sealing helper bound to this actual SDK and raw probe roots')
