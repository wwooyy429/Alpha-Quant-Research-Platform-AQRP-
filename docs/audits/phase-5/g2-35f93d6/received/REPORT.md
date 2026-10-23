# Phase5 G2 修复候选独立复核

审查者/实际执行者：GPT Work，本会话Codex补充审核。日期：2026-10-23（Asia/Shanghai）。

**固定完整SHA：`35f93d640a2304121131d947a465f57a951cf63f`。整体结论：G2 BLOCKED / REQUEST CHANGES。**

**原WORK-P5-G2-001 High、002 Medium均CLOSED — FIX VERIFIED；新增WORK-P5-G2-003 High OPEN，阻断整体G2。** 原提交后缓存余额错误和开仓方向错误已经确实修复。本报告给两项原修复明确关闭，不用扩展反例改称原错误仍复现。新增003是另外的根因：财务重建只比较现金总额，没有逐桶对账，使不一致的现金可用性仍能被认证为已验证。

本轮完整独立SDK1073通过，双OS官方各1073及原ZIP核验通过；这与新增故障反例并存。原bfdcf30的BLOCKED报告和失败原字节保留，不能回填旧版本通过。用户已授权的十二项工程范围/设计决定保持；本轮不授阶段验收或发布。

## 1. 原发现关闭依据

### WORK-P5-G2-001 · 原High · CLOSED — FIX VERIFIED

原根因是commit文件已发布、内存尚未recover时捕获中断，却封存缓存1000/8条。新`services/backtest.py:_failure_snapshot`重新读取磁盘，`TransactionStore.verified_snapshot`在写锁内取得完整state/records/files，调度观察trace与权威committed-trace分开，原报告缺陷修复。

在**本轮新安装wheel**上，原审查边界脚本仅改固定SHA/新输出路径重新执行，原3组均PASS；原生产探针20PASS/0MISMATCH。另写六组真实公共服务边界检查，未改变字面预定金融答案：

| 实际故障位置 | 异常类型 | 现金/事务/Fill/fee | quantity / remaining capacity | 结果 |
|---|---|---|---|---|
| BEFORE_COMMIT | KeyboardInterrupt、ContractError、RuntimeError | 1000 / 8 / 0 / 0 | 0 / 20 | 三组PASS |
| AFTER_COMMIT | KeyboardInterrupt、ContractError、RuntimeError | 98.1 / 9 / 1 / 1 | 9 / 11 | 三组PASS |

`1000−9×100.1−1=98.1`是预定独立答案；容量是已观察两个10share切片的**剩余**合计20→11，不把used与remaining混淆。实际返回/持久化结果、failed-state、transactions、raw commit、文件hash与权威提交trace相符；普通RuntimeError在记录失败后仍抛出，读取终态结果核对，未伪装正常返回。终态resume被拒且原交易文件不变。原脚本另外直接以子进程os._exit终止，在同一个原服务run_id恢复，前/后提交两组均最终1Fill/fee1/cash98.1，无重复扣费。

链hash损坏、模拟读取PermissionError、重算hash但总现金与Journal相差1的三组扩展控制均FAILED/UNVERIFIED_COMMITTED_STATE，不输出缓存账户。部分发布/已有字节冲突保留的新增SDK用例也实际通过。**关闭仅针对原报告问题，不代表所有财务一致性负控通过；新003另列。** 没有改真实ACL或执行真实隔离测试。

### WORK-P5-G2-002 · 原Medium · CLOSED — FIX VERIFIED

`backtest/ledger.py`现在区分execution_side BUY/SELL与持仓暴露direction LONG/SHORT/MIXED，position_before/after和position_legs明确CLOSE再OPEN。单笔Fill及费用经济计算不重复；未改旧0.5.0.dev1运行。

审查方独立十组空仓BUY/SELL、加多/加空、减仓、全平及两个方向跨零，按成交前头寸和非零价差另算腿的数量、符号、按量精确fee及realized_gross，全部PASS。跨零一Fill/一fee、腿数量/fee/已实现收益和为整笔值，FIFO/平均成本及多空贡献与账户守恒。原公共服务反例现在返回/落盘OPEN LONG，cash98.1，LONG贡献−1.9、SHORT0。正常SDK/官方原始事件中的新腿字段亦经独立重建核对。

关闭证据：CANCELLATION_BOUNDARY_PROBE.json、PRODUCTION_PROBES.json、EXTENDED_REPAIR_CHECKS.json、RAW_FINANCIAL_RECONSTRUCTION.json；原命令/stdout/stderr及`reviewer-production-artifacts.zip`内全部请求、返回、事务、错误与原始run。

## 2. 新增发现

### WORK-P5-G2-003 · High · OPEN · 阻断

**现金桶与原始Journal不一致，只要总额抵消，就仍被标为VERIFIED_COMMITTED_PREFIX，并发布错误的已交收/可用现金。**

主要位置：`src/aqrp/services/backtest.py:43`–`:48`，尤其`:44`仅比较cash_total；相关`:87`–`:89`及验证成功后发布last_committed_account的分支。`_reconciled_account`同时被正常projection和失败快照调用。现条件还把应收/应付合并比较为净值；本轮实际反例证明的是现金桶缺口，不声称已经复现R/P另一例。

新失败快照确实校验了事务hash/状态前后链、总权益和Journal**总现金**，但没有将Journal重建出的cash_set、U_free、U_short逐个与实际账户对账。总现金/权益相同不能证明可用资金相同。

**独立实际服务反例（不是OS隔离攻击）：** 使用已批准合成LONG_SHORT gross0.4/net0输入，初始1000，真实撮合long1@100.1和short1@99.9，各fee1。在short Fill的AFTER_COMMIT故障回调里，保留原始有效commit，向post_state注入“cash_set增加1，原未交收SHORT cashlot减少1”的财务不一致，并按现有格式重算post_hash/commit hash；**Journal完全不动、现金桶均非负、总现金/权益不变**。随后抛ContractError进入真实公共服务的捕获/封存路径。这与现有“重算hash但经济状态不一致应失败关闭”的负控属于同一故障模型，不假称随机比特错误会自行重算hash，也不推定同OS用户具备真实隔离。

| 字段 | 原始Journal及未改金融事件应有值 | 被接受并认证的post账户 |
|---|---:|---:|
| cash_set | 897.9 | **898.9** |
| U_short | 99.9 | **98.9** |
| U_free / S_set | 0 / 0 | 0 / 0 |
| cash_total / equity | 997.8 / 997.8 | 997.8 / 997.8 |
| short margin | 100 | 100 |
| available | **797.9** | **798.9** |
| 验证结论 | 应UNVERIFIED_COMMITTED_STATE | **VERIFIED_COMMITTED_PREFIX** |

服务虽然保持外层FAILED，却给出financial_state_known=true、错误的last_committed_account，并将对应failed-state/transactions封存为已验证。正确的交收应伴随Journal现金科目迁移和short限制所得的相应处理；这里没有任何该事件，不能视为合法交收或P4保守H差异。

第二个较小控制将cash_set从98.1降为97.1并添加U_free1，Journal仍cash_set98.1/U_free0；总额/权益不变，也被错误认证。前者证明可用现金可**多报1**，后者说明并非只针对short类型。没有观察到真实账户资金损失，也没有宣称未损坏的正常运行凭空增加了资金；缺陷是故障后“已验证财务状态”的真实性未达契约。

证据：SHORT_BUCKET_RECONCILIATION_PROBE.json、short_bucket_reconciliation_probe.py及command/stdout/stderr；EXTENDED_REPAIR_CHECKS.json的UNKNOWN_bucket_reclassification。`reviewer-production-artifacts.zip`内short-bucket-reconciliation保留原请求、故障前有效commit、注入后commit、完整返回、failure-recovery/failed-state/Journal/终态链。独立从原始Journal逐行相加得897.9/99.9，不调用生产account/reconcile生成期望。

**修复要求：** `_reconciled_account`须逐金融科目/现金桶核对，至少cash_set、U_free、U_short与Journal各自严格一致，不能只比较其和；应收与应付也应分别按科目符号核对，不以净额抵消代替分账证明。明确保证现金lot与限制所得/交收的关系及非负/子集约束。只有全部适用对账通过，才发布financial_state_known=true和VERIFIED_COMMITTED_PREFIX；不一致时保留原始文件、FAILED+COMMITTED_STATE_UNVERIFIED，不输出已知账户替代未知状态。不得通过取消UNKNOWN负控、把错误bucket当另一种合法模型或改正确原答案来绕过。

必要回归：总现金不变但cash_set↔U_free、cash_set↔U_short、U_free↔U_short重分类，正反方向；有效原始Journal下的合法交收/cover为正控制；原总额差/链坏/读取失败负控、前后提交六组、同原run真实退出恢复均保留。用真实服务/返回/落盘核对，而非只调用一个布尔checker。修复后固定新完整SHA再复核。关联BT-005/007/008、QA-003、INT-002；这是当前P5财务工程缺陷，不能随Windows R2延期。

## 3. 固定身份、范围和原证据保存

起止从PR #8读取AQRP_FIXED_REVIEW_SHA和head均为35f93d6；open/draft/unmerged，无漂移替换。独立detached检出`E:/WORK/AQRP-audits/p5-35f93d6/src`，最终工作树干净。首次shared clone因既有Git alternates嵌套层数限制失败；保留原日志，以非shared打包克隆重新取得对象后fetch官方固定提交，未更改审查对象、源文件或安全检查。

main/phase4-baseline/v0.4.0仍同点`32ea5d6b75c84c07017d87377eeabd2f78207c5c`，旧引用/标签与前轮一致。CI临时merge **`c6eafcb309d5dcefaab6747aa21e6f4f45128a21`**的parents为32ea+35f93d6，整tree **`4eaa9710da4c5f1eef409ed23d4f29f434aac173`**与固定head相同；这不等于获授权合并main。

候选0.5.0.dev2、69模块，bundle **`e383e3f1828ca5d28b3f9daaf2714670af5023aa64c1e908c2ed10466edd0058`**，原Python3.13.16标准GIL64及锁 **`86c7bf65c9a9690036006360062c8cd10a91279705b4070af7033d7699abffeb`**不变。相对bfdcf30只改版本、P5账本输出/事务快照/异常服务、相应准入、回归与参考；未改P4金融源码/因子算法/依赖，未增broker/UI/P6。

原131冻结对象及P4保留3440的并集3451，扣除明确7包装例外后3444旧文件严格匹配；12份已审设计/答案/checker与5262032原字节一致，canonical106/P5十二行（10MVP/2CR）不变。原P5身份另存PRE_REPAIR_IDENTITY并与bfdcf30实际Git原件核对；修复身份旧新hash与实际源码相符。

原独立G2封存ZIP **585712844bytes / `e68d2c5ad5b410b19a85e2159ae63b5a134130a335a6a3d43e3a1c439b542adf`**再次CRC/124成员+manifest/全部size/hash校验；新Git received中81个可比原件与原包逐字节一致，包括原报告、发现、反例及错误余额。原大包仍外部保留并绑定hash，不冒称全部复制入新Git或新封存。开发方容量解释纠正/原失败及CRLF原件照原字节保留，不把缺新元数据的测试失败夸大为多个独立金融缺陷。

## 4. 十二项需求适用复核

| 需求 | 当前实现/适用验证意见 |
|---|---|
| BT-001 MVP | 外层调度、原子80/90、commit trace和恢复仍实际存在；原001六组/进程退出恢复通过，关闭原缓存缺陷 |
| BT-002 MVP | PIT/未来open/历史量发布、原P1/P3身份规则未改；完整SDK原时序/篡改回归通过 |
| BT-003 MVP | 原partial/DAY/GTC/cancel/expiry/幂等保留，捕获前后中断终态主路径修复；不能把新003当原缓存错误未修 |
| BT-004 MVP | 双边价格域、最小费/余费上界、ADV/shared10/双lot保持；独立原探针及SDK通过 |
| BT-005 MVP | 账本正常金额/成本/腿和原始重建通过；新003证明财务验证不完整，阻断 |
| BT-006 CR | split/dividend/pay/T+1/delist/stale既定合成范围未删；完整原回归通过，无真实市场规则批准 |
| BT-007 CR | short所得/margin/borrow/应付实现保留；003未交收short桶可抵消进入cash_set而未被拒，尚不可全面通过 |
| BT-008 MVP | 原002方向修复、返回/落盘/原子子记录一致；003错误已验证可用现金需修复 |
| BT-009 MVP | FIFO/平均成本/多空归因守恒，原数学及实际统计独立重算通过，跨零一Fill/一fee未重复 |
| BT-010 MVP | 本轮真实P1九文件→P3终态→P4→两因子模拟与数值重放已实际执行，固定核心bundle；正常链通过 |
| QA-003 MVP | 原1049+24新增=1073均通过，关键覆盖达标；扩展桶级负控漏检，不能以覆盖率/数量替代003闭环 |
| INT-002 MVP | SDK/CLI同服务/正式入口拒绝/旧Ref/真实输入和终态绑定回归通过；财务报告完整性受003阻断 |

G1四项CLOSED_DESIGN和用户接受/实施授权不变；当前无新增设计口径待用户重批，003所需是落实已批准的独立分账核验。PR7的R3候选6207450未集成进本P4/P5分支，不混报已集成。

## 5. 实际执行与原始工件

本会话真实审查方执行，未使用代理冒名、未补写Gemini。标准CPython3.13.16/GIL开启/AMD64/Windows11 build26300；实际解释器、二进制hash、UTC时间见ENVIRONMENT.json。独立新SDK根：`E:/WORK/AQRP-runs/gpt-p5-35f93d6-20261023/aqrp-e6171f64-5e4a-47c3-b7df-d73eb4d05b2d`。开发本地Anaconda与本轮CPython、官方两个OS分别记录。

| 验证 | 实际结果/界限 |
|---|---|
| 全新干净已安装wheel完整SDK | **1073 passed，0failed/error/skipped**；wheel69源码/准入与固定源码相同，模块行/分支门槛通过；旧Ref及66原始发布文件、旧20+4/91、全部smoke/扫描实际执行 |
| 原审查两份生产脚本 | 原3边界PASS、原20生产探针20PASS/0MISMATCH，含真实进程退出、同原服务run恢复/无重复扣费；仅改新SHA/新物理根，原字面金融答案不变 |
| 本轮独立扩展 | 六组捕获前后×3类异常、三个原未知状态负控、十组腿/费用/价差归因通过；另两种总额抵消的桶重分类MISMATCH，明确为新003，不当作PASS |
| 设计数学 | 审查方标准库参考重新核原25组70项、新25组209项均PASS，另6组2349设计模型情景通过；不是产品测试数，不与1073相加 |
| 实际原始重建 | stdlib另算，不导入AQRP/开发checker：两因子×本轮SDK/开发本地/官方Ubuntu/Windows，240提交、6136精确比较PASS，含新腿字段；恒价开多正常场景明确限定，short/FIFO/actions另有实际probe/SDK覆盖 |
| 收益统计 | 从原始Fill/净值重算累计/MDD、ddof1方差361/600000000、Sharpe/年化（Decimal80，绝对容差1e−12）及费用、多空贡献；正常样本通过不验证被故障注入的错误桶 |
| 新开发包 | Evidence.zip **467565279bytes / `773ab0d9e7485aebd107fbd3f092cdd1a0381fbfb412ba4a1a8b2f0b08bd7134`**；8369项+manifest、CRC/精确成员/全部size/hash通过，Fixed-Source.zip4264跟踪文件逐字节匹配固定checkout |

全部受控命令完整argv/cwd/UTC起止/exit/执行身份保存在`*.command.json`，stdout/stderr同名保留。完整SDK子命令/安装/旧回归输出在原commands.log，审查方选取7229个声明工件+selection原字节封存为independent-sdk-artifacts.zip；它是本轮SDK工件包，不是官方ZIP。反例脚本exit0表示取证结束，JSON中的REPRODUCED_MISMATCH/MISMATCH仍是失败发现，不因程序exit0判通过。

### 官方双OS证据

通过GitHub连接重新读取run39889789530/attempt1的jobs/artifacts，两个job成功；收到的原ZIP与官方API身份/大小/摘要匹配。本轮直接核已有原ZIP，没有重打或冒称再次下载。两个ZIP内各1073零失败/错误/跳过，完整SDK/coverage/wheel69/环境/锁/P1及P5终态链/事务/返回工件核验通过。官方Ubuntu是原始证据验证，不虚报为本会话新Linux执行。

| 官方工件 | API ID | Bytes | 匹配官方SHA256 |
|---|---:|---:|---|
| phase5-ubuntu-24.04-1 | 12474053017 | 165545755 | `58e72f5939650f3b1ce754a8ccedce0ecf0435f34d5f561ea967d4c9bdc09133` |
| phase5-windows-latest-1 | 12473924947 | 124302499 | `4c0b7c37b766e8b8b9931a3ed87ebba52c7af8199245ca63219b31768879e9b1` |

原selection Ubuntu7228、Windows7229，并非原ZIP完整集合：各另有3726个current别名文件/195组。审查方独立程序逐组比较完整suffix/hash子树，全部对应已声明数字目录，没有缺canonical或任意额外字节；完整集合、CRC、去重与所有hash通过。只证明字节等价，不伪造未上传的原symlink目标/权限元数据。

## 6. 处置与未验证边界

- **原001、002关闭；新003 High OPEN，整体G2仍BLOCKED。** 请落实逐桶/逐科目对账及新负控，保留本报告和原始反例，提交新的完整固定SHA供复核；不改旧原件或把本旧SHA补写通过。
- 十二项已获实施授权继续有效，不重复请求启动许可；当前尚未用户验收Phase5，不合并、不打标签、不部署、不实盘、不进入P6，没有给其他Codex会话或GitHub发送评论/审批。
- WI-R2-001/002及整体真实Windows隔离继续**DEFERRED / NOT VERIFIED**，最终集成固定SHA真实验证另行授权。本轮没有启用账户、修改真实ACL/服务/调度；模拟读取异常和故障回调不等于真实权限验证，003也不是延期的OS事项。
- 正式最终Test/金融批准/完整历史宿主复现仍**DEFERRED / NOT VERIFIED**；只核正式入口APPROVAL_REQUIRED拒绝，financial_approval=NONE，无真实正式Test。历史证据限软件包/锁/旧Ref/结果重放，不扩写成完整旧宿主或硬件断电耐久性通过。
- 审查辅助过程首次shared clone深度失败、两项工件验证在SDK未complete时提前启动并正确失败等完整保留；待SDK结束后相同检查通过，区别于新003真实生产反例。详EXECUTION_DISPOSITIONS.json。

完整新封存哈希在同目录RECEIPT.json；该收据是字节完整性记录，不是数字签名、隔离证明、金融批准或阶段验收。
