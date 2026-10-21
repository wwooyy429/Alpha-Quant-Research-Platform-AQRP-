# Alpha Quant Research Platform（AQRP）

2026-10-21 当前修复发布：用户已验收固定 `6858c183ab97e270c9b4852cf1885fb55873327c`，PR #4 已合并 main `93b87b4ad5da5e737973ce8882e5dc9d0b656844`，包版本 **0.1.1**。补丁 **ACCEPTED**；本登记与新标签 `v0.1.1` 远端同点发布并核验后为 **RELEASED**。合并树与获批 head 完全一致，合并后干净 SDK 234 项及未编辑原始外置 16 项通过。原阶段基线标签不移动；历史缺字节 NOT VERIFIED 与指定 GPT Work 代执行事实保留。发布证据：`docs/audits/phase-1/repairs/data-validation/publication-v0.1.1/BASELINE.md`。Phase 2 分支不改，受控纳入及重新验证另办，不进入 Phase 3。以下旧状态仅作历史，以本段和实际远端 Git 为准。

2026-10-21 第二轮补充审查：报告目标是已发布 f579，不是 PR #4。开发方在上一修复 SDK 复现新增 WORK-P1-006–009（16 项外置用例 7 失败/9 通过，旧三项回归保持通过）；现于同一独立修复 PR 按既有 Phase1 数据契约纠正，源代码全套 234 项通过，新完整 SDK、双平台 CI 和原始 ZIP 校验已通过；固定 SHA 独立复核仍待完成。详情 docs/audits/phase-1/repairs/data-validation/round2/。修复版本尚未验收/发布；main、稳定标签和 Phase2 分支不变，不合并、不打标签、不进入Phase3。以下各轮数字/状态保留其时点。

2026-10-21 补充审查修复状态：用户已明确授权“核对、归档并修复，提交独立修复 PR（推荐）”。独立分支 fix/phase-1-data-validation 从已发布 main f579b2c99e762085772de6e70ba1fa98792a7add 起步；三项数据校验缺陷已实现并通过开发方验证，固定 SHA 独立复核待完成，候选版本 0.1.1，尚未验收/发布。原 Phase1 ACCEPTED/RELEASED 历史与标签不变。Phase2 已在另一分支获授权并实施（PR #3，核对头部 947467b9d094905cab0af37ec5cc53f1d187e755），但继承的数据层缺陷须在修复经审查、纳入后重新验证，当前不能给予正常技术通过。该分支不修改 Phase2，不合并、不打标签、不进入 Phase3。最新记录见 docs/audits/phase-1/repairs/data-validation/；以下旧状态为历史，若冲突以本段和实际 Git 为准。

2026-10-21 最新发布状态：**Phase1 ACCEPTED / RELEASED**。用户已分别完成验收并授权“请开始合并并打标签”；PR #2已合并（9b843b17ccf362cf5b7a5351269559a627c55b32），稳定标签phase1-baseline指向含发布登记的main版本，远端原子发布后核验生效。原话和合并/SDK证据见docs/audits/phase-1/publication/；基线见docs/audits/phase-1/BASELINE.md。Gemini独立执行及旧远端缺字节事实保留，未声称新增Gemini审查。Phase2尚未授权，不自动启动。

以下既有未合并/未发布/未授权文字为之前各轮历史，当前以本次发布登记和实际Git核验为准。

2026-10-21 最新人工决定：用户明确表示“phase 1验收已完成”，现登记 **Phase1 = ACCEPTED，尚未 RELEASED**。验收对应接收时PR #2的71cc044d5f4e2079426049c0f7c6f747fee01692（业务74bdb92），原话与范围见 docs/audits/phase-1/acceptance/ACCEPTANCE.json。此前“等待验收/未ACCEPTED”仅为历史；Gemini独立执行和原远端缺字节事实继续保留，本次未伪造逐项限制豁免。合并main、打标签及Phase2均未授权。

以下既有状态段落保留为各轮历史，当前人工验收状态以上述记录为准。

2026-10-21 最新本地验证：已按用户授权配置 Conda aqrp-p1（CPython3.13.16）和独立 VS Code 工作区；完整 SDK、Conda 直接运行的同一组102测试、两份 Actions 原始ZIP/八表/SDK回放均通过。实际命令配置与原始日志见 docs/audits/phase-1/implementation/conda-vscode-74bdb92/README.md。执行者为 Codex 开发方，不能补记为 Gemini 独立执行；远端3项根文件及项目wheel原字节缺口、独立执行/人工验收/发布门禁保留。未合并、未打标签、不进入Phase2。


最新补充包：[脚本/日志接收核对](docs/audits/phase-1/VERIFICATION_PACKAGE_RECONCILIATION.md)。文件hash子项材料已补齐，完整SDK/原始产物独立执行仍未闭环；七项认可保留，未验收/发布、不进入Phase2。下列“未附脚本”是此前接收状态。

最新增量：Gemini已认可七项SDK/hash勘误、技术审查建议PASS；[本轮核对](docs/audits/phase-1/SDK_HASH_INCREMENTAL_RECONCILIATION.md)保留独立SDK/产物执行证据缺口及新报告细节勘误。用户未接受限制、未验收/发布；PR保持Draft，不合并、不打标签、不进入Phase2。以下各轮文字作为历史，当前以本轮核对为准。

最新核对：Phase1实现审查建议PASS；[SDK/hash专项](docs/audits/phase-1/SDK_HASH_VERIFICATION_RECONCILIATION.md)仅部分完成，Gemini实际SDK/ZIP验证受阻。开发方已补充原始ZIP/hash/八表及SDK冒烟证据，不替代独立执行；等待用户验收，未合并/发布，不进入Phase2。以下历史状态以最新专项记录为准。

Phase 0 已发布。Phase 1 计划经 Gemini 对固定380d9f8预审PASS，现已实现合成日频数据基础，已收到Gemini对74bdb92的实现PASS报告及独立勘误确认PASS，当前等待人工验收。阶段验收、main合并、发布及Phase 2均尚未获授权。

本阶段提供稳定证券标识、Decimal单位、UTC微秒时间与固定IANA规则、日历、PIT可见修订、历史股票池/状态、拆股与分红研究视图、质量报告、不可变Parquet快照和可重建DuckDB索引。首版只支持明确的SYNTHETIC_V1测试profile，真实市场接入另行确定。

当前范围和真实验证见[Phase1实现审查包](docs/audits/phase-1/IMPLEMENTATION_REVIEW_PACKAGE.md)、[数据SDK使用说明](docs/audits/phase-1/DATA_SDK.md)和[进度](docs/PROGRESS.md)。[独立计划预审原件及索引](docs/audits/phase-1/gemini/PRE_REVIEW_EVIDENCE_INDEX.json)保持原字节。380d9f8中的PLAN、SELF_CHECK、MANIFEST和COMMAND_LOG仍为历史计划快照，不能当作当前实现测试结果。

业务环境精确CPython3.13.16标准GIL/x64，直接与传递依赖固定在requirements.lock。安装及完整验证入口为`python tools/ci.py`，须在干净、已提交工作区和已核实解释器下运行；它把venv/构建/缓存/测试产物放入非同步临时路径，哈希安装依赖，从固定Commit离线构建并安装本项目wheel，执行静态/单元/性质/契约/集成/泄漏/覆盖率/秘密扫描及数据smoke。详见[复现说明](docs/audits/phase-1/REPRODUCE.md)。

因子Registry、因子研究、组合/风险、回测账本、网页及对应业务CLI仍Planned；高级扩展Deferred，真实交易与任意外部代码执行Unsupported。不存在真实凭证、供应商或订单接入。


本轮报告原件、审查方发现关闭记录及开发方核对见[实现审计接收索引](docs/audits/phase-1/gemini/IMPLEMENTATION_AUDIT_EVIDENCE_INDEX.json)与[实现报告勘误/处理意见](docs/audits/phase-1/IMPLEMENTATION_AUDIT_RESPONSE.md)。上述核心勘误已获Gemini确认；最新[补充确认与状态核对](docs/audits/phase-1/ERRATA_CONFIRMATION_RECONCILIATION.md)保留本地SDK未验证及远端产物未重算等非阻断限制。当前审查通过、等待人工验收；不能将用户转交报告当作验收、合并或发布授权。
