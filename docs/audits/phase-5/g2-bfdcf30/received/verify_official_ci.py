"""Independent ZIP/API, alias-subtree, installed-wheel, JUnit and coverage audit."""
from pathlib import Path, PurePosixPath
import json,hashlib,zipfile,io,re,xml.etree.ElementTree as ET
O=Path(__file__).parent;D=O.parent/'p5-g2-bfdcf30';C=Path('E:/WORK/AQRP-audits/p5-bfdcf30/src')
FIX='bfdcf30e525ff802ea483974f58163eedc029ce8';MERGE='b379a8f34b9d43859daaf4dd98cc46021304e7c0'
H=lambda b:hashlib.sha256(b).hexdigest()
api=json.loads((O/'CI_ARTIFACTS_API.json').read_bytes())['artifacts'];results=[]
for art in api:
 zpath=D/'official-ci'/(art['name']+'-official-original.zip')
 with zpath.open('rb') as f:h=hashlib.file_digest(f,'sha256').hexdigest()
 assert h==art['digest'].removeprefix('sha256:') and zpath.stat().st_size==art['size_in_bytes']
 with zipfile.ZipFile(zpath) as z:
  assert z.testzip() is None and len(z.namelist())==len(set(z.namelist()))
  ns=[n for n in z.namelist() if n.endswith('upload-selection.json')];assert len(ns)==1
  prefix=ns[0][:-len('upload-selection.json')];selection=json.loads(z.read(ns[0]));selected={e['path']:e['sha256'] for e in selection['files']}
  allnames={n[len(prefix):]:n for n in z.namelist()};assert all(n.startswith(prefix) for n in z.namelist())
  assert len(selected)==len(selection['files']) and set(selected)<=set(allnames)
  hashes={n:H(z.read(full)) for n,full in allnames.items()}
  assert all(hashes[n]==v for n,v in selected.items())
  extras=set(allnames)-set(selected)-{'upload-selection.json'};groups={}
  for n in extras:
   parts=PurePosixPath(n).parts;idx=next((i for i,v in enumerate(parts[:-1]) if v.endswith('current')),None)
   assert idx is not None and parts[0]=='tmp',n
   alias='/'.join(parts[:idx+1]);suffix='/'.join(parts[idx+1:]);groups.setdefault(alias,{})[suffix]=hashes[n]
  mappings=[]
  for alias,contents in sorted(groups.items()):
   parent,base=alias.rsplit('/',1);stem=base[:-len('current')]
   possible={n.split('/')[len(PurePosixPath(parent).parts)] for n in selected if n.startswith(parent+'/')}
   matched=[]
   for candidate in sorted(possible):
    if not re.fullmatch(re.escape(stem)+r'\d+',candidate):continue
    target=parent+'/'+candidate+'/'
    subtree={n[len(target):]:h for n,h in selected.items() if n.startswith(target)}
    if subtree==contents:matched.append(target[:-1])
   assert matched,(alias,len(contents))
   mappings.append({'alias':alias,'files':len(contents),'byte_equivalent_selected_subtrees':matched,'original_symlink_target_metadata':'NOT UPLOADED / NOT CLAIMED'})
  assert len(extras)==3429 and len(groups)==189
  def read(n):return z.read(prefix+n)
  def J(n):return json.loads(read(n))
  env=J('environment.json');assert env['complete'] and not env['dirty'] and env['code_commit']==MERGE
  assert env['github_run_id']=='39839529359' and env['github_run_attempt']=='1'
  assert env['lock_sha256']==H((C/'requirements.lock').read_bytes())
  junit=ET.fromstring(read('junit.xml'));tests=junit.findall('.//testcase');assert len(tests)==1049 and all(not junit.findall('.//'+n) for n in ['failure','error','skipped'])
  wrname=next(n for n in selected if n.startswith('wheel/') and n.endswith('.whl'));wr=read(wrname);assert H(wr)==env['wheel_sha256']
  with zipfile.ZipFile(io.BytesIO(wr)) as wheel:
   modules=[n for n in wheel.namelist() if n.startswith('aqrp/') and n.endswith('.py')];assert len(modules)==69
   for n in modules:assert wheel.read(n)==(C/'src'/n).read_bytes(),n
   assert wheel.read('aqrp/factors/reviewed_code.json')==(C/'src/aqrp/factors/reviewed_code.json').read_bytes()
  coverage=J('coverage.json');critical=[]
  for name,data in coverage['files'].items():
   n=name.replace('\\','/');s=data['summary'];line=100*s['covered_lines']/max(1,s['num_statements']);branch=100*s['covered_branches']/s['num_branches'] if s['num_branches'] else 100
   if any('/'+p+'/' in n for p in ['backtest','execution','performance']) or n.endswith('/services/backtest.py'):
    assert not s['num_statements'] or (line>=95 and branch>=90),(n,line,branch);critical.append({'module':n,'statements':s['num_statements'],'line':line,'branch':branch})
  expected_critical={p.relative_to(C/'src').as_posix() for d in ['backtest','execution','performance'] for p in (C/'src/aqrp'/d).glob('*.py')}|{'aqrp/services/backtest.py'}
  observed_critical={v['module'][v['module'].rfind('/aqrp/')+1:] for v in critical}
  assert observed_critical==expected_critical,(observed_critical,expected_critical)
  for factor in ['momentum','reversal']:
   result=J('backtest/'+factor+'-result.json');assert result['status']=='SUCCEEDED' and result['financial_approval']=='NONE'
   run=result['run_id'];root='backtest/'+factor+'-runs/'+run+'/'
   m=J(root+'manifest.json');assert m==result['manifest']
   chain=[json.loads(b) for b in read(root+'events.jsonl').splitlines()]
   canonical=lambda x:json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()
   prior='0'*64
   for idx,e in enumerate(chain):
    assert e['seq']==idx and e['previous']==prior and H(canonical({k:v for k,v in e.items() if k!='hash'}))==e['hash'];prior=e['hash']
   assert chain[-1]['kind']=='SUCCEEDED' and H(read(root+'manifest.json'))==chain[-1]['payload']['manifest_sha256']
   assert m['run_id']==run and m['event_prefix_hash']==chain[-2]['hash']
   for e in m['files']:assert H(read(root+e['path']))==e['sha256'],root+e['path']
   for e in J(root+'transaction-files.json'):assert H(read(root+e['path']))==e['sha256'],root+e['path']
   persisted=J(root+'result.json');assert persisted=={k:v for k,v in result.items() if k!='manifest'}
  dest=O/('ci-'+art['name']);dest.mkdir()
  for n in ['environment.json','junit.xml','coverage.json','commands.log','upload-selection.json','backtest/summary.json','backtest/independent-reference.json','backtest/momentum-request.json','backtest/momentum-result.json','backtest/reversal-request.json','backtest/reversal-result.json']:
   p=dest/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(read(n))
  report={'artifact':art,'sha256':h,'CRC_all_selected_hashes':'PASS','selected':len(selected),'official_members':len(allnames),'extra_files':len(extras),'extra_alias_groups':len(groups),'independent_alias_mapping':mappings,'tests':len(tests),'installed_wheel_modules_match_fixed_source':69,'environment':env,'critical_coverage':critical,'actual_backtest_terminal_chains_files_return_binding':'PASS','scope':'Official CI bytes independently checked; not a new GPT execution on those remote OS hosts','result':'PASS'}
  (dest/'VERIFIED.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');results.append({k:v for k,v in report.items() if k!='independent_alias_mapping'})
(O/'OFFICIAL_CI_VERIFICATION.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'artifacts':len(results),'each_tests':1049,'each_extra_files':3429,'each_alias_groups':189,'all_hashes_and_whole_subtrees':'PASS'}))
