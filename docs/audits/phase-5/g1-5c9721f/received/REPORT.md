# Phase5 G1 独立计划预审

审查者：GPT Work / 本会话 Codex 补充审核执行。日期：2026-10-23（Asia/Shanghai）。

**指定完整 SHA：`5c9721f96679f4d495b7b3b93af3e2e31e66ae62`。结论：PLAN BLOCKED / REQUEST CHANGES。**

**收尾漂移记录：** PR #8 的描述锁定值和head已更新为 `bd18d1b98b5647f4f4b6345ffe73dca40acaf038`，状态仍open、未合并。本报告只覆盖用户指定的5c9721f固定对象；未检出或审查新提交，四项发现及BLOCKED结论不直接外推到bd18d1b。起止原始PR响应分别保存为PR8_START.json、PR8_FINAL.json。

四项设计发现：High×2、Medium×2，均 OPEN，本轮不放行 G1。25 组手算候选的 70 项字面答案独立复算全部一致；阻断来自扩展情景下接口/经济语义尚不能唯一确定，而非篡改候选答案或声称不存在的 P5 实现测试失败。P4 已发布验收和 G2 PASS 不受本报告影响。

## 固定版本、范围及基线

开始时实际从 PR #8 描述读取 AQRP_FIXED_REVIEW_SHA，与用户指定完整 SHA/head 一致；独立 clone/fetch 后 detached checkout，审固定对象，没有采用收尾发现的新 HEAD。遵循仓库 AGENTS 与既有审查协议；未创建审计分支或 PR，全部独立脚本与工件存外部目录，开发 checkout 未改。

P4 main / phase4-baseline / v0.4.0 独立远端核对同点 `32ea5d6b75c84c07017d87377eeabd2f78207c5c`；旧标签对象/目标逐项与封存旧表一致。实际 merge `d3993d07e5df1b5c2f7acd30cb628226f7b1fc09` 的 tree 与已审 `3c8757949b0fd5c97953b06a74ebc2d0e56676e4` 相同；随后发布登记不改变业务字节。包仍 0.4.1.dev1、53模块，阶段标签 v0.4.0 与制品版本不同已明确记录，未为标签重写已审 wheel。

本计划相对发布基线仅45个计划/状态/审计资料文件变化。131个冻结文件、整个现有 src/tests/tools/CI/构建/锁无变；canonical106目录不改。P5没有 backtest/execution/performance 业务包或产品测试。35个计划 FILE_MANIFEST 成员逐项核对；开发方外包57项 CRC/hash、Fixed-Source.zip 3894项逐字节匹配固定 checkout。

P4 STATUS 勘误已核：旧冗余字段原值逐项保存在 historical_status_fields，source_commit 指向32ea5d6；当前字段与原G2/用户批准/发布记录相符，未改写原报告、业务或已发布标签。此项不是新增金融批准。

## 十二项需求覆盖及适用验收

原CSV与 REQUIREMENTS_SNAPSHOT 的12行全部相同，10 MVP/2 Competition Ready，无遗漏或降级替代。各项当前均为计划、未实现；以下为G1设计意见。

| 需求 | 主要设计与测试映射 | 复核意见 |
|---|---|---|
| BT-001 MVP | 全事件状态机/因果链，T01/T02/T04 | 有映射；需解决001的总序与原子事务表达 |
| BT-002 MVP | PIT、严格未来开盘、独立open侧车，T01 | 方向合理；±1us参考独立核对，仍须实施后mutation控制 |
| BT-003 MVP | 订单全状态、partial/cancel/expire、幂等，T02/T03/T04 | 有完整计划；001/003影响具体撮合与费用提交 |
| BT-004 MVP | tick/slippage/commission、共享容量、限价/期限，T03/T07 | 不能使用未来日终量的边界明确；003费用上界待定 |
| BT-005 MVP | 复式账本、移动均价、现金/权益及独立重建，T04/T05/T11/T12 | 799/210/1009及买卖等候选正确；001/002影响账户可执行定义 |
| BT-006 CR | split、dividend/ex/pay、T+1、delist/stale，T06/T07 | 明确合成规则和未知规则失败；002需细化结算现金桶 |
| BT-007 CR | short所得限制/额外margin/borrow/股息应付，T05/T06/T07 | 不能把已定义多空改为Unsupported；002和004影响实际分账/归属 |
| BT-008 MVP | RAW mark、每日账户/风险/订单/Fill，T05/T07/T08 | 计划可追踪；需保留真实E_total与预算E_alloc两套记录 |
| BT-009 MVP | A252/ddof1/rf/TWR/MDD/换手/成本/贡献，T08/T12 | 现有算术正确；004胜率/盈亏比缺确定性细则 |
| BT-010 MVP | 真实P1/P3/P4链、只换精确因子配置，T09/T10 | 两次完整模拟/核心hash/预定差异的验收计划合理，未来实际运行待G2 |
| QA-003 MVP | 至少10类核心不变量、T01–T12、独立重建 | 不是“12类”数量即可通过，四项修订应各增加明确trace/守恒/统计答案 |
| INT-002 MVP | provider→P4→提交/撮合/账本→绩效，T09/T10 | 工程/正式入口区分清楚，原始工件UUID/hash双绑定方向合理；资金/排序缺口阻断当前可实施性 |

冻结 Python3.13.16 和既有依赖锁，无新增包、DAG、任意外部插件或P6 UI范围扩张。无融资、多币种、真实市场/税/碎股等明确为该合成profile的边界，用户后续须明确接受；不能据此删去已承诺的多空、行动、交收和部分成交能力。

## 发现与必要修订

### WORK-P5-G1-001 · High · OPEN · 阻断

位置：`docs/audits/phase-5/INTERFACE_DRAFT.md:11`、`:17`；涉及P0 BACKTEST_CONTRACT的排序与逐笔原子要求。

草案同时规定全局事件总序 `(time,phase_priority,sequence_id)`，Match70/Fill80/Account90，以及每笔Fill/账本事务不可被另一订单穿插。若两个订单A/B在同一切片，同一全局队列的严格排序会成为 A.Match70、B.Match70、A.Fill80、B.Fill80、A.Account90、B.Account90；逐笔事务要求的 A.Match→A.Fill→A.Account→B.Match→B.Fill→B.Account 不满足这个总序。

这不是否定“逐笔原子”这一正确要求，而是缺少外层调度事件与内层事务子事件的区分，以及账户状态究竟何时捕获/重查/提交。仅增加“原子”文字仍可能让Match先预计算多个过时候选。独立抽象状态例：E1000、两笔各1股@100、每笔费1、当时单票上限15%，每笔对同一旧状态约10.01%均可过，按两笔实际已提交状态约20.04%应拒后笔；现金预留足够不能替代逐Fill风险。该例是已接受订单状态下的调度反例，不冒称完整当前P4请求或实际P5输出。

修订要求：给出唯一可执行调度定义，例如外层Match事务及有独立因果key的内部Fill/Account记录；或明确其他一致顺序。冻结队列key、Journal/replay key、pre/post状态版本、稳定order顺序、容量消耗及崩溃提交边界。至少给同刻双订单完整期望trace，并含cancel65、borrow95、估值100的交互；不得直接静默改P0冻结契约。需由开发方提出细化，主审复核；若实质变更原契约，须列影响并由用户批准。

证据：`INDEPENDENT_DESIGN_CASES.json` C01_ATOMIC_TOTAL_ORDER / C01_RISK_STATE_REFERENCE。

### WORK-P5-G1-002 · High · OPEN · 阻断

位置：`MATH_CONTRACT.md:5`、`:21`；`INTERFACE_DRAFT.md:21`；`PROFILE_AND_DECISIONS.md:11`、`:13`。

草案D05让卖出款T+1才可用，D07把全部未平仓short原始所得100%限制，并另收100%当前short市值margin；公式实际available=settled−O−S−V−其他，预算又B=U+O+P+F。新short所得在结算前同时属于U和S，违反“冻结项目互斥/不重叠”的声明，但没有分出settled/unsettled restricted proceeds。

完整最小费例：现金1000，short1股实际价100，fee1，C1099、U100、settled999、S100、V100、E999。字面公式available=799；若同一笔100所得只按声明限制一次，再加100 margin，available=899。T+1只把这100从unsettled转settled，short所得仍全部限制、仓位/mark/E不变，字面公式却从799变899，多出100可用。允许这种额外预资金限制是可能的合成选择，但它不是当前声明的两个冻结，也不能暗中用重叠金额代表。

同问题传到P4：加F10，结算前C_alloc989、E_alloc889、P4free789；结算后C_alloc1089、E_alloc989、P4free889。G25的U与S是静态独立输入，其758/768算术完全正确，但没有覆盖“U正是新short所得”这个允许的生命周期。

修订要求：明确互斥现金桶及资金恒等式，区分未交收/已交收限制所得、margin、order reserve、payable、fee预算；逐Fill、结算、部分cover、跨零、分红支付逐项说明迁移/释放。先正确确定P5真实可用现金，再另推P4保守投影并准确命名额外保守量。若要新增临时prefunding，须显式经济决策、用户接受及对应独立答案。补含最小费的short开仓→结算→部分cover与P4同点投影，不能靠Unsupported或拒绝所有合法新short状态绕开。

证据：C02_SHORT_SETTLEMENT_OVERLAP / C02_WITH_PROFILE_MIN_FEE。此处未声称实际P5发生资金损失；当前不存在P5业务实现。

### WORK-P5-G1-003 · Medium · OPEN · 阻断当前费用契约

位置：`INTERFACE_DRAFT.md:25`；`PROFILE_AND_DECISIONS.md:9`。

表中“decision价±5%”可读为双边价格带，接口具体文字却只定义买单最高价和卖单最低价；紧接着 fee_upper 使用 price_upper。卖单最低价不是手续费的最大名义额，未定义卖出向有利方向跳空时的上界，也未明确累计已花费+剩余预留如何受F约束。

独立例：decision100，1股卖单下限95；next raw_open200400.41，10bps向下tick后实际200200.00，佣金200.20，远大于按105上界算的1.00和F10，但仍满足卖出最低价。若本意是所有方向都限制在±5%内，此例应直接拒绝，必须在接口中明确；若允许有利跳空，则需新的有效fee上界或真实费用预算拒绝规则。逐Fill重查的泛称不足以唯一选择这两种经济结果。

修订要求：统一side/type的可成交价格域和price_upper定义，LIMIT和MARKET分别给fee最坏界；逐Fill明确累计实际费用+剩余最坏费用≤预注册F（或其他同样明确的约束），超界拒绝且不自动增加F。补有利卖出gap、部分Fill最小费耗尽、撤单释放的独立答案。由开发方提出具体合成规则、主审复核，用户在实现授权中确认经济选择。

证据：C03_SELL_FEE_UPPER。旧候选G09/G10/G11/G12均仍正确。

### WORK-P5-G1-004 · Medium · OPEN · 阻断当前统计验收口径

位置：`MATH_CONTRACT.md:17`，关联D07/D10与T05/T08/T12。

已写明FIFO和entry/exit费用数量分摊，但没有唯一规定“完成round-trip”的分母单位、部分平仓完成时点，以及逐时点borrow/dividend成本分到哪个未平/已平配对。移动均价账本和FIFO统计分开是正确方向，仍需要冻结统计规则。

同一入场BUY2@100 fee1，分两次SELL1@104 fee1、SELL1@97 fee1：若每个FIFO已闭合fragment算交易，净额+2.5/−4.5，胜率1/2、盈亏比5/9；若等原入场lot全平才完成一个round-trip，总净−2，胜率0/1，无赢家则盈亏比undefined。两者对总账户损益都−2，仅FIFO顺序本身不说明采用哪一计数粒度。

借券分摊同样影响输赢：short A1@1000在session1，B1@1000在session2；第一日借费.04、第二日两股总借费.08；随后cover A1@997.93，entry/exit fee各1。若按lot实际持有期，A承担.08，净−.01；若把累计position费用.12按当前两股池分摊，A承担.06，净+.01。需要明确每次计提归属、每证券/账户/lot舍入单位和余分处理；不能在看结果后挑口径。

修订要求：明确closed fragment/entry lot/flat-to-flat选择与部分成交/跨零规则，冻结borrow/股息应付的时间与配对归属、长仓股息是否进入该交易统计及相应命名。补上面完整例、跨零、部分cover、无完成/无赢家/无亏损/零利润的独立答案；不得用AccountState作为统计期望。可选择不同合理合成口径，但必须唯一、可重放且后续用户明确接受。

证据：C04_FIFO_COMPLETION_UNIT / C04_BORROW_LOT_ATTRIBUTION。不是要求废弃FIFO或修改原有70项正确答案。

## 已确认合理的接口、数学及安全边界

独立open侧车与P1收盘才可得的完整bar分离，严格未来合法open、晚到1us不得倒填、DAY/GTC明确，避免未来volume/high/low做盘前信号或虚构LIMIT成交；同证券共享容量、目标/delta/partial lot和完整奇零股全平例外方向正确。本次另有严格时刻、共享容量和最终odd-close参考推演，尚不是产品运行。

P1真实九文件、P3终态engine/config与信号、P4真实request/candidate/risk/result/audit的UUID+hash绑定和后补文件不取得原证据资格的设计符合前轮缺陷经验。provider因子无关，开发集拟合/参数预注册、不给label/最终Test、运行中不返调冻结配置均保留；具体实现及future-mutation有效性待G2。

精确数量/现金、移动均价费用分离、复式借贷、行动应收/应付、RAW marks、TWR、252/ddof1/rf转换、净费用一次、MDD含初始值及undefined的设计已有明确基础；G01–G25、每一输入/公式/答案/容差均由主审自有标准库脚本复算，25/70通过。G22独立Fraction样本方差1/75，Decimal90平方根求Sharpe=sqrt21，在1e−12内一致；其余容差0，未用未来AQRP实现产生expected。

另有16组独立算术扩展和13组具体设计/边界推演，全部标为design reference。它们不是“新增P5测试通过”，四项反例只是证明草案存在需要选择的语义。开发方reference_check.py另被原字节重执行25/70，仅列辅助结果，未冒充主审独立参考。

12类测试计划覆盖已知答案、边界、性质、独立重建、未来mutation、完整SDK/旧Ref、双OS原ZIP及实际字节检查；需加入本轮四项明确案例和确定的期望trace/金额/统计定义。关键业务≥95% line/≥90% branch及资金/时序不变量逐项案例要求保留；统计数量和总覆盖率不能代替四项闭环。

## 实际执行、环境与证据

本机主审实际使用独立 CPython3.13.16 标准GIL x64、Windows11 build26300。未在本轮重新运行844产品SDK：这是计划审查，业务/测试/工具字节无变。本轮实际执行scope/archive验证、自有独立数学、具体反例与时间/容量参考、开发参考重执行、发布细节验证。各命令argv/cwd/UTC起止/exit和stdout/stderr原件保存。

| 核验对象 | 独立结果及限制 |
|---|---|
| 本固定SHA/发布链 | 固定checkout干净、merge tree等于已审头、新main/标签同点、旧tag未移；收尾PR已漂移至bd18d1b，另行审查 |
| 需求/冻结 | 106目录/12需求/10MVP2CR匹配；131冻结文件和全部业务目录未变；35计划清单hash通过 |
| 自有数学 | 25候选/70字面答案一致；Fraction精确比较，G22为声明容差；不导入AQRP或开发方checker |
| 开发方封存 | Evidence.zip167126343 bytes；57项精确成员/CRC/每文件hash通过；Fixed-Source.zip3894项与Git固定版本匹配 |
| 合并后P4 SDK原件 | 844/0fail/0error/0skip，complete=true；250选择成员逐hash、53模块wheel与固定代码一致，覆盖/P1八表/终态链/原Ref重放核验；这是开发方执行、主审核原件 |
| 旧20/四/91 | 原始归档日志和记录保持，前一独立G2原件保留；本轮没有另跑这些产品用例 |
| PR8 CI | 初次连接器返回run39807961404 success，收尾同一filtered查询空列表；直接官方run端点核completed/success及head=本SHA。未下载本轮新CI原ZIP，不把API成功写成P5测试或完整工件核验 |

开发外包SHA256：`58149088fd6f1e2ca7b77abfc4226489cae1fe5c06f4d94dc6e742e2f743b789`。P4 merge SDK wheel：`8921e4b45bf66d7a96016596b0e1bf1ab35e709cda4289276ab920b1588b4d74`。旧独立P4 G2包 `08622d6a52dec3b17449b1523d4df744db779e17a22e9e0502e2d05b718d242b` 继续外置保存，不将历史双OS原ZIP算作P5证据。

审查辅助C03初稿raw_open曾写200400.40，随后改为200400.41并添加从raw滑点/tick独立推导到200200.00的断言；初稿脚本/JSON及两次原命令日志保留，最终以design-cases-final为准。未改开发方25个输入/expected，未隐去产品失败。

## 未验证、待用户决定及下一步

P5实现、真实P1→P3→P4→P5两因子替换/账本/重放、产品SDK/双OS原ZIP与输出字节均尚不存在或本轮未执行，保持PLANNED/NOT VERIFIED。当前实际只核计划可实施性，不给G2/阶段验收或StrategyApproved。

P5-D01–D10为新的合成经济候选；技术四项闭环后，用户仍需在后续实现授权中明确接受或修改费用/价格带、交收、行动、short限制、borrow、估值及统计口径。P3 U-002不能充当本阶段交易规则批准。真正金融批准还需另定标准及证据，不能以正收益/统计显著/工程通过代替。

按用户决定，R2真实Windows两项继续DEFERRED / NOT VERIFIED，留待全部开发完成后的最终集成固定SHA统一实际验证；PR7代码修复通过不自动成为P4/P5真实隔离证明。正式Test、金融批准和完整历史宿主边界保持，正式入口APPROVAL_REQUIRED、financial_approval=NONE。不得因本报告重复要求现在启用账户或执行真实验证。

下一步仅修订G1计划/接口/数学候选/测试计划，保留正确原答案及修订依据，提交新完整SHA复核。收尾已观察到bd18d1b候选，但尚未审查；不能因本报告仍列OPEN而断言新候选未修，也不能自动判新候选通过。需要改变冻结P0/P4契约时先列变更影响与批准要求。P5业务实现尚未授权，本次不合并、不打标签、不部署、不实盘、不运行正式Test、不授金融批准、不改账户/ACL/服务/调度、不进入P6。

本目录EVIDENCE.zip封存报告/发现/交接、独立脚本和当前及初稿结果、固定计划及冻结资料、命令/原日志、API/发布链与P4 SDK原字节证据。明确省略venv/cache/完整宿主镜像，开发外包/前轮独立包原位保留并hash绑定。清单逐成员SHA256、外层RECEIPT.json重核大小/hash/CRC；该收据不是数字签名。
