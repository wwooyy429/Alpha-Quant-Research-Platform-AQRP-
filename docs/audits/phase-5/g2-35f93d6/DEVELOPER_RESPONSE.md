# 固定35f93d6独立复核接收与003处理

GPT Work对`35f93d640a2304121131d947a465f57a951cf63f`判G2 BLOCKED / REQUEST CHANGES。001、002为CLOSED — FIX VERIFIED；新003 High OPEN。本候选仅实施修复，不自行关闭003、不宣称G2通过/用户验收。原报告、故障脚本/输出、收据及reviewer-production-artifacts.zip原字节见received/；585039742字节原封存包、150声明文件+manifest的CRC/精确成员/全部大小哈希接收核验见RECEIVED_IDENTITY.json，原大ZIP外部保留。不修改原错误VERIFIED结果，不回填旧实验。

|发现|独立审查事实|当前处理|仍待|
|---|---|---|---|
|001 High|35f93d6独立确认关闭|事务前缀重读、真实98.1、原run恢复及未知状态拒绝保留|既定回归，不重新开启|
|002 Medium|35f93d6独立确认关闭|BUY/SELL与LONG/SHORT/MIXED、CLOSE/OPEN腿及单笔费用保留|既定回归，不重新开启|
|003 High|OPEN：cash_set+1/U_short−1漏检，797.9错报798.9|正常projection及失败恢复统一逐桶/逐科目精确核账；lot归属/原始空头所得/交收/限制子集验证|新固定完整SHA及SDK/双OS原证据提交GPT Work独立复核；独立关闭前仍OPEN|

实现不只检查总现金：cash_set、U_free、U_short分别与原始Journal比较，receivable与负号payable分别比较；同时核手续费、借券、分红、已实现损益、外部流及持仓成本/估值科目。禁止相反误差净额抵消。所有现金lot非负、唯一、类型/交收标志完整；每个SHORT lot恰好绑定一个原空头FIFO条目，金额等于剩余股数×原始价（拆股守恒），到期与该条目一致。完成交收的Journal记录增加settlement_session元数据，按持久化交收进度核验标志，不从可变调度当前session推定；会计金额、事件顺序和T+1口径不变。S_set必须为cash_set内非负子集。正常已记账的available<0仍可保留真实margin loss，不能把负可用金额本身当未知。

任一不一致触发现有未知状态路径：FAILED、COMMITTED_STATE_UNVERIFIED、financial_state_known=false、无last_committed_account/failed-state/已知transactions副本；原磁盘提交和原故障原因保留。无回滚假象或覆盖原失败。

新增43项覆盖实际公共服务七组重哈希故障（六方向现金桶错分及R/P相互抵消）、正常projection中六方向全桶非负的恒总额负控、逐金融科目负控、合法T+1前后部分cover/拆股、限制所得归属/交收/子集、缺失或矛盾交收证据，以及真实margin loss正控制。修复前第一轮12失败/7通过日志原样保留；没有删除失败用例或改变正确经济答案。标准库raw-event/Journal参考另外逐R/P及实际AccountUpdated的cash_set/U_free/U_short/S_set/R/P核对。探索自测与最终提交已安装wheel SDK分开；实际数量和执行收据以PR描述外置封存为准。

边界不变：十二项10MVP/2CR、原12设计与3444冻结文件、旧正确答案/四因子实现/锁/main/旧标签保留。WI-R2-001/002仍DEFERRED / NOT VERIFIED，最终集成固定版本真实权限另行授权；无真实ACL/账户/部署/正式Test/金融批准/实盘/合并/标签/P6。
