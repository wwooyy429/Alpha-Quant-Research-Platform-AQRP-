# Phase4 G1预审入口

状态PLAN PRE-REVIEW REQUIRED；GPT Work未出具本轮结论。Phase3基线 `0a57dccb5618ba08cd3572d6d6b78fec963a3041`；用户授权原话AUTHORIZATION.json。先读SCOPE_AND_DEPENDENCIES，然后PLAN、INTERFACE_DRAFT、原需求快照/追踪、GOLDEN_REFERENCE和TEST_AND_EVIDENCE_PLAN。FILE_MANIFEST列本轮资料hash，BASELINE_VERIFICATION列基线/源码及冻结检查。固定审查SHA写PR描述AQRP_FIXED_REVIEW_SHA，所有内容须在该完整SHA读取；HEAD变化必须另行增量复核。

重点判定：7项4MVP/3CR无遗漏；工程输入是否清楚/可行/不会绕过正式审批；PIT/单位/账户与价格一致；长短腿、gross/net/杠杆/换手、行业净总/Beta、borrow总额度与跨0、整手后风险及cash/restricted/margin算术；失败不可绕过；独立Golden候选是否正确；没有写P4业务或P5依赖。提出可部署性设计意见不等于授权部署。

请输出固定SHA、PLAN PASS/PLAN BLOCKED、每项发现级别与需求/位置/独立反例、拟修复建议、尚缺用户决定；分别列工程设计通过和真实隔离/正式Test/金融批准未验证。旧P3 SDK578及此PR CI只是P3回归，不证明P4实现。不得合并/标签/部署/进入P5，G1通过仍待用户授权实际P4实现。
