# P7 拟增薄接口与完整链路 · 设计签名

本文件只有契约草案。复用真实入口 `TaskService.freeze/submit/work/status/result/cancel/register_campaign`、原Registry.resolve、ResearchRequest/research、construct_engineering、simulate_engineering/result_engineering/resume_engineering/replay_engineering，以及原CLI和Streamlit。原公共签名及同一新包内缺省经济请求字节保持，受管工程域的预算拒绝行为按本轮共同准入明确收紧；不承诺旧P6包原地写入/恢复新P7域。不另设交易引擎或把新测试运行器当金融服务。

## 离线通用模拟适配

`AdapterSpec`（候选schema `engineering-adapter/1`）字段：adapter_id、version、scope=ENGINEERING_TEST_ONLY、kind=OFFLINE_SYNTHETIC、approved_profile_id、rule_profile_hash、source_id、source_manifest_hash、source_authority、license_statement、catalogue_revision、snapshot_id/manifest_hash、exposure_manifest_hash、coverage_checksum、market_id/currency/calendar_id及对应版本、supported_request_kinds、capability_matrix_hash、code_commit/bundle/core_lock/UI_lock。这里的source_authority和license_statement是来源声明，不等于独立法律许可认证。不可由网页提交code/bundle/可信根/批准状态等身份覆盖；服务从可信启动配置与核实catalog解析。

本阶段第一通用实现明确限定 **P6受信SYN_A/SYNCCY/SYN_A_CAL工程catalog和已审SYNTHETIC execution profile**，可把其标准序列化输入包及规则映射为原Task请求，不假称任意真实市场都已受支持。标准输入包保留P1八表及其schema/单位/available_at/历史股票池版本，暴露和coverage侧车单独绑定。输入适配不得改写P1历史可见性、替换calendar或从抓取时间倒填available_at；源文件原字节、P1标准化快照与映射收据均保留。输入导入仅由可信本地SDK/CLI配置选择已核标准快照，不开放任意网页路径/上传代码/网络URL。真实源provider和比赛profile没有明确规范时直接返回外部依赖阻断。

`capabilities(spec, requested_requirements) -> CapabilityReport`：每项required规则为EXACT、DECLARED_SYNTHETIC、UNKNOWN_EXTERNAL或UNSUPPORTED。只有与已审合成profile完全相符的工程规则可以运行；UNKNOWN_EXTERNAL、UNSUPPORTED、冲突、缺必填规则均拒绝，不能静默用默认T+1/lot/税/borrow替代。报告保留请求和实际映射值、出处及hash，不用一个布尔掩盖部分支持。

`adapt_engineering(spec_ref, trusted_input_ref, task_draft) -> AdapterReceipt`：只负责验证和确定性映射。AdapterReceipt封存原始输入hash、原始规则hash、字段映射/单位转换（第一实现仅单位恒等映射）、已核catalog版本、完整canonical原Task草案及hash、capabilities结果、范围/拒绝原因。请求仍由原TaskService.freeze冻结；任何必要规则不满足则在submit之前拒绝且无订单/无worker/无新研究试验。Receipt不是批准令牌，也不产生新的研究family。

`execute_engineering(receipt_ref, idempotency_key) -> existing TaskReceipt`：先重新核receipt原始字节和数据/代码/catalog身份，再调用原submit/work；不新增状态机。参数变化必须属于事先登记campaign变体；原12共享候选×期限预算、污染历史、失败/取消不退款不改变。多个adapter ID或新family名不能重置预算。状态和任务成败仍按P6全部必需R/P4/B/全局completion屏障；风险拒绝保留原始P4/P5事实，不能把子run成功升成总Task成功。

共同预算不再依赖原Task预留与legacy trials两个单向扫描。未来由 `experiments/admission.py` 在现 `W/task-control/tasks.sqlite` 建立唯一authority；Task、旧CLI、公共research及直接ledger调用都强制解析受管域，省略TaskContext/令牌或换输出/家族不得回退到另一计数。Task与全N单位准入同一SQLite事务；R子运行可信认领父预留不双扣；取消/失败不退款。完整所有权、幂等、锁序、outbox原字节发布、历史缺损失败关闭及计划slot约束见 [COMMON_BUDGET_ADMISSION_DESIGN.md](COMMON_BUDGET_ADMISSION_DESIGN.md)，具体候选见同名CANDIDATES。

分列requested/admitted/rejected/registered/executed：新共享admitted debit不超过12，第13个拒绝申请保留但不运行研究；原P6历史campaign_attempts及其over_budget计数字面不删除，不把迁移解释当退款。主协议12 charged slots不变；预登记原风险故障夹具单独1-slot严格子限额及主根0研究replay见 [BROWSER_NEGATIVE_PROTOCOL.md](BROWSER_NEGATIVE_PROTOCOL.md)。当前仅设计，001/002仍OPEN，未来实现与严格跨入口行为须新G1及单独用户授权。

`read_adapter_result(receipt_ref, task_id) -> VerifiedResultLinks`：验证receipt→Task原始请求→TaskContext/slots→P3终态与P4实际来源→P5事务prefix/全量清单→completion。只给原始工件引用和读取校验，不能复制一个可变JSON当新真值。输出报告不得从缓存success flag决定金融已知状态；取消/异常仍重读物理账本，缺文件/错桶/错血缘/清单外文件失败关闭。

## 全链验收运行器

`E2EProtocol`含固定commit/dirty=false、精确data/exposure/coverage/FactorRefs、P3 pipeline/split/fit/horizon、原经济/执行profile、组合和风险、seed、campaign全变体、各入口actor列表、允许差异白名单、独立答案hash与容差、预期Task终态、证据收集范围。协议在任何结果前冻结。`run_engineering_e2e(protocol)`按同核请求执行；报告称开发方工程执行，不叫独立G2。

`compare_actors(protocol, original_artifact_roots) -> ComparisonReport`独立读取原字节并先核每条链；金融数量/现金桶/价格/费用/订单/Fill/风险/状态必须精确，研究float遵守原容差。合法但错误UUID必须拒绝，不能作为“run_id差异”忽略。每次actor都有真实P3/R、P5/B及每决策真实P4，保留原physical root与所有权，重放新任务不写原源。

`integration_report(protocol_ref, evidence_manifest_refs)`仅汇总已验证证据；若SDK、任一OS原包、必需真实浏览器或任一阻断用例缺失，工程集成结论为INCOMPLETE/FAILED，不能因为大多数成功而PASS。外部未决和延期项目分别固定为NOT VERIFIED/DEFERRED/NOT AUTHORIZED，不从工程PASS推导金融或真实隔离通过。

主层P3研究19点与P5执行10点通过拟增可选execution_sessions预冻结分离，具体兼容/来源/全Task屏障见EXECUTION_SELECTION_CONTRACT、COMPATIBILITY_IMPACT。它不改P3五阶段/OOS，不跳过实际执行点的风险拒绝；没有字段时保留原P6行为/旧请求字节。

Research/Strategy状态隔离使用原精确Ref与不可变配置：启动时pin的id/version/hash/参数/范围不随Registry后续候选变更自动替换；显式紧急停止按旧契约记录，不能自动升级。未审新代码不进入任何已批准执行环境。修改候选版本的运行测试只使用已审随库版本/只读独立registry夹具，不执行未审任意外部插件。实际OS权限验证不属于此接口或本轮实施授权。

## 原审3c34e3c之后的强制准入接线

共同authority API草案为 resolve_domain / admit_all_units / claim_unit / materialize_outbox / verify_history，TaskState复用同一connection，ledger不反向import TaskState。受信P7执行计划由已审本地runner冻结并绑定W；actor激活、UI随机key首次绑定、legacy无幂等参数时的固定slot映射与恢复必须按COMMON_BUDGET设计，不接受网页自报purpose/slot当权限凭证。新的普通研究观察必须先准入，不能在登记前命中缓存或评估。独立standalone旧P3原family/budget保留，不作为受管W跨入口证明。具体新增API、计划激活和兼容路径都列入允许实施差异，但当前没有实现。
