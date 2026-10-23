from pathlib import Path
import json,hashlib,subprocess,datetime
O=Path(__file__).parent;C=Path('E:/WORK/AQRP-audits/p5-bf5e5a8/src');FIX='bf5e5a89209f2dd24042cd806626f832b531de52'
H=lambda b:hashlib.sha256(b).hexdigest()
git=lambda *a:subprocess.check_output(['git','-C',str(C),*a])
assert git('rev-parse','HEAD').decode().strip()==FIX and git('status','--porcelain')==b''
start=json.loads((O/'PR8_START.json').read_bytes());end=json.loads((O/'PR8_FINAL.json').read_bytes())
for p in [start,end]:assert p['head_sha']==FIX and p['body'].splitlines()[0]=='AQRP_FIXED_REVIEW_SHA: '+FIX and not p['merged']
refs=git('ls-remote','origin','refs/heads/main','refs/tags/*').decode();assert refs==(O/'REMOTE_REFS_START.txt').read_text(encoding='utf-8');(O/'REMOTE_REFS_FINAL.txt').write_text(refs,encoding='utf-8')
docs=['AGENTS.md','docs/PROJECT_CHARTER.md','docs/ARCHITECTURE.md','docs/INTERFACES.md','docs/REQUIREMENTS.md','docs/TRACEABILITY.md','docs/ROADMAP.md','docs/PROGRESS.md','docs/DECISIONS.md','docs/BACKTEST_CONTRACT.md','docs/audits/phase-5/CASH_BUCKETS_AND_PROJECTION.md','docs/audits/phase-5/FIFO_ATTRIBUTION.md','docs/audits/phase-5/IMPLEMENTATION_TRACEABILITY.md','docs/audits/phase-5/IMPLEMENTATION_CONTRACT.md']
bindings=[]
for p in docs:
 raw=(C/p).read_bytes();raw.decode('utf-8');bindings.append(dict(path=p,bytes=len(raw),sha256=H(raw)))
(O/'REVIEWED_GOVERNANCE_BINDINGS.json').write_text(json.dumps(bindings,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
with (O/'REVIEWED_SOURCE_CONTEXT.txt').open('w',encoding='utf-8') as out:
 for p,a,b in [('src/aqrp/backtest/ledger.py',76,142),('src/aqrp/services/backtest.py',40,71),('src/aqrp/services/backtest.py',97,160),('src/aqrp/performance/metrics.py',135,170)]:
  lines=(C/p).read_text(encoding='utf-8').splitlines();out.write(p+'\n')
  for i in range(a,min(b,len(lines))+1):out.write(str(i)+': '+lines[i-1]+'\n')
(O/'CANDIDATE_DIFF.patch').write_bytes(git('diff','35f93d640a2304121131d947a465f57a951cf63f',FIX))
report=dict(fixed_sha=FIX,previous_sha='35f93d640a2304121131d947a465f57a951cf63f',utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),head_and_description_lock_unchanged=True,source_detached_clean=True,main_old_tags_unchanged=True,tree=git('rev-parse','HEAD^{tree}').decode().strip(),CI_execution_merge=end['merge_commit_sha'],baseline='32ea5d6b75c84c07017d87377eeabd2f78207c5c',G2='BLOCKED / REQUEST CHANGES',finding003='OPEN / PARTIAL FIX',result='IDENTITY PASS; not financial/G2 pass')
(O/'FINAL_IDENTITY.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(report,ensure_ascii=False))
