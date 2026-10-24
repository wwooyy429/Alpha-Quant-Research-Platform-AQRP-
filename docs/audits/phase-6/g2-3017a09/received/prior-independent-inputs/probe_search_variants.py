"""Independent installed-wheel counterexample: search variants must not reset one workspace's experiment controls."""
from pathlib import Path
import json,hashlib,sys,datetime
from aqrp.services.task_requests import initialize
from aqrp.services.tasks import TaskService
from aqrp.experiments.ledger import read_chain
O=Path(__file__).parent;ROOT=Path('E:/WORK/AQRP-runs/gpt-p6-independent-probes-20261024')
ROOT.mkdir(exist_ok=True)
root=ROOT/'search-family-variants';assert not root.exists()
initialize(root,'eae807f957f178d19bc55dcfbd668caff5470c6e');s=TaskService(root)
base={'kind':'research','start':'2024-01-06','end':'2024-01-06','horizons':[1]}
results=[]
for i in range(1,15):
 draft={**base,'lookback':i}
 frozen=s.freeze(draft);payload=json.loads(frozen.raw)['payload']['research']
 t=s.submit(frozen,'variant-'+str(i))['task_id'];r=s.work(t)
 files={}
 for name in ['multiplicity.json','approvals.json']:
  try:files[name]=json.loads(s.artifact(t,'R',name))
  except Exception as e:files[name]={'unavailable':getattr(e,'code',type(e).__name__)}
 results.append(dict(task=t,lookback=i,status=r['status'],error=r.get('error'),family=payload['family'],files=files))
trials=read_chain(root/'research-runs/trials.jsonl')
observed=[r['payload'] for r in trials]
report=dict(scope='Installed exact-SHA application; synthetic engineering data only. No real formal Test or financial approval.',executor='GPT Work supplemental reviewer',python=sys.executable,root=str(root),configurations=results,trials=observed,distinct_families=len({r['family'] for r in observed}),total_trials=len(trials),any_over_budget=any(t['over_budget'] for t in observed),contamination_flags=[r['files']['multiplicity.json'].get('contaminated') for r in results])
(O/'SEARCH_VARIANT_PROBE.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:report[k] for k in ['root','total_trials','distinct_families','any_over_budget','contamination_flags']}))

