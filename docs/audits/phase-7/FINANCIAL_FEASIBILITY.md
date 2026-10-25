# 主层19研究点／10执行点的有限金融设计复算

这是**开发方设计模型与上下界分析**，没有导入/运行AQRP，没有P7产品、真实账本、GUI或独立G2通过结论。GPT Work G1仍须独立核对输入、所有适用假设及与真实已审规则的逐项映射。全部模型源码见FINANCIAL_REFERENCE_METHOD.md；实际解释器/源hash/UTC/stdout/stderr/退出码在FINANCIAL_REFERENCE_EXECUTION.json。

## 原提案的两个反例保留

1. 原19日逐日执行：Jan4首次决策选Momentum001/Reversal003，Jan5开盘买4股，股票lot按成交session+1交收；Jan5收盘排名转002/004时，可售仍0。P4在当时决策状态检查SELLABLE，不能假设次日撮合会先解禁。原19逐日成功夹具不成立；不修改T+1或P4门禁。
2. 隔日10点但fee_budget100：第一次换仓前cash_set598.6。若SELL先候选成交，现金597.6、待交收卖出所得399.6；另一BUY仍冻结4×105=420，O_F=4，当前unused=100−1−4=95。P4保守投影equity_alloc=597.6−420−4−95=78.6，逐笔turnover400/78.6>4，合法拒绝该SELL候选。不能靠“现金总额没问题”或只试BUY先顺序证明成功。

SUPERSEDED_FINANCIAL_COUNTEREXAMPLES.json保留两条逐步模型反例和被拒候选；原未送审的fee100/19执行点草案另按SUPERSEDED_INITIAL_*保留。反例是未审夹具设计问题，不称产品缺陷或真实失败日志。

## 修订后的具体候选

- P3完整19研究点、原全处理/中性化/OOS；P5的10个执行点预先冻结为Jan4、6、8、10、12、14、16、18、20、22。显式execution_sessions契约见EXECUTION_SELECTION_CONTRACT.md，不能事后挑成功日。
- 初始1000、每决策commission budget **50**、gross=net=0.5、equal、long_k=short_k=1，保持原风险turnover_max4及其他全部限额。LONG_SHORT公式给long预算0.5、short预算0，故没有实际空头/借券/short restriction；这属于原合法配置，不改权重算法。
- sidecar原价/估值100、tick0.01、lot1、BUY100.10/SELL99.90，qty4的佣金max(1,0.1%成交额)=1。工程profile没有单列卖出税项，因此此fixture税项0，不是任何真实市场免税声明。
- 历史ADV输入均100–160且提前可见，原minADV10/每slice min(10,ADV)给容量10，4股一个slice全部成交。无外部流/公司行动/真实账户，期末保留4股按100估值，不擅自强平。
- 预算50是**每次决策重新创建的commission budget**，不是全程总佣金限额；它也不是研究共享12单位试验预算。主层全部actor、两因子都冻结相同50，不修改任何历史已审默认值。

## 上下界（覆盖首建仓＋最多9次换仓及两种逐单顺序）

第一次可投权益1000−50=950，半仓理想4.75股，向0整手为4股。首建仓实际支出401.4，现金598.6，费用1、滑点0.4。每次完全换仓分别卖4/买4，费用2、滑点0.8；两个撮合顺序的最终现金都减少2.8。最多9次换仓后，已交收现金至少573.4、真实权益至少973.4、累计佣金至多19、滑点至多7.6。

预先隔日决策使上一买入lot和卖出所得均在下次决策前交收。每次决策时仅有已交收4股和现金S，S≥573.4；可投权益S+400−50=S+350，所以半仓理想数量在4.617–4.743之间，整手始终4。旧持仓当时可售4，不产生未交收卖出或新增空头。

提交篮子最多BUY4和SELL4：名义冻结420，累计手续费最坏上界8，S≥573.4>428；预算50>8，所有篮子满足准入资金和费用上界。各对象O_F/unused分开计算，不能重复冻结。

- SELL先：paid1，另一BUY O_N420/O_F4，unused45，equity_alloc=S−470≥103.4，P4逐笔turnover≤400/103.4=2000/517<4，无持仓时gross=0且允许cash-only。
- BUY先：paid1，另一SELL O_F4，unused45，cash_alloc=S−450.4≥123，marked800，equity_alloc=S+349.6；gross<1，单票权重<0.5，资金仍正。
- 两单完成：paid2，未交收卖出所得399.6，cash_set=S−402.4，unused48，cash_alloc=S−450.4≥123，marked400，equity_alloc=S−50.4≥523；单票/净/gross/Beta/行业和逐笔turnover仍低于原限额。

真实P5风控使用总权益不低于973.4；即使BUY先短暂持8股，gross≤800/973.4<1，单票≤400/973.4<1，net/行业≤gross、Beta=gross，均在原限额内，逐决策真实成交额≤800、turnover<1。所有数量整数、可售/权限条件满足，无借券、借券费和short所得。这些界不是因未知结果临时放宽风险，而是对已冻结候选的穷举上界。

## 实际有限模型结果与原始路径

Momentum与Reversal各7次换仓、10个required P4、15次4股Fill。每因子128种BUY/SELL顺序；另以每次都换仓的9次最坏序列枚举512种顺序。合计 **768条有限模型路径／109350条开发方模型检查**，所有路径的逐笔候选符合模型中的P4/P5资金和风险条件。它不是768次产品运行或109350项SDK测试。

两因子模型最终现金579、市值400、权益979、佣金15、滑点6；最终Momentum持004、Reversal持002，各4股。九换仓最坏序列最终现金573.4、权益973.4、佣金19、滑点7.6。实际模型枚举的最小post-P4可投权益106.2，最大post-P4 turnover=2000/531≈3.7665；保守解析界103.4更低，故覆盖该结果。全运行现金桶最低值和完整路径索引见FINANCIAL_MODEL_BOUNDS.json，不能把决策前S≥573.4误读为整个生命周期cash_set都≥573.4。

FINANCIAL_MODEL_ALL_PATHS.json保留全部逐步资金桶、O_N/O_F/unused、live订单、决策、候选Fill及双层风险结果，**115159679字节**。保持外部，不提交大文件到Git；小型FINANCIAL_MODEL_BOUNDS.json和模型执行记录绑定实际SHA256，主开发封存时须再次实核字节和hash。真实SDK/CI/浏览器实施后必须独立核实际输入、精确Ref、P3→P5映射/时点、10个真实P4、Task终态/manifest/物理事务和全部原金融答案，不能拿模型路径代替这些证据。
