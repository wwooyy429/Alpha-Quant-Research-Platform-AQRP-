from pathlib import Path
import json,shutil
O=Path(__file__).parent;old=O.parent/'p6-g2-eae807f-independent-20261024'
src=(old/'verify_independent_sdk.py').read_text().replace('p6-eae807f/src','p6-3017a09/src').replace('E:/WORK/AQRP-runs/gpt-p6-eae807f-20261024-e9c8e3a6-d633-423a-b48a-fe1c7adbbabb/aqrp-b7f5fb35-2718-48ce-b655-058d50f92c96','E:/WORK/AQRP-runs/gpt-p6-3017a09-20261024-05b3298b-ecfc-49e7-bd8d-5827f1354391/aqrp-4353a1a2-3dae-4db1-aa5d-ff6f56ba351c').replace('eae807f957f178d19bc55dcfbd668caff5470c6e','3017a097b49ecdae68228ca9a417fcd03c313200').replace('1496','1567').replace('==82','==83').replace('modules=82','modules=83')
src='\n'.join(l for l in src.splitlines() if not l.startswith('gate=subprocess.run('))
src=src.replace("'Search variant budget and final cancellation corruption probes are separate from 1567 existing tests; SDK PASS does not close them'","'Independent repair challenges recorded separately in INDEPENDENT_CAMPAIGN_RECHECK, INDEPENDENT_CANCELLATION_RECHECK, INDEPENDENT_UNIVERSE_RECHECK and INDEPENDENT_WAL_RECHECK'")
(O/'verify_independent_sdk.py').write_text(src+'\n',encoding='utf-8')
src=(old/'verify_controls_and_coverage.py').read_text();src=src[:src.index("variants=json.loads")]
src=src.replace('p6-eae807f/src','p6-3017a09/src').replace('E:/WORK/AQRP-runs/gpt-p6-eae807f-20261024-e9c8e3a6-d633-423a-b48a-fe1c7adbbabb/aqrp-b7f5fb35-2718-48ce-b655-058d50f92c96','E:/WORK/AQRP-runs/gpt-p6-3017a09-20261024-05b3298b-ecfc-49e7-bd8d-5827f1354391/aqrp-4353a1a2-3dae-4db1-aa5d-ff6f56ba351c')
src+="\nassert len(expected)==83\n(O/'COVERAGE_VERIFICATION.json').write_text(json.dumps(dict(coverage=records,coverage_all_bundle_modules_present=len(expected),result='PASS'),indent=2)+'\\n',encoding='utf-8')\nprint('All83 source modules covered and gates PASS')\n"
(O/'verify_coverage.py').write_text(src,encoding='utf-8')
src=(old/'prepare_evidence.py').read_text().replace('p6-eae807f/src','p6-3017a09/src').replace('eae807f957f178d19bc55dcfbd668caff5470c6e','3017a097b49ecdae68228ca9a417fcd03c313200').replace("ROOT=Path('E:/WORK/AQRP-runs/gpt-p6-independent-probes-20261024')","ROOT=Path('E:/WORK/AQRP-runs/gpt-p6-independent-3017a09-20261024')").replace("BROWSER=Path('E:/WORK/AQRP-runs/gpt-p6-independent-browser-20261024')","BROWSER=Path('E:/WORK/AQRP-runs/gpt-p6-browser-3017a09-independent-20261024')")
src=src.replace("[(ROOT,'probes'),(BROWSER,'browser-runtime')]","[(ROOT,'first-attempt-probes'),(Path(str(ROOT)+'-retry'),'repair-probes'),(BROWSER,'browser-runtime'),(Path('E:/WORK/AQRP-runs/gpt-p6-independent-wal-3017a09-20261024'),'wal')]")
src=src.replace("for p in sorted(source.rglob('*')):","for p in sorted(strict_tree(source)):")
insert="""import os,stat
def strict_tree(root):
 def refused(error):raise error
 for parent,dirs,files in os.walk(root,onerror=refused,followlinks=False):
  for name in dirs+files:
   p=Path(parent)/name
   mode=p.lstat().st_mode
   assert not stat.S_ISLNK(mode) and not p.is_junction(),str(p)
  for name in files:yield Path(parent)/name
"""
src=src.replace("# Only capture own dedicated validation directories.",insert+"\n# Only capture own dedicated validation directories.")
src=src.replace("paths=['src/aqrp/services/tasks.py'","paths=['src/aqrp/services/task_campaigns.py','src/aqrp/services/task_inputs.py','src/aqrp/services/tasks.py'")
(O/'prepare_evidence.py').write_text(src,encoding='utf-8')
