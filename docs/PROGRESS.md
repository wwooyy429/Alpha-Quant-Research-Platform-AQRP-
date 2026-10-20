# 当前真实项目状态

日期：2026-10-20（Asia/Shanghai）。本文件不授予权限。

- 当前授权：仅 Phase 0，需求审计与架构设计；V3.0/V3.1/V3.2合并。
- 当前阶段状态：REVIEW REQUIRED（Gemini已对d4c8218增量版本给出PASS WITH CONDITIONS、人工验收就绪YES建议；开发方核对仍有需求编号勘误未闭环，尚未获用户验收或发布）。
- 当前稳定版本：无。main已存在但只含授权的空初始化提交 `e87d0082a5e448e9550129a486ba965f13a155f8`；无已批准Phase0内容/稳定标签，不算RELEASED。
- 上一阶段：无；Phase 0尚未获人工验收。
- 功能实现：数据、Registry、研究、组合、风险、回测、网页全部Planned；高级研究Deferred；真实执行Unsupported。
- 当前本地分支：feature/phase-0-v3.2-design；精确Git状态及同步结果见审查资料包/实际命令记录，不能据分支名推定固定SHA。
- 仓库：默认分支main；PR#1未合并。最新已复核SHA为 `d4c8218315a9152166cbe56fde54384dc99fb094`，原设计SHA为 `ed6666985bfac8cc94fa302c72e2e6333c679a6f`；PR字段与原/增量报告分别关联。随后归档本次报告和更新状态的新提交不自动继承已审d4结论。
- Gemini原报告已收到：`audits/phase-0/gemini/aqrp_phase0_audit_report.md`；总体PASS WITH CONDITIONS，设计子结论PASS，P1建议BLOCKED。base/head与报告一致，来源文件字节hash核对通过；本次不重新声称运行了Gemini沙箱或验证了未附原始日志。
- Finding F-001 High仍OPEN/GATED；F-002 CI列P1首项；F-003为P1时间验证建议；F-004保留缓解状态并登记配置建议。编号/脚本路径/容差等报告澄清见同目录DEVELOPER_RESPONSE；GPT不改原文、不自行关闭Gemini问题。
- 最新增量原报告：`audits/phase-0/gemini/aqrp_phase0_incremental_audit_report.md`，SHA-256为57a9d7025230ba2924093be4511254a233613548d0271a39324b1c5e2f5fd140；闭环事实核对见INCREMENTAL_RECONCILIATION，来源和数学/CSV核对值见INCREMENTAL_EVIDENCE_INDEX。
- 增量核对：工具路径、数值处理职责、Pearson精度及Finding阶段归属已基本澄清；报告仍把实际16组写成12组并使用FREG/VAL/BACK等非正式前缀，SignalBatch示意字段也非实际契约字段，不能登记“报告勘误全部完成”。Gemini的人工验收就绪YES建议与开发方部分闭环判断分别保留。
- 开发方自查：只允许文档结构/追踪/依赖/案例算式核查，实际结果见 `audits/phase-0/SELF_CHECK.json`，不等同独立语义审核。
- 用户仅授权空main初始化与创建Phase0设计PR，明确不是验收通过。Phase0正式验收、设计合并/发布及Phase1授权均未获得。
- Phase0发布门禁：最新审计建议=PASS WITH CONDITIONS（仅d4c8218，非无条件PASS）；勘误=部分闭环；ACCEPTED=未批准；RELEASED=否；phase0-baseline标签=不存在。
- **PHASE 1 STATUS = BLOCKED**。正式发布及核实main/标签之前不得从草稿分支启动P1，即使发布也仍需P1明确授权。

## 本次交付范围

12份要求文档、统一数据/事件账本/研究/环境安全契约、编号需求和CSV/双向追踪、Golden设计、六项专项审计、架构评审自查、Gemini与ReviewPackage模板、实际文件清单及核查日志。tests下仅目录说明，没有业务测试或功能。所有设计细节与验收数值是待审基线。

## 继续工作的门槛

已收到增量复核，但需求分组勘误仍需Gemini校正；最终审批范围应覆盖明确版本及管理资料差异。用户Phase0验收及合并/发布授权尚未获得，本次明确不执行发布。获授权后才可核实最终main/标签/文件及Gemini主干闭环，达到RELEASED后P1仍需独立授权。当前停止在Phase0。
