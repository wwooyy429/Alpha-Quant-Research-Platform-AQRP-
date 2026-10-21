from pathlib import Path

ROOT=Path(__file__).resolve().parent
prior=ROOT.parent/'work-p2-947467b/verify_p2_evidence.py'
source=prior.read_text(encoding='utf-8')
edits=[
 ("REPO=ROOT.parent/'p2-947467b'", "REPO=ROOT.parent/'p2-c70727c'"),
 ("TARGET='947467b9d094905cab0af37ec5cc53f1d187e755'", "TARGET='c70727c39182f81ee142730da9a9833a51581cd1'"),
 ("BASE='f579b2c99e762085772de6e70ba1fa98792a7add'", "BASE='fb1ba4fd51202a303115e4449ee49db09ccc071c'"),
 ("MERGE='69f64c4d189ce61821fc8726ade32dbae645d392'", "MERGE='adcf22b877e731e2b8de98aa556cf90b6ff2725a'"),
 ("env['github_run_id']=='39608527553'", "env['github_run_id']=='39632670690'"),
 ("tests=254,failures=0", "tests=392,failures=0"),
 ("latest=load(SOURCE/'docs/audits/phase-2/revised-math/FILE_MANIFEST.json')", "integration='docs/audits/phase-2/integration-011/'\n    latest=load(SOURCE/integration/'FILE_MANIFEST.json')"),
 ("b=sourcezip.read(safe(i['path']));assert", "b=sourcezip.read(integration+safe(i['path']));assert"),
 ("summary['checks']['inherited_base_data_unchanged']=True", "summary['checks']['shared_data_equals_released_main']=True\n    reviewed='8902ba00a818150bf00af8d051a3837bc79e6bfc'\n    shared=['src/aqrp/core/time.py','src/aqrp/data/pit.py','src/aqrp/data/quality.py']\n    for path in shared:\n        blob=command('reviewed-source-'+Path(path).stem,['git','--no-optional-locks','show',reviewed+':'+path],cwd=REPO)\n        assert blob==sourcezip.read(path),path\n    changed=command('source-delta-from-previous-p2',['git','--no-optional-locks','diff','--name-only','947467b9d094905cab0af37ec5cc53f1d187e755',TARGET,'--','src'],cwd=REPO).decode().splitlines()\n    assert set(changed)==set(shared)|{'src/aqrp/factors/reviewed_code.json'}\n    merge_parents=command('integration-merge-parents',['git','--no-optional-locks','show','-s','--format=%P','566f0ece4175fddb2703daab3b5b26ff0e4e245f'],cwd=REPO).decode().split()\n    assert merge_parents==['947467b9d094905cab0af37ec5cc53f1d187e755',BASE]\n    assert not command('implementation-to-target-protected-diff',['git','--no-optional-locks','diff','--name-only','566f0ece4175fddb2703daab3b5b26ff0e4e245f',TARGET,'--','src','tests','tools','.github','pyproject.toml','requirements.lock'],cwd=REPO).strip()\n    summary['checks']['controlled_integration']={'merge_parents':merge_parents,'changed_source':changed,'shared_files_equal_previously_reviewed_business':True,'factor_python_logic_unchanged':True,'implementation_to_target_protected_diff':[]}"),
 ("('original16',dict(tests=16,failures=11,errors=0,skipped=0)),('new-probe',dict(tests=4,failures=3,errors=0,skipped=0))", "('original16',dict(tests=16,failures=0,errors=0,skipped=0)),('new-probe',dict(tests=4,failures=2,errors=0,skipped=0))"),
 ("assert (ROOT/(name+'.exit.txt')).read_text().strip()=='1'\n        summary['checks'][name]={'junit':actual,'exit':1,'classification':'confirmed project failures preserved; not audit infrastructure failure'}", "expected_exit=0 if name=='original16' else 1\n        assert (ROOT/(name+'.exit.txt')).read_text().strip()==str(expected_exit)\n        summary['checks'][name]={'junit':actual,'exit':expected_exit,'classification':'original16 now PASS; unchanged P2 probes retain WORK-P2-002/003 failures'}"),
 ("summary['checks']['original16_scripts_unchanged']=old['original_unchanged_test_hashes']", "summary['checks']['original16_scripts_unchanged']=old['original_unchanged_test_hashes']\n    assert (ROOT/'test_work_p2_regressions.py').read_bytes()==(ROOT.parent/'work-p2-947467b/test_work_p2_regressions.py').read_bytes()\n    summary['checks']['original4_p2_probes_unchanged']=sha((ROOT/'test_work_p2_regressions.py').read_bytes())"),
]
for before,after in edits:
    assert source.count(before)==1,(before,source.count(before))
    source=source.replace(before,after)
(ROOT/'verify_p2_evidence.py').write_text(source,encoding='utf-8')
print('Prepared fixed-target evidence verifier; original regression scripts unchanged.')
