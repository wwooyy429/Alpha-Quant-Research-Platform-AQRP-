# 接口契约清单（仅设计；contracts/1.0.0）

所有公共对象带 schema_version、run_id 或查询 request_id；金融单位与 UTC 微秒时间、null/quality 语义继承 DATA_CONTRACT。禁止 DataFrame 的隐式索引成为唯一标识。结构签名是提案，不是已实现 SDK。

## 公共错误与兼容

ContractError（结构/单位）、TimeLeakageError、DataQualityError、SnapshotMismatch、InsufficientHistory、UnknownFactor、DuplicateFactor、IncompatibleVersion、UnapprovedFactor、UnsupportedCapability、InfeasiblePortfolio、RiskRejected、InvalidOrderTransition、ReconciliationError、ImmutableRunError。错误包含 code、字段/事件定位、request/run_id、可重试性；不能吞掉后返回“成功空结果”。业务无效观测用显式 validity；系统/契约异常失败并保留日志。API/数据/因子各自 SemVer，兼容区间由声明和测试证实，禁止自动加载 latest。

## Data API（P1）

`query(QuerySpec, as_of, snapshot_ref) -> DataView`。QuerySpec 含 security_ids、market/calendar、fields、session_range、price_basis。输入 as_of 为锁定 decision_time；服务校验 manifest 并只开放 event/available 双约束下版本，返回确定排序、schema、缺失/拒绝计数和 query_hash。DataView 为只读、无底层全量连接句柄的受限视图，不能用 where 子句由调用方自行保证 PIT。`universe_at`、`actions_as_of`、`status_at` 同样约束。

标签生成 `make_labels(LabelSpec, evaluation_cutoff, snapshot)` 在 Validation 专用服务；不向因子运行上下文暴露，标签必须记录 start/end/available_at。as_of 查询不能被后续标签缓存绕过。

## Factor API（P2）

`FactorSpec`: factor_id、factor_name、factor_version、parameters（类型、默认、范围、schema）、required_fields、lookback_window（session 数和端点）、supported_frequency、signal_available_time（结构化规则/延迟）、output_unit、factor_direction（+1/-1，预注册）、implementation_version（内容哈希）、api_compatibility、data_contract_version、review_ref。

`Factor.compute(view: DataView, context: FactorContext) -> SignalBatch`；context 含 decision_time、snapshot_id、immutable params、security_ids、seed、computation_id。只读与确定性；禁止副作用、账户访问、网络数据、未来数据和改其他因子。lookback 按每证券 session 单独滚动，不跨证券拼接。

Signal 行：signal_time、security_id、symbol（展示）、market_id、factor_id/version、factor_value float64/null、available_at、validity/reason、snapshot_id、params_hash、run_id、computation_id、implementation_hash。逻辑键 `(run_id, factor_id, factor_version, params_hash, security_id, signal_time, processing_stage)`；重试相同结果幂等，不同结果同键报错。available_at 不早于所有依赖及计算完成的模拟逻辑可用时间。

`Registry.register(reviewed_artifact, spec)`、`resolve(exact_ref)`、`validate_compatibility(ref)`、`deactivate(ref)`、`rollback(approved_ref)`。同 ID/version 对应内容不可变；重复相同哈希幂等，不同哈希拒绝；新版本重新登记。Candidate→Reviewed→Validated→Approved→Deprecated/Disabled，每次状态转换附审批者/证据；registry 的 Approved 不等于用户阶段批准。运行中 pin 不被停用/回滚静默改变，紧急停用只允许显式终止运行并记录。

Momentum（P2）：lookback L 的 split-adjusted close_t/close_(t-L)-1，含当前已确认收盘，L+1 有效 session；Reversal 为负的对应收益，两者内置 factor_direction 建议均+1，不能再重复取反。Volume 基础因子为 volume_t/mean(volume_(t-L)..volume_(t-1))-1，前 L 个有效 session，分母为0标 invalid。Price-Volume（P3）提案为 `(close_t/close_(t-1)-1) * (volume_t/mean(volume_(t-L)..volume_(t-1))-1)`，使用同一PIT拆股处理的价格和统一share成交量；不能仅用 Volume 冒充。所有公式、窗口及方向均待独立审批与数值答案核对。

## Research / Validation（P3）

`research(ResearchRequest)->ResearchResult`，请求含 FactorRefs、Data/UniverseRef、预注册 ProtocolRef、PipelineSpec、LabelSpec、SplitSpec。按配置保留 raw/clean/standardized/neutralized/final 五阶段，未启用处理标 SKIPPED 并保留血缘，不能把占位值宣称已中性化。结果含 IC/分层/衰减/相关/OOS、n、异常、处理统计和产物哈希。标签只能在评估端读取。

`validate_for_approval(candidate_ref, frozen_protocol, evidence_refs)->ApprovalProposal`；正式批准还需人工批准记录。预测期限/方向/预处理/参数任何改变都是新实验，不覆盖旧 run。

## Portfolio / Risk（P4；P5对接实际账户）

`construct(ApprovedScores, UniverseView, AccountSnapshot, Constraints)->TargetPortfolio`。输入需统一 decision_time、币种、snapshot/version；分数与证券键对齐。输出 target_weights、target_quantities（可选）、残余现金、gross/net/beta/industry、约束诊断、rounding/residual。Long-only 的 sum(w)<=1；long-short 的 gross=sum(abs(w))、net=sum(w) 分别约束。不可行必须明确返回 infeasible，不偷改风险限值。

`check(target_or_order, account, market_profile, decision_time)->RiskDecision`，含 pass/reject、每约束当前值/阈值/缺数据、原因。行业/Beta 缺数据不能视为0；借券许可、可售数量、单票/杠杆/换手/敞口全部检查。P4 用明确的 AccountSnapshot 夹具验证纯组合，不能声称真实 P5 账本已运行。

P4基础权重规则提案：最终分数为预注册因子权重乘以相应stage分数之和，因子权重按绝对值和归一化；缺失分数默认排除该证券，报告有效交集，不隐式补0或临时重分因子权重。Long-only选定top-K（并列以security_id稳定排序，保留tie标记），等权为1/n；分数权使用max(score,0)/sum(max(score,0))，分母0时全现金并记录NO_POSITIVE_SCORE，若约束禁止全现金则infeasible。选择/标准化规则均在开发期冻结。

Long-short以配置的gross G、net N计算long预算(G+N)/2、short绝对预算(G−N)/2，须G>=abs(N)；top/bottom集合不重叠、借券可用。每腿可等权或对中心化分数的正/负部分按绝对值归一，某腿无有效分数而预算非0即infeasible。不是把long-only输出改个标签。

目标权重按权益换算数量，按lot向0取整后重算现金和所有约束；残余现金显式保留，不用取整后违规权重替代原约束。单票/gross/net/杠杆、行业净/总暴露口径、Beta=sum(w_i*beta_i)、预计换手=sum(abs(w_target−w_current))及其半值分别声明。beta/行业缺失、融资/空头权限不足或费用缓冲后资金不足明确拒绝；提交订单和实际撮合时再次检查。P4不实现优化器来强行满足不可能的约束。

## Backtest / Execution / Performance（P5）

`simulate(BacktestRequest, SignalProvider, PortfolioPolicy, RiskPolicy, ExecutionModel)->BacktestResult`，请求锁定账户初态、日历、行情、事件/费用/profile、批准因子引用、时间范围、seed。引擎只读契约化 provider，不解析具体插件。

Order 包含 order_id、decision_id、signal_refs、security_id、side、qty、type、limit_price（如支持）、submitted_at、eligible_at、expires_at、currency、status、idempotency_key。Fill 含 fill_id、order_id、slice_id、execution_time、signed_qty、price、fee、slippage、currency。AccountSnapshot 含现金及冻结/交收、positions/cost、应收应付、权益、event_seq、valuation_time。BACKTEST_CONTRACT 是唯一时序/账本标准。

`reconcile(journal, fills, cashflows, actions)->ReconciliationReport` 与 `performance(account_series, convention_ref)->PerformanceReport` 独立于具体 Alpha。返回权益、订单/Fill/仓位/成本、指标定义、对账差异、风险拒绝和执行假设。

## 应用服务 / CLI / Streamlit（分阶段接入，P6完整）

`submit(RunRequest, idempotency_key)->RunReceipt`、`status(run_id)->TaskState`、`cancel(run_id)`、`result(run_id)->ArtifactManifest`、`compare(run_ids)`、`reproduce(run_id)`。请求使用相同 canonical config 验证器，不在网页重复算法。CLI 仅映射参数，Streamlit 仅映射表单/显示；同等配置的 config_hash、数据血缘与数值产物一致，run_id/墙钟日志不同是允许项。

任务状态 QUEUED→RUNNING→SUCCEEDED/FAILED/CANCELLED；失败产物不可标成功，取消不产生伪造回测结果。Settings 变更只影响新运行，经确认写新配置，不能改旧实验。页面不接受 eval/exec，不上传即执行 Python。

## 实验与比赛接口

`start_run(config_snapshot, lineage)->RunRecord` → `append_event` → `finish(status, artifacts)`，状态只能追加；canonical UTF-8 JSON、排序键、明确浮点/Decimal 表达、拒绝 NaN 后 SHA-256。run_id 使用随机 UUID 并检查唯一；存 code commit、dirty diff/hash、Python/锁文件/OS、数据 manifest、factor hash、split、费用和审批记录。正式复现只允许干净已提交代码和固定依赖；脏代码探索显式 non_reproducible，不能冒充正式结果。

Competition Adapter（P7）仅转换批准规则到标准契约并声明 capability matrix；未知规则返回 Unsupported/外部待定，不能擅自假定 A 股 T+1、限价、借券等。真实执行/网络账户适配属 Production Extensions，另行批准。
