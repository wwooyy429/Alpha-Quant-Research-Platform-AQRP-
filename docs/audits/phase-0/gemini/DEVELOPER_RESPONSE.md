# Gemini Phase 0 报告接收与开发方处理意见

日期：2026-10-20（Asia/Shanghai）。本文件由开发方编写；不修改、不代替Gemini原报告，不自行关闭其问题。

## 原报告与版本绑定

用户确认来源为Gemini，并提供外部原文件 `aqrp_phase0_audit_report.md`；已逐字节复制到本目录同名文件。SHA-256：`8c04ebb122f33853ef2ae4c59c79e32e941c6f34e168e564f6f8d3ed14762662`。保留原链接、排版、编号、命令及结论，包括其可能的笔误，不在原文上纠正。

报告明确列出base `e87d0082a5e448e9550129a486ba965f13a155f8` 和head `ed6666985bfac8cc94fa302c72e2e6333c679a6f`，与本轮固定设计目标及初始化main一致。原始报告已取得，先前“仅摘要/审查SHA关联待补”的状态已被本文件及EVIDENCE_INDEX取代。

正式总体结论：**PASS WITH CONDITIONS**；设计子结论PASS；Phase1启动建议BLOCKED。不是无条件PASS，不等于用户ACCEPTED或main RELEASED。Gemini所述沙箱运行按“审计方报告已执行”登记；未随文件提供独立脚本、原始输出及SciPy/Pandas/PyArrow精确版本，不能声称开发方复跑了相同环境或核实了原始运行日志。

本次提交只归档报告、登记Finding和更新状态/证据工具；不更改106项设计需求、业务接口、数据/回测/研究契约，不开发P1，不修改main或标签。新证据提交不自动继承原设计SHA的审计结论；合并前需核对管理资料差异，最终main核验按原报告条件执行。

## Findings 处理表

保留原严重度与原状态。下表是开发方拟处理/落实位置，不是Gemini关闭结论。

| Finding | 开发方核对与处置 | 执行阶段 / 状态 / 阻断范围 |
|---|---|---|
| F-001 High / GOV-010 | main仍为空初始化、PR Draft且未合并、无phase0-baseline；保持发布门禁。等待用户明确验收及合并/发布授权，再按批准范围核对最终main/标签/文件/原审计；报告另要求Gemini完成合并后主干复核 | OPEN / GATED；阻断稳定发布闭环与P1启动；当前不申请无条件通过，不擅自关闭或降级 |
| F-002 Medium | CI在正式需求ENV-002（V3.0§11.4）中明确属于P1；TESTING.md第3行及ENVIRONMENT_AND_SECURITY.md第11行已有相同计划。报告建议与阶段边界一致；列为P1获授权后的首项任务，业务逻辑合入前配置并实际运行CI | OPEN / PLANNED FOR P1；不为关闭此项提前开发CI。报告列QA-001/ENV-001的映射需Gemini核对，不能当作P0遗漏已修复 |
| F-003 Medium | DATA_CONTRACT.md第10行已要求UTC带时区微秒timestamp、不接受无时区时间，session_date仅为本地交易日键。P1验证须拒绝把纯日期/naive datetime用于event_time/available_at/decision_time，覆盖盘前/收盘后关联、修订/晚到数据、源时区及夏令时；不得因日频把发布时间降为日期 | DOCUMENTED ADVISORY / P1 IMPLEMENTATION PLANNED；当前契约已有规则，业务验证尚未实现，不能称泄漏风险测试已通过 |
| F-004 Low | 现有.gitattributes的-text规则（禁用自动换行转换）用于保留原来源/证据hash，作者输出已明确UTF-8/LF；直接全局改为text=auto eol=lf可能归一化CRLF来源而使旧hash失效。建议后续采用“普通文本LF + 原始来源/证据显式例外”，先做逐文件字节/检出验证；同步客户端冲突需另设工作区隔离方案，eol规则本身不能隔离云同步 | 原报告为MITIGATED BY DEVELOPER；本次登记建议，保留配置不变；不把附件中的建议当作新增阶段授权，不自行标VERIFIED_CLOSED |

## 需Gemini校正或补充的报告细节

1. B节需求编号并非仓库实际编号：ARCH实际001–003，DATA001–013，FACTOR001–012，RESEARCH001–009，PORT001–004，BT001–010，UI001–008，GOV001–010，QA001–007；还有RISK、VALID、EXP、ENV、SEC、INT、EXT等需求组。报告中的FACT/RES/BACK及ARCH001–008/PORT001–008等应按正式CSV核对。总数106正确，但“全部覆盖”的证据不能仅用错误编号范围支持。V3.0的66是编号小节数，不是正式需求条数。
2. E节与F-002使用的 `docs/tools/check_documents.py` / `docs/tools/build_catalog.py` 不存在；实际路径为 `docs/audits/phase-0/tools/check_documents.py` 和 `docs/audits/phase-0/tools/build_catalog.py`。本地运行证据见原COMMAND_LOG及原设计SHA中的SELF_CHECK，报告需分别标明开发者运行与Gemini独立执行。
3. D节Pearson以约0.893685和±1e-4核对，只支持所报显示精度。项目GOLDEN_DATASET中原文近似值容差为1e-8，高精度公式候选为1e-12。未提供未舍入结果/脚本前，不把报告的较宽容差等同于全部Golden精度要求已验证，也不降低项目容差；边界/性质/更多资金情景仍在其适用阶段实施。
4. C节“standardized signals”应澄清是结构标准化还是数值标准化：正式Factor API输出原始SignalBatch，数值标准化及各处理stage属于P3 Research，不应把职责移回插件；事件摘要未列Match/Valuation，不取代完整BACKTEST_CONTRACT时序。
5. 原报告Repository/PR链接实际指向Google搜索，E表格也缺Markdown分隔行。正确审查对象是用户给定GitHub PR#1和上述完整SHA；仅在索引提供直接链接，原报告保留原状。

这些是对报告可追溯性的开发方反馈，不是擅自修改审计意见。需Gemini确认勘误/澄清；未获人工批准，不合并、不打稳定标签、不进入Phase1。
