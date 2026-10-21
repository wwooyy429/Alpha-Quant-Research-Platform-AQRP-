"""Receipt and safe standard-library replay after manual review, Codex developer evidence."""
import ast,csv,hashlib,json,pathlib,platform,subprocess,sys,uuid
from datetime import datetime,timezone
from fractions import Fraction
ROOT=pathlib.Path(r'C:\Users\11638\AppData\Local\AQRP\checkouts\phase1-57461d5d-5de2-4c78-9b4e-5fad2b5ccb29')
RUN=pathlib.Path(__file__).resolve().parent/'phase2-math-supplement'
RUN.mkdir(exist_ok=True)
SCRIPT=pathlib.Path(r'B:\BaiduSyncdisk\学习\投资\量化\量化交易比赛\审查\aqrp_phase2_math_verification.py')
LOG=pathlib.Path(r'B:\迅雷下载\aqrp_phase2_math_verification.log')
sha=lambda b:hashlib.sha256(b).hexdigest()
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT)
def save(n,o):(RUN/n).write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
assert git('rev-parse','HEAD').decode().strip()=='79c91e4bf7b4341c810705a00648283e80ab805a'
assert not git('status','--porcelain')
manifest=json.loads((ROOT/'docs/audits/phase-2/implementation-audit/FILE_MANIFEST.json').read_bytes())
for f in manifest['files']:assert sha((ROOT/f['path']).read_bytes())==f['sha256'],f['path']
src=SCRIPT.read_bytes(); supplied=LOG.read_bytes()
tree=ast.parse(src)
imports=[ast.unparse(n) for n in ast.walk(tree) if isinstance(n,(ast.Import,ast.ImportFrom))]
assert set(imports)=={'import sys','from decimal import Decimal','from fractions import Fraction'}
assert not any(isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id in {'open','eval','exec','compile','__import__'} for n in ast.walk(tree))
copy=RUN/SCRIPT.name
copy.write_bytes(src)
argv=[sys.executable,'-I','-S',str(copy)]
run=subprocess.run(argv,cwd=RUN,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=30)
(RUN/'developer-replay.stdout.log').write_bytes(run.stdout)
(RUN/'developer-replay.stderr.log').write_bytes(run.stderr)
assert run.returncode==0
assert run.stdout.replace(b'\r\n',b'\n').rstrip(b'\n')==supplied.replace(b'\r\n',b'\n').rstrip(b'\n')
# Source's "volume" example actually computes a raw ratio with different inputs.
hist=[1000,2000,3000,4000,5000]; current=1800
mean=Fraction(sum(hist),len(hist))
raw_ratio=Fraction(current)/mean
formal_same_input=raw_ratio-1
assert mean==3000 and raw_ratio==Fraction(3,5) and formal_same_input==Fraction(-2,5)
cases=json.loads((ROOT/'docs/audits/phase-2/golden_cases.json').read_bytes())['cases']
answers={}
for name in ('G-P2-A','G-P2-B'):
    c=next(c for c in cases if c['id']==name)
    p=list(map(Fraction,c['prices']));v=list(map(Fraction,c['volumes']))
    mom=p[-1]/p[0]-1; rev=-mom; volume=v[-1]/(sum(v[:-1])/len(v[:-1]))-1
    expected={k:Fraction(x) for k,x in c['expected'].items()}
    calculated={'momentum':mom,'reversal':rev,'volume':volume}
    assert calculated==expected
    answers[name]={'inputs':{'prices':c['prices'],'volumes':c['volumes']},'derived':{k:str(x) for k,x in calculated.items()}}
precision=[{'exact':s,'binary64_error':str(abs(Fraction.from_float(float(Fraction(s)))-Fraction(s)))} for s in ('21/100','-21/100','3/5')]
refs={x.split()[1]:x.split()[0] for x in git('ls-remote','origin','refs/heads/main','refs/tags/phase0-baseline','refs/tags/phase0-baseline^{}','refs/tags/phase1-baseline','refs/tags/phase1-baseline^{}').decode().splitlines()}
assert refs['refs/heads/main']=='f579b2c99e762085772de6e70ba1fa98792a7add'
assert refs['refs/tags/phase0-baseline']=='0b2230cd4861ca3b47fa30fc30dae9f4dc4109d0'
assert refs['refs/tags/phase1-baseline']=='1a8e47ee4be910aa7eeeefa430015e683a8aa6f5'
assert not git('ls-remote','--tags','origin','*phase2*')
assert not git('diff','8183b37','--','src','tests','tools','.github','pyproject.toml','requirements.lock')
assert not git('diff','f579b2c','--','docs/audits/phase-0','docs/audits/phase-1')
protected=json.loads((ROOT/'docs/audits/phase-1/implementation/CORE_PRESERVATION.json').read_bytes())['files']
assert all(sha((ROOT/f['path']).read_bytes())==f['sha256'] for f in protected)
sync=[str(p.relative_to(ROOT)) for p in ROOT.rglob('*冲突文件*') if p.is_file() and '.git' not in p.parts]
assert not sync
result={'run_id':'p2-math-supplement-'+str(uuid.uuid4()),'time_utc':datetime.now(timezone.utc).isoformat(),'performed_by':'Codex developer; supplied file header attributes original work to Gemini, historical execution provenance not authenticated by replay','starting_commit':'79c91e4bf7b4341c810705a00648283e80ab805a','received':[{'path':str(p),'bytes':len(b),'sha256':sha(b)} for p,b in [(SCRIPT,src),(LOG,supplied)]],'manual_static_review':'Read entire source; standard-library-only arithmetic/print/assert, no network/file access or dynamic execution, imports checked before isolated replay','imports':imports,'argv':argv,'cwd':str(RUN),'python':sys.version,'platform':platform.platform(),'returncode':run.returncode,'stdout_sha256':sha(run.stdout),'stderr_sha256':sha(run.stderr),'supplied_log_matches_replay_after_only_line_endings_and_final_newlines_normalization':True,'replay_result':'PASS AS WRITTEN; not PASS of AQRP formal factor verification','source_self_identified_scope':'Phase 2 Plan Pre-Review Mathematical Verification Script','source_binds_fixed_commit':False,'source_verifies_hashes_or_zips_or_sdk':False,'source_security_b_computes_from_inputs':False,'source_volume_example':{'historical':hist,'current':current,'mean':str(mean),'script_raw_ratio':str(raw_ratio),'formal_factor_same_inputs':str(formal_same_input),'formal_factor_same_inputs_float':float(formal_same_input),'formal_factor_disagreement':True},'developer_formal_golden_checks':answers,'exact_float_precision':precision,'earlier_current_manifest_files_verified':len(manifest['files']),'phase0_protected_files_verified':len(protected),'source_tests_ci_lock_unchanged':True,'old_audit_files_unchanged':True,'remote_refs':refs,'phase2_tag_exists':False,'sync_conflicts':sync,'gemini_full_sdk_execution':'NOT VERIFIED','new_implementation_math_and_hash_evidence_matched':False,'human_accepted':False,'merge_authorized':False,'tag_authorized':False,'phase3_authorized':False}
save('checks.json',result)
print(json.dumps({'script_sha256':sha(src),'log_sha256':sha(supplied),'replay_returncode':run.returncode,'supplied_log_matches':True,'script_volume_raw_ratio':str(raw_ratio),'formal_volume_same_input':str(formal_same_input),'golden_A':answers['G-P2-A']['derived'],'original_manifest_files_verified':len(manifest['files'])},ensure_ascii=False))

