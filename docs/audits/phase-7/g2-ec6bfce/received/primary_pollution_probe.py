"""Primary adversarial engineering probe. Isolated roots, not statistical samples."""
import sys,json,pathlib,hashlib,uuid,subprocess,datetime
O=pathlib.Path(__file__).parent.resolve();C=pathlib.Path('E:/WORK/AQRP-audits/p7-ec6bfce/src');S='ec6bfcedc0c424b6fa3e817c9a094385bd971d6f'
import aqrp
site=pathlib.Path(aqrp.__file__).parent;identity=[]
source={p.relative_to(C/'src/aqrp').as_posix():p for p in (C/'src/aqrp').rglob('*.py')};installed={p.relative_to(site).as_posix():p for p in site.rglob('*.py')};assert set(source)==set(installed) and len(source)==86
for name,p in source.items():
 h=hashlib.sha256(p.read_bytes()).hexdigest();assert h==hashlib.sha256(installed[name].read_bytes()).hexdigest();identity.append({'path':name,'sha256':h})
from aqrp.services.task_requests import initialize,research_request
from aqrp.services.tasks import TaskService
from aqrp.services.research import research
from aqrp.experiments.ledger import read_chain
from aqrp.experiments.admission import BudgetAuthority
root=pathlib.Path('E:/AQ7')/('primary-pollution-'+uuid.uuid4().hex[:8]);root.mkdir(exist_ok=False)
variant={'factor_ids':['momentum'],'horizons':[1],'start':'2024-01-06','end':'2024-01-06'};results=[]
for mode in ['legacy_api','legacy_cli','task']:
 w=root/mode;cat=initialize(w,S);service=TaskService(w)
 plans=[service.register_campaign(n,[variant]) for n in ['campaign-a','campaign-b']]
 assert all(not p['registration_history']['contaminated_before_registration'] for p in plans)
 fa=service.freeze({**variant,'campaign_id':'campaign-a'});fb=service.freeze({**variant,'campaign_id':'campaign-b'})
 a=service.submit(fa,'cancel-before-R');assert service.cancel(a['task_id'])=='CANCELLED'
 assert service.status(a['task_id'])['slots']=={} and not (w/'research-runs/trials.jsonl').exists()
 request=research_request(w,json.loads(fb.raw));control=None
 if mode=='legacy_api':
  b=research(request,w/'research-runs');run=b['run_id']
 elif mode=='legacy_cli':
  payload={'config':json.loads(request.config),'snapshot':cat['snapshot'],'exposures':cat['exposures'],'coverage':json.loads(cat['coverage']['payload']),'code_commit':S}
  path=w/'original-legacy-request.json';path.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
  argv=[sys.executable,'-B','-m','aqrp.services.cli',str(path),'--output',str(w/'research-runs')];start=datetime.datetime.now(datetime.timezone.utc).isoformat()
  p=subprocess.run(argv,cwd=root,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
  (O/'pollution-legacy-cli.stdout.log').write_bytes(p.stdout);(O/'pollution-legacy-cli.stderr.log').write_bytes(p.stderr)
  (O/'pollution-legacy-cli.command.json').write_text(json.dumps({'argv':argv,'cwd':str(root),'started_utc':start,'ended_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'exit_code':p.returncode,'executor':'Primary GPT Work'},indent=2)+'\n',encoding='utf-8')
  assert p.returncode==0,(p.stdout,p.stderr);run=json.loads(p.stdout)['run_id']
 else:
  b=service.submit(fb,'actual-task-b');b=service.work(b['task_id']);assert b['status']=='SUCCEEDED';run=b['result']['research_run_id'];control=b['research_control']
 report=json.loads((w/'research-runs'/run/'report.json').read_bytes());trial=read_chain(w/'research-runs/trials.jsonl');assert len(trial)==1 and not trial[0]['payload']['repeat_of']
 with BudgetAuthority(w).transaction() as c:history=BudgetAuthority(w).history(c)
 assert history['admitted_units']==2
 results.append({'mode':mode,'workspace':str(w),'campaign_registrations':plans,'cancelled_A_task':service.status(a['task_id']),'B_run_id':run,'B_lineage':json.loads((w/'research-runs'/run/'lineage.json').read_bytes()),'B_task_control':control,'B_trial':trial[0],'B_multiplicity':report['multiplicity'],'authority_history':history})
out={'executor':'Primary GPT Work','fixed_sha':S,'python':sys.version,'executable':sys.executable,'installed_root':str(site),'source_identity86':identity,'fixture_root':str(root),'context':'Three independent code-control fixtures, same logical clean-registration and A-cancel-before-R history; no repeated B research within any fixture','results':results}
(O/'PRIMARY_POLLUTION_REPRODUCTION.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps([{'mode':r['mode'],'contaminated':r['B_multiplicity']['contaminated'],'cross_campaign':r['B_trial']['payload']['cross_campaign_data_access'],'repeat_of':r['B_trial']['payload']['repeat_of'],'admitted_units':r['authority_history']['admitted_units']} for r in results]))
assert results[0]['B_multiplicity']['contaminated'] is False and results[1]['B_multiplicity']['contaminated'] is False and results[2]['B_multiplicity']['contaminated'] is True
