from pathlib import Path
import json,zipfile,xml.etree.ElementTree as ET
O=Path(__file__).parent;C=Path('E:/WORK/AQRP-audits/p6-f7a1a68/src');P=C/'docs/audits/phase-6'
seal=json.loads((P/'PHASE5_SEALED_EVIDENCE.json').read_bytes())
with zipfile.ZipFile(seal['archive']) as z:
 m=json.loads(z.read('EVIDENCE_MANIFEST.json'));assert len(z.namelist())==len(set(z.namelist()))==1125
 paths={e['path'] for e in m['files']};assert len(paths)==1124 and set(z.namelist())==paths|{'EVIDENCE_MANIFEST.json'}
extras=C/'docs/audits/phase-5/publication/extras';counts=[]
for name,n in [('original20.xml',20),('original-reviewer4.xml',4)]:
 x=ET.fromstring((extras/name).read_bytes());assert len(x.findall('.//testcase'))==n and all(not x.findall('.//'+k) for k in ['failure','error','skipped']);counts.append(dict(path=name,tests=n))
math=json.loads((extras/'original-math/independent-implementation-math.json').read_bytes());assert math['passed']==91 and math['failed']==0
out=dict(scope='Developer release regression records verified; not a new reviewer execution of20/4/91',release_exact_members_unique=True,regressions=counts,math_passed=91,math_failed=0,result='PASS')
(O/'RELEASE_EXTRAS_VERIFICATION.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8');print(json.dumps(out))
