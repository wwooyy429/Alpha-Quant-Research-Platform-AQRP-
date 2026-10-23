# Phase5 十二项受限工程实现 · 独立 G2 审核

审查执行者：GPT Work / 本会话 Codex 补充审核；日期：2026-10-23（Asia/Shanghai）。

**唯一审查完整 SHA：`bfdcf30e525ff802ea483974f58163eedc029ce8`。结论：G2 BLOCKED / REQUEST CHANGES。**

发现 **1 High、1 Medium，均 OPEN**。High 是已经实际复现的提交后取消/异常封存账户不一致，阻断本轮G2。Medium 是开仓多头被输出为SHORT的成交方向错误，要求同轮修复。完整干净SDK1049通过、官方双OS各1049的原ZIP核验通过，与这些未覆盖反例可以同时成立，不能用总测试数覆盖反例。

此前5262032的G1四项CLOSED_DESIGN保持原历史处置；本轮是新实现缺陷，不改写G1报告，也不把G1通过当作实现通过。用户对C-P5-001、P5-D01–D10及十二项实施的批准已在固定版本 IMPLEMENTATION_AUTHORIZATION.json 记录；本轮无需再次索取实施启动许可。没有任何阶段验收/合并发布/金融批准由本报告自动产生。

## 1. 发现与修复要求

### WORK-P5-G2-001 · High · OPEN · 阻断

**提交文件已生效但内存未刷新时，取消/异常路径封存了旧账户。**

主要位置：`src/aqrp/services/backtest.py:157`–`:163`（尤其158、160、161），相关 `src/aqrp/backtest/transactions.py:111`–`:122`。原run一旦被该路径终态化，`:183`–`:184`又拒绝恢复。

TransactionStore在原子发布commit之后才执行recover刷新`store.state`/`records`。若在这两步之间发生KeyboardInterrupt或异常，异常处理直接使用旧内存state/records发布failed-state、transactions及`last_committed_account`，随后将原run标为CANCELLED/FAILED。该终态和文件hash可以正常通过ExperimentLedger.verify，但封存账户少记了已经持久化的真实成交。

独立使用本轮**干净安装wheel**的真实服务、原子文件操作与工程fixture，在AFTER_COMMIT边界分别注入KeyboardInterrupt及ContractError；不是修改生产期望，不是仅做模型算术，也没有修改原开发证据。真实进程直接退出及同原run恢复的另组检查可以通过，本缺陷发生在**捕获异常后继续发布终态**的组合路径。

| 注入位置/异常 | 服务终态 | 返回/failed-state现金 | 从磁盘有效commit独立恢复现金 | 封存/实际事务数 | 实际已提交Fill/fee |
|---|---|---:|---:|---:|---:|
| BEFORE_COMMIT / KeyboardInterrupt，正控制 | CANCELLED | 1000 | 1000 | 8 / 8 | 0 / 0 |
| AFTER_COMMIT / KeyboardInterrupt，反例 | CANCELLED | **1000** | **98.1** | **8 / 9** | **1 / 1** |
| AFTER_COMMIT / ContractError，反例 | FAILED | **1000** | **98.1** | **8 / 9** | **1 / 1** |

预定算术：初始1000，已提交买入9股，实际价100.1，fee1，现金必为`1000−9×100.1−1=98.1`。磁盘commit-000000000009.json确实包含Fill和该post账户。服务声称的last committed现金1000及8条transactions因此不真实；不能把已提交资金影响当成未提交候选回滚。

证据：`CANCELLATION_BOUNDARY_PROBE.json`、`cancellation-boundary-probe.command.json`及原stdout/stderr；`cancellation_boundary_probe.py`；封存`reviewer-production-artifacts.zip`内cancellation-boundary的三组原run、请求、返回、failed-state、events/manifest、prepared/commit原字节及独立恢复账户。反例脚本以exit0表示取证完成，JSON中明确`REPRODUCED_MISMATCH`，绝非测试PASS。

**修复要求：** 取消/失败终态发布必须以可信的持久化已提交前缀为准，重新核对pre/post状态、完整事务及资金/数量/费用/容量。不能直接封存未确认的缓存，不能删除已经生效commit、覆盖旧失败、虚构回滚，或将不确定账户标成已知last committed。若链本身损坏/不可读取，应保留原证据并失败关闭，明确未知状态，不伪造旧余额。说明原子发布到缓存更新窗口的取消/异常策略，并让终态输出、failed-state、transactions和真实commit前缀一致。

**必要回归：** 同一个真实服务run，提交前/后×KeyboardInterrupt/ContractError/普通异常，另覆盖实际进程退出后resume；逐项核对实际落盘、返回、终态、Fill/fee/容量、事务数及hash。成功路径与原始损坏链负控保留，真正commit后不得再次扣费。修复后新完整SHA交独立复核，不补写本旧SHA通过。

关联需求：BT-001、BT-003、BT-005、BT-008、QA-003、INT-002；违反实现契约“失败/取消保留实际已提交状态”、G1原子/恢复与资金对账要求。**这属于当前P5工程范围，不能随Windows R2延期到最终整合后再决定是否修复。**

### WORK-P5-G2-002 · Medium · OPEN

**从空仓买入的多头成交被标成`direction=SHORT`。**

位置：`src/aqrp/backtest/ledger.py:306`；该行用`oldq>0`判断LONG，其余全部SHORT，因此oldq=0时的纯开多也输出SHORT。

独立公共服务样例实际买入9股，signed_qty=+9、最终持仓+9、entry lot.direction=+1，返回和落盘Fill却为SHORT。相同字段也存在于提供的正常SDK/官方原始工件，不是仅故障注入导致。当前performance按FIFO lots计算，汇总LONG净贡献−1.9和账户总额均正确，**本轮没有观察到该字段导致汇总PnL错误**；缺陷是公开成交/交易方向记录不准确，不能让下游报告按错误字段归类。

证据：`PRODUCTION_PROBES.json`中的`OBS_OPENING_LONG_FILL_DIRECTION`，实际SHORT/独立预定LONG；`reviewer-production-artifacts.zip`内probes/basic-request.json、basic-return.json、原run result/state及Fill；固定ledger源码。其他19条独立检查PASS不关闭这一MISMATCH。

**修复要求：** 明确定义成交方向与开/平仓腿语义，纯开多/纯开空不得误标；跨零一真实Fill同时含关闭旧方向/打开新方向时须明确表示各腿或其他无歧义字段，不能靠旧仓符号给整笔成交误归类，也不能拆出两笔真实Fill而重复费用。如原字段本意只表示已实现平仓腿，应清楚命名、无平仓时为空，并给开仓腿正确记录。更新输出契约/兼容说明，不回填旧实验原件。

必要回归：空仓BUY/SELL、加多/加空、减仓/全平、两方向跨零、真实序列化与返回/落盘一致；保留账户、FIFO与多空汇总净收益守恒。关联BT-005/008/009及QA-003。本轮硬阻断来自001，002应在修复候选一并处置。

## 2. 固定版本、基线、授权与兼容

起止两次从PR #8实际读取描述锁与head，均为bfdcf30；open/draft、未合并，没有用漂移HEAD替代。独立检出目录为`E:/WORK/AQRP-audits/p5-bfdcf30/src`，detached且最终干净。bootstrap实际clone/fetch/checkout命令和输出已记录，没有创建审计分支或PR。

发布基线main/phase4-baseline/v0.4.0仍是`32ea5d6b75c84c07017d87377eeabd2f78207c5c`，旧远端引用/标签与上一轮逐项一致。官方CI执行的是临时merge **`b379a8f34b9d43859daaf4dd98cc46021304e7c0`**，parents依次为32ea+bfdcf30；整tree **`21a9da12d0a8fd69089543b3edd89473087c3719`**与固定head一致。该CI临时merge并非main合并授权，环境中的不同commit字符串完整保留。

候选0.5.0.dev1、69个Python模块；独立校验源码bundle为`ba6b33df82b5142958a2cb6f7aa5a92109241e0f533dd56d436f32fe83358f07`。Python3.13.16标准GIL64位，依赖锁`86c7bf65c9a9690036006360062c8cd10a91279705b4070af7033d7699abffeb`未变，没有新增/升级依赖。回测核心不识别具体因子或Streamlit，没有新DAG、任意插件执行、broker实盘或P6界面。

131个原G1冻结对象中124不变、7个包装/版本/准入/覆盖/CI例外均列明旧新hash；原P4保留3440中3437不变。两表总路径并集3451，扣除明确7例外，当前严格保护3444个不同文件。不是“原131全部原字节不动”的虚报。旧检查工具、P0金融契约、106目录/12行快照、正确答案与原失败报告不改；12份G1设计/答案/checker身份与5262032逐字节一致。

七个例外：pyproject.toml、src/aqrp/__init__.py、tests/environment/test_installation.py、src/aqrp/factors/reviewed_code.json、tools/ci.py、tools/check_coverage.py、.github/workflows/ci.yml。适用SDK/新包身份替代旧P4形态checker的理由明确，旧金融源码/测试/容差未静默重写。准入收据只是工程包内身份/开发审查，不等于独立G2、沙箱或金融批准。

PR7的Windows R3候选6207450未集成进P4/P5分支；两项R2及整体真实隔离继续DEFERRED / NOT VERIFIED。此状态不是新业务缺陷001的延期理由。

## 3. 十二项需求覆盖与适用结论

canonical106不变，P5=BT-001–010、QA-003、INT-002（10MVP/2CR）。实际代码、测试与原始工件已查，未用Planned/Unsupported替代已承诺合成范围；以下样本通过不构成十二项阶段验收。

| 需求 | 实际实现与验证 | 本轮结论 |
|---|---|---|
| BT-001 MVP | engine外层队列/transactions，80/90内层，真实服务和进程恢复、同刻风险/容量 | 正常与直接退出恢复样本通过；捕获中断后终态违反001，未通过 |
| BT-002 MVP | contracts/provider、严格未来open、PIT/原始P3/P1、历史量发布 | SDK时点/晚到/未来mutation及实际链核验通过；限定合成日历，不称真实市场数据验证 |
| BT-003 MVP | model/engine，完整状态、partial、DAY/GTC、取消/到期/幂等 | SDK生命周期通过；001的取消终态资金不真实需修复 |
| BT-004 MVP | 固定双边价格域/滑点tick/每Fill费/ADV/shared10/lot | 字面答案、真实服务及直接函数负控通过；没有临时加费预算/用未来日终量的证据 |
| BT-005 MVP | 精确复式/现金桶/平均成本/FIFO/交收/独立原始重建 | 正常资金/成本/Journal检查通过；001异常资金报告、002成交方向需修复 |
| BT-006 CR | split/ex/pay/T+1/已知回收liquidations、未知delist/stale拒绝 | 适用已定义合成规则和失败样本通过；真实市场税/碎股/部署不在验收范围 |
| BT-007 CR | short限制所得/margin/borrow/股息应付、P4/P5双投影 | 交收前后A899、partial cover、历史借费和应付样本通过；无融资/自动强平为既定边界 |
| BT-008 MVP | 账户/每日持仓/原始风险/订单/Fill报告 | 正常结果及返回/落盘门禁通过；001/002对报告真实性形成明确缺口 |
| BT-009 MVP | metrics，TWR/ddof1/A252/rf0/FIFO/long-short归因 | 设计答案、SDK与独立实际收益统计重算通过；002不能误传给下游方向归类 |
| BT-010 MVP | 真实P1九文件→P3终态→P4服务→两因子完整P5模拟/数值重放 | 本轮SDK实际执行并核原始工件、固定核心bundle及两因子结果；正常链通过，不以声明表替代 |
| QA-003 MVP | 已知答案/边界/性质、独立参考、关键覆盖门槛 | 1049项与覆盖门槛通过，但现有集合漏001/002；需新增有意义回归，不能按数量判全通过 |
| INT-002 MVP | SDK/CLI同服务、真实父UUID/hash/P3/P4终态/返回与发布门禁 | 正常端到端及SDK篡改/拒绝控制通过；服务001使整体G2阻断 |

正式入口为独立APPROVAL_REQUIRED拒绝路径，无skip_approval或工程fallback。SDK内只执行其门禁单元/拒绝smoke，未运行真实正式Test。终态后附加文件不能获得原始证据资格；源/结果别名、父UUID一致篡改、读时换字节、返回/发布篡改等SDK负控已实际运行。不能据此推定同OS用户的role/API对象构成真实主体隔离。

## 4. 实际执行、数学与原始证据

审查方环境：标准CPython3.13.16，GIL开启，Windows11 build26300、AMD64；完整解释器/二进制hash在ENVIRONMENT.json。独立新venv和SDK根在E盘短路径，未复用开发方已安装包或SDK结果，也未改锁/生产源码。开发方本地SDK的Anaconda解释器与本轮标准CPython分别记录，不能混写身份。Ubuntu结果来自核验的官方工件，不虚报为本会话另起Linux宿主执行。

| 本轮实际验证 | 结果及边界 |
|---|---|
| 独立完整干净安装SDK | 1049 passed，0failed/error/skipped；wheel69源码和准入JSON匹配固定源码；逐模块行/分支门槛通过。原Ref/旧20+4/91、完整smoke、独立开发参考工具和扫描均由本轮SDK实际执行，命令/原日志完整保留 |
| 原数学候选 | 审查方Fraction/整数/Decimal90参考重跑原25组70项全部PASS；补充25组209项全部PASS（容差0）；另6组2349设计模型情景PASS。它们不是产品测试，也不与1049相加 |
| 独立实际生产检查 | production_probes.py的19条检查PASS、1条方向MISMATCH；包含short交收、partial cover、FIFO+2.5/−4.5、borrow历史、红利pay一次、跨零分摊、大数输出、partial费界与四类价格域、真实公共服务及数值重放 |
| 真进程退出与原服务run恢复 | BEFORE/AFTER_COMMIT各自子进程os._exit(71)，原run_id由resume_engineering恢复，最终1Fill/fee1/cash98.1，均PASS。另行组合“捕获KeyboardInterrupt/ContractError后封存终态”复现001，不能混称所有崩溃路径已通过 |
| 审查方原始财务重建 | 纯stdlib另写，不导入AQRP或开发checker：从实际Fill/Market/Settlement与Journal重建各提交现金、持仓、成本、借贷/数量平衡、费用和最终权益；正常两因子×审查方SDK/开发本地/Ubuntu/Windows的240条提交，6096精确比较PASS。明确限这些实际恒价开多场景；short/FIFO/actions由其他实际probe/SDK覆盖，不冒称其全部场景已独立重建 |
| 统计独立核验 | 从实际净值/Fill重算累计−0.0019、MDD0.0019、ddof1方差361/600000000、Sharpe及年化（Decimal80，浮点结果绝对容差1e−12），多空贡献/费用一次一致；宽整数/非终止比例精确原值不使用展示值判定 |
| 开发方外置包 | Evidence.zip470436610bytes，SHA256 `b6daf213c8182790ae5a8675efa131727f5a6689520b65f096efe87124b9c594`；10920声明项+manifest、CRC/完整成员集合/每项size/hash通过；Fixed-Source.zip4169跟踪文件与固定checkout逐字节相同 |
| 原始失败/缺省说明 | 首轮路径过长/PyArrow失败、原wheel/环境/log、原CI严格集合失败与后续别名说明、探索期fixture改动/首次错误等已收到并核其封存身份。部分其他探索临时根仍外置、仅按FAILURE_AND_OMISSION_INDEX声明；本轮未逐一遍历未打包的宿主目录，不把它们说成完整SDK固定证据 |

全部受控验证命令的完整argv、cwd、UTC起止、exit和真实执行者在`*.command.json`，原stdout/stderr同名保存。bootstrap含实际Git命令。`independent-sdk`的详细安装/构建/每个子命令在原SDK commands.log；封存`independent-sdk-artifacts.zip`包括6616个upload-selection声明原文件加selection清单，按原字节核验。venv/cache可再生工具目录未冒称包含为完整历史宿主。

### 官方双OS原始ZIP

从GitHub连接重新读取run/jobs/artifact身份、大小和摘要，与收到的**原ZIP字节**逐项匹配；本轮未重复下载同一ZIP，绝未重打后当官方原包。run39839529359/attempt1，两job success。官方环境实际执行临时merge b379a8f，整tree/parents已独立核对。

| 官方工件 | Artifact ID | 原ZIP字节 | 匹配官方SHA256 |
|---|---:|---:|---|
| phase5-ubuntu-24.04-1 | 12453360470 | 163229282 | `3187bd976370d5b06bb7895c38c23d52c37dc91f36771e4723bc686f50d7f644` |
| phase5-windows-latest-1 | 12451929998 | 121985327 | `96d87b6be97bcf44ac2f64203a44a6fb31ceed797058cb44e53f48aa32257e35` |

两个ZIP均CRC/精确去重成员检查、原upload-selection所有hash、JUnit各1049零失败/错/跳、wheel69源码/准入、依赖锁/环境、关键模块覆盖、P5终态事件链/文件/真实返回值与事务清单检查通过。

每包的原selection6616条加selection自身不等于官方包10046成员，尚多3429文件。审查方**另写**完整子树匹配程序验证189个pytest current别名组的每个suffix/hash与至少一个已声明数字目录完整一致，无缺canonical文件或任意额外字节。只证明字节等价，不推断原symlink目标身份/权限元数据。原上传行为/首次严格检查失败不隐藏。Ubuntu/Windows原参考文本换行差异不改变ZIP原字节，本轮未靠规范化或重排JSON去匹配原工件hash。

## 5. 未验证、处置与权限边界

- 本轮正式结论为**G2 BLOCKED / REQUEST CHANGES**，两项OPEN。适用正常样本通过不能关闭001；没有授权放宽既有P4保守风险或删除正确原答案。请开发方按上述要求修复并提交**新的完整固定SHA**，原失败证据与旧标签保留。
- 十二项实施授权保持原有效范围，修复不需要再次取得启动许可；但用户尚未验收Phase5。本报告不合并、不打标签、不发布、不部署、不实盘、不进入P6，没有发送GitHub审批/评论或向其他Codex会话发消息。
- WI-R2-001/002及整体真实Windows三主体隔离仍**DEFERRED / NOT VERIFIED**，按既定最终集成固定SHA与另行执行授权处理。没有启用账户、修改/探测真实ACL、服务或调度器。本轮同OS工程进程/哈希测试不能代替真实隔离。
- 正式最终Test、金融批准与完整历史宿主复现仍**DEFERRED / NOT VERIFIED**。正式入口只核拒绝，financial_approval=NONE；软件包/锁/旧Ref及结果重放不能改名完整旧宿主。
- 未验证硬件断电、远程文件系统耐久性或真实市场/券商规则；不把这些延期项扩大为现工程已通过。已批准合成范围内的正常功能不因这些限制被静默删除。
- 本轮审查辅助脚本的初始计数/空模块覆盖断言错误及一次shell引号错误单独登记，原日志保留。它们不是开发方产品缺陷；修正辅助脚本后再执行。相对地，001/002是实际生产反例，未因SDK通过改判。

审查方完整报告、发现JSON、可转交说明及原始命令/环境/SDK/反例/官方原包绑定已封存，收据见同目录RECEIPT.json。封存哈希是字节完整性记录，不是数字签名、可信OS隔离或金融批准。
