# Phase 0 main 基线登记与发布门禁

**发布状态：NOT RELEASED。PHASE 1 STATUS = BLOCKED。**

日期2026-10-20（Asia/Shanghai）。需求GOV-010；来源 `docs/sources/AQRP_V3.2_BASELINE_GATE.md`。本文件是事实登记及待发布清单，不是发布证书。

## 已核实的仓库事实

| 项目 | 当前状态 |
|---|---|
| 仓库 | https://github.com/wwooyy429/Alpha-Quant-Research-Platform-AQRP- |
| main | 存在，空初始化基线；完整SHA `e87d0082a5e448e9550129a486ba965f13a155f8` |
| main tree | `4b825dc642cb6eb9a060e54bf8d69288fbee4904`，文件列表为空 |
| 默认分支 | main（已设置并须以GitHub再核实记录为准） |
| 开发分支 | feature/phase-0-v3.2-design，保留0b64148→04deecc→65ae3d3原始历史，6554dfe将空main接入共同祖先 |
| 设计PR | https://github.com/wwooyy429/Alpha-Quant-Research-Platform-AQRP-/pull/1，Draft、Open、未合并 |
| 固定设计审查SHA | `ed6666985bfac8cc94fa302c72e2e6333c679a6f`，与Gemini报告及PR字段一致；后来证据/状态提交不自动归入已审范围 |
| 最新增量复核SHA | `d4c8218315a9152166cbe56fde54384dc99fb094`；原报告与新增增量报告分别明确绑定两个版本，当前归档/记录更新不自动计入d4已审范围 |
| Gemini原设计审查报告 | 原报告明确head为ed6666985bfac8cc94fa302c72e2e6333c679a6f、base为e87d008…；原文保存在 `audits/phase-0/gemini/aqrp_phase0_audit_report.md`，SHA-256为8c04ebb122f33853ef2ae4c59c79e32e941c6f34e168e564f6f8d3ed14762662 |
| 审计建议及条件 | 总体PASS WITH CONDITIONS、设计子结论PASS；F-001 High仍OPEN/GATED，P1 BLOCKED。报告所述沙箱执行按审计方陈述登记，原脚本/原始日志未附，不称开发方已复跑 |
| 增量复核及闭环差异 | 新原报告在同目录aqrp_phase0_incremental_audit_report.md，hash为57a9d7025230ba2924093be4511254a233613548d0271a39324b1c5e2f5fd140；Gemini给人工验收就绪YES，但实际16组与报告“12组”及非正式前缀仍有冲突，开发方判断部分闭环。详见INCREMENTAL_RECONCILIATION，不改审计原文 |
| 用户正式批准Phase0 | 未批准；初始化/建PR授权不是ACCEPTED |
| main中的已批准Phase0文件 | 无；尚无已批准设计内容 |
| phase0-baseline标签 | 不存在，当前不创建 |
| 稳定发布SHA/版本 | 无；RELEASED = 否 |
| Phase1启动条件 | 不满足；即使后续RELEASED仍需另获P1明确启动授权 |

## 已有用户授权的精确范围

用户原文：

> 我授权你建立仓库初始化所需的 main 基线，并创建 Phase 0 设计 PR；这不代表 Phase 0 验收通过。完成后给我一份可直接交给 Gemini 的审查指令，包含仓库地址、固定 SHA 和审查资料位置，不要进入 Phase 1。

用户随后Main Baseline Release Gate再次明确：未正式批准不得自行发布；审查通过不等于发布；Phase1仅可在P0 RELEASED且main基线可验证之后启动。当前授权只支持空main、默认分支设置、待审PR及门禁文档；不支持合入设计、打稳定标签、发布或P1开发。

## 正式发布前必须填齐并核实

1. 原及增量Gemini报告均已取得，分别绑定ed666698与d4c8218。主要技术澄清已有，但分组/编号勘误仍未完全符合CSV，应另补勘误，不能改正确设计迎合报告。人工验收就绪YES是审计方建议，用户未批准；旧SHA不覆盖新管理资料。最终main主干核验仍未执行。
2. 用户明确批准Phase0的原文/可信记录、日期、范围、精确SHA、条件；另记录合并/发布授权。
3. 已批准需求/架构版本及逐文件路径和hash：至少AGENTS、PROJECT_CHARTER、REQUIREMENTS/CSV、TRACEABILITY、ARCHITECTURE、INTERFACES、DATA_CONTRACT、BACKTEST_CONTRACT、RESEARCH_PROTOCOL、ROADMAP、ACCEPTANCE、TESTING、DECISIONS、环境安全与Golden设计、审计/证据/进度文件。当前批准清单为空。
4. PR最终head/base、已核对diff、适用文档/配置检查命令和结果；所有批准范围外变化必须重新批准。
5. 按授权合并后的main完整SHA及tree；若生成新合并SHA，核对最终内容/批准范围并重新执行受影响检查，必要时Gemini对新SHA复核。不是仅复用合并前测试数字。
6. 只有上述条件齐全才创建 `phase0-baseline` 标签并验证其解析Commit与发布时main一致；标签/推送实际成功后才填写发布记录。不移动/覆盖既有稳定标签掩盖错误。
7. 更新本文件、PROGRESS与CHANGELOG，并核对实际main文件/证据与清单。当前不填写不存在的批准人、报告、版本或标签。

正式发布后本文件应登记发布main SHA、标签名、已批准文件版本/清单、Gemini及用户原始证据；发布提交自身SHA通过Git标签/PR发布记录关联，避免把自引用占位符当可核验值。

## 已验证文件与证据位置

- main文件列表：空；见 `audits/phase-0/RELEASE_GATE_AUDIT.json` 的实际Git命令结果。
- 开发分支待审文件：`audits/phase-0/MANIFEST.json`（当前内容快照逐文件hash，不代表批准）。
- 开发方文档自查：SELF_CHECK.json、COMMAND_LOG.txt；没有业务测试/CI/Gemini通过声明。
- 审查资料包：`audits/phase-0/REVIEW_PACKAGE.md`；Gemini原报告及索引：`audits/phase-0/gemini/`。原文保持不变，开发方意见另文件记录，不冒充审计方结论。

不得以空main、草稿PR、17项自查或未来拟建标签代替Phase0稳定发布。
