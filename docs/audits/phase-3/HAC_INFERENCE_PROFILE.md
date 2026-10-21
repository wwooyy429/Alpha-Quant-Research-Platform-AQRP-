# P3-HAC-BARTLETT-1：固定统计profile提案

对应WORK-P3-005、VALID-005/007/008、QA-004。选用已锁NumPy+标准库；本轮不安装SciPy/statsmodels，不变22包锁。HAC公式不变：demean，gamma_k分母n，Bartlett权重，Var(mean)=S/n，small_sample_correction=none，normal双侧p=erfc(|mean|/sqrt(2Var(mean)))。原n=4/mean0仅算术例，保持原件。

三个明确模式：ARITHMETIC_REFERENCE仅验证公式（允许n小但绝不标inferential p）；ENGINEERING_DEMO允许打印带non_formal标记的候选p以测数值；FORMAL_INFERENCE必须满足下述全部条件及预注册/批准证据。p值有效不等于因子金融批准，更不等于策略可交易。

**开发方选定工程候选，尚非用户批准阈值：** 预注册h∈{1,5,10,20}个session，lag `q=max(h-1,5)` 在看Validation/Test前冻结，同一协议不可按结果自动换q。min_hac_n=252，实际所需连续有效观测 `n>=max(252,20*(q+1))`；整数0<=q<n。例h1/5/10分别q5/5/9、min252；h20 q19、min400。252是约一年度规模的保守工程候选（合成日历未宣称252交易日真实市场规律），20*(q+1)是避免带宽相对样本过大的工程安全系数，**都不是任何有限样本或所有依赖结构的理论保证**。额外lag5是显式候选，不宣称覆盖全部自相关。改变h/q/min_n要在开发期新protocol/family试验；不能用Test诊断结果调lag。其它h只支持算术/探索，正式若需扩大须新profile预审和批准，不能静默作为缺省准入。

准入同时要求：预注册protocol_hash/family/all candidates、用户批准的正式样本/标准与实验预算；IC同stage/horizon/股票池，预定session网格完整、连续等间隔于该日历，无dropna压缩时间（任何失效IC记缺失、formal拒绝，不选好看的最长子段）。IC有限，双方有效横截面n及group等标准冻结。正S/Var与非零SE；非平稳/结构断点已知标记、缺样本、lag不足/未冻结、意外有效区间选择拒绝。不自动把日历休市当缺失，但缺一个scheduled session算空洞。

方法假设需预先写进 `dependence_assessment_ref`，由统计预审核验：弱平稳、短记忆/可求和自协方差、适用的渐近中心极限定理条件、该带宽截断可接受的Train/领域依据及局限；IC有界并不能推出平稳/弱依赖。h-1只覆盖机械标签重叠，不能证明更长依赖不存在；已知更长依赖而profile q不足，返回DEPENDENCE_PROFILE_UNSUPPORTED。不得把某个Train检验不显著当假设已证明，也不能在最终Test上作诊断后重选协议。资料无依据=ASSUMPTIONS_UNVERIFIED，缺正式用户标准=FORMAL_PROTOCOL_UNAPPROVED；二者均不可拿p做正式family批准。

拒绝codes：INVALID_HORIZON_OR_LAG、LAG_BELOW_OVERLAP、INSUFFICIENT_HAC_SAMPLE、IRREGULAR_OR_MISSING_IC、NONFINITE_INPUT、NONPOSITIVE_LONG_RUN_VARIANCE、ASSUMPTIONS_UNVERIFIED、DEPENDENCE_PROFILE_UNSUPPORTED、FORMAL_PROTOCOL_UNAPPROVED、CONTAMINATED_OR_OVER_BUDGET。保留n/q/assumption refs/拒绝原因，p=null。无效边际p不能伪装成有效p=1；全family失败项可按事前保守政策另映射p_for_adjustment=1并保留原始null/reason，报告family不完整/无法批准。

family：确认性Holm、探索BY；BH仅预先有适用依赖依据。不删除失败/未完成候选，m为事前全体；Holm/BY不修复无效边际p、可选停止、Test污染。新增m4案例保留失败p原始null、保守校正输入1并公开原因。正式family只要缺有效证据/污染/预算失败则拒绝ResearchValidated，即使校正数显著。

新增非零均值算术：IC=[1/2,0,1/2,0]，mean1/4，gamma0=1/16，gamma1=-3/64，gamma2=1/32；q1 S1/64, Var1/256, SE1/16, z4；q2 S1/48, Var1/192, SE1/(8sqrt3), z2sqrt3。双侧候选p分别0.00006334248366623984、约0.0005320055051392504。用独立高精度erf级数核对float erfc，**n4不可formal**。n251/252及h20的399/400、q边界、空洞和全family失败见supplemental_cases.json；状态是设计预期，不冒充执行了未来门禁。

方法参考：[statsmodels官方cov_hac](https://www.statsmodels.org/stable/generated/statsmodels.stats.sandwich_covariance.cov_hac.html)的等间隔、Bartlett、显式lag及修正选项。该来源不为本项目252/20/5候选背书；数值和带宽适用性须独立复核/用户标准确认。
