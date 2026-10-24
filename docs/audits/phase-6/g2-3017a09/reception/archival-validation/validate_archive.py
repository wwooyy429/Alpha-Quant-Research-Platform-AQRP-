"""Administrative file/identity verification only; no product tests or G2 verdict."""
from pathlib import Path
from datetime import UTC,datetime
import hashlib,json,subprocess
O=Path(__file__).resolve().parent
R=Path(r'C:/Users/11638/AppData/Local/AQRP/checkouts/phase1-57461d5d-5de2-4c78-9b4e-5fad2b5ccb29')
C='3017a097b49ecdae68228ca9a417fcd03c313200';A=R/'docs/audits/phase-6/g2-3017a09'
load=lambda p:json.loads(p.read_bytes())
sha=lambda b:hashlib.sha256(b).hexdigest()
def git(*a):return subprocess.check_output(['git',*a],cwd=R)
index=load(A/'EVIDENCE_INDEX.json');receipt=load(A/'received/RECEIPT.json');findings=load(A/'received/FINDINGS.json')
for v in index['received_files_copied_verbatim']+index['original_externally_sealed_receipt_and_logs']:
 b=(A/'received'/v['path']).read_bytes();assert len(b)==v['bytes'] and sha(b)==v['sha256']
assert sha((A/'received/EVIDENCE_MANIFEST.json').read_bytes())==receipt['manifest_sha256']
assert (A/'reviewed/IMPLEMENTATION_IDENTITY.json').read_bytes()==git('show',C+':docs/audits/phase-6/IMPLEMENTATION_IDENTITY.json')
assert (A/'reviewed/STATUS_AT_REVIEW.json').read_bytes()==git('show',C+':docs/audits/phase-6/STATUS.json')
allowed={'AGENTS.md','docs/PROGRESS.md','docs/TRACEABILITY.md','docs/DECISIONS.md','docs/ROADMAP.md','docs/CHANGELOG.md','docs/audits/phase-6/DEVELOPER_FINDINGS.md','docs/audits/phase-6/IMPLEMENTATION_REVIEW_PACKAGE.md','docs/audits/phase-6/IMPLEMENTATION_TRACEABILITY.md','docs/audits/phase-6/STATUS.json','docs/audits/phase-6/IMPLEMENTATION_IDENTITY.json'}
originals=git('ls-tree','-r','-z','--name-only',C).decode('utf-8').strip('\x00').split('\x00');changed=[];unchanged=0
for n in originals:
 raw=git('show',C+':'+n)
 if (R/n).read_bytes()!=raw:assert n in allowed,n;changed.append(n)
 else:unchanged+=1
assert set(changed)==allowed
new=[x for x in git('ls-files','--others','--exclude-standard','-z').decode('utf-8').strip('\x00').split('\x00') if x]
assert new and all(n.startswith('docs/audits/phase-6/g2-3017a09/') for n in new)
old=load(A/'reviewed/IMPLEMENTATION_IDENTITY.json');current=load(R/'docs/audits/phase-6/IMPLEMENTATION_IDENTITY.json')
assert current['preserved_files']==old['preserved_files'] and current['bundle_manifest']==old['bundle_manifest']
assert current['bundle_sha256']==old['bundle_sha256'] and current['core_lock_sha256']==old['core_lock_sha256']
for v in current['preserved_files']+current['current_files']:
 b=(R/v['path']).read_bytes();assert sha(b)==v['sha256'] and len(b)==v['bytes'],v['path']
for before,after in zip(old['current_files'],current['current_files'],strict=True):
 if before!=after:assert before['path']==after['path'] and before['path'] in allowed and before['path']!='docs/audits/phase-6/IMPLEMENTATION_IDENTITY.json'
state=load(R/'docs/audits/phase-6/STATUS.json');d=load(A/'REVIEW_DISPOSITION.json')
assert state['requirements']==8 and state['tiers']=={'MVP':5,'Competition Ready':3}
assert state['last_independent_reviewed_sha']==d['fixed_review_sha']==receipt['fixed_sha']==C
assert state['new_blocking_technical_findings']==0 and findings['new_open_findings']==[]
assert not any(state[k] for k in ('human_phase_acceptance','released','main_merge_tag_authorized','P7_authorized'))
assert not any(d[k] for k in ('user_phase_acceptance','released','main_merge_tag_authorized','P7_authorized'))
for v in (state,d):
 assert v['WI-R2-001']==v['WI-R2-002']=='DEFERRED / NOT VERIFIED' and v['financial_approval']=='NONE'
for k,v in receipt['findings'].items():assert state['findings'][k]==v
report=load(O/'receipt-check/VERIFICATION.json');assert report['result']=='PASS' and report['not_an_independent_G2_audit']
result={'scope':'Administrative original-byte archive, diff and metadata verification; no business test/G2 reexecution','utc':datetime.now(UTC).isoformat(),'fixed_review_sha':C,'archive_commit':git('rev-parse','HEAD').decode().strip(),'old_fixed_files':len(originals),'old_files_byte_identical':unchanged,'changed_old_document_metadata_files':changed,'new_archive_files':len(new),'received_manifest_files_byte_identical':len(index['received_files_copied_verbatim']),'external_ZIP_kept_verbatim':report['archive'],'protected_files_verified':len(current['preserved_files']),'business_bundle_code_tests_tools_workflow_locks_answers_unchanged':True,'original_reviewed_identity_preserved':True,'document_identity_rows_refreshed_only':10,'original_received_scripts_executed':False,'human_acceptance':False,'released':False,'P7':False,'result':'PASS'}
(O/'ARCHIVAL_VALIDATION.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8');print(json.dumps({k:result[k] for k in ('fixed_review_sha','old_fixed_files','old_files_byte_identical','new_archive_files','received_manifest_files_byte_identical','protected_files_verified','result')}))
