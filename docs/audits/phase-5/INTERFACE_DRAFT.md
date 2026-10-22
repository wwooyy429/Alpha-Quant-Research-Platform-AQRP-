# P5 接口草案 · simulation/1.0.0-proposed

所有签名是 G1 候选，未实现。对象严格 schema_version、UUID run/request/event/order/fill id、UTC微秒、CCY/share、精确十进制字符串；拒绝未知字段、非有限数、重复逻辑键、路径逃逸、别名/链接替代、不同币种或父快照。值/身份/权限错误先失败，不能吞掉后返回空成功。

`simulate_engineering(EngineeringBacktestRequest, SignalProvider, PortfolioPolicy, RiskPolicy, ExecutionModel) -> BacktestResult`；`simulate_approved(...)` 为独立正式入口，缺真实金融依赖明确拒绝。不得添加 skip_approval 或默认 fallback。配置锁定初始账户、日历、信号P3运行清单、精确因子/参数/stage、P1 snapshot_ref、execution_slice_ref、行动/交收/费用/容量/profile、时间段、seed、风控、mark/stale、绩效conventions及全部文件hash。

应用编排器 `prepare_signal_provider` 只从受信终态 P3 manifest 读取原始 engine/config/final 和实际 P1 manifest+八表，验证 UUID 与 hash 双绑定；每个历史 decision 的信号、主档/分类/股票池/参数拟合版本全部当时可用。预生成信号仅在预注册 decision/available 到来后释放；不向引擎提供 labels/最终Test、未来整日表或 Registry 句柄。替换因子只改 provider 配置，核心不变。拟合与选因子只发生许可开发集，回测结果不反向改冻结配置。

`ExecutionSliceRef` 独立 immutable engineering 侧车：原P1 parent_uuid/hash + calendar/market/security，open logical_time、event_time、available_at、raw_open、tick、synthetic_capacity、status revision/known_at、slice_id、manifest/hash。不得重写 P1 daily bar event_time 或把整日 OHLCV 在开盘开放；生成器仅由工程固定输入产生侧车，完整日bar只供事后核对，不作盘前输入。默认开盘切片是零宽时点，event_time=logical_open且available_at<=logical_open；晚到1us的slice不能倒填open成交，DAY无后续合法slice则到期，GTC只可等待下个可用开盘。信号延迟也不得追补已错过的执行。执行模型单独读已到时切片，信号/组合不能获得未来切片；侧车与真实市场/正式隔离严格区分。

外层调度与逐Fill原子事务以 EVENT_TRANSACTION_ADDENDUM.md 的C-P5-001为唯一候选定义：外层(time,dispatch_phase,dispatch_seq)排序；每个70信封读取最新已提交状态后完成一笔Match/Fill/Account原子事务，80/90是事务子记录local_stage，不是两个全局可交错信封。Journal按commit_seq/child_seq重放，前笔提交后后笔才算candidate。65取消、95收盘借费、100估值完整trace、pre/post版本/hash、容量及崩溃边界见该文档。原P0契约影响及所需用户批准见 CONTRACT_CHANGE_IMPACT.md；冻结文件不改，未批准不实施。

`OrderIntent` 非可执行；`submit_order` 校验信号最晚 available<=decision<=submitted，eligible 必须为严格晚于提交的下一个合法开盘（开盘当刻提交亦顺延），所有下单预留原子化。Order 包含原始目标/信号/风险原字节引用、side/signed_qty、MARKET 或 LIMIT、DAY 或 GTC、limit_price、submitted/eligible/expires、idempotency_key；只在配置明确时开放。MARKET引用切片开盘价，LIMIT只使用该切片观察价作保护，不用当天high/low推断日内成交。GTC跨session重新检查有效性、风险/许可/容量/预留，不延续旧pass令牌。

状态：CREATED→SUBMITTED→ACCEPTED→PARTIALLY_FILLED/FILLED；CREATED/SUBMITTED可 REJECTED，ACCEPTED/PARTIAL可 CANCELLED/EXPIRED；终态不可回退/成交。取消先有确认再撤剩余，已经成交不可消失。剩余=original−filled−cancelled，保留 expired_remaining 另栏，不把未成交作fill。重复Fill/order/cashflow/action受真实event键与内容hash保护。

`match(order, VisibleExecutionSlice, LedgerSnapshot, RiskPolicy)` 对每个拟部分成交先计算真实执行价/费用、预留释放与新资金/借券/settled数量/敞口，任何金融约束不满足则不成交并留原因。稳定 submitted/order_id次序共享容量；同切片按security累计，不能每单重置。先算candidate再原子提交 Fill+Journal+状态+预留，无部分写入。崩溃恢复已提交事件重放幂等，未提交事务无效；manifest/Journal任一损坏失败关闭。

`Ledger.apply(event)->AccountSnapshotV1` 是唯一资金/持仓写入者。包含 cash_total/settled/unsettled/reserved/restricted、signed positions/sellable/borrow/cost、receivables/payables、equity、last_event_seq、valuation_time/markrefs及逐币借贷平衡。P5预留不能与P4估计fee_reserve当成重复扣现。交易可用量与结算日期独立，不把未交收应收当现金。

账户以 CASH_BUCKETS_AND_PROJECTION.md 为准：C_total=C_set+U_free+U_short，S_set仅是C_set子集；真实A=C_set−S_set−M−O−P_res−Z。B=U_free+U_short+O+P_res+F_unused，C_alloc=C_total−B，P4 nonshort=Z+max(S_set−V,0)，fee_reserve=0，P4free=A−F_unused−max(V−S_set,0)。额外H只报告预算保守性，不记真实现金冻结。short开仓/交收/partial cover/跨零/红利迁移均逐项定义，不用U_short重复减S_total。

新rebalance若还有ACCEPTED/PARTIAL旧单，REBALANCE_PENDING_ORDERS拒新调仓，不重复发P4 delta。MARKET/LIMIT和BUY/SELL均使用冻结decision完整双边[L,U]，原open与最终滑点价均须在域，LIMIT只收紧。全部订单提交及逐Fill均校验F_paid+Σ余单最坏fee_upper≤F_total，不拿卖价下界当fee上界，不自动扩大F。实际Fill按真实费付一次，撤单释放余预留不抹已付费。详EXECUTION_PRICE_AND_FEES.md。

P4用预算E_alloc，P5每次提交/Fill用真实E_total和正确现金桶完整重核，两套都通过才成功；保留真实同点P3/P4输入，开盘不能强改旧分数请求时间。上述是待G1/用户接受的新设计，尚未实现。

`reconcile(journal, fills, cashflows, actions, initial_state)` 由独立读侧按原事件重建，不能读取AccountState作为期望；返回每事件/每日金额数量差、借贷差、费用和权益。`performance(equity_series, external_flows, convention_ref)` 只读；精确现金/订单表与float统计分层。`replay(run_ref)` 从终态manifest读取原始字节及精确旧软件包，重新计算声明数值投影与hash；不新增后补文件成为原始运行证据。

BacktestResult 成功含真实journal/account/order/fill/risk/valuation/performance和不可变输入/配置/环境/源码hash；失败/取消保留实际事件和已提交资金，未完成结果不可伪装成功收益报告。现有 CLI 拟新增薄 simulate/status/result/replay，走同一服务；不引入Streamlit。终态后任何附加文件仅旁注，不能取得证据资格。
