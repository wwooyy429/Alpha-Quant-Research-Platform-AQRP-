# Phase 0–7 开发及 Gemini 交接计划

当前仅 P0 获授权；以下均为阶段提案，不是启动指令。需求 ID、等级及细化依赖以 REQUIREMENTS/TRACEABILITY 为准。每阶段必须先读正式文档、检查 Git、核对上一阶段验收和本阶段明确授权，再提交阶段计划、测试预期和接口供 Gemini 预审；阻断设计问题解决后才实施。

| Phase / 状态 | 范围、输入前提及允许文件 | 输出与适用验收 / 禁止越界 |
|---|---|---|
| 0 / REVIEW REQUIRED | V3.0–3.2；仅文档、来源、审计资料与文档核查工具 | 需求、架构、所有契约、Golden设计、专项审计及模板；不开发业务包/网页/引擎 |
| 1 / PLANNED | P0人工批准+P1启动授权；数据契约和环境/profile决定；未来 src/aqrp/core,data 与 tests/data、CI/锁文件 | 骨架、精确依赖、DuckDB/Parquet、合成OHLCV、加载清洗/PIT/日历/标准答案、pytest/CI；不实现因子研究或撮合 |
| 2 / PLANNED | P1验收+P2授权；Data API可用；未来 factors 与 tests/factors | Factor API/Registry、元数据/参数/版本、Momentum/Reversal/Volume、注册/替换/回滚/major兼容；不要求研究/回测E2E |
| 3 / PLANNED | P2验收+P3授权；统计/样本外协议冻结；research,validation,experiments,研究services/CLI与报告 | 处理链/算子/Price-Volume、IC/Rank/ICIR/分组/衰减/相关/显著性/OOS、实验记录、完整研究链替换；不调用未实现组合/回测。因子仅ResearchValidated |
| 4 / PLANNED | P3验收+P4授权；风险/交易约束profile批准；portfolio,risk | 单/多因子、等权/分数权、long-only/short、单票/gross/net/杠杆/行业/Beta/换手/借券/不可行测试；账户输入用明确夹具，不声称已撮合 |
| 5 / PLANNED | P4验收+P5授权；事件及账户/profile批准；backtest,execution,performance与模拟services/CLI | 订单/部分成交/拒绝取消/成本滑点/流动性/交收/行动/账本/净值/绩效、独立资金答案、组合回测替换；策略批准需此阶段证据；不提前网页 |
| 6 / PLANNED | P5验收+P6授权；services/CLI已可运行；ui与对应适配测试 | 六页面、任务/错误/日志/图表、因子选择/版本权重、CLI/服务/网页同配置研究及回测一致；不再写核心算法 |
| 7 / PLANNED | P6验收+P7授权；全模块可用；integration/e2e、competition、操作/部署文档 | 完整因子替换、双模式隔离、完整回归/泄漏审计、Gemini代码审查、干净环境CLI/网页运行与比赛规则映射；规则未知时通用模拟验收和具体比赛阻断分别记录 |

每个阶段的禁止范围是表中本阶段及已验收回归范围之外的业务新增；因接口缺陷必须修改已验收模块时，先记录影响/变更批准和回归范围，不能为了未来阶段验收抢先补模块。

## 每阶段 Gemini 审查时点

1. **实施前**：阶段计划、需求ID、允许/禁止文件、接口、预期答案、风险及标准送 Gemini。P0 当前提供全套待审提案，不声称已完成预审。
2. **自测后**：固定 Commit SHA + PR + Review Package，Gemini 阅读该版本实际文档/代码及原始证据；P0 审设计，P1数据，P2插件，P3统计/OOS，P4组合/风险，P5时序/账本，P6界面一致性，P7全链/部署/比赛。
3. **修复后**：新 SHA 映射缺陷，重跑受影响及回归测试；Gemini 对新 SHA 复核关键问题。不得沿用旧 SHA 的 PASS 覆盖新实现。
4. **人工验收前**：证据齐全、适用测试及独立审查完成、阻断问题关闭才提交验收申请。尚缺 Gemini 时只能请求审查/决策，不申请正常通过。
5. **人工批准后**：只执行已获授权的合并/版本标签，保存实际结果；即使阶段通过也停止，等待下一阶段单独授权。

## 功能级别

- MVP：数据、基础因子、研究与基础组合/模拟主链、基本网页，以及不可降级的时间/质量/安全治理；跨 P1–P6 实现，P7集成确认，不意味着早期完整交付。
- Competition Ready：V3.0 规定的其余必须能力（如中性化、多空/行业Beta约束、完整页面管理）及比赛适配，在指定 P3–P7 实现；延期须范围变更批准，不能以非MVP自动免验收。
- Advanced Research：更广因子、公式/机器学习、优化、GPT自动挖掘，核心 P7 通过后独立新阶段，当前 Deferred。
- Production Extensions：真实交易和运维扩展，当前 Unsupported，另立需求、审批和安全设计。

因子替换里程碑：P2 Registry/元数据兼容 → P3 完整研究 → P5 组合/风控/撮合/账本 → P6 CLI/UI同核 → P7 固定数据与组合配置的 Momentum→Reversal 全链；每次切换只改因子配置，记录信号/订单变化及底层核心未改的 diff/hash 证据，不要求收益相同。
