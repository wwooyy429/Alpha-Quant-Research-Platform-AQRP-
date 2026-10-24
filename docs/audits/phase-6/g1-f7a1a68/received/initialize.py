from pathlib import Path
import json,subprocess
O=Path(__file__).parent;old=O.parent/'p5-g2-backing-recheck-1c5a7e6-independent'
FIX='f7a1a68c5f747090f8c8a0e934f2fea859aec998';C=Path('E:/WORK/AQRP-audits/p6-f7a1a68/src')
s=(old/'run_capture.py').read_text(encoding='utf-8').replace('1c5a7e62cace7c3e66b7cc7f12fd564cb0013654',FIX)
(O/'run_capture.py').write_text(s,encoding='utf-8')
assert not C.exists();C.parent.mkdir(parents=True,exist_ok=True)
pr=json.loads((O/'PR9_START.json').read_bytes());assert pr['head_sha']==FIX and 'AQRP_FIXED_REVIEW_SHA: '+FIX in pr['body']
commands=[['git','clone','--no-local','--no-checkout','E:/WORK/AQRP-audits/p5-1c5a7e6/src',str(C)],['git','-C',str(C),'config','core.longpaths','true'],['git','-C',str(C),'config','core.autocrlf','false'],['git','-C',str(C),'remote','set-url','origin','https://github.com/wwooyy429/Alpha-Quant-Research-Platform-AQRP-.git'],['git','-C',str(C),'fetch','--no-tags','origin',FIX,'59246f9fd391c1713b6bed65dd22280f4d248493',pr['merge_commit_sha']],['git','-C',str(C),'checkout','--detach',FIX],['git','-C',str(C),'status','--porcelain']]
for a in commands:print(json.dumps(dict(argv=a)),flush=True);subprocess.run(a,check=True)
print('Fixed clone PASS')
