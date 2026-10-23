from pathlib import Path
import json,subprocess
O=Path(__file__).parent
P=Path('C:/Users/11638/AppData/Local/AQRP/reviews/p5-g2-recheck-35f93d6-independent')
old='35f93d640a2304121131d947a465f57a951cf63f'
fix='bf5e5a89209f2dd24042cd806626f832b531de52'
for name in ['run_capture.py','run_sdk.py','bootstrap.py']:
 s=(P/name).read_text(encoding='utf-8').replace(old,fix).replace('p5-35f93d6','p5-bf5e5a8')
 if name=='bootstrap.py': s=s.replace('E:/WORK/AQRP-audits/p5-bfdcf30/src','E:/WORK/AQRP-audits/p5-35f93d6/src')
 (O/name).write_text(s,encoding='utf-8')
print('INITIALIZED',O)
