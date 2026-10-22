# P5 接口草案 · simulation/1.0.0-proposed

所有签名是 G1 候选，未实现。对象严格 schema_version、UUID run/request/event/order/fill id、UTC微秒、CCY/share、精确十进制字符串；拒绝未知字段、非有限数、重复逻辑键、路径逃逸、别名/链接替代、不同币种或父快照。值/身份/权限错误先失败，不能吞掉后返回空成功。

`simulate_engineering(EngineeringBacktestRequest, SignalProvider, PortfolioPolicy, RiskPolicy, ExecutionModel) -> BacktestResult`；`simulate_approved(...)` 为独立正式入口，缺真实金融依赖明确拒绝。不得添加 skip_approval 或默认 fallback。配置锁定初始账户、日历、信号P3运行清单、精确因子/参数/stage、P1 snapshot_ref、execution_slice_ref、行动/交收/费用/容量/profile、时间段、seed、风控、mark/stale、绩效conventions及全部文件hash。

应用编排器 `prepare_signal_provider` 只从受信终态 P3 manifest 读取原始 engine/config/final 和实际 P1 manifest+八表，验证 UUID 与 hash 双绑定；每个历史 decision 的信号、主档/分类/股票池/参数拟合版本全部当时可用。预生成信号仅在预注册 decision/available 到来后释放；不向引擎提供 labels/最终Test、未来整日表或 Registry 句柄。替换因子只改 provider 配置，核心不变。拟合与选因子只发生许可开发集，回测结果不反向改冻结配置。

`ExecutionSliceRef` 独立 immutable engineering 侧车：原P1 parent_uuid/hash + calendar/market/security，open logical_time、event_time、available_at、raw_open、tick、synthetic_capacity、status revision/known_at、slice_id、manifest/hash。不得重写 P1 daily bar event_time 或把整日 OHLCV 在开盘开放；生成器仅由工程固定输入产生侧车，完整日bar只供事后核对，不作盘前输入。默认开盘切片是零宽时点，event_time=logical_open且available_at<=logical_open；晚到1us的slice不能倒填open成交，DAY无后续合法slice则到期，GTC只可等待下个可用开盘。信号延迟也不得追补已错过的执行。执行模型单独读已到时切片，信号/组合不能获得未来切片；侧车与真实市场/正式隔离严格区分。

事件总序 `(logical_time_utc, phase_priority, sequence_id)`；稳定因果和事件内容hash，重复ID同字节幂等、不同字节冲突。优先级沿 BACKTEST_CONTRACT 10行动/结算，20行情确认，30信号，40决策，50风控，60提交，70撮合，80Fill，90AccountUpdate，100估值。每个 Fill→完整原子账本提交后才能处理下一Fill；事务组不可被另一订单穿插，不能把所有Fill攒完再更新资金。同刻10内部按 settlement→split(action_id)→ex-dividend(action_id)→dividend-pay。取消确认新增优先级65（提交后、Match前），借券计提新增优先级95（当期收盘行情已确认且当刻Fill/账本处理后、估值前）；borrow费用自身是原子Journal事务，不能在10阶段偷看20才确认的收盘价。两项是原总序的显式细化候选，须G1核对。

`OrderIntent` 非可执行；`submit_order` 校验信号最晚 available<=decision<=submitted，eligible 必须为严格晚于提交的下一个合法开盘（开盘当刻提交亦顺延），所有下单预留原子化。Order 包含原始目标/信号/风险原字节引用、side/signed_qty、MARKET 或 LIMIT、DAY 或 GTC、limit_price、submitted/eligible/expires、idempotency_key；只在配置明确时开放。MARKET引用切片开盘价，LIMIT只使用该切片观察价作保护，不用当天high/low推断日内成交。GTC跨session重新检查有效性、风险/许可/容量/预留，不延续旧pass令牌。

状态：CREATED→SUBMITTED→ACCEPTED→PARTIALLY_FILLED/FILLED；可 REJECTED，ACCEPTED/PARTIAL可 CANCELLED/EXPIRED；终态不可回退/成交。取消先有确认再撤剩余，已经成交不可消失。剩余=original−filled−cancelled，保留 expired_remaining 另栏，不把未成交作fill。重复Fill/order/cashflow/action受真实event键与内容hash保护。

`match(order, VisibleExecutionSlice, LedgerSnapshot, RiskPolicy)` 对每个拟部分成交先计算真实执行价/费用、预留释放与新资金/借券/settled数量/敞口，任何金融约束不满足则不成交并留原因。稳定 submitted/order_id次序共享容量；同切片按security累计，不能每单重置。先算candidate再原子提交 Fill+Journal+状态+预留，无部分写入。崩溃恢复已提交事件重放幂等，未提交事务无效；manifest/Journal任一损坏失败关闭。

`Ledger.apply(event)->AccountSnapshotV1` 是唯一资金/持仓写入者。包含 cash_total/settled/unsettled/reserved/restricted、signed positions/sellable/borrow/cost、receivables/payables、equity、last_event_seq、valuation_time/markrefs及逐币借贷平衡。P5预留不能与P4估计fee_reserve当成重复扣现。交易可用量与结算日期独立，不把未交收应收当现金。

P4适配（候选，不修改P4原API）：原API不能直接接非零应收应付，也不能令全仓LongOnly凭空支付佣金。必须先生成有来源/公式的独立预算投影，严禁冒充原始账户。设真实现金C、正的未交收卖出款U、既有订单预留O、已确认红利应付P、本次预注册费用预算F（默认10.00 CCY）、原始短卖未平仓所得冻结S、当前短仓市值V、其他不重叠冻结Z。B=U+O+P+F，预算现金C_alloc=C−B，E_alloc=C_alloc+Σ(q·p)，要求C_alloc>=0且E_alloc>0。P4账户用C_alloc/E_alloc，非short restriction=Z+max(S−V,0)，fee_reserve=0（F已在B中排除），保留同一实际持仓/mark/sellable/borrow。P4默认冻结V并额外margin V，因此该投影对S与V取较严预算，不能把B、F或V再次加入restriction。真实总权益仍是E_total=C+Σ(q·p)+R−P=E_alloc+B+R−P；应收R完全不参与下单预算。投影前后原始账户与每个组成项原字节/hash及守恒式均保存，缺项/重叠/负预算拒绝。

P4按E_alloc构建目标，但P5还按真实E_total在提交和逐Fill重查全部实际仓位/权重/敞口/资金/借券规则；任一套失败都拒绝，禁止只挑较宽分母。P4保守预算导致拒绝不是隐藏的优化器。正式输入不允许用该工程预算投影伪装金融批准。G1需独立核含未交收、红利应收/应付、short所得与市值差、手续费预算的完整适配反例。

每次新rebalance若尚有ACCEPTED/PARTIAL订单，明确REBALANCE_PENDING_ORDERS拒绝新调仓，旧单仍按其profile处理，直到完成/取消/到期；不重复发P4全量delta。MARKET买单最差界价=ceil_tick(decision_raw_price×1.05)，卖单最低界价=floor_tick(decision_raw_price×0.95)，LIMIT再收紧，越界不成交。费用最差预留按整数share的最大可能Fill次数quantity，fee_upper=quantity×ceil_cent(max(1,price_upper×0.001))；总fee_upper>预注册F即拒绝，不临时扩大F或缩单。F是决策预算分区，不是额外现金支出，Order reserve只形成一次notional+fee冻结，成交按真实fee扣一次，所有未用预留/预算显式释放。

收盘decision取得新的P3/P4同点输入；开盘撮合只重查账户/市场风险，不把原P4请求强改decisionTime再送其同点分数入口。工程投影和实际P5总账户的双重核对是本阶段新能力候选，尚未实现或通过。

`reconcile(journal, fills, cashflows, actions, initial_state)` 由独立读侧按原事件重建，不能读取AccountState作为期望；返回每事件/每日金额数量差、借贷差、费用和权益。`performance(equity_series, external_flows, convention_ref)` 只读；精确现金/订单表与float统计分层。`replay(run_ref)` 从终态manifest读取原始字节及精确旧软件包，重新计算声明数值投影与hash；不新增后补文件成为原始运行证据。

BacktestResult 成功含真实journal/account/order/fill/risk/valuation/performance和不可变输入/配置/环境/源码hash；失败/取消保留实际事件和已提交资金，未完成结果不可伪装成功收益报告。现有 CLI 拟新增薄 simulate/status/result/replay，走同一服务；不引入Streamlit。终态后任何附加文件仅旁注，不能取得证据资格。
