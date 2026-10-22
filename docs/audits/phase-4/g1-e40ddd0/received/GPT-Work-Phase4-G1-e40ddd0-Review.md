# AQRP Phase4 G1 独立计划预审报告

固定审查 SHA：`e40ddd0009cc30664c3a0fe0b74c4a497a541d77`。结论：**PLAN BLOCKED，1 High、1 Medium 待修订**。本轮审查计划、接口、合成口径及独立答案候选；不存在 Phase4 业务实现通过结论。执行者为本对话 GPT Work 主审，未委派子代理，也未替其他执行者补写身份。

本报告及证据存于仓库外，未修改被审文件。PR #6 的描述锁值、实际 head、独立 detached checkout 均为上述 SHA，审查结束仍一致。Phase3 的受限工程验收及发布继续有效；真实隔离、正式 Test、金融批准和完整历史宿主不因本轮预审变为已验证。

## A 固定版本与阶段边界

[PR #6](https://github.com/wwooyy429/Alpha-Quant-Research-Platform-AQRP-/pull/6) 的 base 为 `0a57dccb5618ba08cd3572d6d6b78fec963a3041`，与官方远端 main、phase3-baseline、v0.3.0 的 peeled commit 一致。PR #5 API 确认已合并，merge commit 为 `70086a74a632c73a2769ec24901ec47babfa8976`。本轮末次 `git ls-remote` 核对 main、全部 phase0–3 baseline 及 v0.1.1/v0.2.0/v0.3.0 的标签对象和目标，均与固定版本的发布回执逐项相同，未观察到旧标签移动。

固定树为 `66ae3cce5f9d73271963e72aaaf3ec171c08c4c1`。相对 Phase3 发布基线只增加 28 份计划/文档文件的内容：7 份根目录或总览文档、21 份 phase-4 资料，共 779 行。`src/tests/tools/.github/requirements.lock/pyproject.toml`、P0–P3 审计资料、canonical 需求、原文以及已发布接口/数据/回测契约均无差异；与已独立审查的 `9ac5db069287a6e4a095e25ae8c3cc8fa229cded` 比较，业务代码、测试、工具、CI 和锁也完全相同。

独立校验 53 项全部通过，包括 106 条唯一 canonical 需求、16 个 ID 前缀、Phase4 七条原始行逐字段一致、1957 份冻结文件、45 个源码模块及其全量准入 manifest。22 个依赖继续锁定，没有安装或新增依赖。

| 对象 | 实际 SHA256 |
|---|---|
| canonical requirements.csv | `20dd4e6be7188d3121f3cb361faf8901bc91815a6e9752beb14054a12183f0c1` |
| 45 模块完整源码 bundle | `3cec8a9da49a49a93010d7fa6a2012dded25185e2cdca49144cf4d719d56876e` |
| requirements.lock | `86c7bf65c9a9690036006360062c8cd10a91279705b4070af7033d7699abffeb` |

本轮仅 Phase4 G1。P4 实现须在 G1 关闭阻断后另有用户授权；无 P5 订单、撮合、账本、优化器或后续 UI 实现。用户已明确接受的 Phase3 延期不重新作为本轮工程计划的新增阻断。

## B 七项需求覆盖及可达性

逐项核对 `docs/requirements.csv`、原文 V3.0 第7章、Phase4 快照/追踪表及接口草案；七项均保留，没有把 Competition Ready 改为空接口或 Unsupported。下表是设计覆盖，不是测试执行通过。

| ID与等级 | 原始依赖 | 拟实现及测试映射 | 本轮意见 |
|---|---|---|---|
| PORT-001 MVP | FACTOR-009;VALID-008 | 接口§1/4，portfolio/contracts、service；因子无关、账户不可变、身份/PIT/审批与输入 hash 负例，集成服务测试 | 工程入口可达；正式金融入口仍门禁。目标/调仓契约受001影响 |
| PORT-002 MVP | PORT-001 | §2/3，portfolio/weights、construct；G01–06/10–11，单/多、等权/分数权、LongOnly、零负分/并列/交集/现金/lot | 覆盖完整；已有奇零股与调仓 lot 的001待冻结 |
| PORT-003 Competition Ready | PORT-001;RISK-003 | §2/3，真实双腿 G/N 和中心化；G07–09/18–19，空腿/重叠/资金/许可 | 双腿不是更名的 LongOnly；数量边界仍受001影响 |
| RISK-001 MVP | PORT-001 | §3，risk/checks；G12–14/20，单票/gross/net/leverage/完整及半值换手，pre/post-round | 风险顺序有完整复查；测试性质002需修正 |
| RISK-002 Competition Ready | PORT-001;DATA-012 | §1/3，行业净与总、signed Beta、PIT 暴露；G15–16和缺失/修订/过期/未来负例 | 缺失不填0设计正确；增加002取整后的 Beta/行业净反例 |
| RISK-003 Competition Ready | PORT-001;DATA-005 | §3，状态/空头许可/总借券/可售/跨0；G17–19及停牌、平旧空、缺数据 | 总借券与跨0设计合理；001须说明建议数量资格 |
| RISK-004 MVP | RISK-001 | §4，共用服务与重算 RiskDecision；篡改/陈旧/skip/错误证据绑定/失败 ledger 测试 | 拒绝后不得给成功 target；将001 lot 检查接入不可绕过门禁 |

拟测试位置为 `tests/portfolio/{test_weights,test_construct,test_contracts}.py`、`tests/risk/{test_limits,test_tradability}.py` 和 `tests/integration/test_portfolio_service.py`；canonical 各 ID 的原计划测试路径保留，待真正实现后补实际双向映射，不要求现在创建空文件。

## C 接口 数学 安全与依赖意见

同意目前的工程设计方向：`construct_approved` 与显式 `construct_engineering` 共用纯数学/风险内核；工程数据身份、NONE 金融批准和不可执行建议贯穿输出；无默认审批降级、测试凭据冒充正式批准或调用因子代码。正式 ApprovedScores 缺真实批准须 `APPROVAL_REQUIRED`，工程路径不能提升 ResearchValidated/StrategyApproved。这保留了 PORT-001 对 FACTOR-009/VALID-008 的正式依赖，同时使受限工程测试可达。

PIT 候选覆盖 event/available/as_of/decision、同币种/市场/日历/估值价 Ref、原信号 session 年龄及所有输入侧车。缺暴露/许可/借券不是0；持有但未选择的证券不能消失；时点或审批失败先于排名算术。P4 不重新拟合 P3 stage、方向和标准化；因子预注册固定权重按绝对值和归一，共同有效交集、稳定 ties、LongOnly 负分等权和全现金分支都有定义。G/N 双腿、signed Beta、行业总净、总借券额度及资金缓冲口径可独立检验。

合成资金口径有一个应显式写入设计的推论：冻结短卖所得100%并另收短仓100%保证金、无融资时，`free_cash = E*(1-gross) - existing_nonshort_restriction - fee_reserve`。因此默认账户即使 gross/leverage cap 写1.5，资金检查仍使可接受 gross 至多约1（金额容差内）；G08 的1.2双腿是正确的预算算术，按 G19 资金规则会拒绝。这是已声明的合成假设，不是计算错误，不能为使案例成功而暗改保证金或风险限额。

前后风险重查、失败/取消 ledger、不可变终态证据、输入/代码/环境 hash、只返回不可执行建议的阶段边界均合理。新增 portfolio/risk 源码后必须重新审完整 bundle 和 receipt；旧 P3 receipt 不能批准新代码。新依赖目前为零；若后续改变，须先锁候选并验证 Python3.13.16/双OS兼容。

## D 待关闭发现

### P4 G1 001 High 目标整手不能保证调仓数量整手

状态 **OPEN，阻断 G1**。这是核心数量契约缺口，不是尚未存在的 P4 实现故障。

位置：[INTERFACE_DRAFT.md 第25行](https://github.com/wwooyy429/Alpha-Quant-Research-Platform-AQRP-/blob/e40ddd0009cc30664c3a0fe0b74c4a497a541d77/docs/audits/phase-4/INTERFACE_DRAFT.md#L25)，并关联第33、39行；`SYNTHETIC_PROFILE.json:14`；已发布 `BACKTEST_CONTRACT.md:49`。依据为 PORT-001/002/003、RISK-003/004 的合法目标、调仓建议及不可绕过约束。草案用“交易lot”取整绝对目标，只有目标0时允许奇零股全平，然后直接 `delta=target-current`；风险资格清单未明确 delta 的 lot 检查。

独立反例 X01：E=1000，A/B 同价10、lot=10，已有 A=15股、B=0，现金850、受限现金0；两票可交易，A可售15，Beta均1、同一行业，其余默认限额。LongOnly 分数 A=1/B=9 得权重0.1/0.9，目标 A=10/B=90 都整手，但建议 A卖5/B买90。A目标非0，卖5不是整手，也不满足“只允许奇零股全平”的例外；gross/net/Beta均1、行业总净均1、换手0.95、现金与自由现金均0，其余上述检查可通过。只校验目标会漏掉建议数量的不合法性。不可执行标记及 P5 再检查不能代替 P4 自己承诺的数量契约。

请冻结 lot 对 target 和 delta 的适用规则。沿现有合成规则最小修订可为：成功前显式校验每个非零 delta 整手，只有已声明的全平例外可豁免；不合格明确拒绝，不能推迟到 P5。对 delta=0 的原奇零股持有单列规则，避免与“非零目标严格lot”冲突。若改用交易增量格点取整，必须说明 `q_target=q_current+delta`、对目标格点的影响及全部风险重查，不能默许部分奇零股或暗改量化策略。新增已有奇零股部分减仓/增仓/不动/全平与跨0独立案例。

开发方负责给出一致的具体设计；主审核验。若选择扩张合成交易权限、变更已冻结账户/交易语义而非最小拒绝修订，须用户批准具体方案。

### P4 G1 002 Medium 取整性质对风险的单调性表述过宽

状态 **OPEN，需随本轮设计修订关闭**。接口已要求所有必需约束 pre/post 复查，本发现不宣称现有设计删除了这些检查。

位置：[TEST_AND_EVIDENCE_PLAN.md 第5行](https://github.com/wwooyy429/Alpha-Quant-Research-Platform-AQRP-/blob/e40ddd0009cc30664c3a0fe0b74c4a497a541d77/docs/audits/phase-4/TEST_AND_EVIDENCE_PLAN.md#L5) 的“取整后数量不增绝对风险但可能破坏净下界故重查”。涉及 RISK-001/002 及 QA-001/002/004。目标向0取整只保证各项绝对目标数量/固定正价格下的绝对名义金额和 gross 不增；不能推广到绝对 Beta、行业净或相对已有持仓的换手。

独立 X03：E1000、目标权重(+0.5,-0.5)、价格(60,50)、lot均10、Beta均1且同一行业。连续 Beta与行业净为0；目标取整变(0,-10)，权重(0,-0.5)，Beta与行业净变-0.5，绝对值从0增到0.5。若区间[-0.1,0.1]则 pre通过/post拒绝；gross却由1降到0.5。目标资金自由余额500，资金变化不能消除暴露超限。

独立 X04：E1000、现金400、已有 A10/B0，价格(60,50)、lot均10，LongOnly等权各0.5。连续预计换手0.6；目标取整(0,10)后换手1.1。cap0.8时应 pre通过/post拒绝。已有持仓都是整手，本例不依赖001。

请将性质收窄到各绝对目标数量、固定价/权益下的单票绝对目标金额、gross及行业gross；有符号区间、Beta、净/行业净、换手、现金和权限继续分别重查。把 X03/X04 冻结为独立预存答案及未来 post-round 拒绝用例，不能为满足错误性质削弱风险检查或修改 expected。

## E 实际执行与证据

主审在本机 Windows-11-10.0.26300-SP0、CPython3.13.16标准 GIL x64 上执行。精确 `sys.version`、实际解析后的解释器路径、OS、唯一run_id、UTC起止、argv/cwd/exit、stdout/stderr在 `execution-environment.json` 和各 `.command.json/.log`。不复用开发方 Conda 环境身份；无安装、账户/ACL/服务变更。

核心原命令如下，所有审核输出在仓库外；脚本源码随证据封存。

```powershell
git clone --shared --no-checkout --config core.longpaths=true C:/Users/11638/AppData/Local/AQRP/checkouts/phase1-57461d5d-5de2-4c78-9b4e-5fad2b5ccb29 C:/Users/11638/AppData/Local/AQRP/reviews/p4-plan-e40ddd0
git -C C:/Users/11638/AppData/Local/AQRP/reviews/p4-plan-e40ddd0 checkout --detach e40ddd0009cc30664c3a0fe0b74c4a497a541d77
& C:/Users/11638/AppData/Local/AQRP/runtime/Python31316/python.exe -I -B C:/Users/11638/AppData/Local/AQRP/reviews/work-p4-g1-e40ddd0/run_review.py C:/Users/11638/AppData/Local/AQRP/reviews/p4-plan-e40ddd0
& C:/Users/11638/AppData/Local/AQRP/runtime/Python31316/python.exe -I -B C:/Users/11638/AppData/Local/AQRP/reviews/work-p4-g1-e40ddd0/finalize_review.py C:/Users/11638/AppData/Local/AQRP/reviews/p4-plan-e40ddd0
```

| 实际检查 | 结果与适用范围 |
|---|---|
| 主审自写 verify_scope.py | 53项 PASS；原git命令与输出见 scope-raw-git-commands.json；完整源码/旧审计未变 |
| 主审自写 independent_plan_math.py | stdlib Fraction/Decimal，G01–G20全部算术一致，另6组边界/反例断言通过；不导入AQRP或开发参考脚本 |
| 开发方 check_plan.py 重跑 | exit0，仅一致性；输出硬编码“Codex developer”保留，本轮重跑实际执行者单列为GPT Work |
| 开发方 golden_reference.py 重跑 | exit0、20候选；作为参考脚本重跑，不能替代上一行主审独立推导 |
| 结束状态/官方refs/PR/CI树绑定 | 独立checkout及开发checkout均干净；PR仍open且锁值未漂移；旧新标签对象和目标全部匹配 |

G01–G20 的输入、公式、实际值、预存候选值与比较逐组保存在 `independent-math-results.json`，包括 G02合成分数/G06交集、G10连续数量及残余现金、G11全部现金冻结保证金、G13半值换手、G17两类越界、G20 exact借券不借用ratio容差等子字段。缺失/PIT/审批等行为只认定为设计要求，未把手写布尔值当作产品运行测试通过。完整可执行对象、PIT侧车与 hash 夹具必须在实现前冻结。

保留一次主审辅助脚本失败：第一次将共享本地clone的 `origin/main` 当官方远端新main，实际它是旧缓存 f26255f，断言失败；这是主审环境假设错误，不是项目缺陷。`attempt-1/`保存该失败、其余当次命令与日志。随后改查官方 URL 的 `git ls-remote`，第二次四条检查命令均exit0；未移动任何本地/远端标签或分支来迎合结果。探索性读取曾遇不存在的猜测路径和过长输出，后续以文件枚举/目标范围重新读取，不把读取失败当产品失败。

### 官方 CI 证据范围

[run 39740405800](https://github.com/wwooyy429/Alpha-Quant-Research-Platform-AQRP-/actions/runs/39740405800)，attempt1、pull_request、工作流 Phase 3 quality，Ubuntu job119695980314 和 Windows job119695980827 均SUCCESS。API head为固定e40；两份官方解码job日志实际checkout `2c14c96124ec7b1fefbc5f6fc88e27bcf962213a`，父提交依次为0a57与e40，其tree与固定e40相同。

| 官方工件 | 官方字节数 | API及上传日志一致的SHA256 |
|---|---:|---|
| Windows artifact12409500604 | 95545609 | `2fb7ba18624a8dc8a546496bb550c249244205b30a831346fe0b9fff5a3044ca` |
| Ubuntu artifact12408773360 | 136818283 | `94a68c56538a2ec06d20bb9608ecb0c8636f49c35150fbf4fe7276aa73e549b1` |

本轮实际取API元数据、解码原job日志及集成commit并核对树/父/上传digest文本；**未下载这两份原始ZIP，未独立对ZIP字节重算hash，未重新解析内部JUnit/覆盖率/轮子/manifest或逐项确认578计数**。API与日志及精确核验范围见 `ci-review-summary.json`。Phase3已验收578及前轮独立验证保持各自原执行身份；本轮不重复运行未改业务SDK、旧20/4/91及扫描控制，不将CI成功冒充P4测试。

`fixed-plan-source.zip`仅含固定SHA的28份变更文档，是部分源码资料包，明确不是全仓git archive或干净SDK证据。开发方交来的封存包另存，未改压缩后冒充原件；本轮证据包以新主审manifest独立封存，包hash与清单hash见同目录 `RECEIPT.json`。

## F 未验证 用户决定与关闭条件

真实部署隔离、正式最终Test、金融批准、真实账户/市场/借券与费用规则、完整历史宿主继续 **NOT VERIFIED**。此前Windows隔离失败/未完成及修复候选历史保持，不因本轮改记成功。本轮无P4实现、真实订单或账本，不能评定G2/阶段验收。

开发方应先提交001的确定数量/lot规则与002的修正性质及反例、更新候选/追踪/hash，保留本报告和两项OPEN状态，提供新40位SHA及PR描述锁值供增量复核。主审负责确认关闭；开发自查不能自行改判。按当前明确的全平例外进行最小拒绝规则修订不要求重开P3延期决定；如欲允许部分奇零股或改交易格点算法，先给出具体影响，由用户批准设计。合成无融资/双重短仓资金限制须保留并显式说明，改变经济假设也须用户决定。

G1关闭后仍需用户单独授权P4实际实现；不自动授权金融批准、部署、合并、标签、实盘或P5。本报告最终结论为 **PLAN BLOCKED**。
