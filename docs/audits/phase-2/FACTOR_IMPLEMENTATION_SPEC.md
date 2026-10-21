# Phase 2 接口与执行细化提案

对应P0 INTERFACES的Factor API；当前仅文档、所有签名/字段为拟实现，尚无可调用Phase2 SDK。版本提案factor-api/1.0.0、contracts/1.0.0、data/1.0.0；不改变P1 Data API。

## 对象与参数

- FactorSpec保留factor_id/name/version、parameters schema、required_fields、lookback_window、supported_frequency、signal_available_time、output_unit、factor_direction、implementation_version内容hash、api_compatibility、data_contract_version、review_ref。补充显式price_basis及bundle_manifest_ref用于落实既有价格/审查契约，不删既有字段。
- 三内置ID分别momentum/reversal/volume，版本1.0.0；频率daily，basis=split_adjusted，dimensionless ratio，direction均+1且不可从run参数更改。raw compute不再次应用方向；研究处理另属P3。
- FactorRef=(factor_id,exact factor_version,implementation_hash)，禁止latest、浮动别名与不完整版本。版本严格MAJOR.MINOR.PATCH无前导零，P2拒绝预发行/build及未知范围语法。兼容声明仅支持 >=x.y.z,<u.v.w；默认>=1.0.0,<2.0.0；实际host1.0.0是否在界内逐项验证，声明range不等于已证明语义兼容。
- 参数只接收schema已声明键；lookback严格int且拒bool，1..252，测试缺省20。未知键/非法类型/越界/NaN/Infinity/可变嵌套值先失败；默认值先补齐再canonical并hash，不用repr或Python hash。固定config规范UTF8 JSON/排序键/显式Decimal和时区，复用P1 canonical，不扩大格式。
- FactorContext含run_id、computation_id、decision_time、target_session、snapshot_id、manifest_hash、query_hash、calendar版本、只读params/params_hash、security_ids和seed；不含账户/订单/网络会话/标签。DataView沿用现有P1独立IPC副本；其snapshot_ref包含路径，不能据此宣称Python对象阻止恶意读盘。

## 拟接口与准入顺序

register(reviewed_artifact,spec)、resolve(exact_ref)、validate_compatibility(ref)、deactivate(ref)、rollback(approved_ref)落实原签名意图。compute(view,context)->SignalBatch只接受受审内置实现；面向调用者的runner锁定QuerySpec/as_of/SnapshotRef和FactorRef，在host端查询/校验后调用。输入params/config不接受模块路径、文件路径、eval/exec、任意factory/类或pickle。

准入首先验证受信allowlist中的内置ID、完整实现bundle hash、review receipt与环境范围，再导入已知模块。bundle按排序相对路径+源码字节hash封存全部影响计算/准入的随库模块及host/锁版本；不只hash一个插件文件。receipt含reviewer/时间/证据/hash及用途TEST_ONLY，不由插件自报；开发方测试审查不冒充Gemini。代码发生变动需新receipt；测试hash生成不自动等于审查通过。

Registry条目append-only，状态变化/停用/rollback附actor/reason/evidence；同ID/version同规范spec与bundle hash幂等、同ID/version异内容拒绝。新版本保留旧条目；停用禁止新resolve，已建立的运行pin只读不被静默替换。显式紧急停用可终止运行并记录，不可把失败换为其他因子成功。rollback选择已获兼容测试CodeApproval的精确旧版本，仅影响新运行默认选择，不修改旧run、旧参数或数值；不存在自动latest热更新。

P2可维护Candidate/Reviewed及Disabled/Deprecated代码条目，CodeApproval为独立的测试代码准入记录。P3 ResearchValidated、P5后StrategyApproved及完整生命周期转换仍Planned，strategy模式Unsupported；CodeApproval不授予策略交易资格。P0 generic Approved的术语映射作为本次必须预审事项，不能把P2元数据标志冒充金融批准。

## P1输入与时间约束

runner调用既有aqrp.data.query.query；复用P1核验过的read_snapshot/visible_rows在受信host侧得到同decision_time可见的calendar，绝不把全量原始表或未来日历传入插件，不复制PIT/复权算法。若实际实现发现需修改P1公开契约，先提出独立变更审批，不修改已冻结接口后假称兼容。symbol仅展示，无法获得可信可见别名时显式null，不拿symbol作唯一键。

必须校验Context与DataView的snapshot_id/hash、cutoff、basis、字段、市场、日历及security集合一致；行event_time/available_at均<=decision_time。DataView可由普通Python构造，host的完整查询与hash校验是正式入口，不把isinstance或metadata当不可伪造来源证明。未匹配的手造view只用于负例/纯函数单元测试，不能形成正式可复现结果。

一批运行只计算明确target_session的输出；按每个security独立排序窗口，以该可见日历结束在target_session的连续L+1 session为准。target不可见、历史不足或中间缺bar/quality不合格均invalid，不偷换为更早目标日、跨证券滚动、填0或跳缺口。缺输入字段、上下文不匹配、快照损坏、非法版本/参数属异常；合法但无足够历史属有reason的invalid，不吞异常返回“成功空表”。

三因子都使用P1 split_adjusted的close/volume，Price-Volume和total_return因子不在P2；不得自行引入另一套复权。Volume分母只用t之前L个session，排除当期；旧股/拆股后share单位由P1统一。

signal_time为target bar事件时间；available_at采用decision_time且logical_compute_delay=0的明确合成假设，依赖均已在该cutoff可见。不得把wall clock当历史available_at，不能用未来as_of统一生成过去信号；每个过去decision必须重新经PIT查询。该方案不是实际实盘延迟模型，不生成可执行订单。

## SignalBatch与运行血缘

行字段保留signal_time、security_id、symbol、market_id、factor_id/version、factor_value(float64或null)、available_at、validity/reason、snapshot_id、params_hash、run_id、computation_id、implementation_hash，补processing_stage=raw和manifest/query/config版本引用。逻辑键按P0 `(run_id,factor_id,factor_version,params_hash,security_id,signal_time,processing_stage)`；重复相同内容幂等，冲突拒绝。输出排序固定(signal_time,security_id)，NaN/Infinity不作为有效数值。invalid必须value=null并列出reason，不以0替代。

参数/配置用深层不可变快照；新run_id UUID且占用目录已存在即拒绝。P2只生成因子运行receipt/产物，不提前实现P3实验数据库或调参服务。全量产物hash与数值投影hash分开：run/request/computation ID、snapshot_id/manifest/query等真实血缘不为比较方便而伪造相同。跨未来mutation/快照位置比较只核对预先声明的逻辑值/validity/目标证券与时点，保留不同血缘。

错误继承P1 ContractError结构，factor层新增UnknownFactor/DuplicateFactor/IncompatibleVersion/UnapprovedFactor/InsufficientHistory等适用类或reason，保留request_id/run定位。关键API从factor层向data/core单向依赖；禁止导入research/portfolio/backtest/ui，禁止持有可写账户或费用状态。
