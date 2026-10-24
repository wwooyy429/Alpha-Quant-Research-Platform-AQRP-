from pathlib import Path
import json,subprocess,sys
O=Path(__file__).parent
C=Path('E:/WORK/AQRP-audits/p6-e71f6f0/src')
FIX='e71f6f090b102e4abfd70a5999e495f49546a1b5'
pr=json.loads((O/'PR9_START.json').read_bytes())
assert pr['head_sha']==FIX and 'AQRP_FIXED_REVIEW_SHA: '+FIX in pr['body']
assert not C.exists();C.parent.mkdir(parents=True,exist_ok=True)
commands=[['git','clone','--no-local','--no-checkout','E:/WORK/AQRP-audits/p6-f7a1a68/src',str(C)],['git','-C',str(C),'config','core.longpaths','true'],['git','-C',str(C),'config','core.autocrlf','false'],['git','-C',str(C),'remote','set-url','origin','https://github.com/wwooyy429/Alpha-Quant-Research-Platform-AQRP-.git'],['git','-C',str(C),'fetch','--no-tags','origin',FIX,'59246f9fd391c1713b6bed65dd22280f4d248493',pr['merge_commit_sha']],['git','-C',str(C),'checkout','--detach',FIX],['git','-C',str(C),'status','--porcelain']]
for n,a in enumerate(commands):
 print(json.dumps({'argv':a}),flush=True)
 subprocess.run([sys.executable,str(O/'run_capture.py'),'init-%02d'%n,str(O)]+a,check=True)
assert subprocess.check_output(['git','-C',str(C),'rev-parse','HEAD'],text=True).strip()==FIX
assert not (C/'.git/objects/info/alternates').exists()
print('FIXED DETACHED CHECKOUT PASS')

