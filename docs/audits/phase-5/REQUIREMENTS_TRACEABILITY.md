# P5 原始需求追踪与验收计划

目录106条不变，本阶段12条=10MVP+2CR。每行阶段P5、状态Planned；原始完整依赖见snapshot，正式审批依赖不因工程延期删去。

| ID / 等级 | 原始需求 | 设计 | 未来产物 | 测试/证据 |
|---|---|---|---|---|
| BT-001 / MVP | 独立Market/Signal/Decision/Order/Fill/Account/Valuation事件状态机 | INTERFACE_DRAFT.md 事件总序/事务组 | 确定性事件流/Journal因果链；src/aqrp/backtest/ | T01/T02/T04；tests/backtest/test_bt_001.py |
| BT-002 / MVP | 收盘后信号、next session最早开盘，available/decision/submission/eligible/fill约束 | INTERFACE_DRAFT.md + PROFILE D01 | 可得性→订单→严格未来slice证据；src/aqrp/backtest/ | T01/未来mutation；tests/backtest/test_bt_002.py |
| BT-003 / MVP | 创建/状态/成交/部分成交/拒绝/取消/到期与幂等 | INTERFACE_DRAFT.md 状态/幂等 + D04 | 订单全状态/partial/cancel/expiry；src/aqrp/execution/ | T02/T03/T04；tests/execution/test_bt_003.py |
| BT-004 / MVP | 费用/滑点/流动性/停牌与开盘可交易模型 | PROFILE D01/D03/D04/D08 | tick/commission/capacity/status风险；src/aqrp/execution/ | T03/T07；tests/execution/test_bt_004.py |
| BT-005 / MVP | 现金/持仓/成本/费用/现金流/已实现未实现/权益账本及原始重建 | MATH_CONTRACT.md 复式/成本/结算 | 现金/持仓/权益/journal逐笔独立重建；src/aqrp/backtest/ | T04/T05/T11/T12；tests/backtest/test_bt_005.py |
| BT-006 / Competition Ready | 行动/分红应收支付/拆股/交收/退市估值 | PROFILE D05/D06/D08 + MATH行动 | split/dividend/pay/settlement/delist；src/aqrp/backtest/ | T06/T07；tests/backtest/test_bt_006.py |
| BT-007 / Competition Ready | 空头、融资/借券费、保证金与股息应付 | PROFILE D07 + MATH多空 | short proceeds/margin/borrow/dividend payable；src/aqrp/backtest/ | T05/T06/T07；tests/backtest/test_bt_007.py |
| BT-008 / MVP | 估值/权益/每日持仓现金/风险暴露/订单成交报告 | MATH_CONTRACT.md 估值/归因 | 每日原始cash/positions/mark/equity/风险；src/aqrp/performance/ | T05/T07/T08；tests/performance/test_bt_008.py |
| BT-009 / MVP | 累计/年化/波动/Sharpe/MDD/换手/费用/净收益/多空贡献 | MATH_CONTRACT.md 绩效 | 统一conventions/undefined/费用一次；src/aqrp/performance/ | T08/T12；tests/performance/test_bt_009.py |
| BT-010 / MVP | P5因子替换后完整组合/风险/撮合/账本流程 | SCOPE_AND_DEPENDENCIES.md + 接口provider | 仅换精确因子配置的完整模拟与核心hash；src/aqrp/backtest/ | T09/T10；tests/backtest/test_bt_010.py |
| QA-003 / MVP | 10项核心不变量及完整事件/资金独立对账自动测试 | TEST_AND_EVIDENCE_PLAN.md | 至少10类别、边界/性质/独立答案与原日志；tests/（对应模块） | T01–T12；tests/quality/test_qa_003.py |
| INT-002 / MVP | 批准因子→信号→组合→风险→订单→撮合→账户→净值→绩效 | PLAN.md 主链 + INTERFACE_DRAFT.md | 真实原P1/P3/P4接线/完整模拟重放；src/aqrp/services/;tests/integration/;tests/e2e/ | T09/T10/完整SDK；tests/integration/test_int_002.py |

## 本轮G1修订到原需求的补充映射
| 发现 | 原需求 | 新设计 / 独立答案候选 |
|---|---|---|
| 001 | BT-001/002/003/005，QA-003，INT-002 | EVENT_TRANSACTION_ADDENDUM / CONTRACT_CHANGE_IMPACT；N01–N03 |
| 002 | BT-005/006/007/008，QA-003，INT-002 | CASH_BUCKETS_AND_PROJECTION；N04–N11，原G25静态条件明示 |
| 003 | BT-003/004/005，QA-003 | EXECUTION_PRICE_AND_FEES；N12–N17 |
| 004 | BT-005/007/008/009，QA-003 | FIFO_ATTRIBUTION；N18–N25 |
不新增、删除或改变canonical12项等级/阶段。全部P5业务仍Planned；修订候选未审，四项不自判关闭。
