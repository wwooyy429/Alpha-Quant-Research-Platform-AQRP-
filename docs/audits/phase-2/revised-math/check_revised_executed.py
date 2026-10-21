import ast,csv,hashlib,json,pathlib,platform,re,subprocess,sys,uuid
from datetime import datetime,timezone
from fractions import Fraction
ROOT=pathlib.Path(r'C:\Users\11638\AppData\Local\AQRP\checkouts\phase1-57461d5d-5de2-4c78-9b4e-5fad2b5ccb29')
RUN=pathlib.Path(__file__).resolve().parent/'phase2-revised-math'
RUN.mkdir(exist_ok=True)
SOURCE=pathlib.Path(r'B:\BaiduSyncdisk\学习\投资\量化\量化交易比赛\审查\aqrp_phase2_math_verification_revised.py')
LOG=pathlib.Path(r'B:\迅雷下载\aqrp_phase2_math_verification_revised.log')
REPORT=pathlib.Path(r'B:\BaiduSyncdisk\学习\投资\量化\量化交易比赛\审查\aqrp_phase2_math_and_errata_incremental_recheck_report.md')
sha=lambda b:hashlib.sha256(b).hexdigest()
def git(*a):return subprocess.check_output(['git',*a],cwd=ROOT)
def save(n,o):(RUN/n).write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
assert git('rev-parse','HEAD').decode().strip()=='0b5107fa611af9d3a858440261b5321c83ca9fa4'
assert not git('status','--porcelain')
m=json.loads((ROOT/'docs/audits/phase-2/math-supplement/FILE_MANIFEST.json').read_bytes())
for f in m['files']:assert sha((ROOT/f['path']).read_bytes())==f['sha256']
files=[{'source':str(p),'bytes':len(p.read_bytes()),'sha256':sha(p.read_bytes())} for p in (SOURCE,LOG,REPORT)]
assert files[0]['sha256']=='a4d6ab561cf81040411a9980adc4d72dbd69b79661cebaaf395da2312baae92c'
assert files[1]['sha256']=='b211a417759654981eff08309415bcf9f0fd8b682bc9a91711d3750e2b23ffee'
assert files[2]['sha256']=='3df97ed8a3902463a8c7139cc406789b32d08ac9ec554ca38aa560d57c0868d0'
src=SOURCE.read_bytes()
tree=ast.parse(src)
imports=[ast.unparse(n) for n in ast.walk(tree) if isinstance(n,(ast.Import,ast.ImportFrom))]
assert set(imports)=={'import sys','from decimal import Decimal','from fractions import Fraction'}
assert not any(isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id in {'open','eval','exec','compile','__import__'} for n in ast.walk(tree))
copy=RUN/SOURCE.name;copy.write_bytes(src)
argv=[sys.executable,'-I','-S',str(copy)]
proc=subprocess.run(argv,cwd=RUN,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=30)
(RUN/'developer-replay.stdout.log').write_bytes(proc.stdout)
(RUN/'developer-replay.stderr.log').write_bytes(proc.stderr)
assert proc.returncode==0 and proc.stderr==b''
normal=lambda b:b.decode('utf-8-sig').replace('\r\n','\n').rstrip('\n')
given=normal(LOG.read_bytes());actual=normal(proc.stdout)
pattern=r'(\[REVISED_VERIFY\] Review SHA: 0b5107fa611af9d3a858440261b5321c83ca9fa4 \| Python: )([0-9.]+)'
assert len(re.findall(pattern,given))==1 and len(re.findall(pattern,actual))==1
body_match=re.sub(pattern,r'\1<RUNTIME_VERSION>',given)==re.sub(pattern,r'\1<RUNTIME_VERSION>',actual)
assert body_match
checks=[]
for name,q in [('mom',Fraction(121,100)-1),('rev',-(Fraction(121,100)-1)),('volume_raw_old_input',Fraction(1800,3000)),('volume_formal_old_input',Fraction(1800,3000)-1),('golden_A_volume',Fraction(200,125)-1),('golden_B_mom',Fraction(160,200)-1),('golden_B_rev',-(Fraction(160,200)-1)),('golden_B_volume',Fraction(50,50)-1)]:
    f=float(q);err=abs(Fraction.from_float(f)-q);rel=None if q==0 else err/abs(q)
    assert err<Fraction('1e-12') and (rel is None or rel<Fraction('1e-10'))
    checks.append({'name':name,'exact':str(q),'float':f,'absolute_error_exact':str(err),'absolute_error_float':float(err),'relative_error_exact':None if rel is None else str(rel),'relative_error_status':'N/A reference zero' if rel is None else 'CALCULATED'})
append_variant={'bytes':len(src+b'\n'),'sha256':sha(src+b'\n'),'matches_report_16_hex_prefix_4d71b9db4c2362e3':sha(src+b'\n').startswith('4d71b9db4c2362e3')}
# Only diagnose bytes; never alter raw supplied source.
protected=json.loads((ROOT/'docs/audits/phase-1/implementation/CORE_PRESERVATION.json').read_bytes())['files']
assert len(protected)==50 and all(sha((ROOT/f['path']).read_bytes())==f['sha256'] for f in protected)
assert not git('diff','8183b37','--','src','tests','tools','.github','pyproject.toml','requirements.lock')
assert not git('diff','f579b2c','--','docs/audits/phase-0','docs/audits/phase-1')
assert not git('diff','79c91e4','0b5107f','--','docs/BASELINE.md')
refs={x.split()[1]:x.split()[0] for x in git('ls-remote','origin','refs/heads/main','refs/tags/phase0-baseline','refs/tags/phase0-baseline^{}','refs/tags/phase1-baseline','refs/tags/phase1-baseline^{}').decode().splitlines()}
assert refs['refs/heads/main']=='f579b2c99e762085772de6e70ba1fa98792a7add'
assert refs['refs/tags/phase0-baseline']=='0b2230cd4861ca3b47fa30fc30dae9f4dc4109d0'
assert refs['refs/tags/phase1-baseline']=='1a8e47ee4be910aa7eeeefa430015e683a8aa6f5'
assert not git('ls-remote','--tags','origin','*phase2*')
sync=[p.relative_to(ROOT).as_posix() for p in ROOT.rglob('*冲突文件*') if p.is_file() and '.git' not in p.parts]
assert not sync
out={'run_id':'p2-revised-math-'+str(uuid.uuid4()),'received_at_utc':datetime.now(timezone.utc).isoformat(),'performed_by':'Codex developer; original sources identify Gemini, replay does not authenticate original execution provenance','incoming_sha':'0b5107fa611af9d3a858440261b5321c83ca9fa4','received_files':files,'manual_static_review':'Full source read, standard library arithmetic/print/assert only; no network/files/dynamic execution before isolated replay','imports':imports,'argv':argv,'cwd':str(RUN),'python':sys.version,'platform':platform.platform(),'returncode':proc.returncode,'stdout_sha256':sha(proc.stdout),'stderr_sha256':sha(proc.stderr),'supplied_log_runtime':re.findall(pattern,given)[0][1],'developer_replay_runtime':re.findall(pattern,actual)[0][1],'all_other_log_content_matches_after_only_newlines_and_one_runtime_banner_normalization':body_match,'byte_identical_log':proc.stdout==LOG.read_bytes(),'script_target_sha_declared':'0b5107fa611af9d3a858440261b5321c83ca9fa4','script_does_not_programmatically_verify_git_target':True,'volume_formula_and_security_B_derivation':'PASS OF ARITHMETIC SCOPE','independent_developer_fraction_checks':checks,'zero_relative_error_display':'Provided script prints0 but skips relative assertion for zero; interpret N/A, not computed zero','tolerance_operator_display':'Source asserts strict< but prints<=; current cases strictly inside both, no business threshold changed','contains_hash_zip_sdk_verification':False,'report_claim_script_bytes':9528,'report_claim_script_hash_prefix':'4d71b9db4c2362e3','provided_script_matches_report_size_and_prefix':False,'diagnostic_append_one_lf_not_applied':append_variant,'report_log_size_and_hash_prefix_matches':len(LOG.read_bytes())==5702 and sha(LOG.read_bytes()).startswith('b211a41775965498'),'report_twelve_errata_verdict':'ALL AGREE/CLOSED as reported; some explanations contradict actual repository facts','old_current_manifest_files_verified':len(m['files']),'protected_files_verified':len(protected),'source_tests_tools_ci_lock_golden_unchanged':True,'main_and_tags':refs,'phase2_tag_exists':False,'sync_conflicts':sync,'gemini_sdk_independent_execution':'NOT VERIFIED','zip_scope_per_report':'Evidence Reviewed Only; no new independent remote download/execution claimed','human_accepted':False,'user_accepted_limits':False,'merge_authorized':False,'tag_authorized':False,'phase3_authorized':False}
save('checks.json',out)
print(json.dumps({'files':files,'replay':proc.returncode,'body_match_except_runtime':body_match,'reported_python':out['supplied_log_runtime'],'replay_python':out['developer_replay_runtime'],'append_lf_diagnostic':append_variant,'math':'Volume, B and nonzero precision corrected'},ensure_ascii=False))

