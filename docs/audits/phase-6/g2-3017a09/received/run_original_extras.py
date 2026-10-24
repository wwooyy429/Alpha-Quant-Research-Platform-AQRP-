from pathlib import Path
import json,subprocess,sys,shutil,hashlib,xml.etree.ElementTree as ET
O=Path(__file__).parent;C=Path('E:/WORK/AQRP-audits/p6-3017a09/src')
corpus=O/'original-regressions'
for part in ['source','phase1']:
 folder=corpus/part/'tests/golden';folder.mkdir(parents=True,exist_ok=True)
 shutil.copyfile(C/'tests/golden/phase1_input.json',folder/'phase1_input.json')
 assert (folder/'phase1_input.json').read_bytes()==(C/'tests/golden/phase1_input.json').read_bytes()
bindings=[dict(path=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in corpus.rglob('phase1_input.json')]
(O/'ORIGINAL_FIXTURE_BINDINGS.json').write_text(json.dumps(bindings,indent=2)+'\n',encoding='utf-8')
scripts=[corpus/n for n in ['test_round2_regressions.py','test_work_p1_regressions.py','test_work_p2_regressions.py']]
steps=[('original20-rerun',[sys.executable,'-I','-m','pytest',*map(str,scripts),'-q','-p','no:cacheprovider','--basetemp='+str(corpus/'tmp20-rerun'),'--junitxml='+str(O/'original20-rerun.xml')]),('original-reviewer4',[sys.executable,'-I','-m','pytest',str(corpus/'test_review_regressions.py'),'-q','-p','no:cacheprovider','--basetemp='+str(corpus/'tmp4'),'--junitxml='+str(O/'original-reviewer4.xml')]),('original-math91',[sys.executable,'-I',str(O/'original-math/independent_implementation_math.py')])]
for name,args in steps:subprocess.run([sys.executable,str(O/'run_capture.py'),name,str(O)]+args,check=True)
for name,count in [('original20-rerun',20),('original-reviewer4',4)]:
 cases=ET.fromstring((O/(name+'.xml')).read_bytes()).findall('.//testcase');assert len(cases)==count
 assert not any(c.find(n) is not None for c in cases for n in ['failure','error','skipped'])
math=json.loads((O/'original-math/independent-implementation-math.json').read_bytes());assert math['passed']==91 and math['failed']==0
(O/'ORIGINAL_EXTRA_RESULTS.json').write_text(json.dumps(dict(actual_fixed_sha='3017a097b49ecdae68228ca9a417fcd03c313200',original20=20,original_reviewer4=4,independent_math=91,failed=0,scope='Original scripts/answers unchanged; fixture-relative directories restored; historical helper labels preserved; current execution captured separately'),indent=2)+'\n',encoding='utf-8')
print('Original20 + original4 + math91 PASS')

