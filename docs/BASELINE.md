# Phase 0 main 基线登记与发布门禁

**用户验收：ACCEPTED。PR #1：已合并。最终主干独立核验：待Gemini完成。PHASE 1 STATUS = BLOCKED。**

日期2026-10-20（Asia/Shanghai）。GOV-010及Main Baseline Release Gate继续适用。本文件登记已发生的合并及本次标签绑定规则，不以文档文字代替实际Git推送或Gemini复核。

## 版本与证据

| 项目 | 登记内容 |
|---|---|
| 仓库 / 默认分支 | https://github.com/wwooyy429/Alpha-Quant-Research-Platform-AQRP- / main |
| 用户验收与授权 | 用户明确“验收已通过，可以将PR #1 合并入 main 并打上标签”；逐字原话及版本绑定见audits/phase-0/publication/APPROVAL.json |
| 获批PR固定head | 228190a0c46595cf2927125fdc7d4f1c51b39ccf；原话未列SHA，此值为授权时核实的PR版本 |
| 最新Gemini已审SHA | 1830b152ea4b2497fbfc54d4d506a77e3c2abb5f；最终报告设计PASS、人工验收就绪READY |
| 最终报告原文/hash | audits/phase-0/gemini/aqrp_phase0_final_audit_and_acceptance_report.md；1300075acf2a30b34c4053ae256315bdaae1604eb62b26b145e81bf3179556fc |
| 原设计/增量审查 | ed6666985bfac8cc94fa302c72e2e6333c679a6f / d4c8218315a9152166cbe56fde54384dc99fb094；历次原件保留 |
| 合并前main | e87d0082a5e448e9550129a486ba965f13a155f8，原空初始化；现为历史版本 |
| PR #1合并提交 | 8c37e952be61054c6c72b5aaf573026c0355647b；merge保留历史；两个父提交与内容树均已核对 |
| 合并内容一致性 | 合并提交tree与获批228190a完全一致，无额外业务差异 |
| 后续发布登记 | 本提交仅补充批准/基线/进度/审查与自查证据，不改变获批需求、架构或业务契约；完整diff由Git及PR发布回执关联 |
| 基线标签名 | phase0-baseline；绑定包含本登记文件的最终main提交，不绑定较早的空初始化或仅设计草稿 |
| 标签目标完整SHA | 通过Git解析phase0-baseline^{commit}并与远端main核对；实际发布结果及完整SHA在PR #1发布回执记录，避免文件自引用SHA占位符 |
| 正式RELEASED | 待标签/main实际核对及Gemini最终主干链路复核；当前不冒充该独立复核已完成 |
| Phase1 | BLOCKED，尚无Phase1明确启动授权 |

## 实际核查与文件版本

- 合并前：65个清单文件hash一致；已提交17项文档自查通过。GitHub无status及PR workflow runs，CI按ENV-002留P1，不能称CI通过。
- 合并后8c37e95：重跑文档自查17通过/0失败，完整证据为audits/phase-0/publication/MERGED_MAIN_SELF_CHECK.json和MERGED_MAIN_COMMAND_LOG.txt。
- 本发布登记提交：当前SELF_CHECK.json、COMMAND_LOG.txt与MANIFEST.json记录适用自查及逐文件版本/hash；清单不包含自身hash，不代替Git Commit身份。
- 获批需求106条/16组；CSV hash为20dd4e6be7188d3121f3cb361faf8901bc91815a6e9752beb14054a12183f0c1。ARCHITECTURE、INTERFACES、DATA_CONTRACT、BACKTEST_CONTRACT、RESEARCH_PROTOCOL、GOLDEN_DATASET等核心内容保持获批版本。
- 用户批准范围的完整66文件快照可从获批228190a及其MANIFEST核验；最终main新增/修改仅为授权发布记录和自查证据，逐文件最终版本见当前MANIFEST及Git diff。
- 实际合并回执、父提交、范围核对见audits/phase-0/publication/MERGE_VERIFICATION.json；标签推送后的实际远端核对回执保存在PR #1。

## 尚需完成的独立门禁

F-001的获批、合并、main内容与标签步骤分别登记；Gemini最终main/标签/审计/批准/文件链路核验尚未执行，当前不自行将其标为CLOSED。最终独立核验通过后才能登记完整RELEASED；即使RELEASED也须等待用户另行授权Phase1，并从核实main建立独立分支。

F-004物理云同步隔离仍未验证；原始执行日志未附等已披露证据边界继续保留，用户验收不被解释为已实现这些措施或逐项风险豁免。CI、timestamp验证、业务代码/测试仍按原定阶段实施；比赛profile、依赖精确版本、研究阈值等未来阶段前置事项不因本次验收自动确定。

本次完成授权的合并、标签发布及必要记录维护后停止，不进入Phase1。
