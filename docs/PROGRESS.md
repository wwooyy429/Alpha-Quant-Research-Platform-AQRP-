# 当前真实项目状态

日期：2026-10-20（Asia/Shanghai）。本文件不授予权限。

- 当前授权：仅 Phase 0，需求审计与架构设计；V3.0/V3.1/V3.2合并。
- 当前阶段状态：REVIEW REQUIRED（设计提案供Gemini预审）。
- 当前稳定版本：无。尚未创建已批准main、发布标签或已验收业务版本。
- 上一阶段：无；Phase 0尚未获人工验收。
- 功能实现：数据、Registry、研究、组合、风险、回测、网页全部Planned；高级研究Deferred；真实执行Unsupported。
- 当前本地分支：feature/phase-0-v3.2-design；精确Git状态及同步结果见审查资料包/实际命令记录，不能据分支名推定固定SHA。
- 仓库：用户提供的GitHub地址已克隆，初始为空。尚无稳定基线及PR，远端交付状态以证据为准。
- Gemini计划预审：NOT VERIFIED（未收到）。Gemini固定SHA审查：NOT VERIFIED（未发生）。
- 开发方自查：只允许文档结构/追踪/依赖/案例算式核查，实际结果见 `audits/phase-0/SELF_CHECK.json`，不等同独立语义审核。
- 人工验收/合并/发布/下一阶段授权：均未获得。

## 本次交付范围

12份要求文档、统一数据/事件账本/研究/环境安全契约、编号需求和CSV/双向追踪、Golden设计、六项专项审计、架构评审自查、Gemini与ReviewPackage模板、实际文件清单及核查日志。tests下仅目录说明，没有业务测试或功能。所有设计细节与验收数值是待审基线。

## 继续工作的门槛

先解决DECISIONS中的Gemini访问及空仓库PR基线，提交固定SHA可核实资料；Gemini完成计划/架构审查、关键待决事项/阻断项闭环后才具备Phase0人工验收申请条件。用户明确验收不自动授权Phase1；当前必须停止在Phase0。
