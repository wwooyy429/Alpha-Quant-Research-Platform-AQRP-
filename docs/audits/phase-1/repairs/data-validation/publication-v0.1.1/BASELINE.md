# Phase 1 补丁版本 0.1.1 发布登记

用户已 ACCEPTED 固定修复 SHA `6858c183ab97e270c9b4852cf1885fb55873327c`，并明确授权合并 main、更新版本。PR #4 已合并为 `93b87b4ad5da5e737973ce8882e5dc9d0b656844`，双父及完整树相等检查通过。

本登记与新附注标签 `v0.1.1` 原子推送至远端 main、核对两者目标一致后，本补丁状态为 **RELEASED**。最终发布提交用 `git rev-parse 'v0.1.1^{}'` 解析，完整 SHA 另记 PR #4 发布回执，避免文件自包含自身提交号。原 `phase0-baseline` 和 `phase1-baseline` 的标签对象、目标均不移动。

| 记录 | 固定值 / 证据 |
|---|---|
| 仓库 / PR | https://github.com/wwooyy429/Alpha-Quant-Research-Platform-AQRP- / pull/4 |
| 上一 main / 0.1.0 基线 | f579b2c99e762085772de6e70ba1fa98792a7add |
| 用户批准的 PR head | 6858c183ab97e270c9b4852cf1885fb55873327c |
| 已合并 main | 93b87b4ad5da5e737973ce8882e5dc9d0b656844 |
| 业务修复锚点 | 8902ba00a818150bf00af8d051a3837bc79e6bfc |
| 指定代执行审查目标 | 31a548b8790bc1abe0f5ffbe3c55e10917a9503e |
| 合并后完整 SDK | aqrp-99477b13-9457-49fd-acb2-883650fb4fad，234 通过、0 失败/错误/跳过 |
| 两轮未编辑原始外置回归 | 16 通过、0 失败/错误/跳过；original16.log/xml、wheel-origin.json |
| 实际 Python / 包 | CPython 3.13.16；已安装 wheel 0.1.1，锁定依赖未改 |
| 合并前 Actions | 39626219071 / 39626210127，Windows、Ubuntu 成功；PREMERGE_CHECKS.json |
| 原始深度 ZIP 证据 | ../delegated-31a548b/；对应 run39620574953，未冒充新 main CI |
| 合并及人工批准 | MERGE_VERIFICATION.json、APPROVAL.json |
| 文件与环境标识 | BASELINE_FILES.json、sdk/environment.json、EVIDENCE_MANIFEST.json |

合并后 SDK 从干净 main 的 Git 归档构建真实 wheel，并从独立环境执行；Ruff、234 项测试、覆盖率门槛、独立数学参考、八表快照/查询冒烟和秘密扫描正负控制通过。随后发布登记仅新增证据及状态文档，src/tests/tools/workflow/构建/锁/Golden 与获批合并树一致；最终提交执行适用的静态、哈希及秘密检查。当前获批工作流不监听 main push，没有新增 main Actions 执行记录。

七项金融/时间/PIT/类型缺陷保持已修复。WORK-P1-004 的真实执行者是用户指定 GPT Work（Codex），不能记为 Gemini 本人执行；原审查历史保留。WORK-P1-005 当前上传策略及可得原件已验证，历史未上传字节仍 NOT VERIFIED，不追认其存在。用户本次批准是补丁验收和发布授权，不篡改历史证据。

Phase 2 的 PR #3/分支保持原状。本次不纳入因子模块，不更新其共享代码批准哈希；受控纳入补丁并重跑 Phase 2 验证仍另行处理。不进入 Phase 3。
