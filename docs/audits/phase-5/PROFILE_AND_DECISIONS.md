# 合成执行 profile 与待 G1 决定事项

以下全部是**新设计候选**，并非用户已批准交易规则。只有工程合成数据，CCY 单币种、SYNTHETIC_V1 已版本化日历；UTC微秒，session不可按自然日加一。保持原P4双lot门禁、原仓不动/完整全平例外和全部风险，不允许靠拆单绕过非整手delta。

| 决策 | 提案 | G1/实现放行条件 |
|---|---|---|
| P5-D01 时间/调度 | 严格未来开盘/独立侧车；C-P5-001外层信封总序、70逐笔原子、80/90子记录、commit_seq及65/95/100 | EVENT_TRANSACTION_ADDENDUM及CONTRACT_CHANGE_IMPACT；冻结P0不改，须明确用户接受补充后实施 |
| P5-D02 交易单位 | 本合成profile价格tick0.01 CCY/share、数量整数share，lot为正整数；P4通用小数输入不会被当成本profile默认 | 全目标/delta/partial lot精确，允许显式完整奇零股全平；非整数拆股结果拒绝并保留失败，碎股规则未定义不猜现金补偿 |
| P5-D03 价格/费用 | 所有side/type统一L=ceil_tick(.95p0)、U=floor_tick(1.05p0)，raw/actual均需在域；每Fill min1/千分一HALF_UP | EXECUTION_PRICE_AND_FEES；paid+余单H≤F，F默认10，不临时加宽，有利极端卖gap也不成交 |
| P5-D04 容量/限价/期限 | 每证券每开盘合成固定10share容量，共享；历史ADV门槛显式冻结且仅用此前可见量。MARKET/LIMIT，DAY/GTC；LIMIT只在可见开盘参考和最终滑点价均满足limit时成交 | DAY到本session收盘到期；GTC在锁定截止session收盘到期，cancel确认优先于后续match；无成交不伪造胜率 |
| P5-D05 交收 | T+1下一calendar开盘；C_set/U_free/U_short互斥；short所得交收同时进入C_set/S_set，A不变 | CASH_BUCKETS_AND_PROJECTION；未交收cover释放只转U_free、不能提前花；buy可售另算 |
| P5-D06 行动与修订 | 已公告且生效时先拆股，再ex红利资格，再交易；持仓before-action享受，开盘后新买不享受，同刻卖前先确认；PER_OLD_SHARE以前一session收盘锚定，pay>=ex、应收不再投，空头同额应付 | P3 U002只供对照，不能充当本阶段批准。行动必须在effective前已可见；迟到/经济修订生效已过则停止运行标DATA_REVISION_REQUIRES_RERUN，不倒改历史账本；只在新快照新run受审后重算 |
| P5-D07 多空 | short所得按FIFO cashlot限制，分U_short/S_set；M=当前short市值；收盘每证券年1%/252费HALF_UP后给当时未平lots | 无新prefunding；FIFO_ATTRIBUTION冻结历史费用/股息归属，margin breach明确失败，无融资/自动强平 |
| P5-D08 估值/退市 | RAW mark；停牌持仓保留最近已知有效mark，stale超过1个session则运行失败；零价不能代缺失。已知明确合成delist回收价事件才清算，否则FAIL UNRESOLVED_DELISTING | 未知退市不能抹仓/按零归因；有持仓完整报告旧mark和未决损失 |
| P5-D09 账户到P4 | B=U_free+U_short+O+P_res+F_unused；nonshort=Z+max(S_set−V,0)；P4free=A−F_unused−H | CASH_BUCKETS_AND_PROJECTION，H仅预算保守量，不是真实现金冻结；完整双风险，不改P4 API |
| P5-D10 统计 | A252/ddof1/rf/TWR不变；CLOSED_FIFO_FRAGMENT计数，精确历史lot费用/红利池，pay不重计 | FIFO_ATTRIBUTION；partial/cross-zero/无完成/赢家/亏损/零利润原因唯一，待主审/用户接受 |

所有有效权限/输入未知时拒绝。上述提案均需 GPT Work 固定 SHA 审查，涉及经济口径由用户在后续实施授权中明确接受或修改；G1不能替代用户金融批准或部署授权。冲突在 OPEN_QUESTIONS.md 登记，未解阻断不开始实现。
