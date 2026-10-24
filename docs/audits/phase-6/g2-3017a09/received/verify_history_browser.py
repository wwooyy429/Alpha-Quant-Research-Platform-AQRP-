"""Evidence lineage and raw browser checks; no AQRP imports."""
from pathlib import Path
import json,hashlib,zipfile,xml.etree.ElementTree as ET,subprocess
O=Path(__file__).parent;D=Path('C:/Users/11638/AppData/Local/AQRP/reviews/p6-g2-3017a09-developer-20261024T092710Z');P=D/'payload';C=Path('E:/WORK/AQRP-audits/p6-3017a09/src')
H=lambda b:hashlib.sha256(b).hexdigest()
def fh(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
old=json.loads((P/'independent-original/ORIGINAL_ZIP_RETENTION.json').read_bytes());path=Path(old['path'])
assert path.stat().st_size==old['bytes']==902364045 and fh(path)==old['sha256']=='086c0a1d7128c241bff30cfed32f9d5178940c9decf3942cd462021f30983b3c'
with zipfile.ZipFile(path) as z:
 assert z.testzip() is None
 m=json.loads(z.read('EVIDENCE_MANIFEST.json'));assert len(m['files'])==304
 for e in m['files']:
  with z.open(e['path']) as f:assert hashlib.file_digest(f,'sha256').hexdigest()==e['sha256']
for p in (C/'docs/audits/phase-6/g2-eae807f/received').rglob('*'):
 if p.is_file():
  original=path.parent/p.relative_to(C/'docs/audits/phase-6/g2-eae807f/received')
  # Repository adds original probe paths under probes/ in the received archive.
  if not original.is_file() and p.parent.name=='probes':original=path.parent/p.name
  if original.is_file():assert p.read_bytes()==original.read_bytes(),str(p)
hist=[]
for name,sha in [('C3-failed-official-original','418c17fad8fefe50dedc866f95c14ccf0fa433ca'),('C4-failed-official-original','d432c6d23a88fc7a288812760793c17ede602951'),('C5-official-originals-and-verification','e20f8edc49cba1af883ed72436d68492a368dc3a')]:
 files=[P/'history'/name/('early-windows-attempt1-original.zip' if name.startswith('C5') else 'phase6-windows-latest-1-official-original.zip')]
 for p in files:
  with zipfile.ZipFile(p) as z:
   assert z.testzip() is None
   ns=z.namelist();envfile=min([n for n in ns if n.endswith('/environment.json')],key=lambda n:len(n.split('/')))
   env=json.loads(z.read(envfile));assert env['code_commit']==sha and not env['complete']
   xml=[n for n in ns if n.endswith('/junit.xml')]
   failures=[]
   if xml:
    cases=ET.fromstring(z.read(min(xml,key=lambda n:len(n.split('/'))))).findall('.//testcase')
    failures=[dict(name=x.attrib.get('name'),text=''.join(x.find('failure').itertext())) for x in cases if x.find('failure') is not None]
    assert len(failures)==1
    assert '3221225477' in failures[0]['text'] or '1073741819' in failures[0]['text']
   if name.startswith('C5'):
    assert p.stat().st_size==136825457 and fh(p)=='8974dc8c0ec85052fdc6118fd7c2052c951ae92349f1e424d5ba79f3896b9a7a'
   hist.append(dict(path=str(p.relative_to(P)),bytes=p.stat().st_size,sha256=fh(p),code_commit=sha,complete=False,failures=failures,not_relabelled_as_pass=True))
browser=P/'browser';bm=json.loads((browser/'BROWSER_FILES_SHA256.json').read_bytes())
assert bm['fixed_sha']=='3017a097b49ecdae68228ca9a417fcd03c313200'
for e in bm['files']:
 p=browser/e['path'];assert p.stat().st_size==e['bytes'] and fh(p)==e['sha256']
actions=[json.loads(l) for l in (browser/'browser/actions.jsonl').read_bytes().splitlines()]
assert len(actions)==57 and sum(bool(x['screenshot']) for x in actions)==27
text='\n'.join((browser/'browser'/x['ax']).read_text(encoding='utf-8') for x in actions)
assert all('heading '+name in text for name in ['Dashboard','Factor Library','Alpha Research','Strategy Backtest','Experiment Manager','Settings'])
for x in actions:
 if x['screenshot']:assert (browser/'browser'/x['screenshot']).read_bytes().startswith(bytes.fromhex('ffd8'))
par=json.loads((browser/'browser/VERIFIED_BROWSER_PARITY.json').read_bytes())
assert par['fixed_sha']=='3017a097b49ecdae68228ca9a417fcd03c313200' and par['real_browser_executed'] and par['result']=='PASS'
assert par['default_literal_values']==[3,2,4,3] and par['original_source_files_unchanged']==42 and par['original_task_requests_unchanged']==12
for factor in ['momentum','reversal']:
 assert par['factors'][factor]['all_five_actors_match_exact_finance_and_research']
 assert par['factors'][factor]['alpha_only_metrics_and_oos_match']
 for v in par['factors'][factor]['comparisons'].values():assert v['research_equal'] and v['financial_exact_equal']
ctrl=json.loads((browser/'controls/browser/VERIFIED_CONTROLS.json').read_bytes())
assert ctrl['unregistered_variant_no_side_effects'] and ctrl['core_literal_cash']=='98.1' and ctrl['core_literal_equity']=='998.1'
assert ctrl['risk']['status']=='FAILED' and ctrl['cancel']['status']=='CANCELLED'
out=dict(result='PASS',original_independent_zip=old,retained_failed_CI=hist,developer_browser=dict(raw_files=len(bm['files']),main_observations=57,main_screenshots=27,all_6_pages=True,originals42=True,oldrequests12=True,main_text_failclosed='APPROVAL_REQUIRED' in text,controls=ctrl),scope='Developer actual browser evidence and original failure bytes independently checked; reviewer CUA tasks/SDK are separately reported. Does not prove original ACLs or exact historic host.')
(O/'HISTORY_AND_DEVELOPER_BROWSER_VERIFICATION.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('History, failed original CI and developer browser bytes PASS')
