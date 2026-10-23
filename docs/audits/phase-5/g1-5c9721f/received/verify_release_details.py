import pathlib,json,zipfile,hashlib,xml.etree.ElementTree as ET,urllib.request,urllib.error
O=pathlib.Path(__file__).parent;C=O.parent/'p5-g1-review-5c9721f';canon=lambda x:json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode();H=lambda b:hashlib.sha256(b).hexdigest()
with zipfile.ZipFile(O/'Phase4-merged-main-SDK-original.zip') as z:
 prefix=next(n[:-len('upload-selection.json')] for n in z.namelist() if n.endswith('upload-selection.json'));J=lambda p:json.loads(z.read(prefix+p));selected={e['path'] for e in J('upload-selection.json')['files']};cov=J('coverage.json');critical=[]
 for name,d in cov['files'].items():
  if '/portfolio/' in name.replace('\\','/') or '/risk/' in name.replace('\\','/'):
   s=d['summary'];line=s['covered_lines']/max(1,s['num_statements']);branch=s['covered_branches']/s['num_branches'] if s['num_branches'] else 1
   assert not s['num_statements'] or line>=.95 and branch>=.9;critical.append({'module':name,'line':line,'branch':branch})
 snapshots=chains=factors=0
 for n in sorted(p for p in selected if p.endswith('/manifest.json')):
  m=J(n);root=str(pathlib.PurePosixPath(n).parent)
  if 'tables' in m:
   assert H(canon({k:v for k,v in m.items() if k not in ('snapshot_id','manifest_hash')}))==m['manifest_hash']
   for e in m['tables'].values():assert H(z.read(prefix+root+'/'+e['path']))==e['sha256']
   snapshots+=1
  if 'event_prefix_hash' in m:
   for e in m['files']:assert H(z.read(prefix+root+'/'+e['path']))==e['sha256']
   events=[json.loads(x) for x in z.read(prefix+root+'/events.jsonl').splitlines()];prev='0'*64
   for i,e in enumerate(events):assert e['seq']==i and e['previous']==prev and e['hash']==H(canon({k:v for k,v in e.items() if k!='hash'}));prev=e['hash']
   assert events[-1]['kind']==m['status'] and events[-1]['payload']['manifest_sha256']==H(z.read(prefix+n)) and events[-2]['hash']==m['event_prefix_hash'];chains+=1
  if 'artifacts' in m:
   for e in m['artifacts']:assert H(z.read(prefix+root+'/'+e['path']))==e['sha256']
   factors+=1
 replay=J('reproduction/result.json');assert replay['status']=='THREE_ORIGINAL_REFS_EXECUTED';portfolio=J('portfolio/summary.json');assert portfolio['orders_submitted']==0 and portfolio['formal_gate']['reasons']==['APPROVAL_REQUIRED'] and portfolio['financial_approval']=='NONE'
# Verify that redundant status fields were retained with the original values.
s=json.loads((O/'SCOPE_VERIFICATION.json').read_bytes())['status_errata'];hist=s['new_status']['historical_status_fields'];assert hist['source_commit']=='32ea5d6b75c84c07017d87377eeabd2f78207c5c'
for k,v in hist['values'].items():assert s['old_status'][k]==v
logs=[]
for p in (C/'docs/audits/phase-4/publication').rglob('*'):
 if p.is_file() and any(t in p.name.lower() for t in ('original20','original-four','original4','original91','independent-implementation-math')):
  logs.append({'path':p.relative_to(C).as_posix(),'bytes':p.stat().st_size,'sha256':H(p.read_bytes())})
result={'scope':'Independent byte/manifest verification of developer postmerge P4 baseline; no new SDK execution','critical_coverage':critical,'snapshot_manifests':snapshots,'terminal_chains':chains,'factor_manifests':factors,'original_ref_replay':'PASS','formal_gate':'APPROVAL_REQUIRED','status_old_values_exactly_preserved':True,'original_regression_logs':logs,'result':'PASS'}
(O/'P4_RELEASE_DETAILS_VERIFICATION.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
# Direct run endpoint disambiguates a first-page filtered connector query returning [].
url='https://api.github.com/repos/wwooyy429/Alpha-Quant-Research-Platform-AQRP-/actions/runs/39807961404'
try:
 with urllib.request.urlopen(url,timeout=25) as r:run=json.load(r)
 run={'lookup_url':url,'response':run,'raw_artifacts_downloaded_this_turn':False,'scope':'Existing P4 code CI only, not P5 implementation tests'}
except (urllib.error.HTTPError,urllib.error.URLError) as e:run={'lookup_url':url,'error':str(e),'status':'NOT_VERIFIED_CURRENT_RUN_DETAILS','raw_artifacts_downloaded_this_turn':False}
(O/'PR8_CI_DIRECT_LOOKUP.json').write_text(json.dumps(run,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'P4_details':'PASS','original_regression_logs':len(logs),'CI_direct_status':run.get('response',{}).get('conclusion',run.get('status'))}))
