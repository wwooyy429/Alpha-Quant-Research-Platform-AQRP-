"""Independent actual browser tasks, immutable requests, P1 membership, P3 rows, P5 sidecar."""
from pathlib import Path
import sys,json,hashlib,subprocess,time
from aqrp.services.tasks import TaskService
from aqrp.services.task_requests import catalogue,references
from aqrp.data.query import universe_at
O=Path(__file__).parent;root=Path('E:/WORK/AQRP-runs/gpt-p6-browser-3017a09-independent-20261024/workspace')
s=TaskService(root);cat=catalogue(root);ref,_,_=references(root,cat)
assert cat['code_commit']=='3017a097b49ecdae68228ca9a417fcd03c313200'
base={'kind':'research','start':'2024-01-06','end':'2024-01-06','horizons':[1]}
rows=s.list();assert len(rows)==2
deadline=time.monotonic()+180
while any(s.state.get(r['task_id'])['status'] in ('QUEUED','RUNNING') for r in rows):
 assert time.monotonic()<deadline;time.sleep(.5)
record=[]
for r in s.list():
 task=r['task_id'];assert r['status']=='SUCCEEDED',r;x=s.request(task);pool=x['payload']['research']['universe_id']
 expected={f'SYN_A:{i:03d}' for i in (range(3,7) if pool=='SYN_TAIL4' else range(1,5))}
 raw=s.artifact(task,'R','raw.json');actual=json.loads(raw)['rows'];assert {q['security_id'] for q in actual}==expected
 out=dict(task=task,status=r['status'],kind=x['kind'],universe=pool,literal_members=sorted(expected),actual_P3_members=sorted({q['security_id'] for q in actual}),frozen_request=x,raw_sha256=hashlib.sha256(raw).hexdigest())
 if x['kind']=='engineering_pipeline':
  config=json.loads(s.artifact(task,'B','config.json'));request=json.loads(bytes.fromhex(config['raw_request_hex']))
  times=sorted({q['event_time'] for q in request['sidecar']['rows']})
  for t in times:
   allowed={q['security_id'] for q in universe_at(pool,t,ref)}
   assert all(q['in_universe']==(q['security_id'] in allowed) for q in request['sidecar']['rows'] if q['event_time']==t)
  finance=s.financial_result(task);assert finance['account']['cash_total']=='98.1' and finance['account']['equity']=='998.1'
  assert {q['security_id'] for q in finance['fills']}<=expected
  out.update(finance=finance,sidecar=request['sidecar'],membership_times=times)
 record.append(out)
assert {x['universe'] for x in record}=={'SYN_CORE4','SYN_TAIL4'}
canonical=[]
for pool in ['SYN_U','SYN_CORE4','SYN_TAIL4']:
 d={**base,'universe_id':pool};f=s.freeze(d);p=O/('cli-'+pool+'.json');p.write_text(json.dumps(d),encoding='utf-8')
 proc=subprocess.run([sys.executable,'-I','-m','aqrp.services.task_cli','freeze','--workspace',str(root),'--request',str(p)],capture_output=True)
 (O/('cli-'+pool+'.stdout.log')).write_bytes(proc.stdout);(O/('cli-'+pool+'.stderr.log')).write_bytes(proc.stderr)
 assert proc.returncode==0 and json.loads(proc.stdout)==json.loads(f.raw)
 canonical.append(dict(pool=pool,config_hash=f.config_hash,request=json.loads(f.raw)))
assert len({x['config_hash'] for x in canonical})==3
before=s.list()
for pool in [None,'SYN_B','../SYN_U']:
 try:s.freeze({**base,'universe_id':pool});raise AssertionError('Unknown pool admitted')
 except Exception as e:assert getattr(e,'code',None)=='UNKNOWN_ENGINEERING_UNIVERSE'
assert s.list()==before
(O/'INDEPENDENT_UNIVERSE_RECHECK.json').write_text(json.dumps(dict(fixed_sha=cat['code_commit'],executor='GPT Work',scope='Actual reviewer CUA browser submissions; readback via installed SDK/SQLite plus literal expectations; synthetic only',browser_tasks=record,CLI_SDK_canonical_parity=canonical,unknown_universes_refused_without_tasks=True,result='PASS'),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Actual browser TAIL4 research + CORE4 pipeline, raw membership, P5 sidecar and exact finance, three-pool CLI/SDK identity PASS')
