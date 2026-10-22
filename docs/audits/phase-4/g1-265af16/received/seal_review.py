"""Seal primary review evidence and verify every archive member; external-only writes."""
import hashlib, json, sys, zipfile
from datetime import datetime, timezone
from pathlib import Path
O=Path(__file__).resolve().parent; FIX='265af16353d85ce8c2d229a7517809d707498da8'
def sha(b): return hashlib.sha256(b).hexdigest()
def load(p): return json.loads((O/p).read_bytes())
def put(p,x): (O/p).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
scope=load('scope-results.json'); math=load('independent-math-results.json'); end=load('end-state.json'); verdict=load('finding-disposition.json'); env=load('execution-environment.json')
assert all(r['pass_'] for r in scope['checks']) and len(scope['checks'])==64
assert math['groups_passed']==17 and math['additional_edge_groups_passed']==9 and math['monotonicity_vector_samples']==343
assert all(r['pass_'] for r in math['groups']+math['additional_edge_groups'])
assert all(r['exit_code']==0 for r in env['commands'])
assert end['fixed_sha']==end['PR_head']==end['PR_marker']==FIX and end['review_checkout_clean'] and not end['developer_checkout_porcelain']
assert verdict['verdict']=='PLAN PASS' and not verdict['implementation_authorized'] and all(f['status']=='CLOSED_DESIGN' and not f['runtime_implementation_verified'] for f in verdict['findings'])
report=O/'GPT-Work-Phase4-G1-265af16-Recheck.md'; handoff=O/'Codex-Phase4-G1-265af16-Handoff.md'
assert FIX in report.read_text(encoding='utf-8') and FIX in handoff.read_text(encoding='utf-8')
put('REVIEW_EXECUTION.json',dict(actual_executor='GPT Work primary reviewer',review_run_id=env['run_id'],fixed_sha=FIX,core_commands=env['commands'],postcheck_argv=[sys.executable,'-I','-B',str(O/'finalize_review.py'),'C:/Users/11638/AppData/Local/AQRP/reviews/p4-plan-265af16'],postcheck_exit_code=0,postcheck_UTC=end['utc'],seal_argv=[sys.executable,'-I','-B',str(O/'seal_review.py')],tool_scope='Public GitHub API/job logs via connected GitHub; raw JSON and connector-decoded contents retained. No CI original ZIP download.',initialization_note='New-Item found pre-existing developer delivery directory; no files changed by that attempt. Existing 3 delivery originals preserved before clone/checks.'))
archive=O/'GPT-Work-P4-G1-265af16-Evidence.zip'; manifest=O/'REVIEW_EVIDENCE_MANIFEST.json'
excluded={archive.name,manifest.name,'RECEIPT.json'}
files=sorted(p for p in O.rglob('*') if p.is_file() and p.name not in excluded)
entries=[dict(path=p.relative_to(O).as_posix(),bytes=p.stat().st_size,sha256=sha(p.read_bytes())) for p in files]
put(manifest.name,dict(actual_executor='GPT Work primary reviewer',fixed_sha=FIX,verdict='PLAN PASS',scope='Restricted engineering P4 G1 plan review only',self_excluded=True,receipt_outside_zip=True,files=entries))
with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
    for p in files: z.write(p,p.relative_to(O).as_posix())
    z.write(manifest,manifest.name)
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
    assert set(z.namelist())=={e['path'] for e in entries}|{manifest.name}
    for e in entries:
        b=z.read(e['path']);assert len(b)==e['bytes'] and sha(b)==e['sha256']
    assert z.read(manifest.name)==manifest.read_bytes()
receipt=dict(actual_executor='GPT Work primary reviewer',sealed_UTC=datetime.now(timezone.utc).isoformat(),fixed_sha=FIX,previous_sha='e40ddd0009cc30664c3a0fe0b74c4a497a541d77',verdict='PLAN PASS',scope='Restricted engineering design only',findings={'P4-G1-001':'CLOSED_DESIGN','P4-G1-002':'CLOSED_DESIGN'},new_blocking_findings=0,requirements=7,MVP=4,Competition_Ready=3,scope_checks=64,independent_new_design_groups=17,independent_additional_edge_groups=9,mathematical_property_vector_samples=343,product_tests_run=0,old_20_groups='Byte-pinned unchanged; prior independent execution cited; NOT rerun',CI='SUCCESS; official API/decoded logs/parents/tree/digest text only; raw ZIP bytes/internal manifests/test counts NOT VERIFIED this round',P4_implementation_authorized=False,manifest_files=len(entries),zip_members=len(entries)+1,zip={'path':archive.name,'bytes':archive.stat().st_size,'sha256':sha(archive.read_bytes())},manifest={'path':manifest.name,'sha256':sha(manifest.read_bytes())},report_sha256=sha(report.read_bytes()),handoff_sha256=sha(handoff.read_bytes()),CRC_and_all_member_hashes='PASS',authority='No merge/tag/deploy/live trading/accounts/ACL/services or P5; formal Test, financial approval and real isolation remain NOT VERIFIED')
put('RECEIPT.json',receipt); print(json.dumps(receipt,ensure_ascii=False,indent=2))
