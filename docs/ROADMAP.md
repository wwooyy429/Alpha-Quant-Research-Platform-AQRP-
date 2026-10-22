# Phase 0–7 开发及 Gemini 交接计划

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

Phase0已发布；用户现已授权Phase1开发及合成数据/Python3.13.16范围，阶段计划见audits/phase-1/PLAN.md。后续阶段仍为提案，需求ID/等级/依赖以REQUIREMENTS/TRACEABILITY为准。每阶段须核对基线/授权、提交计划/接口/答案供Gemini预审，阻断问题解决后才实施。

| Phase / 状态 | 范围、输入前提及允许文件 | 输出与适用验收 / 禁止越界 |
|---|---|---|
| 0 / RELEASED | V3.0–3.2；用户ACCEPTED，PR#1已合并，phase0-baseline固定7de1d0e，Gemini Gate PASS及F-001 CLOSED | 规范/契约/Golden设计与审计基线已发布；本次仅追加报告归档，不开发业务包/网页/引擎 |
| 1 / ACCEPTED / RELEASED | 用户人工验收及单独合并/标签授权，PR #2已合并；稳定phase1-baseline，详见audits/phase-1/BASELINE.md | 102测试及适用检查通过；历史独立执行/字节限制保留；用户已另行授权Phase2，进入其计划预审 |
| 2 / ACCEPTED / RELEASED | main/phase2-baseline/v0.2.0固定f26255f；合并后417/16/4及原始证据发布核实 | 用户已另行授权P3；真实审查身份/原限制继续保留 |
| 3 / START AUTHORIZED；PLAN BLOCKED | e26主审003/004仅设计CLOSED，001/002/005 OPEN；ff4未被该报告覆盖；新visibility及增长带宽待新SHA主审 | U001/U002具体决定与G1闭环前不业务；部署/金融未验证；P3发布/P4另授权 |
| 4 / PLANNED | P3验收+P4授权；风险/交易约束profile批准；portfolio,risk | 单/多因子、等权/分数权、long-only/short、单票/gross/net/杠杆/行业/Beta/换手/借券/不可行测试；账户输入用明确夹具，不声称已撮合 |
| 5 / PLANNED | P4验收+P5授权；事件及账户/profile批准；backtest,execution,performance与模拟services/CLI | 订单/部分成交/拒绝取消/成本滑点/流动性/交收/行动/账本/净值/绩效、独立资金答案、组合回测替换；策略批准需此阶段证据；不提前网页 |
| 6 / PLANNED | P5验收+P6授权；services/CLI已可运行；ui与对应适配测试 | 六页面、任务/错误/日志/图表、因子选择/版本权重、CLI/服务/网页同配置研究及回测一致；不再写核心算法 |
| 7 / PLANNED | P6验收+P7授权；全模块可用；integration/e2e、competition、操作/部署文档 | 完整因子替换、双模式隔离、完整回归/泄漏审计、Gemini代码审查、干净环境CLI/网页运行与比赛规则映射；规则未知时通用模拟验收和具体比赛阻断分别记录 |

每个阶段的禁止范围是表中本阶段及已验收回归范围之外的业务新增；因接口缺陷必须修改已验收模块时，先记录影响/变更批准和回归范围，不能为了未来阶段验收抢先补模块。

## 每阶段 Gemini 审查时点

1. **实施前**：阶段计划、需求ID、允许/禁止文件、接口、预期答案、风险及标准送Gemini。P0已发布且主干门禁闭环；后续阶段仍分别执行计划预审，不能沿用P0结论代替。
2. **自测后**：固定 Commit SHA + PR + Review Package，Gemini 阅读该版本实际文档/代码及原始证据；P0 审设计，P1数据，P2插件，P3统计/OOS，P4组合/风险，P5时序/账本，P6界面一致性，P7全链/部署/比赛。
3. **修复后**：新 SHA 映射缺陷，重跑受影响及回归测试；Gemini 对新 SHA 复核关键问题。不得沿用旧 SHA 的 PASS 覆盖新实现。
4. **人工验收前**：证据齐全、适用测试及独立审查完成、阻断问题关闭才提交验收申请。尚缺 Gemini 时只能请求审查/决策，不申请正常通过。
5. **人工批准后**：只执行已获授权的合并/版本标签，保存实际结果；Phase0需main稳定内容、phase0-baseline、BASELINE记录及最终SHA/范围核验后才能标RELEASED。即使已RELEASED也停止，等待下一阶段单独授权；审查建议通过或ACCEPTED本身不够启动P1。

## 功能级别

- MVP：数据、基础因子、研究与基础组合/模拟主链、基本网页，以及不可降级的时间/质量/安全治理；跨 P1–P6 实现，P7集成确认，不意味着早期完整交付。
- Competition Ready：V3.0 规定的其余必须能力（如中性化、多空/行业Beta约束、完整页面管理）及比赛适配，在指定 P3–P7 实现；延期须范围变更批准，不能以非MVP自动免验收。
- Advanced Research：更广因子、公式/机器学习、优化、GPT自动挖掘，核心 P7 通过后独立新阶段，当前 Deferred。
- Production Extensions：真实交易和运维扩展，当前 Unsupported，另立需求、审批和安全设计。

因子替换里程碑：P2 Registry/元数据兼容 → P3 完整研究 → P5 组合/风控/撮合/账本 → P6 CLI/UI同核 → P7 固定数据与组合配置的 Momentum→Reversal 全链；每次切换只改因子配置，记录信号/订单变化及底层核心未改的 diff/hash 证据，不要求收益相同。


2026-10-21状态增量：Gemini对380d9f8计划预审PASS，当前Phase1 IMPLEMENTING。原文/证据索引及报告勘误在audits/phase-1/gemini/PRE_REVIEW_EVIDENCE_INDEX.json和DEVELOPER_RESPONSE.md。此状态替代此前等待计划预审描述；验收、main合并、打标、Phase2仍未授权。


2026-10-21实现增量：Phase1计划预审PASS后完成合成数据/通用契约14项实现和102项测试，当前IMPLEMENTATION REVIEW REQUIRED；实际证据和旧失败以audits/phase-1/IMPLEMENTATION_REVIEW_PACKAGE.md及implementation/EVIDENCE_INDEX.json为准。本增量替代此前等待计划预审/尚无业务代码的当前状态描述；初始计划和授权快照保留。main、稳定标签及P0核心契约不变；未验收/未合并/未发布，不进入Phase2。


2026-10-21实现审计接收：Gemini对74bdb92原文PASS并关闭F-002/F-003/F-P1-PRE-001；开发方核对发现500应为1000、数个文件路径及tests/golden独立执行证据表述不符等勘误。报告按字节归档，完整处置见audits/phase-1/IMPLEMENTATION_AUDIT_RESPONSE.md及gemini/IMPLEMENTATION_AUDIT_EVIDENCE_INDEX.json；本次不改业务代码/答案/阈值。当前AUDIT PASS AS REPORTED / REPORT ERRATA CLARIFICATION REQUIRED，尚非ACCEPTED/RELEASED；无合并、标签或Phase2授权。

# Phase 0–7 开发及 Gemini 交接计划

2026-10-21 当前修复发布：用户已验收固定 `6858c183ab97e270c9b4852cf1885fb55873327c`，PR #4 已合并 main `93b87b4ad5da5e737973ce8882e5dc9d0b656844`，包版本 **0.1.1**。补丁 **ACCEPTED**；本登记与新标签 `v0.1.1` 远端同点发布并核验后为 **RELEASED**。合并树与获批 head 完全一致，合并后干净 SDK 234 项及未编辑原始外置 16 项通过。原阶段基线标签不移动；历史缺字节 NOT VERIFIED 与指定 GPT Work 代执行事实保留。发布证据：`docs/audits/phase-1/repairs/data-validation/publication-v0.1.1/BASELINE.md`。Phase 2 分支不改，受控纳入及重新验证另办，不进入 Phase 3。以下旧状态仅作历史，以本段和实际远端 Git 为准。

2026-10-21 第二轮补充审查：报告目标是已发布 f579，不是 PR #4。开发方在上一修复 SDK 复现新增 WORK-P1-006–009（16 项外置用例 7 失败/9 通过，旧三项回归保持通过）；现于同一独立修复 PR 按既有 Phase1 数据契约纠正，源代码全套 234 项通过，新完整 SDK、双平台 CI 和原始 ZIP 校验已通过；固定 SHA 独立复核仍待完成。详情 docs/audits/phase-1/repairs/data-validation/round2/。修复版本尚未验收/发布；main、稳定标签和 Phase2 分支不变，不合并、不打标签、不进入Phase3。以下各轮数字/状态保留其时点。

2026-10-21 补充审查修复状态：用户已明确授权“核对、归档并修复，提交独立修复 PR（推荐）”。独立分支 fix/phase-1-data-validation 从已发布 main f579b2c99e762085772de6e70ba1fa98792a7add 起步；三项数据校验缺陷已实现并通过开发方验证，固定 SHA 独立复核待完成，候选版本 0.1.1，尚未验收/发布。原 Phase1 ACCEPTED/RELEASED 历史与标签不变。Phase2 已在另一分支获授权并实施（PR #3，核对头部 947467b9d094905cab0af37ec5cc53f1d187e755），但继承的数据层缺陷须在修复经审查、纳入后重新验证，当前不能给予正常技术通过。该分支不修改 Phase2，不合并、不打标签、不进入 Phase3。最新记录见 docs/audits/phase-1/repairs/data-validation/；以下旧状态为历史，若冲突以本段和实际 Git 为准。

Phase0已发布；用户现已授权Phase1开发及合成数据/Python3.13.16范围，阶段计划见audits/phase-1/PLAN.md。后续阶段仍为提案，需求ID/等级/依赖以REQUIREMENTS/TRACEABILITY为准。每阶段须核对基线/授权、提交计划/接口/答案供Gemini预审，阻断问题解决后才实施。

| Phase / 状态 | 范围、输入前提及允许文件 | 输出与适用验收 / 禁止越界 |
|---|---|---|
| 0 / RELEASED | V3.0–3.2；用户ACCEPTED，PR#1已合并，phase0-baseline固定7de1d0e，Gemini Gate PASS及F-001 CLOSED | 规范/契约/Golden设计与审计基线已发布；本次仅追加报告归档，不开发业务包/网页/引擎 |
| 1 / ACCEPTED / RELEASED | 用户人工验收及单独合并/标签授权，PR #2已合并；稳定phase1-baseline，详见audits/phase-1/BASELINE.md | 102测试及适用检查通过；历史独立执行/字节限制保留；Phase2未授权，停止等待 |
| 2 / ACCEPTED / RELEASED | main/phase2-baseline/v0.2.0固定f26255f；合并后417/16/4及原始证据发布核实 | 用户已另行授权P3；真实审查身份/原限制继续保留 |
| 3 / START AUTHORIZED；PLAN BLOCKED | e26主审003/004仅设计CLOSED，001/002/005 OPEN；ff4未被该报告覆盖；新visibility及增长带宽待新SHA主审 | U001/U002具体决定与G1闭环前不业务；部署/金融未验证；P3发布/P4另授权 |
| 4 / PLANNED | P3验收+P4授权；风险/交易约束profile批准；portfolio,risk | 单/多因子、等权/分数权、long-only/short、单票/gross/net/杠杆/行业/Beta/换手/借券/不可行测试；账户输入用明确夹具，不声称已撮合 |
| 5 / PLANNED | P4验收+P5授权；事件及账户/profile批准；backtest,execution,performance与模拟services/CLI | 订单/部分成交/拒绝取消/成本滑点/流动性/交收/行动/账本/净值/绩效、独立资金答案、组合回测替换；策略批准需此阶段证据；不提前网页 |
| 6 / PLANNED | P5验收+P6授权；services/CLI已可运行；ui与对应适配测试 | 六页面、任务/错误/日志/图表、因子选择/版本权重、CLI/服务/网页同配置研究及回测一致；不再写核心算法 |
| 7 / PLANNED | P6验收+P7授权；全模块可用；integration/e2e、competition、操作/部署文档 | 完整因子替换、双模式隔离、完整回归/泄漏审计、Gemini代码审查、干净环境CLI/网页运行与比赛规则映射；规则未知时通用模拟验收和具体比赛阻断分别记录 |

每个阶段的禁止范围是表中本阶段及已验收回归范围之外的业务新增；因接口缺陷必须修改已验收模块时，先记录影响/变更批准和回归范围，不能为了未来阶段验收抢先补模块。

## 每阶段 Gemini 审查时点

1. **实施前**：阶段计划、需求ID、允许/禁止文件、接口、预期答案、风险及标准送Gemini。P0已发布且主干门禁闭环；后续阶段仍分别执行计划预审，不能沿用P0结论代替。
2. **自测后**：固定 Commit SHA + PR + Review Package，Gemini 阅读该版本实际文档/代码及原始证据；P0 审设计，P1数据，P2插件，P3统计/OOS，P4组合/风险，P5时序/账本，P6界面一致性，P7全链/部署/比赛。
3. **修复后**：新 SHA 映射缺陷，重跑受影响及回归测试；Gemini 对新 SHA 复核关键问题。不得沿用旧 SHA 的 PASS 覆盖新实现。
4. **人工验收前**：证据齐全、适用测试及独立审查完成、阻断问题关闭才提交验收申请。尚缺 Gemini 时只能请求审查/决策，不申请正常通过。
5. **人工批准后**：只执行已获授权的合并/版本标签，保存实际结果；Phase0需main稳定内容、phase0-baseline、BASELINE记录及最终SHA/范围核验后才能标RELEASED。即使已RELEASED也停止，等待下一阶段单独授权；审查建议通过或ACCEPTED本身不够启动P1。

## 功能级别

- MVP：数据、基础因子、研究与基础组合/模拟主链、基本网页，以及不可降级的时间/质量/安全治理；跨 P1–P6 实现，P7集成确认，不意味着早期完整交付。
- Competition Ready：V3.0 规定的其余必须能力（如中性化、多空/行业Beta约束、完整页面管理）及比赛适配，在指定 P3–P7 实现；延期须范围变更批准，不能以非MVP自动免验收。
- Advanced Research：更广因子、公式/机器学习、优化、GPT自动挖掘，核心 P7 通过后独立新阶段，当前 Deferred。
- Production Extensions：真实交易和运维扩展，当前 Unsupported，另立需求、审批和安全设计。

因子替换里程碑：P2 Registry/元数据兼容 → P3 完整研究 → P5 组合/风控/撮合/账本 → P6 CLI/UI同核 → P7 固定数据与组合配置的 Momentum→Reversal 全链；每次切换只改因子配置，记录信号/订单变化及底层核心未改的 diff/hash 证据，不要求收益相同。


2026-10-21状态增量：Gemini对380d9f8计划预审PASS，当前Phase1 IMPLEMENTING。原文/证据索引及报告勘误在audits/phase-1/gemini/PRE_REVIEW_EVIDENCE_INDEX.json和DEVELOPER_RESPONSE.md。此状态替代此前等待计划预审描述；验收、main合并、打标、Phase2仍未授权。


2026-10-21实现增量：Phase1计划预审PASS后完成合成数据/通用契约14项实现和102项测试，当前IMPLEMENTATION REVIEW REQUIRED；实际证据和旧失败以audits/phase-1/IMPLEMENTATION_REVIEW_PACKAGE.md及implementation/EVIDENCE_INDEX.json为准。本增量替代此前等待计划预审/尚无业务代码的当前状态描述；初始计划和授权快照保留。main、稳定标签及P0核心契约不变；未验收/未合并/未发布，不进入Phase2。


2026-10-21实现审计接收：Gemini对74bdb92原文PASS并关闭F-002/F-003/F-P1-PRE-001；开发方核对发现500应为1000、数个文件路径及tests/golden独立执行证据表述不符等勘误。报告按字节归档，完整处置见audits/phase-1/IMPLEMENTATION_AUDIT_RESPONSE.md及gemini/IMPLEMENTATION_AUDIT_EVIDENCE_INDEX.json；本次不改业务代码/答案/阈值。当前AUDIT PASS AS REPORTED / REPORT ERRATA CLARIFICATION REQUIRED，尚非ACCEPTED/RELEASED；无合并、标签或Phase2授权。
