import concurrent.futures,json,subprocess,sys
from pathlib import Path
from datetime import datetime,UTC
OUT=Path(__file__).parent
tasks=[('SDK_VERIFICATION',str(OUT/'g2-sdk/aqrp-01845d11-b0f7-4778-b5c8-e9a1723d6e1d'),None,None),('WINDOWS_RAW_VERIFICATION',str(OUT/'ci-b3/P4-b3be624-Windows-original.zip'),'4f4c9428ff477194ca689ce04de614f7974b843b1cd7aa71a3d01f393e330ca9',95677477),('UBUNTU_RAW_VERIFICATION',str(OUT/'ci-b3/P4-b3be624-Ubuntu-original.zip'),'d9e3b20bc8a76d4e0a7b61a79f37e58b38712cb070774ae9a16de34807487b4a',136949476)]
def run(t):
    name,path,digest,size=t
    args=[sys.executable,str(OUT/'verify_p4_sdk.py'),path,'--head','b3be62439d8d0877478b7105d68863fcb2a108a0','--tests','799','--output',str(OUT/(name+'.json'))]
    if digest:args+=['--sha',digest,'--size',str(size)]
    start=datetime.now(UTC).isoformat()
    with (OUT/(name+'.log')).open('wb') as f:cp=subprocess.run(args,stdout=f,stderr=subprocess.STDOUT)
    receipt={'actual_executor':'Codex developer','scope':'Byte/contract known-answer verification, not independent GPT Work audit','argv':args,'started_at_UTC':start,'finished_at_UTC':datetime.now(UTC).isoformat(),'exit_code':cp.returncode}
    (OUT/(name+'-command.json')).write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8',newline='\n')
    return {'name':name,'exit':cp.returncode}
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:results=list(pool.map(run,tasks))
print(json.dumps(results,indent=2));assert all(r['exit']==0 for r in results)
