# RESEARCH-007：固定研究分数组合与冗余诊断

对应WORK-P3-003 / RESEARCH-001/006/007/008、EXP-002、INT-001；无账户、资金或P4持仓权重。接口提案 `compose(CompositeSpec, StageScoreRefs, frozen_protocol)->CompositeScores, RedundancyReport`。最小版本只选**预注册固定权重**，无拟合权重优化/按Validation或Test自动挑赢家。

CompositeSpec记录>=2个去重精确FactorRef/params_hash/版本、统一stage/时间频率/父数据/股票池/币种及可见cutoff、每因子单独方向d∈{-1,+1}、非负有限权重w（至少两个正项）、normalization、缺失规则、相关/冗余profile、protocol/lineage。本最小版本输入必须声明direction_applied=false；已按研究方向signed的stage输入返回DIRECTION_ALREADY_APPLIED，不猜测或再次取反。内置Reversal本身的公式语义由精确Ref确定，不能误当该标记。显式零权重作为DISABLED不进入有效集合；若正权重不足2返回INSUFFICIENT_COMPONENTS，全零/NaN/负数为INVALID_WEIGHTS；不能静默丢掉无效因子再改权重。

先取本时点所有正权重因子validity有效且available_at<=decision的**同证券交集**；不补0/不按证券重分权重。min_composite_n预注册，不足返回null+INSUFFICIENT_INTERSECTION及每个排除原因。默认normalization=`cross_sectional_sample_z`，在相同交集上分别均值去中+ddof1标准差，零方差任何有效组件导致本时点invalid；即使输入stage已标准化，也明确记录交集上重新z的阶段，避免不同scale隐式合成。raw单位不同仅能选该normalization；显式NONE仅当量纲/预处理相同且协议选择，不能默认绕过。合成 `s_i=sum(w_j*d_j*z_ij)/sum(w_j)`，方向只施加一次；不能再对已signed stage重复施加。产物记录input refs、mask hash、normalization统计/时点、每组件贡献、固定w/d与score、全部排除计数及protocol。跨日期训练参数只Train；这里的截面参数仅该时点可见交集，不读未来或标签。

冗余：用相同交集的原stage分数报告Pearson及平均并列秩Spearman矩阵、pair n、每时点及覆盖日统计；应用方向前/后的相关分别明确。规则 `abs(rho_spearman)>=tau` 且 pair_n>=min_pair_n、eligible_days>=min_days、触发比例>=min_fraction`。这些阈值必须预注册，不给正式默认值；缺少阈值只输出诊断、status=UNCLASSIFIED，不得自动删除。报告pair精确Ref、阈值来源、hit/eligible/missing/constant计数与RESEARCH_REDUNDANCY_FLAG，不自动改变权重或审批。阈值/方向/权重/替换选择均是新实验，先入ledger。Test数据上不返回给开发端，受同一隔离/访问预算约束。

手工例：A=[-1,0,1]，B=[100,0,-100]，w=[3,1]，d=[+1,-1]，sample z得到A=[-1,0,1]、B=[1,0,-1]，合成[-1,0,1]，Pearson/Spearman原相关-1，方向后+1。d都+1时合成[-1/2,0,1/2]；B正比例改scale结果不变。缺B证券时只在共同证券重新算z，不能取旧z子集冒充；明确测试见supplemental_cases.json。零权重数不足/全缺失/零variance/重复Ref/不同stage或时间、未来available、无阈值都须拒绝或给明确诊断。

将本设计接入INT-001研究服务/报告/ledger；组合输出仍是研究分数，不能生成订单、账户或P4策略批准。
