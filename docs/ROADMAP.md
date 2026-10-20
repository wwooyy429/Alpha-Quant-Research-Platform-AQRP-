# Phase 0–7 开发及 Gemini 交接计划

Phase0已发布；用户现已授权Phase1开发及合成数据/Python3.13.16范围，阶段计划见audits/phase-1/PLAN.md。后续阶段仍为提案，需求ID/等级/依赖以REQUIREMENTS/TRACEABILITY为准。每阶段须核对基线/授权、提交计划/接口/答案供Gemini预审，阻断问题解决后才实施。

| Phase / 状态 | 范围、输入前提及允许文件 | 输出与适用验收 / 禁止越界 |
|---|---|---|
| 0 / RELEASED | V3.0–3.2；用户ACCEPTED，PR#1已合并，phase0-baseline固定7de1d0e，Gemini Gate PASS及F-001 CLOSED | 规范/契约/Golden设计与审计基线已发布；本次仅追加报告归档，不开发业务包/网页/引擎 |
| 1 / AUTHORIZED；PLAN REVIEW REQUIRED | P0已RELEASED，用户已授权合成数据/通用契约并选Python3.13.16；从核实main 502c693建立feature/phase-1-data-system；业务实施前仍需本阶段Gemini预审 | 14项P1需求：core/data、快照/PIT/单位/日历/行动/质量/合成数据、环境锁/CI及测试；先审PLAN/DATA_IMPLEMENTATION_SPEC/GOLDEN_REFERENCE，未预审不先写业务代码 |
| 2 / PLANNED | P1验收+P2授权；Data API可用；未来 factors 与 tests/factors | Factor API/Registry、元数据/参数/版本、Momentum/Reversal/Volume、注册/替换/回滚/major兼容；不要求研究/回测E2E |
| 3 / PLANNED | P2验收+P3授权；统计/样本外协议冻结；research,validation,experiments,研究services/CLI与报告 | 处理链/算子/Price-Volume、IC/Rank/ICIR/分组/衰减/相关/显著性/OOS、实验记录、完整研究链替换；不调用未实现组合/回测。因子仅ResearchValidated |
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
