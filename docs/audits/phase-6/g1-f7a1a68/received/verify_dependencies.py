from pathlib import Path
import re,json,hashlib,urllib.request,subprocess,datetime
O=Path(__file__).parent;C=Path('E:/WORK/AQRP-audits/p6-f7a1a68/src');P=C/'docs/audits/phase-6';UV=Path('E:/WORK/AQRP-runs/gpt-p5-1c5a7e6-20261023/aqrp-87d64547-3922-4678-b3a4-a5cf51d4da00/venv/Scripts/uv.exe')
def parse(p):
 s=p.read_text(encoding='utf-8').replace('\\\n',' ');out={}
 for line in s.splitlines():
  m=re.match(r'^([A-Za-z0-9_.-]+)==([^\s;]+)',line)
  if m:out[m[1].lower().replace('_','-')]=dict(version=m[2],hashes=set(re.findall(r'--hash=sha256:([a-f0-9]{64})',line)))
 return out
assert subprocess.check_output([str(UV),'--version']).decode().split()[1]=='0.13.4'
core=parse(C/'requirements.lock');results=[];official=[]
for name,version in [('streamlit','1.66.1'),('plotly','7.1.0')]:
 url='https://pypi.org/pypi/'+name+'/'+version+'/json'
 with urllib.request.urlopen(url,timeout=30) as r:raw=r.read()
 (O/(name+'-official-pypi.json')).write_bytes(raw);meta=json.loads(raw);assert meta['info']['version']==version
 official.append(dict(name=name,version=version,url=url,requires_python=meta['info']['requires_python'],metadata_sha256=hashlib.sha256(raw).hexdigest(),requires_dist=meta['info']['requires_dist']))
for platform,ext,count in [('x86_64-pc-windows-msvc','UI_EXTENSION_WINDOWS.lock',51),('x86_64-unknown-linux-gnu','UI_EXTENSION_LINUX.lock',50)]:
 candidate=P/('UI_CANDIDATE_'+platform+'.lock');combined=parse(candidate);extension=parse(P/ext)
 selected={k:v for k,v in core.items() if k!='colorama' or 'windows' in ext.lower()};assert len(selected)==count-29 and len(combined)==count and len(extension)==29
 assert set(combined)==set(selected)|set(extension) and not (set(selected)&set(extension))
 for k,v in selected.items():assert combined[k]['version']==v['version']
 for k,v in extension.items():assert combined[k]==v
 for e in official:
  m=json.loads((O/(e['name']+'-official-pypi.json')).read_bytes());hashes={x['digests']['sha256'] for x in m['urls']};assert combined[e['name']]['hashes']<=hashes
 out=O/('independent-resolution-'+platform+'.lock');argv=[str(UV),'pip','compile',str(candidate),'--python-version','3.13.16','--python-platform',platform,'--generate-hashes','--no-build','--no-header','--no-annotate','--output-file',str(out)]
 started=datetime.datetime.now(datetime.timezone.utc).isoformat()
 with (O/(platform+'.resolve.stdout.log')).open('wb') as stdout,(O/(platform+'.resolve.stderr.log')).open('wb') as stderr:proc=subprocess.run(argv,cwd=O,stdout=stdout,stderr=stderr)
 (O/(platform+'.resolve.command.json')).write_text(json.dumps(dict(argv=argv,cwd=str(O),started_utc=started,ended_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),exit_code=proc.returncode,scope='Independent metadata-only resolution of frozen candidate; no installation'),indent=2)+'\n',encoding='utf-8');assert proc.returncode==0
 actual=parse(out);assert actual==combined,(platform,{k:actual.get(k) for k in set(actual)^set(combined)})
 results.append(dict(platform=platform,combined_packages=count,core_exact_pins=len(selected),extension_only_packages=29,original_core_lock_unchanged=True,independent_resolved_pins_and_hashes_exact=True,installation_import_runtime='NOT VERIFIED / NOT EXECUTED'))
(O/'DEPENDENCY_VERIFICATION.json').write_text(json.dumps(dict(executor='GPT Work supplemental reviewer',official_metadata=official,platforms=results,scope='Fresh official PyPI metadata and frozen candidate resolution only; no UI install/browser/core lock change',result='PASS'),ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(dict(result='PASS',platforms=results)))
