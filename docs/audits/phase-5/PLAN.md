# Phase5 G1 计划预审草案 · 独立事件回测

状态：PLAN PRE-REVIEW REQUIRED；用户仅授权 G1 计划。主审 GPT Work，固定 40 位 SHA 以计划 PR 描述 AQRP_FIXED_REVIEW_SHA 为准。G1 通过之后仍需用户另行授权实现；本轮没有 P5 业务代码、实现测试、阶段验收或金融批准。

以核实的 Phase4 已发布 main、phase4-baseline/v0.4.0 同点版本为唯一起点，具体值在 BASELINE_VERIFICATION.json。P4 已验收七项，P5 严格取 canonical 106 条目录中 phase=5 的 12 项：BT-001–010、QA-003、INT-002；10 MVP、2 Competition Ready。逐条原始输入/输出/依赖/等级见 REQUIREMENTS_SNAPSHOT.json，交付与独立证据见 REQUIREMENTS_TRACEABILITY.md。不得把借券/行动或账本作为占位，也不能用 Unsupported 取代此范围内已明确的合成规则。

目标：真实 P1/P2/P3/P4 工程工件 → 因子无关 SignalProvider → 目标/风险 → 合法订单 → 模拟撮合 → 逐笔原子复式账本 → 估值/绩效 → 不可变记录、独立重建及重放。合成工程资金不是现实订单或正式 Test；运行端主动标 ENGINEERING_TEST_ONLY、financial_approval=NONE。正式策略入口继续 APPROVAL_REQUIRED，缺金融批准不能使用工程路径自动降级。

不新增依赖/框架。沿用 Python3.13.16、固定 requirements.lock、单进程确定性队列和现有 Experiments。拟新增 backtest、execution、performance 及薄 services/CLI 适配，现阶段只记录设计，不创建这些业务包。UI/P6、比赛/P7、真实账户和部署均不在范围。既有 P4 API/53模块/准入收据不在本计划更改；如实施需要兼容更改，须先列影响/新 bundle/旧 Ref 复现和新 SHA，不能静默提升原批准。

拟实施次序（G1 PASS + 另获实施授权后）：
1. 冻结请求/profile、事件排序、账户科目及独立答案；先建正式入口失败关闭、输入身份/时间/终态原字节验证。
2. 确定性调度和订单状态机，接入 PIT 信号、P4 目标与 P5 提交/撮合风险；防未来订单、预留超买及重复消费。
3. 开盘切片、滑点/费用、容量、部分成交、拒绝、取消/到期与交收；事务账本及独立重建。
4. 拆股、分红应收/空头应付、借券/保证金、停牌/退市/stale；精确账户到 P4 的显式适配。
5. 估值、成本/多空归因、绩效和完整因子替换链；不可变成功/失败/取消/重放证据。
6. 完整干净 SDK、旧回归、双 OS CI 原始 ZIP 与独立参考。固定新 SHA 交 GPT Work G2；人工验收/合并/标签另行授权。

当前 P4 的 844 项 SDK、旧20/四/91及双OS证据仅是已发布基线回归，绝不是 P5 测试通过。数学候选纯手算与标准库复算也不是实现验证。G1 必须核对 PROFILE_AND_DECISIONS.md 中新执行经济规则；P3 U-002 原批准只覆盖研究标签，不能把它当作 P5 市场规则批准。
