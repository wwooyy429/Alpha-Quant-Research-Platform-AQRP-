# Phase 1 数据系统实施计划（Gemini实施前预审）

状态：**阶段已获用户授权；PLAN REVIEW REQUIRED；业务实现尚未开始**。日期2026-10-20（Asia/Shanghai）。本计划由开发方编写，不是独立审计结论。用户选择合成数据及通用契约，并批准Python 3.13.16，原话见AUTHORIZATION.json。

## 基线及预审关卡

- 从核实main `502c6931dcfce50bee2f71a80524475fae6396bf` 创建 `feature/phase-1-data-system`。
- Phase0已发布且Gate PASS；稳定标签phase0-baseline仍固定 `7de1d0e81385ae97f98ea673fe05dd726f0b577b`。502c693仅含此后门禁原文/状态归档，需求与核心契约相同。
- 遵守AGENTS及V3.2 Step1–3：计划/接口/答案候选→Gemini独立预审→处理阻断事项→实施及自测。当前没有可调用的Gemini连接，沿用用户传递固定SHA审查资料及原报告的流程，不用开发方或其他同模型代签。
- 本次先提交完整可审计划及草稿PR；不提前创建src、运行环境、锁文件或CI来假称预审已通过。获得计划预审结果后再按已授权P1范围实施；仍不自动合并main/发布或进入P2。

## 目标与范围

交付可验证的日频数据基础：证券/市场隔离、单位归一、带时区微秒时间、版本化合成日历、PIT查询、公司行动研究视图、历史股票池及状态、质量报告、不可变Parquet快照与DuckDB查询、环境锁定、自动化检查、无真实凭证的测试。

用户批准的首版为合成数据，不接入任何真实供应商/账户；合成profile和日历不得宣称符合某交易所。P1完成需覆盖全部14项P1条目，不能借MVP或合成范围删去PIT/行动/退市/质量/哈希/安全要求。

| 需求 | 交付 / 验收证据 | 拟实现与测试 |
|---|---|---|
| DATA-001 | security_id稳定、市场隔离、别名双时间、单位及原始来源可追溯 | data/schemas,normalize；test_data_001 |
| DATA-002 | 所有入口强制event/available双约束，按当时可见修订返回，未知可用性拒绝正式PIT | core/contracts,data/pit；test_data_002 |
| DATA-003 | 合成日历版本、假日/半日、DST、日期跨UTC边界；日期键不冒充timestamp | data/calendar；test_data_003 |
| DATA-004 | RAW封存、PIT拆股/总回报研究视图、行动可用/生效分离；无未来行动回填 | data/actions；test_data_004 |
| DATA-005 | 历史成员/停牌/退市的可用修订及生效区间，保留退市ID | data/universe；test_data_005 |
| DATA-006 | null/零量/重复/冲突/异常明确分类，计数守恒，不静默补零/跨证券填充 | data/quality；test_data_006 |
| DATA-007 | 不可变快照、canonical manifest、每片哈希与版本；篡改及路径越界拒绝 | data/snapshot；test_data_007 |
| DATA-008 | DuckDB/Parquet往返、合成数据加载、类型精度及可重建查询索引 | data/store,synthetic；test_data_008 |
| DATA-009 | 固定cutoff的可见投影不受未来记录/晚到修订/成员变化影响；正向控制有效 | tests/data与integration；test_data_009 |
| DATA-011 | Decimal精度/scale、share/currency转换及单币种校验，不经float处理金额 | core/units；test_data_011 |
| ENV-001 | 精确CPython/安装器/直接传递依赖/哈希，Windows与Linux干净安装证据 | pyproject,.python-version,requirements.lock；test_env_001 |
| ENV-002 | 从第一批正式代码建立固定SHA Actions、只读权限、安装/ruff/pytest/覆盖率/报告 | .github/workflows/ci.yml；test_env_002及CI真实run |
| SEC-002 | 无真实凭证、脱敏、固定版本秘密扫描器，正负控制与人工核查 | core/security,安全配置；test_sec_002 |
| QA-002 | 本阶段单元/契约/性质/集成/泄漏/回归与独立参考；仅G-RET基础收益原语，未来统计/回测保留Planned | core/math/simple_return，tests/quality/test_qa_002及本阶段测试集 |

表中名称为规划位置，完整前缀为src/aqrp或tests；REQUIREMENTS/CSV中的原ID、依赖、等级不改，业务状态目前仍Planned。DATA-010/012/013、FACTOR及研究/组合/风险/回测/UI不属于本阶段实现。

## 实施次序（仅在计划预审后执行）

1. **M1.1 工程基础**：用户批准CPython 3.13.16；核验安装来源/哈希、隔离venv、解析完整锁文件；同时提交包骨架、有效导入/安装测试和CI。GitHub未出现实际run前不得关闭F-002，不用空测试占位通过。
2. **M1.2 契约和单位**：只实现P1需要的dataclasses/错误/Arrow schema/Decimal原语；先封存独立预期，验证非法时间、源单位、精度和市场边界。
3. **M1.3 合成源和质量**：建立逐行固定的小样本与显式session表，再实现确定性种子生成器；生成器输出不能自己充当Golden期望。记录输入/重复/缺失/隔离计数。
4. **M1.4 快照与存储**：原数据与行动/状态/日历全部版本化，原子发布Parquet+manifest，DuckDB只作可重建索引；拒绝篡改、越界路径、混合版本。
5. **M1.5 PIT及派生研究视图**：统一SDK入口强制截止时间，覆盖别名/日历/成员/状态/行动的双时间修订；再接RAW/拆股/总回报视图，不实现账户或订单。
6. **M1.6 集成与审查**：Windows/Linux干净安装、全测试/静态/秘密扫描；冻结SHA、数据/环境/结果清单与真实CI链接，送Gemini实现复核；修复后新SHA重测，最后才申请P1人工验收。

## 允许及禁止文件

预审阶段允许：本阶段docs/audits/phase-1资料、必要授权/状态/决策/计划文档；不改P0原件、稳定标签、canonical CSV和核心已批准契约。

实施阶段计划允许：src/aqrp/core的data contracts/errors/units/canonical/security子集及G-RET唯一基础收益原语；src/aqrp/data；tests/data、tests/environment、tests/security、tests/quality、P1专用golden/integration；pyproject/.python-version/requirements.lock、CI和必要工具/说明。所有新增公共接口按DATA_IMPLEMENTATION_SPEC.md预审；若与P0契约冲突，先列影响并取得变更批准，不静默改P0。

禁止：因子执行/Registry、统计研究/OOS、组合/风险引擎、撮合账本/绩效、网页、研究/回测CLI、任意插件执行、真实数据下载或交易、外部凭证、分布式/微服务及P2验收。EXP服务仍P3；P1仅记录数据及安装/测试血缘，不提前实现实验管理平台。

## 测试、答案与验收标准

- 预期答案及计算依据见GOLDEN_REFERENCE.md，接口边界见DATA_IMPLEMENTATION_SPEC.md；均需Gemini预审，不把候选标为已独立签署。
- 关键time/PIT/units/actions/snapshot模块采用行覆盖≥95%、分支≥90%；其余P1核心≥90%/85%，并逐项覆盖列明的关键不变量。覆盖率不能替代已知答案、边界、性质和独立参考。
- 测试要求：完整14条映射、金额/数量精确、微秒时间及session正确、未知可用性拒绝、读写类型往返、输入顺序无关、重复幂等、损坏失败、mutation加正向控制。收益原语G-RET按既定abs1e-12/rel1e-10，不提前验证IC/回测。
- Windows x64与Linux x64均须在实际固定Python/依赖下干净安装并通过；保存OS镜像标识及环境hash。未运行的矩阵项标NOT VERIFIED，不称本地通过等于CI通过。
- F-003只有时间戳入口及相应PIT/DST/纯日期/naive负例真正实现且复核后才可关闭；session_date合法date不在禁止范围。
- 无新增High/Critical阻断；Medium逐项按正确性/安全/标准判断；Gemini实现审查、缺陷复核及用户验收分别完成。P1合并/发布与P2启动仍需各自授权。

## 风险及待核事项

Python精确版本已获用户批准，但本机只有可用3.10.11文档工具，注册的3.11不能启动；尚未安装3.13.16。DEPENDENCY_CANDIDATES仅为官方元数据及部分wheel哈希，非完整锁/兼容证据。合成PIT可验证不证明真实供应商历史可得性。Parquet/Arrow/DuckDB类型转换、DST折叠、revision选择顺序、行动分红口径、snapshot自引用及可变缓存均是重点预审风险。

代码工作区仍在百度同步目录，F-004物理隔离未完成；计划将venv、可变DuckDB缓存及运行产物放到本地非同步目录并记录解析路径，但这不等于整个代码工作区已物理隔离。若实施需额外迁移代码工作区，先明确范围，不把目录建议冒充已落实。

用户已授权启动P1，不需要重复请求启动许可；当前仍缺Gemini实施前预审。预审结论及所有阻断问题处理完成前，不进入业务实现。
