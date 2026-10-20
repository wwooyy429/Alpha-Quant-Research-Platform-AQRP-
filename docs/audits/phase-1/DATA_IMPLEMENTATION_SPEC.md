# Phase1数据接口与实现约束（待Gemini预审）

本文件细化已批准data/1.0.0和INTERFACES的Data API，仍是实施提案。只覆盖P1，不修改P0核心契约或声明SDK已实现。

## 类型与存储

- 使用Python 3.13.16标准GIL x64。P1公共对象为经入口验证的冻结dataclass/枚举；Arrow schema是持久类型边界，不靠Pandas隐式index或自动dtype推断约定主键。
- timestamp字段为Arrow timestamp[us, tz=UTC] / DuckDB TIMESTAMPTZ；source_timezone保存IANA名称，session_date是本地交易日date。源时间必须带时区并与source_timezone一致；纯日期、naive、DST不存在/无明确fold或offset的歧义时间拒绝。
- 输入超过微秒的非零尾数应拒绝，不能默默截断；合法零尾数可精确归一为us。DuckDB会涉及精度/时区转换，必须往返核对，不能以显示格式证明时区保留。
- 合成profile `SYNTHETIC_V1`：market_id、venue_mic和currency均为显式测试标识，不宣称合法交易所MIC/真实货币。单币种；Decimal128(28,8)用于价格/金额/股数/成交量，另存source_scale及原单位。乘除使用扩展Decimal context，最终scale/tick策略在profile固定；溢出或不能精确承载的源精度拒绝，不先转float。
- 合成示例报价tick=0.01、share最小单位=1、金额最小单位=0.01；数据不含账户/撮合，测试不会据此推定真实整手、费用或交收制度。其他profile可声明不同精度，未知profile报错。
- 逻辑表/物理键继承DATA_CONTRACT；P1实现security_master、symbol_alias、calendar、bars_daily、security_status、universe_membership、corporate_actions、adjustment_factors。classification为P3、fundamentals为POST7，不创建空实现冒充支持。

## P1 SDK输入输出

| 接口提案 | 输入→输出 / 必须检查 |
|---|---|
| load_synthetic(spec, profile) | 固定输入或seed、显式sessions→规范化候选表+QualityReport；无网络、无当前时间决定历史数据 |
| validate_dataset(tables, profile) | 类型/键/单位/日历/时序→accepted/quarantined/rejected/missing等分类及逐行原因；冲突/非法数据不能静默发布 |
| publish_snapshot(tables, provenance, destination) | 已验证表+完整元数据→SnapshotRef；临时目录写入、校验、原子封存；已存在snapshot不得覆盖 |
| verify_snapshot(ref) | manifest/schema/所有分片hash/键与范围→通过或SnapshotMismatch；损坏不降级继续 |
| query(QuerySpec, as_of, snapshot_ref) | 显式security_ids/market/calendar/fields/session_range/price_basis和锁定decision_time→DataView；入口统一强制PIT |
| universe_at / status_at / aliases_at | 指定对象、as_of、snapshot→当时可见且有效的成员/状态/ID映射；保留退市历史 |
| actions_as_of | as_of、snapshot→当时已知且生效的行动；已公告但尚未生效者仅独立announcement视图返回，不能提前进入调整视图 |
| simple_price_return | 已验证的前/后Decimal价格→无量纲float64收益和validity；仅计算current/previous−1，缺值明确MISSING、非正前价报错；不实现因子、IC或策略绩效 |

DataView包含独立的只读Arrow结果、显式schema、质量计数、snapshot/query/profile/calendar血缘与排序规则；不得提供全量连接、原始SQL或可变缓存句柄。Pandas转换返回独立副本，输入可变对象更改不能修改已封存数据或后续同键结果。此API隔离不是不可信插件OS沙箱，后者仍P2及D-006范围。

QuerySpec非法字段、跨币种、未知市场/profile、无效区间、非法as_of应报显式ContractError/UnsupportedCurrency/DataQualityError，不把错误转换为“成功空表”。合法但无观测返回有schema的空结果及原因；本阶段不用标签/因子/账户对象作为查询输入。

## PIT与修订选择顺序

1. 先锁定和验证snapshot/profile/calendar，拒绝EXPLORATORY_ONLY快照进入正式PIT查询，未知available_at不能用ingested_at回填。
2. 对bars先筛event_time<=as_of且available_at<=as_of，再按逻辑键选择当时最新可见revision；同一可用时点出现冲突修订应拒绝，不靠输入顺序任取一行。revision_id采用明确规范的单调整数而非字符串字典序。
3. 对成员、状态和别名同样先筛可见修订，再计算effective_from<=as_of<effective_to。未来才公布的effective_to或退市/换码信息不得从最新版泄入历史。calendar保留P0的(calendar_id,session_date)唯一键，修订以新calendar版本/快照承载；先校验固定日历版本及公告可用性，不从最新日历回填，也不擅自加入破坏唯一键的revision列。
4. 日历session终点与bar event_time一致。源bar早于收盘可用、非法session、事件未来但声称已有完整日bar等均拒绝。公司行动announcement_time和effective_at分开，未来已公告行动不能当作当期已生效行动。
5. 所有读取路径均执行上述规则，缓存键含snapshot、as_of、字段、市场/日历/profile、price_basis和规则版本；不提供绕过PIT的快捷查询。
6. 结果排序固定(event_time, security_id, revision_id)，逻辑PIT投影每证券每session至多一条bar。超出查询范围的记录不进入聚合或先做全量填充再过滤。

## RAW、拆股及总回报视图

- 原始bars永远保持RAW，原股数/源单位与行动版本保留；P1不模拟行动记账、持仓变化、应收支付或撮合。
- split_adjusted：只用as_of时已知且已生效的拆股，按目标截止session的股本基准，将此前价格除以累计拆股比、此前量乘相同比；1:2拆股前100/10股→研究50/20股，RAW仍100/10。未来行动不能改变旧cutoff结果。
- total_return：采用显式合成的毛现金分红在ex-session收盘再投资假设，构建从首个有效close开始的研究指数。无缺失情况下，I_t=I_(t-1)×(s_t×C_t+d_t)/C_(t-1)，s为新/旧股数比，d为每旧股当期现金分配。无行动s=1,d=0；profile必须声明现金单位及归属基准，无法规范化或精度溢出时失败，不擅自合并行动。
- 例如拆股100→50、s=2,d=0，毛总回报0；分红100→98、s=1,d=2，毛总回报0。现金分红只计一次；不再叠加dividend到total_return输出。原始价格收益分别-.5和-.02，与研究总回报不同。
- 只使用两端可见且可用行动；缺前价、零/负前价、未知行动或跨缺失session按明确quality/error处理，不随意跨缺口复合。税、支付/交收、空头股息与账户权益留P5，不将研究指数当作可执行净收益。

## 合成日历及质量

sessions为小型显式版本表，含local session_date/open/close、available_at；可选Asia/Shanghai或America/New_York等IANA时区仅用于测试转换，并非真实交易所假日认证。固定样例包括半日、非交易日、夏令时前后及UTC日期与本地日期不同的session。

OHLC正值且满足low<=open/close<=high；volume/amount>=0；零量合法但不推断可成交。null保留并标MISSING，不填0、不推断停牌；停牌由可见状态表指定。同物理键完全相同重复行去重并记录，冲突重复隔离且阻断发布。输入总数必须等于各互斥处理分类之和；“null字段数量”与“缺失行数量”分开，不能重复相加凑守恒。

## 快照、哈希与可重现性

manifest记录版本/父快照、逻辑表及文件相对路径/hash/行数、源及单位、证券/时间范围、schema/calendar/universe/actions/profile版本；canonical UTF-8 JSON排序键，禁止NaN。snapshot_id/hash字段本身不参与自身hash，schema固定排除字段清单，不能用自引用占位符。

路径必须解析到指定快照根下，拒绝绝对路径、../及符号链接/重解析点越界。只在校验全部分片后开放查询；manifest和数据封存后不改，更正另建版本。DuckDB缓存可重建，但校验源manifest后才使用，不能把缓存当唯一权威版本。

跨环境验收分别比较逻辑数据及物理文件：固定已封存快照的文件hash应完全一致；不同平台重新生成文件时只在固定writer/环境证据下比较物理字节，正常逻辑结果必须一致，不能预先承诺所有Parquet生成字节跨平台相同。future mutation使用新快照，完整snapshot_id/query_hash可因数据版本改变；需比较过去可见的规范化值投影hash，而不是错误要求整个快照ID不变。

## 一般错误及接口兼容

复用P0的ContractError、DataQualityError、SnapshotMismatch、TimeLeakageError及明确UnsupportedCurrency等分类；新增错误需给出code/字段定位/可重试性。若实现发现上述细化与已批契约冲突，先记录受影响ID/接口及迁移方案交Gemini与用户，不直接改DATA_CONTRACT/INTERFACES以迎合实现。
