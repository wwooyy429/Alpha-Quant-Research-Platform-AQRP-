# Alpha Quant Research Platform（AQRP）

2026-10-22 当前：**Phase2已ACCEPTED / RELEASED；Phase3 START AUTHORIZED / PLAN PRE-REVIEW REQUIRED**。核实main与phase2-baseline/v0.2.0同点f26255fc40a3080bfa883ad64938f60036a14759，已创建feature/phase-3-alpha-research。P3限既定26项（23 MVP/3 Competition Ready）、沿用合成数据及Python3.13.16；计划/接口/数值候选/风险与测试在docs/audits/phase-3/。本轮无P3业务实现，Gemini G1预审及阻断设计闭环后才实施；不重复索取启动授权，不把P2报告或旧417回归当P3通过。P3验收/合并发布/P4启动尚未授权，历史执行身份与缺原件事实保留。以下旧状态为历史。

2026-10-22 最新人工决定与发布登记：用户明确“验收通过，请合并打标签后进入phase 3开发”。**Phase2 ACCEPTED**，PR #3批准头e50cd75已合并main bb6076f，tree与批准头完全一致；合并后新干净SDK417、原16/四探针均通过。发布登记与 `phase2-baseline` / `v0.2.0` 远端main原子同点发布并核验后为 **RELEASED**。Phase3启动已授权，从核实基线新分支先走Gemini计划预审，不重复索取启动许可。原报告身份/执行与历史缺原件事实不改，未泛化为逐项豁免；详见docs/audits/phase-2/BASELINE.md及publication/。P3业务实施受既有G1预审门禁，P3合并发布/P4–7尚未授权；以下旧待验收/未授权为历史。

2026-10-22 最新复核接收：**Phase2 = GPT WORK SUPPLEMENTAL TECHNICAL PASS / HUMAN ACCEPTANCE PENDING**。GPT Work针对固定c8362953f555606795b6804cdfe28ff690c2364d确认001–003全部CLOSED（补充技术复核），无新业务修复。所附新SDK/双OS各417、原16和原四项通过；接收已核对256项hash、官方原ZIP/26模块wheel/八表/完整Signal回放及12项原查询身份。资料见 `docs/audits/phase-2/recheck-c836/`。这不是Gemini本人执行或用户验收；Gemini新完整SDK/历史原件限制保留，未接受限制/合并/标签发布/P3授权。仅归档及状态更新，业务708b83b/代码bundle51933fe…不改；以下旧OPEN/待复核为历史。

2026-10-22 当前：**Phase2 = REPAIR DEVELOPER VALIDATION PASS / FIXED-SHA RE-REVIEW REQUIRED**。GPT Work对c70727c的001集成补充PASS已接收；002/003两项Medium阻断已开发方复现并修复，业务708b83be1dd597395b41f2ff6e10702749175bbf。新干净wheel SDK及双OS CI各417项、未编辑原16项及原四探针4项全部通过，原两失败及错误成功产物保留；新两份原始ZIP官方hash/46项内部清单/数据与因子重放通过。26模块新bundle51933fe2508e61a25fef53ea73b4210a67cb19d6531e1bf614e206db32a1d62d，经开发方实际重审，仅ENGINEERING_APPROVED / TEST_ONLY / NONE。详情 `docs/audits/phase-2/lineage-fix/`；002/003待审查方新固定SHA确认，不以自测代为CLOSED。Gemini本人执行及人工验收/发布仍分开保留；不合并main、不打标签、不进入Phase3。以下旧状态为历史。

2026-10-22 当前：**Phase2 = INTEGRATED / DEVELOPER VALIDATION PASS / FIXED-SHA RE-REVIEW REQUIRED**。已按用户授权以双父merge集成v0.1.1/main fb1ba4fd51202a303115e4449ee49db09ccc071c，业务提交566f0ece4175fddb2703daab3b5b26ff0e4e245f，候选包保持0.2.0。共享源码重审后新bundle为fc1b50110c02efbe4a53168c43d7fe4972e5ebab3edc3091aeaf58ac72a11fc7，仅ENGINEERING_APPROVED / TEST_ONLY / financial_approval=NONE。新干净wheel SDK和双OS CI各392项通过，原始外置16项通过；当前两份原始ZIP/46项选择文件hash/八表及查询回放/三个因子结果已核实。详见 `docs/audits/phase-2/integration-011/`。这是开发方验证，Gemini须审新固定SHA；旧报告事实对齐及独立执行限制未自动关闭。未Phase2人工验收，不合并main、不打标签、不进入Phase3；以下旧状态保留为历史。

2026-10-21 当前：**Phase2 = INCREMENTAL AUDIT PASS AS REPORTED / CORE MATH VERIFIED / REPORT ALIGNMENT AND EXECUTION LIMITS OPEN**。Gemini对0b5107f增量报告PASS、十二项AGREE/CLOSED及两项Low继续CLOSED已接收；修订数学.py/.log原件已收到，Volume两输入、证券B推导、非零浮点误差经开发方复跑/独立核算通过，旧数学错误不再作为当前未修项。报告解释仍有PR标题/BASELINE、FACTOR-011、源码路径等事实冲突，详见docs/audits/phase-2/MATH_INCREMENTAL_RECONCILIATION.md及gemini/MATH_INCREMENTAL_INDEX.json。SDK独立执行仍NOT VERIFIED、ZIP本轮Evidence Reviewed Only；未人工验收/接受限制，main/稳定标签不动，不合并、不打标签、不进入Phase3。

以下保留历轮状态，当前以上述实现复核状态及固定SHA资料为准。

2026-10-21 Phase2计划预审接收：Gemini对4f8b0de报告PLAN PASS、无阻断项；用户明确允许继续已授权范围。报告原件/需求职责与分支/数学勘误见docs/audits/phase-2/gemini/PRE_REVIEW_INDEX.json及PRE_REVIEW_RESPONSE.md。当前IMPLEMENTING；只实现10项既定需求和Momentum/Reversal/Volume，不按报告误写新增Volatility/DAG。未验收/合并/发布，不进入P3。

以下为历史状态，当前以上述预审接收为准。

2026-10-21 最新授权：用户明确“请正式开始进入phase 2”。已从核实main / phase1-baseline f579b2c99e762085772de6e70ba1fa98792a7add创建feature/phase-2-factor-registry；**Phase2 = PLAN PRE-REVIEW REQUIRED**。计划与10项需求映射见docs/audits/phase-2/PLAN.md和AUTHORIZATION.json；Gemini计划预审前不编写本阶段业务实现。Phase1已发布，既有执行限制保留；P2验收/合并/标签及P3尚未授权。此前“Phase2未授权”仅为历史。

以下各轮状态保留历史来源；当前阶段权限以上述启动记录为准。

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
