# GPT Work 补充审核 — Phase0 / Phase1 第二轮

**Phase0：本轮已检查的设计及发布链未发现新增阻断问题。Phase1：发现阻断问题，不能给出技术完整通过结论。**

本轮新增4项确认缺陷，沿用问题ID WORK-P1-006～009；此前001～005不改号、不自动关闭。累计：**3项High代码缺陷、4项Medium代码缺陷、2项Medium证据缺口**。Phase0的原Gemini执行来源限制继续披露，不把本轮复算当作Gemini执行。

## A. 对象、权限、版本与方法

| 项目 | 固定事实 |
|---|---|
| 仓库 | [AQRP](https://github.com/wwooyy429/Alpha-Quant-Research-Platform-AQRP-) |
| Phase0目标 | `phase0-baseline` → **7de1d0e81385ae97f98ea673fe05dd726f0b577b** |
| Phase0 PR | [#1](https://github.com/wwooyy429/Alpha-Quant-Research-Platform-AQRP-/pull/1)，merged；head `228190a0c46595cf2927125fdc7d4f1c51b39ccf`，历史base `e87d0082a5e448e9550129a486ba965f13a155f8` |
| Phase1本轮目标 | `main` / `phase1-baseline` → **f579b2c99e762085772de6e70ba1fa98792a7add** |
| Phase1 PR | [#2](https://github.com/wwooyy429/Alpha-Quant-Research-Platform-AQRP-/pull/2)，merged；head `18d51fbecc4a1526f2ab75d34874a0b25d00f6c1`，历史base `502c6931dcfce50bee2f71a80524475fae6396bf` |
| 上轮目标与本轮关系 | Phase1 PR head→本轮发布版，src/tests/tools/CI/锁/构建/扫描配置无差异，实际Git diff为空；本轮新增与旧反例直接从**发布版导出源码**导入运行 |
| 日期/时区 | 2026-10-21，Asia/Shanghai；固定副本导出记录21:31:58+08:00，完成时间见末尾 |
| 独立副本 | 本报告目录下 `phase0/` 与 `phase1/`，均为固定Git对象导出的归档，无漂移分支；导出Git库为上轮detached clean审核副本 |
| 开发副本实际状态 | 原开发目录为Phase2分支，核实时HEAD `947467b9d094905cab0af37ec5cc53f1d187e755`、clean；其较上轮前进，不属于本轮业务审核范围 |
| 实际工具与权限 | PowerShell/Python、只读Git对象及refs、GitHub连接器读取PR；没有修改正式仓库、PR、Golden、锁、原报告或用户状态 |

本轮沿用用户原始只读审核及隔离验证授权。没有发送其他聊天/人员消息、提交/推送/创建审计分支、合并、打标、发布，也未开展Phase2–7。

先核实版本及脚本，再执行。Phase0没有业务实现，不强求pytest/引擎/网页；检查V3.0全文、V3.1/V3.2、106条需求、架构接口/契约/六专项、Golden设计及批准/报告/发布链。原文档自查工具会重写SELF_CHECK/COMMAND_LOG/MANIFEST，因此**没有在固定资料中直接运行该工具**；本轮另写只读检查脚本，输出置于审核目录。

验证环境复用上轮隔离SDK创建的CPython3.13.16/x64/标准GIL及锁定依赖，未改其安装；额外回归显式从`phase1/src`导入本轮固定发布源码，完整模块hash及导入路径记录于regression-target.json。上轮102测试是上轮完整SDK实际执行；本轮不冒称又做了一次全量干净安装或新Linux执行。

## B. 阶段及授权边界

1. 两个稳定标签的对象及剥离SHA仍与上轮一致，未发现移动。Phase0附注对象 `0b2230cd4861ca3b47fa30fc30dae9f4dc4109d0`；Phase1附注对象 `1a8e47ee4be910aa7eeeefa430015e683a8aa6f5`。
2. Phase0实际merge `8c37e952be61054c6c72b5aaf573026c0355647b` 与获批PR head完整tree相同；随后发布登记只改批准/状态/证据记录。Gemini Gate针对P0固定基线的原件后续归档，不要求它出现在被审查的较早提交内。
3. Phase0用户原话“验收已通过，可以将PR #1 合并入 main 并打上标签”及绑定记录存在；Phase1用户验收、合并/标签授权与已发布事实也存在。这里只核实记录和Git事实，不代替用户作新决定，也无法认证另一聊天完整对话来源。
4. 发布基线内的旧“待Gemini/未发布”段落按其形成时点解释；后续Gate记录及当前refs是更新事实。不把旧历史段落直接列为当前越权问题。
5. Phase0原Gemini Gate自述只读远端核验，但没有附原始命令日志；本轮可重新核实Git事实，不能认证其原执行过程。Phase1完整Gemini SDK/ZIP独立执行仍NOT VERIFIED；本轮新增验证不能关闭这一角色要求。
6. 真实供应商、市场认证、账户订单与后续模块均未执行；15个P0算例是候选公式/数字复算，**不表示P2–P5业务实现或其验收已完成**。

## C. 问题清单与复现

本节所有新问题及旧问题的本轮适用目标均为完整SHA **f579b2c99e762085772de6e70ba1fa98792a7add**。原发现SHA及原始表述保留在上轮报告，不把它们改写为当时已审发布版。

### WORK-P1-006 — High — UNKNOWN_AVAILABILITY标记可进入正式PIT

- **类别：代码缺陷。需求：DATA-002、DATA-006、DATA-009、QA-002。目标SHA：`f579b2c99e762085772de6e70ba1fa98792a7add`。**
- 位置：`src/aqrp/data/quality.py`，`validate_dataset`，227–228行；`normalize`111–113行只在available_at为空时自动设置未知；`validate_table`203行则允许未知标记进入accepted。[源码](C:/Users/11638/AppData/Local/Packages/OpenAI.Codex_2p2nqsd0c76g0/LocalCache/Local/AQRP/reviews/work-p01-round2-20261021/phase1/src/aqrp/data/quality.py:227)
- 输入：固定phase1_input.json的任一行保持非空available_at，将quality_status明确设置为`UNKNOWN_AVAILABILITY`、reason_code为`SOURCE_HISTORY_UNVERIFIED`。
- 最小步骤：发布该输入，读取manifest，再调用正式RAW query。分别对bars_daily、security_master、calendar、universe_membership首行验证。
- **预期：** 正式发布应拒绝历史可得性未知的记录；仅有一个声称的时间戳不能覆盖明确未知标记。exploratory可保存原件，但正式query应拒绝。
- **实际：** 四类表输入全部发布为`PIT_VERIFIED`，正式query成功。bars反例直接返回带UNKNOWN_AVAILABILITY的价格；master/calendar未知元数据参与正常查询；成员表另用正式universe_at复核，也直接返回UNKNOWN_AVAILABILITY记录。验证器只看available_at是否None。
- 影响/阻断：绕过已批准的正式PIT准入边界；不表示已证明具体真实供应商造假，但平台确实把明确未验证记录升级为正式快照。**High，阻断技术通过。**
- 最小修复：正式数据集同时拒绝未知标记和缺失available_at；对master/calendar/成员/行动等辅助表统一约束，保留exploratory身份并在读取边界防御性检查，不允许静默改标为VALID。
- 复核：4个负例拒绝；已知可得性正例通过；exploratory可保存但所有正式SDK入口拒绝；新完整SHA运行新增及既有测试。

### WORK-P1-007 — Medium — Windows绝对路径绕过固定IANA数据库

- **类别：代码缺陷。需求：DATA-003、ENV-001、DATA-007、QA-002。目标SHA：`f579b2c99e762085772de6e70ba1fa98792a7add`。**
- 位置：`src/aqrp/core/time.py`，`iana`，12–16行。只以`/`拆分并排除空/点段，未拒绝Windows反斜杠/绝对路径，joinpath可转到包外。[源码](C:/Users/11638/AppData/Local/Packages/OpenAI.Codex_2p2nqsd0c76g0/LocalCache/Local/AQRP/reviews/work-p01-round2-20261021/phase1/src/aqrp/core/time.py:11)
- 输入/步骤：把锁定包的UTC TZif字节复制到本轮临时`external-clock.tzif`；将其Windows完整路径作为source_timezone；可先直接调用iana，再把固定输入各行source_timezone改为该路径并发布快照。之后只把外部文件替换为Etc/GMT+12的TZif字节，原manifest/Parquet不动，再verify_snapshot。
- **预期：** source_timezone必须是合法IANA键，只从锁定tzdata包读取；外部文件路径拒绝，不引入未纳入快照/环境的时区字节依赖。
- **实际：** 绝对路径被接受；快照先验证成功。同一快照、manifest_hash不变，仅包外时区文件变化，再验证变成`SnapshotMismatch: SNAPSHOT_INVALID`。完整前后hash及异常栈已保存。
- 影响/阻断：绕过package-only约束，源IANA语义不成立，快照验证依赖未封存的外部文件。**Medium，因可复现性/固定环境契约而阻断技术完整通过**；未声称这等同于任意代码执行或读取了真实秘密。
- 最小修复：先验证IANA键命名空间，拒绝绝对路径、盘符和Windows路径分隔符；确保资源解析仍在固定tzdata包内，保留合法America/New_York等键及既有DST规则。
- 复核：Windows路径负例拒绝；合法IANA、DST fold/nonexistent及跨UTC日期通过；再改包外文件不能影响合法固定快照。不要移动稳定标签来声称旧问题消失。

### WORK-P1-008 — Medium — int64溢出跳过质量报告直接抛异常

- **类别：代码缺陷。需求：DATA-006、QA-002。目标SHA：`f579b2c99e762085772de6e70ba1fa98792a7add`。**
- 位置：`src/aqrp/data/quality.py`，`normalize`60–62行仅检查非负Python int；`validate_table`210行在逐行捕获范围外创建Arrow表。[源码](C:/Users/11638/AppData/Local/Packages/OpenAI.Codex_2p2nqsd0c76g0/LocalCache/Local/AQRP/reviews/work-p01-round2-20261021/phase1/src/aqrp/data/quality.py:210)
- 输入/步骤：固定合法bar，仅设置`revision_id=9223372036854775808`（2**63），调用validate_table('bars_daily',[row])。
- **预期：** 该行超过int64 schema，应归类rejected=1、valid=0，有字段及原因；严格发布随后拒绝，不能宣称质量计数完整却丢失结果。
- **实际：** 规范化接受该Python整数，表构建阶段抛裸`OverflowError: Python int too large to convert to C long`，未返回QualityReport。负数已有正常rejected行为，最大合法int64也接受，说明缺的是上界。
- 影响/阻断：一个超界输入中止整批质量分类，无法获得约定逐行原因/计数。**不单独推定金融计算错误；属于必须修正的错误语义和质量报告缺口**，本轮已有High阻断，不据该问题另行扩大功能。
- 最小修复：按schema整数位宽做逐字段范围验证，在进入Arrow前转为结构化ContractError；保留坏行分类，避免仅在末尾吞异常后返回空成功表。
- 复核：2**63、负值、bool、字符串等均正常计数拒绝；2**63-1通过；input=各互斥分类和，严格发布仍拒绝非法数据。

### WORK-P1-009 — Medium — 第二段小数可绕过纳秒拒绝

- **类别：代码缺陷。需求：DATA-002、DATA-003、QA-002。目标SHA：`f579b2c99e762085772de6e70ba1fa98792a7add`。**
- 位置：`src/aqrp/core/time.py`，`utc`，24–30行；re.search只看第一个小数片段，随后fromisoformat可截断offset中的额外精度。[源码](C:/Users/11638/AppData/Local/Packages/OpenAI.Codex_2p2nqsd0c76g0/LocalCache/Local/AQRP/reviews/work-p01-round2-20261021/phase1/src/aqrp/core/time.py:24)
- 输入/步骤：`utc('2024-01-02T16:00:00.000000+00:00:00.000000001')`。
- **预期：** 1ns偏移不能以UTC微秒精确表示，应TimestampResolutionError或明确契约拒绝，不静默截断。若该offset格式不支持，也应明确拒绝。
- **实际：** 返回`2024-01-02 16:00:00+00:00`；检查只看到前面的`.000000`。删除主时间小数、仅保留offset的1ns时反而能拒绝，验证行为依赖字符串写法。
- 影响/阻断：非法精度可进入cutoff/时间归一入口，违反“所有timestamp入口拒绝非零纳秒尾数”。**Medium，阻断该精度要求完整通过**；不泛称正常微秒时间已有错误。
- 最小修复：明确支持的offset语法，对完整时间字符串做无损精度校验；拒绝不能精确承载的所有小数片段，不能先让datetime截断再检查。
- 复核：当前两种写法都拒绝；合法微秒、合法尾随0的纳秒表现、带偏移/DST、date与naive拒绝规则保持正确。

### 上轮问题的本轮状态（沿用ID）

| ID / 严重度 / 类别 | 需求 / 精确位置 | 本轮输入及实际结果 | 预期、最小修复及关闭条件 |
|---|---|---|---|
| WORK-P1-001 / High / 代码缺陷 | DATA-001/006/011、QA-002；quality.normalize 142–147、units.convert42–55 | volume使用currency且值1.25、amount使用share，发布版仍接受；2回归失败 | 拒绝错误维度；字段限定单位且转换后验目标最小单位；保留3手=300股/1.25千币=1250，需新SHA复核；阻断 |
| WORK-P1-002 / High / 代码缺陷 | DATA-002/004/006、QA-002；quality153–171、actions46–63 | effective_at Jan3而ex_date Jan4，仍接受；回归失败；上轮端到端指数为1.0而非排除该分红后的0.98 | 拒绝不能规范化日期冲突，保留正确ex-session口径/100→98+2答案；新SHA边界对照；阻断 |
| WORK-P1-003 / Medium / 代码缺陷 | DATA-006、QA-002；quality138–141 | open100/high90/low95/close=None仍接受；回归失败 | 已知OHLC成对约束；非法已知值拒绝、合法null保留；新SHA计数/正负控制；阻断 |
| WORK-P1-004 / Medium / 证据缺口 | QA-002/ENV-001/002；gemini/VERIFICATION_PACKAGE_INDEX.json125，归档recheck_execution.py60–76/93 | 原脚本仍只打印拓扑/裁定，没有新的完整Gemini SDK/ZIP执行证据 | 原报告不改；新固定SHA由指定独立角色真实补证，或用户另行决定；阻断“Gemini专项完整完成”声明，不代作验收决定 |
| WORK-P1-005 / Medium / 证据缺口 | ENV-001/002、QA-002；CI32–36，ci.py110–112/139–146 | 原Actions缺字节事实不变；本轮发布本地SDK另有实际项目wheel和coverage.sqlite，已核实，不再泛称发布材料也缺这些字节 | 后续CI保存wheel及约定原件/明确omit；新本地wheel不能替代旧CI字节；不单独否定八表功能，阻断“完整旧CI字节已复算”声明 |

以上旧问题的完整原复现、影响、原目标SHA和修复条件见：[第一轮完整报告](C:/Users/11638/AppData/Local/Packages/OpenAI.Codex_2p2nqsd0c76g0/LocalCache/Local/AQRP/reviews/work-p1-18d51fb-20261021/GPT-Work-Phase1-Supplemental-Review.md)。本轮固定发布版反例不混入旧同步工作树草案。WORK-P1-004/005并非新增代码缺陷，不能用其数量替代金融风险判断。

## D. 需求追踪与Phase0审查结果

### Phase0

- **106条、16组**：ID唯一、字段完整、设计文件存在、REQUIREMENTS和TRACEABILITY各条映射存在；依赖ID存在、无环、无跨未来阶段的硬前置；生成逐条CSV供转交。
- **原文语义定向核查**：V3.0 13模块和职责边界、Factor API/元数据/信号/替换、OHLCV/amount/日历/历史池/行动、研究五阶段及算子、统计/OOS/重复实验、组合/风控、事件/订单/账本/绩效、六页面/同核服务、实验复现、测试/Golden/授权与发布均有对应设计；V3.1六专项和V3.2角色/流程/资料包也存在。未识别新的明确功能族遗漏。章节/ID存在不能单独证明逐句语义完全无遗漏。
- **架构边界**：数据→因子→研究、组合/风险、独立事件引擎及账本所有权、标签隔离、UI同服务有明确设计；不强求尚未实现模块运行。MVP分层没有用来删去原必须功能。
- **Golden设计15例复算**：使用标准库独立实现、无AQRP导入；G-IC得0.893684824964417428…，符合原近似容差；Rank=.9、Tie=sqrt(3)/2、Z样本方差、ICIR=2、成本/买卖/部分成交/拆股/分红/最大回撤均核对。结果不是P3/P5软件测试PASS。
- **69/69文件hash**与P0基线清单匹配；P0归档5份报告hash与其接收索引一致；8份核心架构/接口/需求/数据/回测/研究/Golden/测试文档至P1发布版保持相同字节。
- **遗留限制**：原Gemini Gate无原始执行日志、F-004物理同步隔离历史限制没有被本轮认证。P0固定发布快照里的旧待核验文字，与后续Gate证据按时序区分。

**Phase0补充结论：已检查范围未发现新增阻断问题。** 不是对原审查执行来源、全部逐句语义或未来实现的无条件保证，不更改P0既有批准/标签。

逐条设计追踪：[106条需求CSV](C:/Users/11638/AppData/Local/Packages/OpenAI.Codex_2p2nqsd0c76g0/LocalCache/Local/AQRP/reviews/work-p01-round2-20261021/Phase0-106-Requirements-Trace.csv)。

### Phase1（本轮增量与已知问题映射）

| 需求 | 实现/测试 | 本轮证据与技术状态 |
|---|---|---|
| DATA-001 | schemas/quality/query、旧单位/跨市场测试 | 001仍OPEN；市场ID隔离已测范围无新增缺陷 |
| DATA-002 | time/pit/query；未知可用性、微秒测试 | 新006、009；原测试只覆盖available_at=None及首段纳秒，未覆盖本轮负例 |
| DATA-003 | time.iana/utc、calendar；DST/本地日期测试 | 新007、009；UTC微秒正向控制通过 |
| DATA-004 | actions及行动输入校验 | 002仍OPEN；本轮没有运行P5账本 |
| DATA-005 | universe/status/alias PIT入口 | 成员表UNKNOWN标记穿透属006；合法历史区间测试沿用上轮证据 |
| DATA-006 | quality表/数据集校验 | 001/002/003/006/008显示质量异常语义缺口；008是裸溢出异常非完整报告 |
| DATA-007 | snapshot及固定资源边界 | 新007显示外部时区依赖；519清单、发布八表/Manifest复算通过 |
| DATA-008 | synthetic/store/snapshot | 发布封存八表和原查询实际重放通过；不表示所有输入正确 |
| DATA-009 | 正式PIT边界/未来mutation测试 | 新006；既有mutation通过不能替代未知来源准入检查 |
| DATA-011 | units、source-unit校验 | 001仍OPEN；本轮未更改Decimal口径 |
| ENV-001 | 固定解释器/锁/tzdata/wheel | 新007；发布项目wheel实际hash及17个Python模块与发布源字节吻合 |
| ENV-002 | Actions上传/运行与固定SHA | 005保持；本轮不新发CI、不冒称main有push CI |
| SEC-002 | 原扫描/精确白名单 | 本轮只读取发布扫描证据；无新源码变动，未重新下载执行扫描器 |
| QA-002 | 已有测试+外置针对性回归 | 本轮16项中11失败/5通过；原102是上轮执行或发布开发方原件，归属分别记录 |

## E. 实际验证与NOT VERIFIED

| 本轮执行/核对 | 结果与限制 |
|---|---|
| Git/refs/PR元数据 | 两PR已merged，目标固定；P0/P1标签与main关系核对；P0合并tree与获批head一致；P1 head→release保护目录diff为空 |
| 只读结构/清单 | P0 69/69、P1发布519/519 hash一致；两版106/16及追踪/依赖结构通过 |
| 独立候选数学 | 15个候选算例计算并断言，exit0；未导入AQRP，无后续业务实现执行 |
| 新定向探针 | 未知标记四表正式查询均成功；int64上溢裸异常；外部IANA路径被接受；双小数字符串纳秒被截断；probe exit0是观察脚本结束，不表示功能通过 |
| 外部时区复现实验 | 固定快照先verify通过；只改审核目录的TZif文件，后verify失败；原数据/manifest未改，完整异常栈及前后hash保存 |
| **正式外置回归** | **16项 / 11失败 / 5通过，exit1**。新问题7项负例失败，旧问题4项负例仍失败；5个有效正向控制通过。未修改正式tests/Golden，未删除失败记录 |
| 发布SDK原件 | 按发布映射校验12个已归档根文件；项目wheel SHA256=`5c6f8ac12923cedd9a8594a0afd7c87ccdfb38fe9bda7affb236423cff42c412`，17个Python模块与本轮发布源逐字节相同；原JUnit102/0/0/0系开发方历史运行，非本轮新测试 |
| 发布数据SDK回放 | 从发布证据读取八表，verify_snapshot和迁址后的同配置query实际通过，结果字节与封存smoke一致 |
| 失败保全 | 本轮11项断言失败完整stdout/stderr/JUnit保留；定向探针捕获的OverflowError及外部时区异常栈保留；本轮未清理任何正式或失败资料 |

**NOT VERIFIED**：本轮新的全量干净安装/全量SDK及Linux运行；Gemini原始完整SDK/ZIP执行；另一聊天用户原话来源认证；真实市场历史可得性/交易所认证；P2–7实现与授权情况。本轮只检查到Phase2开发副本前进，不据此复审其业务内容。

关键原件：

- [完整回归失败日志](C:/Users/11638/AppData/Local/Packages/OpenAI.Codex_2p2nqsd0c76g0/LocalCache/Local/AQRP/reviews/work-p01-round2-20261021/round2-regression.log)
- [16项JUnit](C:/Users/11638/AppData/Local/Packages/OpenAI.Codex_2p2nqsd0c76g0/LocalCache/Local/AQRP/reviews/work-p01-round2-20261021/round2-junit.xml)
- [固定发布源/解释器/模块hash](C:/Users/11638/AppData/Local/Packages/OpenAI.Codex_2p2nqsd0c76g0/LocalCache/Local/AQRP/reviews/work-p01-round2-20261021/regression-target.json)
- [新反例完整输入输出](C:/Users/11638/AppData/Local/Packages/OpenAI.Codex_2p2nqsd0c76g0/LocalCache/Local/AQRP/reviews/work-p01-round2-20261021/round2-probe-results.json)
- [外部时区前后验证与栈](C:/Users/11638/AppData/Local/Packages/OpenAI.Codex_2p2nqsd0c76g0/LocalCache/Local/AQRP/reviews/work-p01-round2-20261021/external-timezone-results.json)
- [结构/清单/Git检查结果](C:/Users/11638/AppData/Local/Packages/OpenAI.Codex_2p2nqsd0c76g0/LocalCache/Local/AQRP/reviews/work-p01-round2-20261021/structure-and-math.json)
- [15个Golden独立计算](C:/Users/11638/AppData/Local/Packages/OpenAI.Codex_2p2nqsd0c76g0/LocalCache/Local/AQRP/reviews/work-p01-round2-20261021/independent-golden-math.json)
- [发布SDK原件校验与回放](C:/Users/11638/AppData/Local/Packages/OpenAI.Codex_2p2nqsd0c76g0/LocalCache/Local/AQRP/reviews/work-p01-round2-20261021/publication-evidence-check.json)
- [第一轮报告与证据入口](C:/Users/11638/AppData/Local/Packages/OpenAI.Codex_2p2nqsd0c76g0/LocalCache/Local/AQRP/reviews/work-p1-18d51fb-20261021/GPT-Work-Phase1-Supplemental-Review.md)

## F. 给Codex的增量修复任务及复核条件

由用户转交；没有向任何开发聊天发消息。修复建议不构成需求/架构变更批准或用户验收。

| ID | 最小修改范围 | 必须保留 | 验证要求 |
|---|---|---|---|
| 006（High，优先） | 正式数据集与查询准入统一检查UNKNOWN_AVAILABILITY，不只看时间戳为空 | exploratory原件保存、不得伪填available_at或改标VALID | 四表未知标记+缺时间+exploratory/正式SDK入口的负例及已知正例 |
| 007（Medium） | iana键解析/资源范围检查，封堵Windows绝对/反斜杠路径 | 锁定tzdata、合法IANA及DST规则 | Windows外部文件拒绝；合法IANA固定快照不受包外文件变化影响 |
| 008（Medium） | schema整数上界校验及逐行错误归类 | int64持久类型、QualityReport计数守恒 | 上溢/下溢/bool/字符串拒绝；最大合法int64通过；不得用空成功结果代替 |
| 009（Medium） | 完整timestamp/offset语法与无损精度校验 | UTC微秒、合法offset、合法零尾数、date与naive拒绝 | 双小数纳秒拒绝、正常微秒正例、DST/跨UTC日期回归 |
| 001–003 | 沿用上一轮最小单位/行动日期/部分OHLC修复 | 正确Golden/容差、RAW、ex-session和合法null | 本轮旧4个失败断言应全部转为满足原契约，5项正控保持通过 |
| 004–005 | 补充独立执行与新CI原始wheel等证据；保留旧缺项 | Gemini原件、历史日志/ZIP、用户原话 | 不用本地新原件补造旧CI或代签Gemini；新SHA证据归属清楚 |

Phase0：目前不建议为“整理旧状态”重写已发布基线或原报告。本轮新反例指向Phase1实现不完整遵守既定契约，先修实现；若需要修改核心契约，应另列影响/批准，不以改文档或Golden消除失败。

请开发者提供**修复后的新完整40位SHA**，关联父SHA、每个问题ID、最小diff、测试命令/解释器/退出码/完整失败与成功日志、Windows/Linux run/attempt/head/checkout、wheel/锁/快照/数据hash。关键修复在新SHA复核；不得移动稳定标签、直接合并main或自动启动后续阶段。若原工作正处于Phase2，应明确修复的Phase1回归范围，不能将本清单当作额外Phase2功能授权。

**本轮最终结论：Phase0已检查范围未发现新增阻断问题；Phase1发现阻断问题。仅为GPT Work补充审核，不代表Gemini关卡通过、用户接受执行限制、用户验收或任何新增发布授权。**

报告时间：2026-10-21T21:43:37.961119+08:00（Asia/Shanghai）。
