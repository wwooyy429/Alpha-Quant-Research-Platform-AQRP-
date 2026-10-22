# Phase5 G1 修订候选交审入口

2026-10-23 Phase5十二项（10MVP/2CR）已形成0.5.0.dev1受限工程实现候选，**G2 PENDING，未阶段验收/发布**。G1固定5262032及用户C-P5-001/P5-D01–D10接受/单独实施授权见phase-5/IMPLEMENTATION_AUTHORIZATION.json；实际代码/接口/逐项测试映射与七项包装兼容变化见IMPLEMENTATION_REVIEW_PACKAGE、IMPLEMENTATION_CONTRACT、IMPLEMENTATION_TRACEABILITY及COMPATIBILITY_IMPACT。开发方验证只认PR #8锁定40位SHA对应的真实SDK/CI原包和外置封存收据，不把本状态说明当PASS。旧金融源码/答案、十二份G1设计身份、主干/旧标签不动。WI-R2两项继续DEFERRED / NOT VERIFIED；正式Test/金融批准/旧完整宿主边界保留，无合并/标签/部署/实盘/P6。以下各轮旧状态保留历史。


2026-10-23 用户已明确接受G1固定5262032的C-P5-001及P5-D01–D10（含C-P5-002–004），并单独授权既定12项（10MVP/2CR）P5受限工程实施，当前IMPLEMENTING。原话/范围见docs/audits/phase-5/IMPLEMENTATION_AUTHORIZATION.json。G2、阶段验收、合并/标签另待；真实Windows R2两项继续DEFERRED / NOT VERIFIED，正式Test/金融批准/历史宿主边界不变，无部署/实盘/P6。以下待接受/待实施许可均为原轮历史。


2026-10-23 最新Phase5 G1：GPT Work对固定 `5262032bee4f631f68763e57510e1878945f6b8c` 判 **PLAN PASS WITH CONDITIONS（受限工程设计）**，四项均 **CLOSED_DESIGN**，无新增阻断技术设计。原25/70、新25/209及6组2349设计模型独立通过，均不是P5产品测试。本轮仅接收归档/状态更新；用户仍须明确接受C-P5-001及P5-D01–D10（含C-P5-002–004）经济/统计口径，再单独授权P5实施，当前 **NOT AUTHORIZED / NOT STARTED**。原报告、失败及旧轮OPEN/BLOCKED保留历史；现状见 `docs/audits/phase-5/g1-5262032/DEVELOPER_RESPONSE.md`。12份已审设计身份文件不改，归档提交与已审526版本分别标识；main/标签保持P4基线，真实隔离WI-R2-001/002继续 **DEFERRED / NOT VERIFIED**，正式Test/金融批准/完整旧宿主边界不变，无部署/实盘/合并/标签/P6。

以下既有状态按原轮次保留，由上述新独立处置更新当前状态；不改写原审计结论。


当前G1：原固定5c9721f为PLAN BLOCKED，四项OPEN；本轮仅设计修订，待新完整40位SHA独立复核。PR #8描述AQRP_FIXED_REVIEW_SHA为唯一审查锁，不审漂移HEAD。不能把本文件的完成度或开发参考PASS当作独立PLAN PASS。

先读g1-5c9721f/received/REPORT.md、DEVELOPER_HANDOFF、FINDINGS、接收RECEIVED及DEVELOPER_RESPONSE，再读本轮EVENT_TRANSACTION_ADDENDUM / CASH_BUCKETS_AND_PROJECTION / EXECUTION_PRICE_AND_FEES / FIFO_ATTRIBUTION / CONTRACT_CHANGE_IMPACT，随后核对已同步的INTERFACE_DRAFT/MATH_CONTRACT/PROFILE_AND_DECISIONS及原需求追踪。

要求主审逐项：
1. 独立验证外层信封key与内部80/90、commit_seq/child_seq、最新pre/post状态捕获、A/B同刻风险、容量、取消65/借费95/估值100、真实恢复要求。C-P5-001是待用户接受的冻结契约细化提案，原P0文件保持不变，不能写成已获批准。
2. 独立重建C_set/U_free/U_short/S_set互斥桶、min-fee short开仓/交收前后A899、partial cover/跨零/红利结算，正确区分真实A与P4额外预算保守量H，不额外发明prefunding或把全部short标Unsupported。
3. 所有side/type价格域及有效fee上界，raw与实际价都检查，累计paid+所有余单H≤F，partial最低费、预算耗尽、取消释放；有利sell gap也不得超U成交。
4. 唯一FIFO closed-fragment计数；entry/exit费用与逐时点borrow/long红利/short应付的历史lot归属/未平pool/跨零，精确分摊不二次舍入，pay不重计；零利润与undefined原因。
5. 原25/70正确输入/expected/checker逐字节不变；补充25组209个设计参考断言是开发方执行而非独立核对，请另写参考或扩展反例；预定trace不是产品崩溃恢复通过。
6. 12原需求（10MVP/2CR）不丢项，不以代码模型/当前P4回归冒充P5产品能力；所有依赖、完整SDK/原回归/双OS原ZIP/失败证据要求仍有效。主审收尾若head变动应按指定SHA报告，不把旧结论外推到新提交。

原固定5c及bd/1ab的历史包/锁与原BLOCKED报告保持原字节，本轮包是另一个设计候选。P5实现仍需G1闭环及用户接受C-P5-001/经济候选后的明确授权。四项暂OPEN_PENDING_RECHECK，不合并/标签/部署/正式Test/金融批准/P6。真实Windows R2两项DEFERRED/NOT VERIFIED，最终集成SHA实际验证另行授权，R3代码已关闭但未集成到P4。

实际开发方命令/环境/算术输出/冻结检查见g1-5c9721f/developer-validation/。完整旧独立包留外部并以RECEIVED中的原hash绑定；Git是明确的文本子集，不冒称完整原ZIP。

## 一并保留的既有静态回归修复

本轮首次P4静态冻结检查因docs/REVIEW_PROTOCOL.md失败；该文件在此前1ab819a延期记录提交中被加了提示，已存在于bd18d1b。现恢复为已发布32ea基线原字节，不改检查/期望hash；延期原话与义务仍完整保留于AGENTS及windows-isolation-deferral专项记录。首次失败原命令/stdout/stderr和处置在developer-validation/PREEXISTING_REGRESSION_DISPOSITION.json；仅重新执行受影响检查，通过3440冻结文件核对，没有重复已通过的算术或改写失败。此恢复是文档一致性修复，需随新固定SHA复核，不改变main/旧标签。
