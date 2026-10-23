# Phase6 G1 修订候选 · 交GPT Work固定版本复核

当前独立结论：GPT Work固定`e71f6f090b102e4abfd70a5999e495f49546a1b5` **PLAN PASS WITH CONDITIONS**，001/002/003均CLOSED_DESIGN，无新增技术阻断。当前依据[原报告](g1-e71f6f0/received/REPORT.md)、[接收与处理](g1-e71f6f0/DEVELOPER_RESPONSE.md)、[实施前人工条件](g1-e71f6f0/IMPLEMENTATION_GATE.md)。三项设计选择及单独实施授权仍待用户明确；P6 NOT AUTHORIZED / NOT STARTED。AQRP_FIXED_REVIEW_SHA保持已审版本，归档头另列。以下交审文字/旧OPEN保留原轮历史，不覆盖本轮主审结论；核心设计字节不改。


仓库https://github.com/wwooyy429/Alpha-Quant-Research-Platform-AQRP-，PR #9。以PR描述AQRP_FIXED_REVIEW_SHA完整40位锁定新候选；只审该版本，不审漂移HEAD。最近独立结论仅对应`f7a1a68c5f747090f8c8a0e934f2fea859aec998`：PLAN BLOCKED / REQUEST CHANGES，001High/002、003Medium均OPEN。本轮三项是设计/参考修订，未自行关闭。

先读[g1-f7a1a68原报告](g1-f7a1a68/received/REPORT.md)、[发现](g1-f7a1a68/received/FINDINGS.json)、[开发方处置](g1-f7a1a68/DEVELOPER_RESPONSE.md)与[逐项状态](g1-f7a1a68/FINDING_DISPOSITION.json)。完整584855382-byte独立包/105文件已核、原失败日志保留；接收身份绑定原包SHA256，Git保存70原文件子集，大包仍外置。

修订重点：TASK_COMPLETION_CONTRACT（三kind、全部required slots/动态集合、最终工件/父链、completion+SQL屏障、剩余阶段恢复）；NESTED_CONTEXT_CONTRACT（实际P5内部P4、显式context/完整元组/调用前持久化、保留P5所属root、engine/provider/resume/replay完整适配表）；NUMERIC_REFERENCE_CONTRACT与reference_check（整数精确计算、HALF_EVEN、明确量程/拒绝与原始保留）。INTERFACE_DRAFT、TASK_AND_RECOVERY、兼容/测试计划已对应更新。

原GOLDEN_CANDIDATES整个32答案文件未改。新增SUPPLEMENTAL_CANDIDATES有95组独立字面/规则预期：完成31、绑定30、有效数值24、拒绝10。revision_reference只是有限设计例，不是TaskService/authority/并发实现。原2数值反例修订前实际失败日志和修订后输出均在g1-f7a1a68/developer-validation；32+95、270context和35 Fraction是开发方设计检查，不是独立G1或P6产品通过，请主审另写参考扩展。

请重点挑战：单子run终态不能升级Task；R成功/P5缺失、P4成功/B失败、全子run完成但全局回执缺失、取消竞态；B成功却缺必需P4必须失败关闭；内部P4原binding/真实根/合法错UUID/decision/parent/adapted request/epoch、resume同slot不重复构造、replay新所有权不写原源；新数值量程是待审提案，长输入不能默认28位舍入/报错，也不得放宽旧金融语义。G2真实故障矩阵见G2_FAULT_MATRIX。

基线main/phase5-baseline/v0.5.0仍59246f9fd391c1713b6bed65dd22280f4d248493，4738冻结文件、8需求（5MVP/3CR）、core锁、候选依赖和P5原审计/制品/金融代码均保留。validation/是首轮f7a1a68历史；本轮实际日志只看g1-f7a1a68/developer-validation及新固定SHA封存收据。新自动CI也只是继承P5回归，不是UI通过。

请输出新固定SHA、实际执行环境/方法/原始日志hash、三项逐一CLOSED_DESIGN或OPEN及新发现、8需求和独立数值/边界、待用户明确决定和PLAN PASS/BLOCKED。G1通过后仍需用户另行接受具体方案并单独授权实现；不据此开展业务实现。

WI-R2-001/002及真实Windows隔离DEFERRED / NOT VERIFIED，正式Test未运行、金融批准NONE、完整历史宿主限制不变。原失败/证据保留，无UI安装启动、账户/ACL/服务/调度变更、部署、实盘、正式Test、金融批准、合并、标签或P7。
