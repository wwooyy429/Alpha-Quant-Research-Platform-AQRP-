import json,hashlib,zipfile,subprocess
from pathlib import Path
from datetime import date
from xml.etree import ElementTree as ET
import sys
R=Path(__file__).resolve().parent
sys.path.insert(0,str(R/'phase1/src'))
from aqrp.core.contracts import QuerySpec,SnapshotRef
from aqrp.data.snapshot import verify_snapshot
from aqrp.data.query import query
S=R/'phase1';base=S/'docs/audits/phase-1/publication/sdk'
meta=json.loads((S/'docs/audits/phase-1/publication/MERGE_VERIFICATION.json').read_bytes())
checks=[]
for item in meta['archive']['root_files']:
    if item['repository_archived']:
        p=base/item['archive_name'];actual=hashlib.sha256(p.read_bytes()).hexdigest();assert actual==item['sha256'];checks.append(dict(name=item['path'],archive_name=item['archive_name'],match=True))
wheel=next((base/'wheel').glob('*.whl'));h=hashlib.sha256(wheel.read_bytes()).hexdigest();assert h==meta['merged_main_local_full_sdk']['wheel_sha256']
code=[]
with zipfile.ZipFile(wheel) as z:
    for p in (S/'src').rglob('*.py'):
        n=p.relative_to(S/'src').as_posix();assert z.read(n)==p.read_bytes();code.append(n)
suites=list(ET.fromstring((base/'junit.xml').read_bytes()).iter('testsuite'))
junit={k:sum(int(x.attrib.get(k,0)) for x in suites) for k in ['tests','failures','errors','skipped']};assert junit==dict(tests=102,failures=0,errors=0,skipped=0)
config=json.loads((base/'smoke-config.json').read_bytes());ref=SnapshotRef(base/'dataset',config['snapshot_id'],config['manifest_hash']);manifest,tables=verify_snapshot(ref)
spec=QuerySpec(tuple(config['security_ids']),config['market_id'],config['calendar_id'],tuple(date.fromisoformat(x) for x in config['session_range']))
rows=query(spec,config['as_of'],ref).table.to_pylist()
from aqrp.core.canonical import canonical
assert canonical(rows)==(base/'smoke-result.json').read_bytes()
r={'audit':'GPT Work 补充审核','scope':'Read and verify developer release evidence, not rerun developer original full SDK','target_sha':'f579b2c99e762085772de6e70ba1fa98792a7add','original_execution_commit':meta['merge_sha'],'original_execution_actor':meta['performed_by'],'original_junit':junit,'root_file_hashes':checks,'wheel_sha256':h,'wheel_python_modules_match_release_source':code,'sdk_snapshot_verify':'PASS','sdk_relocated_query_replay':'PASS','table_count':len(tables)}
(R/'publication-evidence-check.json').write_text(json.dumps(r,indent=2,ensure_ascii=False),encoding='utf-8')
print('Publication root files matched',len(checks),'wheel matched',h,'module count',len(code),'junit original',junit,'8-table verify/query replay PASS')
