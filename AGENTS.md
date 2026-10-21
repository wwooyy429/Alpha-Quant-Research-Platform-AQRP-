# AQRP 项目执行规则（V3.0 + V3.1 + V3.2）

2026-10-22 最新交审状态：**Phase3 IMPLEMENTATION READY FOR GPT WORK G2 / DEVELOPER VERIFIED；未验收、未发布**。G1固定3861及U-001/U-002设计已获用户确认；26项（23MVP/3CR）实现与四主体修复见docs/audits/phase-3/。业务07e7c88745c031feeaee5d1e374a02caada77777的干净SDK、双OS各564项及原16/4通过，原ZIP/45源码/95批信号记录（含缓存引用）/1957冻结文件核验见IMPLEMENTATION_VALIDATION.json。无真实权限部署、正式Test或金融批准，不合并、不打标签、不进入P4；以下旧轮状态按时间保留。


2026-10-22 最新用户明确指令：**Phase3 G1固定3861ef1637bc2b4c28725d7afc5f2e1f02242e80 PLAN PASS；U-001设计/责任及U-002合成口径已确认；当前IMPLEMENTING（26项，23MVP+3CR）**。依据docs/audits/phase-3/IMPLEMENTATION_AUTHORIZATION.json，不重复索取启动/设计许可。U001不授权账户/ACL/服务/调度器部署；实际权限证据仍须如实验证。GPT Work固定新SHA实现审核/金融批准/阶段验收分别待办，未合并标签/P4。以下旧BLOCKED/待确认状态为历史。

2026-10-22 当前G1增量：**GPT Work对固定e26判PLAN BLOCKED；003/004仅设计CLOSED，001/002/005 OPEN**。原报告明确ff4未审。接收与处置见docs/audits/phase-3/RECHECK_E26_RESPONSE.md；001具体方案/002经济口径待用户确认，新visibility候选及005增长带宽受限方法待新SHA主审；不扩张原审查范围。未业务、未部署/金融批准、未合并标签/P4。以下早期状态为历史。

2026-10-22 审核分工更新（用户明确授权）：**后续审核、验证和测试以GPT Work为主；Codex负责开发/修复/必要自测，Gemini为可选补充，不再强制重复取得Gemini预审。** 详情见docs/REVIEW_PROTOCOL.md及docs/audits/phase-3/REVIEW_AUTHORITY_CHANGE.json。固定SHA、独立证据、阻断闭环、用户验收/合并/发布/阶段授权制度不变；不能将开发方自查改名为独立审查。当前Phase3 G1仍PLAN BLOCKED，五项待GPT Work主审复核，未获G1放行；以下旧Gemini专属安排为历史。

2026-10-22 当前：**Phase3 G1 = PLAN BLOCKED / DESIGN REVISED / FIXED-SHA RE-REVIEW REQUIRED**。GPT Work对d10a55a补充发现2High/3Medium已按原字节归档，五项具体方案/新候选及开发方处理见docs/audits/phase-3/DEVELOPER_RESPONSE.md。未自判CLOSED；Test主体/权限与合成经济假设待用户具体确认，Gemini G1尚无PASS。P3启动授权保持，本轮仅设计修订，无业务实现、无账户/ACL部署、不合并、不打标签、不进入P4。以下较早状态为历史。

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


## 当前权限

2026-10-21补充包最新依据：旧报告/五文件hash校验现已收到Gemini脚本和日志；只是文件hash范围，不补齐SDK/Actions ZIP/Git拓扑实际执行，脚本缺输入也正常结束。见docs/audits/phase-1/VERIFICATION_PACKAGE_RECONCILIATION.md、gemini/VERIFICATION_PACKAGE_INDEX.json；以下未附脚本说法属于历史。七项AGREE保留，用户未接受限制/验收/发布，完整独立执行仍NOT VERIFIED，不合并、不打标签、不进入Phase2。

2026-10-21本次增量：Gemini七项勘误全部AGREE、技术建议PASS；本轮未附新的ZIP/SDK独立执行原始记录，完整独立执行仍NOT VERIFIED。最新依据docs/audits/phase-1/SDK_HASH_INCREMENTAL_RECONCILIATION.md和gemini/SDK_HASH_INCREMENTAL_INDEX.json，优先于以下旧轮状态。用户未接受限制/验收/发布；不合并、不打标签、不进入Phase2。

2026-10-21最新SDK/hash核对：原报告及5份资料已按字节归档；Gemini未运行指定SDK/下载ZIP，专项未完整通过。开发方实际取得两个原始ZIP并核对hash、八表/结果及SDK回放，证据不能冒充Gemini执行。最新状态和剩余门禁见docs/audits/phase-1/SDK_HASH_VERIFICATION_RECONCILIATION.md、gemini/SDK_HASH_VERIFICATION_INDEX.json；此前非阻断建议不等于用户接受本次独立执行缺口。未ACCEPTED/RELEASED，不合并、不打标签、不进入Phase2。

用户已于2026-10-20明确授权Phase1开发，选择先做合成数据与通用契约、真实源另定，并批准Python3.13.16；原话及核实main起点见docs/audits/phase-1/AUTHORIZATION.json。Phase0验收/发布记录保留。当前Phase1实现审查建议PASS、七项勘误获认可，完整独立执行仍NOT VERIFIED、等待人工验收；Gemini对固定380d9f86467db874033a06a9e6487fd3998e205f计划预审PASS，原件/勘误见docs/audits/phase-1/gemini及DEVELOPER_RESPONSE.md；Phase2–7及P1合并/发布尚未授权。

Phase0已ACCEPTED并RELEASED，Gemini对7de1d0e81385ae97f98ea673fe05dd726f0b577b的Gate给PASS、F-001 CLOSED，索引见docs/audits/phase-0/gemini/GATE_EVIDENCE_INDEX.json，稳定标签不移动。Phase1从核实main 502c6931dcfce50bee2f71a80524475fae6396bf创建feature/phase-1-data-system；启动授权已取得，当前已收到Gemini对74bdb9216c585d27de91123605aff0266ca028cc的实现PASS报告；原件与处理见docs/audits/phase-1/gemini/IMPLEMENTATION_AUDIT_EVIDENCE_INDEX.json及IMPLEMENTATION_AUDIT_RESPONSE.md。Gemini补充勘误确认已收到且PASS，原件/证据分级及非阻断限制见docs/audits/phase-1/gemini/ERRATA_CONFIRMATION_INDEX.json和ERRATA_CONFIRMATION_RECONCILIATION.md；当前可提交人工验收，但不得把报告PASS或用户转交报告登记成用户ACCEPTED/RELEASED。不得重复请求启动许可，不得以旧SHA预审覆盖新实现。

开始任务先读本文件及 docs 中的 PROJECT_CHARTER、ARCHITECTURE、INTERFACES、REQUIREMENTS、TRACEABILITY、ROADMAP、PROGRESS、DECISIONS，再检查实际 Git 状态和上一阶段批准记录。发现文档与代码冲突先报告，不覆盖既有修改。

## 权威及角色

用户最新明确指令优先；V3.2 修订协作流程，V3.1 修订阶段依赖及质量契约，其余保留 V3.0。原文见 `docs/sources/`。GitHub 仓库及与固定 SHA 关联的可信证据为项目事实来源；未推送的本地成果只能称待同步草案。

- Codex开发方：主要开发、修复、文档、必要自测/CI、功能分支及PR；实际执行身份必须如实记录。
- GPT Work审查方（主要）：独立计划预审、指定SHA审查、数学答案/SDK/Actions ZIP与哈希验证及适用测试；初始只读，独立测试分支/PR另需授权。Gemini为可选补充；不能用开发方自查、子代理或模板冒充主审实际执行。
- 用户：批准需求/架构变更、阶段验收、main 合并、发布及下一阶段启动。各项授权分别记录，不推定相互包含。

## 必经关卡

阶段计划与接口草案 → GPT Work主审计划预审 → 解决阻断设计问题 → 已授权范围实现/自测 → PR + 完整Commit SHA → GPT Work固定SHA审查与验证 → 修复新SHA并复核 → 人工验收 → 按授权合并/标签 → 停止等待下一阶段明确授权。

Phase 0 可以准备待审设计和资料包；Gemini 预审前不得宣称正式设计基线已批准或开始业务实现。审查者不得审查漂移的分支头部。Critical/High 未解决则阻断；Medium 根据金融正确性、安全与验收标准判定是否阻断。CI、Gemini 和用户批准是不同事实。

## 架构与安全

固定 Python Quant Core + Streamlit + Factor Registry + 独立事件驱动回测。插件只计算信号；界面/CLI 通过同一个应用服务；回测不得依赖具体因子或 Streamlit。所有模块遵守 DATA_CONTRACT 和 BACKTEST_CONTRACT。

仅审查过、哈希批准的因子可进入批准的执行环境；候选因子在隔离、最小权限、无真实凭证环境中测试。Registry 校验不等于沙箱。禁止从网页输入直接执行任意 Python。无明确授权不得连接真实账户或提交真实订单；不提交真实密钥。

不提前实现后续依赖：P2 只测注册/替换/API 兼容；P3 研究替换；P5 组合回测替换；P6 CLI/网页一致；P7 完整替换 E2E。尚未实现能力标记 Planned、Deferred、Unsupported，不伪造结果。

## 开发与证据

分支：main 为已验收稳定版本；feature/phase-X-*、fix/*；audit/phase-X-* 仅经授权的独立测试。不得未经批准合并 main、发布标签或修改 Gemini 原报告。空仓库基线建立方式见 DECISIONS，不自动建立已验收稳定版本。

Phase0须区分 AUDIT PASSED（Gemini建议通过）、ACCEPTED（用户明确批准）、RELEASED（获批内容已在main形成核实稳定版）。空main初始化是一次性授权例外，不算RELEASED。仅在Gemini证据、用户阶段批准及合并/发布授权齐全后更新main，创建 `phase0-baseline`，维护BASELINE/PROGRESS/CHANGELOG并核对标签与main目标一致；合并新SHA须核对范围及适用检查。不得强推/重写现有历史。Phase1需Phase0为RELEASED、标签/main/文件及证据可核实，并另获Phase1授权，必须从核实main创建独立分支。

每项实现必须追溯 REQUIREMENTS 中的 ID；新范围列变更，不扩大阶段。关键金融计算须已知答案、边界、性质测试及独立参考核对。不能用待测函数生成期望值；不删失败测试、不迎合错误实现修改正确答案、不隐藏 CI 失败。

运行记录含唯一 run_id、不可变配置、代码/数据/环境哈希、完整失败记录；最终 Test 不用于反复调参。修改方向、期限、预处理均算实验。锁定依赖并审查升级。

每阶段更新追踪、进度、变更、Review Package、实际命令/输出和人工验收记录。无法运行仅标 NOT VERIFIED。未获用户批准不得把状态设为 ACCEPTED/RELEASED；“继续”等模糊用语不等于验收或下一阶段授权。

## 自动生成的同步冲突副本

用户于2026-10-20明确要求：“以后出现自动生成的冲突副本请删除它”。后续工作中发现此类副本，应核对正式文件：纯重复或仅换行/编码差异的副本直接删除，无需逐件询问；如有独有有效内容，先以可追溯方式保留差异或在授权范围内合并，再删除自动副本，不能覆盖正确的正式文件或扩大已批准范围。仅清理已确认自动生成的副本，不删除正式需求、历史审计原文或用户独立编辑文件。不据此启动后台监控、移动工作区或改变阶段授权。

# AQRP 项目执行规则（V3.0 + V3.1 + V3.2）

2026-10-21 当前修复发布：用户已验收固定 `6858c183ab97e270c9b4852cf1885fb55873327c`，PR #4 已合并 main `93b87b4ad5da5e737973ce8882e5dc9d0b656844`，包版本 **0.1.1**。补丁 **ACCEPTED**；本登记与新标签 `v0.1.1` 远端同点发布并核验后为 **RELEASED**。合并树与获批 head 完全一致，合并后干净 SDK 234 项及未编辑原始外置 16 项通过。原阶段基线标签不移动；历史缺字节 NOT VERIFIED 与指定 GPT Work 代执行事实保留。发布证据：`docs/audits/phase-1/repairs/data-validation/publication-v0.1.1/BASELINE.md`。Phase 2 分支不改，受控纳入及重新验证另办，不进入 Phase 3。以下旧状态仅作历史，以本段和实际远端 Git 为准。

2026-10-21 用户指定代执行接收：已从原审查对话实际userMessage核实“请代替Gemini执行证据”。固定31a548b的WORK-P1-004登记USER-AUTHORIZED SUBSTITUTE EXECUTION PASS，真实执行者GPT Work而非Gemini；新SDK234项、原始16项及当前CI两份原始ZIP/拓扑/三套数据结果证据已收到并核对。七项修复补充通过保持；005历史缺字节NOT VERIFIED。详情docs/audits/phase-1/repairs/data-validation/delegated-31a548b/。修复仍待用户验收及单独合并/发布授权；本次不授权Phase2纳入，不改main/稳定标签/Phase2分支，不进入Phase3。以下旧OPEN为当时状态。

2026-10-21 指定旧修复版复核接收：GPT Work 对3ab93b3的001–003补充复核通过、005新产物策略获核实；006–009在旧版仍OPEN，但本报告未审后续8902ba0/16083e1，不能外推当前修复失败或通过。当前新SHA独立复核及004指定执行仍待办。16083e1双平台CI现已确认success；本轮仅归档和证据核对，不改业务代码、不重新运行SDK。详见docs/audits/phase-1/repairs/data-validation/recheck-3ab93b3/RECONCILIATION.md。未验收/未发布修复，不合并、不打标签、不进入Phase3；main/稳定标签/Phase2分支不变。

2026-10-21 第二轮补充审查：报告目标是已发布 f579，不是 PR #4。开发方在上一修复 SDK 复现新增 WORK-P1-006–009（16 项外置用例 7 失败/9 通过，旧三项回归保持通过）；现于同一独立修复 PR 按既有 Phase1 数据契约纠正，源代码全套 234 项通过，新完整 SDK、双平台 CI 和原始 ZIP 校验已通过；固定 SHA 独立复核仍待完成。详情 docs/audits/phase-1/repairs/data-validation/round2/。修复版本尚未验收/发布；main、稳定标签和 Phase2 分支不变，不合并、不打标签、不进入Phase3。以下各轮数字/状态保留其时点。

2026-10-21 补充审查修复状态：用户已明确授权“核对、归档并修复，提交独立修复 PR（推荐）”。独立分支 fix/phase-1-data-validation 从已发布 main f579b2c99e762085772de6e70ba1fa98792a7add 起步；三项数据校验缺陷已实现并通过开发方验证，固定 SHA 独立复核待完成，候选版本 0.1.1，尚未验收/发布。原 Phase1 ACCEPTED/RELEASED 历史与标签不变。Phase2 已在另一分支获授权并实施（PR #3，核对头部 947467b9d094905cab0af37ec5cc53f1d187e755），但继承的数据层缺陷须在修复经审查、纳入后重新验证，当前不能给予正常技术通过。该分支不修改 Phase2，不合并、不打标签、不进入 Phase3。最新记录见 docs/audits/phase-1/repairs/data-validation/；以下旧状态为历史，若冲突以本段和实际 Git 为准。

2026-10-21 最新发布状态：**Phase1 ACCEPTED / RELEASED**。用户已分别完成验收并授权“请开始合并并打标签”；PR #2已合并（9b843b17ccf362cf5b7a5351269559a627c55b32），稳定标签phase1-baseline指向含发布登记的main版本，远端原子发布后核验生效。原话和合并/SDK证据见docs/audits/phase-1/publication/；基线见docs/audits/phase-1/BASELINE.md。Gemini独立执行及旧远端缺字节事实保留，未声称新增Gemini审查。Phase2尚未授权，不自动启动。

以下既有未合并/未发布/未授权文字为之前各轮历史，当前以本次发布登记和实际Git核验为准。

2026-10-21 最新人工决定：用户明确表示“phase 1验收已完成”，现登记 **Phase1 = ACCEPTED，尚未 RELEASED**。验收对应接收时PR #2的71cc044d5f4e2079426049c0f7c6f747fee01692（业务74bdb92），原话与范围见 docs/audits/phase-1/acceptance/ACCEPTANCE.json。此前“等待验收/未ACCEPTED”仅为历史；Gemini独立执行和原远端缺字节事实继续保留，本次未伪造逐项限制豁免。合并main、打标签及Phase2均未授权。

以下既有状态段落保留为各轮历史，当前人工验收状态以上述记录为准。

2026-10-21 最新本地验证：已按用户授权配置 Conda aqrp-p1（CPython3.13.16）和独立 VS Code 工作区；完整 SDK、Conda 直接运行的同一组102测试、两份 Actions 原始ZIP/八表/SDK回放均通过。实际命令配置与原始日志见 docs/audits/phase-1/implementation/conda-vscode-74bdb92/README.md。执行者为 Codex 开发方，不能补记为 Gemini 独立执行；远端3项根文件及项目wheel原字节缺口、独立执行/人工验收/发布门禁保留。未合并、未打标签、不进入Phase2。


## 当前权限

2026-10-21补充包最新依据：旧报告/五文件hash校验现已收到Gemini脚本和日志；只是文件hash范围，不补齐SDK/Actions ZIP/Git拓扑实际执行，脚本缺输入也正常结束。见docs/audits/phase-1/VERIFICATION_PACKAGE_RECONCILIATION.md、gemini/VERIFICATION_PACKAGE_INDEX.json；以下未附脚本说法属于历史。七项AGREE保留，用户未接受限制/验收/发布，完整独立执行仍NOT VERIFIED，不合并、不打标签、不进入Phase2。

2026-10-21本次增量：Gemini七项勘误全部AGREE、技术建议PASS；本轮未附新的ZIP/SDK独立执行原始记录，完整独立执行仍NOT VERIFIED。最新依据docs/audits/phase-1/SDK_HASH_INCREMENTAL_RECONCILIATION.md和gemini/SDK_HASH_INCREMENTAL_INDEX.json，优先于以下旧轮状态。用户未接受限制/验收/发布；不合并、不打标签、不进入Phase2。

2026-10-21最新SDK/hash核对：原报告及5份资料已按字节归档；Gemini未运行指定SDK/下载ZIP，专项未完整通过。开发方实际取得两个原始ZIP并核对hash、八表/结果及SDK回放，证据不能冒充Gemini执行。最新状态和剩余门禁见docs/audits/phase-1/SDK_HASH_VERIFICATION_RECONCILIATION.md、gemini/SDK_HASH_VERIFICATION_INDEX.json；此前非阻断建议不等于用户接受本次独立执行缺口。未ACCEPTED/RELEASED，不合并、不打标签、不进入Phase2。

用户已于2026-10-20明确授权Phase1开发，选择先做合成数据与通用契约、真实源另定，并批准Python3.13.16；原话及核实main起点见docs/audits/phase-1/AUTHORIZATION.json。Phase0验收/发布记录保留。当前Phase1实现审查建议PASS、七项勘误获认可，完整独立执行仍NOT VERIFIED、等待人工验收；Gemini对固定380d9f86467db874033a06a9e6487fd3998e205f计划预审PASS，原件/勘误见docs/audits/phase-1/gemini及DEVELOPER_RESPONSE.md；Phase2–7及P1合并/发布尚未授权。

Phase0已ACCEPTED并RELEASED，Gemini对7de1d0e81385ae97f98ea673fe05dd726f0b577b的Gate给PASS、F-001 CLOSED，索引见docs/audits/phase-0/gemini/GATE_EVIDENCE_INDEX.json，稳定标签不移动。Phase1从核实main 502c6931dcfce50bee2f71a80524475fae6396bf创建feature/phase-1-data-system；启动授权已取得，当前已收到Gemini对74bdb9216c585d27de91123605aff0266ca028cc的实现PASS报告；原件与处理见docs/audits/phase-1/gemini/IMPLEMENTATION_AUDIT_EVIDENCE_INDEX.json及IMPLEMENTATION_AUDIT_RESPONSE.md。Gemini补充勘误确认已收到且PASS，原件/证据分级及非阻断限制见docs/audits/phase-1/gemini/ERRATA_CONFIRMATION_INDEX.json和ERRATA_CONFIRMATION_RECONCILIATION.md；当前可提交人工验收，但不得把报告PASS或用户转交报告登记成用户ACCEPTED/RELEASED。不得重复请求启动许可，不得以旧SHA预审覆盖新实现。

开始任务先读本文件及 docs 中的 PROJECT_CHARTER、ARCHITECTURE、INTERFACES、REQUIREMENTS、TRACEABILITY、ROADMAP、PROGRESS、DECISIONS，再检查实际 Git 状态和上一阶段批准记录。发现文档与代码冲突先报告，不覆盖既有修改。

## 权威及角色

用户最新明确指令优先；V3.2 修订协作流程，V3.1 修订阶段依赖及质量契约，其余保留 V3.0。原文见 `docs/sources/`。GitHub 仓库及与固定 SHA 关联的可信证据为项目事实来源；未推送的本地成果只能称待同步草案。

- Codex开发方：主要开发、修复、文档、必要自测/CI、功能分支及PR；实际执行身份必须如实记录。
- GPT Work审查方（主要）：独立计划预审、指定SHA审查、数学答案/SDK/Actions ZIP与哈希验证及适用测试；初始只读，独立测试分支/PR另需授权。Gemini为可选补充；不能用开发方自查、子代理或模板冒充主审实际执行。
- 用户：批准需求/架构变更、阶段验收、main 合并、发布及下一阶段启动。各项授权分别记录，不推定相互包含。

## 必经关卡

阶段计划与接口草案 → GPT Work主审计划预审 → 解决阻断设计问题 → 已授权范围实现/自测 → PR + 完整Commit SHA → GPT Work固定SHA审查与验证 → 修复新SHA并复核 → 人工验收 → 按授权合并/标签 → 停止等待下一阶段明确授权。

Phase 0 可以准备待审设计和资料包；Gemini 预审前不得宣称正式设计基线已批准或开始业务实现。审查者不得审查漂移的分支头部。Critical/High 未解决则阻断；Medium 根据金融正确性、安全与验收标准判定是否阻断。CI、Gemini 和用户批准是不同事实。

## 架构与安全

固定 Python Quant Core + Streamlit + Factor Registry + 独立事件驱动回测。插件只计算信号；界面/CLI 通过同一个应用服务；回测不得依赖具体因子或 Streamlit。所有模块遵守 DATA_CONTRACT 和 BACKTEST_CONTRACT。

仅审查过、哈希批准的因子可进入批准的执行环境；候选因子在隔离、最小权限、无真实凭证环境中测试。Registry 校验不等于沙箱。禁止从网页输入直接执行任意 Python。无明确授权不得连接真实账户或提交真实订单；不提交真实密钥。

不提前实现后续依赖：P2 只测注册/替换/API 兼容；P3 研究替换；P5 组合回测替换；P6 CLI/网页一致；P7 完整替换 E2E。尚未实现能力标记 Planned、Deferred、Unsupported，不伪造结果。

## 开发与证据

分支：main 为已验收稳定版本；feature/phase-X-*、fix/*；audit/phase-X-* 仅经授权的独立测试。不得未经批准合并 main、发布标签或修改 Gemini 原报告。空仓库基线建立方式见 DECISIONS，不自动建立已验收稳定版本。

Phase0须区分 AUDIT PASSED（Gemini建议通过）、ACCEPTED（用户明确批准）、RELEASED（获批内容已在main形成核实稳定版）。空main初始化是一次性授权例外，不算RELEASED。仅在Gemini证据、用户阶段批准及合并/发布授权齐全后更新main，创建 `phase0-baseline`，维护BASELINE/PROGRESS/CHANGELOG并核对标签与main目标一致；合并新SHA须核对范围及适用检查。不得强推/重写现有历史。Phase1需Phase0为RELEASED、标签/main/文件及证据可核实，并另获Phase1授权，必须从核实main创建独立分支。

每项实现必须追溯 REQUIREMENTS 中的 ID；新范围列变更，不扩大阶段。关键金融计算须已知答案、边界、性质测试及独立参考核对。不能用待测函数生成期望值；不删失败测试、不迎合错误实现修改正确答案、不隐藏 CI 失败。

运行记录含唯一 run_id、不可变配置、代码/数据/环境哈希、完整失败记录；最终 Test 不用于反复调参。修改方向、期限、预处理均算实验。锁定依赖并审查升级。

每阶段更新追踪、进度、变更、Review Package、实际命令/输出和人工验收记录。无法运行仅标 NOT VERIFIED。未获用户批准不得把状态设为 ACCEPTED/RELEASED；“继续”等模糊用语不等于验收或下一阶段授权。

## 自动生成的同步冲突副本

用户于2026-10-20明确要求：“以后出现自动生成的冲突副本请删除它”。后续工作中发现此类副本，应核对正式文件：纯重复或仅换行/编码差异的副本直接删除，无需逐件询问；如有独有有效内容，先以可追溯方式保留差异或在授权范围内合并，再删除自动副本，不能覆盖正确的正式文件或扩大已批准范围。仅清理已确认自动生成的副本，不删除正式需求、历史审计原文或用户独立编辑文件。不据此启动后台监控、移动工作区或改变阶段授权。
