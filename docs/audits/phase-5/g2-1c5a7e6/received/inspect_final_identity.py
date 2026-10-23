from pathlib import Path
import json,hashlib,subprocess,datetime
O=Path(__file__).parent;C=Path('E:/WORK/AQRP-audits/p5-1c5a7e6/src');FIX='1c5a7e62cace7c3e66b7cc7f12fd564cb0013654'
H=lambda b:hashlib.sha256(b).hexdigest();git=lambda *a:subprocess.check_output(['git','-C',str(C),*a])
assert git('rev-parse','HEAD').decode().strip()==FIX and git('status','--porcelain')==b''
for n in ['PR8_START.json','PR8_FINAL.json']:
 p=json.loads((O/n).read_bytes());assert p['head_sha']==FIX and p['body'].splitlines()[0]=='AQRP_FIXED_REVIEW_SHA: '+FIX and not p['merged']
refs=git('ls-remote','origin','refs/heads/main','refs/tags/*').decode();assert refs==(O/'REMOTE_REFS_START.txt').read_text(encoding='utf-8');(O/'REMOTE_REFS_FINAL.txt').write_text(refs,encoding='utf-8')
bindings=[]
for p in ['AGENTS.md','docs/PROJECT_CHARTER.md','docs/ARCHITECTURE.md','docs/INTERFACES.md','docs/REQUIREMENTS.md','docs/TRACEABILITY.md','docs/ROADMAP.md','docs/PROGRESS.md','docs/DECISIONS.md','docs/BACKTEST_CONTRACT.md','docs/audits/phase-5/CASH_BUCKETS_AND_PROJECTION.md','docs/audits/phase-5/FIFO_ATTRIBUTION.md','docs/audits/phase-5/IMPLEMENTATION_TRACEABILITY.md','docs/audits/phase-5/IMPLEMENTATION_CONTRACT.md']:
 raw=(C/p).read_bytes();raw.decode('utf-8');bindings.append(dict(path=p,bytes=len(raw),sha256=H(raw)))
(O/'REVIEWED_GOVERNANCE_BINDINGS.json').write_text(json.dumps(bindings,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
with (O/'REVIEWED_SOURCE_CONTEXT.txt').open('w',encoding='utf-8') as out:
 for p,a,b in [('src/aqrp/backtest/ledger.py',78,316),('src/aqrp/backtest/transactions.py',125,154),('src/aqrp/services/backtest.py',43,168),('src/aqrp/services/backtest.py',198,232),('src/aqrp/services/backtest.py',344,381)]:
  lines=(C/p).read_text(encoding='utf-8').splitlines();out.write(p+'\n')
  for i in range(a,min(b,len(lines))+1):out.write(str(i)+': '+lines[i-1]+'\n')
(O/'CANDIDATE_DIFF.patch').write_bytes(git('diff','bf5e5a89209f2dd24042cd806626f832b531de52',FIX))
r=dict(fixed_sha=FIX,previous_sha='bf5e5a89209f2dd24042cd806626f832b531de52',utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),head_and_description_lock_unchanged=True,source_detached_clean=True,main_old_tags_unchanged=True,tree=git('rev-parse','HEAD^{tree}').decode().strip(),CI_execution_merge='db8c9776007dc2e13a0ebd0aa2e6d7045d7a301f',baseline='32ea5d6b75c84c07017d87377eeabd2f78207c5c',G2='PASS — RESTRICTED ENGINEERING SCOPE',finding003='CLOSED — FIX VERIFIED',user_phase_acceptance=False,result='IDENTITY PASS')
(O/'FINAL_IDENTITY.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(r,ensure_ascii=False))
