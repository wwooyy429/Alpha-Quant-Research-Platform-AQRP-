# AQRP 项目执行规则（V3.0 + V3.1 + V3.2）

2026-10-21 第二轮补充审查：报告目标是已发布 f579，不是 PR #4。开发方在上一修复 SDK 复现新增 WORK-P1-006–009（16 项外置用例 7 失败/9 通过，旧三项回归保持通过）；现于同一独立修复 PR 按既有 Phase1 数据契约纠正，源代码全套 234 项通过，新的完整 SDK/CI/独立复核待补。详情 docs/audits/phase-1/repairs/data-validation/round2/。修复版本尚未验收/发布；main、稳定标签和 Phase2 分支不变，不合并、不打标签、不进入Phase3。以下各轮数字/状态保留其时点。

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

- GPT Work：主要开发、测试、文档、功能分支及 PR、修复审查缺陷。
- Gemini：独立计划预审、指定 SHA 审查、独立核对答案及有权限时补充测试。初始只读；独立测试分支与 PR 须用户授权。不能用 GPT 自查、GPT 子代理或模板冒充 Gemini 审查。
- 用户：批准需求/架构变更、阶段验收、main 合并、发布及下一阶段启动。各项授权分别记录，不推定相互包含。

## 必经关卡

阶段计划与接口草案 → Gemini 计划预审 → 解决阻断设计问题 → 已授权范围实现/自测 → PR + 完整 Commit SHA → Gemini 固定 SHA 审查 → 修复新 SHA 并复核 → 人工验收 → 按授权合并/标签 → 停止等待下一阶段明确授权。

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
