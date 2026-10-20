# 当前真实项目状态

日期：2026-10-20（Asia/Shanghai）。本文件不授予权限。

- 当前授权：仅 Phase 0，需求审计与架构设计；V3.0/V3.1/V3.2合并。
- 当前阶段状态：REVIEW REQUIRED（设计提案供Gemini预审）。
- 当前稳定版本：无。main已存在但只含授权的空初始化提交 `e87d0082a5e448e9550129a486ba965f13a155f8`；无已批准Phase0内容/稳定标签，不算RELEASED。
- 上一阶段：无；Phase 0尚未获人工验收。
- 功能实现：数据、Registry、研究、组合、风险、回测、网页全部Planned；高级研究Deferred；真实执行Unsupported。
- 当前本地分支：feature/phase-0-v3.2-design；精确Git状态及同步结果见审查资料包/实际命令记录，不能据分支名推定固定SHA。
- 仓库：默认分支已设为main；Phase0设计草稿PR为 <https://github.com/wwooyy429/Alpha-Quant-Research-Platform-AQRP-/pull/1>，未合并。当前固定待审SHA以PR描述 `AQRP_FIXED_REVIEW_SHA` 为准，历史锚点不替代当前审查目标。
- Gemini计划预审：NOT VERIFIED（未收到）。Gemini固定SHA审查：NOT VERIFIED（未发生）。
- 开发方自查：只允许文档结构/追踪/依赖/案例算式核查，实际结果见 `audits/phase-0/SELF_CHECK.json`，不等同独立语义审核。
- 用户仅授权空main初始化与创建Phase0设计PR，明确不是验收通过。Phase0正式验收、设计合并/发布及Phase1授权均未获得。
- Phase0发布门禁：AUDIT PASSED=NOT VERIFIED；ACCEPTED=未批准；RELEASED=否；phase0-baseline标签=不存在。
- **PHASE 1 STATUS = BLOCKED**。正式发布及核实main/标签之前不得从草稿分支启动P1，即使发布也仍需P1明确授权。

## 本次交付范围

12份要求文档、统一数据/事件账本/研究/环境安全契约、编号需求和CSV/双向追踪、Golden设计、六项专项审计、架构评审自查、Gemini与ReviewPackage模板、实际文件清单及核查日志。tests下仅目录说明，没有业务测试或功能。所有设计细节与验收数值是待审基线。

## 继续工作的门槛

初始化main与PR前提已落实，仍需Gemini完成固定SHA计划/架构审查、关键待决事项/阻断项闭环及用户Phase0明确验收。随后仅凭合并/发布授权更新main、核实最终内容并建立phase0-baseline/BASELINE发布证据后才可标RELEASED；Phase1仍需单独授权。当前停止在Phase0。
