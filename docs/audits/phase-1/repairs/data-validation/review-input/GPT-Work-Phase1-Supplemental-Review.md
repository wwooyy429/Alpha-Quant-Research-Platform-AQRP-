# GPT Work 补充审核 — AQRP Phase1

**补充审核结论：发现阻断问题。** 在固定版本上确认 2 项 High 代码缺陷、1 项 Medium 代码缺陷，另保留 2 项 Medium 证据缺口。原有 102 项测试全绿，但本轮外置回归断言得到 **4 失败、2 通过**；失败与前三项问题直接对应。原始失败记录全部保留。

这份结论只表示本轮 **GPT Work 补充审核**，不表示 Gemini 关卡通过、用户验收或发布授权；不撤销、改写历史原报告及用户记录。

## A. 审核对象、权限、方法与覆盖范围

| 项目 | 本轮核实事实 |
|---|---|
| 仓库 | [Alpha Quant Research Platform](https://github.com/wwooyy429/Alpha-Quant-Research-Platform-AQRP-) |
| PR | [#2](https://github.com/wwooyy429/Alpha-Quant-Research-Platform-AQRP-/pull/2)，已 closed / merged，非正在开发的 Draft PR |
| 固定目标 | `18d51fbecc4a1526f2ab75d34874a0b25d00f6c1`，PR #2 最终 head |
| PR base | `502c6931dcfce50bee2f71a80524475fae6396bf`，为该 PR 历史 base；当前 main 已前进 |
| 业务审查锚点 | `74bdb9216c585d27de91123605aff0266ca028cc`；与本轮目标的 src/tests/tools/CI/锁/扫描配置无差异 |
| 审核日期/时区 | 2026-10-21，Asia/Shanghai；固定副本创建记录为21:14:17+08:00；具体命令/产物UTC时间见原始回执，报告生成时间见末尾 |
| 独立执行副本 | `C:/Users/11638/AppData/Local/AQRP/reviews/p1-18d51fb`，detached HEAD，目标 SHA，运行前 clean |
| 阅读用固定归档 | `C:/Users/11638/AppData/Local/Packages/OpenAI.Codex_2p2nqsd0c76g0/LocalCache/Local/AQRP/reviews/work-p1-18d51fb-20261021/source`，来自目标 SHA 的 git archive |
| 原开发副本 | `C:/Users/11638/AppData/Local/AQRP/checkouts/phase1-57461d5d-5de2-4c78-9b4e-5fad2b5ccb29`，实际为 Phase2 分支，HEAD `0b5107fa611af9d3a858440261b5321c83ca9fa4`，核查时 clean |
| 旧同步副本 | `B:/BaiduSyncdisk/学习/投资/量化/量化交易比赛/Alpha Quant Research Platform (AQRP)`，HEAD `5e3ea461be7b12291b2f6e9108484e263cd8ac7b`；15 个暂存路径，`tools/data_smoke.py` 另有未暂存差异 |
| 实际访问 | 本机文件只读、Git 对象/远端 refs 读取、GitHub 连接器的 PR/Actions 读取及产物下载；仅在独立副本获取 CI 临时提交对象，未创建审计分支 |

Windows 应用对 LocalAppData 路径有重定向；执行环境解析后的真实根为 `C:/Users/11638/AppData/Local/Packages/OpenAI.Codex_2p2nqsd0c76g0/LocalCache/Local/AQRP/reviews/`，独立源码、venv、缓存、快照和本轮产物均位于该非同步目录树。

已读取用户规定的治理、架构、接口、需求/追踪、阶段、契约、测试、验收、Phase1 计划/SDK/复现/实现追踪，以及最新 Gemini 原件、补充包索引、开发方勘误和证据索引；需求按本轮 14 项定向核对。检查了全部 Phase1 core/data 源码、已有测试、锁和 CI/扫描工具。旧同步副本仅检查 Git 状态及差异统计，其草案不混入本轮代码结论。

执行方法：先核实事实，再审阅脚本；以标准 GIL/x64 CPython 3.13.16 在独立副本运行原版 `tools/ci.py`；使用其新建 venv 中安装的目标 wheel 进行额外端到端反例和外置回归；对四份新旧 CI ZIP 实际重算哈希、校验八表并回放查询。本轮未执行真实源、账户、订单、外部因子插件或 P2–7 功能。

权限遵守：未改正式源码/测试/Golden/锁/项目状态/Gemini 原件；未提交、推送、修改 PR 内容、发消息、合并、打标或发布。仅生成本轮报告和隔离验证产物。PR 链接附在当前聊天附件中，未向开发对话发送任何内容。

## B. 授权及阶段边界核对

1. `phase0-baseline` 剥离目标仍为 `7de1d0e81385ae97f98ea673fe05dd726f0b577b`，附注对象仍为 `0b2230cd4861ca3b47fa30fc30dae9f4dc4109d0`；未发现稳定标签移动。
2. Phase1 历史分叉点为 `502c6931dcfce50bee2f71a80524475fae6396bf`。合成数据/通用契约和 Python 3.13.16 的启动授权已有记录，本轮未重复申请启动许可。
3. 当前 PR #2 已合并为 `9b843b17ccf362cf5b7a5351269559a627c55b32`。Git 对象的双父为历史 main502c693 和目标18d51fb，完整 tree 与目标均为 `16aa34f613f0b0a094dc6ce3f44465224ea54299`。
4. 当前 main 与 `phase1-baseline` 剥离目标均为 `f579b2c99e762085772de6e70ba1fa98792a7add`；标签对象 `1a8e47ee4be910aa7eeeefa430015e683a8aa6f5`。目标→发布版的业务目录/测试/工具/CI/锁无差异。本轮不宣称对发布追加的全部资料进行了新的完整 Gemini gate。
5. 发布记录保存用户原话“phase 1验收已完成”和另行的“请开始合并并打标签”，绑定接收时版本；本轮独立核实了记录和 Git 事实，但无法认证另一聊天的全部原始对话。**没有把审核建议登记为用户 ACCEPTED/RELEASED，也未推定用户逐项接受执行限制。** `specific_execution_limitations_waiver` 仍为 NOT SEPARATELY SPECIFIED。
6. 当前原开发副本已有 Phase2 启动记录与代码。这与本次贴入说明中的历史状态有时间差；本轮只说明冲突，不据此启动、修改或审核 Phase2，也不把后来事实当作本次新增授权。
7. Gemini 计划预审、实现报告、补充勘误、CI、开发方执行、GPT Work 本轮执行与用户批准分别记录。最新补充包并未补齐完整 Gemini SDK/ZIP 独立执行。不能从绿色 CI 或本轮 GPT 执行自动关闭此缺口。

## C. 按严重度排序的问题清单

### WORK-P1-001 — High — 成交量/金额校验不区分单位维度

- **类别：代码缺陷。需求：DATA-001、DATA-006、DATA-011、QA-002。目标 SHA：`18d51fbecc4a1526f2ab75d34874a0b25d00f6c1`。**
- 位置：`src/aqrp/data/quality.py`，`normalize`，142–147 行；`src/aqrp/core/units.py`，`convert`，42–55 行。[源码定位](C:/Users/11638/AppData/Local/Packages/OpenAI.Codex_2p2nqsd0c76g0/LocalCache/Local/AQRP/reviews/work-p1-18d51fb-20261021/source/src/aqrp/data/quality.py:142)
- 复现输入：取固定 `tests/golden/phase1_input.json`。第一个 bar 设置 `volume='1.25', source_volume='1.25', source_volume_unit='currency'`。另一独立用例设置 `amount='3', source_amount='3', source_amount_unit='share'`。其余字段不变。
- 最小步骤：调用 `publish_snapshot(tables, PROVENANCE, 独立输出目录)`，再调用 RAW `query`；或运行外置回归 `test_work_p1_001_reject_wrong_unit_dimension`。
- **预期：** 错误维度应被隔离并阻断发布；volume 最终应符合 SYNTHETIC_V1 的 share_unit=1，不因来源单位分支绕过。
- **实际：** 两种输入均发布成功，查询返回 VALID；第一种 `volume=1.25000000`，第二种 `amount=3.00000000`。`convert` 的通用单位集合被两个字段共用，整数股数检查又只在 unit=share/lot 时执行。
- 影响及阻断：货币可被当作股数、股数可被当作金额，并绕过整股约束。错误被封存为 PIT_VERIFIED，影响数据解释及后续用量计算。**阻断本轮技术通过。**
- 最小修复：在字段入口限定 volume 为 share/lot、amount 为 currency/thousand_currency；转换后独立验证目标维度的最小单位。保留 Decimal 精度、正确换算和既有 Golden。
- 复核：两项反例均拒绝发布；3手×100股=300、1.25千币=1250仍通过；补正向及错误维度/分数股边界测试，并在新完整 SHA 重跑适用套件。

### WORK-P1-002 — High — 除权日与生效时间冲突仍被计入总回报

- **类别：代码缺陷。需求：DATA-002、DATA-004、DATA-006、QA-002。目标 SHA：`18d51fbecc4a1526f2ab75d34874a0b25d00f6c1`。**
- 位置：`src/aqrp/data/quality.py`，`normalize`，153–171 行，只验证行动字段存在/类型/金额等；`src/aqrp/data/actions.py`，`action_view`，46–63 行，仅按 effective_at 选入分红。[行动计算定位](C:/Users/11638/AppData/Local/Packages/OpenAI.Codex_2p2nqsd0c76g0/LocalCache/Local/AQRP/reviews/work-p1-18d51fb-20261021/source/src/aqrp/data/actions.py:46)
- 复现输入：固定输入中 SYN_A 两日 close 为100、98；新增每旧股现金分红2，announcement/available 为2024-01-01T00:00Z，`effective_at=2024-01-03T00:00Z`，`ex_date=2024-01-04`，source_timezone=UTC。
- 最小步骤：发布该输入，在 cutoff `2024-01-03T12:05:00Z` 查询 Jan2–Jan3 的 total_return_index。原始完整输入保存在 `probe-results.json` 的 `dividend-exdate-mismatch` 项。
- **预期：** 合成契约采用 ex-session 收盘再投资，不能无解释地同时接受 Jan3 生效和 Jan4 除权。应在归一/发布阶段拒绝冲突；若解释为 Jan4 分红，Jan3 不应加2，指数应为0.98。
- **实际：** 行动标为 VALID、快照发布成功，指数为 `[1.0,1.0]`；Jan4 的 ex_date 没有参与时序校验，分红已计入 Jan3。
- 影响及阻断：输入中的行动日期语义冲突会静默改变历史总回报，hash 自洽不能证明经济时序正确。**阻断本轮技术通过。** 该反例证明的是冲突日期未拒绝，不泛称普通有效行动存在普遍前视泄漏。
- 最小修复：沿用既定 SYNTHETIC_V1 的 ex-session 口径，校验 effective_at、ex_date、源 IANA/所属 session 的关系；无法规范化时明确拒绝，不擅自改为按 pay_date 计算，也不扩大到 P5 账本。
- 复核：冲突日期拒绝；合法100→98加2的毛总回报仍为0；补本地日期跨UTC、晚到修订、已公告未生效及不支持组合的边界。正确答案/容差不改。

### WORK-P1-003 — Medium — 价格缺失会跳过已知 OHLC 矛盾

- **类别：代码缺陷。需求：DATA-006、QA-002。目标 SHA：`18d51fbecc4a1526f2ab75d34874a0b25d00f6c1`。**
- 位置：`src/aqrp/data/quality.py`，`normalize`，138–141 行，OHLC_ORDER 被 `all(v is not None for v in prices)` 包围；151–152 行随后归类 MISSING。[OHLC校验定位](C:/Users/11638/AppData/Local/Packages/OpenAI.Codex_2p2nqsd0c76g0/LocalCache/Local/AQRP/reviews/work-p1-18d51fb-20261021/source/src/aqrp/data/quality.py:138)
- 输入/步骤：固定输入第一个 bar 设置 `open=100, high=90, low=95, close=None`，发布并 RAW 查询。
- **预期：** 虽缺 close，但 low>high、open>high 已确定违反价格区间，应 rejected、严格发布失败；仅缺 close 而其余价格合法的行仍可 MISSING。
- **实际：** 快照发布成功，返回 MISSING/NULL_OBSERVATION，同时保留上述互相矛盾的已知价格；rejected=0。
- 影响及阻断：无效与缺失混同，调用者请求 open/high/low 时可能消费矛盾数据。严格异常隔离是本阶段标准，**本项 Medium 也阻断本轮技术通过**。
- 最小修复：对所有已知字段做可判定的成对约束，不因一个字段为 null 跳过 low≤high、low≤open≤high、low≤close≤high。保留合法 null 和零量语义。
- 复核：本例拒绝；合法部分缺失正例通过；已有六行分类计数及输入守恒保持正确。外置两项正向控制均已通过。

### WORK-P1-004 — Medium — Gemini 全量独立执行证据仍未补齐

- **类别：证据缺口。需求：QA-002、ENV-001、ENV-002；治理关联 GOV-008。目标 SHA：`18d51fbecc4a1526f2ab75d34874a0b25d00f6c1`。**
- 位置：`docs/audits/phase-1/gemini/VERIFICATION_PACKAGE_INDEX.json` 第125行；归档 `aqrp_phase1_recheck_execution.py` 第22、25–56、60–76、93行。[归档脚本定位](C:/Users/11638/AppData/Local/Packages/OpenAI.Codex_2p2nqsd0c76g0/LocalCache/Local/AQRP/reviews/work-p1-18d51fb-20261021/source/docs/audits/phase-1/gemini/verification-package-8bf189d/contents/aqrp_phase1_recheck_execution.py:60)
- 最小核对：打开补充脚本，对照提供日志和包内成员。实际文件存在时计算六个哈希；缺输入仅打印 MISSING；Git拓扑/裁定直接输出常量。脚本没有 SDK/pytest/ZIP/Git 实际调用。
- **预期：** 完整独立执行的声明需对应指定解释器、SHA、真实命令、原始输出和产物。
- **实际：** 33832字节补充ZIP及10成员hash已核实；有真实hash脚本和日志，不能继续声称完全没有执行附件。但没有与完整SDK或Actions内部/跨OS独立运行相匹配的新增代码/命令/日志；原日志Python3.11.2，不满足SDK3.13.16要求。
- 影响/阻断：这是“没有证据证明该专项完成”，不等于已证明数据计算错误。**阻断将 Gemini 专项标为完整通过**；已有用户验收/发布事实继续分别保留，不凭本报告改写历史授权。
- 最小处置/复核：保留 P1-SDK-EXEC-OPEN；由有权限的 Gemini 审查环境对修复后的新固定 SHA 真实执行并另存原始回执，或由用户另行明确裁定证据限制。本轮 GPT Work SDK/ZIP执行只记本轮归属，不能代签 Gemini。不得修改旧脚本或原报告掩盖事实。

### WORK-P1-005 — Medium — 新旧 Actions ZIP 均不含完整构建字节

- **类别：证据缺口。需求：ENV-001、ENV-002、QA-002。目标 SHA：`18d51fbecc4a1526f2ab75d34874a0b25d00f6c1`。**
- 位置：`.github/workflows/ci.yml` 第32–36行的上传白名单；`tools/ci.py` 第110–112行记录并安装项目 wheel、第139–146行只列根文件。[上传配置定位](C:/Users/11638/AppData/Local/Packages/OpenAI.Codex_2p2nqsd0c76g0/LocalCache/Local/AQRP/reviews/work-p1-18d51fb-20261021/source/.github/workflows/ci.yml:32)
- 复现：下载本轮 head 对应 run39581713605 的 artifact12338115029/12336921248，校验官方digest后遍历根 artifacts.json；同时读取旧run39476825340归档的两个原始ZIP。
- **预期：** 每个文件按“原字节已保存/仅摘要/未上传”逐项归类；若声称完整安装/构建可复核，应有实际被安装项目wheel等对应字节，不能凭新构建替代旧产物。
- **实际：** 四份ZIP均根清单11/14可复算，缺 `.coverage`、`gitleaks(.exe)`、`pip-26.2.1-py3-none-any.whl`。项目wheel亦缺，其摘要在environment.json，**不属于根14条中的第4条缺项**。缺项不是下载损坏；上传范围本来不含这些路径。
- 影响/阻断：不能核实这些旧字节及CI实际项目wheel摘要；已存在的JSON/XML、八表、Manifest和smoke均通过实际复算。**不单独判定数据功能失败，但阻断“14/14齐全”或完整wheel原字节验证的声明。**
- 最小处置/复核：后续CI保存项目wheel及计划要求保留的原字节，清单覆盖实际上传内容或明确列 omitted；旧字节不可恢复项继续标NOT VERIFIED，不用本地新wheel伪补历史。证据策略如保留精简，须清楚披露并依既有授权流程处置，本轮不代作接受决定。

## D. 需求 → 实现 → 测试 → 原始证据 → 状态

下表状态是本轮技术核对，不改正式需求表或用户验收状态。“已测范围通过”不表示穷尽所有输入。`SDK` 指本轮新建环境完整执行；`ZIP` 指本轮实际校验四份原始产物并回放；原始证据入口见 E。

| 需求 | 实现 | 原有测试/参考 | 本轮证据与状态 |
|---|---|---|---|
| DATA-001 | schemas/quality/query、units | test_data_001_002_pit_microseconds_and_revisions；source_units_survive_pipeline | SDK跨市场同symbol隔离通过；WORK-P1-001 阻断单位维度 |
| DATA-002 | time、pit.visible_rows、query._load/_effective | test_data_002_*；晚到status/alias及revision单调 | 源码顺序为先event/available过滤→可见修订→有效区间；SDK对应边界通过；行动日期另见002 |
| DATA-003 | time.localize/iana、quality/synthetic日历 | DST/local_date/cross_timezone_roundtrip、session关系 | SDK拒绝naive/纯日期/非零纳秒，接受session_date；DST/fold/半日/跨UTC测试通过；非交易所认证 |
| DATA-004 | actions.action_view、query | 拆股/分红/future_action、守恒、multi-split拒绝 | 正常已知答案通过；WORK-P1-002 冲突ex_date未拒绝阻断 |
| DATA-005 | pit、query.universe_at/status_at/aliases_at | late_status_universe_and_alias；overlapping_alias_and_universe | SDK历史退出/停牌/换码可见性、半开区间通过；未发现已测范围的新阻断 |
| DATA-006 | quality.normalize/validate_table/validate_dataset | 分类计数守恒、错误字段、冲突重复 | SDK已有六行/重复测试通过；WORK-P1-001/002/003显示异常校验缺口 |
| DATA-007 | snapshot.publish/_verify/safe_path、canonical | hash_tamper/path_traversal/symlink/forged_manifest/cleanup | SDK篡改、越界、混合快照等通过；阅读确认hash后从同一binary解码；ZIP各8表验证通过 |
| DATA-008 | synthetic/store/snapshot | frozen_input_pipeline、roundtrip_and_rebuild | SDK及ZIP Arrow/Parquet/DuckDB回放通过；DuckDB每次从核验Arrow重建内存索引 |
| DATA-009 | query/pit、DataView独立IPC副本 | mutations_and_positive_control；order_independent_reference | SDK未来价格/迟到修订/行动/成员/日历mutation及正向控制通过；Pandas/Arrow副本隔离不等于插件沙箱 |
| DATA-011 | units、quality | Decimal边界/换算性质/源单位保留 | 精确金额及正常换算通过；WORK-P1-001 阻断维度/最小股数绕过 |
| ENV-001 | pyproject/requirements.lock、ci | exact_runtime_and_imports | 本轮3.13.16/x64/标准GIL、22活动锁包版本、hash安装、pip check、wheel通过；CI wheel字节缺口005 |
| ENV-002 | CI固定Actions SHA/只读权限、ci工具 | 实际Windows/Ubuntu矩阵 | GitHub API success与ZIP原始environment/JUnit对上目标tree；失败上传if:always；005保留 |
| SEC-002 | secret_scan.py、精确allowlist | gitleaks8.30.1及hash、正负控制 | SDK扫描及控制通过；白名单限定单个历史完整行hash+路径，未见扩大豁免；无真实交易调用 |
| QA-002 | tests/data/integration/environment、Golden、独立参考/覆盖工具 | Fraction/Decimal常量和实现前答案 | 原102通过，但外置4失败证明关键反例缺测；001–003阻断，004–005证据分级保留 |

测试质量核对：期望来源可追到实现前 GOLDEN_REFERENCE，已有基础收益用Fraction推导，未发现用待测SDK生成上述期望。独立参考脚本只验证列出的基础常量，不等于全SDK参考实现。`tests/golden`本身是fixture而非独立pytest测试目录。覆盖工具实际逐模块执行门槛，无coverage业务排除；quality行100%/分支98.413%，query行98.718%/分支95.833%，仍未覆盖本次语义反例。绿色数量与覆盖不能单独证明正确。

## E. 实际验证、失败记录及 NOT VERIFIED

### EXECUTED — GPT Work 补充验证

| 验证 | 实际结果/来源 |
|---|---|
| 固定版本/refs/差异 | 独立副本detached clean；远端PR head、main、两个附注标签核实；读取两原副本status/暂存与未暂存统计；未清理Git锁 |
| 当前验收清单 | acceptance/MANIFEST 的487项hash全部匹配；旧历史清单未误当当前清单 |
| Gemini补充包 | 原ZIP SHA256 `318323ff77651537cc47470fe20d32930bb07495bb51fd71f0772f80c11c023d`，10成员逐项匹配；脚本只读审查，本轮未重新执行其常量裁定 |
| 全量SDK | run_id `aqrp-b3151194-e140-41c1-ab75-baaf42589142`，目标18d51fb，dirty=false，complete=true，外层exit0；102测试/0失败/0错误/0跳过；锁安装、wheel、ruff、逐模块覆盖、独立基础数学、smoke及扫描/控制均通过 |
| 本轮本地项目wheel | SHA256 `1582ec6205058dd45c6c868ee243c1f51c7f9889f0a49e0d7056e2ba23ea36e8`；实际新建环境构建及安装，不能替代历史CI wheel |
| 锁与实际环境 | lock SHA256 `86c7bf65c9a9690036006360062c8cd10a91279705b4070af7033d7699abffeb`；22个当前平台活动包版本匹配；CPython3.13.16、x64、GIL enabled、非free-threaded |
| 定向探针 | `probe.py` exit0是观察脚本正常结束；已记录各错误输入被接受，**不表示功能通过**；完整输入/输出及快照均保留 |
| 外置回归 | 6项中4失败、2通过，exit1；两种错误维度、行动冲突、部分OHLC矛盾分别失败；合法完整/合法部分缺失两个控制通过。未改仓库测试 |
| 最新CI原件 | run39581713605 attempt1；Windows job119160647533与Ubuntu job119160647162成功；下载ZIP并按API官方digest重算，两端JUnit均102/0/0/0 |
| 最新CI实际代码 | environment记录checkout `c0dd568dcaf2e74e82c3df4c417279b5d9166c1f`；本轮先遇到本地对象缺失，保留原失败，再只在独立副本fetch该对象，实核双父502c693+18d51fb，完整tree与目标一致 |
| 四ZIP回放 | 两新ZIP加两旧归档ZIP；安全检查路径/链接/重复/体积/CRC，实际核对每份11可用根文件、8表文件hash/Manifest、SDK verify与query回放；同run跨OS八表逻辑值、smoke原字节、固定业务配置一致 |

四ZIP的实际SHA256：

| run / 平台 / artifact | SHA256 |
|---|---|
| 39581713605 / Windows /12338115029 | `13cea520aa96ac63619e353fb55a45e580571cdd8da85485a820f119894d3864` |
| 39581713605 / Ubuntu /12336921248 | `075094178e27d6a3bc829cd273fbdf044e1f4ab32387a42cb40668a9f760377f` |
| 39476825340 / Windows /12288679676 | `8f092b7214202292995276a4dab3187063cd481d8a6556ac342e450738b64ea5` |
| 39476825340 / Ubuntu /12288989083 | `73385602dad830f3157dba8f5629616127777511830b02675fd06df517f93e7c` |

旧run实际checkout为 `f093faca9a9dd4977caa1142267ff494766d3c7e`，其tree与业务74bdb92等价。两次run分别核对，未将旧PASS直接外推至新SHA。ZIP中coverage门禁是读取原报告再核验；本地SDK的102项才是本轮重新执行测试。Linux本轮未新建环境运行。

### 失败与限制明确保留

- 首次长路径独立checkout失败；该失败副本未清理，最早会话工具输出被长度限制截断，**没有完整落盘的首次checkout stderr，不伪称其完整保全**。第二副本初次SDK因本副本未启用core.longpaths导致Git误报dirty而exit1，environment/console保留；只设置本轮副本的Git长路径配置后确认clean并成功运行，未改系统Git或正式副本。
- 本轮外置回归4个失败完整stdout/stderr与JUnit保留，不删除、不改Golden来变绿。
- ZIP首次拓扑读取缺c0对象的exit128原始记录在zip-verification.json保留；后续成功fetch/对象日志另存，不覆盖首次失败记录。
- 新旧CI每端3项根文件及项目wheel原始字节不可复算，见005。下载成功不等于不存在缺项。
- **NOT VERIFIED：** Gemini完整指定SDK及原始ZIP独立执行；本轮新的Linux干净执行；本轮Conda直接运行/VS Code GUI；真实供应商历史available_at真实性、真实交易所profile认证、未授权账户/订单、后续阶段功能。
- 本轮没有把此前开发方Conda直接验证与隔离安装混写。历史开发方Conda和发布SDK记录已读取，其执行归属保留；本轮是独立新venv，未修改开发者conda或系统默认Python。
- 探针另观察到“master listing_at为Feb1、Jan2 bar仍可发布”。这一接受行为已有输出，但上市时间应怎样结合历史master修订判定，未在本轮建立足够完整的契约/边界证明，**暂不另列确证缺陷或强加修复要求**。它不计入前三项确认问题或四项失败断言。

原始证据快捷入口：

- [实际SDK命令与输出](C:/Users/11638/AppData/Local/Packages/OpenAI.Codex_2p2nqsd0c76g0/LocalCache/Local/AQRP/reviews/work-p1-18d51fb-20261021/runs/aqrp-b3151194-e140-41c1-ab75-baaf42589142/commands.log)
- [SDK环境](C:/Users/11638/AppData/Local/Packages/OpenAI.Codex_2p2nqsd0c76g0/LocalCache/Local/AQRP/reviews/work-p1-18d51fb-20261021/runs/aqrp-b3151194-e140-41c1-ab75-baaf42589142/environment.json)
- [外置回归原始失败日志](C:/Users/11638/AppData/Local/Packages/OpenAI.Codex_2p2nqsd0c76g0/LocalCache/Local/AQRP/reviews/work-p1-18d51fb-20261021/regression.stdout-stderr.log)
- [外置回归脚本](C:/Users/11638/AppData/Local/Packages/OpenAI.Codex_2p2nqsd0c76g0/LocalCache/Local/AQRP/reviews/work-p1-18d51fb-20261021/test_work_p1_regressions.py)
- [端到端完整反例输入输出](C:/Users/11638/AppData/Local/Packages/OpenAI.Codex_2p2nqsd0c76g0/LocalCache/Local/AQRP/reviews/work-p1-18d51fb-20261021/probe-results.json)
- [四ZIP逐项核对结果](C:/Users/11638/AppData/Local/Packages/OpenAI.Codex_2p2nqsd0c76g0/LocalCache/Local/AQRP/reviews/work-p1-18d51fb-20261021/zip-verification.json)
- [CI缺失对象补取与tree核对](C:/Users/11638/AppData/Local/Packages/OpenAI.Codex_2p2nqsd0c76g0/LocalCache/Local/AQRP/reviews/work-p1-18d51fb-20261021/ci-topology-object.log)
- [Git事实命令回执](C:/Users/11638/AppData/Local/Packages/OpenAI.Codex_2p2nqsd0c76g0/LocalCache/Local/AQRP/reviews/work-p1-18d51fb-20261021/facts/commands.json)
- [环境与覆盖率汇总](C:/Users/11638/AppData/Local/Packages/OpenAI.Codex_2p2nqsd0c76g0/LocalCache/Local/AQRP/reviews/work-p1-18d51fb-20261021/environment-summary.json)
- [GitHub PR原始查询](C:/Users/11638/AppData/Local/Packages/OpenAI.Codex_2p2nqsd0c76g0/LocalCache/Local/AQRP/reviews/work-p1-18d51fb-20261021/github-pr2.json)

## F. 给 Codex 的修复任务单与复核清单

本节由用户转交；本轮未向开发者或其他聊天发送消息。所有状态均为审查建议，不能直接代写验收或批准记录。

| 优先顺序 / ID | 最小修改范围 | 保留项 | 验证与关闭条件 |
|---|---|---|---|
| 1 / WORK-P1-001 | quality字段单位维度约束及必要units目标最小单位校验；对应测试 | 既有share/lot/currency/thousand_currency合法转换、Decimal、混币拒绝 | 两个外置反例均拒绝；补字段交叉单位矩阵及合法控制；新SHA完整SDK/CI |
| 2 / WORK-P1-002 | action输入的ex_date/effective_at/session/IANA一致性验证；必要时明确拒绝不能规范化组合 | 原RAW、拆股、100→98加2、旧股口径、已有容差及P1边界 | 冲突日期拒绝；跨本地日期、晚到、未来生效、修订与正常行动对照通过 |
| 3 / WORK-P1-003 | quality中已知OHLC成对校验；对应测试 | 合法null、不补0、零量、计数守恒 | 违反已知区间必拒绝；合法部分缺失仍通过；六行分类原答案不变 |
| 4 / WORK-P1-005 | 后续CI上传与产物清单；不补造历史字节 | 原始ZIP/digest/环境/失败日志 | 保存实际项目wheel并hash核对；声明应保存项全在，或明确精简缺项和证据等级；旧缺项保持历史 |
| 5 / WORK-P1-004 | 审核资料中当前执行分级及新独立回执 | Gemini原件/正确答案/历史失败/用户原话 | Gemini在修复新SHA的真实执行，或用户另行决定；GPT输出不冒充Gemini |

修复后需提交**新的完整40位SHA**，给出父SHA、修改文件、问题ID→commit→测试→原始产物映射，保持固定范围；由开发者按实际适用工作流提出修复，不能复用已合并PR#2作为仍开放PR，也不能擅自移动稳定标签。修复源自Phase1缺陷，不能据此扩展P2–7功能。

复核清单：前三项新反例全部满足预期；两项合法控制不回归；既有102及新增测试实际运行、逐模块门槛与扫描控制均通过；Windows/Linux新CI明确run/attempt/head/checkout及tree关系；保全成功与失败日志；新wheel/Manifest/八表和跨OS结果可核；正确Golden、容差与核心契约未经授权不改；新独立报告固定SHA。未提交的新本地改动仍只能称“本地待同步草案”。

**最终选择：发现阻断问题。** 仅为本轮 GPT Work 补充审核；本轮不能签署技术全面通过，也不能签署 Gemini独立执行已完成、用户接受证据限制、用户验收或任何新增合并/标签/发布/下一阶段授权。

报告生成时间：2026-10-21T21:29:39.015249+08:00（Asia/Shanghai）。
