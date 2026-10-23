# FIFO closed-fragment计数与逐事件成本归属

处理WORK-P5-G1-004，唯一统计单位 **CLOSED_FIFO_FRAGMENT**：每个非零(close_fill_id,entry_fill_id)FIFO交集计一条已闭合观察。一次close跨两个entry lot计两条；同entry分两次close也计两条。不等整entry全平，不按flat-to-flat；未平量不进分母。顺序(security,direction,entry_time,entry_fill_id)；入场每Fill建不可追加的新lot，后加仓另建lot。

lot保存remaining_qty、未分配entry_fee及按时点分配的borrow/dividend pools。close按被平qty/close前remaining比例消耗该lot的历史未分配池，exit_fee按该Fill各fragment数量分配。全部用精确有理数；实际账户每事件只舍入一次，fragment不第二次货币分舍入。fragment+剩余pool精确等于事件已入账额，不丢“余分”或按输赢给尾差。显示可HALF_UP，胜负使用未舍入精确net、容差0，保存numerator/denominator。

跨零一真实Fill先close旧方向再open新方向，commission按close_qty/total与open_qty/total分一次；close部分再FIFO分配，open部分进新lot池。新lot不承担旧lot的历史费用。移动加权均价仍是账户成本法，FIFO是统计与明示cashlot跟踪，二者分开不能互充自身期望。

借券在收盘95且mark已确认后，每证券总额B=HALF_UP_cent(abs(short_qty)·mark·.01/252)，只按该时点**实际未平lot**股数比例分配有理数。95前已cover者不承担之后费用，95前新开仍持有者承担当期费用，无未声明日内时长比例。历史成本各归当时lot，后续部分cover按qty/remaining消耗池；不得把累计position费按当前两股重平均。每笔费用与lot归属/Journal同事务提交。

ex/资格10时按真实合格lots给long dividend credit、short dividend cost，均进入本指标 **total-accrual-attributed closed-fragment net**。old-share/split单位先转换正确，按当时合格股数分配原事件总额；同刻entry前已发生的权益不归新lot，同刻exit前确认的权益归旧lot。pay只结算R/P与cash，不重算已经闭合fragment净额或再记收入，未付权利按确认时归属，不猜违约。

fragment net=sign(entry_direction)·closed_qty·(exit−entry)−entry_fee_alloc−exit_fee_alloc−borrow_alloc−short_dividend_alloc+long_dividend_alloc。win_rate=positive_net_count/closed_fragment_count；zero是nonwin且单列，不进入赢/亏均值。profit_loss_ratio=mean(positive net)/abs(mean(negative net))。无完成两指标undefined(NO_CLOSED_FRAGMENTS)，无赢家/亏损分别NO_WINNERS/NO_LOSERS，全零NO_NONZERO_OUTCOMES；未平pool另列，不能伪作零利润完成交易。sum(fragment net)+未平经济贡献需按公开口径核权益损益。

固定例：buy2@100 fee1，sell1@104 fee1、sell1@97 fee1→entry各.5，净+2.5/−4.5，胜率1/2，ratio5/9，总−2，不改成全lot一笔。

short A1@1000 day1、B1@1000 day2：day1总borrow.04只给A，day2总.08分A.04/B.04。cover A1@997.93，entry/exit各1：2.07−2−.08=−.01，B未平仍携.04，不能把总.12均分令A+.01。partial借费例：short2 day1费.08，cover1分.04；剩1 day2再.04，末fragment承担.08，总.12。

split改变剩余股数/单位成本但不改各lot未分配金额；完整碎股规则缺失仍失败。新候选还覆盖跨零、long dividend、short ex后pay前退出、无完成/赢家/亏损/零利润及分摊精度。当前仅预注册设计答案，尚无P5产品结果。
