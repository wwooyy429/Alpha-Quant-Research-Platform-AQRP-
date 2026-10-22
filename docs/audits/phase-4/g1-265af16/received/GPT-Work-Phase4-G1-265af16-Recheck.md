# AQRP Phase4 G1 增量复核报告

固定审查 SHA：`265af16353d85ce8c2d229a7517809d707498da8`。结论：**PLAN PASS，受限工程设计预审通过**。原 P4-G1-001 High、P4-G1-002 Medium 均 **CLOSED_DESIGN**，未发现新增 G1 阻断。此结论只确认计划与独立数学候选；P4业务实现、G2、阶段验收及金融批准均不因此通过，P4实施授权仍未授予。

本轮由本对话 GPT Work 主审实际执行，未使用子代理。原审固定 `e40ddd0009cc30664c3a0fe0b74c4a497a541d77` 的报告/失败记录及未验证边界继续保留。本报告存于仓库外，不改写已审提交里的OPEN状态；开发方可以据本报告新增关闭登记，保留旧轮历史。

## A 版本 范围与归档核验

从 [PR #6](https://github.com/wwooyy429/Alpha-Quant-Research-Platform-AQRP-/pull/6) 描述读取的 `AQRP_FIXED_REVIEW_SHA`、API head、独立 detached checkout 均为完整265af16，结束再次核对一致。base/main/phase3-baseline/v0.3.0为 `0a57dccb5618ba08cd3572d6d6b78fec963a3041`。实际固定树为 `f6faa305c3084dd027d607615cc146f7908e5034`。

相对前审e40有100份文件差异，相对P3发布基线共111份：均限已允许的7份根目录/总览文档及phase-4计划、参考候选、验证记录和旧报告归档。`src/tests/tools/.github`、构建/版本/依赖锁、扫描配置、P0–P3原审计、原文、canonical需求及已发布接口/数据/回测契约完全相同；也与已独立复核的P3业务9ac版本比对无业务差异。未创建portfolio/risk/backtest/execution/ui业务包。

64项独立范围/版本/归档检查全部通过。canonical106条唯一ID、16前缀不变；P4选中7条逐字段与原快照一致，仍4MVP/3Competition Ready。1957份冻结文件、45份源码及全量准入bundle、22个锁定依赖均核验；Python3.13.16不变，无新增依赖或安装。

| 固定对象 | SHA256 |
|---|---|
| canonical requirements.csv | `20dd4e6be7188d3121f3cb361faf8901bc91815a6e9752beb14054a12183f0c1` |
| 45份源码全量bundle | `3cec8a9da49a49a93010d7fa6a2012dded25185e2cdca49144cf4d719d56876e` |
| requirements.lock | `86c7bf65c9a9690036006360062c8cd10a91279705b4070af7033d7699abffeb` |

原主审ZIP仍269458字节、SHA256 `2e81fcfb77e83a51c802acc662edb6ed58d6cb25e2612bf540c47f38745c5d4d`；其65份manifest所列文件及manifest自身共66个ZIP成员逐项校验CRC/大小/hash/精确集合。`g1-e40ddd0/received`的65份文件和原manifest、`ORIGINAL_RECEIPT.json`均与主审原件逐字节相同，包括attempt-1失败、原报告/交接/数学/日志。原manifest hash仍 `86f6daff0a5f33c4cdaeef2a7021468390eb7f02222d46636964ba880ac994cd`。

当前phase-4总manifest103条、旧归档manifest72条均完整覆盖各自目录（各自排除自身），不是只抽查几份资料。开发交付ZIP594039字节、SHA256 `ba21d6e211eb47aebb7c8a824e2a31b1a278acafb53953eef6cf7303817664db`，CRC和103份manifest文件核验通过；它是开发计划资料包，不是官方CI原ZIP或完整SDK源码证明。原两份job日志的精确whitespace属性只服务字节保留，未扩大秘密扫描豁免。

## B 需求与接口覆盖

| 原需求 | 依赖保持 | 本次设计及后续适用验证 |
|---|---|---|
| PORT-001 MVP | FACTOR-009;VALID-008 | 正式/显式工程身份、因子无关输入、不可变账户及证据；目标与建议的双lot检查闭环；真实服务/来源/PIT/审批负测留待实现 |
| PORT-002 MVP | PORT-001 | 单/多、等权/分数权、LongOnly及现金；原G01–06/10–11不变；新增不动、部分增减、全平、lot精确性答案 |
| PORT-003 Competition Ready | PORT-001;RISK-003 | 真正多空双腿、gross/net、资金及借券；原G07–09/18–19保持；新增正负原仓、跨0及空仓全平边界 |
| RISK-001 MVP | PORT-001 | 单票/gross/net/leverage/完整及半值turnover；收窄性质并补换手pre过/post拒；实现时逐项前后门禁 |
| RISK-002 Competition Ready | PORT-001;DATA-012 | PIT行业净/总及signed Beta，缺失不填0；新增Beta及行业net的pre过/post拒答案 |
| RISK-003 Competition Ready | PORT-001;DATA-005 | 可交易/空头许可/总借券/可售/跨0；全平只免lot，停牌、资金、许可等检查不豁免 |
| RISK-004 MVP | RISK-001 | 公开check_target和共同service均重算lot及pre/post风险；拒绝不输出成功target/token；实际篡改/绕过负测仍待实现 |

原依赖、来源、等级、拟代码/测试映射均未静默删除；新增映射把001关联PORT-001/002/003及RISK-003/004，把002关联RISK-001/002和QA-001/002/004。后续实际代码位置和测试应补双向追踪，不能用空测试、Planned或Unsupported代替七项能力。

EngineeringScores与ApprovedScores仍分别显式进入同一纯内核；仅工程合成路径可测，正式路径缺真实批准必须APPROVAL_REQUIRED，不默认回退，不接受测试凭据充正式金融审批。PIT、估值价/时点/币种、共同有效交集、固定分数权、stage/拟合隔离、数据/输入/hash与失败ledger继承前审设计，未扩为DAG、任意插件、优化器、订单账本或UI。

## C 两项发现关闭依据

### P4 G1 001 High 在设计层面关闭

定位：[INTERFACE_DRAFT.md第25行](https://github.com/wwooyy429/Alpha-Quant-Research-Platform-AQRP-/blob/265af16353d85ce8c2d229a7517809d707498da8/docs/audits/phase-4/INTERFACE_DRAFT.md#L25)、第29/33/34/35/37/39/47/53行，配套quantity_policy和R01–R13/R17。

新规则先计算理想数量；只有理想数量与原数量**精确相等**才保留原仓。其余仍绝对目标向零取整，不在失败后自动保留原仓，不改交易增量格点。delta始终等于target-current：无调仓可保持已有奇零股且不生成零数量建议；变化的非零target与非零delta分别校验整手。仅target=0、完整原long/short一次全平且原flag=true时，非整手delta可走原全平例外；其他风险从不豁免。非整手部分调仓、跨0或调用者risk_passed无法绕过共同服务。

独立复算X01：E1000，A15/B0、现金850，价格均10、lot10，分数1/9得目标10/90、delta -5/+90，完整换手0.95、目标现金/free均0。新规则明确在A的DELTA_LOT_MISMATCH拒绝，消除了“目标整手却返回非法调仓”的原缺口。R03/R13只保留精确不动，R04/R06只免全平lot，R17外部非整手变化target优先TARGET_LOT_MISMATCH；正负仓及跨0矩阵一致。补充验证普通整手全平不需flag，以及原仓整手的跨0仅在数量层面可以通过。

这属于已声明合成权限内的最小拒绝/持有规则，不增加部分奇零股交易、融资或自动拆单权限，不产生新的用户设计批准需求。**001状态为CLOSED_DESIGN；真实P4服务执行和不可绕过实现尚未验证，G2须复查。**

### P4 G1 002 Medium 在设计层面关闭

定位：[TEST_AND_EVIDENCE_PLAN.md第5行](https://github.com/wwooyy429/Alpha-Quant-Research-Platform-AQRP-/blob/265af16353d85ce8c2d229a7517809d707498da8/docs/audits/phase-4/TEST_AND_EVIDENCE_PLAN.md#L5)、新增冻结案例段，ROUNDING_REFERENCE R14–R16，以及INTERFACE第39/43/45行。

“不增加绝对风险”的泛称已删除。性质现限定固定正价格、正权益和行业映射下的各绝对目标数量、绝对名义金额、gross及行业gross不增；精确保持分支也满足该命题。不推论signed或absolute Beta、net/行业net、相对原仓的turnover、现金或许可单调。数学依据是各绝对目标数量收缩，乘以固定非负系数并求和保持不增；所有前后风险检查仍保留。

R14/X03独立答案：理想(25/3,-10)、目标(0,-10)，权重(0,-0.5)，gross由1降0.5，Beta/行业net由0变-0.5，绝对值由0升0.5；区间[-0.1,0.1]先过后拒。现金1000→1500，post限制500、额外保证金500、自由资金500，不能抵消暴露失败。

R15/X04独立答案：已有(10,0)、cash400、p=(60,50)、lot10、LongOnly等权，连续delta=(-5/3,10)，完整换手0.6/半值0.3；取整target=(0,10)、delta=(-10,10)，完整换手1.1/半值0.55，cap0.8先过后拒。已有与最终调仓均整手，本例独立于001。

R16重新推得 `free_cash=E*(1-gross)-nonshort_restriction-fee_reserve`。原100%短卖冻结加额外100%短仓保证金、无融资参数未改，gross cap1.5仍不能突破资金门禁；G08预算与G19资金答案没有为通过测试而改变。**002状态为CLOSED_DESIGN；实际post-round门禁仍是未来实现/G2必测。**

## D 独立数学与实际执行

主审使用本机CPython3.13.16、MSC1944 x64、Windows11 build26300，以`-I -B`运行自写标准库参考；精确解释器、OS、run_id、UTC、argv/cwd/exit与原stdout/stderr在execution-environment及各command文件。没有AQRP或开发参考脚本导入，也没有用未来待测实现生成expected。

| 新候选 | 独立复核结果 |
|---|---|
| R01/R02 | target整手但部分delta不整手，拒绝；R01完整账户/风险/现金重新推导 |
| R03/R13 | 正/负奇零股精确不动，无调仓，不需要全平flag |
| R04/R06 | 正/负原仓完整全平、flag=true，仅数量例外允许 |
| R05/R07 | 相同全平、flag=false，delta不整手拒绝 |
| R08/R09 | 正反跨0非整手delta拒绝，不拆单 |
| R10 | target与delta均整手，局部数量允许 |
| R11/R12 | 部分平空/加空的delta非整手，拒绝 |
| R17 | 外部变化target本身非整手，先拒TARGET_LOT_MISMATCH |
| R14/R15/R16 | Beta/行业净、换手反例及收窄性质/资金恒等式全部一致 |

17组新候选全部一致。另9组主审补充涵盖完整X01、普通整手正/负全平与正反跨0、极小数量差不能借用ratio容差/不能自动不动、非法lot和非short冻结/fee资金等；343组三资产signed数量向量抽样核对固定价/权益、两行业映射的收窄性质。它们均为设计数学核验，不是新增P4产品测试数量；数量局部允许不代表PortfolioResult成功。逐组输入、公式、actual、预存expected及比较在independent-math-results.json。

原G01–G20文档hash `216430df135be104f59cb0ab6ea375b1af4c7f2a309879c166c410409e822268`、原golden脚本hash `6a272bd1b1744b7bc4d45780776a80b2e32b1bdcd019e2ea7f4fec6bb5a852fa` 与前审逐字节相同。本轮不重复执行未改20组；前轮主审独立复算继续按原执行记录引用，不补写为新执行。

开发check_plan及rounding_reference另各重跑exit0；其输出硬编码Codex developer身份原样保留，command回执注明本轮实际执行者GPT Work。它们只作开发参考重跑，不替代上述主审独立数学。

关键原命令：

```powershell
git clone --shared --no-checkout --config core.longpaths=true C:/Users/11638/AppData/Local/AQRP/checkouts/phase1-57461d5d-5de2-4c78-9b4e-5fad2b5ccb29 C:/Users/11638/AppData/Local/AQRP/reviews/p4-plan-265af16
git -C C:/Users/11638/AppData/Local/AQRP/reviews/p4-plan-265af16 checkout --detach 265af16353d85ce8c2d229a7517809d707498da8
& C:/Users/11638/AppData/Local/AQRP/runtime/Python31316/python.exe -I -B C:/Users/11638/AppData/Local/AQRP/reviews/work-p4-g1-265af16/run_review.py C:/Users/11638/AppData/Local/AQRP/reviews/p4-plan-265af16
& C:/Users/11638/AppData/Local/AQRP/runtime/Python31316/python.exe -I -B C:/Users/11638/AppData/Local/AQRP/reviews/work-p4-g1-265af16/finalize_review.py C:/Users/11638/AppData/Local/AQRP/reviews/p4-plan-265af16
```

scope-raw-git-commands记录原Git查询、diff及输出；reviewer脚本随包封存。初始化输出目录时发现开发方已有3件交付文件，保留原件继续使用目录；没有覆盖旧成果。四项正式scope/math/developer replay均exit0。结束时独立checkout与开发checkout均干净，远端全部旧新标签对象/目标与P3发布回执一致。

## E 官方 CI 的实际核验范围

[run39749034994](https://github.com/wwooyy429/Alpha-Quant-Research-Platform-AQRP-/actions/runs/39749034994)，attempt1、pull_request、Phase3 quality已SUCCESS。Windows job119724639334、Ubuntu job119724639665均成功。API head为265af16，两份官方解码日志实际checkout `adc628bbcd89100116d4121e950b8c72be9579b1`，父依次为发布基线0a57与固定265af16，整tree与固定版本相同。

| 官方工件 | 字节数 | API与上传日志一致的SHA256 |
|---|---:|---|
| Ubuntu artifact12413072103 | 136818044 | `dc192a68bf1c9a88a3bf9513baa93d76bb6d2f24c79470473485cd4e5ccc94dc` |
| Windows artifact12412862175 | 95545877 | `894265c8c250ac0fd80126c4c9be2e3a70402a09c6bc959ad64fbb77d62800c5` |

本轮取回API、原job解码日志并核checkout/集成父/tree及上传digest文本；**未下载两份CI原ZIP、未独立对其字节重算hash，未核内部JUnit/coverage/wheel/manifest或重数578**。精确范围在ci-review-summary.json。旧578为既有P3回归；本轮未另跑未改业务SDK/旧20+4/91/扫描控制，不能将CI成功或新候选脚本改名为P4实现测试。

本轮主审证据ZIP、逐文件manifest及外部RECEIPT独立封存，保存命令/脚本/数学/原API和解码日志/关闭登记/开发交付原件；包hash和成员复核见RECEIPT.json。新主审ZIP与官方Actions原ZIP明确区分。

## F 未验证事项与后续门禁

没有需要为本轮最小设计修订另行批准的交易权限或经济假设变更。**用户尚未授权P4实际实现**；G1通过后可据本报告决定是否授权既定7项受限工程实现，不自动包含阶段验收、合并、标签、部署、实盘或P5。原P3受限验收及延期保持，不重新请求已接受的P3设计/验收决定。

真正物理隔离、正式Test、金融批准及完整历史宿主仍NOT VERIFIED；旧Windows恢复尝试的FAILED_CLOSED和局部验证记录不改判。工程双入口不能把上述延期变成正式ResearchValidated/StrategyApproved。

进入已授权实现后必须冻结完整PIT/账户/权限/配置夹具与hash，按独立答案检验真实内核和共同service，执行目标/delta篡改、停牌不动/全平、sellable/借券/资金限制、全部pre/post拒绝和证据不可变负测。不能因局部数量通过而返回完整成功；不能用自动保留/拆单/增量格点改变冻结策略。新增源码重新审全bundle/receipt，锁及双OS证据按实际变更验证，完成实现后提交完整固定SHA给GPT Work G2。

最终结论：**PLAN PASS；001/002仅在设计层面关闭，P4实现与授权仍未完成。**
