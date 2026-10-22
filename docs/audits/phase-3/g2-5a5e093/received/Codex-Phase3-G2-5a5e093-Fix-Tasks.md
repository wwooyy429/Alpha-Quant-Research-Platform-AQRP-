# 开发方修复任务 · 固定SHA 5a5e093c2e9b39abe1332e49d1df40d20f9fd33f

G2建议：REQUEST CHANGES / IMPLEMENTATION BLOCKED。G1 PLAN PASS不变。发现1 High/2 Medium，审查方4个真实回归失败；本机独立SDK564、原16+4、数学91及扫描3控制通过，不能用这些成功代替新缺陷闭环。

1. WORK-P3-IMPL-001 / High：labels.py:186、227遗漏决定listing/delisting资格的选中security_master依赖。将实际因果依赖纳入label_available_at/版本/hash。晚到退市更正使标签1月5日才有效，不得标1月4日可用；修复后fit_cutoff=1月4日12:10须拒绝该新标签，保留原17组及purge边界。
2. WORK-P3-IMPL-002 / Medium：approvals.py:125–129应先要求approvals.json存在于不可变终态manifest并匹配原字节hash，再验证proposal。原run没有该工件时，后补文件必须拒绝；不能只path.exists或读当前文件。强化终态文件集合/绑定策略并保留缺文件及后补文件两个负例。审查反例仅公开ledger/测试key，不是实际金融批准。
3. WORK-P3-IMPL-003 / Medium：pipeline.py:206–211的公开compose入口必须对齐共同decision cutoff、拒绝未来available和混合decision_time，保留血缘。修复两项独立负例及正常同刻/交集重新z/方向控制。反例属于公共SDK入口，未夸大成普通统一服务已发生泄漏。
4. 将test_review_regressions.py四项期望集成到适当测试位置，保持正确expected和旧失败证据，不删用例或降低门槛。仍需完整26项、五stage、全ledger/cache/OOS/报告/INT001和旧三Ref正向重放。
5. 代码变化重新生成全bundle/工程receipt，保留旧精确Ref及原锁；完整干净SDK、原16/4、冻结数学/独立关键答案、双OS原ZIP/hash/coverage、扫描例外对抗控制均以真实输出为准。提交新40位固定SHA并锁PR描述供GPT Work复核。
6. U-001只批准设计：不部署、不创建账户/ACL/服务/调度器。实际权限/私有Test/模型证明/正式协议和金融批准仍NOT VERIFIED，缺项fail closed，不全项验收VALID004或自动ResearchValidated。
7. 不合并、不标签、不进入P4；不把G1/开发自测/本机564成功登记为Phase3用户验收。接收本报告和证据按原字节归档，不改审查原文。

原始复现：adversarial_probes.py、late_master_causal.py、verify_fit_leak.py；正确拒绝/时钟期望在test_review_regressions.py。四失败JUnit和所有成功/失败日志保留。完整逐需求映射见canonical-phase3-implementation-coverage.csv。
