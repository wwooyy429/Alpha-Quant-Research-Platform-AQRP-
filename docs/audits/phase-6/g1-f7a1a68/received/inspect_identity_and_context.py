from pathlib import Path
import json,hashlib,subprocess
O=Path(__file__).parent;C=Path('E:/WORK/AQRP-audits/p6-f7a1a68/src');P=C/'docs/audits/phase-6';FIX='f7a1a68c5f747090f8c8a0e934f2fea859aec998';git=lambda *a:subprocess.check_output(['git','-C',str(C),*a])
out=[]
for n in ['TASK_AND_RECOVERY_CONTRACT.md','DEPENDENCY_AND_COMPATIBILITY_PLAN.md','INTERFACE_DRAFT.md','MATH_AND_COMPARISON_CONTRACT.md','TEST_AND_EVIDENCE_PLAN.md','reference_check.py']:
 lines=(P/n).read_text(encoding='utf-8').splitlines();out.append('docs/audits/phase-6/'+n)
 out.extend(str(i)+': '+s for i,s in enumerate(lines,1))
for n,a,b in [('src/aqrp/backtest/engine.py',320,338),('src/aqrp/backtest/provider.py',191,218),('src/aqrp/services/backtest.py',186,215),('src/aqrp/experiments/ledger.py',109,140)]:
 lines=(C/n).read_text(encoding='utf-8').splitlines();out.append(n);out.extend(str(i)+': '+lines[i-1] for i in range(a,b+1))
(O/'REVIEWED_SOURCE_CONTEXT.txt').write_text('\n'.join(out)+'\n',encoding='utf-8')
docs=['AGENTS.md','docs/PROJECT_CHARTER.md','docs/ARCHITECTURE.md','docs/INTERFACES.md','docs/REQUIREMENTS.md','docs/TRACEABILITY.md','docs/ROADMAP.md','docs/PROGRESS.md','docs/DECISIONS.md']+[str(p.relative_to(C)).replace('\\','/') for p in P.glob('*.md')]
bindings=[]
for n in docs:
 raw=(C/n).read_bytes();raw.decode('utf-8');bindings.append(dict(path=n,bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest()))
(O/'REVIEWED_DOCUMENT_BINDINGS.json').write_text(json.dumps(bindings,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(O/'CANDIDATE_DIFF.patch').write_bytes(git('diff','59246f9fd391c1713b6bed65dd22280f4d248493',FIX))
assert git('rev-parse','HEAD').decode().strip()==FIX and git('status','--porcelain')==b''
print('Numbered design/current-core contexts captured; fixed source clean')
