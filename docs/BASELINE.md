# Phase 0 已发布main基线与门禁闭环登记

**AUDIT：PASS。ACCEPTED：YES。Phase0：RELEASED。F-001：RESOLVED / CLOSED。**

日期2026-10-20（Asia/Shanghai）。Gemini已对固定发布基线完成Baseline Verification Gate；本文件将历史待核验状态更新为实际闭环结论。

## 固定基线与追溯链

| 项目 | 已核实版本 / 证据 |
|---|---|
| 仓库 / 默认分支 | https://github.com/wwooyy429/Alpha-Quant-Research-Platform-AQRP- / main |
| 用户验收与合并/标签授权 | audits/phase-0/publication/APPROVAL.json，保留用户原话、日期、范围及开发方SHA绑定依据 |
| 获批PR#1 head | 228190a0c46595cf2927125fdc7d4f1c51b39ccf；用户原话指名PR，未逐字列SHA |
| PR#1实际merge | 8c37e952be61054c6c72b5aaf573026c0355647b；保留历史，tree与获批head一致 |
| 已发布基线完整Commit | **7de1d0e81385ae97f98ea673fe05dd726f0b577b** |
| 稳定标签 | **phase0-baseline** |
| 附注标签对象 | 0b2230cd4861ca3b47fa30fc30dae9f4dc4109d0；剥离后Commit为7de1d0e81385ae97f98ea673fe05dd726f0b577b |
| 基线tree | bf19580b68e42f1aca8a838b94795adcef574ca6 |
| 独立Gate结论 | Gemini：PASS；Phase0 RELEASED；F-001 RESOLVED / CLOSED |
| Gate原报告 | audits/phase-0/gemini/aqrp_phase0_baseline_verification_gate_report.md |
| Gate原报告SHA-256 | aa9761ef9ef20a5645d22297ab2ef9ee18455521c912226a2e342c1ff65129b1 |
| Gate来源、版本与只读观察 | audits/phase-0/gemini/GATE_EVIDENCE_INDEX.json |
| 此前最终设计审查 | 1830b152ea4b2497fbfc54d4d506a77e3c2abb5f；原报告hash1300075acf2a30b34c4053ae256315bdaae1604eb62b26b145e81bf3179556fc |
| 历史设计/增量审查 | ed6666985bfac8cc94fa302c72e2e6333c679a6f / d4c8218315a9152166cbe56fde54384dc99fb094；所有原件保留 |
| 原空初始化 | e87d0082a5e448e9550129a486ba965f13a155f8，仅历史，不是发布基线 |

## 发布版本与后续归档的区别

Gate报告描述的是核验时main与标签都指向7de1d0e的事实。本次在main追加报告/状态归档记录后，main head会前进；**发布基线及其标签仍固定为7de1d0e，不移动标签来让它追随最新main**。本次归档不改变获批需求、架构或核心契约；其差异和当前提交SHA通过Git与PR#1回执追溯，不冒充已获Gemini追加审计，也不产生一个替代基线。

后续阶段应从核实的main创建独立分支，并核对main相对该固定基线的已授权差异。若有真正的设计/业务变更，应走新的变更审查，而不是改动phase0-baseline掩盖版本变化。

## 文件版本与实际检查

- 固定发布基线包含70个项目文件，其MANIFEST登记69个文件hash（不自包含）。请读取7de1d0e提交中的MANIFEST核对该发布版本，不拿本次新归档清单替换历史快照。
- 当前MANIFEST、SELF_CHECK及COMMAND_LOG登记本次归档版本的文件/hash和文档检查；这不替代Git SHA、CI或独立审查。
- 获批需求为106条/16个正式前缀组；CSV hash为20dd4e6be7188d3121f3cb361faf8901bc91815a6e9752beb14054a12183f0c1。ARCHITECTURE、INTERFACES、DATA_CONTRACT、BACKTEST_CONTRACT、RESEARCH_PROTOCOL、GOLDEN_DATASET等核心内容与经审发布基线一致。
- 用户批准66文件快照、PR合并后的检查及发布登记证据分别见获批228190a版本、publication/MERGE_VERIFICATION.json、MERGED_MAIN_SELF_CHECK.json和MERGED_MAIN_COMMAND_LOG.txt。
- 原需求表中的Planned/Deferred/Unsupported描述业务实现状态；不因Phase0设计发布而将未来代码或测试标为已实现。历史审计索引的待验收/待复核标记按当时快照保留，当前状态以Gate报告及本登记为准。

## 后续状态与保留条件

**Phase1基线前置门禁：UNBLOCKED；用户现已明确启动授权；本阶段状态：PLAN REVIEW REQUIRED。**

本次用户已另行明确授权P1，批准先做合成数据及Python3.13.16，证据见audits/phase-1/AUTHORIZATION.json；已从核实main 502c693创建独立分支。Gemini门禁报告仍只覆盖固定P0基线；P1实施须先完成自己的计划预审，不以本次启动授权替代独立审查。

F-002 CI、F-003时间戳实现/测试留P1；F-004物理云同步隔离仍未验证。Gemini原始运行脚本/日志未附等已披露边界保留，Gate PASS不等于其他能力均已验证。当前门禁报告中的Google搜索仓库链接原样保留，直接GitHub地址和完整SHA由索引提供。
