"""Independent G2 repair controls. Expected arithmetic uses fractions only, not AQRP math."""
import pathlib,json,hashlib,copy,shutil,random
from fractions import Fraction as Q
from decimal import localcontext,Decimal,Context,ROUND_HALF_EVEN
from unittest.mock import patch
import pyarrow as pa
import pyarrow.parquet as pq
from independent_reference import reference
from aqrp.portfolio.contracts import PortfolioRequest
from aqrp.portfolio.service import construct_engineering,replay_engineering
from aqrp.portfolio.research_input import bind_research
from aqrp.core.contracts import SnapshotRef
from aqrp.core.errors import ContractError
from aqrp.experiments.ledger import ExperimentLedger
O=pathlib.Path(__file__).parent;C=O.parent/'p4-g2-recheck-3c87579';OLD=O.parent/'work-p4-g2-18439f3-independent';FIX='3c8757949b0fd5c97953b06a74ebc2d0e56676e4';RUN=O/'repair-runs';RUN.mkdir(exist_ok=True)
def canon(x):return json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()
H=lambda b:hashlib.sha256(b).hexdigest()
def save(p,x):p.write_bytes(canon(x))
def load(p):return json.loads(p.read_bytes())
def base():return load(C/'tests/portfolio/fixtures/base.json')
def seal(x):
 es=[e for k,e in x['inputs'].items() if k!='scores']+x['inputs']['scores']
 for e in es:e['content_sha256']=H(canon({k:v for k,v in e.items() if k!='content_sha256'}))
 x['source']['fixture_manifest']={e['ref']:e['content_sha256'] for e in es};return PortfolioRequest(canon(x))
def exact_decimal(q):
 # Decimal exponent chosen from denominator size; expected values retain the exact rational too.
 d=q.denominator
 for p in (2,5):
  while d%p==0:d//=p
 if d!=1:
  with localcontext(Context(prec=34,rounding=ROUND_HALF_EVEN)):return Q(Decimal(q.numerator)/Decimal(q.denominator))
 return q
def compare(a,e,path=''):
 if isinstance(e,dict):
  for k,v in e.items():compare(a[k],v,path+'.'+k)
 else:assert Q(a)==exact_decimal(e),(path,a,str(e))
records=[]
def trial(name,x,precision=None):
 expect=reference(x);request=seal(x)
 with localcontext() as ctx:
  if precision:ctx.prec=precision
  result=construct_engineering(request,RUN,FIX).read()
 assert result['status']==expect['status'],(name,result.get('reasons'),expect['status'])
 directory=RUN/result['run_id'];raw=(directory/'result.json').read_bytes();stored=load(directory/'result.json');returned=copy.deepcopy(result);returned.pop('manifest');assert canon(returned)==raw
 for phase in ('pre','post'):
  compare(result['risk'][phase]['metrics'],expect[phase]['metrics'],phase)
  assert sorted({r['code'] for r in result['risk'][phase]['checks'] if not r['passed']})==expect[phase]['failures']
 assert load(directory/'risk.json')==result['risk']
 candidate=load(directory/'candidate.json');compare(candidate['rounded'],expect['rounded'],'candidate.rounded');compare(candidate['ideal'],expect['ideal'],'candidate.ideal')
 if result['status']=='SUCCEEDED':
  compare(result['target'],expect['post']['metrics'],'target');audit=load(directory/'published-byte-audit.json');assert audit['result_sha256']==H(raw)
  assert H(canon({k:v for k,v in result['target'].items() if k!='content_sha256'}))==result['target']['content_sha256']
  assert result['target']['risk_hash']==result['risk']['content_sha256']
  q={s:Q(v) for s,v in result['target']['quantities'].items()};d={s:Q(v) for s,v in result['target']['deltas'].items()};prices={r['security_id']:Q(r['price']) for r in x['inputs']['prices']['data']}
  assert Q(result['target']['cash'])+sum(q[s]*prices[s] for s in q)==Q(x['inputs']['account']['data']['equity'])
  assert {r['security_id']:Q(r['delta_qty']) for r in result['rebalance_proposals']}=={s:v for s,v in d.items() if v}
 assert replay_engineering(RUN,result['run_id'])['result']==stored
 record={'case':name,'run_id':result['run_id'],'status':result['status'],'request_sha256':request.content_hash,'actual_result_sha256':H(raw),'expected':json.loads(json.dumps(expect,default=str)),'all_persisted_and_returned_values_match':True};records.append(record)
for n in (0,3,33,34,35,40,67,99,100):
 x=base();x['inputs']['account']['data'].update(equity='1e'+str(n),total_cash='1e'+str(n));x['policy']['top_k']=1
 for row in x['inputs']['prices']['data']:row.update(price='1',lot='3')
 trial('integer-E1e'+str(n),x,2)
for n,p,l in [(35,'0.01','0.03'),(100,'1e-100','7'),(-100,'1e100','1e-100'),(34,'0.125','0.375'),(40,'3','7'),(35,'7','3')]:
 x=base();x['inputs']['account']['data'].update(equity='1e'+str(n),total_cash='1e'+str(n));x['policy']['top_k']=1
 for row in x['inputs']['prices']['data']:row.update(price=p,lot=l)
 trial('price-lot-'+str(n)+'-'+p,x,3)
for n in (34,35,40,100):
 for weighting in ('equal','score'):
  x=base();x['inputs']['account']['data'].update(equity='1e'+str(n),total_cash='1e'+str(n));x['policy'].update(mode='LONG_SHORT',weighting=weighting,gross='1',net='0')
  for row in x['inputs']['prices']['data']:row.update(price='1',lot='3')
  for row in x['inputs']['permissions']['data']:row.update(short_permission=True,borrow_limit_total='1e'+str(n))
  trial('short-'+str(n)+'-'+weighting,x,2)
# Nonzero positions and a changed target exercise exact deltas at both positive/negative scales.
for oldq in ('3','-3','0.03'):
 x=base();E=10**35;x['inputs']['account']['data'].update(equity='1e35',total_cash=str(E-int(Q(oldq))) if Q(oldq).denominator==1 else str(E)+'.00');x['policy']['top_k']=1
 # Smaller old values need an exact decimal total_cash not a context-rounded subtraction.
 with localcontext(Context(prec=100)):x['inputs']['account']['data']['total_cash']=format(Decimal(E)-Decimal(oldq),'f')
 # 35-digit cash is outside input domain: use 1e34, maintaining <=34 significant digits.
 E=10**33;x['inputs']['account']['data']['equity']=str(E)
 with localcontext(Context(prec=100)):x['inputs']['account']['data']['total_cash']=format(Decimal(E)-Decimal(oldq),'f')
 if len(Decimal(x['inputs']['account']['data']['total_cash']).as_tuple().digits)>34:continue
 x['inputs']['account']['data']['positions'][0]['quantity']=oldq
 short=max(-Q(oldq),Q(0));x['inputs']['account']['data'].update(restricted_cash=str(short),short_restriction=str(short))
 for row in x['inputs']['prices']['data']:row.update(price='1',lot='3')
 trial('existing-'+oldq,x,2)
# Reuse the original positive-control request bytes to reconstruct source projection, not test helpers.
positive=next(r for r in load(OLD/'ADVERSARIAL_RESULTS.json')['records'] if r['case']=='original-snapshot-id')
oldcfg=load(OLD/'adversarial-runs'/positive['run_id']/'config.json');payload=json.loads(bytes.fromhex(oldcfg['raw_request_hex']))
P=C/'docs/audits/phase-3/publication/sdk/research';RID='0c902a7a-6e21-4003-9e18-365bf8bc3b68';SID='9e3a5971-d66e-4aee-bdb4-1082c6907e02'
m=load(P/'inputs/dataset'/SID/'manifest.json');manifest_raw=(P/'inputs/dataset'/SID/'manifest.json').read_bytes();assert H(canon({k:v for k,v in m.items() if k not in ('snapshot_id','manifest_hash')}))==m['manifest_hash']
assert len(list((P/'inputs/dataset'/SID).iterdir()))==9
source_hashes={p.name:H(p.read_bytes()) for p in (P/'inputs/dataset'/SID).iterdir()}
for e in m['tables'].values():assert source_hashes[e['path']]==e['sha256'];assert all(r['snapshot_id']==SID for r in pq.read_table(pa.BufferReader((P/'inputs/dataset'/SID/e['path']).read_bytes())).to_pylist())
engine=load(P/'runs'/RID/'engine.json');terminal=load(P/'runs'/RID/'manifest.json');assert terminal['status']=='SUCCEEDED'
assert H((P/'runs'/RID/'engine.json').read_bytes())==next(e['sha256'] for e in terminal['files'] if e['path']=='engine.json')
for row in engine:
 raw=row['config_snapshot_utf8'].encode();cfg=json.loads(raw);assert H(raw)==row['config_snapshot_sha256'];assert cfg==row['config'];assert cfg['snapshot_id']==SID and cfg['manifest_hash']==m['manifest_hash'];assert H(canon({'rows':row['signals'],'config':raw.decode()}))==row['content_hash'];assert all(r['snapshot_id']==SID for r in row['signals'])
bound=json.loads(bind_research(payload,P/'runs',RID).raw);bound=json.loads(seal(bound).raw)
parents=[]
def parent_trial(name,x,success=False):
 result=construct_engineering(seal(x),RUN,FIX).read();assert (result['status']=='SUCCEEDED')==success,(name,result.get('reasons'));assert ('target' in result)==success
 if success:assert result['target']['context']['snapshot_id']==SID
 parents.append({'case':name,'run_id':result['run_id'],'status':result['status'],'reasons':result.get('reasons',[])})
parent_trial('default-original-nine',copy.deepcopy(bound),True)
newid='00000000-0000-4000-8000-000000000001'
for kind in ('contexts_only','all_claimed_ids','cross_data_hash','raw_manifest_hash','missing_snapshot','missing_raw_hash','absent_root'):
 x=copy.deepcopy(bound);b=x['source']['research_bindings'][0]
 if kind in ('contexts_only','all_claimed_ids'):
  x['context']['snapshot_id']=newid
  for key,e in x['inputs'].items():
   for item in e if key=='scores' else [e]:item['context']['snapshot_id']=newid
  if kind=='all_claimed_ids':b['snapshot']['snapshot_id']=newid
 if kind=='cross_data_hash':b['snapshot']['manifest_hash']='0'*64
 if kind=='raw_manifest_hash':b['snapshot_manifest_sha256']='0'*64
 if kind=='missing_snapshot':del b['snapshot']
 if kind=='missing_raw_hash':del b['snapshot_manifest_sha256']
 if kind=='absent_root':b['snapshot']['root']=str(O/'absent-parent')
 parent_trial(kind,x)
for mutation in ('none','manifest_id','table_bytes','table_inner_id','missing_table'):
 dataset=O/'parent-copies'/mutation;shutil.copytree(P/'inputs/dataset'/SID,dataset/SID);folder=dataset/SID
 if mutation=='manifest_id':md=load(folder/'manifest.json');md['snapshot_id']=newid;save(folder/'manifest.json',md)
 if mutation=='table_bytes':p=next(folder.glob('*.parquet'));p.write_bytes(p.read_bytes()+b'x')
 if mutation=='missing_table':next(folder.glob('*.parquet')).unlink()
 if mutation=='table_inner_id':
  md=load(folder/'manifest.json');name=next(k for k,e in md['tables'].items() if e['rows']>0);p=folder/md['tables'][name]['path'];t=pq.read_table(pa.BufferReader(p.read_bytes()));t=t.set_column(t.schema.get_field_index('snapshot_id'),'snapshot_id',pa.array([newid]*len(t)));pq.write_table(t,p)
  # Rehash all physical descriptions consistently; the original engine data hash must still reject.
  md['tables'][name]['sha256']=H(p.read_bytes());md['manifest_hash']=H(canon({k:v for k,v in md.items() if k not in ('snapshot_id','manifest_hash')}));save(folder/'manifest.json',md)
 try:
  req=bind_research(payload,P/'runs',RID,source_snapshot=SnapshotRef(dataset,SID,m['manifest_hash']))
 except ContractError as exc:assert mutation!='none';parents.append({'case':'physical-'+mutation,'rejected_by':exc.code});continue
 assert mutation=='none';parent_trial('explicit-relocated-nine',json.loads(req.raw),True)
assert source_hashes=={p.name:H(p.read_bytes()) for p in (P/'inputs/dataset'/SID).iterdir()}
# Service-level serialization and persisted mutation probes; retain every failed ledger.
import aqrp.portfolio.service as service
from aqrp.core.canonical import canonical as production_canonical
failure_controls=[]
large=base();large['inputs']['account']['data'].update(equity='1e35',total_cash='1e35');large['policy']['top_k']=1
for row in large['inputs']['prices']['data']:row.update(price='1',lot='3')
for stage in ('wire_before','disk','wire_return'):
 root=O/'publication-controls'/stage
 def corrupt_wire(value):
  d=json.loads(production_canonical(value))
  if isinstance(d,dict) and 'target' in d and ((stage=='wire_before' and 'manifest' not in d) or (stage=='wire_return' and 'manifest' in d)):d['target']['cash']='2'
  return production_canonical(d)
 artifact=ExperimentLedger.artifact
 def corrupt_disk(self,run_id,name,value):
  if name=='result.json':value=copy.deepcopy(value);value['target']['cash']='2'
  return artifact(self,run_id,name,value)
 try:
  with patch.object(ExperimentLedger,'artifact',corrupt_disk) if stage=='disk' else patch.object(service,'canonical',corrupt_wire):result=construct_engineering(seal(copy.deepcopy(large)),root,FIX).read()
  assert stage=='wire_before' and result['status']=='REJECTED' and 'target' not in result
  failure_controls.append({'case':stage,'run_id':result['run_id'],'status':result['status'],'reason':result['reasons']})
 except ContractError as exc:
  assert stage in ('disk','wire_return');rid=next(root.iterdir()).name;status=ExperimentLedger(root).verify(rid)['status']
  if stage=='disk':
   assert status=='FAILED' and (root/rid/'publication-failure.json').exists()
   try:replay_engineering(root,rid);raise AssertionError('failed publication replayed')
   except ContractError as e:assert e.code=='PUBLICATION_FAILED_NOT_REPLAYABLE'
  else:assert status=='SUCCEEDED' # Valid stored result remains valid; corrupt outgoing bytes never returned.
  failure_controls.append({'case':stage,'run_id':rid,'exception':exc.code,'stored_terminal':status})
summary={'fixed_sha':FIX,'executor':'GPT Work supplemental reviewer','independent_exact_reference_cases':len(records),'records':records,'source_parent':{'run_id':RID,'snapshot_id':SID,'nine_original_hashes':source_hashes,'manifest_raw_sha256':H(manifest_raw),'engine_records_independently_checked':len(engine),'original_bytes_unchanged':True},'parent_controls':parents,'publication_controls':failure_controls,'actual_installed_module':service.__file__,'formal_Test':False,'financial_approval':'NONE','result':'PASS'}
(O/'REPAIR_RECHECK_RESULTS.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:summary[k] for k in ['fixed_sha','independent_exact_reference_cases','actual_installed_module','result']}));print(json.dumps({'parent_controls':len(parents),'publication_controls':failure_controls}))
