from pathlib import Path
import json,hashlib,subprocess,platform,sys
O=Path(__file__).parent;C=Path('E:/WORK/AQRP-audits/p6-e71f6f0/src');P=C/'docs/audits/phase-6';D=O.parent/'p6-g1-recheck-e71f6f0-20261023'
H=lambda b:hashlib.sha256(b).hexdigest()
save=lambda n,x:(O/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
manifest=json.loads((P/'FILE_MANIFEST.json').read_bytes())
rows=manifest['files'];assert len(rows)==len({e['path'] for e in rows})
for e in rows:
 b=(P/e['path']).read_bytes();assert len(b)==e['bytes'] and H(b)==e['sha256'],e['path']
tracked=subprocess.check_output(['git','-C',str(C),'ls-files','-z','docs/audits/phase-6']).decode().rstrip('\0').split('\0')
relative={p.removeprefix('docs/audits/phase-6/') for p in tracked}
assert relative=={e['path'] for e in rows}|{'FILE_MANIFEST.json'}
binding=json.loads((D/'COMMITTED_MODEL_BINDING.json').read_bytes())
assert binding['fixed_sha']=='e71f6f090b102e4abfd70a5999e495f49546a1b5'
for n,h in binding['models_and_inputs'].items():assert H((P/n).read_bytes())==h
runs=json.loads((D/'REFERENCE_RUN.json').read_bytes())
for entry in runs['commands']:
 assert entry['source_parent_commit']=='f7a1a68c5f747090f8c8a0e934f2fea859aec998'
 assert entry['source_dirty_design'] is True and entry['exit_code']==0
 for name,h in entry['source_files'].items():assert H((P/name).read_bytes())==h
assert not (C/'src/aqrp/ui').exists()
# Script/source inspection line bindings, no business imports.
docs=['TASK_COMPLETION_CONTRACT.md','NESTED_CONTEXT_CONTRACT.md','NUMERIC_REFERENCE_CONTRACT.md','TASK_AND_RECOVERY_CONTRACT.md','DEPENDENCY_AND_COMPATIBILITY_PLAN.md','TEST_AND_EVIDENCE_PLAN.md','G2_FAULT_MATRIX.md','INTERFACE_DRAFT.md','OPEN_QUESTIONS.md','reference_check.py','revision_reference.py']
with (O/'FIXED_LINE_CONTEXT.txt').open('w',encoding='utf-8') as out:
 for name in docs:
  out.write('\n===== docs/audits/phase-6/'+name+' =====\n')
  for i,line in enumerate((P/name).read_text(encoding='utf-8').splitlines(),1):out.write(str(i)+': '+line+'\n')
before=json.loads((P/'g1-f7a1a68/developer-validation/BEFORE_NUMERIC_COUNTEREXAMPLES.json').read_bytes())
save('CURRENT_MANIFEST_AND_EXECUTION_IDENTITY.json',dict(plan_manifest_members=len(rows)+1,exact_tracked_set=True,developer_model_binding=binding,actual_developer_run='Parent f7 plus dirty design; hashes bind exact current committed input/model bytes; not clean SDK or GPT Work',original_failure_record=before,passed=True))
# Capture current raw identity and scope commands via wrapper.
cmds=[('identity',['git','rev-parse','HEAD']),('status',['git','status','--porcelain=v1']),('revision-stat',['git','diff','--stat','f7a1a68c5f747090f8c8a0e934f2fea859aec998','e71f6f090b102e4abfd70a5999e495f49546a1b5']),('core-diff',['git','diff','--exit-code','59246f9fd391c1713b6bed65dd22280f4d248493','HEAD','--','src','tests','tools','.github','pyproject.toml','requirements.lock']),('remote-final',['git','ls-remote','origin','refs/heads/main','refs/tags/*'])]
for name,argv in cmds:subprocess.run([sys.executable,str(O/'run_capture.py'),name,str(C)]+argv,check=True)
save('EXECUTION_DISPOSITIONS.json',dict(reviewer_actual='GPT Work supplemental reviewer; design and byte verification only',source_count_reporting_first_attempt='All 4909 source files were compared correctly. A reviewer reporting variable was later overwritten by 29 context filenames; final script uses context_names, rerun passes with source_files4909. Initial raw log kept. Not a product failure.',design_first_attempt='Original32/new95/numeric context observations passed before extension assertion. Reviewer exhaustive replay generator omitted comparison_verified=True while expecting a positive replay. Both independent and candidate models correctly refused; generator corrected, no expected answer or candidate changed; initial script and failed log kept. Rerun passes all3456 valid-premise masks.',read_only_lookup='One inspection queried non-existent phase-6/DESIGN_DECISIONS.md; actual decision proposals are OPEN_QUESTIONS and three normative contracts. No product/source change.',new_full_SDK_run=False,UI_install_browser=False,real_SQLite_or_authority_test=False,CI='Fresh official API metadata success; no original ZIP bytes acquired in this audit',original_evidence='Original independent seal105+1 and received70 exact bytes retained and reverified'))
print(json.dumps(dict(plan_manifest=len(rows)+1,model_identity='PASS',original_failures_retained=True,core_diff='EMPTY')))

