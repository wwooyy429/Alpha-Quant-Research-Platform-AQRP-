# 双边成交价格域与累计commission预算

处理WORK-P5-G1-003。明确选择买卖双方都受固定价格带约束的合成规则，**不允许有利方向无限gap**；须主审与用户后续接受，不是真实市场规则。

每订单在decision冻结p0和tick .01。所有BUY/SELL、MARKET/LIMIT共享L=ceil_tick(.95p0)、U=floor_tick(1.05p0)，L>U拒单。原raw_open和滑点后的实际价都必须在[L,U]。BUY=ceil_tick(raw_open·1.001)，SELL=floor_tick(raw_open·.999)。LIMIT买另要求raw/actual≤limit，LIMIT卖另要求raw/actual≥limit；limit正数且整tick，无交集拒单。有效price_upper：MARKET买/卖均U，LIMIT买min(U,limit)，LIMIT卖仍U（卖limit只加下界）。GTC沿原p0/L/U，不逐日改宽。

每Fill commission=HALF_UP_cent(max(1,abs(q)·price·.001))。整数share、每Fill至少1share（含完整odd-close）；b(Ueff)=ceil_cent(max(1,Ueff·.001))，余单上界H_i=remaining_qty_i·b(Ueff_i)。最多remaining_qty次Fill的最小费在内。每Fill n≥1，max(1,n·Ueff·r)≤n·max(1,Ueff·r)，向上cent界覆盖实际HALF_UP，累加得上界；不是用一次整单fee覆盖无限partial。

同decision的F_total固定默认10，F_paid+ΣH_i+F_unused=F_total，F_unused≥0；O_F=ΣH_i只进入现金预留一次。所有提交单一起算H，paid+ΣH>F拒绝整个调仓，不能先发部分订单再临时加F/缩单/改因子。逐Fill在最新版本计算真实n/price/f及余量H'_i=(remaining−n)·b，要求F_paid+f+ΣH'_i≤F_total（含其他活单），资金/真实post风险也通过后，才原子付费/Fill/更新预算/预留。失败无Fill/fee/容量消耗，明确取消余单留原因，不先扣费后伪装成功。

取消/到期只释放剩余H_i回F_unused，F_paid不退；决策终结释放规划余额不是新增现金流。H_i和F_unused在P4投影不能再各算一次同一预算。borrow/dividend独立计费，不混commission F。

p0=100域[95,105]；卖raw200400.41经10bps向下tick为200200.00，raw/actual均超U，MATCH_SKIPPED_PRICE_DOMAIN，Fill0/fee0/预算不变，DAY后到期。LIMIT卖100也不放行该gap；LIMIT买102的最高价为102。

partial例：3share、U105、b1、F3，初H3/paid0；三个1share Fill每次fee1，状态paid/H依次1/2、2/1、3/0，各步和为3。F2时提交3share就拒绝；不成交前两笔再强做第三笔。首笔后取消剩2，paid1/H0/F_unused2，实际只付1。额外负控：paid2、H1时注入真实fee2，假定余量H'=0，paid+f=4>F3，必须无Fill/无扣费拒绝。费用界不代替可用现金检查。
