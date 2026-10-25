# WORK-P7-G1-002 修订候选：真实浏览器负例及独立预算账

仅设计候选，未运行产品、worker、服务器或浏览器；未关闭独立发现。依据固定计划 3c34e3ca75c9799307b8a98b34f045b40988bbca 的源码静态阅读。原主协议 12 个研究准入、全部正确答案、19/10 截面、768 路径均不改。

## 两套目的及账本先登记，不能事后补数

1. **主协议 MAIN-12**：同一受信工程 workspace、同一原 P1 数据身份、一个预登记 campaign；原 SDK/TaskCLI/AppTest/真实浏览器两因子各 2 + 旧研究 CLI 2 + 透明 SDK 2，合计 12 个研究假设单位。失败、取消仍消耗，不退款、不新建 family，不临时换根补齐成功数。原成功 actor 必须各自真实运行，不能用 replay 替代研究 actor。
2. **原故障回归夹具 ORIGINAL-P6-RISK-1**：实施前、主协议开始前，在不可变协议 manifest 中一次登记的独立原 P6 故障夹具；来源是 `tests/ui/test_task_core.py::test_legitimate_risk_rejection_is_task_failure_with_original_p5_result`，另有 `test_view_interactions.py` 原同类风险展示覆盖。不是 MAIN-12 的第 13 次运行，也不扩展主研究成功数。夹具沿用原 SYN_U 公开合成配方/原 P6 风险断言和受审精确 runtime Ref，独立 workspace_id、purpose、campaign、ledger_root 及各自实际数据身份明确写入证据；同源配方不能自动推定不同初始化的 snapshot_id/manifest/data_hash 相等；这个根不是发生失败后临时换的根。仅用于证明合法金融风险门禁与 UI 原件链，不用于因子筛选、收益/参数优化、统计独立性或正式金融证据。
3. 两个根与目的、适用数据 hash、预登记请求、选定解释器、包/锁/源码身份须在看到任何本轮结果前同时冻结。不得仅靠路径名称或操作者自述区别。统一可信准入设计须绑定已审 fixture-purpose/固定根/精确数据身份，并将该故障夹具的**协议分配硬上限冻结为 1 个研究 attempt**（总产品预算 12 的原常量不改）。这个 1-slot 不是允许失败后重建夹具/新 family 的权利。超限拒绝且原失败不可覆盖；若统一准入未能强制这个单次分配，不能宣称该设计已落实。
4. 外层总表必须分列 MAIN-12 研究 consumed=12、原故障夹具 consumed=1、既有完整 SDK 的各原隔离测试夹具，以及 replay consumed=0。不得把整个测试套件所有临时根合成一个“共用 12”结论，也不能声称故障夹具不产生研究。

## 物理输入根、来源及独立初始化约束

MAIN-12 使用唯一 canonical workspace **W**；原故障夹具使用实施前已登记的 canonical workspace **Wneg**。共同预算 resolver 的一项强制条件是请求输入和研究输出均归属于该次唯一受管 workspace：风险夹具的 snapshot、exposures、coverage、catalog、campaign、admission 及 research/backtest 输出必须全部绑定 Wneg 自己受管的根，不能让 `W/inputs/...` 的物理 P1 输入与 `Wneg/research-runs` 输出配对。真实路径与可信祖先链检查不因只读输入而豁免，不能用 junction/symlink/路径字符串或手改 catalog 绕过。

首选在任何结果之前，可信初始化按原 P6 `_engineering_inputs` / `initialize` 故障夹具流程，把同源 SYN_U 合成工程输入生成并发布在 `Wneg/inputs/source`、`Wneg/inputs/pools`、`Wneg/inputs/pool-exposures`，coverage 绑定 Wneg 的实际 snapshot manifest，catalog 的所有输入 root 与 workspace_id 绑定 Wneg，原 P1 私有临时目录语义保持。此处只设计将来的初始化及普通工程文件发布，不授权账户、ACL 或部署操作。W 的原输入、catalog、manifest、admission 和原始成功协议不改。

若受审的可信发布流程允许复用原文件，则必须在预登记时确定来源，按完整成员/原字节/实际 manifest 与 ID 验证后，把允许复用的输入放到 Wneg 自己的受管输入根；不能仅将 Wneg 的 catalog 指向 W 的物理路径，也不能通过改 snapshot_id、时间或 manifest 原件强凑身份相等。是否能够逐字节复用、目录引用/元数据应如何发布，须由真实格式验证决定，不预先声称复用已验证。

正常重建可能产生新的 snapshot_id、manifest_hash、exposure/coverage 身份或实际 canonical data_hash。必须如实记录 W 与 Wneg 各自实际值及来源对应表，分别核验格式/内容/来源/单位/时间语义；只有经原字节独立核验相同的成员才能标 `bytes_equal=true`，只有实际 digest 相等才标 hash 相等，不能预填未来 UUID/hash 或重写旧原件。两根仍只来自同一公开 SYN 配方，绝无金融样本独立性或新市场信息声明。共同 authority 以各自实际 canonical data 身份计数，fixture-purpose/根/1-slot 资格来自先登记的受信执行计划，不能仅因为数据 hash 不同就任意生成新的负例命名空间。

在看到任何本轮结果前，同时冻结 W/Wneg 的 canonical real paths、各自 catalog/source/input manifests、实际数据/依赖标识、固定来源配方 SHA、campaign/variant/目的及限额收据；原先写过“同数据 hash”的说法只可表示已实际核验的相等，不是创建 Wneg 的强制预设。禁止发生 MAIN-12 额度耗尽/失败之后再复制 W 输入创建新 Wneg，以补主协议研究或成功数。

**必需拒绝控制 ROOT-MIX-01**：以 MAIN W 的真实 snapshot/exposures 路径、对应原数据身份，配上 Wneg 的研究输出/预算根。共同 resolver 必须在研究准入和新 trial/run 之前拒绝；W 与 Wneg admission/trial/原件/计数完全不变。反向 Wneg 输入配 W 输出也拒绝。Task catalog 路径的原守门错误可为已有 `CATALOG_INPUT_OUTSIDE_WORKSPACE`；共享 legacy resolver 的最终明确错误码按独立审过的准入设计冻结，不能编造本轮实际执行结果。还须测试跨根别名/链接不能绕过；合法 Wneg 所有输入/输出同根的正控制必须到真实 P4 风险拒绝，不能用这项边界拒绝代替 BR-RISK-ORIGINAL-01。

## BR-RISK-ORIGINAL-01：浏览器真正提交并执行合法风险拒绝

**先决**：固定的 ORIGINAL-P6-RISK-1 根，默认配置 revision=0/payload={}；没有既有研究 trial、没有已占用 admission。唯一 campaign `p7-original-risk-1` 在首次显示结果前冻结完整研究 variant；campaign、Wneg 自己的实际 canonical data 身份、runtime Ref/参数的 canonical bytes 与 hashes 进入 preregistration。原 global 12 控制仍生效，额外受信协议分配仅允许这一个研究 attempt。

真实浏览器访问该预登记夹具的本机受控 Streamlit 实例，进入 **Strategy Backtest**，表单逐字段输入：

```json
{
  "kind": "engineering_pipeline",
  "factor_ids": ["momentum"],
  "universe_id": "SYN_U",
  "campaign_id": "p7-original-risk-1",
  "start": "2024-01-06",
  "end": "2024-01-06",
  "lookback": 2,
  "horizons": [1],
  "neutralize": true,
  "weights_percent": {"momentum": "100"},
  "initial_cash": "1000",
  "fee_budget": "10",
  "policy": {"top_k": 1},
  "constraints": {"gross_max": "0"}
}
```

方向控件选 +1；当 defaults 不含 direction 时，现 UI 原始 draft 会省略 direction 字段，effective research config 的方向仍精确为 +1。不得把字段差异掩成完全相同 raw bytes：记录实际 UI draft、冻结 effective request、catalog/default revision/commit/bundle/锁/环境的全部原字节及 hash。`gross_max=0` 放在现成 **Risk overrides (existing schema)** 文本框；不需要新增 UI 风险字段或更改 defaults。单击现成 **Submit engineering pipeline**：现代码 freeze→submit→start_worker，真实浏览器必须造成该链的实际执行，而不是只看 SDK 预造的失败截图。

预期分层终态：

| 对象 | 原契约下的预期 |
|---|---|
| admission/trial | 允许且消耗 1 单位；不是 EXPERIMENT_BUDGET_EXCEEDED；失败不退款 |
| P3 / R | 真实研究 SUCCEEDED；一条真实研究 trial；R slot VERIFIED_SUCCESS；financial_approval=NONE |
| P4 / P:0 | 真实候选及风险门禁运行；result.status=REJECTED；risk.passed=false，GROSS 高界 0 且实际正暴露导致检查失败；原 P4 ledger manifest.status=FAILED，slot VERIFIED_FAILURE；不能只有 invalid input/字段错误 |
| P5 / B | 原 result.status=SUCCEEDED，B slot VERIFIED_SUCCESS；原始 portfolio-lineage 包含该实际 P4 run；fills=[]，现金及权益 1000，所有资产 quantity=0（保留原资产映射及估值字段，不能断言 positions={}）；P4 拒绝没有下订单 |
| 整 Task | FAILED，error=REQUIRED_STAGE_REJECTED；不能因 B 成功提升为任务成功，不能显示为取消或预算拒绝；保留全部原始失败及子结果 |

上述现金/权益是无订单、无持仓、无费用的独立算术。精确每个 GROSS 数值及其他风险检查随受审 P3 输出/原 P4 运算记录核对；不从待测产品首次结果生成新的 expected。原代码及原已审断言已经规定 cash_total=1000、fills=[]、P4 REJECTED、Task FAILED，保持原答案。

浏览器选 Task 和 P:0，实际下载并哈希 `risk.json`、`result.json`；选 B 下载原 `result.json`、`portfolio-lineage.json`/交易文件目录原件（后者由可信只读采集导出），保留 R 原件。AX/截图必须能绑定同一 task_id、R/B/P:0 run_id；worker argv/pid/解释器/启动结束/退出码与安装包身份均记录。不同实例使用独立、显式标识 URL/端口及 workspace 映射，不能把它说成 MAIN-12 的浏览器成功运行。

## BR-CANCEL-REPLAY-01：主协议根内，零新增研究的真实浏览器取消

**源**：MAIN-12 中预指定的成功 Momentum 主层 Task（实际 UUID 由该 actor 执行后写入只增映射，不按收益择优），经 status/proofs 全链验证有 backtest_run_id。源默认、原 B 请求/数据/Ref/环境/所有原件 hash 已固定。

可信 SDK 只执行现成 `freeze({"kind":"replay","source_task":<source_task_id>})` 和 `submit(..., "p7-browser-cancel-replay-01")`，**不执行 work 或 start_worker**。这是计划内队列准备，不假称浏览器完成提交。新 Task 为 QUEUED、slots={}，request.payload.profile=P5_NUMERICAL，无 campaign/research；队列准备前后 admission/trial 数必须精确不变。没有通用自动 poll/dispatcher；原 UI inspect/Refresh 只读取，不启动 QUEUED worker。登记任何后台 worker/调度若存在即不满足本案例前提，失败后不能重试挑一张取消截图。

真实浏览器在 MAIN-12 原实例 **Experiment Manager** 选这个精确 Task，确认 QUEUED 后点击 **Cancel safely**。现 `TaskState.cancel` 原子设置 cancel=1 与 status=CANCELLED，追加 CANCEL_REQUESTED；屏幕重新读取状态。预期 Task CANCELLED/cancel_requested=true/slots={}，P3、P4、B、E 均没有创建、没有现金变化、没有 source mutation、没有新的 campaign_attempt/trial。此案例仅覆盖真实排队取消，不声称运行中/提交后取消已被本次浏览器验证；后两类保留完整 SDK 原资金/故障回归。

取消后可信命令对同一 task 调用实际 worker CLI `work`：现 `TaskService.work` 对 terminal 直接返回 CANCELLED，不能创建任何 child。`start_worker` 对非 QUEUED 原样返回 ALREADY_SUBMITTED，也应记录但不能替代真实 work 无执行控制。保留前后 Task SQLite 只读快照/事件链、全部目录清单、trial/admission 清单和源工件哈希。相同 idempotency_key 再 submit 仅返回同一已取消 task，不退款或新建；改请求同 key 必须拒绝。

## BR-REPLAY-01：主协议根内，零新增研究的真实浏览器正常重放

在同一个已成功源 Task 上点击现成 **Replay verified P5 result**。该点击走 freeze/replay→submit→start_worker；记录浏览器真正造成的 request/task/worker 身份。新的 replay Task 不带 campaign/research config，不登记新研究 admission/trial；调用原 P5_NUMERICAL 受信只读 source，重算原冻结 B 请求，不能重新运行 P3 或改 selection。

主层源有十个决策，预期 replay 的 E 与十个 P:i 在各自新可信所有权中完成，Task SUCCEEDED，result.replay.status=NUMERICAL_REPLAY_VERIFIED；comparison.json expected/actual/equal=true；同原 source 的 declared numeric projection 相等；source 原字节及主协议 12 单位计数保持不变。重放产生新的执行/portfolio run 和事务，不能称零运行，且不增加主成功 actor 的研究数量。新 package 与源必须同受审固定 implementation；跨 bundle 原宿主恢复不在这个案例承诺内。

## 必需证据及未满足时的处置

- 实施前不可变主/负例登记 manifest、W/Wneg 自己的受管输入与输出真实根、各自实际数据身份及同源/成员字节对应证明、目的/campaign/variant/attempt allocation 哈希及三案例的准确 raw/effective request 或模板；runtime UUID 仅填入预指定 actor 的执行身份，无事后自由选源。
- 三案例执行前/后 admission ledger、trial chain、Task SQLite、events、目录清单、source/request/slots/resolved-plan/completion 及原 P3/P4/B/E 账本原件。每个 file 的相对路径/长度/SHA256，采集者/命令/UTC/退出码齐全；清单自身和外层 ZIP hash 分列。
- 真实浏览器完整 AX/截图/操作记录、任务页下载原件及实际下载原字节哈希；AppTest/SDK 不冒充 browser；含风险拒绝、排队取消、正常 replay 三种实际终态，而非第十三次额度拒绝。
- 既有 SDK 原提交后取消/损坏现金拒绝/三桶与 backing 对账全部回归；新 protocol cap=1、零研究 replay、源不可改、混合统一准入均需实现测试，不能拿设计表当通过。
- 若任一入口新增研究、fixture 根或目的不匹配、cap 无法硬执行、未到真实 P4、worker 偷跑造成取消竞态、源在过程中变化、或正式 Test/金融入口可达，记录原失败并阻断该设计/实现证据；不换根补成功，不删失败，不增加 12 上限。

源码位置：`ui/app.py::submit_page` 315–352 风险控件/提交；`inspect_task` 90–105 取消；Experiment Manager 552–563 replay；`services/task_requests.py::freeze_request` 329–389 区分 replay 无 research/campaign；`services/task_state.py::submit` 106–149、`cancel` 278–289；`services/tasks.py::_replay` 794起、`work` 606起、`_proofs` 323起；`services/task_worker.py::start_worker` 10起；`portfolio/service.py::construct_engineering` 54–110；`risk/checks.py::assess` GROSS；`backtest/engine.py::_risk_portfolio` 328–370；`backtest/provider.py::verify_portfolio_result` 191–230；原 `tests/ui/test_task_core.py` 158、171 与 `test_view_interactions.py` 81。
