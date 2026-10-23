from pathlib import Path
import subprocess,json,datetime
O=Path(__file__).parent;C=Path('E:/WORK/AQRP-audits/p5-bfdcf30/src');FIX='bfdcf30e525ff802ea483974f58163eedc029ce8'
assert not C.exists();C.parent.mkdir(parents=True,exist_ok=True)
commands=[['git','clone','--shared','--no-checkout','C:/Users/11638/AppData/Local/AQRP/reviews/p5-g1-review-5262032',str(C)],['git','-C',str(C),'config','core.longpaths','true'],['git','-C',str(C),'config','core.autocrlf','false'],['git','-C',str(C),'remote','set-url','origin','https://github.com/wwooyy429/Alpha-Quant-Research-Platform-AQRP-.git'],['git','-C',str(C),'fetch','--no-tags','origin',FIX,'b379a8f34b9d43859daaf4dd98cc46021304e7c0'],['git','-C',str(C),'checkout','--detach',FIX],['git','-C',str(C),'rev-parse','HEAD'],['git','-C',str(C),'status','--porcelain']]
for argv in commands:
 print(json.dumps({'argv':argv}),flush=True);subprocess.run(argv,check=True)
print('BOOTSTRAP PASS',flush=True)
