from pathlib import Path
import json,datetime
O=Path(__file__).parent;FIX='f7a1a68c5f747090f8c8a0e934f2fea859aec998';J=lambda n:json.loads((O/n).read_bytes())
scope=J('SCOPE_RELEASE_VERIFICATION.json');design=J('INDEPENDENT_DESIGN_RESULTS.json');deps=J('DEPENDENCY_VERIFICATION.json');env=J('ENVIRONMENT.json')
assert scope['result']==deps['result']=='PASS' and design['golden_passed']==32
findings=[dict(id='WORK-P6-G1-001',severity='High',status='OPEN',blocking=True,title='多阶段Task缺少全阶段完成屏障，单个核心终态恢复与Task终态提升未区分',path='docs/audits/phase-6/TASK_AND_RECOVERY_CONTRACT.md',line=9,related=['docs/audits/phase-6/INTERFACE_DRAFT.md:9','docs/audits/phase-6/TEST_AND_EVIDENCE_PLAN.md:9'],basis='engineering_pipeline包含P3/P4/P5多个子run，但恢复规则直接由一个合法核心终态恢复Task终态，未冻结每kind的required stages/子slot终态归并及恢复继续/停止条件',minimal_counterexample='P3 SUCCEEDED且manifest有效；P4/P5未执行；映射写回前宕机。按现文核心终态→Task终态的无条件解释会标Task SUCCEEDED，完整回测尚不存在。P3/P4成功但P5缺失同样未定义。',scope='Design contract ambiguity/counterexample, not observed P6 production defect',required_fix='为research/engineering_pipeline/replay分别冻结固定阶段/动态slot完成条件；明确子run终态只恢复该slot；Task成功必须全部必需子阶段及最终工件/血缘验证成功。定义剩余未执行阶段的安全继续或RECOVERY_REQUIRED，禁止重跑完成的P3或退还家族预算。补充每阶段映射前后崩溃、P3成功P5失败/未启动、取消、全链成功设计答案及实际G2矩阵。'),dict(id='WORK-P6-G1-002',severity='Medium',status='OPEN',blocking=True,title='可信TaskContext和ledger根布局未覆盖P5内部逐决策P4调用',path='docs/audits/phase-6/DEPENDENCY_AND_COMPATIBILITY_PLAN.md',line=11,related=['docs/audits/phase-6/TASK_AND_RECOVERY_CONTRACT.md:3','docs/audits/phase-6/TASK_AND_RECOVERY_CONTRACT.md:9','src/aqrp/backtest/engine.py:324','src/aqrp/backtest/provider.py:191'],basis='已列兼容适配只列ledger和三应用服务；实际P5在Simulator._risk_portfolio内部不带context调用construct_engineering，并固定到P5 run内portfolio-runs，随后在同一根核验。外层适配不自动说明动态P4 slot如何预分配/持久化所有权和根绑定。',minimal_counterexample='Task已预分配P5；第一个内部P4已提交合法终态、Task slot/映射尚未写回即宕机。现方案未指定P4的预分配slot/父run/physical root与上下文传递，恢复者无法只凭一个合法UUID证明它属于该Task/decision。',scope='Missing implementable adapter/ownership design, not claim no possible implementation',required_fix='补全TaskService→P5 service→Simulator内部P4的可信传播机制、并发隔离及明确非金融适配文件；可选显式参数或受控上下文，但须说明原无context行为兼容。冻结(task,slot,service kind,decision,parent,run_id,root,config hash)绑定和动态slot登记时点；说明P3共享家族根与P5内部P4实际根如何同时遵守原来源校验/重放；增加内部P4提交/映射断点及错UUID/根负控。不得靠全局monkeypatch、事后凭UUID补所有权或扩张金融算法。'),dict(id='WORK-P6-G1-003',severity='Medium',status='OPEN',blocking=True,title='设计参考使用默认Decimal精度，长百分比静默舍入，大金额格式化抛异常',path='docs/audits/phase-6/reference_check.py',line=8,related=['docs/audits/phase-6/reference_check.py:9','docs/audits/phase-6/MATH_AND_COMPARISON_CONTRACT.md:5','docs/audits/phase-6/MATH_AND_COMPARISON_CONTRACT.md:7'],basis='原32项全部正确，但规范未限定输入到28有效位，参考的Decimal除法/normalize/quantize使用默认精度28；与精确请求及大金额呈现承诺不符。',minimal_counterexample=design['developer_reference_boundary_observations'],scope='Actually executed design-reference defect, not UI implementation defect',required_fix='精确百分比转换用整数/Fraction或按输入长度设置足够localcontext，不能受默认28位影响。大金额显示也需明确精度/溢出/原值保留策略；若选择schema范围上限，超限须显式拒绝而非舍入。保留32原正确答案字节，增加超过28位的小权重、长大整数金额及正负HALF_EVEN边界，另给独立字面答案并复核参考。')]
result=dict(fixed_sha=FIX,scope='Phase6 G1 plan only',verdict='PLAN BLOCKED / REQUEST CHANGES',findings=findings,counts=dict(High=1,Medium=2,Critical=0,Low=0),P5_published_baseline_verified=True,P6_business_implementation=False,P6_runtime_browser_tests=0,UI_installation='NOT VERIFIED / NOT EXECUTED',Windows_R2='DEFERRED / NOT VERIFIED',formal_Test=False,financial_approval='NONE',full_historical_host='NOT VERIFIED beyond accepted package/lock/oldRef/result replay',merge_tag_deploy_live_P7=False)
(O/'FINDINGS.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
report=f'''# AQRP Phase6 G1 固定版本独立计划预审

固定完整SHA：`{FIX}`；PR #9；审查者：GPT Work补充审核员（本会话），2026-10-23 Asia/Shanghai。

**PLAN BLOCKED / REQUEST CHANGES：1 High、2 Medium，均OPEN，须修订计划/参考后交新固定SHA。** 本轮只审G1，没有启动P6业务实现、安装UI、运行AppTest/浏览器或将设计模型称为产品测试。Phase5既有G2/验收/受限发布保持，前置基线已实际核实。

## 已核范围与前置发布

PR起止描述及head锁为本40SHA，detached检出，工作树干净；直接父提交为已发布`59246f9fd391c1713b6bed65dd22280f4d248493`。远端main、phase5-baseline、v0.5.0 peeled targets一致，旧标签对象/目标与前轮记录相比未移动。

实际普通merge `36c26911afb47ff68544e4bf64f060504dfdd94d`与归档头`c43b594f2f427e8a7b3614518b84aa00502365f2`整树相同，已审P5实现`1c5a7e62cace7c3e66b7cc7f12fd564cb0013654`为祖先。P6对比P5只改55文件：7份治理状态文档及48份phase-6计划/模型/锁/记录；4738冻结文件内容SHA256及原基线Git blob身份逐项核对通过。src/tests/tools/CI/build/core lock与已审P5实现完全相同，无src/aqrp/ui。

P5发布证据499154943字节、SHA256 `5eb3a1165ae489d004e24dfd6c183878bb529e8b55ceb8c21f3418485f0ce79b`，1124声明文件+manifest，CRC/全部大小/hash核实。原合并后SDK ZIP115510697字节、SHA256 `b177bbbe4d04c0b5c0412d447218596489293e90d2876346f52baf7844e5f5ab`的8008选择文件+selection、CRC/全hash、environment.complete、1158 testcase/0失败错误跳过及69模块wheel与当前源码一致均核实。它们是**开发方实际发布回归字节，本审查方核验**，不是本轮新运行完整SDK或P6产品/浏览器通过。

原106条canonical目录及P6八条逐字段快照相同，5MVP/3Competition Ready。所有8项仍为本阶段必需交付，不因当前Planned静默删减。六页面、统一入口、真实来源/终态、精确数值、正式入口拒绝、历史不覆盖、工程范围及测试层次总体方向正确；以下三项具体边界尚不能放行实施。

## 发现001 — High：多阶段完成/恢复缺少Task级屏障

位置：[TASK_AND_RECOVERY_CONTRACT.md:9](https://github.com/wwooyy429/Alpha-Quant-Research-Platform-AQRP-/blob/{FIX}/docs/audits/phase-6/TASK_AND_RECOVERY_CONTRACT.md#L9)，关联INTERFACE_DRAFT:9和TEST_AND_EVIDENCE_PLAN任务故障矩阵。

文档一方面为每个子阶段/动态调仓分配slot，engineering_pipeline明确包含P3/P4/P5；另一方面对合法核心终态直接规定恢复原run映射和Task终态，没有区分“子阶段完成”与“全部Task完成”，没有按kind冻结必需阶段、所有required slots齐备条件或剩余阶段如何继续/停止。G16–G19只是单状态事件，没有多阶段完成答案。

最小设计反例：P3真实SUCCEEDED且manifest有效，P4/P5尚未执行，写Task映射前宕机。恢复找到P3合法终态；按当前未限定的核心终态→Task终态解释会提前标Task SUCCEEDED，完整回测并不存在。P3/P4成功而P5缺失同样未闭环。独立设计模型列出这两个不应成功的状态及全链成功正控；这是**规范歧义反例，不是已观察到的P6产品错误**。

修复：分别冻结research/engineering_pipeline/replay的固定阶段与动态slot完成条件；子run终态只恢复对应slot。Task成功必须所有必需阶段及最终真实工件/父链已验证成功。明确剩余阶段安全继续或RECOVERY_REQUIRED的判据，禁止重跑已完成P3/重复计数或取消退款。新增P3成功/P5未开始、P3/P4成功/P5失败、各阶段提交/映射前后宕机、取消及全链成功的设计答案与实际G2矩阵。无需引入任意DAG/插件框架，用受限固定编排即可。

## 发现002 — Medium：嵌套P4的可信上下文/根布局尚无具体衔接

位置：[DEPENDENCY_AND_COMPATIBILITY_PLAN.md:11](https://github.com/wwooyy429/Alpha-Quant-Research-Platform-AQRP-/blob/{FIX}/docs/audits/phase-6/DEPENDENCY_AND_COMPATIBILITY_PLAN.md#L11)及TASK_AND_RECOVERY_CONTRACT:3、9；实际既有`src/aqrp/backtest/engine.py:324`、`provider.py:191`。

允许适配清单列ExperimentLedger.start、P3/P4/P5外层应用服务；但现有P5在Simulator._risk_portfolio内部不带TaskContext调用construct_engineering，根固定为该P5 run下portfolio-runs，再于该根验证P4终态/原始字节。外层P5获TaskContext并不能自动说明内部每个决策P4怎样预分配slot、绑定父P5/task/config/物理根、在调用前持久化，以及怎样同时保持文档的共享根要求和原来源/重放约束。

最小边界：Task已预分配P5，内部第一个P4提交终态后、外部slot映射写回前宕机。没有明确传播/slot及根绑定方案，恢复者不能仅凭一个合法P4 UUID证明其属于该task/decision；也不能安全重做或把它当别的任务结果。此项指出缺失的具体设计，**不声称没有可行实现或现在已有UI漏洞**。

修复：给出TaskService→P5 service→内部逐决策P4的可信传播机制及完整非金融适配文件表。可选显式参数或受控调用上下文，但须规定并发隔离、作用域、旧无context调用兼容、不可被网页伪造。冻结(task,slot,service kind,decision,parent,run_id,root,config hash)绑定和登记时点；区分P3共享家族预算根与P5内部P4实际根，明确目录布局/校验/重放。补内部P4提交/映射断点与错UUID/错根负控；不以全局monkeypatch或事后自报UUID补所有权，不改金融算法。

## 发现003 — Medium：参考模型默认28位精度违背精确输入边界

位置：[reference_check.py:8](https://github.com/wwooyy429/Alpha-Quant-Research-Platform-AQRP-/blob/{FIX}/docs/audits/phase-6/reference_check.py#L8)、9；关联MATH_AND_COMPARISON_CONTRACT:5、7。

本审查方从整数/Fraction另写算法复算，原32组输入/答案/容差全部正确；但扩展到规范未排除的精度边界，**实际执行开发参考函数**得到：

| 输入/动作 | 独立精确答案 | 当前参考 |
|---|---|---|
| 百分比0.123456789012345678901234567890123456789 ÷100 | 0.00123456789012345678901234567890123456789 | 0.001234567890123456789012345679（静默舍入） |
| 金额999999999999999999999999999999.995，HALF_EVEN分位显示 | 1,000,000,000,000,000,000,000,000,000,000.00 | InvalidOperation |

原因是Decimal除法、normalize及quantize使用默认context精度28。规范承诺精确字符串/无金融舍入回写及大整数原值，没有规定28位上限。现有32小值通过不能覆盖这些边界。这是当前**设计参考执行缺陷**，不是未来尚未实现UI已出错。

修复：百分比用整数/Fraction或足够且明确的localcontext计算，保留全部输入精度；大金额显示明确精度/溢出与原始值保留策略。若确需schema范围上限，先明确范围并显式拒绝超限，不能静默舍入。保留原32正确答案字节，补超过28位小权重、大整数金额、正负HALF_EVEN临界和溢出负控，提供独立字面答案。该缺口影响本阶段新精确适配的可审查答案，需与计划一同修正后复核。

## 逐需求结论

| ID / 等级 | 已有设计覆盖 | G1处置 |
|---|---|---|
| UI-001 MVP | 真实状态/因子数/最近任务/完整性错误，不凭图表或文件存在报成功 | 覆盖；Task状态受001影响 |
| UI-002 CR | 精确FactorRef/参数/工程状态、选择配置/权重/比较/新增revision回滚，无任意Python | 覆盖；精确权重参考受003影响 |
| UI-003 MVP | P3研究配置、原IC/Rank/ICIR/分层/衰减/OOS、NA原因、家族预算共享、无正式Test | 覆盖；流水线完成与恢复受001影响 |
| UI-004 MVP | 真实P3/P4/P5、工程模式/正式拒绝、逐桶/订单/Fill/unknown不回退余额 | 001/002/003需闭环 |
| UI-005 CR | 原manifest/UUID/路径/字节来源验证，比较与声明范围重放，不覆盖历史 | 覆盖；嵌套来源及恢复受001/002影响 |
| UI-006 CR | CAS默认值新revision/回滚、仅影响新请求，依赖/日志，不管账户ACL | 覆盖；显示精度边界受003影响 |
| UI-007 MVP | 同canonical config、精确金融字段、有限元数据差异、原CLI/TaskCLI/SDK/真实UI两因子链 | 覆盖；上下文/来源映射与精确转换须补齐 |
| UI-008 MVP | SQLite幂等、唯一claim、原子边界取消/unknown失败关闭、原失败与试验保留 | 001/002为完成/身份协议缺口 |

其余意见：固定Ref/canonical/config/defaults/catalogue及真实父链、manifest/清单外追加/错UUID/路径逃逸拒绝、文本转义、禁任意插件/命令、缓存不替代真状态的方向符合既有契约。正式入口仅后端APPROVAL_REQUIRED，单OS用户/TaskContext不构成真实隔离，计划已正确保留边界。Task取消/失败不退还已发生P3试验，P3家族根不能按task重建的要求应保留。没有要求扩张P7、部署或新经济口径。

## 实际独立执行、依赖与证据

环境：`{env['python']}`，标准GIL，`{env['platform']}`；Python可执行文件/其SHA256、全部argv/cwd/UTC/退出码/stdout/stderr见ENVIRONMENT及*.command.json/*.log。源检出/初始化直接由工具执行，原输出保留在会话工具记录；后续核验统一run_capture捕获。首次4738文件比对逐个调用git show过慢，核实只读子进程身份后中止该审核辅助进程（退出4294967295原记录/脚本保留），改用一次ls-tree读取基线blob身份并逐文件SHA256/Git内容hash核对，完整批量轮PASS；不是产品失败或放宽比较。初始工作目录rg无匹配返回1；一次只读查询误找仓库内resolve_candidates.py（实际在开发外置目录），未改变任何文件或产品结论。原失败记录不删除。

独立设计执行：32/32原Golden通过；20条额外精度/有类型null/0/false/重复JSON/非有限等边界推导，2个多阶段未闭环状态及1完整正控；开发参考在两条独立高精度答案上不一致。只运行设计数学/契约模型，未运行P6实现。没有使用未来待测函数生成expected。INDEPENDENT_DESIGN_RESULTS含每项输入/答案/容差/原始实际值。

依赖独立验证：从官方PyPI新取固定[Streamlit1.66.1](https://pypi.org/project/streamlit/1.66.1/)与[Plotly7.1.0](https://pypi.org/project/plotly/7.1.0/)元数据，核版本/Requires-Python/候选hash。使用已锁uv0.13.4对冻结的组合候选再做Windows x64/Python3.13.16、Linux x64/Python3.13.16 metadata-only解析，版本和全部hash集合分别完全一致；Windows51=原core22+扩展29，Linux50=core21+扩展29。原requirements.lock SHA256仍为`86c7bf65c9a9690036006360062c8cd10a91279705b4070af7033d7699abffeb`，扩展锁不含core包项，未扩大原core wheel批准hash集合。**没有安装UI，实际wheel安装/import/浏览器/双OS UI兼容NOT VERIFIED，按计划留待授权后验证；此限制本身不阻断G1。**

AppTest模拟与真实浏览器证据已分开，符合[官方AppTest说明](https://docs.streamlit.io/develop/api-reference/app-testing/st.testing.v1.apptest)的模拟API性质。未来六页面/真实交互、两因子、取消/失败/下载证据以及全SDK/双OS原ZIP/源码wheel环境终态链矩阵总体足够，须补001/002的实际故障用例；AppTest不代替浏览器或真实ACL。

本轮新读取计划commit的Actions run39936980379两job均completed/success及工件API身份/digest；该自动CI是继承的P5回归。**本轮未下载核验该新plan run两份原始ZIP/测试计数，因此其原包与成员范围NOT VERIFIED，不冒称新独立完整SDK/产品通过。** 已核P5前置发布原包与此明确区分。没有把API success或旧1158当P6实现通过。

开发计划Evidence.zip84283342字节，SHA256 `3d3b0ec529a72f5b90755b823d8dc367d148fdfd49b6aec1c380380fda3b527b`，82声明文件+manifest、CRC/精确成员/所有大小hash及Fixed-Source.zip全部跟踪文件对固定Git字节核验通过。P5发布包与合并后SDK字节另核如上；原发布20+4/91为开发回归，记录/工件保留，不补写为本轮重新执行。

## 待决定、未验证与后续

开发方先解决上述三项，提供新完整固定SHA及新增独立字面答案/计划差异再交G1复核。恢复协议、可信上下文适配和数学参考属于本次技术设计闭环，不要求用户替尚未明确的方案批准；也不授权据此开始业务实现。技术阻断闭环后，再按OPEN_QUESTIONS向用户确认具体方案及单独申请P6实现授权。无新金融经济选择、依赖升级或真实权限申请被本轮默许。

WI-R2-001/002及整体真实Windows隔离继续DEFERRED / NOT VERIFIED；正式最终Test未运行，金融批准NONE；完整历史宿主NOT VERIFIED，仅既有已接受package/lock/oldRef/result replay范围。原失败/封存证据继续保留。本轮未启用账户、修改真实ACL/服务/调度、部署、实盘、运行真实正式Test、授金融批准、合并/打标签或进入P7。PLAN BLOCKED不改变Phase5受限发布事实；未来PLAN PASS亦不等于实施授权、G2通过或用户阶段验收。

独立报告、逐发现、数学/契约反例、冻结/发布/依赖核验、源码定位和实际命令日志统一封存；独立EVIDENCE.zip的字节/sha256/manifest与CRC/全部成员核验见RECEIPT.json。收据是字节封存，不是数字签名或阶段许可。
'''
(O/'REPORT.md').write_text(report,encoding='utf-8')
handoff=f'''开发Codex：GPT Work已对Phase6 PR #9固定`{FIX}`完成独立G1预审，结论**PLAN BLOCKED / REQUEST CHANGES（1 High、2 Medium）**，当前仍只允许计划修订。001 High：TASK_AND_RECOVERY_CONTRACT.md:9将合法核心终态直接提升Task终态，未区分engineering_pipeline多阶段完成；请为research/engineering_pipeline/replay冻结required stages/动态slot及全链完成条件，子run成功只恢复该slot，P3成功而P5缺失/失败不能Task成功；补每阶段提交/映射断点、取消和全链正控，已完成P3不重跑/预算不退。002 Medium：既有P5在engine.py:324内部不带context调用P4并固定在该P5 run的portfolio-runs根，当前外层服务适配清单未说明TaskContext怎样可信传到每次内部P4、预分配并持久化slot/父run/decision/config/root；请明确传播机制、并发隔离/无context兼容、物理根布局、非金融适配文件及内部P4崩溃/错UUID/错根验收，不以事后UUID映射代替所有权。003 Medium：reference_check.py:8–9默认Decimal精度28，使合法长百分比除100静默舍入、大金额quantize抛InvalidOperation；请改精确计算/明确量程与拒绝策略，保留原32正确答案字节，补28位以上小权重、大金额和正负HALF_EVEN边界独立字面答案。原32/32独立复算通过，两OS51/50组合与扩展29候选解析/hash集合独立匹配，4738冻结文件/源码测试工具CI根锁未改、P5发布前置已核；这些不是P6产品通过。详情/最小设计反例与实测参考错误见同目录REPORT.md、FINDINGS.json、INDEPENDENT_DESIGN_RESULTS.json，原始命令/日志/hash已封存。修订后提交新40位固定SHA供G1复核；不开始P6业务实现，不合并、打标签、部署、实盘、进入P7或安装启动UI。Windows R2及整体真实隔离仍DEFERRED / NOT VERIFIED，正式Test未运行、金融批准NONE、完整历史宿主既有限制不变；不启用账户/改真实ACL/服务/调度或授金融批准。'''
(O/'DEVELOPER_HANDOFF.md').write_text(handoff+'\n',encoding='utf-8')
print(json.dumps(dict(fixed_sha=FIX,verdict=result['verdict'],counts=result['counts'],report_bytes=(O/'REPORT.md').stat().st_size),ensure_ascii=False))
