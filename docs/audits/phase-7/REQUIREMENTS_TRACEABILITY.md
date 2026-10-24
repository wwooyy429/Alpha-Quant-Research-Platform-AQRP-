# Phase7 原目录映射 · 5项（3 MVP / 2 Competition Ready）

规范源是 docs/requirements.csv 的原字段快照；本表仅设计映射，不改原目录 capability_status，也不证明实现完成。共同实施前提为 P6 已核实 RELEASED、P7 G1 固定 SHA 通过、阻断设计闭环及用户单独实施授权。

| ID / 等级 | 原依赖 | 本阶段必须交付 | 接口 / 未来位置候选 | 通过证据及关键反例 |
|---|---|---|---|---|
| DATA-013 / Competition Ready | DATA-008;INT-006 | 数据源/授权/字段/市场单位/时区/日历/可用时间/复权/历史股票池/版本映射表；真实源未知时明确外部阻断；工程适配真实输出标准请求及来源收据 | 离线 AdapterSpec / InputManifest → verified catalogue binding；src/aqrp/competition/；tests/competition/test_data_013.py | T7-ADAPTER/T7-BOUNDARY：工程源原始字节、8表/manifest、单位时间和规则逐字段对账；未知源、缺授权、无available_at、日期冒充时间、真实provider ID不得回退到合成源 |
| INT-003 / MVP | INT-002;UI-007 | 候选参数/版本/停用回滚不污染固定工程 Strategy pin、运行状态、历史实验；候选修改受原家族预算和污染控制 | 现有 Registry 精确Ref / TaskService / 原账本；tests/integration/test_int_003.py | T7-MODES：变更前后 exact Ref、config/父链/旧工件 hash；并发/恢复、反向控制、候选未批准正式入口拒绝；不可把只读Python对象当真实OS隔离 |
| INT-004 / MVP | INT-003;ENV-002 | 新源 checkout + 精确依赖/hash安装 + 数据准备 + 全SDK/CLI研究回测 + 真实网页任务和数值比对 + 手册/运行及部署边界文档 | 原CLI/TaskCLI/SDK/UI；tests/integration/test_int_004.py；USER_GUIDE.md、DEPLOYMENT.md候选 | T7-CLEAN/T7-PARITY/T7-OPS：两个OS原始工件/真实浏览器、逐命令退出码、scope/失败完整；实际部署未授权，不能仅以UI启动宣称部署完成 |
| INT-005 / MVP | INT-004;FACTOR-011;RESEARCH-009;BT-010;UI-007 | 同固定数据/组合/执行配置的 Momentum→Reversal 全研究/策略/所有入口替换及全回归；信号/订单按独立答案变化 | 已有服务组合 + E2E证据运行器；tests/integration/test_int_005.py；tests/e2e/ | T7-REPLACE/T7-LEAK/T7-REGRESSION：完整P3/P4/P5/Task绑定、原始财务重建、核心diff/hash、入口逐字段比较；无假报告/假子run，禁止通配忽略hash/lineage |
| INT-006 / Competition Ready | INT-002 | 通用离线工程模拟接口、规则/能力矩阵、真实映射及规则拒绝测试；具体比赛规则未定就保留外部依赖 | AdapterSpec / CapabilityReport / adapt_engineering / emit_report；src/aqrp/competition/；tests/competition/test_int_006.py | T7-ADAPTER：可部署为本地库/CLI的确定性映射与同核运行；缺/冲突规则失败关闭；不添加第二撮合引擎、真实连接或任意Python映射代码 |

V3.0§18额外列出的全系统集成、泄漏审计、独立代码审查、完整回归、操作手册及最终报告分别映射到上述 INT-003/004/005，不能因为原表仅5项而遗漏交付。未知外部比赛依赖由原 DATA-013/INT-006 的验收文字允许单独记录；不得以此免除可实现的通用接口和工程规则验证。

跨阶段不重复计数：GOV-001–010、ARCH-001–003、ENV-001–003、QA-001–007；DATA-001–009/011/012、FACTOR-004/005/011、INT-001/002、RESEARCH-009、VALID-003–008、EXP-001–004、BT-010、UI-007/008。旧源码和全部已审正确答案、失败证据继续保护，既有严格门槛不降低。来源旧称Gemini的角色按2026-10-22用户改令由GPT Work主审执行，保留原文字不伪造历史角色。

本轮G1修订补充：INT-003/005 → T7-ADMISSION/COMMON_BUDGET（跨入口12、并发/幂等/取消/恢复）；INT-004/005 → T7-BROWSER-NEGATIVE（真实原风险夹具1与同W零研究取消/replay）；INT-006适配执行也必须经过相同准入，不能独立新family。治理依赖EXP/UI-007/008、QA与旧证据不重复计数，原106及五项快照不变。
