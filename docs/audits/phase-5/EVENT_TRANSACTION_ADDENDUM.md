# C-P5-001 · 外层调度与原子成交事务提案

处理WORK-P5-G1-001。这是待G1复核、待用户明确接受的契约细化/变更提案，**不修改冻结BACKTEST_CONTRACT.md，不宣称原契约已经包含该解释**。影响/批准见CONTRACT_CHANGE_IMPACT.md，未获所需批准不实施。

仅外层调度信封进入全局队列，key=(logical_time_utc, dispatch_phase, dispatch_seq)。phase=10行动/结算、20行情确认、30信号、40决策、50风控、60提交接受、65取消/到期确认、70 MatchTransaction、95收盘借费、100估值。10内部settlement→split(action_id)→ex-dividend(action_id)→dividend-pay；禁止高phase执行中回插同刻低phase，缺前置/后到则顺延合法时点或失败。

同一slice按(submitted_at,order_id)稳定生成每单70信封；order_id由run内规范decision/ref/submit索引确定性UUID生成，重放使用原ID。共享capacity只有一份。每个70信封出队后才串行读取最新已提交account_version/order/reserve/capacity及hash，再算**一笔**实际price/fee/qty、释放本单相应预留、构造候选post账户，按候选真实权益重算单票/gross/net/行业/Beta/现金/settled/借券/lot等全部风险。不得先用旧状态预计算多笔candidate或复用旧pass。

通过后Fill、Journal、AccountUpdated、订单/费用预算/共享容量和收据一次原子提交。Fill与Account是该70事务内local_stage=80/90的子记录，**不再是全局可交错的两个信封**。前笔事务完成才允许后笔70计算。风险失败无Fill/无费用/不扣容量，已ACCEPTED/PARTIAL订单合法转CANCELLED(RISK_RECHECK_FAILED)，余预留释放与诊断同事务提交；不添加原状态机没有的ACCEPTED→REJECTED。价格域不符则MATCH_SKIPPED_PRICE_DOMAIN，等下一合法slice/到期，不收费。

外层排序key、持久化key分开：提交递增commit_seq，事务子记录key=(commit_seq,child_seq)，保存parent_dispatch_key、local_stage、causation、pre/post_version和hash。Journal按已提交commit_seq/child_seq重放，禁止用显示local_stage重新全局排序。无状态变化的市场/skip/零借费记录保存外层key与read_version，不虚增account版本。65取消已确认的单不能进70；70执行中收到、available_at等于当前logical_time的取消请求不能回插同刻65：本profile统一在下一个UTC微秒确认65，本刻其他70先完成；记录requested_at与ack_at及顺延原因，不能抹已成交。声明available_at小于当前logical_time的迟到控制输入直接STALE_CANCELLATION_TIME拒绝，不能任择两套执行次序。

准备文件不等于提交。提交标记绑定完整事务字节/hash；提交前崩溃恢复pre_version，资金/Fill/容量均未消费；提交后恢复post_version，重试同ID同字节幂等、异字节冲突。不发布没有同事务账本的成功Fill，终态manifest不完整失败关闭。95只在收盘、20确认mark之后原子记借费，100读取最后提交版本。

固定trace：初始C1000/q0/E1000，A/B各buy1@实际100 fee1，C为待取消单，预留A101+B101+C51=253，容量10，单票上限.15。本例直接给实际价，是调度/风险子案例。
- 开盘Market20；CancelC65：v0→v1，预留253→202。
- A70读v1；post C899/q1/E999，100/999≤.15，内部Fill80→Account90一次提交v2，预留101/容量9。
- B70读v2；候选C798/q2/E998，200/998>.15，无Fill；取消B、释放101后提交v3，C899/q1/E999/容量9不变。
- 开盘Valuation100读v3。同日收盘Market20→既定信号/决策/提交（新单只可下个open）→取消/到期65→Borrow95（本例无short，fee0不增版本）→Valuation100。非零95费用另有补充案例。
- A提交前崩溃：恢复v1/预留202/容量10/Fill0；提交后崩溃：恢复v2/预留101/容量9/Fill1，A重试无第二次扣费，B仍读v2拒绝。

这些是唯一候选调度/审计语义和预先期望trace，尚无P5产品实现或恢复测试结果。
