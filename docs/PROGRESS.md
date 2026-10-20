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
- 最新增量原报告Rev 2：`audits/phase-0/gemini/aqrp_phase0_incremental_audit_report_rev2.md`，SHA-256为e604da87cbedbbeac068f3f7e4acb99dd034c6f9699ad81f9a4f64a3a6b8e83b；配套勘误表aqrp_phase0_requirements_taxonomy_errata.md的SHA-256为c05416efe31b205dc8e567800f2cedae5cc04498959fac542c85938f63c272a0。旧Rev 1及其核对记录保留，最新事实核对见REV2_RECONCILIATION与REV2_EVIDENCE_INDEX。
- Rev 2已纠正12→16组、撤销FREG/VAL/BACK等非正式前缀；工具路径、数值职责、Pearson精度及Finding阶段归属主要澄清已登记。附录16行业务能力分类并非CSV的16个正式前缀，EXP-001至004实际均为P3而非附录P5–7，SignalBatch示意字段也非实际契约字段；勘误仍部分闭环。正式前缀/数量/阶段见REQUIREMENTS_TAXONOMY_VERIFICATION；Gemini就绪YES建议不等于用户批准。
- 开发方自查：只允许文档结构/追踪/依赖/案例算式核查，实际结果见 `audits/phase-0/SELF_CHECK.json`，不等同独立语义审核。
- 用户仅授权空main初始化与创建Phase0设计PR，明确不是验收通过。Phase0正式验收、设计合并/发布及Phase1授权均未获得。
- Phase0发布门禁：最新审计建议=PASS WITH CONDITIONS（仅d4c8218，非无条件PASS）；勘误=部分闭环；ACCEPTED=未批准；RELEASED=否；phase0-baseline标签=不存在。
- **PHASE 1 STATUS = BLOCKED**。正式发布及核实main/标签之前不得从草稿分支启动P1，即使发布也仍需P1明确授权。

## 本次交付范围

12份要求文档、统一数据/事件账本/研究/环境安全契约、编号需求和CSV/双向追踪、Golden设计、六项专项审计、架构评审自查、Gemini与ReviewPackage模板、实际文件清单及核查日志。tests下仅目录说明，没有业务测试或功能。所有设计细节与验收数值是待审基线。

## 继续工作的门槛

已收到Rev 2与勘误表，两项旧计数/前缀错误已纠正；仍需Gemini区分能力视图与正式前缀并校正EXP阶段等说明。最终审批范围须覆盖明确版本及后续管理资料差异。用户Phase0验收及合并/发布授权尚未获得，本次明确不执行发布。获授权后才可核实最终main/标签/文件及Gemini主干闭环，达到RELEASED后P1仍需独立授权。当前停止在Phase0。
