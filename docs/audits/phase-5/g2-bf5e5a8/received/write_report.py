from pathlib import Path
import json,datetime
O=Path(__file__).parent;FIX='bf5e5a89209f2dd24042cd806626f832b531de52'
J=lambda name:json.loads((O/name).read_bytes())
sdk=J('INDEPENDENT_SDK_VERIFICATION.json');ci=J('OFFICIAL_CI_VERIFICATION.json');scope=J('SCOPE_VERIFICATION.json');pres=J('ORIGINAL_AUDIT_PRESERVATION.json');probe=J('SETTLED_SHORT_BACKING_PROBE.json');cash=J('INDEPENDENT_CASH_STRUCTURE_CONTROLS.json');raw=J('RAW_FINANCIAL_RECONSTRUCTION.json');env=J('ENVIRONMENT.json')
assert sdk['tests']==1116 and sdk['result']=='PASS' and all(x['result']=='PASS' for x in ci)
assert probe['result']=='REPRODUCED_MISMATCH' and [r['result'] for r in probe['records']]==['PASS','REPRODUCED_MISMATCH','REPRODUCED_MISMATCH']
assert cash['PASS']==40 and cash['MISMATCH']==1 and raw['exact_comparisons']==7864
finding=dict(id='WORK-P5-G2-003',severity='High',status='OPEN / PARTIAL FIX',fixed_sha=FIX,prior_sha='35f93d640a2304121131d947a465f57a951cf63f',title='已交收SHORT所得仍可由两个相互自证的可变lot字段错误认证，异常/取消公开多1现金',locations=[dict(path='src/aqrp/backtest/ledger.py',start=123,end=128),dict(path='src/aqrp/services/backtest.py',start=100,end=103)],basis=['CASH_BUCKETS_AND_PROJECTION.md: S_set is original FIFO gross short proceeds backed by original opening Fill, adjusted by actual splits/covers; A=C_set-S_set-M-O-P-Z','BACKTEST_CONTRACT.md: independently reconstruct from original Fill/cashflow; AccountState cannot prove itself','003 repair requires failure recovery to certify only proven financial state; otherwise FAILED+COMMITTED_STATE_UNVERIFIED and no known account'],reproduction=dict(request='Same original synthetic LONG_SHORT gross0.4/net0 request',boundary='Public service AFTER_COMMIT of actual settlement session2',mutations=['post_state.assets.SYNTH:1.lots[0].price:99.9 ->98.9','post_state.cashlots[0].amount:99.9 ->98.9'],post_hash_and_commit_hash_recomputed=True,original_journal_fills_payload_children_unchanged=True,correct_cash_set='997.8',correct_S_set='99.9',correct_available='797.9',claimed_S_set='98.9',claimed_available='798.9',verification='VERIFIED_COMMITTED_PREFIX',financial_state_known=True,ContractError='FAILED but false VERIFIED and known account',KeyboardInterrupt='CANCELLED but false VERIFIED and known account',chain_manifest_getter_independently_verified=True),root_cause='verify_cash_structure calls mutable post_state asset lot original; paired changes keep amount=remaining*price. S_set is a cash_set subset absent from aggregate Journal balance comparison. Failure path calls shared gate+average-cost economic identity but omits normal performance attribution check, which rejects this same state. Original Fill witness remains99.9.',required_fix=['Reconstruct original SHORT gross-proceeds and remaining FIFO restriction from durable original Fill/SPLIT/actual cover and settlement records; do not use two mutable post_state lot fields as independent evidence','Run the same necessary financial proof before success and before failed/cancelled known-account publication; if unproven force FAILED+COMMITTED_STATE_UNVERIFIED, financial_state_known=false, no last_committed_account/known financial snapshot','Preserve original commit/failure evidence; add current paired-field counterexample for ContractError and KeyboardInterrupt, original six directions/RP and legal settled/unsettled partial cover/split/margin controls; submit new fixed SHA and complete SDK/dual-OS raw evidence'],evidence=['SETTLED_SHORT_BACKING_PROBE.json','settled_short_backing_probe.py','INDEPENDENT_CASH_STRUCTURE_CONTROLS.json','reviewer-production-artifacts.zip','REVIEWED_SOURCE_CONTEXT.txt'],security_scope='Synthetic financial consistency injection with recomputed hashes, same class as original003; not native ACL bypass, deployment or actual funds loss')
findings=dict(fixed_sha=FIX,reviewer='GPT Work supplemental reviewer',G2='BLOCKED / REQUEST CHANGES',finding001='CLOSED — FIX VERIFIED at35f93d6; current independent boundary regression PASS',finding002='CLOSED — FIX VERIFIED at35f93d6; current independent direction/legs regression PASS',findings=[finding],new_separate_findings=[],Windows_R2='DEFERRED / NOT VERIFIED',formal_Test=False,financial_approval='NONE',full_historical_host='NOT VERIFIED; accepted package/lock/oldRef/result replay scope only',user_phase_acceptance=False,merge_tag_deploy_live_P6=False)
(O/'FINDINGS.json').write_text(json.dumps(findings,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
rows='\n'.join('| '+r['artifact']['name']+' | '+str(r['tests'])+' | '+str(r['artifact']['size_in_bytes'])+' | `'+r['sha256']+'` |' for r in ci)
report=f'''# AQRP Phase5 G2 — 003修复候选独立复核

审查完整固定SHA：`{FIX}`。对照已审 `35f93d640a2304121131d947a465f57a951cf63f`；实际执行者GPT Work补充审核员，日期2026-10-23（Asia/Shanghai）。PR #8起止描述锁和head均核实一致，detached检出，工作树干净；没有审漂移HEAD或改业务代码。结论：**G2 BLOCKED / REQUEST CHANGES；003 High仍OPEN（部分修复），001/002保持CLOSED — FIX VERIFIED**。没有把开发自测或1116通过改判为G2通过。

## 阻断发现与实际反例

**WORK-P5-G2-003 / High / OPEN — PARTIAL FIX**。位置：`src/aqrp/backtest/ledger.py:123–128`，以及`src/aqrp/services/backtest.py:100–103`的失败恢复认证。新逐桶/逐R/P核对确实纠正原两个反例；但已交收SHORT所得限制S_set仍只将cashlot.amount与同一post_state中的asset lot.remaining×price相比，变量名original并不意味着它已绑定原成交价格。

独立真实公共服务反例沿原LONG_SHORT、gross0.4/net0合成请求，在session2交收原子提交后的AFTER_COMMIT注入。此前真实SHORT Fill为1股@99.9；仅把最新post_state的该持仓lot.price从99.9改98.9，同时把已交收SHORT cashlot.amount从99.9改98.9，重算post_hash及commit hash。原始Journal、真实Fill、payload/children、实际交收时点、现金总额、持仓数量及均价不变。独立重新核过完整提交链、终态manifest所有成员hash及公开result getter；反例通过实际应用服务生成和读取结果，没有手工伪造结果文件。

| 项目 | 原始Fill/Journal应有 | 本版错误发布 |
|---|---:|---:|
| C_set / C_total | 997.8 | 997.8 |
| U_free / U_short | 0 / 0 | 0 / 0 |
| 原始未平SHORT限制所得S_set | 99.9 | 98.9 |
| 当前SHORT市值M | 100 | 100 |
| 真实可用A=C_set−S_set−M | **797.9** | **798.9** |

普通ContractError分支返回FAILED，却给`VERIFIED_COMMITTED_PREFIX`、`financial_state_known=true`和错误last_committed_account；KeyboardInterrupt分支返回CANCELLED，也发布同样错误认证和账户。未改状态的同边界正控正确发布797.9。两个单字段损坏负控正确拒绝；两个字段同时损坏的同一情况在额外41组检查及单独最小脚本均重现。后者1个正控通过、2个捕获类型均复现同一003，不计为两个独立发现。

同一损坏状态通过`_reconciled_account`和平均成本经济恒等式；正常完整projection随后会被绩效归因的`LONG_SHORT_ATTRIBUTION_MISMATCH`拦住，失败快照路径却未执行此检查，因而两条输出路径实际保护不同。这不证明正常成功路径已公开错误账户；本次已证实的是**失败/取消结果错误认证已提交财务状态**。不是Windows权限攻击，也没有运行真实资金或正式Test。

依据：已冻结`CASH_BUCKETS_AND_PROJECTION.md`明确“开仓Fill建立的FIFO gross-proceeds cashlot为权威”，S_set为原始未平空头所得；`BACKTEST_CONTRACT.md`要求从原始Fill/现金流独立重建，不能让AccountState自证。本轮修复还明确承诺原始SHORT背书及正常/失败共享门禁。因此保留原003 High，不新增编号掩盖未闭环。

处置要求：从持久化的真实原始Fill、拆股、实际FIFO cover及交收记录重建未平SHORT gross所得/交收限制，验证量、价、剩余限制，而非只比较两个可变lot字段。让正常、异常、取消的已知财务状态公开使用必要的同一证明；无法证明时必须FAILED+COMMITTED_STATE_UNVERIFIED、known=false，不能公开last_committed_account或已知财务快照。保留原始commit及最初异常，不修改正确答案、删除反例或放松金额/桶/归因门禁。新增本轮成对字段反例（含ContractError/KeyboardInterrupt），继续合法未交收/已交收cover、拆股、margin loss正控和原回归，修复后交新40位固定SHA复核。

关键证据：`SETTLED_SHORT_BACKING_PROBE.json`、`settled_short_backing_probe.py`、`INDEPENDENT_CASH_STRUCTURE_CONTROLS.json`、原始before/at-fault commit及公开返回字节见`reviewer-production-artifacts.zip`。原脚本和当前新增脚本执行原始stdout/stderr、命令及退出码均在本目录。脚本退出0表示证据采集完成，**不代表其中MISMATCH通过**。

## 范围与12项覆盖

保持106条canonical目录、P5十二项（10MVP/2CR），本轮以两处金融源码增量、原始反例、新独立控制及完整SDK复核，不声称把每个历史宿主或后续阶段能力重新实现。

| 需求 | 实际入口/本轮证据及处置 |
|---|---|
| BT-001 | engine/transactions；原子提交、原run真实子进程退出恢复、六组捕获异常边界回归通过；财务认证仍受003阻断 |
| BT-002 | contracts/provider/engine；完整SDK的时序、PIT、严格未来执行及原P1数据可见性回归通过 |
| BT-003 | execution/model与engine；完整SDK的订单合法状态/部分成交/撤销/到期/幂等回归通过 |
| BT-004 | execution/model/liquidity；完整SDK及原20探针的费用/价格域/容量/可见ADV边界通过 |
| BT-005 | ledger/transactions；新逐三桶、逐R/P/科目核对、原短反例及总额对账通过；S_set原始Fill背书仍有003 |
| BT-006 | ledger/engine行动；完整SDK与独立合法拆股/cover/交收正控通过 |
| BT-007 | short/borrow/dividend/margin；正常工程回归及独立正控通过；失败/取消已交收SHORT限制存在003 |
| BT-008 | account/projection/report；正常输出、原始Journal及数值重放通过；错误last_committed_account仍阻断 |
| BT-009 | performance；原25/70、补充25/209、FIFO/费用/方向及标准库原始数值重建通过；不授金融批准 |
| BT-010 | 两因子P1九输入→P3→P4→P5真实服务、替换与重放在新SDK及双OS原包通过 |
| QA-003 | 完整1116与覆盖门槛通过，独立新41组为40通过/1不一致；不能以数量关闭003 |
| INT-002 | 已安装wheel、薄CLI/服务、原Ref、正常终态返回/字节/重放通过；失败结果getter能读出反例错误认证 |

原001提交后缓存问题、002成交方向/跨零腿问题已在35f93d6独立关闭。本轮原三边界一致，扩展20/20、生产20/20及六组BEFORE/AFTER×KeyboardInterrupt/ContractError/RuntimeError通过；实际os._exit子进程原run恢复和重复终态拒绝均回归。坏链、注入PermissionError、现金总额差及原桶错分现在均失败关闭。这些是工程合成执行，PermissionError注入不是真实ACL验证。

## 实际独立执行、环境与原始证据

- 新干净SDK：`{sdk['run_root']}`；CPython3.13.16、标准GIL、64位AMD64；本机`{env['platform']}`。新venv按原哈希锁安装依赖、构建并安装0.5.0.dev3真实wheel，69源码模块逐字节对照固定Git。**1116 passed / 0 failure / 0 error / 0 skipped**；全部模块既定行/分支门槛通过，命令退出0，environment.complete=true。
- 依赖锁SHA256保持`86c7bf65c9a9690036006360062c8cd10a91279705b4070af7033d7699abffeb`；bundle为`a741748c115cd98ecbc2fdfed784cdc5636aea44362ef6ecc81a15933a3b3d94`。未新增依赖/因子/P4金融源码。实际Python完整版本、可执行文件hash、OS、安装/wheel/依赖记录见ENVIRONMENT及SDK原件。
- 原20+4、P3的91项参考检查、扫描三项控制、原Ref/66发布文件/三个原run重放、P1八表+manifest/P3/P4/P5两因子及数值重放实际在本轮SDK执行。`commands.log`逐命令保留，不引用旧SDK代替本轮。
- 审核方标准库独立复算原25组/70项、补充25组/209项及6组2349设计模型场景通过，不导入AQRP或开发方参考脚本产生expected。它们是数学模型，不加进1116或当作额外产品pytest数。
- 另从本轮独立SDK、开发本地SDK和官方双OS实际原始Fill/Market/Settlement及Journal，标准库复算两因子共240个提交、**7864项精确比较**通过，含三现金桶和R/P分别核对、原子交收session、80位Decimal年化/Sharpe核对。该oracle仅覆盖这些实际恒价long开仓SDK场景，short/拆股/cover/损坏另由独立探针覆盖；不将此窄场景说成完整历史宿主证明。开发方1026/因子断言如实另列开发执行，不冒充本审核方执行。
- 新独立41组现金结构检查40 PASS/1 MISMATCH；随后单独最小脚本1个正控正确、2个异常类型重复003。原短桶、扩展20、原三边界、生产20的期望/输入保持；只改固定SHA和独立物理输出路径，适配记录见AUDIT_SCRIPT_ADAPTATIONS。

实际主命令由`run_capture.py`捕获完整argv/cwd/起止UTC/退出码及原始stdout/stderr：固定clone/fetch/detach；标准Python运行`run_sdk.py`→`tools/ci.py`；新venv Python运行四原探针、`independent_cash_structure_controls.py`、`settled_short_backing_probe.py`；标准Python运行scope/CI/SDK/原件核验和独立数学/原始数值复算。可复查所有`*.command.json`、`*.stdout.log`、`*.stderr.log`；不是仅列计划命令。

## 官方双OS原始CI与归档

通过GitHub连接器新读取run39908760220的jobs/artifacts，两job completed/success，官方head为本固定SHA。实际CI执行临时merge `2d1667fb3ec9b1fb5405770a13f6c2a0004f4a81`，parents恰为P4基线+固定head，整树`8d46d3d7a3984e606b7224ea7c2641083d9570d6`与固定head相同；这不是main合并。

| 官方原始ZIP | 测试 | 字节 | SHA256（匹配新读取的API digest） |
|---|---:|---:|---|
{rows}

使用收到的官方原始ZIP字节与新API身份/大小/digest逐项比对；本轮没有再声称重新下载或由GPT在远程双OS执行。独立CRC、全部选中文件hash、完整成员集、wheel69模块/锁/环境、JUnit/覆盖与实际P5终态链、manifest/返回/事务文件核验通过。两包各3757个额外pytest current上传副本、196组，均独立逐完整子树比对原selected数字目录；没有把原selection说成整个ZIP，也未冒称未上传的原symlink身份/ACL已验证。映射/逐成员证据在ci-*及OFFICIAL_CI_VERIFICATION。

开发Evidence.zip：471751695字节，SHA256 `63ba0c413417fbeac30d092815350584dcb14e3c8b661afa98a7e042140e296a`；8599声明文件+manifest，共8600成员，CRC/集合/全部hash独立通过。Fixed-Source.zip全4382跟踪文件逐字节等于本轮固定Git检出。3444受保护文件、12份G1设计/答案与原SHA逐字节核对通过；七项既定包装例外按清单处理。

前轮35f93d6独立封存585039742字节、SHA256 `11b354600fa80c8d806ebddf75bfbf3b1f976fca888a3d98a168ad345aadc51f`已重新核CRC/150项hash；本版本接收的108原件与前轮archive或其外部自排除收据/封存日志字节一致，PRE_REPAIR_IDENTITY等于原Git。三份误写的Phase0 COMMAND_LOG/SELF_CHECK/MANIFEST现均精确恢复35f原字节；错误原件hash仍有保留。daf0551源码/测试/门禁到本候选未变，原本地失败SDK与run39908508825的两份失败官方ZIP新API digest/CRC/原失败日志核实，均保持失败。未用重写旧报告或放宽冻结检查制造通过。

审核辅助脚本首次两处采集错误也保留：首次R/P夹具把dividend赋予空仓，触发合法归因拒绝，改为真实多/空头持仓后重跑；首次原件核验假定自排除RECEIPT在旧ZIP，改为与旧外部原文件比对。初始脚本/原始异常日志及新独立目录保留，未改正确预期或业务代码。它们不是本产品G2发现。详EXECUTION_DISPOSITIONS。

## 未验证与权限边界

WI-R2-001/002及真实Windows三主体隔离继续**DEFERRED / NOT VERIFIED**；不因本轮工程测试或新版恢复代码关闭。正式最终Test没有运行，金融批准NONE，完整历史宿主NOT VERIFIED；只维持已接受的软件包/锁/旧Ref/结果重放范围。SDK中的正式入口拒绝单元/烟雾控制仅证明APPROVAL_REQUIRED，没有执行真实正式Test。没有启用账户、修改真实ACL/服务/调度、部署或实盘。

main/phase4-baseline/v0.4.0仍为`32ea5d6b75c84c07017d87377eeabd2f78207c5c`，全部旧标签与起止远端refs一致；没有合并/标签/P6。本轮没有新增需要用户决定的经济口径或权限申请：003属当前实现必须修复的正确性缺陷，不能套用Windows延期。修复后需新固定SHA独立复核；未来G2通过、用户阶段验收、合并发布及下一阶段授权仍分别判断。

本轮报告及原始证据在独立EVIDENCE.zip封存；字节数、SHA256、清单hash及全部成员复核见独立RECEIPT.json。收据是字节封存，不是数字签名、用户验收或发布许可。
'''
(O/'REPORT.md').write_text(report,encoding='utf-8')
handoff=f'''开发Codex：GPT Work已对PR #8固定`{FIX}`完成003候选独立复核，结论**G2 BLOCKED / REQUEST CHANGES**；001/002保持CLOSED — FIX VERIFIED，003 High为PARTIAL FIX / OPEN。原两个现金桶反例和逐R/P修复已通过，独立干净SDK1116及官方双OS各1116/原始ZIP核验也通过，但新已交收SHORT背书反例仍公开错误已知财务状态：沿原LONG_SHORT合成请求，在session2交收AFTER_COMMIT，只把最新post_state该SHORT持仓lot.price与已交收cashlot.amount同时99.9→98.9，重算post_hash/commit hash；原始Journal、真实Fill1股@99.9、payload/children、数量及均价均不改。应有C_set997.8、S_set99.9、A797.9，实际ContractError给FAILED、KeyboardInterrupt给CANCELLED，却均VERIFIED_COMMITTED_PREFIX/financial_state_known=true，last_committed_account错误给S_set98.9/A798.9；终态manifest和公开result getter也可读出。单字段损坏正确拒绝、未损坏同边界正控正确；成对损坏独立重现两次，不能用测试计数或hash完整替代金融一致性。原因在ledger.py:123–128把同一post_state的可变asset lot当original，只自证amount=remaining×price；正常projection的归因检查会拒绝该状态，failure snapshot的共享gate+平均成本恒等式却接受。请从持久化真实原始Fill、拆股、实际FIFO cover和交收记录重建未平SHORT原始gross所得/限制，让正常、异常及取消公开已知账户前使用完整必要的同一证明；无法证明就FAILED+COMMITTED_STATE_UNVERIFIED、known=false，不公开last_committed_account/已知快照，保留原始commit/故障原因。增加本轮成对字段ContractError/KeyboardInterrupt反例并保持合法未交收/已交收cover、split、margin loss及原六方向/RP、001/002/全部旧回归；不得改正确expected、弱化检查或重写历史审计。报告/逐项证据见同目录REPORT.md、FINDINGS.json、SETTLED_SHORT_BACKING_PROBE.json及settled_short_backing_probe.py；原始before/at-fault/return与实际命令日志已封存。复跑请用新的独立输出目录，保留输入与正确期望；修复后提交新完整固定SHA、干净SDK/双OS原始证据供复核。Windows R2两项及真实隔离继续DEFERRED / NOT VERIFIED，既有正式Test/金融批准/历史宿主边界保持；不启用账户、不改真实ACL、不运行真实正式Test、不授金融批准、不合并、不打标签、不部署、不实盘、不进入P6。'''
(O/'DEVELOPER_HANDOFF.md').write_text(handoff+'\n',encoding='utf-8')
dispositions=dict(product_findings={'003':'OPEN / PARTIAL FIX; paired settled-lot public-service mismatch','001':'CLOSED regression PASS','002':'CLOSED regression PASS'},independent_product_suites={'SDK':1116,'original_boundary':3,'extended_checks':'20 PASS','production_probes':'20 PASS','original_short_bucket':'PASS','new_cash_structure':'40 PASS / 1 MISMATCH','minimal_settled_backing':'1 control PASS / 2 repeated same003 mismatches'},reviewer_acquisition_failures=[dict(command='independent-cash-structure-controls',exit=1,cause='Reviewer first RP fixture accrued dividends on flat position, causing legitimate performance attribution rejection',resolution='Saved first script/raw failure; created fresh rerun1 root with genuine long/short positions and derived equity1002; expectations for original counterexample unchanged'),dict(command='original-audit-preservation',exit=1,cause='Reviewer assumed original self-excluded RECEIPT was inside prior ZIP',resolution='Self-excluded original receipt/logs compared bytewise against retained old external originals; archive members remain all checked')],failed_developer_history='retained/independently verified; no reclassification to PASS',unknown_not_executed=['real native Windows isolation','real formal Test','financial approval','full historical host','deployment/live/P6'],misc_read_errors='One read-only rg attempted historical nonexistent plan filenames STATISTICAL_CONVENTIONS.md and TEST_PLAN.md; exit2 retained in tool transcript, no product execution or files changed; correct existing frozen design paths verified via identity')
(O/'EXECUTION_DISPOSITIONS.json').write_text(json.dumps(dispositions,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(fixed_sha=FIX,G2='BLOCKED / REQUEST CHANGES',finding003='OPEN / PARTIAL FIX',report_bytes=(O/'REPORT.md').stat().st_size),ensure_ascii=False))
