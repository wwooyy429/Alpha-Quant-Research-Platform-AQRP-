"""External evidence sealing, no repository mutations. Re-read every member after ZIP creation."""
import hashlib, json, sys, zipfile
from datetime import datetime, timezone
from pathlib import Path
O=Path(__file__).resolve().parent; FIX='e40ddd0009cc30664c3a0fe0b74c4a497a541d77'
def sha(b): return hashlib.sha256(b).hexdigest()
def put(p,x): (O/p).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
developer=json.loads((O/'DEVELOPER-SEAL.json').read_bytes()); receipt_checks=[]
for e in developer['files']:
    b=(O/e['path']).read_bytes(); assert len(b)==e['bytes'] and sha(b)==e['sha256']
    receipt_checks.append(dict(path=e['path'],bytes=len(b),sha256=sha(b),matches_received_developer_seal=True))
with zipfile.ZipFile(O/'AQRP-P4-G1-e40ddd0-Developer-Plan.zip') as z:
    assert z.testzip() is None
    suffix='docs/audits/phase-4/FILE_MANIFEST.json'
    names=z.namelist(); manifest_name=next(n for n in names if n.endswith(suffix))
    prefix=manifest_name[:-len('FILE_MANIFEST.json')]; m=json.loads(z.read(manifest_name))
    for e in m['files']:
        b=z.read(prefix+e['path']); assert len(b)==e['bytes'] and sha(b)==e['sha256']
put('received-developer-package-verification.json',dict(actual_executor='GPT Work primary reviewer',fixed_sha=FIX,received_files=receipt_checks,developer_zip_CRC='PASS',developer_zip_manifest_files_verified=len(m['files']),scope='Developer plan archive only; not GitHub original Actions artifact',extra_zip_members=[n for n in names if not n.endswith('/') and n not in {prefix+e['path'] for e in m['files']} and n!=manifest_name]))
for p in ['scope-results.json','independent-math-results.json','ci-review-summary.json','end-state.json','findings.json']:
    json.loads((O/p).read_bytes())
findings=json.loads((O/'findings.json').read_bytes()); assert len(findings)==2 and all(x['status']=='OPEN' for x in findings)
report=(O/'GPT-Work-Phase4-G1-e40ddd0-Review.md').read_text(encoding='utf-8')
assert FIX in report and 'PLAN BLOCKED' in report and report.count('### P4 G1')==2
outzip=O/'GPT-Work-P4-G1-e40ddd0-Evidence.zip'; manifest=O/'REVIEW_EVIDENCE_MANIFEST.json'
exclude={outzip.name,manifest.name,'RECEIPT.json','seal.stdout.log','seal.stderr.log','seal.command.json'}
files=sorted(p for p in O.rglob('*') if p.is_file() and p.name not in exclude)
entries=[dict(path=p.relative_to(O).as_posix(),bytes=p.stat().st_size,sha256=sha(p.read_bytes())) for p in files]
put(manifest.name,dict(actual_executor='GPT Work primary reviewer',fixed_sha=FIX,scope='P4 G1 independent plan review, no product implementation verdict',self_excluded=True,receipt_outside_zip=True,files=entries))
with zipfile.ZipFile(outzip,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
    for p in files: z.write(p,p.relative_to(O).as_posix())
    z.write(manifest,manifest.name)
with zipfile.ZipFile(outzip) as z:
    assert z.testzip() is None
    assert set(z.namelist())=={e['path'] for e in entries}|{manifest.name}
    for e in entries:
        b=z.read(e['path']); assert len(b)==e['bytes'] and sha(b)==e['sha256']
    assert z.read(manifest.name)==manifest.read_bytes()
receipt=dict(actual_executor='GPT Work primary reviewer',sealed_at_UTC=datetime.now(timezone.utc).isoformat(),fixed_sha=FIX,verdict='PLAN BLOCKED',findings={'High':1,'Medium':1,'all':'OPEN'},manifest_files=len(entries),zip_members=len(entries)+1,zip=dict(path=outzip.name,bytes=outzip.stat().st_size,sha256=sha(outzip.read_bytes())),manifest=dict(path=manifest.name,sha256=sha(manifest.read_bytes())),report_sha256=sha((O/'GPT-Work-Phase4-G1-e40ddd0-Review.md').read_bytes()),handoff_sha256=sha((O/'Codex-Phase4-G1-e40ddd0-Handoff.md').read_bytes()),zip_CRC_and_all_manifest_member_hashes='PASS',raw_CI_ZIPs_NOT_VERIFIED_this_round=True,authority='No merge, tag, deployment, financial approval, P4 implementation authorization or P5')
put('RECEIPT.json',receipt); print(json.dumps(receipt,ensure_ascii=False,indent=2))
