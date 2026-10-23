# 互斥现金桶、交收与P4保守投影

处理WORK-P5-G1-002；新合成profile候选，不引入真实市场或隐含临时prefunding。C_set为已交收现金；U_free为未交收且不再属于未平空仓限制所得的卖出款；U_short为未交收、仍属于未平空仓的原始gross short所得。**C_total=C_set+U_free+U_short**，三桶互斥。S_set仅是C_set内未平short限制所得的子集，0≤S_set≤C_set，不是第四现金桶。S_total=S_set+U_short；U_short已排除在C_set外，不能再减S_total一次。

V=M=当前RAW mark短仓绝对市值（100%额外margin）；O=O_N+O_F为订单notional/commission预留，P_res为已确认短仓红利等应付准备，Z为其他不重复冻结。真实可用A=C_set−S_set−M−O_N−O_F−P_res−Z。有效状态A≥0，不能把一份金额重复编码在O/P/Z。Equity=C_total+signed_position_value+R−P，不从权益再扣S/M/O。市场mark使A<0则MARGIN_BREACH，保留实际亏损/失败，不制造可用现金或融资。

Commission预算独立：F_total=F_paid+O_F+F_unused，F_unused≥0，默认初始10。O_F已计入O，F_unused只在P4投资规划中排除；不是额外现金扣费。borrow/dividend不混进commission F，独立事件资金检查。

| 事件 | 同一原子事务内的迁移 |
|---|---|
| 新short gross n、fee f | U_short+=n，C_set−=f；S_set不变，S_total增n；M重算。不能再把n加进C_set |
| long卖出 | U_free+=gross，C_set−=fee；U_free不能立即新买 |
| buy/cover | C_set−=notional+fee，不能用U_free/U_short；只释放本次真实平仓对应的S_set/O/M后核post资金，不能先释放他单/他仓资金 |
| T+1交收U_short中n | U_short−=n，C_set+=n，S_set+=n；A、持仓、mark、E严格不变 |
| T+1交收U_free中n | U_free−=n，C_set+=n；A增n，为已解除short限制/long卖出款真实到期解冻 |
| cover解除所得限制 | 开仓Fill建立的FIFO gross-proceeds cashlot为权威；已交收部分S_set减少，C_set不因解冻增加；未交收部分U_short→U_free，仍按原settlement_id/due_time交收 |
| long→short跨零卖单 | 一真实Fill分close_long/open_short，gross分别进U_free/U_short，整笔fee只付一次 |
| short→long跨零买单 | 从C_set付全部notional+fee，实际close_short释放对应限制，新long可售数量T+1；不可用未交收所得 |
| ex-dividend | long确认R/收入，short确认P/费用及P_res，不移动现金；lot归属见FIFO_ATTRIBUTION |
| dividend支付 | long R→C_set；short C_set、P、P_res同时减同额，已准备款不能再扣一遍A |
| borrow95 | 从C_set扣已舍入实际fee、重核post资金，lot归属与Journal同事务，不能以未交收款付费 |

cashlot与原settlement条目绑定；cover可将条目拆为受限/非受限部分，总额/交收时点不变。split改股数/单位gross成本不改总gross限制额，缺碎股规则失败。新short佣金须有已交收现金付；买入可售数量另算，不由现金桶推断权限。

最小费全生命周期：初始C_set1000，short1@100 fee1→C1099/C_set999/U_short100/U_free0/S_set0/V100/E999/A899。T+1→C_set1099/U_short0/S_set100，E/V不变，**A仍899**，没有旧799→899的虚假解冻。

partial cover：short2@100 fee1，mark90时C1199/C_set999/U_short200/S_set0/V180/E1019/A819。T+1前cover1@90 fee1→C_set908/U_short100/U_free100/S_set0/C1108/V90/E1018/A818；两部分交收各100后C_set1108/S_set100/U均0/A918。增加100仅来自已cover而仍等交收的U_free；未平short部分转S_set不改变A。T+1后才cover的对应最终C1108/S_set100/A918相同，费用只一次。

## P4兼容预算（原P4 API/业务不改）

新rebalance仅在无ACCEPTED/PARTIAL旧单时调用P4，但以下公式也用于生命周期对账：B=U_free+U_short+O+P_res+F_unused，C_alloc=C_total−B=C_set−O−P_res−F_unused，E_alloc=C_alloc+signed_position_value。C_alloc≥0、E_alloc>0；P4 account用C_alloc/E_alloc、真实positions/marks/sellable/borrow、fee_reserve=0。

P4自身冻结V+额外V，投影账户restricted_cash=max(V,S_set)+Z（这是明示预算投影值，不冒称真实原生冻结）；故nonshort_restriction=Z+max(S_set−V,0)，**不是S_total**。P4free=C_set−O−P_res−F_unused−Z−V−max(S_set,V)。明示预算保守差额H=max(V−S_set,0)，则 **P4free=A−F_unused−H**。

H来自既有P4模型，仅是投资预算保守量，不是P5现金冻结/新prefunding/费用，不写真实Journal。交收前后H变化可改变P4预算，但不得改变P5真实A。实际提交/逐Fill仍按真实E_total/现金桶完整重核，两套都通过；保守不可行须报告A/H/两种equity，不能冒称真实资金缺口。

short1例F_unused10：交收前C_alloc989/E_alloc889/H100/P4free789；交收后C_alloc1089/E_alloc989/H0/P4free889；两次A均899。合法初始short1目标在P4初始E_alloc990下，目标cash1090、V100+margin100，free890，允许正常建模拟单，不拒绝所有新short。

原G25字面答案不改：其孤立静态U50指定为U_free50/U_short0，S200为S_set200，F10为F_unused10。C1200/C_set1150、V180/P2/R4/O0/Z0→A768，B62/C_alloc1138/E_alloc958/P4free758/H0，E_total1022。它未验证新short全生命周期；新增补充案例另覆盖。完整实际账户/P4请求接线待实现授权，不冒充本轮产品运行。
