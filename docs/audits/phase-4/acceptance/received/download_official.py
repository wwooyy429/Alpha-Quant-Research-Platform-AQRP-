import pathlib,json,urllib.request,hashlib,concurrent.futures
O=pathlib.Path(__file__).parent
spec=O/'transient-download.json'
def download(e):
 p=O/(e['label']+'-original.zip')
 with urllib.request.urlopen(e['url'],timeout=90) as r,p.open('wb') as f:
  while b:=r.read(1024*1024):f.write(b)
 return {'label':e['label'],'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
try:
 with concurrent.futures.ThreadPoolExecutor(2) as pool:result=list(pool.map(download,json.loads(spec.read_bytes())))
 (O/'OFFICIAL_DOWNLOAD.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
 print(json.dumps(result))
finally:spec.unlink()
