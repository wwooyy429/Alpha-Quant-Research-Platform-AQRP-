# 统一数据契约 data/1.0.0（设计提案）

适用于数据、因子、研究、组合、回测、CLI、网页与比赛适配；不得私设单位或时间定义。关联 DATA-001–013、EXP-001、BT-001。所有示例仅为合成设计案例。

## 通用规则

- 唯一证券标识 `security_id: string` 是稳定内部 ID，不使用可复用 ticker 作主键；`symbol` 仅显示/兼容字段。`market_id`、`venue_mic`、`asset_type`、`currency` 必填。代码变更/交易所迁移通过带生效区间和可用时间的 alias 表映射；不把同代码不同市场合并。
- 价格/每股现金分配以 `currency/share`；股数、成交量统一为 share；amount 为 currency；收益/权重为无量纲小数，10% 写 0.10；费率与滑点分别声明 decimal/bps，1 bps=0.0001。不把“手”“万股”“千元”直接导入。适配层保留原单位及转换证据。
- 持久金额与数量使用定点 Decimal（Parquet decimal128，精度/scale 由市场 profile 固定），价格保留源精度；禁止先将现金转二进制浮点再记账。单币种最小货币单位与四舍五入规则在运行前固定；统计向量 float64，缺失用 null，不用 0。MVP 只支持单币种账户，混币/FX 未实现时报 UnsupportedCurrency。
- 所有 timestamp 是 UTC 的带时区微秒时间戳；源时区必须为 IANA 名称，不接受无时区时间。session_date 为所属交易所本地交易日，不能从 UTC 日期直接推断。日历包括开闭市、集合竞价（若适用）、半日、假日、夏令时及特殊休市，必须版本化。
- schema_version、snapshot_id、source_id、source_record_id、ingested_at、quality_status 为公共血缘。event_time 是经济事件发生时点；available_at 是该条记录当时首次可被系统合法获得的时点；ingested_at 是本次抓取时点，不能伪装历史 available_at。历史可得性无法验证则标 UNKNOWN_AVAILABILITY，禁止进入正式 PIT 策略。
- decision_time 由调用方指定并锁定，不是查询机器的当前时间。PIT 同时满足 `event_time <= decision_time`、`available_at <= decision_time`；修订按该时点最新可见 revision 选择。未来已公告但尚未生效的公司行动单列 announcement_event，不提前写入已生效账本。

## 逻辑表与唯一键

| 表 | 唯一键（同一快照内） | 主要字段与约束 |
|---|---|---|
| security_master | security_id, revision_id | market/venue/currency、listing/delisting 时间及 known_at；源别名不复用 ID |
| symbol_alias | market_id, symbol, effective_from, revision_id | security_id、effective_to、available_at；区间不冲突 |
| calendar | calendar_id, session_date | open_at、close_at、版本、公告可用时间 |
| bars_daily | security_id, session_date, revision_id | event_time=该 session 结束；OHLC、volume、amount、available_at、price_basis=RAW |
| security_status | security_id, effective_from, revision_id | suspended/delisted/tradable、effective_to、available_at、原因 |
| universe_membership | universe_id, security_id, effective_from, revision_id | effective_to、available_at；按当时可见组成查询 |
| corporate_actions | action_id, revision_id | security_id、type、announcement_at、available_at、effective_at、ex_date、record_date、pay_date、split_ratio、cash_per_share、currency |
| classification | security_id, effective_from, revision_id | 行业、流通市值/暴露观测、available_at，不用最新分类回填历史 |
| fundamentals（后续） | security_id, field_id, period_end, revision_id | announcement_at、available_at、value、unit；会计期结束不等于可用 |
| adjustment_factors | security_id, effective_at, revision_id | ratio、action 引用、available_at、调整方法及视图截止时点 |

修订物理键保留全部 revision；逻辑 PIT 视图一证券一 session 一条有效 bar。完全相同的重复行可去重但留计数/来源；冲突重复进 quarantine 并失败，不任取最后一行。排序固定 `(event_time, security_id, revision_id)`；输入源无序不影响结果。

## 复权、公司行动与可交易性

原始成交价 RAW 为撮合和账本唯一价格基础。研究视图可选 split_adjusted / total_return，但必须记录方法、截止时点及行动版本；不得使用未来拆分/分红反推过去可见视图。不混用复权信号价格和复权后股数撮合，也不在 total-return 标签外再叠加分红。

拆股在 effective_at 原子改变股数与单位成本，不改变总账面成本；未成交订单数量/价格是否调整由 profile 明确。分红在 ex-date 确认应收/空头应付，在 pay-date 结算现金；权益含应收应付。税费、碎股、红利资格、资金交收由市场 profile 指定。尚无批准 profile 时只支持 Golden 中明确的合成假设，不声称符合任何交易所规则。

停牌不以缺失 bar 推断；状态表主导，可见的停牌/退市不可交易。历史股票池按 effective interval 与 available_at 双重约束，退市证券保留，禁止幸存者偏差。无成交且价缺失不填 0；估值沿用最近有效 mark 时必须标 stale、账龄及阈值，超过阈值按 profile 阻断/警告。退市回收价/现金流未知时标未解决，不无依据按 0 清算或删除持仓。

## 缺失及异常语义

quality_status 枚举 VALID、MISSING、INSUFFICIENT_HISTORY、SUSPENDED、INVALID、STALE、UNKNOWN_AVAILABILITY；reason_code 与原始值伴随。OHLC>0、low<=min(open,close)<=max(open,close)<=high；volume/amount>=0；0 volume 允许但不证明可成交；非交易日 bar、负价、冲突币种/时区拒绝。缺字段和空表区别；无效证券不能跨组前向填充；禁止静默删除大量数据。

每次处理保存输入数、每类拒绝/缺失数、处理规则和受影响证券/日期。缺失收益不当作 0；因子 lookback 不足标 INSUFFICIENT_HISTORY；统计成对删缺失并报告 n；组合缺信号不自动平仓，具体动作必须配置。跨市场日频对齐按可见 session 和 UTC 时点，不能简单同日期拼接。

## 快照及版本

snapshot manifest 包含 snapshot_id、schema_version、父版本、源文件/分片路径、每片 SHA-256、行数、时间范围、证券范围、源授权/获取信息、单位映射、日历/股票池/行动版本和整份 canonical manifest 哈希。数据与 manifest 封存后不可修改；更正生成新快照。验证先检查文件哈希、键、单位、时序与 PIT 完整性，失败不能降级静默继续。

`available_at` 不可信的历史供应商数据是显式外部风险，不能凭 snapshot 哈希证明其历史真实性。研究及正式模拟分开标识 `PIT_VERIFIED` / `EXPLORATORY_ONLY`。
