# P7 共同预算准入修订建议 · WORK-P7-G1-001

本文件是开发方的 **设计修订建议**，没有实现或运行产品研究、任务、浏览器、故障探针。固定原审 SHA 为 `3c34e3ca75c9799307b8a98b34f045b40988bbca`。原 P6 产品的反例是 P7 跨入口设计必须覆盖的事实；不反向改变 P6 已验收受限范围。001 仍由 GPT Work 在新固定 SHA 上判断，不能由本建议自行关闭。

## 1. 权威与作用域

未来同一个 P7 包中的 Task SDK、task CLI、Streamlit、adapter、旧 research CLI、公共 `research()` 和 `ExperimentLedger.register_trial()`，必须先做同一个强制域解析；凡源或输出属于受管W，一律经过同一个 **强制预算准入**。`task_context=None`、省略 receipt、换 family、换 campaign、改配置或改 adapter ID 都不能选择原来的无共同计数分支。完全非受管standalone兼容例外仅按第2节原物理边界判断，不能由caller勾选。

建议新增 `src/aqrp/experiments/admission.py`，建立纯标准库的 `BudgetAuthority`。**工程 workspace 的唯一计数权威放在原 `W/task-control/tasks.sqlite` 的新增版本化表中**，而不是再建立一套预算数据库。Task 提交与额度预留在同一个已有 SQLite `BEGIN IMMEDIATE` / `synchronous=FULL` 事务提交。研究 `trials.jsonl`、Task 的 campaign-attempt 文件、run 事件、manifest 和 JSON sidecar 均是可核的原始记录或投影；不以任何单独 JSONL 的长度覆盖 SQLite 已提交预留。

计数键为 `(workspace_id, canonical snapshot manifest_hash)`。exposure/coverage/catalogue/variant/Ref/入口/family/campaign 等绑定进请求和污染记录，但不得换成新的额度命名空间。相同物理 workspace 和同一数据快照总额度仍为 **12 个 candidate × horizon（含 composite）单位**。family 原来的更小预算仍需同时遵守，不能只检查共享 12 而放宽原 family 子预算。

**预算约束不是 OS 沙箱。** 当前只承诺包内所有正式公共入口在完整历史和受信工程文件边界下遵守该权威；不声称能够对抗有权限删除/修改全部控制状态的宿主管理员。真实 Windows 权限验证仍延期、未验证。

## 2. 不可由调用者选择的 workspace 解析

`resolve_admission_domain(output_root, config, lineage, snapshot_ref, exposure_ref)` 是公共服务与 ledger 共用的唯一解析器，结果不能由可选 token、网页字段、caller-supplied workspace UUID 或 family 内容覆盖。

1. 对 output、原始 snapshot/exposure 物理根逐级检查受信 `catalog.json` / workspace anchor 与现有 `tasks.sqlite.workspace`；保持原 `guard_path` 对 symlink、junction、hardlink 的拒绝，禁止多个嵌套/冲突 anchor。输入与输出必须指向同一唯一域。
2. 输入属于 Task workspace `W` 时，无 TaskContext 的旧 CLI/SDK 自动绑定到 `W` 的同一 authority；旧签名和 CLI 参数不需要新增用户令牌。P7 协议中的旧入口固定输出到 `W/research-runs`。同一受管输入配 `--output W/other`、外部输出、新的局部 authority、不同 workspace UUID，必须拒绝 `ADMISSION_DOMAIN_CONFLICT`，不能另计一份预算。
3. `ExperimentLedger.register_trial()` 不能仅依赖 `_research()` 提供检查结果。它必须独立从已封存 run config/lineage 及原始输入 binding 解析 authority，查完整 run admission；调用者只提供字符串 receipt、伪造 campaign_control、漏 TaskContext 或直接调用 ledger 都不能跳过。
4. 原 P3 standalone 的输出与原始输入均不属于任何受管 Task workspace 时，保留真实公共 API 原来的 family/budget 参数和原语义（budget 可以不是12），使用其原 ledger/family 控制，**不虚构一个 Task workspace、不强行改成12、也不把它当作 P7 共同预算已经治理的证据**。输入或输出任一属于受管 W 时不允许回退 standalone。域判断依物理边界/受信catalog，不能以 caller 不传 campaign/budget/family/TaskContext 或声明 purpose=standalone 来回退。若 lineage/config/路径相互矛盾或处于受管域但缺少足以确认唯一域的绑定，失败关闭，不自动归为全新域。
5. P7 工程协议冻结唯一 W、catalogue、data hash、所有入口及其输出根，并先核所有输入来源。运行失败不允许换 W 或复制数据创建新 hash 后继续本轮统计。整个新 workspace 确实是新实验而非预算重试时，应另行登记新实验与污染关系，不能作为本轮成功补数。

## 3. 事务结构与准入凭证

候选 schema `common-research-admission/1` 至少包含以下新增表，均在同一 `tasks.sqlite`：

| 表 | 必须字段/约束 |
|---|---|
| `budget_domains` | workspace_id、data_hash、limit=12、schema_version、catalogue/source anchor 哈希、历史导入根、migration_state；域键唯一 |
| `admissions` | admission_id、domain、owner_kind=`TASK`/`LEGACY`、owner_id、idempotency_key、request_hash、完整 units definition/hash、units_count、decision=`ADMITTED`/`REJECTED`、prior_debit、debit、immutable payload/hash、monotonic seq；owner+idempotency 唯一 |
| `admission_units` | admission_id、unit_ordinal、hypothesis_alias、definition_hash、status；每个单位不可重用；UNIQUE(admission_id, ordinal) |
| `trial_claims` | admission_id、unit_ordinal、physical ledger root、run_id、config_hash、lineage_hash、claim payload/hash、projection state；同一单位只能绑定一个合法 run/hypothesis |
| `admission_outbox` | 权威已提交后必须发布的 Task/legacy sidecar、run/TRIAL 事件内容及 hash、精确相对路径、materialized marker；payload 在事务中冻结 |
| `admission_events` | seq、previous_hash、kind、payload/hash；准入/拒绝/认领/恢复/完整性错误都可追踪，不删除/重写失败 |
| `execution_plans` | 受信workspace anchor绑定的唯一不可变plan_hash/purpose/actor清单，source/data/catalogue/code/profile哈希和严格子约束；caller不能替换/省略来绕过 |
| `execution_plan_slots` | `(plan_hash, actor_slot)` 唯一；fixed service/canonical_request_hash/output_root/source_ref、requested research units、grant capacity/max_admitted_owners、首次绑定的client key/owner；UI随机key不预写，legacy内部key由slot派生；不能以slot名称另建预算域 |
| `execution_plan_activations` | 受信runner按冻结顺序CAS激活的slot/有限并发组、activation_seq、epoch、launcher/code/hash/物理W启动收据、状态；页面没有写此表的服务API |

`debit` 只在 `ADMITTED` 时为 N，拒绝为 0，任何已准入 debit 没有退款更新或负 debit。`SUM(debit) <= 12` 是共享硬上限；单独记录 `requested_units`、`admitted_units`、`rejected_units`、`registered_trials` 和 `executed_trials`，不把第 13 次拒绝当成第 13 次实际执行。原 P6 超额申请保留的 `campaign_attempts.units` 不删除；导入时保留其历史计数字面值和 `over_budget`，与新 admitted debit 分栏报告，不能事后假称原申请不存在。

Task 准入：冻结/核对 request 和 campaign → 同一 SQLite 事务中校验完整历史、幂等 key、总量及 family 条件 → 创建 Task + 全 N 单位 admission + outbox + Task 事件 → COMMIT。超额则提交 `REJECTED` 审计记录、终态 FAILED 和 `EXPERIMENT_BUDGET_EXCEEDED`，**不启动 R/P4/B**。当前没有用去掉 Task 预留来迁就旧 CLI 的选项。

Legacy 准入：`_research()` 完成不读研究结果的 schema、snapshot 原始身份、hypothesis 定义校验，先根据受管plan中唯一当前slot查原owner；**已绑定时先核对并恢复原run或显式拒绝，不先分配新UUID**。首次绑定才分配不可变run ID，并在同一事务一次性准入该run完整N个候选×期限。不能边跑边只登记最有利的候选。然后每个 `register_trial()` 认领已经准入的单位并投影原trials/event记录；直接 legacy `register_trial()` 没有预准入时，必须在该调用中根据整份冻结config推导完整N后经过相同slot/owner准入，不能只计调用者传来的一个hypothesis。任何权威/配置/来源不完整均拒绝，不能以budget参数自行建域。非plan的独立预算回归场景可使用其新run_id作为新试验身份，见第4节限定。

所有研究数据读取、FactorEngine 调用、拟合/评估、缓存结果读取必须在准入和绑定验证之后。读取 snapshot 原始 schema/hash 验证不等于读取或观察研究结果；原始输入校验失败且从未准入，不伪称已执行试验。准入之后的异常、取消、worker 崩溃、风险拒绝、无成交和发布失败均不退款。

`BudgetAuthority` 位于 experiments 层，不能从 `ExperimentLedger` 反向导入 services.TaskState 造成模块循环；TaskState 通过传入同一个 SQLite connection 调用 authority 的事务体，legacy由同一底层connection/交易管理器接入。共同SQLite不是调用TaskService包一层后再另开DB事务；事务和锁的持有权由入口明确传递。

## 3A. 可信执行计划及风险/取消预算安排

P7 E2E工作区初始化时，由受信执行计划在观察任何结果前冻结唯一 plan 与 slots；输入anchor、exact plan hash与authority一致，客户端不能新增另一份 plan、不传 token 降级、修改 purpose 或用新 family 补 slot。**purpose 与 plan 仅是同一 W/data 预算之上的更严格约束，不是额度scope键。** 所有Task/旧CLI/direct ledger仍先进行域识别，在同一SQLite事务校验 exact slot 和共享计数。

- 主 `MAIN_SUCCESS` 计划保持原 **12个 charged slots / 12 research units**：每个slot精确绑定服务、canonical request、输出根、数据/Ref/profile身份；UI客户端随机key在首次提交时原子绑定一次，不能在计划前伪造一个尚未生成的key。失败保留原slot/admission，不能给失败slot换配置/换key/另起workspace补足成功。除此可有明确零研究的 replay slots；**slot行数不等于research units**，不能用“超过12行所以一定超额”或“声明0所以免费研究”判断。
- 风险负例使用与主成功actor事前区分的故障夹具，其 W、purpose、原始数据/catalogue/Ref及配置在观察结果前单独冻结；不是主运行失败后临时换workspace，也不能用其成功增加主12成功数。产品共享上限依旧12，夹具计划只含 **1个 charged slot / 1 unit / max_admitted_owners=1** 作为更严格子约束。固定真实浏览器工程pipeline、`gross_max=0`、其他经济/执行配置的完整canonical request hash和输出根；首次真实UI提交时才绑定其实际随机key/Task_id。第二个不同key或配置即使尚剩11个产品额度也以slot已用/身份冲突拒绝；exact retry仅恢复原owner、不退款、不产生第二次研究。必须核原P3成功、P4 `REJECTED/GROSS`、B成功且无fills/cash1000、Task `FAILED/REQUIRED_STAGE_REJECTED`，**不能用第13次预算拒绝替代风险拒绝**。
- 取消负例在主W选择已核成功Task作为固定source，**SDK只创建并提交queued replay Task，真实浏览器选择该任务并点击 Cancel safely**；不能写成浏览器提交了该Task。其slot是一个预冻结的复合actor（允许操作仅SDK enqueue→browser cancel，不启动worker），严格绑定原replay schema/固定source引用和hash、SDK固定幂等key、**0 research units、无R slot**。SDK入队与浏览器取消之间保持同一activation，不需要把QUEUED任务误判成上一actor已终态再推进。取消后source请求/账本/hash不变，新Task `CANCELLED`仍需原财务可知性门禁；出现账本不完整不能为了满足终态而写CANCELLED。以research/pipeline替换replay、变更source、任意声明units0都拒绝。这个零新研究路径不能变成“免费评估一次P3”。
- actor slot准入身份没有新的用户可选逃逸字段。同canonical请求的SDK、task CLI、AppTest、真实浏览器actor靠受信runner事先冻结顺序、每次只激活对应slot来唯一确定，**不靠页面caller自报entry/purpose或随机key挑选空slot**。服务/ledger按authority当前activation、固定服务请求和物理输出读取唯一slot；UI随机key仅绑定owner，不授予选择slot的权限。
- 旧 research CLI 原本没有idempotency参数。它在分配run_id前，按当前唯一激活的legacy slot、服务种类、canonical请求hash和固定物理输出根解析，内部key为`digest(plan_hash, slot_id)`。已有绑定时只恢复原owner或显式拒绝重复；首次事务才分配并绑定实际run_id。不同请求、过期activation或无法唯一匹配则拒绝并保留原失败，不自动挑别的空slot。入口标签不是独立安全凭证；真正CLI进程和真实浏览器操作链仍由原始证据证明。

## 3B. 可信actor激活API、具体接线与错误顺序

以下是拟实施的包内工程控制API，**不是现有实现或新增真实权限授权**：

1. `open_protocol_driver(W, expected_plan_hash, execution_identity) -> PlanAuthority`：仅新增固定工程runner `tools/p7_engineering_protocol.py` 调用；核已经冻结在W anchor中的plan文件/hash、实际包code/bundle、该runner source hash、只读输入/允许根及当前activation账。返回内部seal构造的非序列化对象，不由浏览器JSON、URL、query参数、任意UI表单或客户端字符串构造。
2. `advance_actor(plan_authority, expected_activation_seq) -> ActivationReceipt`：同一SQLite事务CAS；**无caller提供的slot/purpose参数**，从冻结的actor顺序确定下一slot。要求前一actor已经原始终态验证或冻结的预期拒绝已经记录，不能在失败后换slot配置、跳到同canonical的另一个actor来补成功。生成activation_id/epoch、唯一slot/有限并发组、允许服务、canonical请求、输出、launcher/code/root收据。正常E2E顺序一次只激活一个actor。
3. `bind_current_actor(W, service_kind, canonical_request_hash, physical_output_root, client_key=None, connection=...) -> ActorBinding`：Task/旧research/ledger的强制内部调用，**无可由用户指定的slot**。在同一事务读取唯一active slot、验证固定请求/根/units，首次绑定客户端key/Task_id或派生legacy key/run_id，已有exact key和请求则复用原owner；不同key命中已绑定slot拒绝`EXECUTION_PLAN_SLOT_EXHAUSTED`，同key请求改变拒绝`ADMISSION_IDEMPOTENCY_CONFLICT`。service_kind由各正式服务代码常量给出，仅是协议类型校验，不能把它当作真正OS主体身份。
4. Streamlit启动接线只读取可信本地启动配置中的W，从authority捕获当前activation。固定UI `TaskService`实例和后续submit/cancel都核activation_id/epoch；浏览器页面没有activate/advance/choose-slot/purpose/token控件或写入API。可信runner为每个浏览器actor启动/记录该UI实例（或在上一actor终态后重新绑定并留收据），过期页面/旧session不得认领下一actor。真实浏览器操作与实际服务实例的PID、启动命令、原请求/Task_id/屏幕证据分别留存，单有entry字符串不能证明入口执行。
5. SDK/task CLI/AppTest/oldCLI均由同一个固定runner按顺序启动并保留原始子进程或调用收据。省略actor_context/plan字符串时正式服务仍从W authority读当前activation，不回退旧预算。任意调用者若在该phase提交同一个已核请求，最多认领当前一个owner而不扩大预算；这只是包内工程所有权，不能冒称对抗有宿主写权限的其他进程。并发回归可在独立事前冻结fixture中激活一个有限组，其每个成员请求/原始key必须可唯一匹配，不使用主E2E空slot。
6. Task R子调用继承父Task的已绑定actor/admission，不需要切换激活或再次占slot。直接ledger登记无上下文也须查该run已经绑定的admission/actor，不能以不带activation来变成新legacy登记。

**冻结错误优先顺序**：A 物理域/schema/历史完整性错误；B active plan/slot存在、请求与服务/根身份、key冲突/原owner exact retry（exact retry返回原结果，不重扣）；C 新请求共享12及原family额度是否满足；D slot grant capacity/maxowners是否满足；E 同一事务新增admission+绑定owner。不得在C之前自动找另一个slot。无合法active slot时B就拒绝`EXECUTION_PLAN_SLOT_UNAUTHORIZED`；合法预登记的额满拒绝探针通过B后，C以`EXPERIMENT_BUDGET_EXCEEDED`拒绝。这样原反例与额外未登记actor的期望错误不冲突。

独立预算回归fixture可预登记`EXPECTED_BUDGET_REJECTION`探针slot：`requested_units=1`、`grant_capacity=0`、预期共享已用12；它能调用同一实际旧入口核共同预算，但永远不能增加准入单位，不计主成功actor。若前置未耗尽，D明确拒绝`EXECUTION_PLAN_SLOT_EXHAUSTED`并使该回归候选失败，不能把错误类型当成功。该fixture12个取消占12，探针增加的是一条预期拒绝记录，不是第13次获准或执行。

## 4. Task 所有权与去重

- Task 的 admission owner 是原 Task ID/冻结 request_hash，不是浏览器 session 或随意 family 名；只有原 `TaskAuthority` 校验 owner/epoch/RUNNING 和物理 `R` slot 后，才能将预留一次性绑定到分配的 `child_run_id`。Task 在执行前取消而没有 R slot，原 admission 仍全部占用。
- Task R 子运行逐 hypothesis `register_trial()` **认领父 admission，不再次扣额度**。必须核 Task raw request、trusted TaskContext、slot binding、physical root、catalogue/data/code/bundle、hypothesis alias/definition 与 admission；仅有公开 receipt ID 或伪造 lineage 不足以认领。
- **受管执行plan内**，Legacy key先由`plan_hash+slot_id`派生并查原绑定，再决定是否首次分配run_id；相同slot exact retry仅恢复原run或显式拒绝，不能新UUID抢其他slot。**仅不带E2E actor plan的事前冻结独立预算回归场景**，legacy key才可为`(LEGACY, canonical ledger root, run_id)`，新run_id代表新试验并需新额度。两者都禁止重复claim/重复JSONL。真正非受管standalone维持原P3语义，不套用这套共享12断言。
- Task exact submit retry沿用原key原Task/admission；**受管plan内换key命中已绑定slot一律拒绝slot耗尽**，不能自动解释为可获准的新actor。非plan预算回归新key才代表新试验。被拒绝幂等请求重复返回原拒绝；不能更改请求使同key获准。任务重试/恢复不新建admission，重复取消不退款。
- 同一 hypothesis 在其他 family/campaign 仍根据 data 域共享计数，`repeat_of`、污染历史和多重检验仍保留，不能把新 admission 字段当作金融批准。

## 5. 混合并发与文件恢复：不依赖双库原子性

本方案没有 Task DB 与“另一个预算 DB”的双写；两类入口都在同一现有 SQLite authority 内完成额度判定与扣记。SQLite 与原 JSONL/不可变文件是 **先权威提交、后可核投影**，不宣称两者同时原子。

所有写路径遵守单一锁序：authority `BEGIN IMMEDIATE` → 检查/认领/记录 outbox → COMMIT → 按既有 ledger `.trials-lock` 发布投影；**不得持 `.trials-lock` 再等待 authority**，也不得把所有独立子调用自动重试。投影时需重复读取相关 admission/claim，校验 exact canonical payload。新 Task 预留不能仅旁读旧 trials 并放锁后再写自己，legacy 也不能在 authority 之外独立 append。

| 崩溃点 | 必须恢复结果 |
|---|---|
| authority 事务提交前 | 回滚，无已准入 debit；原孤立临时/运行文件保留并明确未准入，不执行研究；后续不能忽略其完整性含义 |
| commit 后、Task/legacy sidecar 发布前 | admission/debit 已生效，不退款；恢复通过同一幂等 owner 从 outbox 重建原字节，未完成前 worker/研究拒绝执行 |
| sidecar/trial JSONL 部分写、DB materialized 标记前 | 比对原字节/seq/hash；已有完整相同投影复用；无完整记录时只允许从冻结 outbox 发布，不 append 第二个 claim；截断/不同字节失败关闭，保留原文件，不截断原失败日志后改判 |
| 研究失败或取消后 | admission 不变；终态证据依原 Task/ledger/财务对账规则封存；未知账本不能降级成正常 CANCELLED |
| DB丢失/损坏、Task/ledger历史缺项/重复/域冲突 | `ADMISSION_HISTORY_UNVERIFIED` / `ADMISSION_INTEGRITY_ERROR`，阻断新准入和执行，不将空扫描当0额度，不自动重置 DB |

多进程 Task/legacy 各请求一次 N 单位：唯一线性化点是 authority COMMIT；当剩余 1 单位且两个入口并发各请求 1，恰有一个准入、另一个拒绝。相同幂等请求并发只存在一个 admission。N=2 但剩余1时整体拒绝，不先让一个候选读结果。

## 6. 已存在 P6 历史的版本化导入与缺损拒绝

新P7实现不修改固定P6软件包、旧依赖锁或历史工件。**现有catalogue的code/bundle/environment精确匹配仍是前置条件**：真实旧P6 bundle的W不能为导入新门禁而关闭catalogue校验，也不能让新P7包冒充旧bundle恢复写入。它继续由原固定包在独立原根/只读历史路径核验；其历史可作单独只读审计/导入设计参考，不能借导入创建可追加的P7假旧W。下述可写版本化迁移仅适用于同一新bundle、catalogue仍可完整核验、原控制schema升级的W（及事前冻结的工程历史回归夹具）；不能跨此边界。若同包新schema打开这类已有工程W，先进入 `MIGRATING/UNVERIFIED`，持同一authority写事务阻断新运行，逐一核对：

1. workspace 唯一行/anchor/catalogue、所有 Task raw request、campaign 原记录、`campaign_attempts` 精确集合、原 units/over_budget、R slot/child ownership、现有 Task/终态文件及原始 hash。
2. 原 `trials.jsonl` 完整 hash 链和全 run config/lineage/events；通过 **可信 Task R slot + child_run_id + 原 request/hypothesis 绑定** 去重父预留和子 trial，不能仅凭 caller 写的 campaign_control 或相同 UUID 跳过去重。
3. 未执行/失败/取消 Task 预留照样导入；旧独立 legacy trial 按原单位计入。旧超额拒绝申请单独保留，若原历史超额/不能证明 admitted 对应关系，域至少 saturated，拒绝再准入；不利用重解释返还额度。
4. 导入前后原文件 bytes/hash 不变，产生单独不可变迁移清单、完整集合/计数/匹配证据；有缺失、重项、非终态未知、孤立文件或任何不能确定的 Task↔trial 对应，保持 UNVERIFIED 并拒绝新准入。不能“只导入能读的项”。迁移成功仅关闭工程计数版本迁移，不是 OS隔离或金融批准。
5. 原 P6 安装包不能参与新 P7 W 的写入。新 P7 W 用强制新schema anchor，旧包只在原包/原依赖/独立冻结路径执行回归或只读历史重放；不混用跨 bundle 进程同时写新W。旧包本身没有新门禁，因此本方案不宣称已在无真实 ACL 的场景阻止恶意旧进程直接写盘。若发现非新schema authority 认可的外来记录，完整性门禁失败关闭，不自动吸纳后继续跑。

## 7. 精确允许实施范围与兼容影响（仍待实施授权）

| 允许路径 | 必要变化 |
|---|---|
| 新 `src/aqrp/experiments/admission.py` | 唯一authority、域解析、事务/幂等/claims/outbox/迁移与完整性验证；无金融计算 |
| `src/aqrp/experiments/ledger.py` | start/`register_trial`强制域/准入验证、原trials投影幂等；保留原数学答案/家族定义/重复污染语义 |
| `src/aqrp/services/research.py` | 完整候选集合在观察结果前一次性准入；无TaskContext自动共同入口；不改P3金融数学 |
| `src/aqrp/services/task_state.py` | 同一DB原子Task+共同预留；原campaign证据投影；不重复扣R子运行 |
| `src/aqrp/services/task_campaigns.py` | 读共同权威历史/污染，禁止registration扫描与准入各自竞态计数；登记不会重置总量 |
| `src/aqrp/services/task_context.py` / `tasks.py` | trusted R ownership/claim/恢复门禁，运行前投影完整性；不放宽P4/P5/Task完成屏障 |
| `src/aqrp/services/cli.py` | 如需错误映射只展示统一拒绝/原run；旧命令签名不要求token、不设绕过开关 |
| 新 `tools/p7_engineering_protocol.py` | 唯一PlanAuthority控制面：冻结顺序CAS激活、launch/绑定收据、实际entry证据；runner source hash进冻结plan，网页/CLI不增加激活命令；无真实账户/权限操作，未G1+实施授权不得实现 |
| `src/aqrp/ui/app.py`、`services/task_cli.py`及对应可信启动接线 | 固定W+当前activation绑定/过期session拒绝；不新增网页slot/purpose/token输入，不把首次UI随机key预写进计划 |
| 新/受影响实验、Task、CLI、UI及integration测试；P7 reference/SDK/证据运行器 | 下列候选及真实原始证据；旧测试/失败证据全部保留 |
| P7身份/version/bundle/reviewed_code及package gate | 新模块和接线必须新固定bundle；不得沿用P6原hash冒称批准；实施后另G2 |

同包兼容是 **旧签名/旧缺省请求字节保持**，不保证继续允许已被证明不符合共同预算约束的行为。新增独立 sidecar/control schema不把字段偷偷塞回原P6请求bytes；旧Task raw config hash和原结果回放不改。若新门禁导致原独立测试首次进入受管 workspace 时拒绝，应补明确原始环境/边界断言，不能删除失败或改正确数学答案。跨bundle兼容仅指已审旧包隔离路径/只读历史，不承诺旧P6进程能安全加入新P7 authority。

## 8. 设计候选（非已执行产品结果）

机器可读候选见 `COMMON_BUDGET_ADMISSION_CANDIDATES.json`（当前36条）。这些用例除明确写出主/风险/取消actor plan的候选外，使用事前冻结的独立预算控制回归夹具；BUD-001/002/007/008有各自预登记的expected-rejection probe，BUD-003混合并发有固定有限并发组，不能把它们加入主12成功actor。其他预算原子性候选采用不设E2E actor slot限制的独立计数回归模式，仍强制同一W/data authority，不借新W补全链成功。候选必须包括原12个取消后旧入口拒绝、双向顺序、剩余1混合并发、2单位原子拒绝、Task子运行不双扣、direct ledger无上下文、换输出/家族/配置不逃逸、幂等冲突、commit后崩溃恢复、历史缺损/外来写入失败关闭。新P7真实实现另行授权后才执行并保留双OS SDK及原始工件。
