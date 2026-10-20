# 当前真实项目状态

日期：2026-10-20（Asia/Shanghai）。本文件不授予权限。

- 当前授权：仅 Phase 0，需求审计与架构设计；V3.0/V3.1/V3.2合并。
- 当前阶段状态：REVIEW REQUIRED（Gemini最终报告对1830b15给设计PASS、人工验收就绪READY建议；核心分类/阶段/接口勘误已闭环，物理隔离等事实证据仍有限定；用户尚未验收或授权发布）。
- 当前稳定版本：无。main已存在但只含授权的空初始化提交 `e87d0082a5e448e9550129a486ba965f13a155f8`；无已批准Phase0内容/稳定标签，不算RELEASED。
- 上一阶段：无；Phase 0尚未获人工验收。
- 功能实现：数据、Registry、研究、组合、风险、回测、网页全部Planned；高级研究Deferred；真实执行Unsupported。
- 当前本地分支：feature/phase-0-v3.2-design；精确Git状态及同步结果见审查资料包/实际命令记录，不能据分支名推定固定SHA。
- 仓库：默认分支main；PR#1未合并。最新已复核SHA为 `1830b152ea4b2497fbfc54d4d506a77e3c2abb5f`，历史增量d4c8218与原设计ed666698分别保留；PR区分最终已审版本与后续证据头。本次归档/管理更新不自动继承1830b15结论。
- Gemini原报告已收到：`audits/phase-0/gemini/aqrp_phase0_audit_report.md`；总体PASS WITH CONDITIONS，设计子结论PASS，P1建议BLOCKED。base/head与报告一致，来源文件字节hash核对通过；本次不重新声称运行了Gemini沙箱或验证了未附原始日志。
- Finding F-001 High仍OPEN/GATED；F-002 CI列P1首项；F-003为P1时间验证建议；F-004保留缓解状态并登记配置建议。编号/脚本路径/容差等报告澄清见同目录DEVELOPER_RESPONSE；GPT不改原文、不自行关闭Gemini问题。
- 最新原报告：`audits/phase-0/gemini/aqrp_phase0_final_audit_and_acceptance_report.md`，SHA-256为1300075acf2a30b34c4053ae256315bdaae1604eb62b26b145e81bf3179556fc；最新事实核对与证据索引为FINAL_RECONCILIATION及FINAL_EVIDENCE_INDEX。原报告、Rev 1/2、旧勘误表和旧开发方意见均保留。
- 最终核对：16组/106条及全部阶段映射与CSV一致，EXP首次P3、能力视图与编号分组、SignalBatch真实字段、RESEARCH/VALID及分数权已明确，核心勘误闭环。报告F-004称物理隔离但当前仍在百度同步目录，缺少隔离完成证据；浮点零误差/执行日志/部分Finding引用仍需限定。不能登记所有报告事实已验证。原字节及开发方分类建议稿另存证；详见FINAL_RECONCILIATION。
- 开发方自查：只允许文档结构/追踪/依赖/案例算式核查，实际结果见 `audits/phase-0/SELF_CHECK.json`，不等同独立语义审核。
- 用户仅授权空main初始化与创建Phase0设计PR，明确不是验收通过。Phase0正式验收、设计合并/发布及Phase1授权均未获得。
- Phase0发布门禁：最新设计审计建议=PASS（仅1830b15），人工验收就绪=READY（Gemini建议）；核心勘误=闭环，全部环境/执行事实=未全部验证；ACCEPTED=未批准；RELEASED=否；phase0-baseline标签=不存在。
- **PHASE 1 STATUS = BLOCKED**。正式发布及核实main/标签之前不得从草稿分支启动P1，即使发布也仍需P1明确授权。

## 本次交付范围

12份要求文档、统一数据/事件账本/研究/环境安全契约、编号需求和CSV/双向追踪、Golden设计、六项专项审计、架构评审自查、Gemini与ReviewPackage模板、实际文件清单及核查日志。tests下仅目录说明，没有业务测试或功能。所有设计细节与验收数值是待审基线。

## 继续工作的门槛

最终报告已确认核心设计勘误；不再把EXP/字段/正式分组列为未纠正。物理隔离陈述缺乏实际证据，应澄清或验证，不以报告自述替代事实。最终审批仍须明确版本、范围及后续管理资料差异；用户验收与合并/发布授权未获得，本次不执行发布。未来按授权核实main/标签/文件、合并后适用检查及Gemini主干链路，达到RELEASED后P1仍需独立授权。当前停止在Phase0。
