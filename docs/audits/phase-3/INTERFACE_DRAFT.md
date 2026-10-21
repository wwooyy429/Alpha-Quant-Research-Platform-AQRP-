# Phase3 接口草案（加法设计，未实现）

继承contracts/1.0.0的证券/市场/单位、UTC微秒、event_time/available_at/decision_time。字段/内容hash、artifact原字节hash和配置JSON规范化必须复用P2已修规则；不将路径相关query身份当可跨位置相等的逻辑结果。

| DTO / 服务 | 必填内容 / 规则 |
|---|---|
| ExposureSnapshotRef / exposures_as_of | 侧车manifest/schema/hash/parent P1 snapshot、currency/unit/profile；行含security_id/market_id、effective interval、event_time、available_at、revision、industry分类版本、正有限market_cap、可选beta；先PIT过滤再取修订，缺失不补0。行业/市值来源必须绑定当时版本，禁止最新分类回填 |
| Price-Volume FactorSpec | 提议新固定ID price_volume、Factor API兼容范围显式；需close+volume及L+1连续可见session。公式=(C_t/C_(t-1)-1)*(V_t/mean(V_(t-L)..V_(t-1))-1)。历史均量0/缺口/晚到按原validity+reason。现有FactorSpec对required_fields和allowlist需加法扩展并审查；不静默复用旧bundle hash |
| ResearchProtocolRef | immutable protocol_hash、family/全候选/方向/参数/处理链/期限、数据及历史股票池、split/label、purge/embargo、min_n、HAC lag/假设/方法、family m与校正、访问/实验预算、预设通过标准、冻结时点及批准证据；缺正式标准仅EXPLORATORY |
| ResearchRequest | exact FactorRefs、SnapshotRef/ExposureRef/UniverseSpec、逐日decision schedule、ProtocolRef、PipelineSpec、LabelSpec、SplitSpec、seed、purpose、evaluator capability ref；不把Test路径/标签塞进factor context |
| StageScores | (signal_time,security_id,factor_ref,params_hash,stage)、score/validity/reason、PIT lineage、fit_window和参数hash、输入/输出计数。raw/clean/standardized/neutralized/final均有真实artifact或SKIPPED+input_ref |
| LabelSpec / LabelBatch | h正整数session、entry=t+1 open、exit=t+1+h open、RAW+可见行动总收益约定、start/end/available_at、status；按证券/日历，停牌/退市/缺价无法定价为null+reason，不填0；label仅评估端可读 |
| SplitSpec | 时序Train/Validation/Test半开session范围；标签信息闭区间交叠purge；embargo显式session数；walk-forward每窗fit/eval边界和重叠样本去重，不能随机shuffle或用Test拟合 |
| MetricResult | value/null、n/reason、stage/horizon/universe/split、原始/校正p、假设/lag/min_n/不确定性、有效/缺失日和pair计数；不将ICIR当t统计量或经济可交易性 |
| ExperimentLedger | 原子start UUID→append events→terminal；完整canonical配置及code/data/env/seed/protocol/权限/规则成本（P3 NOT_APPLICABLE）hash、全部候选/失败/淘汰/验证访问/重复指纹；相同run不可覆盖，实际文件SHA256核对，终态不能逆转 |
| TestEvaluator | 独立于开发研究/标签对象的权限服务；开始评估前锁定candidate+protocol+data+approval，原子消费Test访问预算；按Test数据身份而非可重命名family/run识别污染，结果只回授权评审主体，开发端不得读标签/反馈。部署边界详DESIGN_DECISIONS，不把role字符串或隐藏Python属性当物理隔离 |
| research / reproduce / compare | 同服务供薄CLI；RUNNING/SUCCEEDED/FAILED/CANCELLED状态，错误/取消也留证据。缓存键全量绑定code/bundle/data/query/split/stage/fit/params/方向/horizon/seed/权限域，Test和开发缓存物理或权限隔开 |
| ApprovalProposal / record_decision | 冻结标准+实际指标/不确定性/校正+全部试验/访问+独立Golden及审查证据；标准/审批身份不足返回拒绝原因，不自动批准。P3只可研究有效性，StrategyApproved需要P4/P5，未实现绝不授予 |

普通开发请求只持Train及协议允许的Validation能力，不持Test标签对象/存储句柄。最终评估只有在隔离profile可验证、单次授权、候选冻结后受控执行。异常/系统失败返回结构化错误并写失败run；合法小样本/缺数据返回null+reason，不伪造成功统计。
