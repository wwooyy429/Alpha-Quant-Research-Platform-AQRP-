# GPT Work — Phase6 G2 固定版本增量复核指令

仓库：https://github.com/wwooyy429/Alpha-Quant-Research-Platform-AQRP-
PR #9：https://github.com/wwooyy429/Alpha-Quant-Research-Platform-AQRP-/pull/9
AQRP_FIXED_REVIEW_SHA: 3017a097b49ecdae68228ca9a417fcd03c313200

请只复核上述完整40位版本。先核对 PR 描述唯一锁、远端实际 head、Git 树、安装 wheel、环境及工件哈希；如果版本漂移，单独记录并停止把漂移 HEAD 当作已审版本。当前是开发方修复及自测交接，WORK-P6-G2-001/002/003 仍 OPEN / FIX_IMPLEMENTED_PENDING_INDEPENDENT_RECHECK，只有你的独立复核才能确认关闭。G2、用户阶段验收和发布是三个不同事实。

证据目录：C:\Users\11638\AppData\Local\AQRP\reviews\p6-g2-3017a09-developer-20261024T092710Z。外层 ZIP 与精确成员/manifest 哈希见 SEAL.json；payload/FILES_SHA256.json 自排除，外层收据避免循环自证。请独立读取原始文件，复跑原反例及新边界；开发方验证脚本和截图不能替代独立执行。

固定源码资料：docs/audits/phase-6/IMPLEMENTATION_REVIEW_PACKAGE.md、IMPLEMENTATION_TRACEABILITY.md、IMPLEMENTATION.md、G2_FAULT_MATRIX.md、IMPLEMENTATION_IDENTITY.json、DEVELOPER_FINDINGS.md；g2-eae807f/DEVELOPER_RESPONSE.md、CAMPAIGNS_AND_UNIVERSES.md、RECEIPT_VERIFICATION.json、CANDIDATE_CI_FAILURE.json、SECOND_CANDIDATE_CI_FAILURE.json、SQLITE_INITIALIZATION_REPAIR.json。八项原需求及 C-P6-001/002/003 继续适用，不扩大至 P7。

原审 eae807f957f178d19bc55dcfbd668caff5470c6e 的报告、交接、反例脚本/输出、manifest、收据已原字节归档。原 ZIP 902364045 字节，SHA256 086c0a1d7128c241bff30cfed32f9d5178940c9decf3942cd462021f30983b3c，304 声明文件和 manifest 逐成员核验，保留路径见 independent-original/ORIGINAL_ZIP_RETENTION.json。DEV-P6-001 配置失编辑问题已由原独立报告 CLOSED — FIX VERIFIED，本轮回归不冒充首次关闭。

## 三项原发现

1. High 001：显式不可变 campaign 预登记有限候选全集、全局 hypothesis 和共同 Holm 定义。首用默认仅冻结首组参数及明确候选集合一次；未登记变体报 UNREGISTERED_CAMPAIGN_VARIANT，不能自动新建 family。全 workspace 同数据共享12候选×期限单位预算，随 Task 在 SQLite 原子预留，失败/取消不退款，幂等不重复。新计划保留既有访问、旧试验台账及跨 family 污染。请独立验证参数编辑、换名 campaign、并发、失败/取消、旧台账、预算耗尽及多重检验完整性。workspace 工程边界不等于跨宿主安全隔离或独立统计样本。
2. Medium blocking 002：取消前重读所有已启动 P5/重放（包括已完成子阶段及源）的物理事务链、初始锚、实际文件集合和完整财务 projection。损坏、缺失、读取/枚举错误或未知状态必须 FAILED / COMMITTED_STATE_UNVERIFIED，不能 CANCELLED，不能信任旧 verified 标志。保留取消意图、原错误和失败字节。封存后发生损坏，对外 INTEGRITY_ERROR，数据库原终态历史不改。请独立复跑原取消损坏反例，并查提交后异常、完整现金桶/backing 关联字段、重放源和终态一致性。
3. Medium blocking 003：两 Web 表单、CLI、SDK 选择 SYN_U / SYN_CORE4 / SYN_TAIL4，冻结 P1 历史成员/可用时间/snapshot 身份，实际作用到 P3 成员及 P5 逐事件 in_universe，未知 ID 拒绝。真实浏览器 TAIL4 为 A003–A006、CORE4 为 A001–A004，全链 CORE4 原始现金98.1、权益998.1、首成交9股；请核 raw.json、请求、P1 历史成员及 P5 侧车，不能只看下拉框。

## 新增开发发现与失败历史（不得省略）

只读 SQLite 历史连接已显式 closing，成功/异常两个真实 Connection 回归保留。

C3（418c17fad8fefe50dedc866f95c14ccf0fa433ca）Windows1557/1558：完成边界 os._exit(73) 返回 0xC0000005；C4（d432c6d23a88fc7a288812760793c17ede602951）Windows1559/1560：剩余 P4_PARTIAL 的 os._exit(74) 同样失败。原失败官方 ZIP、JUnit/日志/收据保留；未取得原生栈，不得把具体异常指令或 DLL 退出原因写成已查明。C5 统一全部六个主动终止控制：faulthandler、fsync 边界/PID/Task/方法/退出码记录；Windows self-TerminateProcess，Unix os._exit。73/74/75 精确退出码、恢复后同一子运行、无重复试验、原始源文件不变等断言全部保留，任何意外原生崩溃仍失败。请独立评价测试控制和必要实测，不能据此宣告真实隔离通过。

C5（e20f8edc49cba1af883ed72436d68492a368dc3a）本地完整 SDK 1559通过/1失败：原十进程并发初始化在 BEGIN 之前 PRAGMA journal_mode=WAL 抛原生 database is locked。这是实际代码缺陷，不能归为仅 CI 波动。C5 Windows 首 attempt 在旧宿主复现校验前失败，原登记 platform_machine 为空；未保留当时计算侧精确差异，原因未证明。一次实际接受的重跑后来远端成功，但不能抵消本地 SDK 失败，更不能当 C6 证明。历史包含首次失败136825457字节/SHA256 8974dc8c0ec85052fdc6118fd7c2052c951ae92349f1e424d5ba79f3896b9a7a、各 attempt API/原始日志/ZIP及重跑请求结果。被拒绝的提前请求与实际接受的201请求分别保留，不伪称两次实际重跑。

本版 C6：0.6.0.dev5，83模块，bundle 28c3cc049efcce8fc3e55b4056e8e116f98deca39eeb1d2c8822799c8e98855b。仅在 BEGIN 前 WAL 准入对主错误码 SQLITE_BUSY/SQLITE_LOCKED 做单调时钟30秒上限重试，要求实返 wal；保留 synchronous=FULL，剩余预算给 native busy_timeout/BEGIN；事务体及 commit 不重放，原回滚/close 保留。7项确定性测试含真实持锁释放、预算耗尽、非 Busy 错误、非 WAL 模式和事务体 Busy 仅执行一次；原十进程断言不减，并在断言前排空所有子进程日志。额外12根×10真实进程=120全部退出0，且每根恰好一 workspace/Task。该压力验证在提交前 editable/dirty 预检运行，bundle 与 C6 一致，不能称为固定 C6 干净安装执行；身份见 execution-metadata/WAL_STRESS.json，原始进程日志/数据库另封存在 preflight-stress-raw/。固定 C6 的实际 SDK 另行覆盖原十进程及7项控制。

旧版负控制的首轮同步等待超时是 INVALID CONTROL，原日志及 OLD_NEGATIVE_FIRST_DISPOSITION.json 保留。修正控制只在测试连接将 native timeout 置0，真实 rollback-journal 读锁造成原生 SQLITE_BUSY；旧版实际抛 OperationalError，新版同控制通过。这不是逐字重放原默认30秒竞态；原 C5 SDK 另有默认30秒在0.748秒报错的证据。修正包装器一度把 stdout 中展示的源码断言文字误判为异常类型，包装器失败原样保留，OLD_NEGATIVE_VERIFIED.json 只读核对实际 E 行确为原生锁错；不得把包装器退出1改写0。请独立审阅这些限定及 WAL 准入状态机。

## 当前固定版本实际证据

本机干净安装 SDK、Windows、Ubuntu 各1567通过，0失败/错误/跳过；适用覆盖、所有旧阶段回归、参考答案、原66发布文件、老 wheel/锁/三旧 Ref 实际执行、P6 SDK/CLI/AppTest 烟测及扫描控制通过。本机保留两条 runpy RuntimeWarning，分别来自同进程测试已导入模块再执行 aqrp.ui.launch / aqrp.services.task_cli，原始 warnings summary 未删除；不宣称零警告。Python3.13.16 新 venv；wheel/distribution/RECORD、core锁和依赖、29个 G1 批准 UI 原 wheel/锁、命令/原始输出/UTC/退出码/环境均保留，未升级锁。以上为开发自测，请你独立复核。

官方 CI：https://github.com/wwooyy429/Alpha-Quant-Research-Platform-AQRP-/actions/runs/40079197702
两份官方原 ZIP 未重打包，run/attempt/job/head/size/digest/CRC、声明文件及上传 current 副本完整子树字节核对见 DOWNLOAD_RECEIPT、UPLOAD_ALIAS_AUDIT 和 verification。副本字节相同不等于原 symlink/ACL 身份。平台 machine 元数据必须非空。
- phase6-windows-latest-1：198336918 字节，SHA256 `1a286a16bf55d9b76dc018efc793aa1f77838a26bf109dfb441638b5078572b8`。
- phase6-ubuntu-24.04-1：239459656 字节，SHA256 `e8392f5dd2adb7953fd6e0e51cd2e28effc4da61a14feca8759ece504408242f`。

sdk/LOCAL_CLEAN_SDK-3017a09.zip 是开发方封存的 SDK 最终声明文件，明确不是官方 ZIP。execution-metadata/SOURCE-3017a09.git.zip 是固定 Git 归档，88435541字节，SHA256 416501153449e423005274870e2ce3397d1108ce292319a381eb123450d6c4d9；5108 个 Git 文件逐一等于实际本机 SDK/source，且归档哈希与环境记录一致。官方原 ZIP 按既定上传选择不含 source，不能声称它自带这份源码。5016受保护文件与原正确金融答案不改。

browser/为真实 CUA 浏览器证据，与 AppTest 区分：六页；Momentum/Reversal 实际研究与完整流水线，逐字段等于 SDK、旧CLI、任务CLI、AppTest 的研究和精确金融结果。新 E/P4 重放目录；源42文件不改；真实浏览器下载字节等于源清单。双会话配置历史[3,2,4,3]：旧 base0 的4被拒且保留编辑，显式 reload 后才保存；12个原请求字节不改。controls 的预登记、TAIL4/CORE4真实成员、未登记参数无副作用拒绝、风险 TaskFAILED 原P4/P5保留及 Web Cancel 证据完整。SDK仅准备排队取消任务，实际 CUA 点击 Cancel。控制工作区不补充主工作区预算、不表示统计独立。AX/JPEG/动作、原始血缘/账本、服务停止回执和环境保留。

请同时核对全部八项需求、全任务完成屏障、可信 TaskContext/嵌套P4所有权及目录时点、至少一个决策与旧零决策API兼容、4096数字位/4098字符十进制限制，并补新反例。输出每项 OPEN/CLOSED/NOT VERIFIED、实际命令/环境/日志/哈希、验证等级及独立G2结论。开发方不得自行关闭发现。

Windows WI-R2-001/002持续 DEFERRED / NOT VERIFIED，整体真实 Windows 隔离 NOT VERIFIED；正式 Test 未运行、金融批准 NONE、完整历史宿主限制保留。不合并、打标签、部署、实盘、运行正式 Test、授金融批准或进入 P7。G2通过不等于用户阶段验收。

封存收据：C:\Users\11638\AppData\Local\AQRP\reviews\p6-g2-3017a09-developer-20261024T092710Z\SEAL.json
外层ZIP SHA256：c2b0ad0b7403734ad178dfcb2f4c588c2ef18097dad10f9428af5514acfefcb8
