# 可直接转交开发 Codex 的 Phase5 G2 修复说明

GPT Work已独立审核PR #8锁定完整SHA `bfdcf30e525ff802ea483974f58163eedc029ce8`，结论 **G2 BLOCKED / REQUEST CHANGES**。发现 **WORK-P5-G2-001 High、WORK-P5-G2-002 Medium，均OPEN**。原G1四项CLOSED_DESIGN不变，不能把设计关闭或本次SDK通过写成实现已验收。

**001 High：** `src/aqrp/services/backtest.py:158–163`在异常/KeyboardInterrupt后直接封存旧`simulator.store.state/records`，而`transactions.py`在原子发布commit到刷新内存之间仍可能被中断。审查方实际已安装wheel和公共服务复现：初始1000，9股@100.1、fee1已生效；AFTER_COMMIT中断后服务返回/落盘CANCELLED或FAILED，last_committed_cash却为1000、transactions8条，磁盘可信commit恢复为98.1、9条、Fill1/fee1。BEFORE_COMMIT正控制1000/1000、8/8、Fill0。请使失败/取消发布以已验证持久化提交前缀为准，统一返回/failed-state/事务/费用/容量，链不确定时保留证据并如实失败关闭，不删已生效commit或伪造回滚/已知余额。补提交前/后×KeyboardInterrupt/ContractError/普通异常的真实服务回归、真实进程退出同原run恢复与损坏链负控；不能用单独的“直接退出可恢复”覆盖“捕获后终态化”组合缺口。

**002 Medium：** `src/aqrp/backtest/ledger.py:306`以oldq>0判断LONG，其余SHORT，导致从空仓BUY+9、最终持仓+9、lot.direction+1的Fill返回/落盘却标SHORT。当前账户总额及汇总LONG净贡献正确，本报告没有声称该字段已经造成汇总PnL损失。请定义并修正开/加/减/全平及跨零的方向/腿字段；若本字段只指平仓腿需准确命名、无平仓时为空，另正确表示开仓腿。一真实Fill不得因两腿重复费用。补真实输出/持久化/返回一致性及账户/FIFO守恒回归，不回填旧运行原件。

审查方完整新venv/wheel SDK **1049通过**，旧Ref/旧20+4/91及完整smoke实际运行；原25/70和新25/209独立复算通过；正常8份因子运行的240提交/6096精确原始重建比较通过。官方Windows/Ubuntu各1049原ZIP/API摘要/完整成员/wheel69/终态工件核验通过，各3429额外文件的189别名子树经另写程序逐字节对账。上述通过项不能关闭两项实际反例。

请按已获授权的十二项受限工程范围修复，保留本报告、反例脚本、原始失败、正确答案及冻结/包装兼容记录；完整SDK和适用双OS官方原ZIP、原命令/环境/hash重新封存，更新PR #8的AQRP_FIXED_REVIEW_SHA并提交新完整40位SHA供GPT Work复核。不得自行关闭发现、判G2通过或改写旧失败为PASS。

Windows WI-R2-001/002及整体真实隔离仍DEFERRED / NOT VERIFIED，最终集成固定SHA另行授权验证；当前P5已提交资金异常001不能随R2延期。保持正式入口APPROVAL_REQUIRED、financial_approval=NONE，不启用账户、不改真实ACL/服务/调度、不运行真实正式Test、不授金融批准、不合并、不打标签、不部署、不实盘、不进入P6。此处不要求重新取得已获实施启动许可。

本文件仅供用户转交，本会话未向GitHub或开发Codex发送消息。
