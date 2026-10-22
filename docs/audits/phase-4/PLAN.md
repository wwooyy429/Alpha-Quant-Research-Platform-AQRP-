# Phase4 组合构建与风险控制计划 · G1 PLAN PASS（受限工程设计）

2026-10-22 当前Phase4 G1：GPT Work对固定265af16353d85ce8c2d229a7517809d707498da8判PLAN PASS（受限工程设计），001 High/002 Medium均CLOSED_DESIGN，无新增阻断。原17候选独立复算、64项证据检查通过；仅设计数学，不是P4实现。原件与接收/关闭在docs/audits/phase-4/g1-265af16/。实际P4实施仍待用户单独授权，未阶段验收/合并/标签/部署/实盘/P5；Phase3受限发布与延期不变。以下旧BLOCKED/OPEN按原轮历史保留。

## 原轮设计修订与预审历史（以下旧状态非当前结论）

当前：GPT Work固定e40ddd0009cc30664c3a0fe0b74c4a497a541d77判**PLAN BLOCKED**。001 High/002 Medium仍OPEN；本轮最小数量门禁及风险性质修订已提出，待新固定SHA增量复核。详DEVELOPER_RESPONSE.md、ROUNDING_REFERENCE.md及g1-e40ddd0/原字节证据；不得自行CLOSED/PLAN PASS。P4实现尚未授权。

当前独立结论 **PLAN BLOCKED**；本轮设计修订候选 **RECHECK REQUIRED / NOT REVIEWED**。从已发布Phase3 main `0a57dccb5618ba08cd3572d6d6b78fec963a3041`、phase3-baseline/v0.3.0创建独立分支。用户只授权启动本计划预审；不推定授权P4业务实现、合并或发布。正式G1审查主要交GPT Work，固定40位SHA见PR描述AQRP_FIXED_REVIEW_SHA；不审漂移HEAD。

范围严格取原106项目录的phase=4：7项（4 MVP、3 Competition Ready），见REQUIREMENTS_SNAPSHOT.json及REQUIREMENTS_TRACEABILITY.md。PORT-004优化器属后续扩展，不在本阶段；不提前写P5订单/撮合/账本、P6网页、P7完整替换E2E。P4必须完整实现7项既定工程行为，不能把多空、借券或暴露缺失处理标Unsupported代替实现。本轮仅可评审设计和独立算术候选，没有P4业务代码或实现通过结论。

继承Python3.13.16、当前requirements.lock及45模块P3包；不增加依赖、优化器、外部服务或真实市场。单币种、合成SYNTHETIC_PORTFOLIO_1为可执行工程profile候选，不解释为任何真实市场规则。审查需核对与DATA_CONTRACT、INTERFACES、BACKTEST_CONTRACT一致性；本目录是P4接口细化提案，不静默改写已发布契约。

## 工程范围与尚未满足的正式依赖

用户明确接受P3受限工程范围：金融批准、物理隔离和真正独立最终Test延期，历史复现按软件包/锁/旧Ref/结果重放验收。PORT-001依赖FACTOR-009及VALID-008仍保留，正式ApprovedScores入口缺真正金融批准必须fail closed。为可测试P4工程行为，另设显式EngineeringScores入口，限synthetic、TEST_ONLY、非真实账户，不能伪造ResearchValidated，不能调用审批绕过代码。双入口汇入相同纯组合与风险内核；返回标识继续保留ENGINEERING_TEST_ONLY。详见SCOPE_AND_DEPENDENCIES.md。工程延期没有消除正式路径的门禁。

## G1后拟实施顺序（须另有用户实施授权）

1. 冻结接口、合成profile、独立答案及风险顺序；补充AccountSnapshot适配器和输入身份/时间/币种校验，先实现审批失败门禁与明确工程入口。
2. 因子无关分数交集/固定权重合成、确定性选择与LongOnly等权/分数权；不重复P3标准化/方向拟合。
3. LongShort真实双腿和gross/net预算、权限与借券；所有配置先验校验，不将单多输出改标签。
4. 权重/数量/整手/现金与约束完整计算，单票/gross/net/杠杆/换手/行业净及总暴露/Beta/可交易性/可售数量；所有约束逐项诊断，任何失败拒绝，不优化或静默松绑。
5. TargetPortfolio与不可执行RebalanceProposal、RiskDecision及不可变运行证据；同内核显式服务适配。纯提案不提交订单，不写资金账本。OrderEvent集成及成交时再查由P5负责。
6. 已知答案、边界/性质/独立参考；回归P3已验收578及外置原20/4、冻结资产与旧Ref重放。完整干净wheel SDK、双OS原始ZIP及hash、失败日志保留。新增P4测试数量以实际收集为准，不能预写通过数。
7. 提交P4实现PR完整固定SHA及代码审查/环境/数据/配置/工件hash给GPT Work G2。G1通过不等于实现通过、金融批准或阶段验收。用户验收/合并/发布及P5启动仍各自授权。

## 预计改动与风险

后续拟src/aqrp/portfolio/{contracts,construct,weights,service}与src/aqrp/risk/{contracts,checks}，按最终设计精简；对应tests/portfolio、tests/risk、集成测试和新Golden。P3研究/标签/审批协议及旧因子公式不改；与实际数据/暴露对象适配尽量新增。任何必要兼容更改须逐项差异、冻结资产保护、重放及完整bundle重新审查；不得用旧P3工程receipt批准新增源码。运行记录复用已验证实验存储，应用追加新schema，不改旧运行。

G1重点：受限P3依赖能否支持两种明确身份、时点一致性、单/多因子与选股、双腿/净总敞口、现金/卖空保证金及整手后约束、不可绕过的风险结果、证据独立性。细节冻结候选在INTERFACE_DRAFT.md、GOLDEN_REFERENCE.md、TEST_AND_EVIDENCE_PLAN.md。正式Test/金融推断/真实隔离仍NOT VERIFIED，不列为已满足。若这些候选存在冲突，列OPEN并等待用户设计决定，不悄悄扩大范围。
