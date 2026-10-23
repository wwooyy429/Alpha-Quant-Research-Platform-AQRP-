# GPT Work Phase5 G2：接收与修复处置

唯一原审查 SHA：`bfdcf30e525ff802ea483974f58163eedc029ce8`。原结论 **G2 BLOCKED / REQUEST CHANGES**；WORK-P5-G2-001 High、002 Medium 均为 **OPEN**。本轮按有效十二项实施授权修复，不重新请求阶段启动许可，不自行关闭发现。G1 四项 CLOSED_DESIGN、用户设计接受及实施授权分别保持原记录，未产生用户 Phase5 验收或发布授权。

原报告、交接、发现、反例脚本、命令、输出、原始实际生产反例包在 received/ 按原字节保存。RECEIVED_IDENTITY.json 记录独立原包 e68d2c5a…、585712844 bytes 的 CRC、124 声明成员+manifest 及全部 size/hash 接收核验；大型独立 SDK/官方原包仍在原审查目录及原封存 ZIP，不把它们冒称本轮新实现测试。原正确答案、失败日志、main/旧标签不改。

## WORK-P5-G2-001 High：FIX IMPLEMENTED / PENDING INDEPENDENT RECHECK

原问题属实：原子 commit 发布后，KeyboardInterrupt/ContractError 可早于 recover 和逻辑 trace 更新。直接封存缓存将已生效第9条成交漏掉；磁盘真实现金98.1被写成1000。不能以 Windows R2 延期豁免此工程缺陷。

现在失败/取消处理新建事务读取器，在写锁内重新核验完整 initial/commit 链、pre/post/hash/序号/子记录，并冻结一致 state、records 和原始文件身份。用原始 Journal 重建现金、数量、应收应付并核经济恒等式后，才允许发布 last_committed_account、failed-state、完整 transactions、transaction-files 及 committed-trace。原始调度 trace 单独保留为观察记录，可能终止于原子发布与观察间，不冒称完整提交证据。捕获前后同一 run 不回滚已提交 Fill、不再次成交/扣费、不删除未提交 prepared 文件。

链损坏、读取失败或经济对账失败时：FAILED、COMMITTED_STATE_UNVERIFIED、financial_state_known=false，保留原始事务及恢复失败原因；不输出缓存 last_committed_account，不封存虚假的 failed-state/transactions。恢复证据写入 failure-recovery.json。普通异常在记录实际终态后继续抛出；可读 ContractError/KeyboardInterrupt 保持原公共服务行为。原 result 已落盘后的发布失败继续拒绝作为成功结果；部分发布已有文件只允许原字节一致复用，冲突保持非终态证据，不覆盖。

新增实服务提交前/后×KeyboardInterrupt/ContractError/RuntimeError 六组，字面答案分别1000/8/0与98.1/9/1（现金/事务/Fill，费用0或1），核返回/落盘/原始commit/股数/剩余容量/hash和重复恢复拒绝；另增链、读取、重算hash但经济不一致负控，真实服务子进程退出同原run恢复、部分发布与冲突保留。原实际进程退出和成功/损坏链回归继续执行。

## WORK-P5-G2-002 Medium：FIX IMPLEMENTED / PENDING INDEPENDENT RECHECK

原问题属实：oldq=0被归入SHORT；报告指出当前FIFO/汇总PnL未被该字段改变，本轮不夸大为实际收益损失。

Fill.direction 现在描述持仓暴露腿方向：单腿 LONG/SHORT，跨零为 MIXED；execution_side 独立表示 BUY/SELL。position_before/after、position_legs 明确每腿 OPEN/CLOSE、暴露方向、正数量、signed_qty、精确分摊 fee 和 realized_gross。先平后开但仍只有一个实际 Fill、一份实际费用；分腿费用仅归属元数据，不产生新 Journal 或重复收费。纯开多、加多、平多为LONG；纯开空、加空、平空为SHORT。两个跨零方向均为MIXED，不能按成交买卖方向误归类关闭空头的收益。

该未发布候选的输出更正/新增枚举见 OUTPUT_CONTRACT_ERRATA.md；不回填0.5.0.dev1旧实验或移动版本标签。新版工程包0.5.0.dev2。十组开/加/减/全平/跨零与真实服务返回/落盘回归保留账户/FIFO/多空贡献守恒。标准库独立参考同时从成交前头寸重建腿数量/费用/已实现收益，不调用生产方向函数。

## 验证与待办

原版本运行新增回归的失败原始日志保留；新增字段断言失败不被夸大为20个独立金融缺陷。首次修复自测中容量断言错误把 remaining 当 used，正确契约为两已观察正容量切片合计20，成交9后剩11；修正测试并保留6失败/14通过原日志，未放宽现金/事务/费用等答案。

本文件只说明实现与拟验证要求，不预写完整 SDK/CI 成功。最终事实以 PR #8 新完整 AQRP_FIXED_REVIEW_SHA 对应实际干净 SDK、双OS官方原始ZIP、原命令/环境/数据/代码/工件hash及外部封存收据为准。原两项持续 OPEN_PENDING_INDEPENDENT_RECHECK，未 G2 PASS、未用户验收。

Windows WI-R2-001/002 持续 DEFERRED / NOT VERIFIED，最终完整集成40位SHA真实验证另行授权。正式Test未运行，financial_approval=NONE；正式入口APPROVAL_REQUIRED。无账户/真实ACL/服务/调度变更，无合并/标签/部署/实盘/P6。
