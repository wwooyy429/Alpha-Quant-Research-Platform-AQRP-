import pathlib,json,hashlib,random,copy,sys,datetime
from fractions import Fraction as Q
from independent_reference import reference
from aqrp.portfolio.contracts import PortfolioRequest,TargetCandidate
from aqrp.portfolio.service import construct_engineering,replay_engineering
from aqrp.portfolio.construct import build_candidate
from aqrp.risk.checks import check_target
from aqrp.core.errors import ContractError
O=pathlib.Path(__file__).parent;C=O.parent/'p4-g2-recheck-3c87579';FIX='3c8757949b0fd5c97953b06a74ebc2d0e56676e4';F=C/'tests/portfolio/fixtures';OUT=O/'independent-runs';OUT.mkdir(exist_ok=True)
def read(p):return json.loads(p.read_bytes())
def canon(x):return json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()
def digest(x):return hashlib.sha256(canon(x)).hexdigest()
def seal(x):
 es=[e for k,e in x['inputs'].items() if k!='scores']+x['inputs']['scores']
 for e in es:e['content_sha256']=digest({k:v for k,v in e.items() if k!='content_sha256'})
 x['source']['fixture_manifest']={e['ref']:e['content_sha256'] for e in es};return PortfolioRequest(canon(x))
def base():return read(F/'base.json')
records=[];mismatches=[]
def compare_value(actual,expected,path=''):
 if isinstance(expected,dict):
  for k,v in expected.items():compare_value(actual[k],v,path+'.'+k)
 else:
  assert abs(Q(actual)-expected)<=max(Q(1,10**24),abs(expected)*Q(1,10**32)),(path,actual,str(expected))
def trial(name,x):
 expect=reference(x);req=seal(x);result=construct_engineering(req,OUT,FIX).read();errors=[]
 try:
  assert result['status']==expect['status'],('status',result['status'],expect['status'])
  if expect['status']=='INFEASIBLE':assert expect['reason'] in result['reasons']
  else:
   assert result['selection']['ranked']==expect['ranked'];compare_value(result['selection']['scores'],expect['scores'])
   for phase in ['pre','post']:
    compare_value(result['risk'][phase]['metrics'],expect[phase]['metrics'],phase)
    codes=sorted({c['code'] for c in result['risk'][phase]['checks'] if not c['passed']});assert codes==expect[phase]['failures'],(phase,codes,expect[phase]['failures'])
  assert result['executable'] is False and result['financial_approval']=='NONE'
  assert ('target' in result)==(result['status']=='SUCCEEDED')
  replay=replay_engineering(OUT,result['run_id']);assert replay['result']['status']==result['status']
 except (AssertionError,KeyError) as e:errors.append(repr(e));mismatches.append({'case':name,'errors':errors,'run_id':result['run_id']})
 records.append({'case':name,'run_id':result['run_id'],'request_hash':req.content_hash,'expected_status':expect['status'],'actual_status':result['status'],'match':not errors,'errors':errors})
for name in ['base','x01','x03','x04','odd_hold','short_close']:trial('frozen-'+name,read(F/(name+'.json')))
# Deterministic generated requests, covering 2-6 assets, two factors/signed coefficients,
# both weighting/mode rules, old long/short/odd positions, permission and risk failures.
rng=random.Random(20261022)
for i in range(160):
 x=base();n=2+i%5;ids=[f'SYNTH:{chr(65+j)}' for j in range(n)]
 for k,e in x['inputs'].items():
  if k in ['account','scores']:continue
  proto=e['data'][0];e['data']=[{**copy.deepcopy(proto),'security_id':s} for s in ids]
 prices=[rng.choice([3,10,37,60]) for _ in ids];old=[rng.choice([-5,-1,0,0,1,5]) for _ in ids]
 for j,s in enumerate(ids):
  x['inputs']['prices']['data'][j].update(price=str(prices[j]),lot=rng.choice(['1','3','10','0.1']))
  x['inputs']['securities']['data'][j]['symbol']=s
  x['inputs']['status']['data'][j].update(tradable=rng.randrange(12)!=0,in_universe=rng.randrange(12)!=0)
  x['inputs']['exposures']['data'][j].update(beta=rng.choice(['-1','0','0.8','1.2','2']),industry='I' if j%2==0 else 'J')
  x['inputs']['permissions']['data'][j].update(sellable_qty=str(max(old[j],0) if i%7 else 0),short_permission=i%13!=0,borrow_limit_total='100000' if i%9 else '2')
 a=x['inputs']['account']['data'];E=10000;nonshort=rng.choice([0,0,15]);short=sum(max(-q*price,0) for q,price in zip(old,prices));cash=E-sum(q*price for q,price in zip(old,prices));a.update(equity=str(E),total_cash=str(cash),restricted_cash=str(short+nonshort),short_restriction=str(short),nonshort_restriction=str(nonshort),positions=[{'security_id':s,'quantity':str(q)} for s,q in zip(ids,old)])
 score_proto=x['inputs']['scores'][0]['data']['rows'][0]
 x['inputs']['scores'][0]['data']['rows']=[{**copy.deepcopy(score_proto),'security_id':s,'score':str(rng.randint(-4,7))} for s in ids]
 if i%3==0:
  e=copy.deepcopy(x['inputs']['scores'][0]);e['ref']='second-factor';e['data']['factor_key']='F2'
  for row in e['data']['rows']:row['score']=str(rng.randint(-3,6))
  if i%6==0:e['data']['rows'][0].update(valid=False,score=None)
  x['inputs']['scores'].append(e);x['policy']['factor_weights']={'F1':'3','F2':'-1' if i%2 else '1'}
 ls=i%2==0;x['policy'].update(mode='LONG_SHORT' if ls else 'LONG_ONLY',weighting='score' if i%4<2 else 'equal',gross=rng.choice(['0','0.5','1','1.2']) if ls else '1',net='0' if ls else '1',top_k=rng.randint(1,n+1),long_k=rng.randint(1,n),short_k=rng.randint(1,n))
 x['profile']['allow_full_close_odd_lot']=i%2==0;x['profile']['fee_reserve']=rng.choice(['0','0','10'])
 lim=x['constraints'];lim['per_asset']={s:rng.choice(['0.4','1']) for s in ids};lim['industries']={k:{'net_min':'-1','net_max':'1','gross_max':'0.8' if i%11==0 else '2'} for k in ['I','J']};lim['turnover_max']=rng.choice(['0.5','1','2']);lim['beta_min']='-0.5';lim['beta_max']='0.5';lim['allow_cash_only']=i%7!=0
 trial(f'grid-{i:03}',x)
# Explicit approved G01..G20 calculation families via complete public service.
for label,mode,weighting,scores in [('G03-ties','LONG_ONLY','equal',[1,1]),('G04-negative','LONG_ONLY','score',[-1,-2]),('G05-negative-equal','LONG_ONLY','equal',[-1,-2]),('G07-two-legs','LONG_SHORT','equal',[3,1]),('G08-budget-funding','LONG_SHORT','equal',[3,1])]:
 x=base();x['policy'].update(mode=mode,weighting=weighting,net='0' if mode=='LONG_SHORT' else '1')
 for row,v in zip(x['inputs']['scores'][0]['data']['rows'],scores):row['score']=str(v)
 if label.startswith('G08'):x['policy'].update(gross='1.2',net='0.2')
 trial(label,x)
for label,mode in [('G10-round-long','LONG_ONLY'),('G11-round-short','LONG_SHORT'),('G14-net-post','LONG_SHORT')]:
 x=base();x['policy'].update(mode=mode,weighting='equal',net='0' if mode=='LONG_SHORT' else '1')
 for row,p in zip(x['inputs']['prices']['data'],[30,40]):row.update(price=str(p),lot='10')
 if label.startswith('G14'):x['constraints']['net_min']='0'
 trial(label,x)
# Absolute input/PIT negative controls, preserving valid hashes when attacking semantics.
negative=[]
for kind in ['securities','prices','status','exposures','permissions','account','scores']:
 for field in ['event_time','available_at','as_of']:
  x=base();e=x['inputs'][kind][0] if kind=='scores' else x['inputs'][kind];e[field]='2024-02-01T16:00:00.000001Z';r=construct_engineering(seal(x),OUT,FIX).read();ok=r['status']=='REJECTED' and 'target' not in r and 'selection' not in r;assert ok;negative.append({'case':kind+'.'+field,'reason':r['reasons'],'run_id':r['run_id']})
req=seal(base());c=build_candidate(req)
for label,obj in [('candidate-bytes',TargetCandidate(c.raw+b' ',c.request_hash)),('request-hash',TargetCandidate(c.raw,'0'*64))]:
 try:check_target(obj,req);raise AssertionError('tamper accepted')
 except ContractError as e:negative.append({'case':label,'reason':e.code})
summary={'actual_executor':'GPT Work supplemental reviewer','fixed_sha':FIX,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'independent_reference':'independent_reference.py has no AQRP imports','full_public_service_cases':len(records),'matching':sum(r['match'] for r in records),'mismatches':mismatches,'negative_controls':negative,'records':records,'installed_aqrp':__import__('aqrp').__file__,'formal_Test_executed':False}
(O/'INDEPENDENT_BEHAVIOR_RESULTS.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in summary.items() if k not in ['records','negative_controls']}));assert not mismatches
