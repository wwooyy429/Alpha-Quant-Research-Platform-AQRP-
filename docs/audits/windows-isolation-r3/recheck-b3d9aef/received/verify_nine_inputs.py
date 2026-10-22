import pathlib,json,zipfile,hashlib,io
from fractions import Fraction as Q
import pyarrow.parquet as pq
from aqrp.core.contracts import SnapshotRef,QuerySpec
from aqrp.factors import FactorEngine,FactorRegistry,builtin_spec,write_run
from datetime import date
O=pathlib.Path(__file__).parent;D=O.parent/'windows-isolation-r3-b3d9aef';manifest=json.loads((D/'Engineering-inputs-manifest.json').read_bytes());archive=D/'Nine-engineering-inputs-original.zip';expected_names={'manifest.json','adjustment_factors.parquet','bars_daily.parquet','calendar.parquet','corporate_actions.parquet','security_master.parquet','security_status.parquet','symbol_alias.parquet','universe_membership.parquet'};R=O/'new-nine-inputs';target=R/manifest['snapshot_id'];target.mkdir(parents=True,exist_ok=True)
H=lambda b:hashlib.sha256(b).hexdigest()
def canon(x):return json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()
with zipfile.ZipFile(archive) as z:
 assert z.testzip() is None and len(z.namelist())==9 and set(z.namelist())==expected_names
 for e in manifest['files']:
  b=z.read(e['path']);assert len(b)==e['bytes'] and H(b)==e['sha256'];(target/e['path']).write_bytes(b)
m=json.loads((target/'manifest.json').read_bytes());assert m['snapshot_id']==manifest['snapshot_id'] and H(canon({k:v for k,v in m.items() if k not in ['snapshot_id','manifest_hash']}))==m['manifest_hash']==manifest['snapshot_manifest_hash'];tables={};summaries=[]
for name,e in m['tables'].items():
 b=(target/e['path']).read_bytes();assert H(b)==e['sha256'];t=pq.read_table(io.BytesIO(b));rows=t.to_pylist();assert len(rows)==e['rows'];assert all(r['snapshot_id']==manifest['snapshot_id'] for r in rows)
 if rows:
  lo=min(r['event_time'] for r in rows).isoformat(timespec='microseconds');hi=max(r['event_time'] for r in rows).isoformat(timespec='microseconds');assert (lo,hi)==(e['event_min'],e['event_max'])
 if rows and 'security_id'in rows[0]:assert sorted({r['security_id'] for r in rows})==e['security_ids']
 q=e['quality'];assert q['input']==q['valid']+q['duplicate']+q['missing']+q['rejected'] and q['valid']+q['missing']==len(rows) and q['rejected']==0
 tables[name]=rows;summaries.append({'table':name,'rows':len(rows),'sha256':H(b),'schema':str(t.schema)})
prices={2:100,3:110,4:121};volumes={2:100,3:150,4:200}
for r in tables['bars_daily']:
 day=r['session_date'].day;assert all(Q(r[k])==prices[day] for k in ['open','high','low','close']);assert Q(r['volume'])==volumes[day] and Q(r['amount'])==prices[day]*volumes[day]
expect={'momentum':Q(121,100)-1,'reversal':1-Q(121,100),'volume':Q(200)/((Q(100)+150)/2)-1};expect['price_volume']=(Q(121,110)-1)*expect['volume'];snapshot=SnapshotRef(R,manifest['snapshot_id'],m['manifest_hash']);query=QuerySpec(('SYN_A:001',),'SYN_A','SYN_A_CAL',(date(2024,1,2),date(2024,1,4)),('close','volume'),'split_adjusted');registry=FactorRegistry();results=[]
for name,answer in expect.items():
 spec=builtin_spec(name);registry.register(spec.implementation_version,spec,actor='GPT Work',reason='New public engineering export math only',evidence=spec.review_ref);batch=FactorEngine(registry).run(spec.ref,query,'2024-01-04T12:05:00Z',snapshot,parameters={'lookback':2});value=batch.rows[0].factor_value;assert abs(Q(str(value))-answer)<=Q(1,10**12);run=write_run(batch,O/'independent-factor-runs',registry);results.append({'factor':name,'expected_exact':str(answer),'actual':value,'tolerance':'1e-12','run':str(run)})
result={'actual_executor':'GPT Work independent bytes, Parquet and exact-rational verification','snapshot_id':m['snapshot_id'],'snapshot_manifest_hash':m['manifest_hash'],'source_archive_bytes':archive.stat().st_size,'source_archive_sha256':H(archive.read_bytes()),'members':9,'tables':summaries,'factor_executions':results,'deployment':'NOT_DEPLOYED','actual_auditor_token_access':'NOT_EXECUTED','old_nine_input_recovery':'NOT_ATTEMPTED_NOT_VERIFIED','scope':'Readable new public export, not a substitute for old inaccessible files or OS isolation proof','result':'PASS'};(O/'NINE_INPUTS_VERIFICATION.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');(O/'Engineering-inputs-manifest-received.json').write_bytes((D/'Engineering-inputs-manifest.json').read_bytes());(O/'Nine-engineering-inputs-original.zip').write_bytes(archive.read_bytes());print(json.dumps({k:v for k,v in result.items() if k!='tables'}))
