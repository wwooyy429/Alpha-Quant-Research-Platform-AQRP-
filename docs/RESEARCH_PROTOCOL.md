# 因子研究、样本外隔离与统计协议（提案）

关联 RESEARCH-001–009、VALID-001–008、EXP-001–004、FACTOR-009。Phase 3 实现；本文件不声称已经运行研究或独立核验统计库。

## 预注册及权限

在任何正式验证前冻结 Protocol：候选 family_id、因子/代码版本、方向、参数网格、预处理顺序/拟合规则、预测期限、股票池/时间区间、标签口径、Train/Validation/Test 日期、purge/embargo、最小样本、检验方法、显著性阈值、经济效用/成本/稳定性门槛、最大试验/验证访问预算及选择规则。阈值无默认“自动批准值”；DECISIONS D-004 待用户批准，字段为空则只能探索，不可正式批准因子。

仅指定开发数据（Train，以及预注册允许的 Validation）用于选方向、参数、处理链及期限。Train 拟合的全局参数只 apply 到验证/Test；横截面当时可见标准化不使用未来日期。原始、清洗、标准化、中性化、最终分数分别存储，报告注明 stage 和 fit 区间。行业/市值/Beta 使用 PIT 暴露，不回填最新分类。

Test 由独立评估权限/服务控制，开发任务不可读其标签或反馈。最终一次评估前锁定代码/数据/配置/通过标准；Test 标签只用于一次最终评估。记录访问主体、purpose、时间、次数和产物。失败或看过结果后重新选参数，旧 Test 即受污染：新候选必须用新封存测试段/前瞻观察，不能改名后再次声称独立。评估程序错误的重跑须记录事故、暴露范围、审批及相同配置证明，不默认恢复独立性。

未完成数据访问隔离前 Test access-control 能力为 Planned，不得把仅靠文档约定称为技术隔离。生产候选批准需独立证据核对与人工记录。

## 标签及切分

默认标签采用与可执行时间一致的 next-open 到 horizon-open 收益：对收盘 t 的信号，entry=t+1 open，exit=t+1+h open，h 为正整数 session。使用一致 split/现金分红总收益口径，明确停牌/退市/缺 open 处理；标签 start/end/available_at 单独保存。close-to-close 可作另一个研究标签，但不得称为同样的可交易收益。多个期限属于多个假设。

时序 Train→Validation→最终 Test；不随机打散。每样本标签信息区间 `[label_start, label_end]`：若训练样本标签与 held-out 标签/受保护区间相交则 purge；embargo 以 session 计且在切分定义中固定（至少覆盖策略信息依赖的已批准长度，不凭空定百分比）。Walk-forward 每窗仅用当时可见资料拟合，保存每窗 fit/evaluate 区间、purge 数和去重规则；窗口覆盖同一观测的重复得分不得当独立样本。边界按半开切分区间、相交判定的闭区间定义测试，跨证券标签和公司行动也计入。

## 基本算子及预处理

Delay(x,k)=本证券第 k 个先前有效交易 session 值；Delta=x_t−x_(t-k)。rolling 窗口 `[t-L+1,t]`，必须 L 个有效观测、min_periods=L；不以删缺失后压缩时间伪装连续窗口。Mean/Sum/Min/Max 直接按窗口；Std 使用 ddof=1；Correlation 成对有效且方差非零；Ts_Rank 是当前值在窗口的平均并列秩/L。横截面 Rank 平均并列秩，输出归一化方法必须记录。条件算子只允许已白名单数据表达式，不 eval 任意代码。

处理链顺序须配置；建议 raw→按规则标无效/删缺失→去极值→标准化→中性化→最终分数。去极值可选预注册分位数或 MAD 规则，分位数插值方法固定；不隐藏探索不同规则。横截面 z-score=(x−mean)/std(ddof=1)，不足2/方差0标 invalid。行业/市值中性化按截面 OLS 残差，截距、基准行业、log 市值、样本过滤、秩亏处理显式；不以没做处理的复制列冒充中性化。

## 统计口径

每日 PIT 历史股票池内，成对有效的 final score 与 forward label 计算横截面 Pearson IC；n>=3 且两向量方差非零，否则 null + reason。Spearman 为平均并列秩的 Pearson，不能对并列情况套无并列简式。原始/预处理 stage 不混合。Mean IC 为有效日等权均值；std(IC,ddof=1)，至少2日；ICIR=mean/std，默认不年化，若展示年化另列 sqrt(A) 假设。IC 正值比例只计 >0，有效日为分母并报告零值比例。

分位数采用稳定 `(score,security_id)` 排序并声明 tie policy（不得把并列强行拆分解释为真实差异）、最小组规模及未成组数量。组收益为指定标签的等权或明确权重均值，TMB=最高组−最低组；方向在开发期预设并固定。单调性报告组序号与组均收益的 Spearman 及相邻违反数。衰减按固定 horizon 网格；年度稳定性记录每年 n/均值/置信区间。因子相关性必须对齐同一时点、股票池和 stage，报告缺失交集与冗余候选。

显著性对 IC 序列用预注册 HAC 均值标准误（Bartlett 权重、固定 lag 及小样本规则），不能将重叠 h 日标签当独立样本；至少考虑 h−1 的重叠依赖，lag 还要覆盖额外自相关且在开发期固定。样本不满足等间隔、过短等假设则不报告假精确 p 值，可采用预注册时间块 bootstrap，保存 seed/块长/重复数。ICIR 不是显著性检验，统计显著也不等于成本后经济价值。

## 重复试验与多重检验

append-only experiment ledger 保存所有成功/失败/淘汰候选、参数、方向、处理链、期限、family_id、parent_run_id、数据/代码/配置、Validation 使用次数与筛选依据；相同规范配置指纹关联重复试验，不能删差结果。预算超限、测试集重用、未注册候选、择优报告等触发 overfit 风险标记，阻止自动批准。

研究 family 在观察结果前定义，不能只把最后赢家计入 m。确认性 family 建议使用 Holm 控制 family-wise error；探索性 FDR 可用 BY，BH 仅在相应依赖假设有依据时用。依赖关系与自适应搜索的限制必须在报告解释，方法不自动消除重复使用 Validation 的偏差。保存原始与校正 p、总 m、淘汰项、显著性阈值及选择路径，经济门槛单独判断。

## 正式批准证据

ApprovalProposal 必须关联：预注册标准及冻结时间、开发选择记录、所有试验计数、OOS/Test 访问审计、实际指标与不确定性、校正方法、数据/代码/环境哈希、未来数据变更测试、独立 Golden 核对及审查记录。P3 只可批准研究有效性状态（ResearchValidated）；进入策略池还需 P4/P5 成本、风险和交易限制证据，不能以尚不可运行的回测作为 P3 门槛。P2 的 Reviewed 表示代码/API 审核，不是统计有效性批准。

## 参考依据

HAC 接口的假设与参数可核对 [statsmodels 官方 cov_hac 文档](https://www.statsmodels.org/stable/generated/statsmodels.stats.sandwich_covariance.cov_hac.html)；多重检验方法可核对 [statsmodels 官方 multipletests 源码](https://www.statsmodels.org/stable/_modules/statsmodels/stats/multitest.html)。这些资料支持方法选择，不代替本项目的独立答案和假设审查；实施时以锁定版本重新核对。
