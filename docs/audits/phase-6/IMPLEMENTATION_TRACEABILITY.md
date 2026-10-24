<!-- Phase6 release-publication override -->
2026-10-24 最新人工验收及发布覆盖说明：Phase6八项受限工程范围已由用户ACCEPTED，GPT Work固定3017a097b49ecdae68228ca9a417fcd03c313200 G2 PASS及三项修复关闭维持。PR #9批准归档头a4d650d5d15e814600fde0bb6858fe97f14e5229只改文档/审计存储/身份元数据，双系统实际CI各1567通过；旧H1扫描失败及原证据保留，7份外部原件位置/哈希明确，扫描规则未改。实际普通合并7b4864f4d750fa96b5b5634c4bba0cd84b5b077f整树等于批准头；开发方合并后新干净SDK1567、原20＋4及数学91通过。发布证据提交仅文档及其身份元数据，main/phase6-baseline/v0.6.0原子同点核验后才RELEASED，旧标签不移动，已审包仍0.6.0.dev5。仅授权其后Phase7 G1计划，不授权业务实现。WI-R2两项和真实隔离持续DEFERRED / NOT VERIFIED，正式Test未运行、金融批准NONE、历史宿主边界及原native原因NOT VERIFIED维持；无部署/实盘/真实权限操作。详docs/audits/phase-6/BASELINE.md。以下既有轮次为历史，不覆盖本次最新人工决定。

> 2026-10-24 当前独立结论：GPT Work 对固定 `3017a097b49ecdae68228ca9a417fcd03c313200` 的 **Phase6八项受限工程范围G2 PASS**，WORK-P6-G2-001/002/003均CLOSED — FIX VERIFIED，无新增阻断；DEV002/003/004按主审工程范围关闭，旧原生精确原因仍NOT VERIFIED。独立SDK1567、已核验双OS原包各1567；原始报告、失败及辅助执行勘误完整保留。**等待用户阶段验收，未ACCEPTED / RELEASED，未获合并/基线/标签或P7授权。** WI-R2-001/002及真实Windows隔离DEFERRED / NOT VERIFIED；正式Test未运行、金融批准NONE、完整历史宿主边界保持。已审实现与后续文档归档SHA分列，PR9审查锁保持3017完整SHA。以下旧OPEN/BLOCKED及待审状态仅作原轮历史，由本条更新当前状态。 [本轮接收与处置](g2-3017a09/DEVELOPER_RESPONSE.md)。

本轮独立报告逐项确认 UI-001–008 PASS（5MVP/3CR）；UI-003的SYN_U / CORE4 / TAIL4实际P3成员及逐事件P5侧车已核。原表是候选实现时的覆盖说明，当前结论以上述固定版本原报告为准。

> 2026-10-24 当前修复记录：G2补全UI-003可信历史股票池选择；补强research计划污染/共享预算与取消的物理财务核验。八项需求级别与范围不扩展，三项仍待独立G2复核。 八项受限P6工程范围；不合并、标签、部署、实盘、正式Test、金融批准或P7。WI-R2-001/002和真实Windows隔离DEFERRED / NOT VERIFIED；完整历史宿主限制保留。

# 实现与证据追踪（候选，待 G2）

原106项需求及阶段/级别不变；八项为5 MVP、3 Competition Ready，全部为本阶段必需能力。原 REQUIREMENTS_TRACEABILITY.md 是当时的 G1 记录，本表为实现增量。

| ID | 等级 | 实际实现 | 开发验证及独立答案 |
|---|---|---|---|
| UI-001 | MVP | ui/app Dashboard、tasks.list/status、最近真实 R/B 入口与完整性错误 | test_views、test_view_interactions、任务损坏负控；最终浏览器六页面 |
| UI-002 | Competition Ready | task_requests 固定目录/Ref/schema、Factor Library 选择/权重/版本/参数和 revision | test_task_requests、numbers 字面/Fraction oracle、真实两因子链、旧包/Ref重放 |
| UI-003 | MVP | 真实 P3、研究表单、metrics/OOS/分层/衰减/试验与原工件 | P3旧回归、test_task_core、原20+4/91、ui_reference逐字段核对 |
| UI-004 | MVP | 实际 P5内部P4、资金/订单/成交/持仓/净值/回撤及原逐桶对账 | 原P4/P5全部金融回归、提交后取消/unknown、字面98.1/998.1/9股 |
| UI-005 | Competition Ready | 筛选/配置和声明结果比较、manifest下载、新数值重放及实际旧Ref执行 | test_task_history/proofs/core、原工件/源只读/hash核验、真实浏览器下载/重放 |
| UI-006 | Competition Ready | 追加式默认配置、CAS/回滚、输入/环境/日志与白名单拒绝 | test_task_state/requests/frontends/views；旧请求不变、secret scan |
| UI-007 | MVP | SDK/旧CLI/新CLI/Streamlit同一请求及金融内核 | tools/ui_smoke +不导入AQRP的ui_reference；两个Ref真实完整链+固定版真实浏览器 |
| UI-008 | MVP | SQLite幂等/claim/槽位/全局完成、协作取消、严格恢复与图表 | 10实际进程、真实P4崩溃/恢复、取消与成功竞争、终态和来源负控 |

测试命令、原始输出/环境/工件哈希以最终固定提交对应的证据索引为准；表中列出覆盖对象，不提前声称全部执行完成。G1 CLOSED_DESIGN 不是实现发现已独立关闭，G2等待 GPT Work。
