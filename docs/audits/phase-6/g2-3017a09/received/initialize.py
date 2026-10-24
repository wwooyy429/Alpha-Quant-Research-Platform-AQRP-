from pathlib import Path
import json,subprocess,sys
O=Path(__file__).parent;C=Path('E:/WORK/AQRP-audits/p6-3017a09/src')
FIX='3017a097b49ecdae68228ca9a417fcd03c313200'
records=json.loads((O/'GITHUB_START_BUNDLE.json').read_text(encoding='utf-8-sig'))
for name,value in zip(['PR9_START','CI_RUNS_START','CI_ARTIFACTS_START','CI_JOBS_START'],records):(O/(name+'.json')).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
pr=records[0];assert pr['head_sha']==FIX and 'AQRP_FIXED_REVIEW_SHA: '+FIX in pr['body'] and not pr['merged']
old=Path('C:/Users/11638/AppData/Local/AQRP/reviews/p6-g2-eae807f-independent-20261024')
(O/'run_capture.py').write_text((old/'run_capture.py').read_text().replace('eae807f957f178d19bc55dcfbd668caff5470c6e',FIX),encoding='utf-8')
assert not C.exists();C.parent.mkdir(parents=True,exist_ok=True)
cmds=[['git','clone','--no-local','--no-checkout','E:/WORK/AQRP-audits/p6-eae807f/src',str(C)],['git','-C',str(C),'config','core.longpaths','true'],['git','-C',str(C),'config','core.autocrlf','false'],['git','-C',str(C),'remote','set-url','origin','https://github.com/wwooyy429/Alpha-Quant-Research-Platform-AQRP-.git'],['git','-C',str(C),'fetch','--no-tags','origin',FIX,'59246f9fd391c1713b6bed65dd22280f4d248493',pr['merge_commit_sha']],['git','-C',str(C),'checkout','--detach',FIX],['git','-C',str(C),'status','--porcelain=v1']]
for i,a in enumerate(cmds):subprocess.run([sys.executable,str(O/'run_capture.py'),'init-%02d'%i,str(O)]+a,check=True)
assert subprocess.check_output(['git','-C',str(C),'rev-parse','HEAD'],text=True).strip()==FIX
assert not (C/'.git/objects/info/alternates').exists()
sdk=(old/'run_clean_sdk.py').read_text().replace('p6-eae807f/src','p6-3017a09/src').replace('eae807f957f178d19bc55dcfbd668caff5470c6e',FIX).replace('gpt-p6-eae807f-20261024-','gpt-p6-3017a09-20261024-')
(O/'run_clean_sdk.py').write_text(sdk,encoding='utf-8')
print('Detached checkout ready')
