# Phase4原需求逐项映射（7项）

2026-10-22 当前Phase4 G1：GPT Work对固定265af16353d85ce8c2d229a7517809d707498da8判PLAN PASS（受限工程设计），001 High/002 Medium均CLOSED_DESIGN，无新增阻断。原17候选独立复算、64项证据检查通过；仅设计数学，不是P4实现。原件与接收/关闭在docs/audits/phase-4/g1-265af16/。实际P4实施仍待用户单独授权，未阶段验收/合并/标签/部署/实盘/P5；Phase3受限发布与延期不变。以下旧BLOCKED/OPEN按原轮历史保留。

原106项和12业务分类/16 ID前缀不改；级别来自canonical目录，不把Competition Ready推迟成空接口。本轮全部业务状态Planned，设计候选待G1。

| ID / 级别 | 依赖 | 具体设计/后续实现 | 验收与独立答案/负例 |
|---|---|---|---|
| PORT-001 / MVP | FACTOR-009;VALID-008 | INTERFACE_DRAFT§1/4；portfolio/contracts,service；正式与显式工程身份，同纯内核 | 因子名称无关、原账户字节不变、审批/来源/时点拒绝、目标/数量/建议完整；正式金融依赖延期明确 |
| PORT-002 / MVP | PORT-001 | §2/3；portfolio/weights,construct；单/多、等权/分数权、LongOnly | G01–06/10–11，零负分、共同交集、并列、lot/现金、性质守恒 |
| PORT-003 / Competition Ready | PORT-001;RISK-003 | §2/3；真实LongShort两腿、G/N、等权/中心化 | G07–09/18–19，空腿/重叠/缺许可/借券、非0净敞口、资金缓冲 |
| RISK-001 / MVP | PORT-001 | §3；risk/checks，单票/gross/net/leverage/turnover | G12–14/20，边界/超限/矛盾、取整后低净界、全持仓平仓检查 |
| RISK-002 / Competition Ready | PORT-001;DATA-012 | §1/3，PIT侧车、行业净/总及Beta | G15–16，行业抵消、缺失/修订/过期/未来/重复、精确边界 |
| RISK-003 / Competition Ready | PORT-001;DATA-005 | §3，可交易/许可/借券/可售、跨0 | G17–19，停牌、borrow总额度、平旧空、sellable不足、缺输入拒绝 |
| RISK-004 / MVP | RISK-001 | §4；无可执行目标/订单的拒绝与不可绕过服务 | 公开入口篡改/陈旧结果/skip标记/错误封存绑定均拒绝；失败记账完整 |

G编号为GOLDEN_REFERENCE候选，只是独立算术校对，不是P4实现测试通过。未来需tests/portfolio/test_weights.py,test_construct.py,test_contracts.py及tests/risk/test_limits.py,test_tradability.py和tests/integration/test_portfolio_service.py；以实际最终代码路径补映射，不生成空测试文件来满足表格。


## e40ddd0 G1修订的增量映射（不新增需求）

- PORT-001/002/003、RISK-003/004 → INTERFACE_DRAFT §3.1、profile.quantity_policy、ROUNDING_REFERENCE R01–R13/R17：目标及delta分别检查；原奇零股保持/全平开关/部分增减/跨0；所有拒绝在P4共同service闭环，不等P5。001仍OPEN待复核。
- RISK-001/002及QA-001/002/004 → TEST_AND_EVIDENCE_PLAN新增性质边界、ROUNDING_REFERENCE R14–R16：X03绝对Beta/行业net增加，X04turnover增加，收窄单调断言并保留所有pre/post门禁。002仍OPEN待复核。
- 原7项4MVP/3CR、原依赖和拟实现路径不变。本次参考脚本校对不是P4产品测试、金融批准或独立G1通过。
