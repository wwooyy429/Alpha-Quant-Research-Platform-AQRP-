from pathlib import Path
import json,subprocess
O=Path(__file__).parent;C=Path('E:/WORK/AQRP-audits/p5-35f93d6/src');FIX='35f93d640a2304121131d947a465f57a951cf63f'
assert not C.exists();C.parent.mkdir(parents=True,exist_ok=True)
pr=json.loads((O/'PR8_START.json').read_bytes());assert pr['head_sha']==FIX and ('AQRP_FIXED_REVIEW_SHA: '+FIX) in pr['body']
merge=pr['merge_commit_sha']
commands=[['git','clone','--no-local','--no-checkout','E:/WORK/AQRP-audits/p5-bfdcf30/src',str(C)],['git','-C',str(C),'config','core.longpaths','true'],['git','-C',str(C),'config','core.autocrlf','false'],['git','-C',str(C),'remote','set-url','origin','https://github.com/wwooyy429/Alpha-Quant-Research-Platform-AQRP-.git'],['git','-C',str(C),'fetch','--no-tags','origin',FIX,merge],['git','-C',str(C),'checkout','--detach',FIX],['git','-C',str(C),'rev-parse','HEAD'],['git','-C',str(C),'status','--porcelain']]
for argv in commands:print(json.dumps({'argv':argv}),flush=True);subprocess.run(argv,check=True)
print('BOOTSTRAP PASS',flush=True)
