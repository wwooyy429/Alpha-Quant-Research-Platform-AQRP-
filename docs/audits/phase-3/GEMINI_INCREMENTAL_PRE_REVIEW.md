# 可直接转交Gemini：P3 G1修订固定SHA复核

当前主审入口已依用户明确指令改为GPT_WORK_REVIEW.md；本文件保留为此前准备及可选Gemini补充参考，不再是强制重复门禁。历史原件与实际执行者不改。

仓库 https://github.com/wwooyy429/Alpha-Quant-Research-Platform-AQRP- ；PR https://github.com/wwooyy429/Alpha-Quant-Research-Platform-AQRP-/pull/5 。先记录PR描述AQRP_FIXED_REVIEW_SHA的完整40位SHA并checkout，起止核验，禁止审漂移HEAD；审查报告必须写出实际值。旧审查d10a55a7dd4bc9ca7793ed474bdc1b056916e96e，稳定main/phase2-baseline/v0.2.0=f26255fc40a3080bfa883ad64938f60036a14759。P3启动已授权，无业务实现，当前PLAN BLOCKED。

1. 先核g1-d10/原报告/任务/原始ZIP、RECEIPT逐项hash、审查身份GPT Work及开发方DEVELOPER_RESPONSE。原15组75断言PASS不能当Gemini G1放行；双OS原始417仅P2回归。五项开发方修订都未自行CLOSED。不得回写旧报告/正确Golden。
2. WORK-P3-001：TEST_ISOLATION_PROFILE.md单一OS多主体方案；完整Test原始输入/seed/行动/暴露/缓存/反馈/日志/预算/制品权限矩阵、管理员信任边界、物理开发投影、已公开合成数据不能成为formal Test、私有新seed、受管inbox/双OS主体证据/崩溃并发/反改名。分别判设计是否可部署、缺哪些用户决定、部署未验证；同用户逻辑对象不算隔离。
3. WORK-P3-002：LABEL_ACTION_PROFILE.md行动先于entry/exit的明确顺序、(entry,exit]权益、PER_OLD_SHARE前收盘锚点/拆股换算/跨日重置、pay在退出后的credit、P1完整日bar收盘才可见、LabelCoverageRef迟到/修订/label_available_at、fit<=cutoff与信息闭区间purge。独立复算supplemental_cases的每组时间/股数/应收/return/可用时点及±1us，不用未来实现生成答案；区分经济假设待用户确认与实际代码缺陷。
4. WORK-P3-003：COMPOSITE_RESEARCH.md是否完整覆盖RESEARCH-007研究合成/冗余；固定方向权重、不同scale、共同交集重z/缺失、不少于2正权重、诊断及无阈值UNCLASSIFIED、未来数据不影响过去、进入INT001服务/报告/ledger；不能删成P4或实现账户。
5. WORK-P3-004：REPRODUCTION_PROFILE.md旧0.2原wheel+锁+receipt独立解释器路由、新0.3完整bundle重审/精确API和三Ref矩阵、缺失/篡改/未知env拒绝；归档原件hash与逻辑/数值比较投影不能混淆。核引用原wheel/锁/bundle及实际保管；新路由没有运行过。
6. WORK-P3-005：HAC_INFERENCE_PROFILE.md的252/20(q+1)/q=max(h-1,5)、h集合、3模式、假设依据和拒绝契约是否有足够工程/统计依据；这些不是有限样本保证且未用户批准。独立用高精度方法复算非零mean的q1/q2 SE/z/p及m4失败项Holm/BY/BH，核样本/lag/空洞/污染及全family无效p拒绝；不得将门槛满足当假设已证明。正式协议/研究预算等未批准继续阻断金融批准。
7. 对照26需求23MVP+3CR的行为/接口/测试与106/16 canonical及50冻结资产，确保src/tests/tools/CI/锁/版本/P2原件保持。新supplemental_reference是开发方标准库参考，不能登记为你已独立执行；有权限请保存你自己程序/原始日志/环境/hash，无权限NOT VERIFIED。

输出：完整固定SHA、需求覆盖、5项逐条CLOSED/OPEN及证据、设计vs部署vs金融三类剩余条件/批准人、你真实执行的原始脚本/日志/环境/命令/hash、数学数值/性质/边界核对和PLAN PASS/PASS WITH CONDITIONS/BLOCKED。严格保留实际执行身份，不将GPT Work补充审或开发方自查冒充Gemini。没有用户具体决定/未能核方案时保留阻断；G1通过不等于P3实现/验收/合并/发布授权。不合并、不打标签、不进入P4。
