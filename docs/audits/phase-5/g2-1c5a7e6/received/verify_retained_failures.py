from pathlib import Path
import json,zipfile,hashlib,re
O=Path(__file__).parent;D=O.parent/'p5-g2-backing-recheck-1c5a7e6';H=D/'developer-history'
checks=[]
for label,failed,passed in [('development-001',7,3),('development-002',4,6),('development-006',1,300)]:
 raw=(H/(label+'.stdout.log')).read_text(encoding='utf-8');assert re.search(str(failed)+r' failed.*'+str(passed)+r' passed',raw)
 cfg=json.loads((H/(label+'.command.json')).read_bytes());checks.append(dict(label=label,failed=failed,passed=passed,command=cfg))
anchor=(H/'anchor-before-captured.stdout.log').read_text(encoding='utf-8');assert '4 failed' in anchor
receipt=json.loads((D/'intermediate-d7b7eaa/OFFICIAL_DOWNLOAD_RECEIPT.json').read_bytes());old=[]
for e in receipt['original_artifact_receipts']:
 p=Path(e['original_zip']);assert p.stat().st_size==e['bytes']
 with p.open('rb') as f:sha=hashlib.file_digest(f,'sha256').hexdigest()
 assert sha==e['sha256']==e['official_digest'].removeprefix('sha256:')
 with zipfile.ZipFile(p) as z:assert z.testzip() is None
 old.append(dict(path=str(p),bytes=p.stat().st_size,sha256=sha,CRC='PASS',identity_scope='Against preserved old official receipt; not a fresh API query or new execution'))
env=json.loads((D/'intermediate-d7b7eaa/environment.json').read_bytes());assert env['complete']
report=dict(result='PASS',scope='Original developer successes and failures remain historical; no relabeling or claim of independent rerun of old candidate',original_failures=checks,additional_anchor_failures_preserved=4,old_CI_original_archives=old,old_SDK_complete=True,old_SDK_used_as_current=False)
(O/'RETAINED_FAILURE_VERIFICATION.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print('Original 7/3,4/6,1/300 and four anchor failures preserved; old original ZIP/receipt hashes/CRC verified')
