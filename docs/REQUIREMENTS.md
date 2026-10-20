# 正式需求清单 V3.2（待审）

共 105 条编号需求，规范源表为 `requirements.csv`；本文件由同目录审计编制工具生成。每条均保留输入、输出、来源、优先级、模块、阶段、等级、依赖、验收、设计及未来代码/测试位置。

设计状态 DRAFT_PRESENT 只指设计已编写；能力状态 Planned/Deferred/Unsupported 均表示尚未实现。所有未来代码/测试路径是规划位置，不是现有文件。Phase 0 治理/设计实际文件由交付清单核实，执行强制控制仍未实施。

等级：MVP / Competition Ready / Advanced Research / Production Extensions。优先级 P0 为不可降级治理或关键质量要求，P1 为指定阶段功能，P2 为后续扩展；不能因等级或优先级擅自延期原V3.0必须项。POST7 仅可在核心P7后另行授权。

通过标准均为待审提案；实际数值的业务门槛待 DECISIONS 批准。批准状态变更须附证据而不能直接改表。来源 `§18` 为原文阶段计划，V3.2 `§4.x` 为对应Step。

## GOV-001 · 只执行Phase0，质量顺序及长期平台目标，保留未修订原要求

- 来源：V3.0§1.1;V3.0§1.2;V3.0§1.3;V3.0§22;V3.1§5;V3.2§9；等级：MVP；阶段：0；优先级：P0；模块：governance。
- 输入：V3.0–3.2。输出：正式规范及授权范围。依赖：NONE。
- 验收：无业务实现且不启动P1，未实现如实标注。
- 设计：[契约/方案](PROJECT_CHARTER.md)；拟代码：`docs/PROJECT_CHARTER.md`；拟测试：`docs/audits/phase-0/`。
- 能力状态：Planned；设计状态：DRAFT_PRESENT；实际实现/测试证据：尚无（P0文档证据另见审查包）。

## GOV-002 · 维护规定的12份正式文档及audits/golden/integration/e2e目录

- 来源：V3.0§14.1;V3.0§14.2;V3.2§2；等级：MVP；阶段：0；优先级：P0；模块：governance。
- 输入：原始指令。输出：版本化文档与目录。依赖：GOV-001。
- 验收：全部真实文件存在，后续手册/部署阶段明确。
- 设计：[契约/方案](PROJECT_CHARTER.md)；拟代码：`docs/PROJECT_CHARTER.md`；拟测试：`docs/audits/phase-0/`。
- 能力状态：Planned；设计状态：DRAFT_PRESENT；实际实现/测试证据：尚无（P0文档证据另见审查包）。

## GOV-003 · 唯一需求ID、完整字段、双向追踪及需求覆盖/遗漏/重复/冲突审计

- 来源：V3.0§14.3;V3.0§14.4;V3.0§14.5;V3.1§8；等级：MVP；阶段：0；优先级：P0；模块：governance。
- 输入：原文与设计。输出：需求清单及追踪矩阵。依赖：GOV-001。
- 验收：每条有来源等级阶段依赖验收代码测试状态，原文节与实际文件均可反查。
- 设计：[契约/方案](REQUIREMENTS.md)；拟代码：`docs/REQUIREMENTS.md`；拟测试：`docs/audits/phase-0/`。
- 能力状态：Planned；设计状态：DRAFT_PRESENT；实际实现/测试证据：尚无（P0文档证据另见审查包）。

## GOV-004 · 每阶段计划/范围/依赖/测试/审查/人工批准，合法状态与禁止越级

- 来源：V3.0§15.1;V3.0§15.2;V3.0§15.3;V3.0§15.4;V3.0§15.5;V3.0§18;V3.1§1；等级：MVP；阶段：0；优先级：P0；模块：governance。
- 输入：阶段授权及依赖。输出：独立阶段计划。依赖：GOV-001。
- 验收：仅明确批准推进，验收与模块可用性一致。
- 设计：[契约/方案](ROADMAP.md)；拟代码：`docs/ROADMAP.md`；拟测试：`docs/audits/phase-0/`。
- 能力状态：Planned；设计状态：DRAFT_PRESENT；实际实现/测试证据：尚无（P0文档证据另见审查包）。

## GOV-005 · 每阶段A–F报告、停止等待、阶段验收不等于下阶段授权

- 来源：V3.0§19;V3.2§4.7;V3.2§4.9；等级：MVP；阶段：0；优先级：P0；模块：governance。
- 输入：阶段成果及证据。输出：验收报告及授权记录。依赖：GOV-004。
- 验收：无用户记录不标ACCEPTED/RELEASED，无Gemini审查不申请正常通过。
- 设计：[契约/方案](ACCEPTANCE.md)；拟代码：`docs/ACCEPTANCE.md`；拟测试：`docs/audits/phase-0/`。
- 能力状态：Planned；设计状态：DRAFT_PRESENT；实际实现/测试证据：尚无（P0文档证据另见审查包）。

## GOV-006 · feature/fix/audit/main分工、PR、授权合并发布标签与可回滚

- 来源：V3.0§17.1;V3.0§17.2;V3.0§17.3;V3.2§3;V3.2§4.8；等级：MVP；阶段：0；优先级：P0；模块：governance。
- 输入：固定提交及批准。输出：可追溯版本/回滚记录。依赖：GOV-005。
- 验收：无实际合并标签不称发布，不删历史掩盖错误。
- 设计：[契约/方案](ACCEPTANCE.md)；拟代码：`docs/ACCEPTANCE.md`；拟测试：`docs/audits/phase-0/`。
- 能力状态：Planned；设计状态：DRAFT_PRESENT；实际实现/测试证据：尚无（P0文档证据另见审查包）。

## GOV-007 · 跨对话先读规定文档及Git，GitHub与可信记录为事实源，冲突先报告

- 来源：V3.0§21;V3.2§2；等级：MVP；阶段：0；优先级：P0；模块：governance。
- 输入：文档和实际Git。输出：当前授权/稳定版核查。依赖：GOV-002。
- 验收：记录未提交与未同步状态，不凭记忆猜测。
- 设计：[契约/方案](PROJECT_CHARTER.md)；拟代码：`docs/PROJECT_CHARTER.md`；拟测试：`docs/audits/phase-0/`。
- 能力状态：Planned；设计状态：DRAFT_PRESENT；实际实现/测试证据：尚无（P0文档证据另见审查包）。

## GOV-008 · GPT开发、Gemini独立计划预审/固定SHA复审、15项ReviewPackage与审计模板

- 来源：V3.0§16;V3.2§1;V3.2§4;V3.2§5;V3.2§7；等级：MVP；阶段：0；优先级：P0；模块：governance。
- 输入：计划/指定SHA/原始证据。输出：独立审查材料及报告。依赖：GOV-004。
- 验收：每阶段两次交接和修复复核明确，不用GPT自查代Gemini。
- 设计：[契约/方案](ACCEPTANCE.md)；拟代码：`docs/ACCEPTANCE.md`；拟测试：`docs/audits/phase-0/`。
- 能力状态：Planned；设计状态：DRAFT_PRESENT；实际实现/测试证据：尚无（P0文档证据另见审查包）。

## GOV-009 · 缺陷严重度/复现/预期实际/修复SHA/独立复核，保留争议及原报告

- 来源：V3.0§16;V3.0§20;V3.2§4.6;V3.2§6;V3.2§8；等级：MVP；阶段：0；优先级：P0；模块：governance。
- 输入：审查发现。输出：缺陷闭环及阻断判断。依赖：GOV-008。
- 验收：Critical/High未关闭禁止正常通过，Medium按金融安全判断。
- 设计：[契约/方案](ACCEPTANCE.md)；拟代码：`docs/ACCEPTANCE.md`；拟测试：`docs/audits/phase-0/`。
- 能力状态：Planned；设计状态：DRAFT_PRESENT；实际实现/测试证据：尚无（P0文档证据另见审查包）。

## ARCH-001 · 固定PythonCore/Streamlit/Registry/独立回测，13模块明确边界和依赖图

- 来源：V3.0§2.1;V3.0§2.3;V3.0§9；等级：MVP；阶段：0；优先级：P0；模块：architecture。
- 输入：业务目标。输出：模块架构及责任。依赖：GOV-001。
- 验收：插件不动资金、UI不撮合、报告不改持仓、回测不识别具体因子。
- 设计：[契约/方案](ARCHITECTURE.md)；拟代码：`docs/ARCHITECTURE.md`；拟测试：`docs/audits/phase-0/`。
- 能力状态：Planned；设计状态：DRAFT_PRESENT；实际实现/测试证据：尚无（P0文档证据另见审查包）。

## ARCH-002 · 优先技术栈及大型框架/微服务/后期库变更审批

- 来源：V3.0§2.2；等级：MVP；阶段：0；优先级：P0；模块：architecture。
- 输入：技术要求。输出：受控选型。依赖：ARCH-001。
- 验收：未批准不引入额外框架，静态类型/结构校验按风险评估。
- 设计：[契约/方案](ARCHITECTURE.md)；拟代码：`docs/ARCHITECTURE.md`；拟测试：`docs/audits/phase-0/`。
- 能力状态：Planned；设计状态：DRAFT_PRESENT；实际实现/测试证据：尚无（P0文档证据另见审查包）。

## ARCH-003 · 接口统一输入输出类型单位时间异常和SemVer，变更影响/兼容测试

- 来源：V3.0§2.4;V3.1§2;V3.1§3；等级：MVP；阶段：0；优先级：P0；模块：architecture。
- 输入：各模块边界。输出：版本化契约。依赖：ARCH-001。
- 验收：无隐式单位或静默不兼容升级。
- 设计：[契约/方案](INTERFACES.md)；拟代码：`docs/INTERFACES.md`；拟测试：`docs/audits/phase-0/`。
- 能力状态：Planned；设计状态：DRAFT_PRESENT；实际实现/测试证据：尚无（P0文档证据另见审查包）。

## DATA-001 · 稳定security_id及市场/别名，OHLCV/amount标准化，原单位可追溯

- 来源：V3.0§4.1;V3.0§4.3;V3.1§2；等级：MVP；阶段：1；优先级：P1；模块：data。
- 输入：标准化源记录。输出：市场隔离日频数据。依赖：ARCH-003。
- 验收：同ticker不同市场不混，价格/股数/金额单位正确。
- 设计：[契约/方案](DATA_CONTRACT.md)；拟代码：`src/aqrp/data/`；拟测试：`tests/data/test_data_001.py`。
- 能力状态：Planned；设计状态：DRAFT_PRESENT；实际实现/测试证据：尚无（P0文档证据另见审查包）。

## DATA-002 · UTC带时区event_time/available_at/decision_time及PIT修订查询

- 来源：V3.0§4.2;V3.0§4.3;V3.1§2；等级：MVP；阶段：1；优先级：P1；模块：data。
- 输入：时间约束/历史版本。输出：当时可见DataView。依赖：DATA-001。
- 验收：未来修订/晚到数据不进入过去决策，未知历史可用性阻断正式PIT。
- 设计：[契约/方案](DATA_CONTRACT.md)；拟代码：`src/aqrp/data/`；拟测试：`tests/data/test_data_002.py`。
- 能力状态：Planned；设计状态：DRAFT_PRESENT；实际实现/测试证据：尚无（P0文档证据另见审查包）。

## DATA-003 · 日历/交易session/本地日期/夏令时/半日休市及确定排序

- 来源：V3.0§4.1;V3.0§4.4;V3.0§18；等级：MVP；阶段：1；优先级：P1；模块：data。
- 输入：版本化日历。输出：跨市场一致时间映射。依赖：DATA-002。
- 验收：非交易日与边界正确，UTC日期不替代本地session。
- 设计：[契约/方案](DATA_CONTRACT.md)；拟代码：`src/aqrp/data/`；拟测试：`tests/data/test_data_003.py`。
- 能力状态：Planned；设计状态：DRAFT_PRESENT；实际实现/测试证据：尚无（P0文档证据另见审查包）。

## DATA-004 · RAW和PIT复权视图、分红/拆股/行动数据不重复计收益

- 来源：V3.0§4.1;V3.0§4.4;V3.1§2；等级：MVP；阶段：1；优先级：P1；模块：data。
- 输入：原价及行动。输出：版本化复权视图。依赖：DATA-002。
- 验收：未来行动不回填历史，撮合永用RAW。
- 设计：[契约/方案](DATA_CONTRACT.md)；拟代码：`src/aqrp/data/`；拟测试：`tests/data/test_data_004.py`。
- 能力状态：Planned；设计状态：DRAFT_PRESENT；实际实现/测试证据：尚无（P0文档证据另见审查包）。

## DATA-005 · 历史股票池/停牌/退市及生效和可用双时间

- 来源：V3.0§4.1;V3.0§4.4;V3.1§2；等级：MVP；阶段：1；优先级：P1；模块：data。
- 输入：成员及证券状态。输出：Universe/StatusView。依赖：DATA-002。
- 验收：保留退市证券，禁止用当前股票池过滤历史。
- 设计：[契约/方案](DATA_CONTRACT.md)；拟代码：`src/aqrp/data/`；拟测试：`tests/data/test_data_005.py`。
- 能力状态：Planned；设计状态：DRAFT_PRESENT；实际实现/测试证据：尚无（P0文档证据另见审查包）。

## DATA-006 · 缺失/重复/异常/零量/非法价格/错位/历史不足明确语义

- 来源：V3.0§4.4;V3.1§2；等级：MVP；阶段：1；优先级：P1；模块：data。
- 输入：原始记录。输出：质量报告及隔离数据。依赖：DATA-001。
- 验收：不静默删大量记录、不缺失填零、不跨证券填充。
- 设计：[契约/方案](DATA_CONTRACT.md)；拟代码：`src/aqrp/data/`；拟测试：`tests/data/test_data_006.py`。
- 能力状态：Planned；设计状态：DRAFT_PRESENT；实际实现/测试证据：尚无（P0文档证据另见审查包）。

## DATA-007 · 不可变数据快照、分片与manifest哈希、schema/日历/行动版本

- 来源：V3.0§4.3;V3.0§13;V3.1§2;V3.1§7；等级：MVP；阶段：1；优先级：P1；模块：data。
- 输入：Parquet与元数据。输出：可验证snapshot_id。依赖：DATA-001。
- 验收：修改或损坏被识别，更正另建版本。
- 设计：[契约/方案](DATA_CONTRACT.md)；拟代码：`src/aqrp/data/`；拟测试：`tests/data/test_data_007.py`。
- 能力状态：Planned；设计状态：DRAFT_PRESENT；实际实现/测试证据：尚无（P0文档证据另见审查包）。

## DATA-008 · DuckDB/Parquet加载清洗及合成OHLCV基础

- 来源：V3.0§18;V3.0§2.2；等级：MVP；阶段：1；优先级：P1；模块：data。
- 输入：固定合成输入。输出：可复现标准数据。依赖：DATA-001;DATA-007。
- 验收：干净环境加载并与独立数据答案一致，合成不冒充真实源。
- 设计：[契约/方案](DATA_CONTRACT.md)；拟代码：`src/aqrp/data/`；拟测试：`tests/data/test_data_008.py`。
- 能力状态：Planned；设计状态：DRAFT_PRESENT；实际实现/测试证据：尚无（P0文档证据另见审查包）。

## DATA-009 · 未来数据变更/PIT修订/股票池时间测试，P2/P3扩展信号链

- 来源：V3.0§4.5;V3.0§11.2；等级：MVP；阶段：1；优先级：P1；模块：data。
- 输入：固定cutoff及变更集。输出：不泄漏证据。依赖：DATA-002。
- 验收：历史可见投影不变，正向控制会变化；不只依赖mutation。
- 设计：[契约/方案](DATA_CONTRACT.md)；拟代码：`src/aqrp/data/`；拟测试：`tests/data/test_data_009.py`。
- 能力状态：Planned；设计状态：DRAFT_PRESENT；实际实现/测试证据：尚无（P0文档证据另见审查包）。

## DATA-010 · 财务等扩展数据PIT公告/修订及字段契约

- 来源：V3.0§4.1;V3.0§4.2;V3.0§3.4；等级：Advanced Research；阶段：POST7；优先级：P2；模块：data。
- 输入：财报/其他数据。输出：扩展DataView。依赖：DATA-002。
- 验收：财报期末不等于可用时点，单独审批。
- 设计：[契约/方案](DATA_CONTRACT.md)；拟代码：`src/aqrp/data/`；拟测试：`tests/data/test_data_010.py`。
- 能力状态：Deferred；设计状态：DRAFT_PRESENT；实际实现/测试证据：尚无（P0文档证据另见审查包）。

## DATA-011 · 货币、最小单位、Decimal精度/scale及价格/成交量换算

- 来源：V3.1§2；等级：MVP；阶段：1；优先级：P1；模块：data。
- 输入：源单位/profile。输出：统一金融单位。依赖：DATA-001。
- 验收：跨币种未实现明确拒绝，金额不经float记账。
- 设计：[契约/方案](DATA_CONTRACT.md)；拟代码：`src/aqrp/data/`；拟测试：`tests/data/test_data_011.py`。
- 能力状态：Planned；设计状态：DRAFT_PRESENT；实际实现/测试证据：尚无（P0文档证据另见审查包）。

## DATA-012 · PIT行业/市值/风险暴露数据接口及缺失语义

- 来源：V3.0§4.4;V3.0§7.3；等级：Competition Ready；阶段：3；优先级：P1；模块：data。
- 输入：分类/暴露版本。输出：研究风险可用暴露。依赖：DATA-002。
- 验收：不拿最新行业回填历史，缺失不视为0。
- 设计：[契约/方案](DATA_CONTRACT.md)；拟代码：`src/aqrp/data/`；拟测试：`tests/data/test_data_012.py`。
- 能力状态：Planned；设计状态：DRAFT_PRESENT；实际实现/测试证据：尚无（P0文档证据另见审查包）。

## DATA-013 · 真实比赛数据源映射、授权/规则和能力边界

- 来源：V3.0§4.1;V3.0§18;V3.1§5；等级：Competition Ready；阶段：7；优先级：P1；模块：competition。
- 输入：用户选定源及比赛规范。输出：来源明确的数据适配。依赖：DATA-008;INT-006。
- 验收：未知源/规则保持外部待决，不假称真实接入。
- 设计：[契约/方案](DATA_CONTRACT.md)；拟代码：`src/aqrp/competition/`；拟测试：`tests/competition/test_data_013.py`。
- 能力状态：Planned；设计状态：DRAFT_PRESENT；实际实现/测试证据：尚无（P0文档证据另见审查包）。

## FACTOR-001 · 统一Factor协议及12项元数据、参数schema、数据与API兼容声明

- 来源：V3.0§3.1;V3.0§3.3；等级：MVP；阶段：2；优先级：P1；模块：factors。
- 输入：FactorSpec/DataView/Context。输出：只读确定性信号。依赖：DATA-002;DATA-008。
- 验收：必填字段/窗口/频率/方向/可用时间完整、无账户或网络副作用。
- 设计：[契约/方案](INTERFACES.md)；拟代码：`src/aqrp/factors/`；拟测试：`tests/factors/test_factor_001.py`。
- 能力状态：Planned；设计状态：DRAFT_PRESENT；实际实现/测试证据：尚无（P0文档证据另见审查包）。

## FACTOR-002 · 信号时间/证券/ID版本/值、快照参数任务/可用时间/有效性及唯一键

- 来源：V3.0§3.2；等级：MVP；阶段：2；优先级：P1；模块：factors。
- 输入：计算输出。输出：SignalBatch。依赖：FACTOR-001。
- 验收：重复幂等而冲突失败，血缘完整。
- 设计：[契约/方案](INTERFACES.md)；拟代码：`src/aqrp/factors/`；拟测试：`tests/factors/test_factor_002.py`。
- 能力状态：Planned；设计状态：DRAFT_PRESENT；实际实现/测试证据：尚无（P0文档证据另见审查包）。

## FACTOR-003 · 注册/resolve/兼容校验/停用/精确版本/回滚/参数校验

- 来源：V3.0§2.1;V3.0§3.5;V3.1§1；等级：MVP；阶段：2；优先级：P1；模块：factors。
- 输入：审查代码与精确FactorRef。输出：固定Registry记录。依赖：FACTOR-001;SEC-001。
- 验收：同ID版本异内容拒绝，回滚只选已批准兼容版本。
- 设计：[契约/方案](INTERFACES.md)；拟代码：`src/aqrp/factors/`；拟测试：`tests/factors/test_factor_003.py`。
- 能力状态：Planned；设计状态：DRAFT_PRESENT；实际实现/测试证据：尚无（P0文档证据另见审查包）。

## FACTOR-004 · Momentum基础因子

- 来源：V3.0§3.4;V3.0§18；等级：MVP；阶段：2；优先级：P1；模块：factors。
- 输入：L+1个有效session收盘。输出：L期收益信号。依赖：FACTOR-002。
- 验收：121/100−1=.21且窗口不跨股票。
- 设计：[契约/方案](INTERFACES.md)；拟代码：`src/aqrp/factors/`；拟测试：`tests/factors/test_factor_004.py`。
- 能力状态：Planned；设计状态：DRAFT_PRESENT；实际实现/测试证据：尚无（P0文档证据另见审查包）。

## FACTOR-005 · Reversal基础因子

- 来源：V3.0§3.4;V3.0§18；等级：MVP；阶段：2；优先级：P1；模块：factors。
- 输入：同Momentum输入。输出：负L期收益。依赖：FACTOR-002。
- 验收：相同输入输出−.21，方向不重复反号。
- 设计：[契约/方案](INTERFACES.md)；拟代码：`src/aqrp/factors/`；拟测试：`tests/factors/test_factor_005.py`。
- 能力状态：Planned；设计状态：DRAFT_PRESENT；实际实现/测试证据：尚无（P0文档证据另见审查包）。

## FACTOR-006 · Volume基础因子

- 来源：V3.0§3.4;V3.0§18；等级：MVP；阶段：2；优先级：P1；模块：factors。
- 输入：当日及前L日股数。输出：相对历史均量信号。依赖：FACTOR-002。
- 验收：分母0/历史不足显式无效，手与股不混。
- 设计：[契约/方案](INTERFACES.md)；拟代码：`src/aqrp/factors/`；拟测试：`tests/factors/test_factor_006.py`。
- 能力状态：Planned；设计状态：DRAFT_PRESENT；实际实现/测试证据：尚无（P0文档证据另见审查包）。

## FACTOR-007 · Price-Volume基础因子与独立公式审批

- 来源：V3.0§3.4；等级：Competition Ready；阶段：3；优先级：P1；模块：factors。
- 输入：价格和成交量。输出：价量信号。依赖：FACTOR-003。
- 验收：公式预注册和独立答案，不以Volume冒充价量。
- 设计：[契约/方案](INTERFACES.md)；拟代码：`src/aqrp/factors/`；拟测试：`tests/factors/test_factor_007.py`。
- 能力状态：Planned；设计状态：DRAFT_PRESENT；实际实现/测试证据：尚无（P0文档证据另见审查包）。

## FACTOR-008 · 波动率/流动性/基本面/更广截面/公式WorldQuant/ML扩展

- 来源：V3.0§3.4；等级：Advanced Research；阶段：POST7；优先级：P2；模块：factors。
- 输入：已审批数据及模型。输出：新候选因子。依赖：FACTOR-003;INT-004。
- 验收：每类新增独立需求/答案，不提前加框架。
- 设计：[契约/方案](ROADMAP.md)；拟代码：`src/aqrp/factors/`；拟测试：`tests/factors/test_factor_008.py`。
- 能力状态：Deferred；设计状态：DRAFT_PRESENT；实际实现/测试证据：尚无（P0文档证据另见审查包）。

## FACTOR-009 · Candidate/Reviewed/ResearchValidated/StrategyApproved审批证据隔离

- 来源：V3.0§1.3;V3.0§3.5;V3.0§12.3;V3.0§18；等级：MVP；阶段：3；优先级：P1；模块：factors。
- 输入：代码审查及研究标准/证据。输出：审批记录。依赖：FACTOR-003;VALID-008。
- 验收：P3不凭空要求P5，策略批准待P5经济证据。
- 设计：[契约/方案](RESEARCH_PROTOCOL.md)；拟代码：`src/aqrp/factors/`；拟测试：`tests/factors/test_factor_009.py`。
- 能力状态：Planned；设计状态：DRAFT_PRESENT；实际实现/测试证据：尚无（P0文档证据另见审查包）。

## FACTOR-010 · 配置选因子/参数/增删/停用/权重/版本/回滚，新运行pin不可热替换

- 来源：V3.0§3.5;V3.0§13；等级：MVP；阶段：2；优先级：P1；模块：factors。
- 输入：不可变因子配置。输出：新运行版本。依赖：FACTOR-003。
- 验收：旧运行不随registry变化；权重由P4消费，UI由P6提供。
- 设计：[契约/方案](INTERFACES.md)；拟代码：`src/aqrp/factors/`；拟测试：`tests/factors/test_factor_010.py`。
- 能力状态：Planned；设计状态：DRAFT_PRESENT；实际实现/测试证据：尚无（P0文档证据另见审查包）。

## FACTOR-011 · P2注册替换和版本兼容测试

- 来源：V3.0§3.6;V3.1§1;V3.2§7；等级：MVP；阶段：2；优先级：P1；模块：factors。
- 输入：固定DataView/两个因子。输出：API替换证据。依赖：FACTOR-004;FACTOR-005。
- 验收：只改FactorRef，不调用尚不存在研究/回测。
- 设计：[契约/方案](TESTING.md)；拟代码：`src/aqrp/factors/`；拟测试：`tests/factors/test_factor_011.py`。
- 能力状态：Planned；设计状态：DRAFT_PRESENT；实际实现/测试证据：尚无（P0文档证据另见审查包）。

## FACTOR-012 · 因子隔离/确定性/不修改资金持仓费用或其他代码

- 来源：V3.0§3.3;V3.0§11.2;V3.1§7；等级：MVP；阶段：2；优先级：P1；模块：factors。
- 输入：受审插件与只读数据。输出：受限执行。依赖：FACTOR-001;SEC-001。
- 验收：未授权读取未来/网络/账户被拒，接口不冒充沙箱。
- 设计：[契约/方案](ENVIRONMENT_AND_SECURITY.md)；拟代码：`src/aqrp/factors/`；拟测试：`tests/factors/test_factor_012.py`。
- 能力状态：Planned；设计状态：DRAFT_PRESENT；实际实现/测试证据：尚无（P0文档证据另见审查包）。

## RESEARCH-001 · 批量Alpha计算/预处理/验证/报告/实验完整研究编排

- 来源：V3.0§5.1;V3.0§12.1；等级：MVP；阶段：3；优先级：P1；模块：research。
- 输入：因子股票池/区间/协议。输出：完整研究产物。依赖：FACTOR-003。
- 验收：链路真实可运行，无占位模块伪装。
- 设计：[契约/方案](INTERFACES.md)；拟代码：`src/aqrp/research/`；拟测试：`tests/research/test_research_001.py`。
- 能力状态：Planned；设计状态：DRAFT_PRESENT；实际实现/测试证据：尚无（P0文档证据另见审查包）。

## RESEARCH-002 · 去极值/缺失处理/横截面排名/z标准化，顺序和拟合区间配置化

- 来源：V3.0§5.1；等级：MVP；阶段：3；优先级：P1；模块：research。
- 输入：原始信号与处理链。输出：清洗和标准化分数。依赖：RESEARCH-001。
- 验收：常数/极端/缺失/小样本有明确定义和答案。
- 设计：[契约/方案](RESEARCH_PROTOCOL.md)；拟代码：`src/aqrp/research/`；拟测试：`tests/research/test_research_002.py`。
- 能力状态：Planned；设计状态：DRAFT_PRESENT；实际实现/测试证据：尚无（P0文档证据另见审查包）。

## RESEARCH-003 · 行业和市值中性化基础

- 来源：V3.0§5.1;V3.0§18；等级：Competition Ready；阶段：3；优先级：P1；模块：research。
- 输入：PIT行业/市值与分数。输出：残差及诊断。依赖：RESEARCH-002;DATA-012。
- 验收：秩亏/暴露缺失处理明确，不复制原值冒充。
- 设计：[契约/方案](RESEARCH_PROTOCOL.md)；拟代码：`src/aqrp/research/`；拟测试：`tests/research/test_research_003.py`。
- 能力状态：Planned；设计状态：DRAFT_PRESENT；实际实现/测试证据：尚无（P0文档证据另见审查包）。

## RESEARCH-004 · Delay/Delta/RollingMean/Std/Correlation/Sum/Min/Max

- 来源：V3.0§5.2；等级：MVP；阶段：3；优先级：P1；模块：research。
- 输入：逐证券session序列。输出：窗口算子输出。依赖：RESEARCH-001。
- 验收：端点/min_periods/ddof明示，独立测试每算子。
- 设计：[契约/方案](RESEARCH_PROTOCOL.md)；拟代码：`src/aqrp/research/`；拟测试：`tests/research/test_research_004.py`。
- 能力状态：Planned；设计状态：DRAFT_PRESENT；实际实现/测试证据：尚无（P0文档证据另见审查包）。

## RESEARCH-005 · Rank/Ts_Rank/Conditional白名单算子

- 来源：V3.0§5.2；等级：MVP；阶段：3；优先级：P1；模块：research。
- 输入：当前截面/窗口。输出：秩及条件结果。依赖：RESEARCH-004。
- 验收：并列秩正确，条件不执行任意代码。
- 设计：[契约/方案](RESEARCH_PROTOCOL.md)；拟代码：`src/aqrp/research/`；拟测试：`tests/research/test_research_005.py`。
- 能力状态：Planned；设计状态：DRAFT_PRESENT；实际实现/测试证据：尚无（P0文档证据另见审查包）。

## RESEARCH-006 · 分别保存raw/clean/standardized/neutralized/final及报告stage

- 来源：V3.0§5.3；等级：MVP；阶段：3；优先级：P1；模块：research。
- 输入：处理链结果。输出：分阶段产物。依赖：RESEARCH-002。
- 验收：未启用stage标SKIPPED，不能混报。
- 设计：[契约/方案](INTERFACES.md)；拟代码：`src/aqrp/research/`；拟测试：`tests/research/test_research_006.py`。
- 能力状态：Planned；设计状态：DRAFT_PRESENT；实际实现/测试证据：尚无（P0文档证据另见审查包）。

## RESEARCH-007 · 因子相关/组合研究/冗余分析

- 来源：V3.0§5.1；等级：MVP；阶段：3；优先级：P1；模块：research。
- 输入：同股票池及stage因子。输出：相关与冗余报告。依赖：RESEARCH-006。
- 验收：对齐交集和缺失n，研究组合不动账户。
- 设计：[契约/方案](RESEARCH_PROTOCOL.md)；拟代码：`src/aqrp/research/`；拟测试：`tests/research/test_research_007.py`。
- 能力状态：Planned；设计状态：DRAFT_PRESENT；实际实现/测试证据：尚无（P0文档证据另见审查包）。

## RESEARCH-008 · 缓存和参数实验，版本/时点/处理链缓存隔离

- 来源：V3.0§5.1;V3.0§13；等级：MVP；阶段：3；优先级：P1；模块：research。
- 输入：运行配置和数据hash。输出：可追溯缓存/实验。依赖：EXP-001;RESEARCH-001。
- 验收：未来数据/参数改变不复用错误缓存，所有试验保留。
- 设计：[契约/方案](ARCHITECTURE.md)；拟代码：`src/aqrp/research/`；拟测试：`tests/research/test_research_008.py`。
- 能力状态：Planned；设计状态：DRAFT_PRESENT；实际实现/测试证据：尚无（P0文档证据另见审查包）。

## RESEARCH-009 · P3因子替换后完整研究可运行

- 来源：V3.1§1;V3.0§3.6；等级：MVP；阶段：3；优先级：P1；模块：research。
- 输入：固定研究配置及Momentum/Reversal。输出：研究替换报告。依赖：RESEARCH-001;VALID-001。
- 验收：只改因子选择，报告/统计核心无需改动。
- 设计：[契约/方案](TESTING.md)；拟代码：`src/aqrp/research/`；拟测试：`tests/research/test_research_009.py`。
- 能力状态：Planned；设计状态：DRAFT_PRESENT；实际实现/测试证据：尚无（P0文档证据另见审查包）。

## VALID-001 · Pearson/Spearman/MeanIC/std/ICIR/正值比例/序列

- 来源：V3.0§6.1;V3.0§6.2;V3.0§10.2；等级：MVP；阶段：3；优先级：P1；模块：validation。
- 输入：有效截面分数与未来标签。输出：统计指标及n/reason。依赖：RESEARCH-006。
- 验收：平均并列秩/ddof1/默认非年化正确，Golden对齐。
- 设计：[契约/方案](RESEARCH_PROTOCOL.md)；拟代码：`src/aqrp/validation/`；拟测试：`tests/validation/test_valid_001.py`。
- 能力状态：Planned；设计状态：DRAFT_PRESENT；实际实现/测试证据：尚无（P0文档证据另见审查包）。

## VALID-002 · 分位组收益/单调/TMB、衰减/多期限/年度稳定

- 来源：V3.0§6.1;V3.0§6.2；等级：MVP；阶段：3；优先级：P1；模块：validation。
- 输入：已注册期限和标签。输出：分层衰减年度报告。依赖：VALID-001。
- 验收：标签起止可用/股票池/权重明确，不混期限。
- 设计：[契约/方案](RESEARCH_PROTOCOL.md)；拟代码：`src/aqrp/validation/`；拟测试：`tests/validation/test_valid_002.py`。
- 能力状态：Planned；设计状态：DRAFT_PRESENT；实际实现/测试证据：尚无（P0文档证据另见审查包）。

## VALID-003 · Train/Validation/Test及Walk-forward/Purge/Embargo

- 来源：V3.0§6.3;V3.1§4；等级：MVP；阶段：3；优先级：P1；模块：validation。
- 输入：标签信息区间和split协议。输出：无重叠污染评估。依赖：VALID-001。
- 验收：相交训练标签剔除、窗口留痕、不随机打散。
- 设计：[契约/方案](RESEARCH_PROTOCOL.md)；拟代码：`src/aqrp/validation/`；拟测试：`tests/validation/test_valid_003.py`。
- 能力状态：Planned；设计状态：DRAFT_PRESENT；实际实现/测试证据：尚无（P0文档证据另见审查包）。

## VALID-004 · 开发期确定方向/参数/预处理/期限，最终Test封存与访问审计

- 来源：V3.0§6.4;V3.1§4；等级：MVP；阶段：3；优先级：P1；模块：validation。
- 输入：预注册协议和访问身份。输出：冻结配置及测试记录。依赖：VALID-003;EXP-002。
- 验收：反复Test调参被识别为污染，不能继续宣称独立。
- 设计：[契约/方案](RESEARCH_PROTOCOL.md)；拟代码：`src/aqrp/validation/`；拟测试：`tests/validation/test_valid_004.py`。
- 能力状态：Planned；设计状态：DRAFT_PRESENT；实际实现/测试证据：尚无（P0文档证据另见审查包）。

## VALID-005 · 显著性/自相关/重叠期限稳健SE或预注册替代法

- 来源：V3.0§6.1;V3.0§6.5；等级：MVP；阶段：3；优先级：P1；模块：validation。
- 输入：IC序列和依赖假设。输出：SE/p/不确定性。依赖：VALID-001。
- 验收：不把ICIR当t值，假设不满足明确拒绝。
- 设计：[契约/方案](RESEARCH_PROTOCOL.md)；拟代码：`src/aqrp/validation/`；拟测试：`tests/validation/test_valid_005.py`。
- 能力状态：Planned；设计状态：DRAFT_PRESENT；实际实现/测试证据：尚无（P0文档证据另见审查包）。

## VALID-006 · 记录全部候选/参数/淘汰/筛选/验证访问次数与重复试验

- 来源：V3.0§6.4;V3.1§4；等级：MVP；阶段：3；优先级：P1；模块：validation。
- 输入：所有实验及family。输出：搜索路径及overfit风险。依赖：EXP-002;VALID-004。
- 验收：不能只保留赢家或重命名Test，重复指纹可查。
- 设计：[契约/方案](RESEARCH_PROTOCOL.md)；拟代码：`src/aqrp/validation/`；拟测试：`tests/validation/test_valid_006.py`。
- 能力状态：Planned；设计状态：DRAFT_PRESENT；实际实现/测试证据：尚无（P0文档证据另见审查包）。

## VALID-007 · 多重假设family及Holm/BY/BH适用性和校正记录

- 来源：V3.0§6.4;V3.1§4；等级：MVP；阶段：3；优先级：P1；模块：validation。
- 输入：原始p及预注册m。输出：校正p和风险说明。依赖：VALID-005;VALID-006。
- 验收：计入全部假设，依赖/自适应限制披露。
- 设计：[契约/方案](RESEARCH_PROTOCOL.md)；拟代码：`src/aqrp/validation/`；拟测试：`tests/validation/test_valid_007.py`。
- 能力状态：Planned；设计状态：DRAFT_PRESENT；实际实现/测试证据：尚无（P0文档证据另见审查包）。

## VALID-008 · 批准前记录预定标准及实际验证，不以正IC批准

- 来源：V3.0§6.5;V3.1§4；等级：MVP；阶段：3；优先级：P1；模块：validation。
- 输入：冻结标准/独立OOS证据。输出：ResearchValidated提案。依赖：VALID-004;VALID-007。
- 验收：阈值未批准或证据不齐不可正式批准，交易适用待P5。
- 设计：[契约/方案](RESEARCH_PROTOCOL.md)；拟代码：`src/aqrp/validation/`；拟测试：`tests/validation/test_valid_008.py`。
- 能力状态：Planned；设计状态：DRAFT_PRESENT；实际实现/测试证据：尚无（P0文档证据另见审查包）。

## PORT-001 · 因子无关组合输入和目标权重/仓位/调仓建议及诊断

- 来源：V3.0§7.1；等级：MVP；阶段：4；优先级：P1；模块：portfolio。
- 输入：已批准分数/股票池/账户/权益/暴露。输出：TargetPortfolio。依赖：FACTOR-009;VALID-008。
- 验收：不依赖具体因子名称，不修改账本。
- 设计：[契约/方案](INTERFACES.md)；拟代码：`src/aqrp/portfolio/`；拟测试：`tests/portfolio/test_port_001.py`。
- 能力状态：Planned；设计状态：DRAFT_PRESENT；实际实现/测试证据：尚无（P0文档证据另见审查包）。

## PORT-002 · 单/多因子组合、等权/分数权、LongOnly

- 来源：V3.0§7.2;V3.0§3.4；等级：MVP；阶段：4；优先级：P1；模块：portfolio。
- 输入：分数和权重规则。输出：合法目标及残余现金。依赖：PORT-001。
- 验收：零分/负分/整手余数有定义，权重守恒。
- 设计：[契约/方案](INTERFACES.md)；拟代码：`src/aqrp/portfolio/`；拟测试：`tests/portfolio/test_port_002.py`。
- 能力状态：Planned；设计状态：DRAFT_PRESENT；实际实现/测试证据：尚无（P0文档证据另见审查包）。

## PORT-003 · LongShort组合及gross/net分别控制

- 来源：V3.0§7.2;V3.0§18；等级：Competition Ready；阶段：4；优先级：P1；模块：portfolio。
- 输入：多空权限及分数。输出：多空目标。依赖：PORT-001;RISK-003。
- 验收：不得用long-only冒充多空，P5另测真实模拟约束。
- 设计：[契约/方案](INTERFACES.md)；拟代码：`src/aqrp/portfolio/`；拟测试：`tests/portfolio/test_port_003.py`。
- 能力状态：Planned；设计状态：DRAFT_PRESENT；实际实现/测试证据：尚无（P0文档证据另见审查包）。

## PORT-004 · 优化算法扩展

- 来源：V3.0§7.2；等级：Advanced Research；阶段：POST7；优先级：P2；模块：portfolio。
- 输入：批准的约束/优化方案。输出：优化目标。依赖：PORT-001;INT-004。
- 验收：代价/兼容/迁移评审后另行授权。
- 设计：[契约/方案](ROADMAP.md)；拟代码：`src/aqrp/portfolio/`；拟测试：`tests/portfolio/test_port_004.py`。
- 能力状态：Deferred；设计状态：DRAFT_PRESENT；实际实现/测试证据：尚无（P0文档证据另见审查包）。

## RISK-001 · 单票/总敞口/净敞口/杠杆/换手限制

- 来源：V3.0§7.3；等级：MVP；阶段：4；优先级：P1；模块：risk。
- 输入：目标账户/配置。输出：逐项风险诊断。依赖：PORT-001。
- 验收：等号/越界/冲突约束测试，不静默放宽。
- 设计：[契约/方案](INTERFACES.md)；拟代码：`src/aqrp/risk/`；拟测试：`tests/risk/test_risk_001.py`。
- 能力状态：Planned；设计状态：DRAFT_PRESENT；实际实现/测试证据：尚无（P0文档证据另见审查包）。

## RISK-002 · 行业与Beta暴露限制

- 来源：V3.0§7.3；等级：Competition Ready；阶段：4；优先级：P1；模块：risk。
- 输入：PIT暴露及目标。输出：合规或拒绝。依赖：PORT-001;DATA-012。
- 验收：缺暴露不视为0，容差明确。
- 设计：[契约/方案](INTERFACES.md)；拟代码：`src/aqrp/risk/`；拟测试：`tests/risk/test_risk_002.py`。
- 能力状态：Planned；设计状态：DRAFT_PRESENT；实际实现/测试证据：尚无（P0文档证据另见审查包）。

## RISK-003 · 可交易性/空头许可/借券/可售数量检查

- 来源：V3.0§7.3；等级：Competition Ready；阶段：4；优先级：P1；模块：risk。
- 输入：市场profile/状态/账户。输出：交易资格诊断。依赖：PORT-001;DATA-005。
- 验收：停牌/借券不足显式拒绝，P5提交撮合再检查。
- 设计：[契约/方案](INTERFACES.md)；拟代码：`src/aqrp/risk/`；拟测试：`tests/risk/test_risk_003.py`。
- 能力状态：Planned；设计状态：DRAFT_PRESENT；实际实现/测试证据：尚无（P0文档证据另见审查包）。

## RISK-004 · 风险拒单及不可行组合显式错误，不可绕过

- 来源：V3.0§7.3;V3.0§11.2；等级：MVP；阶段：4；优先级：P1；模块：risk。
- 输入：候选目标/订单。输出：RiskDecision/reason。依赖：RISK-001。
- 验收：调用方不能强制忽略拒绝；实际订单接线P5测。
- 设计：[契约/方案](INTERFACES.md)；拟代码：`src/aqrp/risk/`；拟测试：`tests/risk/test_risk_004.py`。
- 能力状态：Planned；设计状态：DRAFT_PRESENT；实际实现/测试证据：尚无（P0文档证据另见审查包）。

## BT-001 · 独立Market/Signal/Decision/Order/Fill/Account/Valuation事件状态机

- 来源：V3.0§8.1;V3.1§3；等级：MVP；阶段：5；优先级：P1；模块：backtest。
- 输入：有序事件及causation。输出：确定性事件流。依赖：PORT-001;RISK-004;DATA-002。
- 验收：P0契约在P5自动验证，逐笔Fill/账户原子配对。
- 设计：[契约/方案](BACKTEST_CONTRACT.md)；拟代码：`src/aqrp/backtest/`；拟测试：`tests/backtest/test_bt_001.py`。
- 能力状态：Planned；设计状态：DRAFT_PRESENT；实际实现/测试证据：尚无（P0文档证据另见审查包）。

## BT-002 · 收盘后信号、next session最早开盘，available/decision/submission/eligible/fill约束

- 来源：V3.0§8.2;V3.1§3；等级：MVP；阶段：5；优先级：P1；模块：backtest。
- 输入：可用数据及日历。输出：合法可执行订单。依赖：BT-001。
- 验收：不可用前无订单，延迟错过开盘不得倒填。
- 设计：[契约/方案](BACKTEST_CONTRACT.md)；拟代码：`src/aqrp/backtest/`；拟测试：`tests/backtest/test_bt_002.py`。
- 能力状态：Planned；设计状态：DRAFT_PRESENT；实际实现/测试证据：尚无（P0文档证据另见审查包）。

## BT-003 · 创建/状态/成交/部分成交/拒绝/取消/到期与幂等

- 来源：V3.0§8.3；等级：MVP；阶段：5；优先级：P1；模块：execution。
- 输入：订单和执行切片。输出：Fill/状态记录。依赖：BT-002;RISK-004。
- 验收：非法终态拒绝，累计数量守恒，重试不重复成交。
- 设计：[契约/方案](BACKTEST_CONTRACT.md)；拟代码：`src/aqrp/execution/`；拟测试：`tests/execution/test_bt_003.py`。
- 能力状态：Planned；设计状态：DRAFT_PRESENT；实际实现/测试证据：尚无（P0文档证据另见审查包）。

## BT-004 · 费用/滑点/流动性/停牌与开盘可交易模型

- 来源：V3.0§8.2;V3.0§8.3；等级：MVP；阶段：5；优先级：P1；模块：execution。
- 输入：批准profile和历史可见容量。输出：现实假设模拟Fill。依赖：BT-003。
- 验收：无日终量泄漏，不能无条件全额理想成交。
- 设计：[契约/方案](BACKTEST_CONTRACT.md)；拟代码：`src/aqrp/execution/`；拟测试：`tests/execution/test_bt_004.py`。
- 能力状态：Planned；设计状态：DRAFT_PRESENT；实际实现/测试证据：尚无（P0文档证据另见审查包）。

## BT-005 · 现金/持仓/成本/费用/现金流/已实现未实现/权益账本及原始重建

- 来源：V3.0§8.4;V3.0§10.3;V3.1§3；等级：MVP；阶段：5；优先级：P1；模块：backtest。
- 输入：Fill/现金流/账户初态。输出：Journal/AccountState。依赖：BT-003;DATA-011。
- 验收：799/210/1009独立核对，买卖部分成交边界性质均测。
- 设计：[契约/方案](BACKTEST_CONTRACT.md)；拟代码：`src/aqrp/backtest/`；拟测试：`tests/backtest/test_bt_005.py`。
- 能力状态：Planned；设计状态：DRAFT_PRESENT；实际实现/测试证据：尚无（P0文档证据另见审查包）。

## BT-006 · 行动/分红应收支付/拆股/交收/退市估值

- 来源：V3.0§2.1;V3.0§8.4;V3.0§10.3；等级：Competition Ready；阶段：5；优先级：P1；模块：backtest。
- 输入：行动/市场profile/持仓。输出：资金和证券变动。依赖：BT-005;DATA-004;DATA-005。
- 验收：行动不双计，碎股/税务/停退市未知明确阻断。
- 设计：[契约/方案](BACKTEST_CONTRACT.md)；拟代码：`src/aqrp/backtest/`；拟测试：`tests/backtest/test_bt_006.py`。
- 能力状态：Planned；设计状态：DRAFT_PRESENT；实际实现/测试证据：尚无（P0文档证据另见审查包）。

## BT-007 · 空头、融资/借券费、保证金与股息应付

- 来源：V3.0§8.4;V3.0§10.3；等级：Competition Ready；阶段：5；优先级：P1；模块：backtest。
- 输入：已批准多空profile。输出：多空账本和费用。依赖：BT-005;PORT-003;RISK-003。
- 验收：独立空头答案+边界/性质，缺规则Unsupported不假装通过。
- 设计：[契约/方案](BACKTEST_CONTRACT.md)；拟代码：`src/aqrp/backtest/`；拟测试：`tests/backtest/test_bt_007.py`。
- 能力状态：Planned；设计状态：DRAFT_PRESENT；实际实现/测试证据：尚无（P0文档证据另见审查包）。

## BT-008 · 估值/权益/每日持仓现金/风险暴露/订单成交报告

- 来源：V3.0§8.4;V3.0§8.5；等级：MVP；阶段：5；优先级：P1；模块：performance。
- 输入：账本及RAW marks。输出：账户与策略报告。依赖：BT-005。
- 验收：权益独立对账，stale/缺估值明确披露。
- 设计：[契约/方案](BACKTEST_CONTRACT.md)；拟代码：`src/aqrp/performance/`；拟测试：`tests/performance/test_bt_008.py`。
- 能力状态：Planned；设计状态：DRAFT_PRESENT；实际实现/测试证据：尚无（P0文档证据另见审查包）。

## BT-009 · 累计/年化/波动/Sharpe/MDD/换手/费用/净收益/多空贡献

- 来源：V3.0§8.5；等级：MVP；阶段：5；优先级：P1；模块：performance。
- 输入：日权益收益/费用及约定。输出：统一绩效指标。依赖：BT-008。
- 验收：A/ddof/rf/现金流/换手定义明确，费用不双扣。
- 设计：[契约/方案](BACKTEST_CONTRACT.md)；拟代码：`src/aqrp/performance/`；拟测试：`tests/performance/test_bt_009.py`。
- 能力状态：Planned；设计状态：DRAFT_PRESENT；实际实现/测试证据：尚无（P0文档证据另见审查包）。

## BT-010 · P5因子替换后完整组合/风险/撮合/账本流程

- 来源：V3.1§1;V3.0§3.6;V3.0§12.2；等级：MVP；阶段：5；优先级：P1；模块：backtest。
- 输入：固定模拟配置及两因子。输出：回测替换证据。依赖：BT-009;FACTOR-004;FACTOR-005。
- 验收：只改因子配置，核心hash未变，独立订单/资金答案正确。
- 设计：[契约/方案](TESTING.md)；拟代码：`src/aqrp/backtest/`；拟测试：`tests/backtest/test_bt_010.py`。
- 能力状态：Planned；设计状态：DRAFT_PRESENT；实际实现/测试证据：尚无（P0文档证据另见审查包）。

## UI-001 · Dashboard状态/因子数/任务/最近研究回测/错误警告

- 来源：V3.0§9.1；等级：MVP；阶段：6；优先级：P1；模块：ui。
- 输入：应用服务结果。输出：状态页面。依赖：BT-009;RESEARCH-001。
- 验收：真实任务状态，不伪造成功/数量。
- 设计：[契约/方案](INTERFACES.md)；拟代码：`src/aqrp/ui/`；拟测试：`tests/ui/test_ui_001.py`。
- 能力状态：Planned；设计状态：DRAFT_PRESENT；实际实现/测试证据：尚无（P0文档证据另见审查包）。

## UI-002 · FactorLibrary列表详情/版本参数/选择状态/比较/增删配置权重回滚

- 来源：V3.0§9.2;V3.0§3.5；等级：Competition Ready；阶段：6；优先级：P1；模块：ui。
- 输入：Registry及请求配置。输出：因子管理页面。依赖：FACTOR-010;UI-001。
- 验收：精确版本和审批可见，无网页任意Python执行。
- 设计：[契约/方案](INTERFACES.md)；拟代码：`src/aqrp/ui/`；拟测试：`tests/ui/test_ui_002.py`。
- 能力状态：Planned；设计状态：DRAFT_PRESENT；实际实现/测试证据：尚无（P0文档证据另见审查包）。

## UI-003 · AlphaResearch选择股票池/因子/区间/期限，IC/Rank/ICIR/分层/衰减/OOS展示

- 来源：V3.0§9.3；等级：MVP；阶段：6；优先级：P1；模块：ui。
- 输入：ResearchRequest。输出：研究页面。依赖：RESEARCH-009;UI-001。
- 验收：展示后端原始产物不私改统计，缺项明确。
- 设计：[契约/方案](INTERFACES.md)；拟代码：`src/aqrp/ui/`；拟测试：`tests/ui/test_ui_003.py`。
- 能力状态：Planned；设计状态：DRAFT_PRESENT；实际实现/测试证据：尚无（P0文档证据另见审查包）。

## UI-004 · StrategyBacktest选批准因子/权重/仓位/风险/成本，收益回撤订单Fill持仓

- 来源：V3.0§9.4；等级：MVP；阶段：6；优先级：P1；模块：ui。
- 输入：BacktestRequest。输出：回测页面。依赖：BT-010;UI-001。
- 验收：候选因子禁止策略调用，结果来自统一服务。
- 设计：[契约/方案](INTERFACES.md)；拟代码：`src/aqrp/ui/`；拟测试：`tests/ui/test_ui_004.py`。
- 能力状态：Planned；设计状态：DRAFT_PRESENT；实际实现/测试证据：尚无（P0文档证据另见审查包）。

## UI-005 · ExperimentManager查询/版本参数比较/数据版本/报告/复现

- 来源：V3.0§9.5；等级：Competition Ready；阶段：6；优先级：P1；模块：ui。
- 输入：run_id及索引。输出：实验页面。依赖：EXP-003;UI-001。
- 验收：历史不可覆盖，差异及不可复现原因展示。
- 设计：[契约/方案](INTERFACES.md)；拟代码：`src/aqrp/ui/`；拟测试：`tests/ui/test_ui_005.py`。
- 能力状态：Planned；设计状态：DRAFT_PRESENT；实际实现/测试证据：尚无（P0文档证据另见审查包）。

## UI-006 · Settings数据源/默认参数/费用/风险/依赖信息/日志

- 来源：V3.0§9.6；等级：Competition Ready；阶段：6；优先级：P1；模块：ui。
- 输入：经校验设置。输出：新配置及可见日志。依赖：UI-001;ENV-001。
- 验收：只影响新任务，不改已封存实验，敏感值不泄露。
- 设计：[契约/方案](INTERFACES.md)；拟代码：`src/aqrp/ui/`；拟测试：`tests/ui/test_ui_006.py`。
- 能力状态：Planned；设计状态：DRAFT_PRESENT；实际实现/测试证据：尚无（P0文档证据另见审查包）。

## UI-007 · CLI/服务/网页因子选择和研究/回测同配置同核一致

- 来源：V3.0§9.7;V3.1§1；等级：MVP；阶段：6；优先级：P1；模块：ui。
- 输入：同canonical配置/数据/版本。输出：一致性比对证据。依赖：UI-002;UI-003;UI-004。
- 验收：config_hash和数值相同，允许run_id/墙钟不同。
- 设计：[契约/方案](TESTING.md)；拟代码：`src/aqrp/ui/`；拟测试：`tests/ui/test_ui_007.py`。
- 能力状态：Planned；设计状态：DRAFT_PRESENT；实际实现/测试证据：尚无（P0文档证据另见审查包）。

## UI-008 · 任务提交/状态/取消/错误日志/图表报告，算法不在页面重写

- 来源：V3.0§9;V3.0§18;V3.0§2.1；等级：MVP；阶段：6；优先级：P1；模块：services。
- 输入：统一RunRequest。输出：RunReceipt/TaskState/Artifact。依赖：UI-001;EXP-001。
- 验收：失败取消不标SUCCEEDED，幂等重试不重复任务。
- 设计：[契约/方案](INTERFACES.md)；拟代码：`src/aqrp/services/`；拟测试：`tests/services/test_ui_008.py`。
- 能力状态：Planned；设计状态：DRAFT_PRESENT；实际实现/测试证据：尚无（P0文档证据另见审查包）。

## EXP-001 · 唯一run_id和不可变配置，代码/数据/因子/参数/股票池/split/seed/环境/规则成本/时间/日志/失败

- 来源：V3.0§13;V3.1§7；等级：MVP；阶段：3；优先级：P1；模块：experiments。
- 输入：完整运行配置与血缘。输出：append-only RunRecord。依赖：DATA-007;FACTOR-003。
- 验收：所有指定字段完整，封存后修改被拒，不覆盖历史。
- 设计：[契约/方案](INTERFACES.md)；拟代码：`src/aqrp/experiments/`；拟测试：`tests/experiments/test_exp_001.py`。
- 能力状态：Planned；设计状态：DRAFT_PRESENT；实际实现/测试证据：尚无（P0文档证据另见审查包）。

## EXP-002 · 全部参数候选/淘汰与验证访问次数及重复指纹

- 来源：V3.0§6.4;V3.0§13;V3.1§4；等级：MVP；阶段：3；优先级：P1；模块：experiments。
- 输入：每次研究调用。输出：实验搜索ledger。依赖：EXP-001。
- 验收：失败实验留痕，赢家选择可反查。
- 设计：[契约/方案](RESEARCH_PROTOCOL.md)；拟代码：`src/aqrp/experiments/`；拟测试：`tests/experiments/test_exp_002.py`。
- 能力状态：Planned；设计状态：DRAFT_PRESENT；实际实现/测试证据：尚无（P0文档证据另见审查包）。

## EXP-003 · 版本差异比较/复现与不可复现原因

- 来源：V3.0§13;V3.0§9.5；等级：MVP；阶段：3；优先级：P1；模块：experiments。
- 输入：固定run与工件。输出：差异报告或重放任务。依赖：EXP-001。
- 验收：缺hash/脏代码不冒充正式复现，旧结果不改写。
- 设计：[契约/方案](INTERFACES.md)；拟代码：`src/aqrp/experiments/`；拟测试：`tests/experiments/test_exp_003.py`。
- 能力状态：Planned；设计状态：DRAFT_PRESENT；实际实现/测试证据：尚无（P0文档证据另见审查包）。

## EXP-004 · 批准因子时预设标准/冻结时间/实际证据/审批者

- 来源：V3.1§4;V3.1§7；等级：MVP；阶段：3；优先级：P1；模块：experiments。
- 输入：ApprovalProposal与审核记录。输出：可验证批准记录。依赖：VALID-008;EXP-001。
- 验收：候选变更必须新版本再验证，P5后才可策略批准。
- 设计：[契约/方案](RESEARCH_PROTOCOL.md)；拟代码：`src/aqrp/experiments/`；拟测试：`tests/experiments/test_exp_004.py`。
- 能力状态：Planned；设计状态：DRAFT_PRESENT；实际实现/测试证据：尚无（P0文档证据另见审查包）。

## ENV-001 · 精确Python及直接传递依赖/哈希/平台环境固定

- 来源：V3.0§18;V3.1§7；等级：MVP；阶段：1；优先级：P1；模块：environment。
- 输入：批准环境选型。输出：锁文件及环境清单。依赖：GOV-004。
- 验收：P1干净安装可复现，升级经评审；P0不得称已锁定。
- 设计：[契约/方案](ENVIRONMENT_AND_SECURITY.md)；拟代码：`pyproject.toml;requirements.lock;.github/workflows/ci.yml`；拟测试：`tests/environment/test_env_001.py`。
- 能力状态：Planned；设计状态：DRAFT_PRESENT；实际实现/测试证据：尚无（P0文档证据另见审查包）。

## ENV-002 · 开始正式代码即建Actions安装/格式静态/单元集成回归/报告

- 来源：V3.0§11.4；等级：MVP；阶段：1；优先级：P1；模块：environment。
- 输入：固定依赖及适用测试。输出：可信CI证据。依赖：ENV-001。
- 验收：关键失败阻断，外部PR无秘密/写权限执行。
- 设计：[契约/方案](ENVIRONMENT_AND_SECURITY.md)；拟代码：`pyproject.toml;requirements.lock;.github/workflows/ci.yml`；拟测试：`tests/environment/test_env_002.py`。
- 能力状态：Planned；设计状态：DRAFT_PRESENT；实际实现/测试证据：尚无（P0文档证据另见审查包）。

## ENV-003 · 风险分层覆盖率目标，不能代替数学答案

- 来源：V3.0§11.3；等级：MVP；阶段：0；优先级：P1；模块：environment。
- 输入：模块风险。输出：覆盖率与案例门槛。依赖：ARCH-001。
- 验收：金融关键行95/分支90等目标明确并待批准。
- 设计：[契约/方案](TESTING.md)；拟代码：`docs/TESTING.md`；拟测试：`docs/audits/phase-0/`。
- 能力状态：Planned；设计状态：DRAFT_PRESENT；实际实现/测试证据：尚无（P0文档证据另见审查包）。

## SEC-001 · 新因子审查后才入批准环境，隔离最小权限/不可信代码禁执行

- 来源：V3.0§3.3;V3.0§9.2;V3.0§20;V3.1§7;V3.2§3；等级：MVP；阶段：2；优先级：P0；模块：security。
- 输入：代码hash/审查证据。输出：允许列表与受限测试。依赖：ENV-001。
- 验收：Candidate不获账户/网络权限，AST检查不当安全边界。
- 设计：[契约/方案](ENVIRONMENT_AND_SECURITY.md)；拟代码：`src/aqrp/core/security/`；拟测试：`tests/security/test_sec_001.py`。
- 能力状态：Planned；设计状态：DRAFT_PRESENT；实际实现/测试证据：尚无（P0文档证据另见审查包）。

## SEC-002 · 禁止提交真实密钥、凭证隔离与日志脱敏/提交CI扫描

- 来源：V3.0§20;V3.1§7;V3.2§3；等级：MVP；阶段：1；优先级：P0；模块：security。
- 输入：源码配置日志。输出：无秘密工件。依赖：ENV-001。
- 验收：扫描与人工核查，无真实交易凭证进入测试。
- 设计：[契约/方案](ENVIRONMENT_AND_SECURITY.md)；拟代码：`src/aqrp/core/security/`；拟测试：`tests/security/test_sec_002.py`。
- 能力状态：Planned；设计状态：DRAFT_PRESENT；实际实现/测试证据：尚无（P0文档证据另见审查包）。

## SEC-003 · 真实账户/真实订单及生产权限隔离

- 来源：V3.0§20;V3.1§7;V3.1§5；等级：Production Extensions；阶段：POST7；优先级：P2；模块：security。
- 输入：另行明确授权。输出：未来真实执行能力。依赖：INT-004。
- 验收：当前Unsupported，不因比赛适配或研究自动开放。
- 设计：[契约/方案](ENVIRONMENT_AND_SECURITY.md)；拟代码：`src/aqrp/core/security/`；拟测试：`tests/security/test_sec_003.py`。
- 能力状态：Unsupported；设计状态：DRAFT_PRESENT；实际实现/测试证据：尚无（P0文档证据另见审查包）。

## SEC-004 · Gemini初始只读，独立测试分支/执行须授权，GPT保留原审计

- 来源：V3.2§1;V3.2§3;V3.2§8；等级：MVP；阶段：0；优先级：P0；模块：security。
- 输入：用户权限和原报告。输出：权限/审查记录。依赖：GOV-008。
- 验收：不代写或篡改Gemini结论，不代用户批准。
- 设计：[契约/方案](ACCEPTANCE.md)；拟代码：`docs/ACCEPTANCE.md`；拟测试：`docs/audits/phase-0/`。
- 能力状态：Planned；设计状态：DRAFT_PRESENT；实际实现/测试证据：尚无（P0文档证据另见审查包）。

## QA-001 · Golden设计覆盖收益/因子/IC/Rank/ICIR/排名标准化/权重/费用账本/MDD/卖出部分空头分红异常

- 来源：V3.0§10.1;V3.0§10.2;V3.0§10.3;V3.1§6；等级：MVP；阶段：0；优先级：P0；模块：quality。
- 输入：独立手算/参考。输出：输入答案依据容差核验方案。依赖：ARCH-003。
- 验收：不调用待测函数生成答案，Gemini/人工核对状态明确。
- 设计：[契约/方案](GOLDEN_DATASET.md)；拟代码：`docs/GOLDEN_DATASET.md`；拟测试：`docs/audits/phase-0/`。
- 能力状态：Planned；设计状态：DRAFT_PRESENT；实际实现/测试证据：尚无（P0文档证据另见审查包）。

## QA-002 · 单元/契约/集成/回归/E2E/泄漏/性质/必要性能测试按阶段实施

- 来源：V3.0§10.4;V3.0§11.1;V3.1§6；等级：MVP；阶段：1；优先级：P0；模块：quality。
- 输入：需求与独立预期。输出：实际适用测试报告。依赖：QA-001;DATA-008。
- 验收：关键数学和资金同时有边界性质独立参考，未来测试仅Planned。
- 设计：[契约/方案](TESTING.md)；拟代码：`tests/（对应模块）`；拟测试：`tests/quality/test_qa_002.py`。
- 能力状态：Planned；设计状态：DRAFT_PRESENT；实际实现/测试证据：尚无（P0文档证据另见审查包）。

## QA-003 · 10项核心不变量及完整事件/资金独立对账自动测试

- 来源：V3.0§11.2;V3.1§3；等级：MVP；阶段：5；优先级：P0；模块：quality。
- 输入：原始事件和独立答案。输出：不变量与已知答案证据。依赖：BT-009;QA-002。
- 验收：费用守恒/合法状态/风险/无未来/复现/批准/同核逐项适用验证。
- 设计：[契约/方案](TESTING.md)；拟代码：`tests/（对应模块）`；拟测试：`tests/quality/test_qa_003.py`。
- 能力状态：Planned；设计状态：DRAFT_PRESENT；实际实现/测试证据：尚无（P0文档证据另见审查包）。

## QA-004 · Gemini独立建立/核对Golden，人工复算关键金融数学

- 来源：V3.0§10.4;V3.1§6;V3.2§1；等级：MVP；阶段：3；优先级：P0；模块：quality。
- 输入：输入公式及原始参考。输出：核验者/日期/证据。依赖：QA-001;VALID-001。
- 验收：GPT手算不标独立审查完成，修答案走缺陷版本。
- 设计：[契约/方案](GOLDEN_DATASET.md)；拟代码：`tests/（对应模块）`；拟测试：`tests/quality/test_qa_004.py`。
- 能力状态：Planned；设计状态：DRAFT_PRESENT；实际实现/测试证据：尚无（P0文档证据另见审查包）。

## QA-005 · 六项专项审计及原V3.0覆盖/架构评审

- 来源：V3.1§8；等级：MVP；阶段：0；优先级：P0；模块：quality。
- 输入：需求与契约。输出：专项检查和架构报告。依赖：GOV-003;ARCH-003;QA-001。
- 验收：与追踪矩阵一致，未知/冲突明确列出。
- 设计：[契约/方案](audits/phase-0/SPECIAL_AUDITS.md)；拟代码：`docs/audits/phase-0/SPECIAL_AUDITS.md`；拟测试：`docs/audits/phase-0/`。
- 能力状态：Planned；设计状态：DRAFT_PRESENT；实际实现/测试证据：尚无（P0文档证据另见审查包）。

## QA-006 · ReviewPackage15项及真实命令/日志/CI/Golden/缺项证据

- 来源：V3.2§5;V3.2§6；等级：MVP；阶段：0；优先级：P0；模块：quality。
- 输入：固定SHA和实际工件。输出：可核实资料包。依赖：GOV-008。
- 验收：无实际证据不称通过，空字段和未来项如实标示。
- 设计：[契约/方案](audits/phase-0/REVIEW_PACKAGE.md)；拟代码：`docs/audits/phase-0/REVIEW_PACKAGE.md`；拟测试：`docs/audits/phase-0/`。
- 能力状态：Planned；设计状态：DRAFT_PRESENT；实际实现/测试证据：尚无（P0文档证据另见审查包）。

## QA-007 · 独立审查适用范围与运行限制、阻断闭环后人工验收

- 来源：V3.0§16;V3.0§19;V3.2§4;V3.2§6；等级：MVP；阶段：0；优先级：P0；模块：quality。
- 输入：Gemini报告/修复SHA。输出：人工验收申请。依赖：GOV-008;GOV-009。
- 验收：CI不代Gemini，Gemini不代用户，未运行不报运行级审计。
- 设计：[契约/方案](ACCEPTANCE.md)；拟代码：`docs/ACCEPTANCE.md`；拟测试：`docs/audits/phase-0/`。
- 能力状态：Planned；设计状态：DRAFT_PRESENT；实际实现/测试证据：尚无（P0文档证据另见审查包）。

## INT-001 · 加载数据→股票池→因子→预处理→IC/分层/OOS→报告→实验

- 来源：V3.0§12.1;V3.1§1；等级：MVP；阶段：3；优先级：P1；模块：integration。
- 输入：研究请求。输出：完整研究运行。依赖：RESEARCH-009;VALID-003;EXP-001。
- 验收：P3真实研究E2E，数据/版本/失败全留痕。
- 设计：[契约/方案](TESTING.md)；拟代码：`src/aqrp/services/;tests/integration/;tests/e2e/`；拟测试：`tests/integration/test_int_001.py`。
- 能力状态：Planned；设计状态：DRAFT_PRESENT；实际实现/测试证据：尚无（P0文档证据另见审查包）。

## INT-002 · 批准因子→信号→组合→风险→订单→撮合→账户→净值→绩效

- 来源：V3.0§12.2;V3.1§1；等级：MVP；阶段：5；优先级：P1；模块：integration。
- 输入：回测请求。输出：完整策略运行。依赖：BT-010;INT-001。
- 验收：各步骤真实可执行，成本后证据才授策略批准。
- 设计：[契约/方案](TESTING.md)；拟代码：`src/aqrp/services/;tests/integration/;tests/e2e/`；拟测试：`tests/integration/test_int_002.py`。
- 能力状态：Planned；设计状态：DRAFT_PRESENT；实际实现/测试证据：尚无（P0文档证据另见审查包）。

## INT-003 · Research/Strategy状态与版本隔离

- 来源：V3.0§12.3;V3.0§11.2；等级：MVP；阶段：7；优先级：P1；模块：integration。
- 输入：候选变更与固定策略配置。输出：互不污染证据。依赖：INT-002;UI-007。
- 验收：候选代码/参数修改不影响策略pin及历史实验。
- 设计：[契约/方案](TESTING.md)；拟代码：`src/aqrp/services/;tests/integration/;tests/e2e/`；拟测试：`tests/integration/test_int_003.py`。
- 能力状态：Planned；设计状态：DRAFT_PRESENT；实际实现/测试证据：尚无（P0文档证据另见审查包）。

## INT-004 · 全新环境源代码/锁依赖/数据/测试/CLI研究回测/网页执行数值比对/手册部署证据

- 来源：V3.0§12.4;V3.0§18；等级：MVP；阶段：7；优先级：P1；模块：integration。
- 输入：已审查全模块及干净环境。输出：部署及最终运行验收报告。依赖：INT-003;ENV-002。
- 验收：全部实际运行留日志，不以UI启动代完整部署。
- 设计：[契约/方案](TESTING.md)；拟代码：`src/aqrp/services/;tests/integration/;tests/e2e/`；拟测试：`tests/integration/test_int_004.py`。
- 能力状态：Planned；设计状态：DRAFT_PRESENT；实际实现/测试证据：尚无（P0文档证据另见审查包）。

## INT-005 · 固定快照和组合回测配置Momentum→Reversal完整替换/全回归

- 来源：V3.0§3.6;V3.1§1;V3.2§7；等级：MVP；阶段：7；优先级：P1；模块：integration。
- 输入：固定SHA/数据/配置。输出：全链兼容与正确性证据。依赖：INT-004;FACTOR-011;RESEARCH-009;BT-010;UI-007。
- 验收：仅改因子配置且核心不变，信号订单按独立预期变化。
- 设计：[契约/方案](TESTING.md)；拟代码：`src/aqrp/services/;tests/integration/;tests/e2e/`；拟测试：`tests/integration/test_int_005.py`。
- 能力状态：Planned；设计状态：DRAFT_PRESENT；实际实现/测试证据：尚无（P0文档证据另见审查包）。

## INT-006 · 比赛执行/数据规则适配及通用模拟能力声明

- 来源：V3.0§1.2;V3.0§2.3;V3.0§18;V3.1§5；等级：Competition Ready；阶段：7；优先级：P1；模块：competition。
- 输入：正式比赛规则。输出：适配器/规则测试/能力清单。依赖：INT-002。
- 验收：未知规则明确外部阻断，不声称具体比赛验收通过。
- 设计：[契约/方案](INTERFACES.md)；拟代码：`src/aqrp/competition/`；拟测试：`tests/competition/test_int_006.py`。
- 能力状态：Planned；设计状态：DRAFT_PRESENT；实际实现/测试证据：尚无（P0文档证据另见审查包）。

## EXT-001 · GPT候选生成/公式检查/批评估/去重/稳健筛选/排序/审批

- 来源：V3.0§18;V3.0§1.2；等级：Advanced Research；阶段：POST7；优先级：P2；模块：extension。
- 输入：独立新阶段授权。输出：默认Candidate的候选池。依赖：INT-004;FACTOR-008。
- 验收：无代码审查自动测试OOS不得进入正式策略。
- 设计：[契约/方案](ROADMAP.md)；拟代码：`后续单独批准的扩展模块（尚未选型）`；拟测试：`tests/extension/test_ext_001.py`。
- 能力状态：Deferred；设计状态：DRAFT_PRESENT；实际实现/测试证据：尚无（P0文档证据另见审查包）。
