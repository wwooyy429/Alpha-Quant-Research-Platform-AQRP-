# 可直接转交开发Codex的复核处置

GPT Work已独立复核PR #8固定完整SHA `35f93d640a2304121131d947a465f57a951cf63f`。**原WORK-P5-G2-001 High、002 Medium均CLOSED — FIX VERIFIED。** 提交后捕获异常已正确返回/落盘98.1、9事务、1Fill/fee1；六组前后×三类异常、原审查脚本、真进程退出同原run恢复通过。方向BUY/SELL与LONG/SHORT/MIXED分开、CLOSE/OPEN腿和单笔费用/数量/收益归属经独立十组及实际输出验证通过。原bfdcf30报告和错误样例仍原字节保留。

**新增WORK-P5-G2-003 High OPEN，整体G2仍BLOCKED / REQUEST CHANGES。** `src/aqrp/services/backtest.py:44–47`的`_reconciled_account`只核总现金/净应收应付，未逐桶比较Journal。真实服务合成LONG_SHORT在short Fill AFTER_COMMIT注入“cash_set+1、原未交收SHORT cashlot−1”，Journal不变、按现格式重算commit/post hash、所有桶非负且总现金/权益997.8不变。Journal证明cash_set897.9、U_short99.9、available797.9；服务却认证VERIFIED_COMMITTED_PREFIX并发布cash_set898.9、U_short98.9、available798.9。另cash_set−1/U_free+1的总额抵消控制同样漏检。外层FAILED不使错误的financial_state_known=true/last_committed_account变正确；本发现不声称真实资金损失或OS隔离被突破，属于现有“重算hash但财务不一致需UNKNOWN”负控的扩展。

请逐个核对Journal与cash_set/U_free/U_short，并按符号分别核R/P，落实相关现金lot/限制所得/交收非负/子集关系；不允许总额抵消替代分账证据。不一致时保留原始commit和恢复失败原因，FAILED+COMMITTED_STATE_UNVERIFIED/financial_state_known=false，不输出已知账户。新增恒总额桶重分类正反负控及合法交收/cover正控制，保留原六边界、坏链、读取错误、总额差、真实进程原run恢复及方向/费用/原始正确答案。不得通过删除负控或放宽现金口径修复。

审查方全新完整SDK1073通过；双OS官方各1073原ZIP/API摘要、精确成员及各3726文件/195别名子树、wheel69/锁/环境/终态核验通过。原25/70、新25/209独立算术通过，正常240提交/6136精确原始账本/腿/统计重建通过。通过项不能关闭003。

请在已授权十二项范围内修复003，原报告、原失败、两项关闭依据和新反例完整归档；新完整SDK/适用双OS官方原ZIP、环境/命令/输出/hash封存后更新AQRP_FIXED_REVIEW_SHA并提交新40位SHA独立复核。不要重开已真正修复的原001/002或回填旧版本通过，也不得自行关闭003/判G2通过或用户验收。

既有实施授权保持，无需重新取得启动许可。main/旧标签不动；Windows WI-R2-001/002及整体真实隔离继续DEFERRED / NOT VERIFIED，最终集成SHA真实执行另行授权，不能延期003。当前不启用账户、不改真实ACL/服务/调度、不运行真实正式Test、不授金融批准、不合并、不打标签、不部署、不实盘、不进入P6。本文件供用户转交，本会话未向GitHub或其他Codex会话发送消息。
