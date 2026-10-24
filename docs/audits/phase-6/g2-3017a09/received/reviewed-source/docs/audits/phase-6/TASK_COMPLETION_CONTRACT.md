# 固定三种Task的完成屏障与恢复契约（G1修订候选）

本契约修订WORK-P6-G1-001，供新固定SHA独立复核，发现仍OPEN_PENDING_RECHECK；不是P6实现。Task的成功与任一核心子run的成功严格分开。核心终态只更新它所属的slot；只有TaskService完成本文件的全Task屏障和提交，才可发布Task SUCCEEDED。没有通用DAG/插件调度框架。

## 固定kind、必需阶段和产物

| kind | 冻结的必需阶段 / slot | 成功的必要证据 |
|---|---|---|
| research | R=一次P3研究；RV=研究工件验证/发布 | R的真实SUCCEEDED终态、原始report/metrics/审批建议/全部manifest成员与输入/家族记录绑定；RV验证回执；Task全局完成回执 |
| engineering_pipeline | R=P3研究 → PLAN=冻结P5请求和决策集合 → B=P5模拟，内部P[i]=逐决策P4 → BV=全链验证/发布 | R真终态、不可变ResolvedPlan、B真SUCCEEDED及已核金融投影、全部必需P[i]真SUCCEEDED和P5实际portfolio-lineage一致、BV全链工件/来源验证及Task回执 |
| replay | SV=原run/包/锁/投影范围验证 → E=声明范围内实际重放（含其内部P4 slots，如适用） → CV=独立比较/封存 | SV回执、E实际NUMERICAL_REPLAY_VERIFIED或目录已登记的原Ref投影重放成功、CV比较与目标工件清单、Task完成回执；原run成功仅是SV输入 |

RV/PLAN/BV/SV/CV是受限编排的校验/封存步骤，不伪装成既有P3/P4/P5业务run。其原始输入hash、声明投影、结果与检查证据都写不可变Task工件清单。replay仅允许catalog登记的P5_NUMERICAL或PUBLISHED_REF_PROJECTION；不支持的旧宿主/缺包范围明确拒绝，不能把验证原始源文件当执行了重放。

engineering_pipeline不另造外层假P4 run：必需P4就是P5内部真实逐决策调用。R验证后，用原P3/P1来源、共享builder和已冻结有效配置构造P5请求；这只是请求/来源组装，不重复拟合或改PIT。先冻结ResolvedPlan（父TaskPlan hash、P5请求原字节/hash、严格有序决策表index/decision_time/source-request hash、N、每个必需slot/UUID/root）。N取已验证请求decisions的完整集合，本应用流水线要求N>=1；空区间在此以NO_REQUIRED_DECISIONS明确拒绝，不修改底层P5合法零决策API。ResolvedPlan在B启动前持久化，之后不能缩减N、删失败/缺失slot或事后追加替代UUID。P[i]适配请求hash在调用前按NESTED_CONTEXT_CONTRACT做一次性finalize。

## 成功屏障

TaskService在可信同一claim中逐项确认：
1. 有效配置/初始TaskPlan、必要时ResolvedPlan、catalog/defaults、代码/bundle/core与UI锁/输入快照及侧车身份全部一致；plan已封闭，固定必需slot集合完整且实际注册调用集合精确对账，无遗漏/多余/未登记run。
2. 每个必需slot的服务类型、Task/parent/decision/root/config绑定已核；各核心真实终态和原始manifest/成员hash通过既有完整门禁。R/P[i]/B均真实SUCCEEDED；RV/BV/SV/CV相应验证回执完整。replay的E必须有本次实际重放/比较证据，不能借原run的SUCCEEDED替代。
3. B成功必须具有原始result/state/transactions/transaction-files/portfolio-lineage/published-byte-audit/trace等manifest内所需工件及既有完整金融对账证明。每个P[i]原始result/candidate/risk/成功审计与B对应决策/真实父链一致；只凭P5返回success或一个合法UUID不足以通过。
4. 没有运行中的worker/未处理副作用或未决取消；取消与完成竞争在同一任务终态事务串行化。若完整成功屏障先完成并提交，后来的取消TOO_LATE；若取消意图先被接收，禁止继续提升成功，等待安全取消/对账。未知财务状态一律FAILED+COMMITTED_STATE_UNVERIFIED，不能CANCELLED known=true。
5. 所有上述证据写成一次性completion.json，列出task/kind/config/plan hashes、完整required slots及绑定、各终态/产物/父链hash、验证结果和最后claim。先原子发布并验证回执，再在SQLite事务内检查同一plan/claim/取消版本并提交Task SUCCEEDED及回执hash。两侧未闭环时仍RUNNING/finalizing，不因文件存在报成功。

SQLite提交前宕机，恢复者重新验证整个屏障及completion.json，才可追加恢复Task终态；绝不能从一个恢复的P3/P4终态提升整个Task。SQL终态若指向丢失/损坏回执，保留原记录并对外标INTEGRITY_ERROR/usable=false，不作为成功计数，也不重写旧证据来维持成功。

这是明确的应用级严格全链成功口径：合法P4风险拒绝仍保留真实P4 REJECTED/FAILED与P5可能SUCCEEDED的原始事实，但该Task以FAILED/REQUIRED_STAGE_REJECTED展示，不能说全链所有必需阶段成功。此规则不改P5风险/事件/金融算法、不把拒绝改成下单、不强制中断原模拟，也不要求成交数或收益为正。所有真实子结果可按各自状态查看。

## 恢复与未完成阶段

| 观察到的可信状态 | 只允许的恢复动作 | Task不能宣称的事实 |
|---|---|---|
| R终态已提交、slot映射未写；P4/P5尚未启动 | 核原预分配R绑定后恢复R slot；用其原字节组装/验证PLAN；只有未启动且ALLOCATED的后续slot可执行 | 不能Task成功，不能重跑R、重计或退还试验 |
| R/部分P[i]成功，B未形成终态 | 只恢复这些slots；严格满足原P5 resume条件时使用同一B run/请求/上下文和原始事务prefix恢复；否则RECOVERY_REQUIRED | 不能凭已完成P4或缓存余额成功，不能新建B替代 |
| R/P[i]成功，B缺失但START_INTENT已登记，或存在半初始化/部分发布 | FAILED/RECOVERY_REQUIRED，保留所有记录；不自动从缺目录推断未执行 | 不能自动重做或抹去已提交副作用 |
| B声称SUCCEEDED但缺必需P4记录/归属/原始工件 | FAILED/RECOVERY_REQUIRED；不能在B结束后补开P4来填清单 | 不能接受B的success字符串替代全链 |
| B真实FAILED、P[i]失败/拒绝、unknown或真实取消 | 分别记录全部子事实并按失败/安全取消规则归并；未运行后续slot标明未执行 | 不能删掉失败slot来满足all条件 |
| 全部必需slots、最终工件及父链成功，但Task回执/索引未提交 | 全量重验证，补完成回执/终态事务；不重新执行核心 | 不能在补验证之前发布成功 |
| 全部屏障、回执及终态事务通过 | 返回原Task和原子run引用，后续同key幂等读取 | 不能生成新核心run或覆盖历史 |

只有slot仍ALLOCATED、无START_INTENT、无核心目录/初始记录且完整枚举和claim证据均能证明从未执行时，才可首次调用。任何枚举错误、未知/冲突、活跃旧claim、配置漂移都失败关闭。P5恢复只适用既有resume_engineering条件（同包/原config/原prefix、无部分发布等）；不能借Task恢复放宽原拒绝。replay是新执行且新归属，resume是同一执行同一slot，不能互换。

G2必须在真实服务/SQLite/磁盘执行R、每个P[i]、B、RV/BV/CV提交及映射前后、completion发布与SQL提交之间的断点，验证未完成任务不成功、无重复核心调用/试验或金融提交，取消竞态和原始失败仍完整。设计模型通过不代表这些实际故障已测。
