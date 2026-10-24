from pathlib import Path
import json,subprocess,sys
O=Path(__file__).parent;C=Path('E:/WORK/AQRP-audits/p7-3c34e3c/src');FIX='3c34e3ca75c9799307b8a98b34f045b40988bbca';P='d563347ad11e1f26e131dc06e343250282c05c33'
pr=json.loads((O/'PR10_START.json').read_bytes());assert pr['head_sha']==FIX and not pr['merged'] and 'AQRP_FIXED_REVIEW_SHA: '+FIX in pr['body']
old=O.parent/'p6-g2-recheck-3017a09-independent-20261024'
(O/'run_capture.py').write_text((old/'run_capture.py').read_text(encoding='utf-8').replace('3017a097b49ecdae68228ca9a417fcd03c313200',FIX),encoding='utf-8')
assert not C.exists();C.parent.mkdir(parents=True,exist_ok=True)
cmds=[['git','clone','--no-local','--no-checkout','E:/WORK/AQRP-audits/p6-3017a09/src',str(C)],['git','-C',str(C),'config','core.longpaths','true'],['git','-C',str(C),'config','core.autocrlf','false'],['git','-C',str(C),'remote','set-url','origin','https://github.com/wwooyy429/Alpha-Quant-Research-Platform-AQRP-.git'],['git','-C',str(C),'fetch','--no-tags','origin',FIX,P,'7b4864f4d750fa96b5b5634c4bba0cd84b5b077f','a4d650d5d15e814600fde0bb6858fe97f14e5229','e0d8d79cecbb0f3d36ace7fa9fdc983c13b30bee'],['git','-C',str(C),'checkout','--detach',FIX],['git','-C',str(C),'status','--porcelain=v1']]
for i,a in enumerate(cmds):subprocess.run([sys.executable,str(O/'run_capture.py'),'init-%02d'%i,str(O)]+a,check=True)
assert subprocess.check_output(['git','-C',str(C),'show','-s','--format=%P','HEAD'],text=True).strip()==P
assert not (C/'.git/objects/info/alternates').exists()
print('Fixed P7 plan detached checkout ready')
