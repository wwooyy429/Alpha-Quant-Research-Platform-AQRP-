# GPT Work 补充审核：Phase 3 G1 增量复核

**PLAN BLOCKED。** 对固定版本本轮关闭003、004的**设计缺口**；001、002、005仍OPEN。现有候选未发现超容差的数值错误；HAC固定带宽的正式推断依据仍须修订/论证。G1、部署、金融批准和P3实现验收分别判断。

**目标SHA：`e26d4bbfe28262c35396f66daa183771573a988e`。** 它与用户链接、开始时PR描述AQRP_FIXED_REVIEW_SHA和初始PR head一致，先记录后detached checkout。复核结束前，PR字段/head已变为 **`ff4c546b9a8f6652ff70804055d9435ac08f63b3`**。本轮副本始终留在e26，**新提交NOT REVIEWED / 不被本报告覆盖**；不外推其修复成功或失败。证据：[sha-drift.json](<C:/Users/11638/AppData/Local/Packages/OpenAI.Codex_2p2nqsd0c76g0/LocalCache/Local/AQRP/reviews/work-p3-g1-e26d4bb/sha-drift.json>)、pr5-start.json/pr5-end.json。

## A · 对象、权限与覆盖

- 仓库 / [PR #5](https://github.com/wwooyy429/Alpha-Quant-Research-Platform-AQRP-/pull/5)。
- 上轮审查：`d10a55a7dd4bc9ca7793ed474bdc1b056916e96e`；本轮基线main/phase2-baseline/v0.2.0：`f26255fc40a3080bfa883ad64938f60036a14759`。
- 起始2026-10-22 02:36:22 Asia/Shanghai；报告生成2026-10-22T02:54:54.948737+08:00。
- 固定副本：[p3-e26d4bb](<C:/Users/11638/AppData/Local/Packages/OpenAI.Codex_2p2nqsd0c76g0/LocalCache/Local/AQRP/reviews/p3-e26d4bb>)；起始及结束核查detached、clean。开发副本只读定位，无同时改文件/操作环境。
- 实际身份：**GPT Work 补充审核，非Gemini**。本轮链接是增量审查请求，不是对Test账户、部署、经济假设、正式金融阈值的批准。
- 只运行审查方独立程序和已读开发方标准库参考。没有改正式src/tests/tools/CI/锁/版本/Golden/状态/原报告；没有commit/push、ACL/账户/调度器部署、PR编辑、合并/标签/P4。

实际重核：canonical **106条/16组，P3 26条=23 MVP+3 Competition Ready**。REQUIREMENTS_SNAPSHOT逐字段等于CSV筛选，TRACEABILITY_SNAPSHOT的ID/tier/dependencies无遗漏。50冻结资产、P3本轮manifest50项、P2 publication manifest66项全部hash一致。对f262和旧d10的src/tests/tools/.github/pyproject.toml/requirements.lock及全部P2原件无差异；0.2.0版本保持。新增仅计划/参考/归档/状态文档，未实现P3业务。局部.gitattributes仅作用于归档行尾检查，原始字节实核不变，不是放宽业务测试。

| ID | 等级 | canonical来源 | 原依赖 | 行为/接口落点 | 未来测试映射 | 本轮意见 |
|---|---|---|---|---|---|---|
| DATA-012 | Competition Ready | V3.0§4.4;V3.0§7.3 | DATA-002 | INTERFACE_DRAFT:7 | tests/data/test_data_012.py | PIT侧车/缺失契约保留，待实现 |
| FACTOR-007 | Competition Ready | V3.0§3.4 | FACTOR-003 | INTERFACE_DRAFT:8 + REPRODUCTION_PROFILE | tests/factors/test_factor_007.py | PV原0.06正确；新bundle/新Ref准入仍待实现 |
| FACTOR-009 | MVP | V3.0§1.3;V3.0§3.5;V3.0§12.3;V3.0§18 | FACTOR-003;VALID-008 | TEST_ISOLATION + approvals | tests/factors/test_factor_009.py | 001/005及正式标准约束；无金融批准 |
| RESEARCH-001 | MVP | V3.0§5.1;V3.0§12.1 | FACTOR-003 | PLAN + research service | tests/research/test_research_001.py | 完整链继续，接口/失败记录待真实实现 |
| RESEARCH-002 | MVP | V3.0§5.1 | RESEARCH-001 | STATISTICAL_CONVENTIONS | tests/research/test_research_002.py | Train全局拟合/当时截面、ddof/MAD/rank继承 |
| RESEARCH-003 | Competition Ready | V3.0§5.1;V3.0§18 | RESEARCH-002;DATA-012 | Exposure + OLS | tests/research/test_research_003.py | 原OLS答案正确；PIT构矩阵/秩亏待测 |
| RESEARCH-004 | MVP | V3.0§5.2 | RESEARCH-001 | operators | tests/research/test_research_004.py | 原窗口/算子答案保持；session边界待实现 |
| RESEARCH-005 | MVP | V3.0§5.2 | RESEARCH-004 | rank/conditional whitelist | tests/research/test_research_005.py | 并列秩正确，条件白名单待实际正负测试 |
| RESEARCH-006 | MVP | V3.0§5.3 | RESEARCH-002 | StageScores | tests/research/test_research_006.py | 五stage真实产物或SKIPPED+input_ref，未验收 |
| RESEARCH-007 | MVP | V3.0§5.1 | RESEARCH-006 | COMPOSITE_RESEARCH:3–13 | tests/research/test_research_007.py | 003设计CLOSED；compose/冗余/INT001映射补齐 |
| RESEARCH-008 | MVP | V3.0§5.1;V3.0§13 | EXP-001;RESEARCH-001 | cache + protocol + reproduce | tests/research/test_research_008.py | 全配置/权限/fit隔离保留，004设计CLOSED |
| RESEARCH-009 | MVP | V3.1§1;V3.0§3.6 | RESEARCH-001;VALID-001 | TEST_PLAN:15 | tests/research/test_research_009.py | Momentum→Reversal完整研究替换待实现 |
| VALID-001 | MVP | V3.0§6.1;V3.0§6.2;V3.0§10.2 | RESEARCH-006 | LABEL_ACTION + IC metrics | tests/validation/test_valid_001.py | 原IC/Rank/ICIR和新标签算术通过；002仍OPEN |
| VALID-002 | MVP | V3.0§6.1;V3.0§6.2 | VALID-001 | LABEL_ACTION + group metrics | tests/validation/test_valid_002.py | 分组/TMB/期限年度范围保留，时序按新profile |
| VALID-003 | MVP | V3.0§6.3;V3.1§4 | VALID-001 | LABEL_ACTION:11–15 | tests/validation/test_valid_003.py | label可用<=fit、信息区间闭接触purge已明示 |
| VALID-004 | MVP | V3.0§6.4;V3.1§4 | VALID-003;EXP-002 | TEST_ISOLATION_PROFILE | tests/validation/test_valid_004.py | 001 OPEN；无真实权限证据不得全项验收 |
| VALID-005 | MVP | V3.0§6.1;V3.0§6.5 | VALID-001 | HAC_INFERENCE_PROFILE | tests/validation/test_valid_005.py | 005 OPEN：固定带宽正式推断依据待闭环 |
| VALID-006 | MVP | V3.0§6.4;V3.1§4 | EXP-002;VALID-004 | private Test ledger + lineage | tests/validation/test_valid_006.py | 全部候选/重复/污染/消费不返还已设计，未运行 |
| VALID-007 | MVP | V3.0§6.4;V3.1§4 | VALID-005;VALID-006 | HAC_INFERENCE:13–15 | tests/validation/test_valid_007.py | 完整m4校正正确；无效p/null不能伪装正式p=1 |
| VALID-008 | MVP | V3.0§6.5;V3.1§4 | VALID-004;VALID-007 | formal protocol + approvals | tests/validation/test_valid_008.py | 无标准/样本/证据不得ResearchValidated |
| EXP-001 | MVP | V3.0§13;V3.1§7 | DATA-007;FACTOR-003 | ExperimentLedger | tests/experiments/test_exp_001.py | 不可变全配置/原hash/失败/终态范围保留 |
| EXP-002 | MVP | V3.0§6.4;V3.0§13;V3.1§4 | EXP-001 | ledger + composite + family | tests/experiments/test_exp_002.py | 方向/权重/期限/预处理/lag改动均新实验 |
| EXP-003 | MVP | V3.0§13;V3.0§9.5 | EXP-001 | REPRODUCTION_PROFILE:3–23 | tests/experiments/test_exp_003.py | 004设计CLOSED；旧wheel保管实核，真实路由未测 |
| EXP-004 | MVP | V3.1§4;V3.1§7 | VALID-008;EXP-001 | approvals + IsolationDeploymentRef | tests/experiments/test_exp_004.py | 审批证据/身份/冻结与预算齐备才可研究批准 |
| QA-004 | MVP | V3.0§10.4;V3.1§6;V3.2§1 | QA-001;VALID-001 | original + supplemental Golden | tests/quality/test_qa_004.py | 本人43组221断言；不登记为Gemini全项完成 |
| INT-001 | MVP | V3.0§12.1;V3.1§1 | RESEARCH-009;VALID-003;EXP-001 | research service/report/ledger + compose | tests/integration/test_int_001.py | 完整链含新增compose及OOS，未运行P3实现 |

所有P3能力仍为Planned；上述CLOSED仅关设计发现，不把能力标Implemented/ACCEPTED。P3研究级合成属于既有RESEARCH-007，不提前做P4持仓/资金/风险、P5账本回测或P6 UI；没有DAG/外部任意插件扩张。

## B · 实际数学核对与执行

### 独立方法、数量与限制

1. 复用本人上轮原始独立程序（字节不变），针对e26再次跑原15组，**75/75断言通过**；原golden_cases.json/reference_arithmetic.py/.log三份字节相对d10保持。
2. 新写 [independent_supplemental.py](<C:/Users/11638/AppData/Local/Packages/OpenAI.Codex_2p2nqsd0c76g0/LocalCache/Local/AQRP/reviews/work-p3-g1-e26d4bb/independent_supplemental.py>)，只用标准库Fraction/90位Decimal及日期运算；**28组146/146断言通过**。未导入AQRP或开发方reference。用真实时点排序的合成权益事件复算，复算交集上的sample z，HAC用Toeplitz二次型，校正用直接有序公式。
3. 正态尾p独立于开发方erf幂级数：Machin公式计算pi，32/64点Gauss–Legendre积分exp(−t²)。两阶结果差分别约6.29e−46和3.53e−50，远小于候选容差；不把90位工作精度宣称为90位严格误差证明。
4. 合计**43组、221个成功断言**。其中状态/拒绝码是设计契约谓词核对，并非运行未来P3服务/权限状态机。原始逐字段记录：[independent-math-results.json](<C:/Users/11638/AppData/Local/Packages/OpenAI.Codex_2p2nqsd0c76g0/LocalCache/Local/AQRP/reviews/work-p3-g1-e26d4bb/independent-math-results.json>)、[independent-supplemental-results.json](<C:/Users/11638/AppData/Local/Packages/OpenAI.Codex_2p2nqsd0c76g0/LocalCache/Local/AQRP/reviews/work-p3-g1-e26d4bb/independent-supplemental-results.json>)、[independent-supplemental-checks.csv](<C:/Users/11638/AppData/Local/Packages/OpenAI.Codex_2p2nqsd0c76g0/LocalCache/Local/AQRP/reviews/work-p3-g1-e26d4bb/independent-supplemental-checks.csv>)。
5. 容差abs1e−12/rel1e−10未改，按max(abs_tol,rel_tol*abs(expected))；有理数/UTC微秒/布尔/状态精确。旧15组仍按原独立来源处理，不改expected，不调用未来实现生成答案。

**输入完整性限制**：普通行动候选未给全action event_time/available_at；其收益/资格在明确经济时点下可算，但label_available_at的通过是条件性的——省略依赖须不晚于已给的bar/coverage最大水位。开发方脚本的隐藏fallback不能算JSON输入已独立冻结。迟到/修订/不可用/拟合案例中显式给出的时点已逐项计算。实际P1完整行/coverage签名/数据库查询尚未运行，002据此也保留完善自包含输入的要求。

| 新case | 断言数 | 主要复算输出/检查（均为候选核对） |
|---|---|---|
| LABEL-NONE | 4 | shares=1；credit=0；return=1/10；label_available_at=2026-01-08 16:00:00.000001+00:00 |
| LABEL-INTERIOR-OLD-UNIT | 4 | shares=2；credit=2；return=1/25；label_available_at=2026-01-08 16:00:00.000001+00:00 |
| LABEL-ENTRY-SAME | 4 | shares=1；credit=0；return=1/50；label_available_at=2026-01-08 16:00:00.000001+00:00 |
| LABEL-ENTRY-MINUS-US | 4 | shares=1；credit=0；return=1/50；label_available_at=2026-01-08 16:00:00.000001+00:00 |
| LABEL-ENTRY-PLUS-US | 4 | shares=2；credit=2；return=1/25；label_available_at=2026-01-08 16:00:00.000001+00:00 |
| LABEL-EXIT-SAME | 4 | shares=2；credit=2；return=1/25；label_available_at=2026-01-08 16:00:00.000001+00:00 |
| LABEL-EXIT-MINUS-US | 4 | shares=2；credit=2；return=1/25；label_available_at=2026-01-08 16:00:00.000001+00:00 |
| LABEL-EXIT-PLUS-US | 4 | shares=1；credit=0；return=1/50；label_available_at=2026-01-08 16:00:00.000001+00:00 |
| LABEL-DIV-ENTRY-NO-ENTITLEMENT | 4 | shares=1；credit=0；return=1/50；label_available_at=2026-01-08 16:00:00.000001+00:00 |
| LABEL-DIV-EXIT-ENTITLEMENT | 4 | shares=1；credit=2；return=1/25；label_available_at=2026-01-08 16:00:00.000001+00:00 |
| LABEL-LATE-VISIBLE | 4 | shares=2；credit=2；return=1/25；label_available_at=2026-01-09 12:00:00.000001+00:00 |
| LABEL-LATE-NOT-VISIBLE | 6 | shares=None；credit=None；return=None；label_available_at=None；status=NOT_YET_AVAILABLE |
| LABEL-REVISION-OLD-ASOF | 4 | shares=2；credit=2；return=1/25；label_available_at=2026-01-08 16:00:00.000001+00:00 |
| LABEL-REVISION-NEW-ASOF | 4 | shares=2；credit=4；return=3/50；label_available_at=2026-01-10 12:00:00+00:00 |
| LABEL-ANCHOR-RESET | 5 | shares=2；credit=2；return=1/25；label_available_at=2026-01-08 16:00:00.000001+00:00 |
| LABEL-BAR-CLOSE-AND-FIT | 4 | visible_at_exit_open=False；fit_before=False；fit_equal=True；fit_after=True |
| LABEL-LATE-TRAIN-FIT | 1 | fit_allowed=False |
| PURGE-INFORMATION-CONTACT | 1 | purge=True |
| COMPOSITE-SIGNED-SCALE | 9 | composite/0=-1；composite/1=0；composite/2=1；raw_correlation=-1；signed_correlation=1；raw_spearman=-1 |
| COMPOSITE-POSITIVE-DIRECTION | 3 | composite/0=-0.5；composite/1=0；composite/2=0.5 |
| COMPOSITE-MISSING-INTERSECTION | 5 | composite/0=-0.70710678118654752440084436210484903928483593768847403658833986899536623923105351942519377；composite/1=0.70710678118654752440084436210484903928483593768847403658833986899536623923105351942519377；kept_indices/0=0；kept_indices/1=2；excluded_indices/0=1 |
| COMPOSITE-REJECTIONS | 4 | all_zero=INVALID_WEIGHTS；one_positive=INSUFFICIENT_COMPONENTS；empty=INSUFFICIENT_INTERSECTION；missing_thresholds=UNCLASSIFIED |
| REDUNDANCY-PREDECLARED | 3 | flag=True；automatic_weight_change=False；account_write=False |
| HAC-NONZERO-Q1 | 10 | SE=0.0625；z=4；p=0.0000633424836662398425075415；非formal |
| HAC-NONZERO-Q2 | 11 | SE=0.0721687836487032205636；z=3.4641016151377545870548；p=0.0005320055051392496992898821；非formal |
| HAC-PROFILE-BOUNDARIES | 12 | lags/0=5；lags/1=5；lags/2=9；lags/3=19；minimum_ns/0=252；minimum_ns/1=252 |
| HAC-REJECTION-CONTRACT | 5 | short_lag=LAG_BELOW_OVERLAP；lag_equal_n=INVALID_HORIZON_OR_LAG；missing_session=IRREGULAR_OR_MISSING_IC；no_assumptions=ASSUMPTIONS_UNVERIFIED；no_approval=FORMAL_PROTOCOL_UNAPPROVED |
| MULTI-FAILED-FAMILY | 15 | m4：Holm[.04,.09,.09,1]；BY[1/12,1/9,1/9,1]；BH[.04,4/75,4/75,1]；正式批准=false |

非零HAC结果：q1 SE=1/16，z=4，p=0.00006334248366623984250754…；q2 SE=1/(8sqrt3)，z=2sqrt3，p=0.00053200550513924969928988…。q2手写近似与高精度值差约7e−19，在原容差内，不构成答案错误。n4两个例子均不可formal。m4失败项保留raw_p=null/reason，保守校正输入才为1，正式family批准仍false。

另本人实际重跑已审阅的开发方supplemental_reference：28组122断言通过，原脚本输出自称Codex developer身份，这是脚本的原文；**实际重跑者为本报告GPT Work**，只能列作开发参考重放，不能顶替本人的146断言独立核对。

审查程序首轮在Gauss节点初值中混用float/Decimal而TypeError、exit1，中止记录保留；只修正审查方初值表达式，原脚本留independent_supplemental-attempt1.py。attempt2 exit0。没有项目业务测试失败，没有改候选值/容差。

### 原件接收与当前CI

- g1-d10的完整旧ZIP SHA256 **09198db18696e972067955a59d92b5058872b9e9f660fc8cd29c471d7a44f607**，与本人上轮封存值一致；CRC/内部66项manifest全部逐字节hash通过，RECEIPT的9份原件hash通过，含旧报告/任务/发现/数学结果与manifest。原身份GPT Work保持，未倒填Gemini。见 [archive-and-reproduction-evidence.json](<C:/Users/11638/AppData/Local/Packages/OpenAI.Codex_2p2nqsd0c76g0/LocalCache/Local/AQRP/reviews/work-p3-g1-e26d4bb/archive-and-reproduction-evidence.json>)。
- 已实际打开P2发布保管的原0.2.0 wheel，hash **70b43271ee142b18d5d9d306d452936f8409322fda5e676431f24eb150871c9d**，其26模块和receipt逐字节匹配固定源码；原22包锁hash及bundle保持。没有执行新reproduce路由。
- 本轮 [CI run39653524560](https://github.com/wwooyy429/Alpha-Quant-Research-Platform-AQRP-/actions/runs/39653524560) 两份原ZIP实际下载、大小/官方digest/CRC/JUnit/环境与wheel源码核对通过。

| CI artifact | ID | bytes | 原ZIP SHA256 | tests/fail/error/skip |
|---|---|---|---|---|
| phase2-ubuntu-24.04-1 | 12370449123 | 149762 | 6bacc95fbeac4632174854761f54ce344b1e86e816f91043b51a8b7c61bed408 | 417/0/0/0 |
| phase2-windows-latest-1 | 12370309429 | 149816 | 8cfa74555a373cc04b6319a56a978f441eff6a52c7939b601928d202287c4cac | 417/0/0/0 |

CI实际checkout临时merge **`3d626c92b56903a1b8e9edc7ad30bd66b409b01e`**，其tree **`9a7c2f9be96db170e7e3f5a79416a9103e13ec4a`**与e26固定副本相同；父为f262+e26。两个环境均clean、Python3.13.16、原锁hash、真实0.2.0 wheel；每个wheel的26源码与receipt核对。它是**未改变的P2回归417**，不是main实际合并或P3测试/预审PASS。新ff4 CI不在这份证据内。

### 原始命令、环境与日志

本机 Windows-11-10.0.26300-SP0，AMD64/x64标准GIL，CPython3.13.16（cbc944f）。没有安装/升级新依赖。CI Windows/Ubuntu执行者是GitHub hosted runners，读取CI原件不是本人在Linux运行。

wrapper逐条保留argv/cwd/开始结束/退出码及独立stdout/stderr；Git原始操作见git-commands.json，联网工具/IDs及辅助错误说明见provenance.json。

| 命令记录 | exit | 开始→结束 |
|---|---|---|
| archive-and-reproduction.command.json | 0 | 2026-10-22T02:43:34.4493068+08:00 → 2026-10-22T02:43:35.4847406+08:00 |
| current-ci.command.json | 0 | 2026-10-22T02:44:50.8515006+08:00 → 2026-10-22T02:44:51.3415878+08:00 |
| developer-supplemental-replay.command.json | 0 | 2026-10-22T02:45:16.5320820+08:00 → 2026-10-22T02:45:16.9115219+08:00 |
| fixed-bandwidth-analysis.command.json | 0 | 2026-10-22T02:48:03.8700393+08:00 → 2026-10-22T02:48:04.0652475+08:00 |
| original15-independent.command.json | 0 | 2026-10-22T02:41:02.3061518+08:00 → 2026-10-22T02:41:02.5102222+08:00 |
| scope.command.json | 0 | 2026-10-22T02:40:55.7021479+08:00 → 2026-10-22T02:41:02.2606801+08:00 |
| supplemental-independent-attempt2.command.json | 0 | 2026-10-22T02:42:47.2322871+08:00 → 2026-10-22T02:42:47.5124099+08:00 |
| supplemental-independent.command.json | 1 | 2026-10-22T02:42:33.3486128+08:00 → 2026-10-22T02:42:33.6101439+08:00 |

```powershell
$review='C:\Users\11638\AppData\Local\AQRP\reviews\work-p3-g1-e26d4bb'
$fixed='C:\Users\11638\AppData\Local\AQRP\reviews\p3-e26d4bb'
& "$review/run-review.ps1" -Name scope -Script "$review/verify_scope.py" -ScriptArgs $fixed
& "$review/run-review.ps1" -Name original15-independent -Script "$review/independent_original15.py" -ScriptArgs $fixed
& "$review/run-review.ps1" -Name supplemental-independent-attempt2 -Script "$review/independent_supplemental.py" -ScriptArgs $fixed
& "$review/run-review.ps1" -Name archive-and-reproduction -Script "$review/verify_archive.py" -ScriptArgs $fixed
& "$review/run-review.ps1" -Name current-ci -Script "$review/verify_current_ci.py" -ScriptArgs $fixed
& "$review/run-review.ps1" -Name fixed-bandwidth-analysis -Script "$review/verify_bandwidth.py"
```

实际解释器为 `C:\Users\11638\AppData\Local\AQRP\runtime\Python31316\python.exe -I`。独立副本用longpaths=true、shared/no-checkout clone后checkout --detach本固定SHA；未操作开发者工作树。GitHub connector取得原ZIP后只下载/读取，不执行ZIP内容。短期bearer URL不持久化，原artifact ID/官方digest均保留。MSIX物理路径在LocalCache非同步目录，最终证据manifest及ZIP逐文件再hash封存。

## C · 五项发现处置、依据与最小闭环

### WORK-P3-001 · High · OPEN：设计可行，用户具体决定及部署未验证

位置：[TEST_ISOLATION_PROFILE.md](<C:/Users/11638/AppData/Local/Packages/OpenAI.Codex_2p2nqsd0c76g0/LocalCache/Local/AQRP/reviews/p3-e26d4bb/docs/audits/phase-3/TEST_ISOLATION_PROFILE.md:5>)、:7–26；[DESIGN_DECISIONS.md](<C:/Users/11638/AppData/Local/Packages/OpenAI.Codex_2p2nqsd0c76g0/LocalCache/Local/AQRP/reviews/p3-e26d4bb/docs/audits/phase-3/DESIGN_DECISIONS.md:8>)。关联VALID-004/006/008、FACTOR-009、EXP-004。

**设计认可范围**：三个不同非admin SID/UID、可信管理员保管、物理Train/Validation投影；完整Test原始输入/行动/暴露/seed/生成私参/备份/cache/label/反馈/log/控制ledger私有；管理员固定入口+sealed inbox避免TOCTOU；缓存先授权/消费，RESERVED先落盘、失败消费不返还、按真实Test lineage跨名识别污染。公开Golden/已知seed永远ENGINEERING_DEMO、独立新seed在冻结后生成，边界明确。它是受信主机方案，不是管理员或恶意内核沙箱。SID/UID与实际ACL才是身份，当前11638管理员身份不适用。

**仍OPEN**：固定e26尚无用户对实际主体、可信保管者/审查者/批准人、真实路径及部署权限的具体确认。本轮链接不等于该确认；未创建用户/任务/ACL，未实测两个OS。高危原始数据直读/标签重建路径现有设计已覆盖，不能仅因设计写得具体就登记VALID-004完成。

处置：开发方给一张待批准的具体配置表，用户确认方案/责任主体；实际部署另获明确授权。缺部署证据仍UNVERIFIED_ISOLATION，formal fail closed。实施后须真实权限正负控制、并发/断进程/预算恢复/改名/缓存绕过实证。当前阻断为具体决定未到位，不重复索取P3启动许可。

[Microsoft icacls主源](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/icacls)支持DACL保存/核验等工具能力；网页不能证明本机ACL、token或调度器已部署。

### WORK-P3-002 · High · OPEN：时间与算术认可，经济确认/完整输入待补

位置：[LABEL_ACTION_PROFILE.md](<C:/Users/11638/AppData/Local/Packages/OpenAI.Codex_2p2nqsd0c76g0/LocalCache/Local/AQRP/reviews/p3-e26d4bb/docs/audits/phase-3/LABEL_ACTION_PROFILE.md:5>)、:7–15；[supplemental_cases.json](<C:/Users/11638/AppData/Local/Packages/OpenAI.Codex_2p2nqsd0c76g0/LocalCache/Local/AQRP/reviews/p3-e26d4bb/docs/audits/phase-3/supplemental_cases.json:44>)、普通label defaults及case。关联VALID-001/002/003、QA-004、INT-001。

**已补齐并核对**：同刻split→dividend→entry→exit；资格(entry,exit]；entry同刻不享受入场前权益、exit同刻先确认权益；PER_OLD_SHARE以前收盘锚点转换，同刻2:1/旧股现金2得到2股/credit2；跨日锚点重置不重复除。pay晚于exit保留应收且不重复记收益。完整日bar必须等close/event及available后可见；LabelCoverageRef及revision冻结，尚不可见不从未来输入暴露label_available_at；Train标签须available<=fit；information interval=[signal_decision,label_available_at]闭接触purge。新增边界/修订算术一致。

**仍OPEN**：这是合成经济假设，用户尚未明确确认；普通行动case还应显式冻结announcement/event/available的默认或边界、coverage版本，不能靠开发参考脚本的fallback补输入。当前返回4%等值是对规定资格/可用性条件的核算，不等于已核P1真实行和权限。

最小处理：用户确认SYNTHETIC_V1_LABEL_1仅作合成研究口径；开发方新增自包含时间字段/候选版本，不改旧正确Golden。随后固定新SHA复核。未来实施时还须P1旧现金基准兼容、真实sidecar/可用修订/fit/purge负例。未指控不存在的P3实现泄漏。

### WORK-P3-003 · Medium · CLOSED（仅设计）

位置：[COMPOSITE_RESEARCH.md](<C:/Users/11638/AppData/Local/Packages/OpenAI.Codex_2p2nqsd0c76g0/LocalCache/Local/AQRP/reviews/p3-e26d4bb/docs/audits/phase-3/COMPOSITE_RESEARCH.md:3>)、:5–13；[TEST_PLAN.md](<C:/Users/11638/AppData/Local/Packages/OpenAI.Codex_2p2nqsd0c76g0/LocalCache/Local/AQRP/reviews/p3-e26d4bb/docs/audits/phase-3/TEST_PLAN.md:25>)。关联RESEARCH-007、INT-001。

原目录名式映射已补成compose接口及三类DTO；固定2+非负权重、一次方向、共同交集重新sample-z、缺失/零方差/零权重/重复Ref/不同stage明确；原/方向后相关、pair n和预注册冗余规则，不设正式默认阈值，无阈值UNCLASSIFIED不自动删因子；血缘/ledger/INT001报告路径完整。三组合向量、scale、缺失交集和冗余候选独立核对通过。

设计缺口关闭。实现和需求验收仍Planned；以后必须跑真实服务/报告/全部实验，不能用这些算术谓词冒充已实现。范围不涉及P4账户权重/订单。

### WORK-P3-004 · Medium · CLOSED（仅设计；环境重放NOT VERIFIED）

位置：[REPRODUCTION_PROFILE.md](<C:/Users/11638/AppData/Local/Packages/OpenAI.Codex_2p2nqsd0c76g0/LocalCache/Local/AQRP/reviews/p3-e26d4bb/docs/audits/phase-3/REPRODUCTION_PROFILE.md:3>)、:5–23。关联FACTOR-007、RESEARCH-008、EXP-003、INT-001。

选择原wheel+原22锁/receipt的独立解释器子进程，固定JSON/size/schema、离线hash制品、受管cwd/temp/环境、不接受任意脚本或路径。旧三精确Ref→旧env，新bundle/新Ref/PriceVolume→新env；旧Ref直指新env拒绝或显式reproduce路由，缺损明确失败；原字节完整性和允许的UUID/墙钟/路径逻辑投影分开。旧0.2发布wheel实际位于publication/sdk/wheel且hash/26模块/receipt匹配，非仅文档自述。

这满足原“未选择具体路线”的设计发现，关闭该发现。**完整EnvironmentArchiveRef（解释器安装包、OS身份、22包wheelhouse）未在P3包中提供，新路由未运行**，不宣称旧环境完整重现通过。G2必须真实成功重放适用旧Refs并保留原manifest；不能对所有旧Ref返回Unsupported后称EXP-003完成。新registry/factor-version/API的具体值须实施时精确pin，同一registry不能以相同ID/version静默塞不同内容。

### WORK-P3-005 · Medium · OPEN：工程候选补齐，正式带宽依据未闭环

位置：[HAC_INFERENCE_PROFILE.md](<C:/Users/11638/AppData/Local/Packages/OpenAI.Codex_2p2nqsd0c76g0/LocalCache/Local/AQRP/reviews/p3-e26d4bb/docs/audits/phase-3/HAC_INFERENCE_PROFILE.md:7>)、:9–15。关联VALID-005/007/008、QA-004。

认可改进：三模式、固定候选252/20(q+1)/max(h−1,5)、显式拒绝/假设ref、失效IC不dropna压时间、有效p与失败p_for_adjustment分开、全family污染/审批拒绝。非零mean q1/q2的S/SE/z/p全部正确。min n是工程筛查值，不是统计保证；当前文档也承认未获用户金融批准。

**独立反例**：令eps为独立等概率±1，x_t=(eps_t+eps_(t−1))/2，x∈{−1,0,1}。它平稳、只有lag1人口自协方差非零。本人枚举16种独立符号组合得到gamma0=1/2、gamma1=1/4、gamma(k>=2)=0，真实长期方差=1。按本profile的Bartlett定义，固定q=5的长期方差估计极限为

`1/2 + 2*(1−1/6)*(1/4) = 11/12`

即使n持续增加仍低估1/12≈8.33%；q9为19/20、q19为39/40。这里q已覆盖所有非零相关lag，问题还包括窗内taper权重偏差，并非只要“没有更长依赖”就消失。增大n门槛不使固定q自动一致。证据：[fixed-bandwidth-counterexample.json](<C:/Users/11638/AppData/Local/Packages/OpenAI.Codex_2p2nqsd0c76g0/LocalCache/Local/AQRP/reviews/work-p3-g1-e26d4bb/fixed-bandwidth-counterexample.json>)及本人程序/原日志。

这不是指控尚未批准/实现的FORMAL_INFERENCE已放行该过程：依赖审查可以拒绝它。但目前“该带宽截断可接受的Train/领域依据”没有给可复核的taper偏差/误差控制判据，**252/20/5加一般平稳/短记忆/CLT不能作为通用正式p依据**。因此005不因数值Golden正确而关闭。

最小选择：在开发期预注册并论证依事先样本长度n及h确定的带宽/推断规则及其条件，或限定有依据的依赖模型/预注册替代方法；若保留固定q，只能在有具体、可核验的校准/偏差控制下进入formal，否则保留ARITHMETIC/DEMO，正式路径fail closed。选择在看Validation/Test结果前冻结，不用Test诊断来调lag。金融阈值由用户批准，但用户批准数字不能替代估计量/推断方法有效性的论证。

[statsmodels cov_hac主源](https://www.statsmodels.org/stable/generated/statsmodels.stats.sandwich_covariance.cov_hac.html)给出等间隔、lag、Bartlett及修正选项，不为本项目252/20/5背书。本轮尝试直取NBER原论文遇403，未声称读取其正文；上述具体意见依赖本人精确反例和本项目公式，不靠未读来源代证明。

## D · 环境、哈希与追溯

| 对象 | SHA256 |
|---|---|
| e26 git archive fixed-source.zip | ff38a1da971424068a6ecd250c67353c08fe7eda749f79f80112bb3a7091bdab |
| canonical requirements.csv | 20dd4e6be7188d3121f3cb361faf8901bc91815a6e9752beb14054a12183f0c1 |
| 原22包requirements.lock | 86c7bf65c9a9690036006360062c8cd10a91279705b4070af7033d7699abffeb |
| 原15组Golden | 75e25b25bb024428a0323c7e5f3941ca6a33fc488adabaad0b24d8440c296bd5 |
| 新28组supplemental_cases | 21ef09832d29d3f7da72f51c0f90efa55280b2b17291e87f5e8b036ba919f896 |
| 本人新增独立程序（成功版） | f57f223ee2d3e20853c502c92e276bca4dfaec199f679e1a40cedade4a6b32ec |
| 原0.2.0发布wheel | 70b43271ee142b18d5d9d306d452936f8409322fda5e676431f24eb150871c9d |
| 原26模块bundle | 51933fe2508e61a25fef53ea73b4210a67cb19d6531e1bf614e206db32a1d62d |

本轮不猜SciPy/statsmodels已安装，也未加新依赖。选现有NumPy+stdlib的有限方法路线可行，不因引用网页强制装库；正式方法若确需新库须先精确候选/wheel hash/3.13.16双OS验证，再审锁变更。原架构未来库能力没有删除。

机器可读发现：[finding-disposition.json](<C:/Users/11638/AppData/Local/Packages/OpenAI.Codex_2p2nqsd0c76g0/LocalCache/Local/AQRP/reviews/work-p3-g1-e26d4bb/finding-disposition.json>)；范围/每文件hash：[scope-verification.json](<C:/Users/11638/AppData/Local/Packages/OpenAI.Codex_2p2nqsd0c76g0/LocalCache/Local/AQRP/reviews/work-p3-g1-e26d4bb/scope-verification.json>)；旧原件/原wheel：[archive-and-reproduction-evidence.json](<C:/Users/11638/AppData/Local/Packages/OpenAI.Codex_2p2nqsd0c76g0/LocalCache/Local/AQRP/reviews/work-p3-g1-e26d4bb/archive-and-reproduction-evidence.json>)；当前CI：[ci-verification.json](<C:/Users/11638/AppData/Local/Packages/OpenAI.Codex_2p2nqsd0c76g0/LocalCache/Local/AQRP/reviews/work-p3-g1-e26d4bb/ci-verification.json>)。原始命令/失败日志和所有实际输入随 [REVIEW_EVIDENCE_MANIFEST.json](<C:/Users/11638/AppData/Local/Packages/OpenAI.Codex_2p2nqsd0c76g0/LocalCache/Local/AQRP/reviews/work-p3-g1-e26d4bb/REVIEW_EVIDENCE_MANIFEST.json>) 封存，manifest不包含自身。

## E · 总结论与三类剩余条件

**本固定e26：PLAN BLOCKED。** 003/004设计CLOSED；001/002/005 OPEN。没有新P3业务实现，也没有金融批准；不把设计认可当G2/G3通过或用户验收。ff4及之后的修改未覆盖本轮结论。

| 类别 | 具体剩余条件 / 批准人 | 截止/效果 |
|---|---|---|
| 设计/用户选择 | 001：实际主体、保管/审查/批准人、本地路径与具体部署方案由用户确认 | 固定e26 G1仍阻断；不是再次批准P3启动 |
| 设计/经济假设 | 002：用户确认合成权益/同刻/old-share口径；开发方补齐自包含visibility输入 | 阻断标签设计整体放行，原正确算术不改 |
| 设计/统计依据 | 005：开发方选择可辩护正式推断方法/带宽及依赖准入，统计预审核验 | 阻断正式推断子门禁；不能靠签一个假设ref或用户数字批准代数学 |
| 部署/实施证据 | 真SID/UID/ACL/私有输入投影/seed/缓存/反馈/预算并发崩溃及两OS实证 | 本轮未授权部署、NOT VERIFIED；正式Test fail closed，VALID-004不全项完成 |
| 实施/复现证据 | 完整EnvironmentArchiveRef、旧三Ref真实路由与原字节/数值投影、新P3兼容 | G2证据待实现；不能用P2旧417代替 |
| 金融协议 | 实际日期/样本/期限/alpha/稳定性/研究门槛、实验/访问预算及审批者由用户正式批准 | 缺项禁止Formal ResearchValidated；正IC/显著性不代替批准；不凭空要求P5先完成 |
| 后续授权 | P3实现审查/用户验收/合并标签、P4启动分别授权 | 本轮不执行或推定 |

NOT VERIFIED/NOT RUN：真实权限部署/攻击；P3完整研究/五stage/算子/ledger/cache/OOS/compose/报告/重现路由；正式金融评估/批准；Gemini本人执行；新依赖安装/兼容；本人新本地完整SDK及原16/4复跑；新ff4提交。已核双OS417属CI他人执行证据，非本轮P3功能测试。

## F · 可转交的下一步

1. 对本固定e26只登记003/004设计关闭，001/002/005仍OPEN；不要重写旧d10报告、正确Golden或历史身份。
2. 先补002完整visibility默认/候选，并按005给出正式带宽/误差控制选择；用户具体确认001部署方案及002经济假设。不得把“P3启动已授权”推为这些决定已批准。
3. 本轮中出现的ff4应作为**新固定版本另行复核**，首先核其差异/具体决定证据，再判断上述残留是否已解决；不以本报告PASS/BLOCKED外推新提交。
4. G1明确闭环后才进入已授权范围实施；随后真实P3测试/旧Ref重放/独立审查及人工验收分别完成。不合并、不标签、不进入P4。

转交清单：[Codex-Phase3-G1-e26d4bb-Tasks.md](<C:/Users/11638/AppData/Local/Packages/OpenAI.Codex_2p2nqsd0c76g0/LocalCache/Local/AQRP/reviews/work-p3-g1-e26d4bb/Codex-Phase3-G1-e26d4bb-Tasks.md>)。
