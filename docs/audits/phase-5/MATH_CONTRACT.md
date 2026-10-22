# 数学与账本候选口径

账本不使用binary float。profile数量整数、价格精确tick0.01，成交名义额精确为分；commission/borrow每事件分HALF_UP，累计由实际已舍入事件相加。中间持仓成本均值用有理数保存(numerator,denominator)或等价无损定点，禁止统一Decimal34破坏已验证数量/权益。输入有限域、精确quantity/lot/ledger比较容差0；统计display才float64，有限小数精确输出，非终止比例另存精确分数及展示口径。

每Fill signed q买>0卖<0：C_total'=C_total−q·p−fee，positions'=positions+q；cash_total变化不等于settled变化。C_set/U_free/U_short互斥，限制所得只扣已交收S_set；真实A=C_set−S_set−M−O−P_res−Z，Equity=C_total+Σq·mark+R−P。逐Fill/交收/cover和P4预算见CASH_BUCKETS_AND_PROJECTION.md，不得再用settled减全部S_total；同一预留/费用/应付只计一次。

复式交易：long buy借positions-cost，贷cash；sell借cash，贷positions-cost，差额credit realized-gain/debit realized-loss；佣金借fee-expense贷cash。short sale借cash贷short-position-liability（负position成本），cover相反，差额独立realized-short-PnL；所有每事件每币借贷=0。valuation借/贷持仓unrealized valuation与未实现损益，和成本子账分开；Journal可按科目重建实际账户，不能只写总额抵消行而无经济科目。

移动均价**不含费用**：同方向加仓 c'=(abs(Q)c+abs(q)p)/abs(Q+q)；减仓realized_gross=closed_qty·sign(Q)·(p−c)，剩余c不变；跨零拆成原仓平仓和新方向开仓两分录（同一个真实Fill，commission只扣一次且归因按数量比例精确分配），新仓c=p。费用作为expense全计，不在净收益再扣。realized/unrealized/净费用/红利/借券费之和对齐权益损益，外部注资剔除。

split r：已有q'=rq，unit cost'=cost/r，总成本/权益连续；raw mark相应变换，未成交订单先CANCELLED(CORPORATE_ACTION_REPLACE_REQUIRED)释放预留，不无声改原单数量/价；后续新决策才可建新订单。合成非整数结果/缺价格规则失败，不自动填补。红利按生效时合格旧股数与单位计，long借receivable贷dividend-income；short借dividend-expense贷payable；支付时只在R/P与cash间结转。价格除息损益和红利收入共同解释E，不能重复加total-return价格。

外部流带direction/flow_id，流前后估值不混入策略收益；每子区间R=(E_end−flow_at_end)/E_start−1（流在期首先调整起点），多流分段连乘TWR，不粗暴用日末权益忽略流时刻。简单无流r_t=E_t/E_(t−1)−1；cum=Π(1+r)−1；annual=(1+cum)^(252/n)−1。n为有效session间隔，不是权益行数。std(r,ddof1)√252；Sharpe=mean(r−rf_daily)/std(r−rf_daily,ddof1)√252；非正权益/样本不足/零方差明确undefined并解释。

MDD=max(1−E_t/max_{s<=t}E_s)，包括起始E；有外部流用流调整净值序列计算，保留原现金权益另表。turnover_full=Σabs(fill_notional)/decision前正权益、half=full/2；多decision分开分母、汇总明确加总，不混淆P4目标估计。滑点归因买signedqty·(actual−raw_open)（卖同样signedqty使逆向成本为正），成本已反映交易价格，展示的fee/slippage不能在净收益再次扣除。long/short现金流贡献与净收益核对。

FIFO统计选择CLOSED_FIFO_FRAGMENT，每非零(close_fill_id,entry_fill_id)交集计一条完成观察；partial/cross-zero、entry/exit费用与逐时点borrow/long红利/short应付按FIFO_ATTRIBUTION.md唯一规则归属。历史成本池只给计提当时未平lots，精确有理数分配，pay不再计收益，零利润nonwin，无完成/赢家/亏损给明确undefined原因。均价成本账与FIFO统计分层，不能互充自身期望。

参考候选在GOLDEN_CANDIDATES.json，给定输入、字面expected、计算依据与容差；reference_check.py只用标准库独立算术，不导入AQRP或任何待实现函数。审查方应另写参考，不能仅运行该开发方文件宣称独立答案已批准。

原G25静态算术不改：其U50为U_free50/U_short0，S200为S_set200；P4free758、真实A768、E_total1022只对该静态子例成立，不冒充short开仓/交收生命周期。新short前后A899守恒、partial cover及新FIFO/费用/事务候选另存SUPPLEMENTAL_CANDIDATES.json，原25/70输入/expected/容差及reference_check.py原字节保持。完整公式及预算保守差H见CASH_BUCKETS_AND_PROJECTION.md。
