from pathlib import Path

ROOT=Path(__file__).resolve().parent
source=(ROOT.parent/'work-p2-c70727c/verify_p2_evidence.py').read_text(encoding='utf-8')
edits=[
 ("REPO=ROOT.parent/'p2-c70727c'", "REPO=ROOT.parent/'p2-c836295'"),
 ("TARGET='c70727c39182f81ee142730da9a9833a51581cd1'", "TARGET='c8362953f555606795b6804cdfe28ff690c2364d'"),
 ("MERGE='adcf22b877e731e2b8de98aa556cf90b6ff2725a'", "MERGE='d1feaae218b25741e57fdfa024c0072f87f32e67'"),
 ("env['github_run_id']=='39632670690'", "env['github_run_id']=='39637043080'"),
 ("tests=392,failures=0", "tests=417,failures=0"),
 ("integration='docs/audits/phase-2/integration-011/'", "integration='docs/audits/phase-2/lineage-fix/'"),
 ("assert set(changed)==set(shared)|{'src/aqrp/factors/reviewed_code.json'}", "assert set(changed)==set(shared)|{'src/aqrp/factors/reviewed_code.json','src/aqrp/factors/contracts.py','src/aqrp/factors/engine.py'}"),
 ("'diff','--name-only','566f0ece4175fddb2703daab3b5b26ff0e4e245f',TARGET", "'diff','--name-only','708b83be1dd597395b41f2ff6e10702749175bbf',TARGET"),
 ("'factor_python_logic_unchanged':True", "'factor_formulas_and_input_unchanged':True"),
 ("('new-probe',dict(tests=4,failures=2,errors=0,skipped=0))", "('new-probe',dict(tests=4,failures=0,errors=0,skipped=0))"),
 ("expected_exit=0 if name=='original16' else 1", "expected_exit=0"),
 ("'classification':'original16 now PASS; unchanged P2 probes retain WORK-P2-002/003 failures'", "'classification':'all original16 and unchanged original4 probes PASS on newly installed fixed target'"),
 ("summary['status']='EVIDENCE VERIFIED; PROJECT REVIEW BLOCKING'", "summary['status']='EVIDENCE VERIFIED; NO BLOCKING FINDING IN REVIEWED SCOPE'"),
 ("summary['checks']['original4_p2_probes_unchanged']=sha((ROOT/'test_work_p2_regressions.py').read_bytes())", "summary['checks']['original4_p2_probes_unchanged']=sha((ROOT/'test_work_p2_regressions.py').read_bytes())\n    prior=ROOT.parent/'work-p2-c70727c'\n    original_manifest=load(prior/'REVIEW_EVIDENCE_MANIFEST.json')\n    originals={i['path']:i for i in original_manifest['files']}\n    receipt=load(SOURCE/integration/'RECEIPT_INDEX.json')\n    assert len(originals)==receipt['original_entries_hash_verified']==248\n    mapped={i['path'] for i in receipt['files']}\n    omitted={i['path'] for i in receipt['omitted_files']}\n    assert len(mapped)==245 and len(omitted)==3 and not mapped&omitted and mapped|omitted==set(originals)\n    for i in receipt['files']+receipt['omitted_files']:\n        old=(prior/safe(i['path'])).read_bytes()\n        expected=originals[i['path']]\n        assert sha(old)==i['sha256']==expected['sha256'] and len(old)==i['bytes']==expected['bytes']\n        if i['path'] in mapped:\n            assert (SOURCE/integration/safe(i['archive_path'])).read_bytes()==old\n    assert (SOURCE/integration/'received/REVIEW_EVIDENCE_MANIFEST.json').read_bytes()==(prior/'REVIEW_EVIDENCE_MANIFEST.json').read_bytes()\n    summary['checks']['received_prior_evidence']={'source_entries_verified':248,'copies_matching_original_bytes':245,'explicit_verified_omissions':3,'original_manifest_unchanged':True}\n    delta=command('repair-source-delta',['git','--no-optional-locks','diff','--name-only','c70727c39182f81ee142730da9a9833a51581cd1',TARGET,'--','src'],cwd=REPO).decode().splitlines()\n    assert set(delta)=={'src/aqrp/factors/contracts.py','src/aqrp/factors/engine.py','src/aqrp/factors/reviewed_code.json'}\n    summary['checks']['repair_scope']={'changed_source':delta,'candidate_version':'0.2.0','shared_P1_source_preserved':True}"),
]
for before,after in edits:
    assert source.count(before)==1,(before,source.count(before))
    source=source.replace(before,after)
(ROOT/'verify_p2_evidence.py').write_text(source,encoding='utf-8')
query=(ROOT.parent/'work-p2-c70727c/verify_query_identity.py').read_text(encoding='utf-8')
assert query.count('c70727c39182f81ee142730da9a9833a51581cd1')==1
(ROOT/'verify_query_identity.py').write_text(query.replace('c70727c39182f81ee142730da9a9833a51581cd1','c8362953f555606795b6804cdfe28ff690c2364d'),encoding='utf-8')
print('Prepared fixed-target verification and exact original-evidence receipt checks.')
