# 冻结契约影响与待批准事项

本轮不改131冻结文件、P0 BACKTEST_CONTRACT/INTERFACES/DATA_CONTRACT、P4 API/源码/准入、106需求及原25组70项正确输入/答案/容差。四项原发现保持OPEN_PENDING_RECHECK，不自判CLOSED。

| 候选 | 原缺口 | 明确方案 | 影响/放行条件 |
|---|---|---|---|
| C-P5-001 | P0“全局phase总序”与“逐Fill原子”同一扁平队列有歧义 | 外层信封总序，70原子事务内80/90子记录，commit_seq重放 | 显式冻结契约解释/语义细化提案，不能暗称已兼容批准；主审核trace/状态/恢复，用户须在实施授权前明确接受该补充。如需正式改P0，另列版本/迁移批准；原文件本轮不改 |
| C-P5-002 | U与全部S重叠 | 互斥C_set/U_free/U_short、S_set子集；P4free=A−F_unused−H | 新P5合成规则细化，不改P4算法；H仅预算保守量，不是新prefunding。保守拒绝影响须主审/用户接受 |
| C-P5-003 | 卖单最低价不能给最大fee | 所有side/type固定双边[L,U]，LIMIT只收紧，paid+余单H≤F | 明确拒绝有利极端gap，GTC不漂移；用户后续接受经济选择 |
| C-P5-004 | FIFO完成粒度与历史成本不唯一 | CLOSED_FIFO_FRAGMENT，历史lot费用/红利池精确分摊 | 新统计convention版本，不能回填旧实验；用户后续接受 |

状态PENDING_GPT_WORK_RECHECK_AND_EXPLICIT_HUMAN_IMPLEMENTATION_ACCEPTANCE。G1可审可实施性，但不代用户确认契约变更/经济口径，不授实现/金融/部署权限。P5仍只计划。真实Windows两项持续DEFERRED / NOT VERIFIED，最后集成SHA与真实执行方案另行授权，不因此要求现在启用账户/改ACL。
