# Windows 三主体隔离 R2 实际执行复核

审查人：GPT Work 独立复核；管理员执行人：用户。日期：2026-10-22。业务固定 SHA：`9ac5db069287a6e4a095e25ae8c3cc8fa229cded`。本次不是 Phase4 代码审核。

**结论：部分工程验证通过；完整 Windows 隔离配置仍为 NOT VERIFIED / BLOCKED，不得标为正式 Test 或 VALID-004 全项通过。** 未发现本轮所测路径上的越权读写；运行后权限门禁确实失败，且实际生成输入的审计访问尚未验证。继续 fail closed 是正确结果。

## 身份、版本和执行范围

- 尝试 ID：`e6968f1c-3552-4a98-af61-98a5194dafea`；管理员实际执行 UTC 10:06:06–10:08:54（北京时间 18:06–18:08）。原始文件见 `raw-admin/`，37 个文件原字节复制。
- 实际三主体：aqrp_research / evaluator / auditor，其 SID 尾号分别 1007 / 1008 / 1009，公共前缀 `S-1-5-21-2664406737-4182919061-3647612378`。13 个子进程记录实际 Windows token；三主体均未提升，不以 role 字符串代替身份。崩溃进程原始 stderr 中也有 SID / elevated 证据。
- 受管入口 `worker-r2.py` SHA256：`da6cced2a92dc3a63832f068dab39ca23525ba2922c5c67d00f2205b2efaacb6`。驱动：`93ac3f54923289f23d90477fc9dc32dcba5918f76d71606648dd5dbf09c5f0ea`。辅助脚本：`b2ad10bcc05027fa8f10930780e2d04a1350b045d059e0b5ff504915cff8d61b`。
- 配置 SHA256：`8f4b26210938633a16115241402f1808a7e6fc9c3d4f8e8b3a20b469eec28115`。本次入口及配置另存 `reviewed-harness/`；准备包与旧失败包的原哈希引用保留。
- 实际 runtime：CPython 3.13.16 standard GIL x64，Windows 11 build 26300。review 脚本同用标准库 Python，不导入 AQRP 生成独立答案。环境与原始子进程 argv、起止时间、退出码分别见 `INDEPENDENT_VERIFICATION.json`、`raw-admin/process-results.json`。
- 两份部署运行时各 6,250 个文件在执行后逐个与旧冻结 PAYLOAD_MANIFEST 核对大小和 SHA256，通过；业务 45 个 Python 模块 bundle 均为 `3cec8a9da49a49a93010d7fa6a2012dded25185e2cdca49144cf4d719d56876e`，锁哈希 `86c7bf65c9a9690036006360062c8cd10a91279705b4070af7033d7699abffeb`。另以 Git 固定对象逐模块字节核对，见 `FIXED_GIT_SOURCE_VERIFICATION.json`。
- 本轮前 1,322 条 ACL 快照记录在动态执行后逐条完全相同；新增对象单独检查。两份 runtime 的 6,887 节点 ACL 全量导出保留，不能用这些元数据替代每个节点的实际身份访问测试。
- 管理员 finally 报告三个账户禁用；本次复核再次通过 Get-LocalUser 读取确认全部禁用，见 `current-accounts.json`。本复核未改 ACL、账户、仓库或业务文件，未接管任何不可读对象。

## 实际检查结果

| 子进程 | 检查通过/总数 | 实际退出码 | 说明 |
|---|---:|---:|---|
| research-inspect | 53/53 | 0 | 身份、公共读取、私域拒绝、不可写运行时/入口等 |
| auditor-inspect | 48/48 | 0 | 身份、canary 只读及禁止写/改 DACL/接管等 |
| evaluator-inspect | 56/56 | 0 | 初始 host 门禁、身份、工程因子与安全负控制等 |
| evaluator-abort-before | 1/1 | 0 | 保留前中断未建立访问账本 |
| evaluator-race-a | 2/2 | 0 | 单次保留及工程结果 |
| evaluator-race-b | 0/0 | 42 | 预期重复拒绝，不能算成新增通过检查 |
| evaluator-crash | 0/0 | 23 | 预期工程崩溃，stderr 原始身份记录保留 |
| evaluator-recover | 3/3 | 0 | 首次恢复 1、再次 0，预算已消耗 |
| evaluator-alias | 4/4 | 0 | family/run_id/protocol_hash/cache 变体均拒绝 |
| research-post-inspect | 6/6 | 0 | 新动态账本/race.go 的拒绝访问 |
| auditor-post-inspect | 6/6 | 0 | 所测新文件只读 |
| evaluator-post-inspect | 3/3 | 0 | 所测新文件可读 |
| evaluator-after | 1/2 | 2 | 单保留成立；运行后 host 门禁失败 |

**合计 184 个检查记录：183 PASS、1 FAIL。** exit 42 / 23 是预期负控制，不当作程序意外崩溃；exit 2 为保留诊断的实际检查失败，不能因驱动接受该退出码就算通过。inspect/after 的非空 stderr 为 PowerShell CLIXML progress，独立解析确认类别，原字节保留；工程 crash 的 JSON 也单独保留。

独立复核 `demo-race` 七条记录：RESERVED、SUCCEEDED、五条 REJECTED_REPEAT；`demo-crash` 三条：RESERVED、FAILED_CONSUMED、REJECTED_REPEAT。逐条以标准库重算规范 JSON SHA256、seq 和 previous，全部一致。`demo-abort` 没有 access.jsonl。仅能支持本次同控制域的这些别名/并发/恢复用例，不支持跨控制根、所有缓存入口和真实正式 Test 的无遗漏结论。

工程因子实际落盘各四个文件，共四个运行：每份 manifest 的成员 SHA256、logical_hash 和 content_hash 独立重算通过。以精确分数计算收盘价 100/110/121、量 100/150/200、lookback=2：momentum=21/100，reversal=-21/100，volume=3/5，price_volume=(121/110-1)×3/5=3/50。实际值 0.21/-0.21/0.6/0.06，绝对容差 1e-12 内通过。全部 TEST_ONLY / financial_approval=NONE。该四例不是全量 QA-004 或 SDK 578 回归的新执行。

## 发现及处置

### WI-R2-001 — 中：动态文件 ACL 与 Windows 门禁不兼容，OPEN

位置：固定版本 `src/aqrp/validation/evaluator.py:61`、`:154`、`:163`；写入路径 `experiments/ledger.py:23/76/93`；原始证据 `raw-admin/evaluator-after.stdout.log`、`ACL_INCOMPATIBILITIES.json`。

运行前 OperatorPolicy.verify_host 通过；运行后返回 UNVERIFIED_ISOLATION。全量 sealed 快照中有 42 个新对象 AreAccessRulesProtected=false。账本/锁等采用默认创建方式，继承受保护父目录的权限；而固定门禁要求每个对象自身都禁止继承。对默认继承的控制目录/文件逐个按源码谓词回放，足以导致拒绝。另一个 OW 问题见下项，不能声称已单步捕获门禁遍历时第一个具体失败文件。

已测动态文件实际三角色边界仍符合预期，未证实数据泄漏；但配置无法完成“先运行、再门禁复核”的完整循环，阻断完整 Windows profile 通过和部署。此问题为已延期隔离能力的实际 Windows 集成缺口，不把受限 P3 发布自动改判失败。

处置：开发方提出并固定设计/代码候选供复审。可保留逐对象受保护策略，在安全创建/发布流程中落实所需 ACL；或单独审查一个能验证有效权限及可信祖先链的继承策略。不能直接删除 protected 判断，也不能先执行后临时补 ACL 再把原失败改成 PASS。涉及真实部署的批准仍归用户，当前无部署授权。

### WI-R2-002 — 中：实际生成快照的审计读取及证据覆盖不足，OPEN

位置：固定 `src/aqrp/data/snapshot.py:80`、`:127`；标准库 `Lib/tempfile.py`；`worker-r2.py` 工程 factor-run 创建路径；固定 TEST_ISOLATION_PROFILE 的三主体输入权限约定。原始证据 `OMISSIONS.json`、`ACL_INCOMPATIBILITIES.json`。

工程 evaluator 在封闭运行中实际生成 P1 快照 `cb10857f-e12b-4c82-8962-16a41fdf8377`。根目录 DACL 为 `(A;OICI;FA;;;OW)(A;OICI;FA;;;SY)(A;OICI;FA;;;BA)`，owner=evaluator；子文件继承该权限，未列 auditor。10 条 ACL 记录含根及九个文件。OW 是 owner rights SID，不能误称 research 越权；但它也不在本固定门禁的允许 SID 集合中。

P1 使用 tempfile.mkdtemp 后 rename。Python 3.13 对 Windows mkdir(mode=0o700)设置创建者/管理员专属权限，mkdtemp 也采用私有临时目录语义；因此不能假设其输出会自然继承外层三主体只读配置。参见 [Python os.mkdir 文档](https://docs.python.org/3.13/library/os.html#os.mkdir)及 [tempfile.mkdtemp 文档](https://docs.python.org/3.13/library/tempfile.html#tempfile.mkdtemp)。这是标准库安全默认值与本次多主体存储流程组合的问题，不是要求把 P1 临时目录改为宽权限。

已通过的 auditor snapshot-canary 探针没有触达这份真实新快照，故 actual auditor access = NOT VERIFIED。当前 reviewer 1001 非提升进程实测枚举根目录被拒绝（errno13 / winerror5），九个原始文件未复制、未重新散列。管理员 ACL 导出已完整保留，但不能代替输入内容。actor 报告 snapshot_manifest_hash=`bd7ebd46326c6358b76c9bb1c5d25cfd2273de4bf58417aba952270d23d41c67`，本次未独立重算，明确列为证据限制。

处置：可信 operator 在 evaluator 启动前建立工程输入、设置经过审查的角色只读权限，再以真实三主体验证所有实际输入/输出/侧车路径；或评审完整安全发布适配层。不要给 Users/Everyone 权限，不扩大用户既有授权；未解决前不能用 canary 覆盖声明替代实际文件覆盖。此轮不要求用户为同一脚本再跑一次。

## 未验证与权限界限

本次真实验证了 Windows 三个标准账户的代表性访问控制及固定工程执行，证明范围比同 OS 用户的模拟 role 测试更强；仍未完成整个受管域在动态生命周期后的门禁闭环。完整 Windows 隔离为 NOT VERIFIED，真实正式 Test 未执行/未授权，金融批准为 NONE，完整历史宿主复现 NOT VERIFIED；Linux 同等三主体隔离、系统管理员威胁模型、任意恶意代码沙箱、所有路径/重解析竞态、跨控制根预算均未在本次验证。

不把 Formal ResearchValidated、VALID-004 全项、正式 OOS、金融标准验收、完整历史宿主复现标完成。原失败执行身份及日志保留；本次执行者归属为用户管理员运行 + GPT Work 独立复核，不改写为 Gemini。

不合并、不打标签、不部署、不进入 P5；P3 受限工程验收和已完成的 P4 G1 计划结论保持其原有范围。本次未启动 P4 实现。

## 可复核记录和封存

管理员原始 argv/环境/日志在 raw-admin；复核脚本 `verify_results.py`、`verify_fixed_git.py` 和 stdout/stderr 均保存，可在同目录用记录的 Python 执行，只写本复核目录。`FIXED_GIT_SOURCE_VERIFICATION.json`保存实际只读 Git 命令。辅助核验：Get-LocalUser（读取三个指定账户）、whoami /user（读取当前身份），无账户或 ACL 变更命令。

复核脚本初次因账户字段大小写假设停止，第二次因误将执行前 ACL 条目数预期为 1313 而停止；改为实际 1322 后全部独立核验通过。失败脚本和 stderr 均保留为 attempt1 / attempt2。这些仅是复核统计断言问题，不修改管理员原始执行、业务代码或其 1 个失败结果。

`COPIED_FILES.json`逐文件记录来源/大小/SHA256；raw-admin 37 文件及可读工程产物 24 文件已复制。不可读快照九文件以 OMISSIONS 列明，故本包是完整原始执行导出及可读工程证据封存，不声称完整输入快照封存。EVIDENCE_MANIFEST/ZIP/RECEIPT 将验证包内全部成员，不把证据哈希等同于第三方签名或完备性证明。旧准备包、旧失败包、旧 DEPLOYMENT_STATE 和旧入口均未覆盖。

封存器首次因 Windows 默认文本编码读取 UTF-8 核验 JSON 而停止；显式 UTF-8 后完成封存。原首次脚本及 stderr 以 seal-attempt1 保留，未生成伪成功收据。最终收据以全成员重新读取校验为准。
