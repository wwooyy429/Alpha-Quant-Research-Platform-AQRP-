from pathlib import Path
O=Path(__file__).parent;P=O.parent/'p5-g2-003-recheck-bf5e5a8-independent'
old='bf5e5a89209f2dd24042cd806626f832b531de52';new='1c5a7e62cace7c3e66b7cc7f12fd564cb0013654'
for name in ['run_capture.py','bootstrap.py','run_sdk.py']:
 s=(P/name).read_text(encoding='utf-8').replace(old,new).replace('p5-bf5e5a8','p5-1c5a7e6')
 if name=='bootstrap.py':s=s.replace('E:/WORK/AQRP-audits/p5-35f93d6/src','E:/WORK/AQRP-audits/p5-bf5e5a8/src')
 (O/name).write_text(s,encoding='utf-8')
print('Initialized independent fixed-version audit')
