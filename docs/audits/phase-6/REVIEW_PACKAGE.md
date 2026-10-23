# 交 GPT Work · Phase6 G1 固定版本计划预审

仓库 https://github.com/wwooyy429/Alpha-Quant-Research-Platform-AQRP- 。计划PR中 `AQRP_FIXED_REVIEW_SHA` 必须锁定完整40位SHA；请检出该固定提交，记录实际HEAD及所有偏离，仅审锁定版本。当前申请PLAN预审，未实现、未安装UI依赖、未运行浏览器，不申请G2/金融批准/阶段验收。

基线 main/phase5-baseline/v0.5.0 `59246f9fd391c1713b6bed65dd22280f4d248493`，用户已验收Phase5十二项；普通合并36c2691、合并后SDK1158/原20+4/91及原始工件/哈希见PHASE5_RELEASE_RECEIPT、PHASE5_SEALED_EVIDENCE和 ../phase-5/publication/。原始独立G2固定1c5 PASS；这些证明P5前置，不是P6产品测试。

审查顺序：AUTHORIZATION / STATUS → REQUIREMENTS_SNAPSHOT / REQUIREMENTS_TRACEABILITY → PLAN / SCOPE_AND_DEPENDENCIES → INTERFACE_DRAFT / TASK_AND_RECOVERY_CONTRACT / PAGE_SPECIFICATIONS → MATH_AND_COMPARISON_CONTRACT / GOLDEN_CANDIDATES → DEPENDENCY_AND_COMPATIBILITY_PLAN及两OS候选锁 → TEST_AND_EVIDENCE_PLAN / OPEN_QUESTIONS / FROZEN_INPUTS及静态证据。

请独立核对：8项（5MVP/3CR）不遗漏；P1–P5冻结资料未改、无src/tests/tools/工作流/根锁变更；完整UI/CLI/SDK共用服务而非页面重写金融算法；幂等、取消/宕机和真实核心终态/逐桶未知状态安全；配置rollback与精确Ref、真实来源及manifest验证；三入口数值比较不宽松忽略金融字段、hash或UUID；候选依赖仅解析、core版本未升级；AppTest非实际浏览器，原始双OS/真实GUI证据计划足够。

请另写独立参考，复算预设设计答案，并扩展边界与反例，不从未来待测函数生成期望。区分设计参考/既有P5回归/未来P6产品测试；报告固定SHA、实际方法与环境、逐项需求、严重度/文件定位/复现、待用户决定及PLAN PASS/BLOCKED。若主分支或PR漂移，新SHA须单列，不能把旧结论外推。

WI-R2-001/002及真实Windows隔离DEFERRED / NOT VERIFIED；正式Test未运行、金融批准NONE、完整历史宿主未验证，仅已接受包/锁/旧Ref/结果投影。原失败及收据保留。禁止启用账户/真实ACL/服务/调度、部署、实盘、真实正式Test或授金融批准。G1通过不等于用户实施授权；本轮不合并、不打标签、不进入P7。
