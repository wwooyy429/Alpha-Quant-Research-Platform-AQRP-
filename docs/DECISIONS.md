# 架构决策、冲突及待用户决定事项

2026-10-21 补充审查修复状态：用户已明确授权“核对、归档并修复，提交独立修复 PR（推荐）”。独立分支 fix/phase-1-data-validation 从已发布 main f579b2c99e762085772de6e70ba1fa98792a7add 起步；三项数据校验缺陷修复中，候选版本 0.1.1，尚未验收/发布。原 Phase1 ACCEPTED/RELEASED 历史与标签不变。Phase2 已在另一分支获授权并实施（PR #3，核对头部 947467b9d094905cab0af37ec5cc53f1d187e755），但继承的数据层缺陷须在修复经审查、纳入后重新验证，当前不能给予正常技术通过。该分支不修改 Phase2，不合并、不打标签、不进入 Phase3。最新记录见 docs/audits/phase-1/repairs/data-validation/；以下旧状态为历史，若冲突以本段和实际 Git 为准。

2026-10-21 最新发布状态：**Phase1 ACCEPTED / RELEASED**。用户已分别完成验收并授权“请开始合并并打标签”；PR #2已合并（9b843b17ccf362cf5b7a5351269559a627c55b32），稳定标签phase1-baseline指向含发布登记的main版本，远端原子发布后核验生效。原话和合并/SDK证据见docs/audits/phase-1/publication/；基线见docs/audits/phase-1/BASELINE.md。Gemini独立执行及旧远端缺字节事实保留，未声称新增Gemini审查。Phase2尚未授权，不自动启动。

以下既有未合并/未发布/未授权文字为之前各轮历史，当前以本次发布登记和实际Git核验为准。

2026-10-21 最新人工决定：用户明确表示“phase 1验收已完成”，现登记 **Phase1 = ACCEPTED，尚未 RELEASED**。验收对应接收时PR #2的71cc044d5f4e2079426049c0f7c6f747fee01692（业务74bdb92），原话与范围见 docs/audits/phase-1/acceptance/ACCEPTANCE.json。此前“等待验收/未ACCEPTED”仅为历史；Gemini独立执行和原远端缺字节事实继续保留，本次未伪造逐项限制豁免。合并main、打标签及Phase2均未授权。

以下既有状态段落保留为各轮历史，当前人工验收状态以上述记录为准。

2026-10-21本轮决定边界：新增Gemini报告认可全部七项勘误、技术PASS；完整独立执行仍未获可核验原始证据，用户未接受限制。当前依据audits/phase-1/SDK_HASH_INCREMENTAL_RECONCILIATION.md，以下旧轮非阻断建议不代替用户决定。人工验收、合并/标签、主干基线和Phase2授权仍未发生。

2026-10-21最新：本次SDK/hash报告承认Gemini执行受阻，不能按技术PASS视作专项完整通过。开发方补充原始ZIP及数据/SDK核对已实际完成，独立执行缺口仍需补齐或由用户明确决定接受；未发生该决定。详见audits/phase-1/SDK_HASH_VERIFICATION_RECONCILIATION.md；下列既有D-012等非阻断意见保留历史来源，不代替本次用户决定。

Phase0已发布且Gate PASS/F-001 CLOSED，证据在audits/phase-0。用户现已授权Phase1，选择合成数据/通用契约及Python3.13.16，原话见audits/phase-1/AUTHORIZATION.json；Phase1计划/实现审查和补充勘误确认均PASS，当前等待用户Phase1人工验收；未来阶段profile及业务假设仍按各项条件批准。

| ID | 类型 / 事项 | 当前处理与提案 | 决策者 / 截止关卡 |
|---|---|---|---|
| D-001 | 已有指令：固定架构与P0范围 | V3.0架构继续；当前只做设计；V3.2覆盖审查协作 | 用户原始指令；未来变更需新批准 |
| D-002 | P1合成范围已批准；真实市场/源另定 | 用户明确先做合成数据与通用契约。P1采用显式测试profile/日历，不能宣称符合任何交易所；真实市场/供应商/许可、费用/税/限制等仍未指定 | P1按合成计划预审实施；真实源接入前及P4/P5/P7按阶段确定相应规则 |
| D-003 | 用户已批准Python3.13.16；兼容/锁/安装待验证 | 本机3.10.11仅文档工具，注册3.11无法启动；业务3.13.16尚未安装。候选依赖/工具精确版本及主源wheel元数据见phase-1/ENVIRONMENT_PLAN与DEPENDENCY_CANDIDATES，不能当作已锁定或安装通过 | 本阶段Gemini计划预审后解析完整锁并验证Windows/Linux实际环境，变更精确版本仍需记录依据 |
| D-004 | 未决：样本划分/通过门槛 | 实际日期、期限网格、最小n、试验预算、IC/成本后收益/风险门槛尚未指定；缺项不能正式批准因子 | 用户+Gemini；P3正式评估前，P5补交易门槛 |
| D-005 | 未决：数学/执行定义提案 | ddof=1、平均并列秩、next-open标签、非年化ICIR、移动均价成本法、Decimal舍入、单币种和合成开盘容量等为提案 | 用户+Gemini；对应阶段计划批准前 |
| D-006 | 未决：不可信代码隔离 | P2先限已审随库因子；任意外部插件上传执行Unsupported；独立进程/OS沙箱方案须威胁建模及权限确认 | 用户+Gemini；开放外部执行前 |
| D-007 | 核心勘误及P0独立主干门禁闭环 | 发布7de1d0e已Gate PASS/F-001 CLOSED，P0标签保留，物理隔离等原限制不抹除。用户现已授权P1并选范围/版本，P0报告不能替代P1预审 | Phase1先提交计划/接口/独立答案候选，未取得本阶段Gemini预审不写业务代码 |
| D-008 | 未决：性能与资源 | 证券数量/年份/数据量/内存/耗时目标未知；不预设无依据SLA，不提前分布式实现 | 用户；必要性能测试前 |
| D-009 | 未决：能力分级与覆盖率 | 四级划分和测试覆盖门槛已提出；CompetitionReady中的V3.0必需功能不能自动延期 | 用户+Gemini；P0设计批准前 |
| D-010 | 初始化/批准/合并/标签/独立核验已追溯 | PR#1合并8c37e95的tree与获批228190a一致；phase0-baseline固定7de1d0e，附注对象0b2230cd4861ca3b47fa30fc30dae9f4dc4109d0，Gemini已完成主干链路核验 | APPROVAL、MERGE_VERIFICATION及GATE_EVIDENCE_INDEX分别存证；新归档提交不是替代基线 |
| D-011 | 未决：PIT证据不足历史源 | 供应商无历史available_at证据时仅Exploratory，不能用抓取时间倒填历史；需独立来源核对方案 | 用户+Gemini；正式PIT验收前 |
| D-012 | P1独立审查通过，用户验收未发生 | 74bdb92实现报告及针对578fb51的补充确认均PASS；保留本地SDK与远端hash未验证的非阻断限制，详见ERRATA_CONFIRMATION_RECONCILIATION | 用户决定人工验收；main合并、标签/基线发布及Phase2各自另行授权，不能用转交报告代替 |

## 已识别冲突及处理

1. V3.0因子替换“完整流程”与早期模块不可用：按V3.1/V3.2分P2/P3/P5/P6/P7测试，不提前开发后续模块；未实现测试Planned。
2. V3.0 Phase0完成后“等待人工批准”与V3.2审查后才可申请验收：先交待审设计和Gemini资料；未有Gemini审查不申请正常通过，不输出暗示通过的结论。
3. V3.2要求实施前Gemini预审，而本次无Gemini连接：当前成果全是供预审的提案，无业务实现；不得视为G1已通过。
4. V3.0批准因子输入P4但实用性需P5成本/限制：拆分Reviewed、ResearchValidated和StrategyApproved。P4纯组合可用研究已验证的精确分数和显式夹具；正式策略执行须P5后的最终审批证据。
5. V3.0要求第一版多空/中性化等，V3.1要求MVP分离：仅作交付层级，不删除/静默延期原必须项；完整系统阶段需对应CompetitionReady需求，扩展能力另授权。
6. 原空仓库无base/PR的问题已解决，空main及开发历史保留。批准、合并8c37e95、标签7de1d0e及Gemini Gate PASS现均有证据；归档记录随后追加main，稳定标签不移动。清单hash仍不替代Git SHA、CI或独立复核。

## 变更控制

变更记录需change_id、源要求、原因、影响需求/接口/阶段、测试及迁移、风险、批准人/证据、实施SHA。分级变化、依赖变更、Golden修订与稳定接口变化均不能靠改文档消除未通过项。未知比赛规则可以明确列待决，不应擅自填入；影响当前设计的关键争议未处理前不宣布架构验收通过。


2026-10-21状态增量：Gemini对380d9f8计划预审PASS，当前Phase1 IMPLEMENTING。原文/证据索引及报告勘误在audits/phase-1/gemini/PRE_REVIEW_EVIDENCE_INDEX.json和DEVELOPER_RESPONSE.md。此状态替代此前等待计划预审描述；验收、main合并、打标、Phase2仍未授权。


2026-10-21实现增量：Phase1计划预审PASS后完成合成数据/通用契约14项实现和102项测试，当前IMPLEMENTATION REVIEW REQUIRED；实际证据和旧失败以audits/phase-1/IMPLEMENTATION_REVIEW_PACKAGE.md及implementation/EVIDENCE_INDEX.json为准。本增量替代此前等待计划预审/尚无业务代码的当前状态描述；初始计划和授权快照保留。main、稳定标签及P0核心契约不变；未验收/未合并/未发布，不进入Phase2。


2026-10-21实现审计接收：Gemini对74bdb92原文PASS并关闭F-002/F-003/F-P1-PRE-001；开发方核对发现500应为1000、数个文件路径及tests/golden独立执行证据表述不符等勘误。报告按字节归档，完整处置见audits/phase-1/IMPLEMENTATION_AUDIT_RESPONSE.md及gemini/IMPLEMENTATION_AUDIT_EVIDENCE_INDEX.json；本次不改业务代码/答案/阈值。当前AUDIT PASS AS REPORTED / REPORT ERRATA CLARIFICATION REQUIRED，尚非ACCEPTED/RELEASED；无合并、标签或Phase2授权。
