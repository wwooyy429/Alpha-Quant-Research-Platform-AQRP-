# Phase1数据SDK

范围data/1.0.0及contracts/1.0.0；SYNTHETIC_V1为合成假设，不能据此推断交易所日历、货币、整手或交收规则。核心批准契约保持原字节，预审计划在380d9f8；下面描述实际实现。

```python
from datetime import date
from pathlib import Path
from aqrp.core.contracts import QuerySpec
from aqrp.data.synthetic import load_synthetic, PROVENANCE
from aqrp.data.snapshot import publish_snapshot
from aqrp.data.query import query

ref = publish_snapshot(load_synthetic(seed=17), PROVENANCE, Path('/your/local/snapshots'))
spec = QuerySpec(('SYN_A:001',), 'SYN_A', 'SYN_A_CAL',
                 (date(2024, 1, 2), date(2024, 1, 3)))
view = query(spec, '2024-01-03T12:05:00Z', ref)
# view.table: independent Arrow buffers; view.to_pandas(): independent copy
```

Windows应传入自己的非同步绝对路径。每个新快照单独ID和manifest hash，已存在ID拒绝覆盖。更正发布新版本；SnapshotRef必须同时保留root、snapshot_id、manifest_hash，不能只保存易漂移的目录名。并发正式查询必须各自显式传入ref/as_of，不维护全局latest或可变连接。

数据集须包含八张有显式schema的表（空行动/调整表也需存在）。validate_table返回规范化表及QualityReport，可审查逐行拒绝原因；validate_dataset及publish_snapshot严格阻断冲突/异常及正式PIT未知available_at。exploratory=True仅允许留存可用性未知原件，所有正式query/lookup仍拒绝该快照。不能用ingested_at倒填历史available_at。

所有timestamp入口拒绝naive、纯日期及非零纳秒尾数。源带偏移时间须与source_timezone的IANA规则一致；规范持久时点为UTC，保留源IANA并以它核对session_date，不把已归一的UTC钟面误当源当地钟面。localize是显式墙钟适配器：DST不存在时点拒绝，歧义必须fold/offset；IANA数据库仅从tzdata==2026.5包读取，两平台一致。date字段session_date仍合法。

query统一校验全部manifest和分片后，先过滤event_time/available_at，再选可见最新修订、判半开生效区间。同一可用时点的冲突修订拒绝；revision_id为单调整数。calendar沿用(calendar_id,session_date)，修订通过快照/版本封存。universe_at/status_at/aliases_at/actions_as_of沿同一约束，公告但未生效行动仅announcements_as_of开放。退市ID和历史记录保留；不以缺bar推断停牌。

QuerySpec支持显式字段、市场、日历、证券及闭区间session_range；非法字段/跨市场/未知ID失败。合法空查询返回有schema空表和NO_VISIBLE_OBSERVATIONS。DataView仅含独立IPC字节、表转换、query_hash及只读血缘，无SQL/底层连接。调用者修改Arrow/Pandas副本不改变同一视图或后续查询；这不是不可信插件OS沙箱。

RAW永不改写。split_adjusted只应用截至as_of已可见且生效行动，历史价格除拆股比、量乘同一比。total_return额外字段total_return_index以所查询有效序列首行1为起点，按(s_t*C_t+d_t)/C_prev毛回报累乘，d按前期旧股口径；原OHLC不变。缺失或断session报错，不跨空档复合。一个session间隔多个不同生效时点的拆股明确Unsupported并报错，须先规范到合成日频口径，不隐式猜测中间公司行动。税费/支付/账户/订单/净收益属于P5，未实现。

价格/金额/数量持久为decimal128(28,8)，source_scale和原量/额/单位保留。合成tick0.01、share_unit1；溢出/不可精确承载的scale、float金额、负量/混币拒绝。统计收益才输出float64；simple_price_return仅G-RET，缺值MISSING、非正价格拒绝。固定Golden及独立Fraction/Decimal参考在tests/golden和tools/independent_reference.py，后者是开发方参考执行，不冒充Gemini。

DuckDB每次从已核验Arrow数据重建内存索引，无权威可变磁盘缓存；性能优化Planned，不改变Parquet持久边界。读取分片先验hash再从同一字节缓冲解码，避免校验后重新打开另一个文件。快照manifest记录源/单位/日历/股票池/行动版本、父ID、键/时段/证券范围及质量计数；自身hash排除snapshot_id/manifest_hash两个顶层字段，ref继续核对ID与hash。
