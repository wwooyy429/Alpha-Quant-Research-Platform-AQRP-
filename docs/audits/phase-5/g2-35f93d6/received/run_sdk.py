import os,pathlib,subprocess,sys,json
C=pathlib.Path('E:/WORK/AQRP-audits/p5-35f93d6/src');R=pathlib.Path('E:/WORK/AQRP-runs/gpt-p5-35f93d6-20261023')
assert not R.exists();R.mkdir()
os.environ['AQRP_RUN_ROOT']=str(R);os.environ['PYTHONUTF8']='1'
print(json.dumps({'executor':'GPT Work supplemental reviewer','argv':[sys.executable,'-B','-X','utf8',str(C/'tools/ci.py')],'run_root':str(R)}),flush=True)
subprocess.run([sys.executable,'-B','-X','utf8',str(C/'tools/ci.py')],cwd=C,check=True)
