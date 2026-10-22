# Phase4 G1预审入口

2026-10-22 当前Phase4 G1：GPT Work对固定265af16353d85ce8c2d229a7517809d707498da8判PLAN PASS（受限工程设计），001 High/002 Medium均CLOSED_DESIGN，无新增阻断。原17候选独立复算、64项证据检查通过；仅设计数学，不是P4实现。原件与接收/关闭在docs/audits/phase-4/g1-265af16/。实际P4实施仍待用户单独授权，未阶段验收/合并/标签/部署/实盘/P5；Phase3受限发布与延期不变。以下旧BLOCKED/OPEN按原轮历史保留。

## 原轮设计修订与预审历史（以下旧状态非当前结论）

当前：GPT Work固定e40ddd0009cc30664c3a0fe0b74c4a497a541d77判**PLAN BLOCKED**。001 High/002 Medium仍OPEN；本轮最小数量门禁及风险性质修订已提出，待新固定SHA增量复核。详DEVELOPER_RESPONSE.md、ROUNDING_REFERENCE.md及g1-e40ddd0/原字节证据；不得自行CLOSED/PLAN PASS。P4实现尚未授权。

当前独立结论PLAN BLOCKED；GPT Work已审原e40，本轮修订尚未增量复核。Phase3基线 `0a57dccb5618ba08cd3572d6d6b78fec963a3041`；用户授权原话AUTHORIZATION.json。先读SCOPE_AND_DEPENDENCIES，然后PLAN、INTERFACE_DRAFT、原需求快照/追踪、GOLDEN_REFERENCE、ROUNDING_REFERENCE和TEST_AND_EVIDENCE_PLAN。FILE_MANIFEST列本轮资料hash，BASELINE_VERIFICATION列基线/源码及冻结检查。固定审查SHA写PR描述AQRP_FIXED_REVIEW_SHA，所有内容须在该完整SHA读取；HEAD变化必须另行增量复核。

重点判定：7项4MVP/3CR无遗漏；工程输入是否清楚/可行/不会绕过正式审批；PIT/单位/账户与价格一致；长短腿、gross/net/杠杆/换手、行业净总/Beta、borrow总额度与跨0、整手后风险及cash/restricted/margin算术；失败不可绕过；独立Golden候选是否正确；没有写P4业务或P5依赖。提出可部署性设计意见不等于授权部署。

请输出固定SHA、PLAN PASS/PLAN BLOCKED、每项发现级别与需求/位置/独立反例、拟修复建议、尚缺用户决定；分别列工程设计通过和真实隔离/正式Test/金融批准未验证。旧P3 SDK578及此PR CI只是P3回归，不证明P4实现。不得合并/标签/部署/进入P5，G1通过仍待用户授权实际P4实现。

增量主审重点：§3.1两类数量lot与不动/全平例外是否一致；原X01/X02及新增正负/跨0矩阵；X03/X04独立预存答案与收窄性质；free_cash/gross推论保持原经济口径；原G01–G20和发布资产不变；主审原CI核验范围不升级为原ZIP字节验证。
