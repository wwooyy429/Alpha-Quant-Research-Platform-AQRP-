# AQRP Phase 0 需求业务分类与编号勘误对照表（开发方提交 Gemini 复核）

日期：2026-10-20（Asia/Shanghai）。作者：开发方 GPT Work。本文件是供 Gemini 独立核对的勘误建议稿，不是 Gemini 已签署的报告，也不是用户验收或发布批准。不覆盖历史审计原文。

## 1. 固定核对对象与计数口径

- 仓库：[Alpha Quant Research Platform](https://github.com/wwooyy429/Alpha-Quant-Research-Platform-AQRP-)。
- Pull Request：[PR #1](https://github.com/wwooyy429/Alpha-Quant-Research-Platform-AQRP-/pull/1)。
- 本表依据的固定证据提交：`1830b152ea4b2497fbfc54d4d506a77e3c2abb5f`。
- Gemini Rev 2 原报告明确审查的提交：`d4c8218315a9152166cbe56fde54384dc99fb094`。这与上述后续证据提交分开登记，不假称 Gemini 已审后续提交。
- 两个提交中的 `docs/requirements.csv` 字节一致；SHA-256：`20dd4e6be7188d3121f3cb361faf8901bc91815a6e9752beb14054a12183f0c1`。

计数必须区分：**12份规定文档、V3.0的66个编号小节、106条正式需求、16个正式需求ID前缀组**。四者属于不同口径，不能相互替代。业务模块可以跨多个需求组，一个需求组也可以覆盖多个模块。

下表业务名称仅解释正式前缀的含义；唯一编号、数量、实施阶段和依赖仍以固定提交的CSV、REQUIREMENTS、TRACEABILITY及ROADMAP为依据。P0表示设计/治理交付；这些规则后续持续适用，不表示后续业务代码已实现。POST7表示Phase 7后另行授权的扩展，不能当作已排入P1–P7。

## 2. 与正式CSV逐组一致的业务分类表

| 正式前缀 | 业务分类与职责 | 正式ID范围 | 条数 | CSV规定的交付阶段 |
|---|---|---|---:|---|
| ARCH | 架构与接口治理：固定技术架构、模块解耦、技术栈选择、接口版本与兼容性 | ARCH-001–ARCH-003 | 3 | 全部P0设计；后续各阶段遵守 |
| BT | 独立回测、模拟执行、账本与绩效：事件时序、订单、撮合、费用、公司行动、现金持仓、估值、绩效及替换验证 | BT-001–BT-010 | 10 | 全部P5 |
| DATA | 数据与时间契约：证券标识、单位、PIT、日历、复权、历史股票池、质量、快照、存储及后续数据适配 | DATA-001–DATA-013 | 13 | P1：001–009、011；P3：012；P7：013；POST7：010 |
| ENV | 开发环境与工程基础：精确依赖/环境固定、CI，以及风险分层覆盖率目标设计 | ENV-001–ENV-003 | 3 | P0：003；P1：001–002 |
| EXP | 实验与审批证据管理：run_id、不可变配置、版本血缘、全部试验、比较复现、通过标准及审批证据 | EXP-001–EXP-004 | 4 | 全部P3；P5/P6/P7后续复用、展示或集成 |
| EXT | 后续高级研究扩展：GPT候选生成、公式检查、批评估、去重、稳健筛选、排序与审批 | EXT-001 | 1 | POST7；当前Deferred |
| FACTOR | 因子协议、Registry及因子生命周期：元数据、信号结构、注册/替换/回滚、基础因子、审批隔离及扩展 | FACTOR-001–FACTOR-012 | 12 | P2：001–006、010–012；P3：007、009；POST7：008 |
| GOV | 项目治理与阶段门禁：范围、文档、需求追踪、阶段授权、Git/PR、独立审查、缺陷闭环及主干发布门禁 | GOV-001–GOV-010 | 10 | 全部P0设计；阶段与授权规则持续适用 |
| INT | 跨模块集成、完整验收及比赛适配：研究链、交易模拟链、模式隔离、环境复现、完整替换与比赛规则适配 | INT-001–INT-006 | 6 | P3：001；P5：002；P7：003–006 |
| PORT | 组合构建：目标权重/仓位、单多因子、等权/分数权、Long-only/Long-short及优化扩展 | PORT-001–PORT-004 | 4 | P4：001–003；POST7：004 |
| QA | 质量保证与独立核对：Golden设计、分阶段测试、不变量、独立答案、专项审计、审查资料与人工验收证据 | QA-001–QA-007 | 7 | P0：001、005–007；P1：002；P3：004；P5：003 |
| RESEARCH | 因子研究处理与编排：计算、预处理、算子、中性化、处理阶段、相关/冗余、缓存与研究流程替换 | RESEARCH-001–RESEARCH-009 | 9 | 全部P3 |
| RISK | 独立风险约束：单票、gross/net、杠杆、换手、行业/Beta、可交易性、借券及不可行组合拒绝 | RISK-001–RISK-004 | 4 | 全部P4；P5接入实际模拟订单与账户流程 |
| SEC | 安全与执行权限：新因子代码审查隔离、凭证保护、真实交易权限、独立审查者执行权限边界 | SEC-001–SEC-004 | 4 | P0：004；P1：002；P2：001；POST7：003（真实执行当前Unsupported） |
| UI | 网页呈现与统一服务交互：Dashboard、因子库、研究、回测、实验、设置、CLI/网页一致性、任务状态与日志 | UI-001–UI-008 | 8 | 全部P6；底层服务/研究CLI按各自阶段提供 |
| VALID | 统计验证、样本外隔离与过拟合控制：IC/Rank IC、分层/衰减、显著性、数据划分、Test封存、多重检验及批准证据 | VALID-001–VALID-008 | 8 | 全部P3 |
| **合计** | **16个正式前缀组；每条正式需求仅按ID前缀计入一次** | — | **106** | 各条依赖保持CSV原值 |

同组条目的阶段并不必然相同；例如DATA、FACTOR、QA、SEC均跨阶段。不能用“模块主要在P1/P2完成”的概括覆盖其中较晚交付或POST7条目。因子审批仍遵守研究验证与策略执行批准分离的契约，不因某条目阶段为P3而声称P5策略证据已具备。

## 3. 原业务分类附录的具体勘误对照

| 原表述或分类方式 | 正确表述与映射 | 核对依据 |
|---|---|---|
| “12组需求” | 正式CSV为16个ID前缀组；此项Rev 2已明确纠正 | 上表16组，合计106条 |
| FREG、VAL、BACK作为正式前缀 | 撤销；实际前缀分别使用FACTOR、VALID、BT，仍须逐条核对语义，不能只按名称机械替换 | 正式ID清单；此项Rev 2已纠正 |
| 将原附录16行业务能力称为“正式16组”逐项对照 | 改为“业务能力概览”，声明与正式ID组是多对多关系；正式分组核对采用本表第2节 | 模块划分与需求编号分组属于不同视图 |
| 回测引擎、订单生命周期、账本、绩效分别算作四个正式需求组 | 可作为四项能力展示，但正式归属均为BT；事件BT-001–002、订单BT-003–004、账本/行动/空头BT-005–007、估值报告BT-008、绩效BT-009、完整替换BT-010 | BT-001–010；BACKTEST_CONTRACT |
| “Alpha Validation”同时包含横截面预处理与统计验证，另列OOS却未给出正式分组关系 | 预处理/算子/中性化属于RESEARCH；统计与OOS同属VALID；试验及审批记录还关联EXP。不能把OOS当作另一个独立CSV前缀 | RESEARCH-001–009、VALID-001–008、EXP-001–004 |
| 实验管理仅Phase5–7 | EXP-001–004首次交付全部为P3；P5复用模拟记录，P6由UI-005呈现，P7执行完整复现/集成验收 | EXP-001–004；ARCHITECTURE、ROADMAP |
| 组合使用“等权/分位数加权” | 正式PORT-002为“等权/分数权”；分位数组收益属于VALID-002的研究验证，不等于组合权重规则 | PORT-002、VALID-002、INTERFACES |
| “绩效统计与归因”暗示已要求完整归因系统 | 使用“绩效统计与多空贡献”；列明BT-009已有指标，不将完整行业/风格/Brinson等归因系统推定为现有需求 | BT-008–009；不得增加未批准范围 |
| 将环境与安全合为一个正式组，将治理与QA合为一个正式组 | 能力概览可以合并展示，但正式CSV仍分别计ENV、SEC、GOV、QA四组 | 第2节对应四行 |
| 单列比赛适配主题，却未明确INT与EXT独立需求组 | 比赛适配具体关联INT-006与DATA-013，实施P7；INT还覆盖P3/P5/P7的集成与验收。EXT独立为POST7高级研究扩展，不属于比赛适配组 | INT-001–006、DATA-013、EXT-001 |
| 数据仅P1、因子仅P2、组合仅P4 | 只能描述基础能力的主要实施阶段；完整需求分组阶段须保留DATA的P3/P7/POST7、FACTOR的P3/POST7、PORT的POST7 | 第2节分条阶段映射 |

## 4. 同步澄清的接口与需求引用

- 因子原始输出是SignalBatch。真实字段包括 `signal_time`、`security_id`、`factor_value`，以及 `available_at`、因子/快照/运行版本和有效性等元数据；三字段摘要不是完整schema。不得将示意的 `event_time/asset_id/raw_signal` 写成正式输出字段。数值预处理属于P3 Research，插件输出原始因子值。
- QA-001是Golden Dataset设计；通用分阶段测试为QA-002；CI建立为ENV-002。不能以QA-001概括全部CI/测试职责。
- DATA-005具体为历史股票池、停牌、退市及双时间；通用时间戳/PIT规则主要关联DATA-002，日历/session_date关联DATA-003。必须区分带时区timestamp字段与合法交易日日期键。
- P2只验证注册/替换/接口兼容，P3验证完整研究替换，P5验证组合回测替换，P6验证CLI/网页一致，P7验证完整端到端替换；不得因分类概括提前实施后续模块。

## 5. 请 Gemini 给出的复核回应

请从固定SHA读取正式CSV与契约，独立核对本表的16组、106条及逐条阶段；不要仅根据本文件文字确认通过。请另行出具补充勘误说明，逐项标记“同意 / 不同意及理由 / 尚未验证”，明确：

1. 组数和虚构前缀两项原错误已纠正；正式分组采用第2节，历史业务概览仅保留为多对多视图。
2. EXP首次交付为P3；等权/分数权及RESEARCH/VALID职责按正式契约纠正。
3. INT、EXT及跨阶段/POST7需求没有被遗漏或静默改期；本表不新增、删除或修改正式需求。
4. 本表为开发方建议，确认前不得记为Gemini已经签署；若审查后续证据提交，应在新说明中明确完整SHA及实际核对范围。
5. 分类勘误闭环、设计审计建议、用户ACCEPTED与main RELEASED分别登记。当前本文件不改变F-001 OPEN/GATED、NOT RELEASED及PHASE 1 BLOCKED，不构成合并、打标签或下一阶段授权。

历史原报告与原勘误表应保持字节不变，通过新增勘误说明追溯修订，不覆盖原件。

## 6. 固定版本资料链接

- [正式CSV](https://github.com/wwooyy429/Alpha-Quant-Research-Platform-AQRP-/blob/1830b152ea4b2497fbfc54d4d506a77e3c2abb5f/docs/requirements.csv)
- [需求定义](https://github.com/wwooyy429/Alpha-Quant-Research-Platform-AQRP-/blob/1830b152ea4b2497fbfc54d4d506a77e3c2abb5f/docs/REQUIREMENTS.md)
- [双向追踪与依赖](https://github.com/wwooyy429/Alpha-Quant-Research-Platform-AQRP-/blob/1830b152ea4b2497fbfc54d4d506a77e3c2abb5f/docs/TRACEABILITY.md)
- [阶段计划](https://github.com/wwooyy429/Alpha-Quant-Research-Platform-AQRP-/blob/1830b152ea4b2497fbfc54d4d506a77e3c2abb5f/docs/ROADMAP.md)
- [架构职责](https://github.com/wwooyy429/Alpha-Quant-Research-Platform-AQRP-/blob/1830b152ea4b2497fbfc54d4d506a77e3c2abb5f/docs/ARCHITECTURE.md)
- [接口契约](https://github.com/wwooyy429/Alpha-Quant-Research-Platform-AQRP-/blob/1830b152ea4b2497fbfc54d4d506a77e3c2abb5f/docs/INTERFACES.md)
- [开发方Rev 2核对记录](https://github.com/wwooyy429/Alpha-Quant-Research-Platform-AQRP-/blob/1830b152ea4b2497fbfc54d4d506a77e3c2abb5f/docs/audits/phase-0/gemini/REV2_RECONCILIATION.md)

本文件为仓库外交付件；上述固定SHA是本表的核对依据，不是本文件已入库的声明。
