# AQRP Phase6 固定版本 G2 独立审核

完整固定 SHA：**eae807f957f178d19bc55dcfbd668caff5470c6e**；PR #9。审查者：本会话 GPT Work 补充审核员。审查日期：2026-10-24，Asia/Shanghai。

**结论：G2 BLOCKED / REQUEST CHANGES。新增三项 OPEN：1 High、2 Medium。** 开发方 DEV-P6-001 配置编辑问题已由本轮独立确认 CLOSED — FIX VERIFIED。主审新干净 SDK 1496项、官方双系统各1496项及其原始字节核验通过；通过结果不覆盖下述新反例与需求缺项。尚不能进入 Phase6 用户阶段验收或合并发布。

## 固定版本与范围

起止 PR 描述 AQRP_FIXED_REVIEW_SHA、实际 head、独立 detached 检出一致。副本 E:/WORK/AQRP-audits/p6-eae807f/src 无共享 alternates，工作树干净。本轮没有修改候选源码、测试、锁或开发分支。

P5 main / phase5-baseline / v0.5.0 仍同点 59246f9fd391c1713b6bed65dd22280f4d248493；全部旧标签对象及目标未变化。G1 已审 e71f6f090b102e4abfd70a5999e495f49546a1b5；仓库 IMPLEMENTATION_AUTHORIZATION 记录用户明确接受 C-P6-001/002/003 并单独授权既定八项实施。本报告不追加实施范围或任何发布权限。

原106项 canonical 目录及 P6 八项逐字段快照保持，5 MVP/3 Competition Ready。实现归档起点 0242db37b4c822e7c73ef6c17faf104bcea54892 的5016份保留文件，逐文件 SHA256、大小及原 Git blob 身份一致；64份变更/新增文件和自排除身份文件精确覆盖5081份跟踪文件。22份既有适配文件与 COMPATIBILITY_IMPACT 清单完全一致。原 G1 合同及32＋95答案字节保留。

既有金融模块差异已逐段审查：ledger 预分配归属及排除 Task 运维字段的重复试验指纹；P3/P4/P5服务的可选 context、检查点；Simulator 实例上下文、内部 P4 预登记/复用；provider 原门禁前的归属验证；P5重放目标封存。未见数据、标签/拟合、推断、组合取整、风险、撮合、金融账本或绩效公式被替换。新任务包装仍须正确使用这些内核，001/002正是该层的实现问题。

## 发现001：High / OPEN — 改变参数自动换family，预算与污染控制可绕过

位置：[task_requests.py:270](https://github.com/wwooyy429/Alpha-Quant-Research-Platform-AQRP-/blob/eae807f957f178d19bc55dcfbd668caff5470c6e/src/aqrp/services/task_requests.py#L270)。相关 ledger.py:261–288、services/research.py:506–509、P3 STATISTICAL_CONVENTIONS.md:11。

freeze_request 以除 family 外的整个研究 config 哈希生成 family.id，再给每个新 family 设置 budget=12。lookback、direction、horizon、预处理等变化会自动获得新 family。核心 ledger 按 family 统计预算，multiplicity 污染标记只见当前 family 的重复假设/完全重复试验；UI 包装没有预先冻结一个覆盖本次参数搜索的研究计划。

主审在新安装 wheel、独立工程工作区实际执行：

- 同一 P1 数据身份、因子 momentum、同一决策日、horizon=1，仅依次改 lookback=1…14。
- 14个真实研究 Task 全部 SUCCEEDED；14个不同 family；每个 budget=12、over_budget=false，multiplicity.contaminated=false，均单独 m=1。
- 同一个全局 trials.jsonl 确实保留14条，prior_data_attempts 为0…13。因此这是预算/污染判定边界问题，未丢失日志。
- 新工作区同配置对照只有一个 family：前12次成功，第13/14次均 EXPERIMENT_BUDGET_EXCEEDED。证明限制本身存在，参数变化却绕开它。

依据：既有规则要求参数、方向、期限、预处理变化均记实验；P3统计约定禁止观察结果后跨family改名规避校正，并要求自适应选择/超预算保留污染。已审 P6 也承诺共享家族根、次数和预算不重置。自动把每种配置当新 family 并标未污染，不符合该承诺。工程目的和金融批准 NONE 的边界保持，未声称本例获得正式金融资格。

修复要求：在观察结果前冻结研究计划/campaign的身份、全部声明候选及变体和预算，让同一计划的参数/方向/期限试验持续记入该范围；新计划也须保留数据级既往访问/污染事实。不能只改成一个常量 family 名称而继续改变已冻结 definitions，也不能通过涨预算、隐藏失败/取消或删记录消除反例。可选择预注册搜索集合或对未登记的自适应变体明确拒绝，但不能静默发放新预算和“未污染”标签。补跨参数/方向/期限及取消失败的安装包回归、相同配置正控，提供新固定 SHA。

原始证据：SEARCH_VARIANT_PROBE.json、SEARCH_REPEAT_CONTROL.json、COVERAGE_AND_FINDING_CONTROLS.json；对应 search-variants、repeat-budget-control 的原始命令/日志；两个完整研究工作区封存。

## 发现002：Medium / OPEN（阻断）— Task取消收尾没有重新验证实际财务提交前缀

位置：[tasks.py:628](https://github.com/wwooyy429/Alpha-Quant-Research-Platform-AQRP-/blob/eae807f957f178d19bc55dcfbd668caff5470c6e/src/aqrp/services/tasks.py#L628)，范围620–646；依据 TASK_COMPLETION_CONTRACT.md:23、TASK_AND_RECOVERY_CONTRACT.md:9。

取消异常处理只用 read_core 核顶层 manifest/结果原字节，再读结果中已有的 financial_state_known 标志。已完成 P5 的结果通常没有失败路径上的该标志。此处没有重新读取 transactions 目录及其初始锚点/实际提交链、transaction-files 和金融投影。

主审用真实服务、SQLite、磁盘做三组独立断点：

| COMPLETION_BEFORE_SQL时的条件 | 实际Task结果 | 财务读取／对照 |
|---|---|---|
| 完整已核前缀，收到取消 | CANCELLED | 原核心资金98.1仍可验证，正控通过 |
| 最后一条实际成交提交文件损坏，再收到取消 | **CANCELLED，error=KeyboardInterrupt** | TransactionStore和financial_result均报TRANSACTION_CHAIN_CORRUPTED |
| 同样的提交损坏，不请求取消 | INTEGRITY_ERROR / usable=false | 原SQL成功记录保留；公开成功读取能够发现损坏 |

故障发生前，本例真实 R/P4/B 及全局 _proofs 已完成；现金98.1、权益998.1，UI流水线有19条事务。主审只在专属负控工作区给最后一条实际 commit 文件追加一个空格，保留原文件/前后hash；完整性检查立即确认 TRANSACTION_CHAIN_CORRUPTED，再发起正常 cancel。没有改 manifest、DB状态或返回字段来制造期望结果。

批准契约要求未知财务状态一律 FAILED＋COMMITTED_STATE_UNVERIFIED，不能认证安全取消。本例的 Task 与 DB 却仍 CANCELLED，且后续 status 对取消任务不复核该财务前缀。该项涉及取消终态/错误分类和安全取消承诺，故 Medium 仍阻断。财务读取本身继续拒绝损坏；本轮未观察到坏余额被作为可信结果展示。

修复要求：发布 Task 级安全取消前，对所有已启动 P5／适用 replay，包含已经 SUCCEEDED 的子run，重新执行实际磁盘前缀、transaction-files、锚点、逐桶/科目及既有完整金融对账；任何读取/枚举/链/账目未知转 FAILED＋COMMITTED_STATE_UNVERIFIED。保留取消意图及原子run、原失败/原始终态，不重写历史来维持取消成功。补该断点、initial/提交丢失、读取/枚举报错及正常取消对照；适用 replay 路径也要覆盖。本轮实际负控为 P5，未把它冒充全部 replay 故障已执行。

证据：CANCELLATION_FINANCIAL_PROBE.json、cancel-corrupt-original-transaction.json、三个完整负控/正控工作区及 cancellation-financial-rerun 命令/日志。

## 发现003：Medium / OPEN（阻断）— UI-003股票池选择未交付

位置：[ui/app.py:250](https://github.com/wwooyy429/Alpha-Quant-Research-Platform-AQRP-/blob/eae807f957f178d19bc55dcfbd668caff5470c6e/src/aqrp/ui/app.py#L250)、task_requests.py:114、231；依据 canonical UI-003（V3.0§9.3）及已审 PAGE_SPECIFICATIONS 的股票池/因子/区间/期限选择。

当前页面只有“fixed public synthetic six-asset catalogue”的说明；共享请求字段支持因子、日期、期限等，却没有任何股票池或池目录ID选择。builder直接沿用单一 catalogue.config 的 SYN_U。安装包中即使显式指定当前池 universe_id 也返回 UNKNOWN_TASK_DRAFT_FIELD。未知字段拒绝本身正确；结合页面和接口检查，可以确认没有另一套已实现的股票池选择机制。

该缺项未见用户明确豁免，不能把一个固定池的研究通过当成整个 UI-003 选择能力完成。此处不要求接真实市场源、不允许网页任意路径、不要求新金融算法。

修复要求：补可信已登记工程股票池/目录ID选择，冻结所选身份、历史membership和数据/PIT引用，走原P3校验；纳入 canonical config_hash、三入口一致与未知池拒绝测试。若确需永久收窄为固定池，先提交具体需求影响并取得用户明确范围变更，不能用 Planned/Unsupported 或笼统“受限工程”自行删除原必需能力。本轮无需用户替开发方尚未补齐的功能直接验收。

证据：STOCK_POOL_SCOPE_PROBE.json、源码/字段表、固定版本原UI-003快照；原浏览器资料中的研究表单及固定池说明与源码一致。

## 已确认关闭的开发发现及G1状态

DEV-P6-001：CLOSED — FIX VERIFIED。本轮在新安装 wheel、全新工程工作区、本机loopback实际 CUA 浏览器中建两个独立会话：

1. A从revision0保存lookback=3，实际revision1；再保存2，实际revision2。
2. B已在revision1加载，输入4后提交；返回DEFAULTS_REVISION_CONFLICT，当前2/编辑基准1，草稿4保留，没有创建新revision。
3. B明确Reload后以基准2保存4，形成revision3；回滚target1追加revision4，值恢复3。
4. 只读SQLite独立读取的原始历史为 **[3,2,4,3]**，fee_budget="12.50"均保留，各payload/hash相符。没有用额外手工rerun迎合原错误。
5. 主审保存22份AX、2张原始JPEG，动作顺序、独立进程argv/安装包、DB和停止收据均封存。两个测试标签已关闭，仅本轮创建的loopback进程经身份核实后停止。

原C1失败、旧1486自动化成功与修复前后资料均保留历史，不移作新版本通过证据。G1的001/002/003仍是CLOSED_DESIGN，不把新实现缺陷改写成原计划审核曾验证了实现。原数值修复在安装包实测也通过。

## 八项需求与实际验收覆盖

| 需求 | 实际实现及核对 | 本轮处置 |
|---|---|---|
| UI-001 MVP | 真Task/因子数量、最近R/B入口、完整性错误；主审组件/SDK与开发浏览器资料 | 已有真实功能；取消终态受002影响 |
| UI-002 CR | 四个精确Ref、参数、选择/权重、配置revision/回滚、历史Ref；数值与配置双会话实测 | 现有受限目录范围通过；无任意Python执行 |
| UI-003 MVP | 真实P3、因子/日期/期限/方向/预处理、IC/Rank/ICIR/分层/衰减/OOS原工件 | **PARTIAL / OPEN-001、003**；固定合成六股不能替代股票池选择 |
| UI-004 MVP | 真实P3→P5内部P4、风险拒绝保留原子事实、订单/Fill/资金/绩效，正式后端拒绝 | 核心正向及旧回归通过；取消收尾受002影响 |
| UI-005 CR | 原manifest/唯一成员/hash/父链、下载、比较、新E/P4重放及旧Ref范围执行 | 原字节/只读和正常重放有证据；试验管理受001影响 |
| UI-006 CR | 默认配置追加CAS、显式重载、回滚、新请求边界、依赖/安全日志 | DEV-P6-001独立关闭；未操作真实凭证/ACL |
| UI-007 MVP | 主审新SDK实际跑SDK/旧CLI/任务CLI/AppTest两个因子完整链和精确投影；开发真实浏览器另核 | 当前已支持配置的同核证据通过；股票池维度缺失，001也需同入口回归 |
| UI-008 MVP | SQLite幂等/10进程claim、epoch/预登记slot、真实恢复、取消/日志/图表、completion+SQL | 主体真实实现及现有故障测试通过；001/002阻断完整通过 |

八项均有代码/测试定位，未把 CR 静默延期；“存在测试”不等于每项需求已经独立完成。完整任务完成屏障、P5内部P4绑定/物理根/原适配raw、resume复用、P3预算根、原manifest/candidate/risk/发布字节门禁整体存在。实际测试和本轮反例同时保留。

正式入口在共享builder/后端拒绝，FINAL_TEST无网页选项；没有任意DAG、任意因子代码上传、外部插件框架、P7竞争模块或新回测引擎。历史Ref重放限定既有已接受包/锁/声明结果投影，未扩张到任意旧宿主。

## 主审实际执行、环境与原始证据

主审新干净SDK根：
E:/WORK/AQRP-runs/gpt-p6-eae807f-20261024-e9c8e3a6-d633-423a-b48a-fe1c7adbbabb/aqrp-b7f5fb35-2718-48ce-b655-058d50f92c96

CPython3.13.16标准GIL/x64，Windows-11-10.0.26300-SP0；基础解释器SHA256 31fe10b4ed82a2f960af0ef9931f46a4b84ff286f8b6ffd9dee098cf4f10f17f。新venv按原core锁＋29包UI扩展哈希安装、构建并安装0.6.0.dev2 wheel。初始提供已保留wheel目录作下载候选，仍执行新环境哈希安装，没有复用已安装开发环境。网络实际下载/命令原文在commands.log，不把候选缓存说成全程离线。

- **完整SDK进程exit0、environment.complete=true、dirty=false，1496 passed / 0 failures / 0 errors / 0 skipped。**
- 所有82个bundle模块均在覆盖报告，主审另按批准阈值逐文件复核。任务/context/state95/90、原关键模块阈值不降，纯UI/CLI按已审80/70。82个Git源码、项目wheel与实际安装模块逐字节一致。
- SDK中真实SDK/旧CLI/任务CLI/AppTest、Momentum/Reversal全链、config_hash/精确研究及金融投影、旧66文件/三个已发布run及旧Ref执行、32＋95设计参考、P1–P5烟测、扫描正负控均通过。AppTest为组件执行，本段不称真实浏览器。
- 另复制原始不修改脚本/答案，实际运行原20＋4回归均通过；91项Fraction/矩阵/有序p独立数学检查通过。旧数学脚本静态reviewed_sha标签原样保留，当前实际执行由eae固定wheel、包装命令及原始日志绑定，没有改写历史执行身份。
- 安装版ui.numbers用主审先前独立Fraction/round期望测试852输入×6精度/陷阱，共5112次观察通过；含4096/4098边界、超限/类型/指数/非有限/Unicode、两条原长数反例及正负HALF_EVEN。expected来自原独立答案字节，不由当前被测函数生成。
- 新反例独立于上述1496计数；没有把预算对照、故障试验、数学观察加总成产品pytest通过数。
- 两项原数值反例未因新增输入量程被排除；原P1–P5数值域规则保持，词法接受不等于金融可执行。

主审SDK独立ZIP：166035035字节，SHA256 **dae6c76de5954e7dc633f703e1693dccff61f8b8c518ca302582e1203c0c5933**，11115个选择文件加selection，共11116成员，CRC/精确集合/全hash核验通过。

独立完整SDK核心命令为固定检出下 Python31316/python.exe -X utf8 tools/ci.py；每个内部命令argv/cwd/开始结束UTC/exit在SDK commands.jsonl及combined raw commands.log。额外审查命令由run_capture.py记录，不需要从本文推测：init-00…06、archive-verification、scope-verification、search-variants、repeat-budget-control、cancellation-financial-rerun、stock-pool-scope、installed-numerics、original20-rerun、original-reviewer4、original-math91、browser-start/stop、browser-verification-rerun、controls-and-coverage、independent-sdk-verification等。

本轮辅助验证器的首次失败保留并区分：取消探针误把旧fixture9事务数用于本次完整UI profile19事务，断言在损坏/取消注入前阻止实验；纠正为本试验必要前提“98.1且前缀非空”，新工作区重跑才是本报告反例。原20首次复制漏两个相对目录的phase1_input.json，collection报错；补回固定Git原字节，未改脚本/正确答案。截图API实际返回JPEG，首次误按PNG签名检查失败；后提供同字节JPEG扩展名副本，原件及hash保留，未转码图像。各次原stdout/stderr、错误XML、脚本和工作区都保留，详COVERAGE_AND_FINDING_CONTROLS。只读误查不存在的报告文件不归为产品失败。

## 官方CI、开发证据与浏览器证据等级

新从GitHub连接器读取run39983233050及job/artifacts，attempt1；Windows job120515657495和Ubuntu job120515656895均completed/success。CI workflow已明确checkout head SHA；实际environment.code_commit均为本eae固定提交，不把临时merge误当已合并main。

| 官方原始ZIP | 测试 | 字节 | 与新API匹配SHA256 |
|---|---:|---:|---|
| Windows12515158777 |1496|181803920|d054222d48f853eb62c2c760e0ff740e5b9b088846606841b1c10c110e275e45|
| Ubuntu12513829924 |1496|222929025|a7fe418a0c10535b0fceb8e27838828a8c1befa7391a809ff84f998dce5391b9|

两份收到的官方原始ZIP未重打包；独立核新API身份/digest/长度、CRC、全部selected hash及精确成员，JUnit/完整环境、82源码wheel、22/21 core依赖wheel与各29 UI wheel/锁、命令/原终态链/八表快照、原Ref记录均通过。Windows11115/Ubuntu11114声明文件之外，各5658个pytest current上传副本，主审另按237组**完整子树集合及逐字节相同**对账；另有自排除selection。未冒称副本具有原symlink/ACL身份，也未声称主审亲自在远程runner上执行。

core锁SHA256仍86c7bf65c9a9690036006360062c8cd10a91279705b4070af7033d7699abffeb；UI扩展锁ff28bee3db0e2a4c0b3d3b5037186a5ace5e75836027268424bbe469da4a75a3与G1候选/根文件/包内文件一致；新bundle为7ddc968a3e2f2de42a95ed7538735e34af1778b947032e5e0b61587cabc5c4ab。未猜测或升级依赖版本。

开发外层ZIP731873958字节，SHA256 **97f738a9a2c4dedace11a213dda254020189368f7cd184693a6e0623776c9df7**；1132声明文件＋manifest共1133成员，CRC/精确成员/全大小hash及固定源码tar全部5081跟踪文件对Git字节核验通过。开发本地SDK原包1496亦独立核验，与主审新SDK分开。

开发真实浏览器ZIP4471007字节，SHA256 **13f017ff94af7807d1c9137fc39fc4fcd9cf1455974fa18c0fdcca27e154ad61**；983成员全字节核验。55份AX、21份JPEG及动作顺序、六页面标题、正式拒绝/实际失败/取消/CAS文本、原下载/重放/父子资料均有原件；相关开发parity/源42文件不变/旧14请求等记录按其执行身份保留。本轮未把开发者每一步交互或全部比较重新记为主审亲自执行。

主审实际新浏览器范围是上述双会话Settings/连续保存/CAS/显式重载/追加回滚，22份AX、2张原始JPEG、SQLite及进程身份可核。其余六页面/两因子三入口在主审新SDK的真实组件及服务执行通过，并核开发真实浏览器原始资料；未声称主审另在浏览器完整重复所有六页。关闭的DEV-P6-001有主审实际浏览器与磁盘独立证据。

## 处置及未验证边界

开发方须保留本报告/三项反例/首次辅助失败/旧C1和历史报告原字节，按既定范围修复001/002并补齐003，保留完整既有回归与新增独立期望，再给新完整固定SHA和干净SDK/双OS官方原包/实际浏览器证据复核。不得只改正确期望、把失败标记为Unsupported或自行关闭发现/改判G2。若提出范围变更，先具体说明受影响需求及批准依据。

WI-R2-001/002与整体真实Windows隔离继续 **DEFERRED / NOT VERIFIED**；正式Test未运行，金融批准NONE；完整历史宿主仍未验证，仅保持已接受的软件包/锁/oldRef/声明结果重放边界。工程单用户TaskAuthority/Python对象、故障注入或浏览器/CI通过不构成真实三主体隔离。本轮没有启用账户、改真实ACL/服务/调度、部署、实盘、运行正式Test、授金融批准、合并、打标签或进入P7。

主审临时loopback UI只用于已授权的工程验证，测试标签关闭，自己的启动进程已核身份停止。实际原始命令、环境、反例工作区、源位置、报告及所有封存原件的大小/hash、CRC/精确成员核验见本目录RECEIPT.json。收据证明字节身份，不代替数字签名、用户阶段验收或任何发布许可。

配置编辑已修复的实际浏览器证据（不表示整体G2通过）：

![过期配置保存被拒绝，原草稿保留](C:/Users/11638/AppData/Local/AQRP/reviews/p6-g2-eae807f-independent-20261024/browser-observations/015-stale-rejected.jpg)

