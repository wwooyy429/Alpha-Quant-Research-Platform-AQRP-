# Phase5 G2 固定版本审查入口

当前0.5.0.dev2修复勘误以[g2-bfdcf30/OUTPUT_CONTRACT_ERRATA.md](g2-bfdcf30/OUTPUT_CONTRACT_ERRATA.md)及[修复复核入口](g2-bfdcf30/REVIEW_PACKAGE.md)为准：原bfdcf30独立G2为BLOCKED，两项仍待新固定版本独立确认；以下原实施说明及正确经济口径保留，不把旧PENDING或正常SDK通过改称G2通过。


对象为PR #8描述的AQRP_FIXED_REVIEW_SHA完整40位值，必须与实际PR head核实一致后detached检出，禁止审漂移HEAD。G1固定5262032的四项CLOSED_DESIGN及用户C-P5-001/P5-D01–D10接受/单独实施授权已归档；这些不等于本次实现通过、金融批准或阶段验收。

先读IMPLEMENTATION_AUTHORIZATION、IMPLEMENTATION_CONTRACT、COMPATIBILITY_IMPACT、IMPLEMENTATION_TRACEABILITY、ENGINEERING_CODE_REVIEW和IMPLEMENTATION_IDENTITY；再独立读取代码、原始实际运行工件。此候选不含独立GPT Work G2结论，所有实现关闭/阶段验收由后续独立报告和用户明确决定。

## 重点核验

1. C-P5-001队列总序，40组合/50真实风险/60提交/65控制/70逐单最新状态和80/90子事务；同刻前笔改变后笔风险/容量；准备/提交两边实际进程崩溃及同原run恢复，异字节ID冲突，损坏链失败。
2. 真实P4双投影，C_set/U_free/U_short互斥、S_set已交收子集、short交收前后A899、cover/FIFO原始cashlot、payable与fee/O不重冻；实际P5风险和P4保守预算分别判定，不自动放宽保守拒绝。
3. 双边价格域/限价/有利gap拒绝、严格未来开盘、每Fill最小费、所有余单最坏费用预算、共享10容量/lot、历史ADV发布与修订/P1原值绑定。不能把当天未来日终量或晚到切片用于过去成交。
4. 复式账本、均价/跨零、CLOSED_FIFO_FRAGMENT及历史borrow/dividend池、不二次舍入、分红支付不重计、拆股/未知退市/显式已知回收、stale/margin失败保留。精确宽输出不得按34位输入域截断。
5. 原始Fill/action/cashflow/Journal独立重建账户/收益，而不是复用生产函数生成答案；大数/边界/性质与预先字面答案，统计A252/ddof1/TWR/undefined及真实多空净贡献。
6. 真实P1九文件/P3终态engine/config/P4候选与risk/result/audit原字节和返回值，合法父UUID一致篡改、终态后补文件、别名/链接/读取时更换、发布及返回字节损坏；无skip_approval，正式入口只拒绝。
7. 固定候选真实wheel干净安装、完整SDK及旧P4/原20+四/91/旧Ref实际重放、双OS官方CI原始ZIP/API摘要/执行SHA、JUnit/覆盖/源码包/环境与数据Hash。部署/正式Test/金融批准和真实Windows隔离不能从工程SDK推定。

## 证据获取与范围

开发方在完成固定提交后，把实际命令/原始stdout/stderr、环境、Git源码、wheel、原始GitHub Actions ZIP、下载/摘要及逐成员核验、实际工程输入/交易/账户、独立参考及首次失败封存在外部review目录，并在PR描述提供实际路径、完整SHA、包大小和SHA256。未记录执行结果时必须NOT VERIFIED，不能把本文件当测试通过证据。探索期的未提交版本自测与最终干净SDK分别标识，保留原失败，不补记为独立审核。

原G1报告/失败、131冻结输入原表和12份设计身份不改。实施只升级七个已列明的版本/准入收据/CI/覆盖文件，其余金融基线和答案按身份表严格校验。新阶段检查替代仅针对P4包形态的checker，不改原checker或其保护答案。

真实WI-R2-001/002持续DEFERRED / NOT VERIFIED，PR7候选6207450未集成，最终全部开发完成的完整集成SHA真实验证另行授权。正式Test、金融批准、完整历史宿主复现的延期/限定重放边界保留；当前无合并、标签、部署、实盘或P6授权。
