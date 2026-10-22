from pathlib import Path
from datetime import datetime,UTC
import hashlib,json,os,subprocess
root=Path(r'C:\Users\11638\AppData\Local\AQRP\checkouts\phase1-57461d5d-5de2-4c78-9b4e-5fad2b5ccb29')
run=Path(r'C:\Users\11638\AppData\Local\AQRP\runs\p3-g2-repair-20261022')
review=Path(r'C:\Users\11638\AppData\Local\AQRP\reviews\work-p3-implementation-5a5e093')
sdk=run/'clean-sdk/aqrp-991faaf3-2e20-471d-a576-d1b64dbe3eaa'
py=sdk/'venv/Scripts/python.exe'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
out=run/'extras';out.mkdir(exist_ok=True)
head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=root).decode().strip()
commands=[]
def command(name,args):
    start=datetime.now(UTC).isoformat()
    with (out/(name+'.log')).open('wb') as f:
        result=subprocess.run([str(a) for a in args],cwd=out,stdout=f,stderr=subprocess.STDOUT)
    r={'actual_executor':'Codex developer','code_commit':head,'cwd':str(out),'argv':[str(a) for a in args],'started_at_utc':start,'finished_at_utc':datetime.now(UTC).isoformat(),'exit_code':result.returncode}
    (out/(name+'-command.json')).write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8',newline='\n');commands.append(r)
    assert result.returncode==0,name
probes=[review/'original-probes'/n for n in ('test_round2_regressions.py','test_work_p1_regressions.py','test_work_p2_regressions.py')]
command('original20',[py,'-I','-m','pytest',*probes,'-q','-p','no:cacheprovider','--junitxml='+str(out/'original20.xml')])
command('original-reviewer4',[py,'-I','-m','pytest',review/'test_review_regressions.py','-q','-p','no:cacheprovider','--junitxml='+str(out/'original-reviewer4.xml')])
math=out/'original-math';math.mkdir(exist_ok=True)
source=review/'independent_implementation_math.py';copy=math/source.name;copy.write_bytes(source.read_bytes())
command('original-math91',[py,'-I',copy])
raw=json.loads((math/'independent-implementation-math.json').read_bytes())
assert raw['passed']==91 and raw['failed']==0
result={'actual_executor':'Codex developer re-executing reviewer-authored exact script; not new independent GPT Work review','actual_code_commit':head,'script_origin':str(source),'script_sha256':sha(source),'copied_script_byte_identical':sha(copy)==sha(source),'embedded_metadata_scope':'Original script hardcodes GPT Work executor/old SHA; those strings in raw stdout/result are retained as source labels and do not describe this re-execution. This receipt records actual executor and commit. No algorithm/expected answer was changed.','math_checks_passed':91,'math_checks_failed':0,'original_probe_script_hashes':{p.name:sha(p) for p in probes},'reviewer_regression_script_sha256':sha(review/'test_review_regressions.py'),'commands':commands,'independent_recheck':'PENDING','formal_test_or_financial_approval':False}
(out/'EXTRA_VERIFICATION.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
print(json.dumps({'executor':'Codex developer','code_commit':head,'original20':'PASS','reviewer4':'PASS','original_math':raw['passed']}))
