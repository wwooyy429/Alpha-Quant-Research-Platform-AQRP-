# 架构决策、冲突及待用户决定事项

2026-10-22 当前Phase4：用户已授权7项受限工程实现，53模块0.4.0已完成开发自测，业务b3be62439d8d0877478b7105d68863fcb2a108a0干净SDK799、双OS各799及原始ZIP/hash核验、外置20/四/数学91通过。当前IMPLEMENTATION READY FOR GPT WORK G2，不是独立G2通过或阶段验收；详docs/audits/phase-4/IMPLEMENTATION_REVIEW_PACKAGE.md。真实隔离/正式Test/金融批准及旧完整宿主限制保留，main/标签不动，无合并/发布/部署/实盘/P5。以下旧状态按轮次保留。

2026-10-22 当前Phase4 G1：GPT Work对固定265af16353d85ce8c2d229a7517809d707498da8判PLAN PASS（受限工程设计），001 High/002 Medium均CLOSED_DESIGN，无新增阻断。原17候选独立复算、64项证据检查通过；仅设计数学，不是P4实现。原件与接收/关闭在docs/audits/phase-4/g1-265af16/。实际P4实施仍待用户单独授权，未阶段验收/合并/标签/部署/实盘/P5；Phase3受限发布与延期不变。以下旧BLOCKED/OPEN按原轮历史保留。

2026-10-22 当前Phase4 G1：GPT Work对固定e40ddd0009cc30664c3a0fe0b74c4a497a541d77判PLAN BLOCKED（001 High、002 Medium仍OPEN）。本轮仅修订目标/delta双lot门禁、不动/全平例外及收窄取整性质，新增独立反例，待新固定SHA主审复核；详docs/audits/phase-4/DEVELOPER_RESPONSE.md。Phase3受限发布不变，不写P4业务、无合并/标签/部署/实盘/P5；以下旧状态为历史。

2026-10-22 当前：Phase3已按用户明确受限工程范围ACCEPTED/RELEASED，phase3-baseline/v0.3.0/main基线0a57dccb5618ba08cd3572d6d6b78fec963a3041。金融批准、真实隔离和正式Test延期且未验证；历史复现限软件包/锁/旧Ref/结果重放。本轮仅Phase4的7项（4 MVP、3 Competition Ready）计划/接口/独立答案候选及GPT Work G1预审资料，状态PLAN PRE-REVIEW REQUIRED；P4业务实现、合并发布及P5未授权，无部署/实盘。详docs/audits/phase-4/REVIEW_PACKAGE.md；以下旧状态为历史。

2026-10-22 最新人工决定：Phase3按明确受限工程范围ACCEPTED，PR #5已普通merge 70086a74a632c73a2769ec24901ec47babfa8976（整tree等于批准头2a3400c）。合并后干净SDK578、原20/四及数学91通过；金融批准、真实隔离和正式Test延期，历史复现限软件包/锁/旧Ref/结果重放。发布登记与phase3-baseline/v0.3.0远端main原子同点并核验后为RELEASED，详docs/audits/phase-3/BASELINE.md及publication/。Phase4仅计划预审已授权，主审GPT Work，P4业务实现及P5未授权；无部署/账户/ACL/服务/调度或实盘。旧待验收/未授权文字保留历史，由本决定替代当前状态。

2026-10-22 最新独立复核：**G2 TECHNICAL PASS WITH CONDITIONS / HUMAN ACCEPTANCE PENDING**。GPT Work已对固定9ac5db069287a6e4a095e25ae8c3cc8fa229cded确认001 High、002/003 Medium均CLOSED，无新增阻断代码问题；独立SDK578、原四/旧16+4/91数学/扫描3及双OS各578与原ZIP核验通过。原报告/关闭/26项覆盖/390件hash核验见docs/audits/phase-3/g2-9ac5db0/。真实隔离/正式Test/金融批准/完整历史宿主仍未验证；Phase3未人工验收/发布，无部署、合并、标签或P4。以下旧状态按其原轮次保留。


2026-10-22 G2修复自测完成：**DEVELOPER REPAIR VALIDATED / GPT WORK RECHECK REQUIRED**。修复业务1b4be236e888805f5c4e45357b158fcdb6058df0的干净SDK和双OS各578项、原16/4、原四产品回归、原91数学及3扫描控制通过；实际时钟/fit探针和原ZIP/hash见docs/audits/phase-3/g2-5a5e093/validation-1b4be23/。原1High/2Medium仍待主审确认CLOSED，未部署/金融批准/验收/合并/标签/P4。以下各旧状态按原轮次保留。


2026-10-22 最新G2状态：**GPT Work对固定5a5e093判REQUEST CHANGES（1 High/2 Medium）；修复候选待新固定SHA复核**。G1 PLAN PASS不变。原四失败、封存319项/hash核验、3项开发方处理见docs/audits/phase-3/g2-5a5e093/；不自判CLOSED/验收。实际部署/正式Test/金融批准仍未验证，无合并、标签或P4；以下旧交审状态按其时间保留。


2026-10-22 最新交审状态：**Phase3 IMPLEMENTATION READY FOR GPT WORK G2 / DEVELOPER VERIFIED；未验收、未发布**。G1固定3861及U-001/U-002设计已获用户确认；26项（23MVP/3CR）实现与四主体修复见docs/audits/phase-3/。业务07e7c88745c031feeaee5d1e374a02caada77777的干净SDK、双OS各564项及原16/4通过，原ZIP/45源码/95批信号记录（含缓存引用）/1957冻结文件核验见IMPLEMENTATION_VALIDATION.json。无真实权限部署、正式Test或金融批准，不合并、不打标签、不进入P4；以下旧轮状态按时间保留。


Phase3实际实现入口：`docs/audits/phase-3/IMPLEMENTATION_NOTES.md`、`IMPLEMENTATION_TRACEABILITY.md`、`IMPLEMENTATION_IDENTITY.json`。


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

# 架构决策、冲突及待用户决定事项

2026-10-21 当前修复发布：用户已验收固定 `6858c183ab97e270c9b4852cf1885fb55873327c`，PR #4 已合并 main `93b87b4ad5da5e737973ce8882e5dc9d0b656844`，包版本 **0.1.1**。补丁 **ACCEPTED**；本登记与新标签 `v0.1.1` 远端同点发布并核验后为 **RELEASED**。合并树与获批 head 完全一致，合并后干净 SDK 234 项及未编辑原始外置 16 项通过。原阶段基线标签不移动；历史缺字节 NOT VERIFIED 与指定 GPT Work 代执行事实保留。发布证据：`docs/audits/phase-1/repairs/data-validation/publication-v0.1.1/BASELINE.md`。Phase 2 分支不改，受控纳入及重新验证另办，不进入 Phase 3。以下旧状态仅作历史，以本段和实际远端 Git 为准。

2026-10-21 第二轮补充审查：报告目标是已发布 f579，不是 PR #4。开发方在上一修复 SDK 复现新增 WORK-P1-006–009（16 项外置用例 7 失败/9 通过，旧三项回归保持通过）；现于同一独立修复 PR 按既有 Phase1 数据契约纠正，源代码全套 234 项通过，新完整 SDK、双平台 CI 和原始 ZIP 校验已通过；固定 SHA 独立复核仍待完成。详情 docs/audits/phase-1/repairs/data-validation/round2/。修复版本尚未验收/发布；main、稳定标签和 Phase2 分支不变，不合并、不打标签、不进入Phase3。以下各轮数字/状态保留其时点。

2026-10-21 补充审查修复状态：用户已明确授权“核对、归档并修复，提交独立修复 PR（推荐）”。独立分支 fix/phase-1-data-validation 从已发布 main f579b2c99e762085772de6e70ba1fa98792a7add 起步；三项数据校验缺陷已实现并通过开发方验证，固定 SHA 独立复核待完成，候选版本 0.1.1，尚未验收/发布。原 Phase1 ACCEPTED/RELEASED 历史与标签不变。Phase2 已在另一分支获授权并实施（PR #3，核对头部 947467b9d094905cab0af37ec5cc53f1d187e755），但继承的数据层缺陷须在修复经审查、纳入后重新验证，当前不能给予正常技术通过。该分支不修改 Phase2，不合并、不打标签、不进入 Phase3。最新记录见 docs/audits/phase-1/repairs/data-validation/；以下旧状态为历史，若冲突以本段和实际 Git 为准。

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
