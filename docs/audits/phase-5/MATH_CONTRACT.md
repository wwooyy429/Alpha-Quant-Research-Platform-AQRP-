# 数学与账本候选口径

账本不使用binary float。profile数量整数、价格精确tick0.01，成交名义额精确为分；commission/borrow每事件分HALF_UP，累计由实际已舍入事件相加。中间持仓成本均值用有理数保存(numerator,denominator)或等价无损定点，禁止统一Decimal34破坏已验证数量/权益。输入有限域、精确quantity/lot/ledger比较容差0；统计display才float64，有限小数精确输出，非终止比例另存精确分数及展示口径。

每Fill signed q买>0卖<0：C'=C−q·p−fee；positions'=positions+q。reserve/restricted为cash子账，冻结不重复扣cash。Equity=C+Σq·mark+R−P，settled/unsettled不改变total；available=settled−orders_reserved−short_proceeds_restricted−additional_short_margin−other_payable_reserve。冻结项目互斥编码，释放只释放对应order剩余额；不得把short proceeds和margin作为负债重复扣E。

复式交易：long buy借positions-cost，贷cash；sell借cash，贷positions-cost，差额credit realized-gain/debit realized-loss；佣金借fee-expense贷cash。short sale借cash贷short-position-liability（负position成本），cover相反，差额独立realized-short-PnL；所有每事件每币借贷=0。valuation借/贷持仓unrealized valuation与未实现损益，和成本子账分开；Journal可按科目重建实际账户，不能只写总额抵消行而无经济科目。

移动均价**不含费用**：同方向加仓 c'=(abs(Q)c+abs(q)p)/abs(Q+q)；减仓realized_gross=closed_qty·sign(Q)·(p−c)，剩余c不变；跨零拆成原仓平仓和新方向开仓两分录（同一个真实Fill，commission只扣一次且归因按数量比例精确分配），新仓c=p。费用作为expense全计，不在净收益再扣。realized/unrealized/净费用/红利/借券费之和对齐权益损益，外部注资剔除。

split r：已有q'=rq，unit cost'=cost/r，总成本/权益连续；raw mark相应变换，未成交订单先CANCELLED(CORPORATE_ACTION_REPLACE_REQUIRED)释放预留，不无声改原单数量/价；后续新决策才可建新订单。合成非整数结果/缺价格规则失败，不自动填补。红利按生效时合格旧股数与单位计，long借receivable贷dividend-income；short借dividend-expense贷payable；支付时只在R/P与cash间结转。价格除息损益和红利收入共同解释E，不能重复加total-return价格。

外部流带direction/flow_id，流前后估值不混入策略收益；每子区间R=(E_end−flow_at_end)/E_start−1（流在期首先调整起点），多流分段连乘TWR，不粗暴用日末权益忽略流时刻。简单无流r_t=E_t/E_(t−1)−1；cum=Π(1+r)−1；annual=(1+cum)^(252/n)−1。n为有效session间隔，不是权益行数。std(r,ddof1)√252；Sharpe=mean(r−rf_daily)/std(r−rf_daily,ddof1)√252；非正权益/样本不足/零方差明确undefined并解释。

MDD=max(1−E_t/max_{s<=t}E_s)，包括起始E；有外部流用流调整净值序列计算，保留原现金权益另表。turnover_full=Σabs(fill_notional)/decision前正权益、half=full/2；多decision分开分母、汇总明确加总，不混淆P4目标估计。滑点归因买signedqty·(actual−raw_open)（卖同样signedqty使逆向成本为正），成本已反映交易价格，展示的fee/slippage不能在净收益再次扣除。long/short现金流贡献与净收益核对。

胜率=已平仓配对gross realized−按数量分摊entry/exit fees−该持仓borrow/dividend成本后>0的已完成round-trip数量/已完成数，0利润为nonwin；按证券方向FIFO配对用于交易统计，账本成本仍移动均价，二者独立标记；未平仓不混分母，无完成交易undefined。平均赢/平均亏绝对比为profit_loss_ratio；无亏损/无赢家分别undefined并列计数。尾部VaR/optimizer/显著性研究不从这些统计推定。

参考候选在GOLDEN_CANDIDATES.json，给定输入、字面expected、计算依据与容差；reference_check.py只用标准库独立算术，不导入AQRP或任何待实现函数。审查方应另写参考，不能仅运行该开发方文件宣称独立答案已批准。

完整预算投影候选：C=1200、持仓净市值−180、U=50、O=0、P=2、F=10、R=4、S=200、V=180、Z=0，则B=62，C_alloc=1138，E_alloc=958；P4非short restriction=20，预留V180+额外margin180后预算free=758；实际总权益1200−180+4−2=1022=958+62+4−2。应付/未交收/F不重复加冻结；P5真实既有free（未含新单）=1200−50−200−180−2=768，预留预算F10后758。该候选须主审独立复算并在未来集成中冻结。
