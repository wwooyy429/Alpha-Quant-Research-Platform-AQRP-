# GPT Work 补充审核：Phase 3 G1 计划预审

**结论：PLAN BLOCKED。** 15组候选算术正确；完整G1仍有2项High、3项Medium待处理。本结论针对计划、接口、数学候选和验收路径，不是P3实现失败，也不是P3用户验收、Gemini审查登记或发布授权。既有P3启动授权有效，无需重复申请。未合并、打标签或进入P4。

## A · 对象、范围与需求覆盖

- 仓库 / PR：[AQRP PR #5](https://github.com/wwooyy429/Alpha-Quant-Research-Platform-AQRP-/pull/5)，draft。
- 固定审查SHA：**`d10a55a7dd4bc9ca7793ed474bdc1b056916e96e`**，从PR描述AQRP_FIXED_REVIEW_SHA读取，先记录后checkout；结束时字段/head仍相同。
- 基线：`f26255fc40a3080bfa883ad64938f60036a14759`，main/phase2-baseline/v0.2.0同点。PR #3合并`bb6076f87f616a98feb98287d661830b102ad015`的tree与批准头`e50cd75bf461b6ba02856591d5ef968c622da609`相同。
- 核对时间：2026-10-22 01:43 Asia/Shanghai起；报告生成 2026-10-22T02:02:28.787931+08:00。
- 独立只读副本：[fixed checkout](<C:/Users/11638/AppData/Local/Packages/OpenAI.Codex_2p2nqsd0c76g0/LocalCache/Local/AQRP/reviews/p3-d10a55a>)，detached HEAD，起始/结束干净。实际开发副本仅定位和读状态，无修改。
- 本人执行身份：**GPT Work 补充审核**；不是Gemini，不把P2指定代执行扩写为本轮Gemini执行。
- 权限：读取GitHub/本地，独立副本运行已审阅验证，输出审查方证据；未改正式代码、测试、Golden、锁、状态或原审计。无权限/未实际执行的部署、正式Test、金融批准均NOT VERIFIED。

重新解析canonical：**106条、16组；phase=3为26条，23 MVP、3 Competition Ready**。需求快照完整逐字段等于CSV筛选结果；trace ID/tier/dependencies等于canonical。DATA-012、FACTOR-007/009、QA-004、INT-001均在。下面的“映射存在”只表示计划追踪，全部P3业务仍未实现；文件名不能代替行为设计。

CR=Competition Ready；接口列均来自P3 INTERFACE_DRAFT，独立答案来自GOLDEN_REFERENCE。完整原始输入/输出/定义/来源/计划代码/测试在 [canonical-phase3-coverage.csv](<C:/Users/11638/AppData/Local/Packages/OpenAI.Codex_2p2nqsd0c76g0/LocalCache/Local/AQRP/reviews/work-p3-g1-d10a55a/canonical-phase3-coverage.csv>)。

| ID | 等级 | 原始来源 | 原依赖 | 接口/服务映射 | 未来测试 | 覆盖/可达性评审 |
|---|---|---|---|---|---|---|
| DATA-012 | CR | V3.0§4.4;V3.0§7.3 | DATA-002 | ExposureSnapshotRef | tests/data/test_data_012.py | PIT侧车与缺失方向可取；真实连接/边界测试待实施。 |
| FACTOR-007 | CR | V3.0§3.4 | FACTOR-003 | Price-Volume | tests/factors/test_factor_007.py | PriceVolume两案正确；新准入/API及旧Ref路径见004。 |
| FACTOR-009 | MVP | V3.0§1.3;V3.0§3.5;V3.0§12.3;V3.0§18 | FACTOR-003;VALID-008 | ApprovalProposal | tests/factors/test_factor_009.py | 工程/研究/策略域分开正确；001及正式标准仍限制批准。 |
| RESEARCH-001 | MVP | V3.0§5.1;V3.0§12.1 | FACTOR-003 | ResearchRequest, StageScores, research | tests/research/test_research_001.py | 真实批量编排有步骤；须含全部阶段、失败记录及001/002/003闭环。 |
| RESEARCH-002 | MVP | V3.0§5.1 | RESEARCH-001 | ResearchRequest, StageScores, research | tests/research/test_research_002.py | ddof/MAD/分位/平均秩明确；全局Train拟合及当时截面按原协议隔离。 |
| RESEARCH-003 | CR | V3.0§5.1;V3.0§18 | RESEARCH-002;DATA-012 | ResearchRequest, StageScores, research | tests/research/test_research_003.py | OLS算术/正交性通过；PIT行业/市值构矩阵与秩亏仍待实现。 |
| RESEARCH-004 | MVP | V3.0§5.2 | RESEARCH-001 | ResearchRequest, StageScores, research | tests/research/test_research_004.py | 9项滚动/时序标量答案通过；session缺失/边界未来测试。 |
| RESEARCH-005 | MVP | V3.0§5.2 | RESEARCH-004 | ResearchRequest, StageScores, research | tests/research/test_research_005.py | 平均并列秩和Ts_Rank正确；Conditional仅白名单，待实际正负测试。 |
| RESEARCH-006 | MVP | V3.0§5.3 | RESEARCH-002 | ResearchRequest, StageScores, research | tests/research/test_research_006.py | 五stage契约保留；真实artifact/SKIPPED+input_ref待实施。 |
| RESEARCH-007 | MVP | V3.0§5.1 | RESEARCH-006 | ResearchRequest, StageScores, research | tests/research/test_research_007.py | **003：合成/冗余行为缺少具体设计，ID存在不等于完整覆盖。** |
| RESEARCH-008 | MVP | V3.0§5.1;V3.0§13 | EXP-001;RESEARCH-001 | ResearchRequest, StageScores, research | tests/research/test_research_008.py | cache/参数实验契约可取；须绑定全配置及权限，004复现路径待定。 |
| RESEARCH-009 | MVP | V3.1§1;V3.0§3.6 | RESEARCH-001;VALID-001 | ResearchRequest, StageScores, research | tests/research/test_research_009.py | Momentum→Reversal真实全研究替换已计划；无P4/P5要求。 |
| VALID-001 | MVP | V3.0§6.1;V3.0§6.2;V3.0§10.2 | RESEARCH-006 | LabelBatch, SplitSpec, MetricResult, TestEvaluator | tests/validation/test_valid_001.py | Pearson/ties/ICIR答案通过；002标签时点待闭合。 |
| VALID-002 | MVP | V3.0§6.1;V3.0§6.2 | VALID-001 | LabelBatch, SplitSpec, MetricResult, TestEvaluator | tests/validation/test_valid_002.py | 三组/TMB/单调答案通过；行动标签见002，衰减/年度测试待实施。 |
| VALID-003 | MVP | V3.0§6.3;V3.1§4 | VALID-001 | LabelBatch, SplitSpec, MetricResult, TestEvaluator | tests/validation/test_valid_003.py | 闭区间接触purge/embargo答案通过；真实日期、标签可用性见002。 |
| VALID-004 | MVP | V3.0§6.4;V3.1§4 | VALID-003;EXP-002 | LabelBatch, SplitSpec, MetricResult, TestEvaluator | tests/validation/test_valid_004.py | **001：正式权限部署/可达性待决；无隔离必须fail closed。** |
| VALID-005 | MVP | V3.0§6.1;V3.0§6.5 | VALID-001 | LabelBatch, SplitSpec, MetricResult, TestEvaluator | tests/validation/test_valid_005.py | HAC算术尺度通过；**005：正式推断profile尚未冻结。** |
| VALID-006 | MVP | V3.0§6.4;V3.1§4 | EXP-002;VALID-004 | LabelBatch, SplitSpec, MetricResult, TestEvaluator | tests/validation/test_valid_006.py | 全部候选/访问/重复指纹已设计；不能仅靠family改名解除污染。 |
| VALID-007 | MVP | V3.0§6.4;V3.1§4 | VALID-005;VALID-006 | LabelBatch, SplitSpec, MetricResult, TestEvaluator | tests/validation/test_valid_007.py | Holm/BY/BH全m=3答案通过；有效p/依赖/适应性限制必须保留。 |
| VALID-008 | MVP | V3.0§6.5;V3.1§4 | VALID-004;VALID-007 | LabelBatch, SplitSpec, MetricResult, TestEvaluator | tests/validation/test_valid_008.py | 缺标准/身份/证据拒绝正确；正式ResearchValidated未批准。 |
| EXP-001 | MVP | V3.0§13;V3.1§7 | DATA-007;FACTOR-003 | ExperimentLedger, reproduce, ApprovalProposal | tests/experiments/test_exp_001.py | 唯一UUID、全配置/环境/失败/原文件hash和终态已计划。 |
| EXP-002 | MVP | V3.0§6.4;V3.0§13;V3.1§4 | EXP-001 | ExperimentLedger, reproduce, ApprovalProposal | tests/experiments/test_exp_002.py | 先ledger再候选的顺序正确；所有失败/淘汰/重复及选择路径须存。 |
| EXP-003 | MVP | V3.0§13;V3.0§9.5 | EXP-001 | ExperimentLedger, reproduce, ApprovalProposal | tests/experiments/test_exp_003.py | **004：比较/复现接口有承诺，旧制品运行路由缺失。** |
| EXP-004 | MVP | V3.1§4;V3.1§7 | VALID-008;EXP-001 | ExperimentLedger, reproduce, ApprovalProposal | tests/experiments/test_exp_004.py | 冻结/实际证据/人工记录域明确；001及正式标准限制正向批准。 |
| QA-004 | MVP | V3.0§10.4;V3.1§6;V3.2§1 | QA-001;VALID-001 | GOLDEN_REFERENCE.md / independent answers | tests/quality/test_qa_004.py | 本次GPT Work独立15组/75断言通过；不登记成Gemini全项完成。 |
| INT-001 | MVP | V3.0§12.1;V3.1§1 | RESEARCH-009;VALID-003;EXP-001 | complete research service | tests/integration/test_int_001.py | Data→Universe→Factor→五stage→统计/OOS→报告/实验全链已规划；依赖上述闭环。 |

本轮diff仅26个文件：20个P3计划/参考文件及6个说明/状态文档。**src/tests/tools/.github/pyproject.toml/requirements.lock/已发布版本/全部phase-2材料对基线无差异。** 50份冻结资产逐字节核验通过；P3 manifest 19项、P2 publication manifest 66项全部匹配。没有提前实现P4组合/风险、P5账本回测、P6 UI，没有DAG或任意外部插件扩张。RESEARCH-007自身已有的研究分数合成仍属P3，不可因此删除。

## B · 实际执行、数学与原始证据

### 独立复算

本人的 [independent_math.py](<C:/Users/11638/AppData/Local/Packages/OpenAI.Codex_2p2nqsd0c76g0/LocalCache/Local/AQRP/reviews/work-p3-g1-d10a55a/independent_math.py>) 只用标准库Fraction/80位Decimal/受限AST解析，未导入AQRP、NumPy或开发方reference。采用成对计数定义平均秩、原始和式相关、正交投影OLS、HAC Toeplitz二次型、直接排序公式多重校正，独立于开发方参考的代码路径。**15组、75个标量/状态断言，75通过、0失败。** 详细输入字段与每个答案比较见 [independent-math-results.json](<C:/Users/11638/AppData/Local/Packages/OpenAI.Codex_2p2nqsd0c76g0/LocalCache/Local/AQRP/reviews/work-p3-g1-d10a55a/independent-math-results.json>)。

| case | 独立计算依据 | 核对结果 |
|---|---|---|
| P3-PV | t−1收益1/10 × 历史量惊喜3/5 | 3/50 = 0.06；L2收益乘量为0.126，不能替代 |
| P3-PV-ZERO-CURRENT | 当前volume=0，前两日均量125 | −1/10；零当前量与零历史均量不同 |
| P3-IC | Sxy=.19，Sxx=10，Syy=.00452；y秩[1,3,2,4,5] | Pearson=.893684824964417428…；Spearman=.9 |
| P3-TIE | 秩[3/2,3/2,3]与[1,2,3] | sqrt(3)/2=.866025403784438647… |
| P3-Z-ICIR | z的sample variance=5/2；IC均值.2/样本std.1 | z=x/sqrt(5/2)；ICIR=2，非年化 |
| P3-ROLL | Mean/Std/Sum/Min/Max/Corr/Delay/Delta/TsRank | 2,1,6,1,3,−1,2,1,5/6 |
| P3-WINSOR | linear分位p(n−1)；上下界3/4、53/2 | [3/4,1,2,53/2] |
| P3-MAD | median=2，MAD=1，k=3 | [0,1,2,3,5] |
| P3-OLS | 独立正交投影，未用开发方正规方程消元 | beta=[2,2,1]；e=[1,−1,−1,1]；Xᵀe=0；SSE=4 |
| P3-GROUP | 平均秩分箱[0,0,1,1,2,2] | 均值[−.02,.01,.05]；TMB=.07；单调1 |
| P3-HAC | 独立Bartlett Toeplitz二次型uᵀWu/n² | gamma=[1,−3/4]；S=1/4；Var(mean)=1/16；SE=1/4 |
| P3-MULTI | 全部3项排序校正后恢复输入顺序 | Holm=[.03,.06,.06]；BY=[11/200,11/150,11/150]；BH=[.03,.04,.04] |
| P3-LABEL | signal0，h2，entry1，exit3；110/100−1 | 1/10；实际时点/数据可用边界NOT VERIFIED |
| P3-LABEL-ACTION | 终值股票102 + 应收2；(104−100)/100 | 1/25，条件于享有红利资格；时序边界见002 |
| P3-PURGE | [1,4]∩[4,6]非空；[1,3]∩[4,6]为空 | purge=true；safe overlap=false；embargo 7、8 |

容差没有更改：float abs=1e-12、rel=1e-10，采用 `abs(actual-expected)<=max(atol,rtol*abs(expected))`；有理数、索引、布尔、hash精确比较。P0的六位/九位摘要不作为新精确答案；旧近似值按原abs1e-8。复算程序额外打印全family加入一个失败候选p=1、m=4时的结果：Holm=[.04,.09,.09,1]；BY=[1/12,1/9,1/9,1]；BH=[.04,4/75,4/75,1]。这进一步显示不能只保留赢家的m=3结果，但并非AQRP实现测试。

HAC的n=4案例只证明算术尺度，不能证明正式渐近p或有限样本可靠性。若错误应用n/(n−1)修正，Var(mean)会是1/12，而非当前正确1/16。行动案例4%仅在其已声明权益假设下成立；缺少时间输入不能由纯算术补出边界。没有生成或修改任何正式expected。

另实际重跑了已审阅的开发方reference，15组通过，见 [developer-reference-replay.stdout.log](<C:/Users/11638/AppData/Local/Packages/OpenAI.Codex_2p2nqsd0c76g0/LocalCache/Local/AQRP/reviews/work-p3-g1-d10a55a/developer-reference-replay.stdout.log>)。这是“本人重跑开发方脚本”的补充证据，不能替代上述独立复算。

### 基线CI原件核验

[run 39645351705](https://github.com/wwooyy429/Alpha-Quant-Research-Platform-AQRP-/actions/runs/39645351705) 的2个job均success。原始ZIP实际下载，官方digest和大小匹配，CRC检查通过，每个文件建立SHA256清单，JUnit实际有417个testcase且无failure/error/skip；两个wheel的26个Python源码及receipt均与固定副本逐字节匹配。

| 原CI artifact | ID | tests/fail/error/skip | 原ZIP SHA256 |
|---|---|---|---|
| phase2-windows-latest-1 | 12367341501 | 417/0/0/0 | 6470f0006025306d36d95468896e6ed4f77261c46eab94796a215fa7ca70aa32 |
| phase2-ubuntu-24.04-1 | 12366772314 | 417/0/0/0 | 95cfdc3cf411d52525ed22a0f850139cb99a22cf7f36c33c0c1152dd8509d5df |

CI实际checkout为临时合并 `a4f55ea258b3e0153f6724eee0a9d7f4a7f01923`，双父为baseline+固定审查SHA，tree `69557390cd4907237102375d6bcceedbd1c5ed1e` 与固定审查版本完全相同。**这不是main的新合并，也不是P3实现测试。** CI仍叫Phase 2 quality，运行未变更0.2.0基线。源码未变化，不把这轮工作扩展为再次完整本地SDK重跑；原16/4本轮未重跑，P2发布记录与原件仅作已接受基线引用。

- 本机：Windows-11-10.0.26300-SP0，AMD64/x64、标准GIL，CPython **3.13.16**。本轮只用标准库；没有新建业务安装环境、安装/升级依赖。
- CI原件环境：Windows-2025Server、Ubuntu24 Linux，均Python3.13.16、clean，code_commit精确为上述临时合并。并非本人在Linux执行。
- 22包锁及Python约束保持。SciPy/statsmodels未在本轮安装，网页文档的版本不代表已安装。
- 验证命令、UTC/本地时间、stdout/stderr和退出码均保留；查看 [git-commands.json](<C:/Users/11638/AppData/Local/Packages/OpenAI.Codex_2p2nqsd0c76g0/LocalCache/Local/AQRP/reviews/work-p3-g1-d10a55a/git-commands.json>)、各 `*.command.json` 及对应日志。

| 命令记录 | exit | 原记录开始→结束 |
|---|---|---|
| ci-evidence.command.json | 0 | 2026-10-22T01:54:44.8301537+08:00 → 2026-10-22T01:54:45.3522490+08:00 |
| developer-reference-replay.command.json | 0 | 2026-10-22T01:53:47.4330734+08:00 → 2026-10-22T01:53:47.7653868+08:00 |
| independent-math.command.json | 0 | 2026-10-22T01:50:02.6964226+08:00 → 2026-10-22T01:50:02.9328790+08:00 |
| package-compatibility.command.json | 0 | 2026-10-22T01:58:04.7412975+08:00 → 2026-10-22T01:58:04.9927192+08:00 |
| scope.command.json | 0 | 2026-10-22T01:48:43.5131960+08:00 → 2026-10-22T01:48:49.3126177+08:00 |

原始执行方式（独立副本和审查方目录，不运行未来AQRP实现）：

```powershell
$review='C:\Users\11638\AppData\Local\AQRP\reviews\work-p3-g1-d10a55a'
$fixed='C:\Users\11638\AppData\Local\AQRP\reviews\p3-d10a55a'
& "$review/run-review.ps1" -Name scope -Script "$review/verify_scope.py" -ScriptArgs $fixed
& "$review/run-review.ps1" -Name independent-math -Script "$review/independent_math.py" -ScriptArgs $fixed
& "$review/run-review.ps1" -Name developer-reference-replay -Script "$fixed/docs/audits/phase-3/reference_arithmetic.py"
& "$review/run-review.ps1" -Name ci-evidence -Script "$review/verify_ci.py" -ScriptArgs $fixed
& "$review/run-review.ps1" -Name package-compatibility -Script "$review/verify_package.py" -ScriptArgs $fixed
```

wrapper实际调用固定 `C:\Users\11638\AppData\Local\AQRP\runtime\Python31316\python.exe -I`。首次创建独立副本用 `git clone --shared --no-checkout --config core.longpaths=true <developer-checkout> <fixed-checkout>` 后 `git checkout --detach d10a55a7dd4bc9ca7793ed474bdc1b056916e96e`；clone/checkout stdout/stderr/exit单独保存。source ZIP由精确SHA的git archive生成。GitHub读取/下载的工具名、immutable IDs和时序见 [review-provenance.json](<C:/Users/11638/AppData/Local/Packages/OpenAI.Codex_2p2nqsd0c76g0/LocalCache/Local/AQRP/reviews/work-p3-g1-d10a55a/review-provenance.json>)；短期下载URL不持久化。

审查辅助操作曾误查不存在的data/api.py、发现gh未安装、首次connector参数名错误。最终封存辅助程序首次因Windows默认GBK读取本人UTF-8报告失败，原脚本及错误保留于finalize-attempt1.py、finalization-attempt1-error.json，改为显式UTF-8后重试；与项目验证无关。其余辅助错误保留于 [reviewer-operation-errors.json](<C:/Users/11638/AppData/Local/Packages/OpenAI.Codex_2p2nqsd0c76g0/LocalCache/Local/AQRP/reviews/work-p3-g1-d10a55a/reviewer-operation-errors.json>)；随后定位实际data/query.py并用已有GitHub connector完成下载，没有安装工具或改仓库。这些不是项目测试失败。

## C · 接口、数学、安全与设计发现

总体可取：Data API和8表边界保留，DATA-012独立PIT侧车；价格/量公式t−1正确；缺失不补0；stage与fit lineage分开；白名单算子不执行任意Python；全部试验ledger先于候选；Test预算与污染按数据身份；原字节hash与逻辑配置身份分开；研究/工程/策略批准域分离。以下缺口不能以这些正确方向替代闭环。

### WORK-P3-001 · High · 正式 Test 隔离仍未选定可部署、可验证的权限 profile

- 类别 / 需求：设计/验收可达性缺口；VALID-004, VALID-006, VALID-008, FACTOR-009, EXP-004。
- 固定版本：`d10a55a7dd4bc9ca7793ed474bdc1b056916e96e`；位置：[docs/audits/phase-3/DESIGN_DECISIONS.md](<C:/Users/11638/AppData/Local/Packages/OpenAI.Codex_2p2nqsd0c76g0/LocalCache/Local/AQRP/reviews/p3-d10a55a/docs/audits/phase-3/DESIGN_DECISIONS.md:6>)。
- 依据：P3-D02 只提议专用 OS 主体/可替换 evaluator，并明确尚未配置/证明；没有主体/存储 ACL/输入投影/执行制品/结果与日志所有者矩阵或双 OS 验证路径。INTERFACE_DRAFT.md:10,16,20 提供的是能力对象约定。
- 最小核对 / 复现：对照 P3-D02 与接口，尝试确定开发身份能否直接读含 Test 区间的原始行情/公司行动快照、重建标签，或读 evaluator 的结果/缓存/日志；本包没有足够部署定义可回答。未执行越权或更改 ACL。
- 预期：G1 选定威胁模型和评估身份、实际可部署隔离边界及验证方案；正式最终 Test 的数据/反馈封存可证明。
- 实际：安全失败策略明确且正确，但全项 VALID-004 的实际验收路径未闭合。role/API、同 OS 用户的另一进程不构成独立权限证明。
- 影响：即便隐藏标签对象，开发端若有同一 Test 原始输入仍可重建标签；正式 OOS 独立性不能由逻辑单测推出。
- 门禁处置：阻断完整 G1 实施基线；无需在本轮部署，但必须选定可达方案。无部署能力只能继续 fail closed，不能全项验收 VALID-004。
- 最小修订：开发方提交单一可部署方案及资产/权限矩阵，覆盖原始 Test 输入、标签、缓存、ledger、报告/反馈、访问预算存储和已批准代码身份；明确普通研究身份和管理员/存储拥有者的信任边界。用户确认评估主体/部署权限与批准人；没有条件时显式保留阻断，不删需求。
- 复核条件：固定新 SHA 审方案；实施时用真实不同权限主体验证读标签/可重建标签的原始数据/缓存/结果均被拒，授权评估成功、并发/崩溃/重复/改名访问受控。双 OS 支持或已批准的能力边界分别存证。
- 负责人 / 状态：开发方方案；用户批准主体/权限；审查方核验；**OPEN**，设计提案缺口，不是已实现代码故障。

### WORK-P3-002 · High · next-open 行动标签尚缺权益时序与信息可用边界

- 类别 / 需求：时间/金融接口定义缺口；VALID-001, VALID-002, VALID-003, QA-004, INT-001。
- 固定版本：`d10a55a7dd4bc9ca7793ed474bdc1b056916e96e`；位置：[docs/audits/phase-3/INTERFACE_DRAFT.md](<C:/Users/11638/AppData/Local/Packages/OpenAI.Codex_2p2nqsd0c76g0/LocalCache/Local/AQRP/reviews/p3-d10a55a/docs/audits/phase-3/INTERFACE_DRAFT.md:12>)。
- 依据：LabelSpec 仅给 RAW+可见行动总收益/start/end/available_at；golden_cases.json:375–382 只有 entry_price/split/cash_per_postsplit_share/exit_price，没有公司行动时点。原 P1 日 bar 以收盘为 event_time，且 action_view 的现金基准为 PER_OLD_SHARE。
- 最小核对 / 复现：现有行动向量可独立算得 (2*51+2*1)/100-1=4%；若同样末端价格/拆股但不具红利资格，收益为2%。输入未提供 entry/exit、ex/effective/record/pay/available 时点，无法判定哪种权益路径成立。exit-open 已发生但该日完整 bar 尚未可见，也不能把该 bar 提前用于拟合。
- 预期：明示入场/退出与行动同刻的处理顺序、含/不含端点、股数和现金基准转换、未支付应收、修订和 evaluation_cutoff；标签 available_at 为实际依赖可用时点。拟合还须检查 training label available_at<=fit cutoff，不能只按 signal session 或价格终点 purge。
- 实际：4% 是条件算术正确；时点/资格和 fit 可用边界 NOT VERIFIED，现有两组标签 Golden 不能证明这些边界。
- 影响：错误纳入入场前红利、退出后拆股，或把尚未发布的标签用于训练，会使统计和 OOS 划分失真。
- 门禁处置：阻断标签/切分的 G1 定义；这是待定设计，未指控不存在的 P3 实现已泄漏。
- 最小修订：冻结 SYNTHETIC_V1 的明确行动标签协议，沿用 RAW 并显式转换 P1 PER_OLD_SHARE 与本案例 post-split 单位；规定公司行动排序、evaluation_cutoff/available_at 与 price holding interval、purge interval 的关系。新增带 UTC 微秒及 session 日历的独立答案，保留当前正确算术原件。
- 复核条件：入场/退出同刻拆股或除息、端点前后1微秒、晚到/修订、支付在退出后、P1日bar直到收盘才可见、train label 延迟发布、purge闭区间接触；每案列预期股数/应收/收益/可用时点。
- 负责人 / 状态：开发方协议与候选；审查方独立复算；用户确认合成经济假设；**OPEN**，设计提案缺口，不是已实现代码故障。

### WORK-P3-003 · Medium · RESEARCH-007 的因子合成和冗余分析只有目录映射

- 类别 / 需求：需求设计/测试映射缺口；RESEARCH-007, INT-001。
- 固定版本：`d10a55a7dd4bc9ca7793ed474bdc1b056916e96e`；位置：[docs/audits/phase-3/REQUIREMENTS_TRACEABILITY.md](<C:/Users/11638/AppData/Local/Packages/OpenAI.Codex_2p2nqsd0c76g0/LocalCache/Local/AQRP/reviews/p3-d10a55a/docs/audits/phase-3/REQUIREMENTS_TRACEABILITY.md:16>)。
- 依据：canonical 定义为因子相关/组合研究/冗余分析；V3.0§5.1 第435–436行分别列因子组合及冗余。P3 PLAN:12、统计口径:9 只展开跨因子相关；接口无合成配置/输出，TEST_PLAN 无合成及冗余答案。
- 最小核对 / 复现：搜索 Phase3 计划可找到需求快照中的“组合研究/冗余”，但实际接口与测试只给通用 ResearchRequest/StageScores 和 test_research_007.py 文件名。不能确定两因子输入如何合成、缺失如何处理、产物和冗余结论是什么。
- 预期：26项逐项有可实现、可验收的行为；P3研究级分数组合/冗余分析有公式、配置、stage/对齐/缺失与测试。
- 实际：ID/来源/依赖映射未遗漏，但该项内部必需行为没有设计落点。
- 影响：实现可能仅交相关矩阵却将整项记完成；该范围不能因“后续组合”一词被误归为 P4 而静默删除。
- 门禁处置：阻断26项覆盖的 G1 完整性；不要求提前实现 P4 账户、资金权重或风险模块。
- 最小修订：选择最小研究级合成接口与冗余诊断输出：精确Ref、stage、预注册因子方向/权重、同样本交集及缺失政策、合成分数/血缘、相关和预注册冗余规则。若使用学习权重须只在Train拟合，否则选择固定权重。补手算/性质/失败测试映射。
- 复核条件：固定2因子独立数值、符号/不同scale、缺失交集、零权重或无有效组合、冗余规则及未来数据变更；所有权重/规则选择进ledger，无账户写入。
- 负责人 / 状态：开发方补设计，审查方核覆盖；范围变更仅用户批准；**OPEN**，设计提案缺口，不是已实现代码故障。

### WORK-P3-004 · Medium · 旧 FactorRef 重现尚未选择具体运行与制品方案

- 类别 / 需求：兼容/复现设计缺口；FACTOR-007, RESEARCH-008, EXP-003, INT-001。
- 固定版本：`d10a55a7dd4bc9ca7793ed474bdc1b056916e96e`；位置：[docs/audits/phase-3/DESIGN_DECISIONS.md](<C:/Users/11638/AppData/Local/Packages/OpenAI.Codex_2p2nqsd0c76g0/LocalCache/Local/AQRP/reviews/p3-d10a55a/docs/audits/phase-3/DESIGN_DECISIONS.md:10>)。
- 依据：P3-D06 要求后续提供新旧 API 范围与旧 wheel 重现测试，但包内未提供。现有 admission.py:19–36 对整个 aqrp/**/*.py 和锁做身份，:49–50 校验当前 bundle，:67–70 要求精确Ref指向当前receipt。新增P3代码必改bundle。
- 最小核对 / 复现：只读追踪 bundle_manifest/reviewed_policy/validate_admission：旧Ref中的51933fe…与新增P3代码后的新bundle必不相等。全bundle新receipt不是旧Ref的运行环境；reproduce接口未说明如何路由旧制品。未改或运行正式源码。
- 预期：加法功能与旧实验可重现同时成立，并给精确制品/版本路由与验收投影。
- 实际：承诺正确，但所选机制、错误语义和测试矩阵尚缺。旧Ref不能靠原地替换implementation_hash变成新Ref。
- 影响：新代码准入后，既有实验可能只剩拒绝或被静默迁移，违反固定版本复现。
- 门禁处置：阻断兼容/重现的G1设计闭环；这是P3变更前需要选定的机制，不是要求旧P2准入当前支持未知新代码。
- 最小修订：选择经哈希核对的旧0.2.0源/原wheel+原锁独立运行方案，或具有等价安全证据的多版本路由；列旧3因子/Ref/API与新PriceVolume/API矩阵、制品保管及缺失拒绝语义、可允许不同的run_id/墙钟/路径身份投影；新bundle完整重审，不重写旧receipt或Ref。
- 复核条件：新P3 runtime运行新Ref；原精确Ref在其原0.2.0环境重放；原manifest原字节hash及声明数值投影核对；旧制品缺失/篡改明确不可复现；老接口与三公式回归不变。
- 负责人 / 状态：开发方选择方案，审查方核验；破坏契约或架构变更由用户批准；**OPEN**，设计提案缺口，不是已实现代码故障。

### WORK-P3-005 · Medium · HAC 正式推断 profile 与最小样本准入尚未冻结

- 类别 / 需求：统计准入/验收标准未闭合；VALID-005, VALID-007, VALID-008, QA-004。
- 固定版本：`d10a55a7dd4bc9ca7793ed474bdc1b056916e96e`；位置：[docs/audits/phase-3/STATISTICAL_CONVENTIONS.md](<C:/Users/11638/AppData/Local/Packages/OpenAI.Codex_2p2nqsd0c76g0/LocalCache/Local/AQRP/reviews/p3-d10a55a/docs/audits/phase-3/STATISTICAL_CONVENTIONS.md:10>)。
- 依据：文中明说min_hac_n待预注册/预审，P3-D03/D04尚无数值或完整假设profile。唯一HAC Golden是n=4、均值0、q=1，并声明只验算术。
- 最小核对 / 复现：现有案例可证明gamma/S/Var(mean)/SE尺度；不能据此决定任一h、样本长度或缺失序列能否输出正式p，均值为0也无法验证非零均值p值路径。q>=h-1本身不构成HAC有效性证明。
- 预期：明确区分算术原语、工程演示、正式推断；正式profile冻结min_hac_n、0<=q<n、h/lag兼容、等间隔/额外自相关与渐近假设、拒绝原因及非零均值已知答案。
- 实际：拒绝小样本/空洞的方向正确，具体准入profile仍开放。没有数学错误，也不能据此默认小样本可靠。
- 影响：若实施者任意选min_n/自动lag或库默认修正，可能对无效p值再做Holm/BY而产生伪正式结论。
- 门禁处置：正式推断的G1子门禁未闭合；可设计/实现显式fail-closed原语，但不得把本包视作正式统计准入已批准。无用户金融阈值本身只阻断Formal ResearchValidated，并不要求停止无关纯计算模块。
- 最小修订：开发方提出带依据的统计profile与拒绝契约，明确min_hac_n是保守工程门槛而非有限样本保证；不由审查者凭空拍一个通用数字。保留Bartlett、gamma除n、Var(mean)=S/n、correction=none及已算正确答案；新增非零均值/多个lag/缺失/不足样本及全family失败项候选。
- 复核条件：独立复算新非零均值SE/p；样本/lag边界与拒绝路径；全family有效边际p要求、Holm/BY/BH假设及污染门禁。NumPy/stdlib可维持22锁；若加SciPy/statsmodels，先精确候选/哈希/3.13.16双OS方案。
- 负责人 / 状态：开发方提出方法与profile；统计预审核验；用户批准正式样本/经济阈值/实验预算；**OPEN**，设计提案缺口，不是已实现代码故障。

### 其他必须保留的实施约束（本轮无额外缺陷编号）

1. **拟合隔离**：继承冻结RESEARCH_PROTOCOL.md:9：全局参数仅Train拟合、Validation仅按预注册选型、Test不参与；当日截面z/OLS只能用该日decision cutoff可见样本/暴露。每个窗口记录fit的输入身份/截止点及应用区间，禁止全panel拟合后再split。横截面变换与跨日期拟合是不同作用域，不能一概把未来Test截面或Train拟合统计混为一谈。002另要求训练标签在fit时已可用。
2. **PIT侧车**：父快照+自己的manifest/schema/分片hash，event/available先过滤再取可见修订、再处理生效区间。正cap/currency/unit、行业字典版本/可选beta、UNKNOWN_AVAILABILITY/null+reason继承主契约；不拿“缺暴露=0”逃避中性化或未来风险约束。
3. **五stage**：已启用处理必须有真实变换及计数/拟合参数；SKIPPED只能表示明确未启用，必须指回输入。报告同时标stage/horizon/universe/split，不能把raw或原样复制列称为neutralized/final已处理。INT-001需实际跑服务、CLI、报告、ledger及OOS，不能只测DTO/mock。
4. **全部试验与cache**：成功/失败/淘汰/超预算/重复/取消均留记录，终态不可回退；配置方向、预处理、期限、lag等改动算新实验。cache键须实质覆盖原始/侧车/股票池/日历/label/protocol及fit权限域的完整配置，不以缓存命中绕过Test访问和预算。数值缓存不直接缓存人工金融批准。全family未完成/失败项的保守p=1政策及原因必须披露。
5. **统计依赖**：Holm/BY校正不修复无效边际p、适应性挑选或Test污染；BH只能在预先有相应依赖依据时运行。分组不拆tie可产生空组，不能造观测；年度/期限/衰减不混样本或重复计数。显著不构成金融适用批准。
6. **依赖选择**：建议本阶段明确选择已锁NumPy+标准库实现当前有限方法，保存独立高精度参考；这在技术上可达，不需要为了引用文档而安装SciPy/statsmodels。原架构列这些库仍保留，不能借此宣称永久删除。若转用新依赖，先列精确候选、来源/wheel hash及Python3.13.16 Windows/Ubuntu验证方案，再审锁变更；不猜最新版本。
7. **独立身份与范围**：本轮算术补充PASS不自动把canonical QA-004全项标完成，也不自行登记Gemini G1 PASS。P2 GPT Work复核/历史限制原字节保持。DAG、不可信外部插件、真实数据/账户、P4–P7功能都未开放。

库边界以主源核实：官方[NumPy lstsq](https://numpy.org/doc/stable/reference/generated/numpy.linalg.lstsq.html)说明rcond及秩亏/M<=N时residuals可为空；不能将空数组解释为零残差。[statsmodels cov_hac](https://www.statsmodels.org/stable/generated/statsmodels.stats.sandwich_covariance.cov_hac.html)明确连续等间隔序列、默认自动lag和小样本修正选项；本项目必须显式覆盖这些默认值。[multipletests](https://www.statsmodels.org/stable/generated/statsmodels.stats.multitest.multipletests.html)列方法及原顺序恢复。这里只核接口约定，不声称已运行该库或用其网页替代独立答案。

## D · 版本、哈希与可复核材料

| 对象 | SHA256 / 身份 |
|---|---|
| fixed source ZIP | `b00d5b5c84d6001a2f2e369b94eead145c68bb1b87d8d1e2c466466667e83664` |
| canonical requirements.csv | `20dd4e6be7188d3121f3cb361faf8901bc91815a6e9752beb14054a12183f0c1` |
| requirements.lock（22包） | `86c7bf65c9a9690036006360062c8cd10a91279705b4070af7033d7699abffeb` |
| P3 golden_cases.json | `75e25b25bb024428a0323c7e5f3941ca6a33fc488adabaad0b24d8440c296bd5` |
| 本人独立复算脚本 | `5370af8de2c459f59f69f7bff686a6f32c59ab9b8ba2b0121bc713b6f99877f5` |
| 当前26模块代码bundle | `51933fe2508e61a25fef53ea73b4210a67cb19d6531e1bf614e206db32a1d62d` |

[scope-verification.json](<C:/Users/11638/AppData/Local/Packages/OpenAI.Codex_2p2nqsd0c76g0/LocalCache/Local/AQRP/reviews/work-p3-g1-d10a55a/scope-verification.json>)含50冻结资产、两份manifest每文件预期/实际hash及remote refs；[compatibility-evidence.json](<C:/Users/11638/AppData/Local/Packages/OpenAI.Codex_2p2nqsd0c76g0/LocalCache/Local/AQRP/reviews/work-p3-g1-d10a55a/compatibility-evidence.json>)含22锁包、当前bundle及双CI wheel逐源码字节核对。仅在内存的“增加一个空research/__init__.py”身份计算将bundle变为c7af030cfe302c9a366dad88ae4e91745a00f142c259d2011d7a67fccd632011，证明004需要设计；未向正式包添加文件。

全部材料索引：[REVIEW_EVIDENCE_MANIFEST.json](<C:/Users/11638/AppData/Local/Packages/OpenAI.Codex_2p2nqsd0c76g0/LocalCache/Local/AQRP/reviews/work-p3-g1-d10a55a/REVIEW_EVIDENCE_MANIFEST.json>)（不包含自身），包括原ZIP、source ZIP、命令/环境/原日志、独立脚本/结果、本报告及任务清单。原始证据以ZIP内字节为准；connector job文本副本按LF保存。MSIX把Local/AQRP别名解析为本报告使用的物理LocalCache路径；该目录在同步盘之外。

## E · 判定、NOT VERIFIED与待决定

**PLAN BLOCKED**，主要由001–004的设计未闭环构成；005的正式推断profile也未批准。当前无数值错误、范围越界或业务实现改动的发现。不能把“写明待决”当“待决已解决”，也不能因这些条件删掉26项中的任何必需能力。

| 待决定项 | 需谁决定 / 截止 | 是否阻断 |
|---|---|---|
| 真正Test评估身份、输入/标签/结果存储权限、支持OS及部署profile | 开发方提交可达方案，用户确认主体/部署授权，审查方核设计；G1闭环前 | 001阻断完整G1。未能部署时formal Test fail closed；完整VALID-004仍未验收 |
| 合成行动标签的权益/同刻顺序、信息可用与purge规则 | 开发方+独立数学审查；涉及经济假设由用户确认；G1前 | 002阻断标签/split基线 |
| RESEARCH-007研究合成/冗余规则 | 开发方提具体接口/答案，审查核canonical；若删减必须用户范围变更批准 | 003阻断覆盖完整性，不借机实现P4 |
| 新/旧Ref/API/制品运行与重现路线 | 开发方，审查方；破坏兼容时用户批准 | 004阻断兼容设计 |
| min_hac_n/lag/假设/拒绝profile及正式推断方法 | 开发方给有依据的工程方案、统计预审；正式数值/预算用户批准 | 005阻断正式推断准入；纯算术/fail-closed框架不需假造金融阈值 |
| 实际日期、期限网格、alpha/样本/稳定性/研究通过阈值、实验/访问预算D-004 | 用户按明确候选和证据批准，审查核符合性；正式评估/ResearchValidated前 | 缺失**阻断Formal ResearchValidated**；不能用正IC/显著性代替，也不要求P5交易批准先行 |
| 保持22包或引入新库 | 明确选用现有NumPy+stdlib不构成新依赖阻断；新库须候选/锁/双OS验证，架构变更用户批准 | 不因当前未安装SciPy/statsmodels单独阻断G1；不批准未知候选 |

**NOT VERIFIED / 未执行**：真实独立Test身份/ACL部署及攻击测试；正式金融有效性/用户标准批准；P3算子/服务/ledger/cache/OOS/五stage/报告真实运行（无实现，不能跑）；P3新增依赖/跨OS实现验证（无新依赖/实现）；Gemini本人独立执行；本轮新本地完整SDK及原16/4重跑。已核当前双OS417是他人CI原件验证，不写为本人本地执行。

当前具备提交设计修订与具体决定的证据，**不具备完整G1放行或P3人工验收条件**。不要求重新批准P3启动。

## F · 给开发方的最小闭环顺序

1. 保持本固定版本原件；只修订计划/接口/新增版本候选答案，逐项回应WORK-P3-001–005，尚未闭环不得启用P3业务。
2. 先提交可部署Test权限profile和标签权益/可用时点协议，再补研究合成/冗余及旧Ref制品路由。对正式标准和统计profile给具体可评审选项、批准人和截止关卡；没有部署/标准的路径明确拒绝。
3. 新增时点边界与非零均值HAC/全family候选，交独立复算；保留本轮正确数值、原Goldens及全部失败/历史材料。
4. 固定新的40位PR审查SHA，请复核本轮设计缺口。G1闭环后才实施已授权26项，所有适用测试及新完整实现审查另办。
5. 不合并、不打标签、不进入P4；不将本报告登记为用户ACCEPTED/RELEASED或Gemini完成。

可转交的逐项任务见 [Codex-Phase3-G1-d10a55a-Tasks.md](<C:/Users/11638/AppData/Local/Packages/OpenAI.Codex_2p2nqsd0c76g0/LocalCache/Local/AQRP/reviews/work-p3-g1-d10a55a/Codex-Phase3-G1-d10a55a-Tasks.md>)，机器可读发现见 [findings.json](<C:/Users/11638/AppData/Local/Packages/OpenAI.Codex_2p2nqsd0c76g0/LocalCache/Local/AQRP/reviews/work-p3-g1-d10a55a/findings.json>)。
