# 合成执行 profile 与待 G1 决定事项

以下全部是**新设计候选**，并非用户已批准交易规则。只有工程合成数据，CCY 单币种、SYNTHETIC_V1 已版本化日历；UTC微秒，session不可按自然日加一。保持原P4双lot门禁、原仓不动/完整全平例外和全部风险，不允许靠拆单绕过非整手delta。

| 决策 | 提案 | G1/实现放行条件 |
|---|---|---|
| P5-D01 时间与开盘输入 | 前收盘已确认信号，严格未来开盘；开盘切片独立于完整日bar | 审核切片双时间/父manifest；周末、假日、晚到/同刻/±1us独立负例 |
| P5-D02 交易单位 | 本合成profile价格tick0.01 CCY/share、数量整数share，lot为正整数；P4通用小数输入不会被当成本profile默认 | 全目标/delta/partial lot精确，允许显式完整奇零股全平；非整数拆股结果拒绝并保留失败，碎股规则未定义不猜现金补偿 |
| P5-D03 费用/滑点 | commission=max(1.00,abs(q·price)×0.001) **每个Fill** 向分HALF_UP；无税；滑点10bps，买价向上tick、卖价向下tick；无隐含真实市场含义 | 订单最差界为decision价±5%并按tick方向舍入，费用预算F默认10CCY先从P4可投资现金排除；按share最坏Fill次数预留费用，上界超预算拒绝；越界拒绝而非无限透支，部分Fill最小费重复是明示经济模型 |
| P5-D04 容量/限价/期限 | 每证券每开盘合成固定10share容量，共享；历史ADV门槛显式冻结且仅用此前可见量。MARKET/LIMIT，DAY/GTC；LIMIT只在可见开盘参考和最终滑点价均满足limit时成交 | DAY到本session收盘到期；GTC在锁定截止session收盘到期，cancel确认优先于后续match；无成交不伪造胜率 |
| P5-D05 交收 | T+1 **下一calendar session开盘** 结算卖出现金/买入可售数量；买入成交时立即扣total/settled资金，未交收买入不能再卖；卖出时total现金增加但仅结算后可用 | explicit unsettled ledgers，不以总现金超买；P4投影保留unsettled与reserved，卖出可售/下一开盘边界测试 |
| P5-D06 行动与修订 | 已公告且生效时先拆股，再ex红利资格，再交易；持仓before-action享受，开盘后新买不享受，同刻卖前先确认；PER_OLD_SHARE以前一session收盘锚定，pay>=ex、应收不再投，空头同额应付 | P3 U002只供对照，不能充当本阶段批准。行动必须在effective前已可见；迟到/经济修订生效已过则停止运行标DATA_REVISION_REQUIRES_RERUN，不倒改历史账本；只在新快照新run受审后重算 |
| P5-D07 多空 | 无融资；未平仓短卖原始所得100%限制（按原始开仓成交成本的未平仓部分释放），另100%当前短仓市值margin；borrow限额/权限逐次重查，费率年1%，A=252，每收盘按当时已确认raw mark计当期1/252费，向分HALF_UP；short dividend payable | margin breach阻断新风险/撤单并标MARGIN_BREACH，保留账户亏损，不伪装自动平仓或允许负自由资金继续；预先冻结强平并非此profile隐含能力 |
| P5-D08 估值/退市 | RAW mark；停牌持仓保留最近已知有效mark，stale超过1个session则运行失败；零价不能代缺失。已知明确合成delist回收价事件才清算，否则FAIL UNRESOLVED_DELISTING | 未知退市不能抹仓/按零归因；有持仓完整报告旧mark和未决损失 |
| P5-D09 账户到P4 | B=U+O+P+F、C_alloc=C−B/E_alloc与E_total双投影；应收不买入、费用预算独立分区、P4+P5完整双风险，见接口 | 必须独立手算含long/short现金红利及未交收/预留；若无法无歧义适配列阻断，不静默删风险项 |
| P5-D10 统计 | A252、ddof1、rf_daily=(1+rf_annual)^(1/A)−1；默认rf0；外部流单独事件与流前/后估值TWR | 无交易/零方差/样本<2/非正权益明示undefined，不能用0冒充；合成统计不作为金融批准 |

所有有效权限/输入未知时拒绝。上述提案均需 GPT Work 固定 SHA 审查，涉及经济口径由用户在后续实施授权中明确接受或修改；G1不能替代用户金融批准或部署授权。冲突在 OPEN_QUESTIONS.md 登记，未解阻断不开始实现。
