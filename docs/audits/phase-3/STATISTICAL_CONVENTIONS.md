# 研究数值与统计口径提案

所有选择在开发资料中预注册，改变方向/参数/处理链/期限/lag/分组/tie规则均是新实验。以下是待G1批准的工程定义，不是正式因子收益通过阈值。

- 顺序raw→clean(缺失规则及去极值)→standardized→neutralized→final；可选环节明确SKIPPED，不计算标签驱动的处理参数。MAD为median(abs(x-median(x)))，k须配置，MAD=0时invalid而非悄悄放过异常；分位去极值固定linear插值。截面z用sample std(ddof=1)，n<2/零方差invalid；横截面rank用平均并列秩/n，Ts_Rank用窗口平均并列秩/L。
- rolling完整session网格、min_periods=L；缺失不压缩时间；Std ddof=1、Correlation成对且非零方差，窗口一证券独立。Delay/Delta只找本证券前k个预定session，不是随意前k条非缺数据。Conditional仅白名单比较/布尔与字段，不eval任意Python。
- 中性化截面OLS：截距+industry dummy（固定字典排序第一类为基准）+log正市值；PIT暴露缺失排除并计数，n<=列数、秩亏/无法求解返回invalid及诊断。NumPy lstsq提议固定rcond=1e-12并记录rank/singular values/残差，不能把空residuals数组当零残差。工程参考用独立有理数矩阵，不从待测实现反算。
- IC每日对同stage/时点/股票池的有效score/forward label成对过滤，n>=3、双方方差非零。Spearman是平均并列秩后的Pearson。MeanIC有效日等权，std ddof1，ICIR=mean/std默认非年化；至少2日/零std返回null。正值比例只计>0，并另报零值与有效日分母。
- 分组按平均并列秩确定bin=min(q-1,floor((rank_avg-1)*q/n))，完整tie块不拆分、security_id仅稳定展示。同分位组过小/空组不强行凑数；min_group_n预注册，TMB需两端合格。等权组标签均值、TMB=top-bottom；单调Spearman及相邻违反数，n不足不报假精度。多期限/年度按固定网格及样本计数，跨因子相关仅同样本交集及stage。
- HAC提案：去均值IC序列u，gamma_k=sum(u_t*u_(t-k))/n，S=gamma0+2*sum((1-k/(q+1))*gamma_k,k1..q)，Var(mean)=S/n；显式small_sample_correction=none。若用statsmodels参考必须use_correction=False且固定q，不能混用默认修正/自动lag。q>=h-1且额外自相关lag在开发期冻结。仅在等间隔/样本与假设合格时给渐近正态双侧p=erfc(abs(mean)/sqrt(2*Var(mean)))，明确不是Student有限样本保证；短样本/空洞/零或负有效方差给null+reason。min_hac_n必须在预注册标准中给出并经预审，不凭空默认“足够”。
- 确认性family用Holm；探索性可用BY。BH须预先记录适用依赖依据，缺依据不执行。m是观察结果前已登记的全部假设，未完成/失败候选保留（对需保守纳入者记p=1并披露），不能只数赢家或跨family改名避校正；超预算/重复Test/自适应选择触发污染标记，校正不使污染自动消失。
- 财务标签按一致拆股/现金红利权益口径；不当作P5账本收益。可见公司行动不得在signal cutoff前注入，标签只在evaluation_cutoff有全部必要信息后生成。现金再投资/税/退市未知规则不虚构，先限明确合成profile，正式规则缺失返回Unsupported/invalid。

已阅读的主源（2026-10-22）：[HAC假设、Bartlett、修正参数](https://www.statsmodels.org/stable/generated/statsmodels.stats.sandwich_covariance.cov_hac.html)、[Holm/BH/BY接口](https://www.statsmodels.org/stable/generated/statsmodels.stats.multitest.multipletests.html)、[lstsq rank/rcond与residuals](https://numpy.org/doc/stable/reference/generated/numpy.linalg.lstsq.html)。仅作为方法边界参考，不声称当前已安装statsmodels或已独立核验所有库，亦不代替锁版本核验和Golden。资料中的默认参数不自动成为本项目默认。
