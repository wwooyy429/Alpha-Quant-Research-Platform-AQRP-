# P4接口与算术冻结候选 · portfolio/1.0.0-proposed

这是待G1审查设计，不是已实现SDK。继承docs/INTERFACES.md、DATA_CONTRACT与BACKTEST_CONTRACT。所有对象schema_version、request_id/run_id、canonical config、来源manifest/hash、精确Ref及决策时点齐备；拒绝NaN/Inf、布尔数值、重复键/证券、未知字段和schema，不使用隐式DataFrame索引。

## 1. 身份、时间与不可变输入

construct_approved(ApprovedScores, UniverseView, AccountSnapshot, Constraints, SyntheticMarketProfile) -> PortfolioResult；construct_engineering(EngineeringScores, ...) -> PortfolioResult。后者专门标ENGINEERING_TEST_ONLY，详SCOPE_AND_DEPENDENCIES。没有skip_approval或默认降级。入口依据工件原字节hash、schema与来源身份校验，不执行因子代码、不看因子名称、不读取未来数据/标签。

统一单币种CCY、market/calendar、decision_time UTC微秒、parent snapshot/version。每份输入具有event_time、available_at、as_of；as_of等于本次decision_time，event_time/available_at <= decision_time。各分数组不得混合决策时点；不同原信号可早于决策，但必须在预注册max_age_sessions内，按同交易日历验证，缺session映射拒绝。score有效行、池/状态/主档/行业/Beta/价格/账户及借券侧车一律PIT；未来/错误父快照/过期/含糊日期立即拒绝，不能靠调用者where保证。账户valuation_time等于decision_time，来源price_ref一致；不接受用未来价格换算当期目标。synthetic快照hash显式区分数据投影和账户fixture身份，不能要求不同类型hash字面相等。

AccountSnapshot：equity>0，total_cash、restricted_cash、positions的signed_qty与同一估值价、sellable_qty>=0、borrow_limit_total>=0、short_permission及冻结/交收投影。单位CCY/share；E = total_cash + sum(q_i*p_i)，restricted_cash<=total_cash，p_i>0且有限。成本/应收等如非零须已纳入明确equity组成，首版合成profile要求无这些项，否则契约拒绝，不遗漏估值。持仓含非当期选择资产，目标补0用于平仓与风险；证券消失不能直接丢弃其持仓。输入不可变，不修改账户或源DataFrame。

## 2. 分数、选择与双腿

分数为P3指定stage已定向/已处理结果，P4不重新拟合方向、标准化或择优。单/多因子预注册a_j，S_i=sum(a_j*s_ij)/sum(abs(a_j))；a均有限，分母>0；仅所有选定因子的有效资产交集，剔除原因及数量逐一报告，不补0、不按证券重配a。池必须PIT可选择；非可交易资产的选择资格由冻结规则显式排除且报告；已持有不可交易资产仍不能被忽略，任何实际调仓不合法即拒绝。

TopK为严格正整数；分数降序、相等按完整security_id稳定排序，保留tie标识。LongOnly等权：取前min(K,n)后每个1/n（允许负分，因为是排名等权，配置明示）。分数权：先取相同topK，对max(S,0)归一；分母0全现金并记NO_POSITIVE_SCORE。空交集也是显式CASH/EMPTY_INTERSECTION，若cash不允许则INFEASIBLE，绝不假造有效Alpha。权重守恒含cash。

LongShort：预算L=(G+N)/2、H=(G-N)/2，要求G>=abs(N)，G>=0，0预算腿可为空，非0预算腿必须有资产。等权腿从同一排序选top K_long和bottom K_short，必须不重叠；K总数>n且两腿预算非0即拒绝，不偷改K。分数腿先对全共同交集S计算横截面算术均值m；只从S-m>0取前K_long，S-m<0取后K_short；每腿按中心化分数绝对值归一再乘L或-H。无有效腿但预算非0即INFEASIBLE；不把零中心化值分配至任一腿。选择及权重规则随config冻结，不能通过试验最终Test调参。

## 3. 数量、现金及风险顺序

有限Decimal输入字符串（不接受隐式binary float金额），候选context precision=34、ROUND_HALF_EVEN；权重/比率数值边界容差固定1e-12，金额核对1e-8 CCY，数量/许可/lot精确比较、时间精确微秒。阈值比较value <= limit+tolerance；低界value >= limit-tolerance。容差随profile/hash冻结，不能按失败动态扩大。独立分数输入可float64，但必须canonical十进制投影并记录，禁止非有限值。

先以目标连续权重预检经济/资金/暴露/许可等约束（lot格点不适用于连续理想数量），再计算q*_i=w_i*E/p_i。冻结原“绝对目标向零取整”策略：仅当q*_i与q_current_i数量精确相等时保持q'_i=q_current_i，分类UNCHANGED_HOLDING；否则q'_i=sign(q*)*floor(abs(q*)/lot)*lot。不能因后续失败自动保留旧仓或改用交易增量格点。

### 3.1 目标与调仓数量的双重lot门禁

lot为严格正的share单位Decimal，数量等于/整除均精确，不应用ratio或现金容差。始终delta_i=q'_i-q_current_i。生成成功目标前依次校验：

| 情形 | 目标与delta规则 | 例外边界 |
|---|---|---|
| delta=0 | 原数量可为奇零股，保留原仓，记UNCHANGED_HOLDING；不生成零数量调仓建议 | 不要求交易资格，但仍纳入PIT/估值、所有资金及敞口检查；不是新增奇零股交易权限 |
| delta!=0且q'!=0 | q'必须严格整手，delta也必须严格整手；分别检查，不能由前者推导后者 | 原奇零股的部分增/减或跨0若delta非整手，一律拒绝；不自动拆单/先平再开 |
| delta!=0且q'=0 | 0目标天然整手；delta整手按普通规则通过lot；若非整手，仅当完整原仓一次全平且allow_full_close_odd_lot=true才允许 | 同时适用于原long全卖和原short全量买回；false时非整手全平拒绝。不可用于部分平仓或跨0后新仓 |

有变化的非零目标不整手返回TARGET_LOT_MISMATCH；非零delta不整手且无全平例外返回DELTA_LOT_MISMATCH，RiskDecision=REJECTED，PortfolioResult=REJECTED，无成功target/token。全平仅豁免delta的lot，不豁免可交易性、可售数量、空头/借券、现金或任何风险约束。公开check_target和共同service均重算此门禁，不能依赖外部risk_passed，也不能延到P5再发现。新例见ROUNDING_REFERENCE的R01–R13/R17。

每次取整或保持原仓后重算w'_i=q'_i*p_i/E、delta、预计现金C'=E-sum(q'_i*p_i)，执行全部post风险（不只净下界）。输出continuous与rounded两套诊断；lot门禁及其他任何必需约束失败均拒绝，不静默夹紧/改预算/重复归一/放宽限额。

合成profile短卖所得全部限制：required_restricted=max(existing_nonshort_restriction,0)+sum(max(-q'_i*p_i,0))，initial_margin_ratio=1.0要求额外sum(short_abs_notional)*1.0资金缓冲。free_cash=C'-required_restricted-margin_requirement-fee_reserve，须>=0（金额容差1e-8）；fee_reserve为显式非负输入，不计算真实佣金。现有restricted_cash须分解short/nonshort且一致，避免重复扣短卖冻结。负自由现金拒绝，无融资。现金权重=1-net，可因卖空>1；这不是杠杆可用资金。所有值是纯目标估算，没有成交或复式账本更新。上述100%短卖冻结加额外100%短仓保证金且无融资时，恒有free_cash=E*(1-gross)-existing_nonshort_restriction-fee_reserve。因此默认现金账户即使gross/leverage cap配置1.5，资金检查仍限制gross至约1（固定现金容差内）；G08只证明预算算术，按G19资金门禁仍拒绝，不改变经济假设。

风险check_target(TargetCandidate, account, market_profile, constraints, decision_time)->RiskDecision，服务总是重算与核验候选hash，不信任调用者risk_passed标志。约束：每票abs(w_i)<=cap_i；gross=sum(abs(w))<=G_cap；net=sum(w)在[N_min,N_max]；合成无衍生品leverage=gross（分别报告）；turnover=sum(abs((q'_i-q_i)*p_i))/E，另报half_turnover=turnover/2，限额明确作用于前者。合成账户按同价当前权重，不把净额抵消当低换手。

行业逐行业净暴露=sum(w_i)，总暴露=sum(abs(w_i))分别给上下界/上界，Beta=sum(w_i*beta_i)检查有符号区间；所有非零当前/目标或需调仓证券的必需暴露缺失、过期、未来、重复均拒绝，不赋0；不以行业净额代替总暴露。profile启用风险项必须提供对应限额，不因缺配置默认禁用。

先逐证券完成§3.1的目标/delta双lot门禁，对每项delta!=0的证券检查PIT tradable；sell_qty=max(-delta,0)，long_sale=min(sell_qty,max(current_qty,0))<=sellable_qty；额外新空头及目标总short_qty必须short_permission=true且<=borrow_limit_total（包含现有借券，不把总额度误作新增）。平旧空不要求新增借券，但仍须可交易、资金足够；long-to-short跨0先验可售部分和总借券两项均查。净delta为0的停牌持仓允许持有，但仍计全部敞口，不能生成调仓建议。缺许可与缺借券不是false/0默认，明确MISSING_INPUT拒绝。

## 4. 输出与不可绕过门禁

PortfolioResult.status为SUCCEEDED/INFEASIBLE/REJECTED；成功含不可变TargetPortfolio、各证券score/rank/target_weight/qty、cash/free/restricted/margin/reserve、gross/net/leverage/turnover、行业/Beta与所有constraint结果、取整余数、inputs/config/code/env hashes。拒绝也保留所有可安全计算的诊断，缺输入项标NOT_EVALUATED与原因，不伪造0或pass；无可执行target/token。

RebalanceProposal仅delta_qty、source_position/price_ref与决策引用，executable=false、engineering scope贯穿，无order_id/submitted_at/fill或账户写入。共用service必须消费刚生成RiskDecision及同输入hash，包含§3.1双lot及所有pre/post检查，任一拒绝不能返回成功目标；公开权重函数只能返回UnvalidatedCandidate，不能绕过service风险获得可用目标。用户构造/篡改对象和陈旧decision均重算拒绝。P5将独立生成OrderEvent并在提交/撮合前重查，不由P4假装已实现。

所有成功/失败/取消写独立run_id及不可变配置/输入清单、代码/环境/数据/hash，复用已验证ledger；末态后不允许后补文件成为证据。时点/审批失败不运行后续算术，避免从未来输入泄漏排名。来源标签与真实/工程身份必须在报告中直接可见。
