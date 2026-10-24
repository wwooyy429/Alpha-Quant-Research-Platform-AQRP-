"""Read exact raw crash/control receipts from final evidence; no AQRP imports."""
from pathlib import Path
import json,zipfile,xml.etree.ElementTree as ET,hashlib
O=Path(__file__).parent;R=Path('E:/WORK/AQRP-runs/gpt-p6-3017a09-20261024-05b3298b-ecfc-49e7-bd8d-5827f1354391/aqrp-4353a1a2-3dae-4db1-aa5d-ff6f56ba351c');P=Path('C:/Users/11638/AppData/Local/AQRP/reviews/p6-g2-3017a09-developer-20261024T092710Z')/'payload'
expected={'R_TERMINAL_BEFORE_MAPPING':73,'COMPLETION_BEFORE_SQL':73,'BOUND':74,'P4_TERMINAL':74,'P4_PARTIAL':74,'B_TERMINAL_BEFORE_MAPPING':75}
rows=[]
def validate(read,selected,label,method):
 cases=ET.fromstring(read('junit.xml')).findall('.//testcase')
 prefixes=('test_real_process_crash_recovery_reuses_research_and_retains_receipts','test_real_process_nested_p4_crash_resume_never_constructs_second_child','test_real_process_b_terminal_before_mapping_reuses_same_run')
 controls=[x for x in cases if x.attrib['name'].startswith(prefixes)]
 assert len(controls)==6 and not any(x.find(k) is not None for x in controls for k in ('failure','error','skipped'))
 markers=[]
 for e in selected:
  if e['path'].endswith('/injected-crash-boundary.json'):
   raw=read(e['path']);v=json.loads(raw)
   assert hashlib.sha256(raw).hexdigest()==e['sha256']
   assert v['method']==method and v['exit_code']==expected[v['point']] and v['pid']>0
   markers.append(dict(path=e['path'],**v))
 assert len(markers)==6 and {x['point'] for x in markers}==set(expected)
 rows.append(dict(label=label,markers=markers,intended_exit_values=expected,actual_exit_codes_verified_by_strict_passing_pytest_assertions=True,strict_testcases=[x.attrib['name'] for x in controls]))
validate(lambda p:(R/p).read_bytes(),json.loads((R/'upload-selection.json').read_bytes())['files'],'independent-Windows','self-TerminateProcess')
for label,name,method in [('official-Windows','windows-latest','self-TerminateProcess'),('official-Ubuntu','ubuntu-24.04','os._exit')]:
 with zipfile.ZipFile(P/'official-ci'/('phase6-'+name+'-1-official-original.zip')) as z:
  ns=z.namelist();env=min([n for n in ns if n.endswith('/environment.json')],key=lambda n:len(n.split('/')));prefix=env[:-len('environment.json')]
  read=lambda p:z.read(prefix+p)
  validate(read,json.loads(read('upload-selection.json'))['files'],label,method)
historical=json.loads((O/'HISTORICAL_MACHINE_READBACK.json').read_bytes())
assert [x['archive_environment']['inspection']['markers']['platform_machine'] for x in historical]==['AMD64','x86_64','']
# Verify editor algorithm/source did not change when pool/campaign widgets were added.
C=Path('E:/WORK/AQRP-audits/p6-3017a09/src')
import subprocess,ast
old=subprocess.check_output(['git','-C',str(C),'show','eae807f957f178d19bc55dcfbd668caff5470c6e:src/aqrp/ui/app.py']).decode()
new=(C/'src/aqrp/ui/app.py').read_text(encoding='utf-8')
import textwrap
def settings_tree(text):
 marker='            st.subheader("Default configuration revisions")'
 start=text.index(marker);end=text.index('\n    except (ContractError',start)
 return ast.dump(ast.parse(textwrap.dedent(text[start:end])),include_attributes=False)
assert settings_tree(old)==settings_tree(new)
stable=['main(): complete Settings branch AST']
(O/'CRASH_LIFECYCLE_AND_IDENTITY_CONTROLS.json').write_text(json.dumps(dict(result='PASS',strict_raw_markers=rows,current_vs_retained_old_machine=['AMD64','x86_64',''],original_environment_failure_cause_not_proved=True,unchanged_editor_functions=stable,scope='Abrupt termination harness and engineering recovery; original native fault exact cause remains NOT VERIFIED'),indent=2)+'\n',encoding='utf-8')
print('Three final environments,6 strict crash points each, editor AST unchanged PASS')
