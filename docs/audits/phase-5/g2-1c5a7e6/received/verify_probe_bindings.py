from pathlib import Path
import json,hashlib
O=Path(__file__).parent;R=Path('E:/WORK/AQRP-audits/p5-1c5a7e6/extended-repair')
H=lambda b:hashlib.sha256(b).hexdigest()
C=lambda v:json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()
rows=[]
for stage in ['BEFORE_COMMIT','AFTER_COMMIT']:
 for typ in ['KeyboardInterrupt','ContractError','RuntimeError']:
  label=stage+'-'+typ;root=next(p for p in (R/label).iterdir() if p.is_dir());tx=json.loads((root/'transactions.json').read_bytes());trace=json.loads((root/'committed-trace.json').read_bytes());state=json.loads((root/'failed-state.json').read_bytes());result=json.loads((root/'result.json').read_bytes());v=result['committed_state_verification'];raws=sorted((root/'transactions').glob('commit-*.json'))
  assert [json.loads(p.read_bytes()) for p in raws]==tx
  assert trace==[{'commit_seq':t['commit_seq'],'sha256':t['sha256'],'dispatch_key':t['dispatch_key'],'children':t['children']} for t in tx]
  assert state==tx[-1]['post_state'] and H(C(state))==v['state_sha256'] and tx[-1]['sha256']==v['prefix_sha256'] and v['commit_count']==len(tx)
  for e in json.loads((root/'transaction-files.json').read_bytes()):assert H((root/e['path']).read_bytes())==e['sha256']
  m=json.loads((root/'manifest.json').read_bytes())
  for e in m['files']:assert H((root/e['path']).read_bytes())==e['sha256']
  rows.append({'case':label,'transactions':len(tx),'full_committed_trace_equals_raw_records':True,'failed_state_equals_durable_post_state':True,'metadata_state_prefix_hashes_exact':True,'manifest_all_actual_bytes_verified':True})
(O/'REPAIR_PROBE_BINDINGS.json').write_text(json.dumps({'fixed_sha':'1c5a7e62cace7c3e66b7cc7f12fd564cb0013654','executor':'GPT Work supplemental reviewer','cases':rows,'result':'PASS'},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'cases':6,'raw_commits_trace_state_return_hash_bindings':'PASS'}))
