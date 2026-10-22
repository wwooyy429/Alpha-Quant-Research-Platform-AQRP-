# Windows 隔离 R3 两项修复：固定版本独立复核

审查者：GPT Work / 本会话 Codex 补充审核执行；日期：2026-10-22。

**固定 SHA：`62074502aa4c32556b5e690bac10bd8054bd9178`。修复候选结论：PASS（代码、模型及工程证据范围）。整体 Windows 真实隔离：NOT VERIFIED。**

`WORK-WI-R3-001`、`WORK-WI-R3-002` 两项 Medium 代码/工具发现均 **CLOSED — FIX VERIFIED**，本轮未发现新增阻断。原 `WI-R2-001`、`WI-R2-002` 仍未完全关闭，继续等待真实主体及完整生命周期证据。这不是实际三主体权限验收、正式 Test、金融批准或 VALID-004 全项通过；也不是 P4 的集成隔离验收。

## 1. 固定对象与范围

实际读取 PR #7 描述中的 AQRP_FIXED_REVIEW_SHA，记录完整 40 位值，独立 clone、fetch 并 detached checkout。本轮开始和收尾的锁定 SHA/head 均一致，PR 仍 open、未合并。起始主连接器读取成功；收尾通过 GitHub 公开 API 核对。

原阻断版本：`b3d9aef79396db948d326f5ce247131f96739d9d`。本次源码树：`15555f2d4d9ea2c12e3c9519564a8da4843c20c4`。CI 实际执行临时集成提交 `08a1dd1733c7a00676b59e377ccd15a33330d527`；已从 Git 对象独立核其父为 P3 基线 `0a57dccb5618ba08cd3572d6d6b78fec963a3041` 和本固定 SHA，整树相同，未将临时 CI 引用称为 main 合并。

版本 `0.3.1.dev3`，47 个 Python 模块；默认因子身份 `1.1.3` 区分新 bundle。bundle SHA256：`bff586a45b200ab047947bc461cafbc912a975b9f7dd09bf10ac47d594aca967`。依赖锁仍为 `86c7bf65c9a9690036006360062c8cd10a91279705b4070af7033d7699abffeb`，没有新增依赖。

独立逐文件核对本轮 IDENTITY 中 2,990 项保留文件和全部 bundle 模块；P1 snapshot.py、依赖锁、106 项目录与 P3 main 原字节一致。P1 私有临时目录/rename 和 P3 因子经济公式未修改。Fixed-Source.zip 的 3,110 个源文件成员与固定 checkout 逐字节一致。无 P4 portfolio/risk 模块，本轮不能宣称已覆盖 P4 组合产物。

## 2. 发现关闭依据

### WORK-WI-R3-001 · Medium → CLOSED — FIX VERIFIED

位置：`src/aqrp/validation/windows_acl.py:24`、`:36`、`:64`、`:190`、`:211`。

原问题：前后 os.walk 都可能吞掉枚举错误，因此相同的不完整集合仍可能被认证为完整树。

当前 enumerate_tree 使用严格 scandir 及 entry.stat(follow_symlinks=False)，目录打开、迭代、条目元数据错误立即转为结构化 ContractError。保留 phase/path/errno/winerror/错误类型/信息及原异常 cause；前后独立完整采集，仍执行对象身份/类型、link/reparse、硬链接、集合和 ACL 再捕获检查。未删掉原 closed ACL、继承链或可信祖先证明。

主审独立实现模型描述符适配器，未导入仓库测试 helper；实际普通目录/文件由主审创建，采集仍使用真实 scandir/stat。正常五对象树通过。分别在 before/after 对目录打开 PermissionError、FileNotFoundError、I/O 错误、迭代 I/O 错误和 DirEntry.stat 错误注入，再分别对身份捕获的 lstat 注错，共 **12 项拒绝控制通过**。均检查错误代码、阶段和路径，枚举错误同时核原 cause。新实现不会把持续缺失同一子树当成完整成功。

执行等级：真实文件系统采集＋显式模型 ACL；注错不是实际 NTFS 越权。主审 SDK 及原始双系统测试另覆盖条目分类、成员/身份/link/ACL 变化等回归。关闭的是代码漏检发现，不将其扩大为原 WI-R2 动态继承实际验证已经通过。

证据：`INDEPENDENT_RECHECK_RESULTS.json.strict_collection_controls`、`independent_recheck.py`、`independent-controls.*`。

### WORK-WI-R3-002 · Medium → CLOSED — FIX VERIFIED

位置：`tools/windows_access_probe.py:99`、`:216`、`:342`、`:360`、`:370`、`:389`、`:477`。

原问题：传入清单缺失仍存在的动态产物，三角色仍可能 all_pass；目录按文件 read_bytes，缺少 DELETE_CHILD=0x40，不能证明完整覆盖。

当前流程为可信 operator freeze 权威原字节清单 → 三角色 probe → operator reconcile 自行重新采集。清单绑定 attempt/phase/root/四主体/policy、真实九输入、sidecar、key、动态文件和全部目录，以及完整 gate、对象身份/类型、目录成员和文件 bytes/hash。probe 配置机械生成并与原清单 SHA/集合严格对账。

目录逐项请求 LIST_DIRECTORY、ADD_FILE、ADD_SUBDIRECTORY、WRITE_DAC、WRITE_OWNER、DELETE、DELETE_CHILD；文件才读取字节。按当前 closed MODIFY 定义，三角色 DELETE_CHILD 都应拒绝。key 仅 evaluator 可读不可写，auditor/research 拒绝。research 只消费可信清单，无须枚举私域。

单角色只能报告 listed_checks_pass，其 coverage_verified/all_pass 仍 false。reconcile 必须自己执行 freeze，不接受传入旧 current 清单顶替；逐检查重核角色/SID/阶段/根/策略、mask、允许或 native 错误5、实际字节和目录成员，不能仅相信 pass 标志。before/after 原字节 SHA 链、动态新增/删除及输入/sidecar/key 不变条件均在本次代码范围。

主审独立构建合法新协议正例：从已独立散列的公开九文件调用工程复制发布；只在模型边界替换 ACL 描述符与 token/access，普通文件的复制/读取/成员操作实际执行。before 和 after 两阶段均有完整三角色模型结果，phase reconcile 通过；after 实际新增目录/文件、删除一个动态文件，独立核新增/删除列表和 predecessor SHA。

每阶段、每角色删去一个仍存在的动态文件或目录并保持原权威 hash，均拒绝。另核缺/重复角色、缺/多检查、错 mask、错误码2冒充拒绝、错 attempt/SID、提权、错内容 hash/目录成员、采集后新增文件、内容漂移、错清单 hash、重新采集遇权限错误以及 after 缺前序/跨 attempt，共 **44 项负向控制通过**。额外模拟实际目录列举失败，确认局部结果失败。完整访问矩阵由主审独立定义，未调用生产 operations 生成期望。

因此新协议完整正例可以通过，原删项路径及目录缺口已修复；并非仅拒绝旧缺字段协议。结果仍明确 MODEL_ADAPTER、real_token_claims=false、overall_windows_isolation=NOT_VERIFIED。JSON 中的身份声明不是密码学认证，真实运行须再核原进程身份和日志；该限制已在协议中明确，不能以这些模型结果关闭原实际隔离发现。

证据：`INDEPENDENT_RECHECK_RESULTS.json`、`independent-before/after-*.json`、`independent-directory-list-failure.json`、`independent-model/`；后续执行契约见固定仓库 OPERATOR_COVERAGE_PROTOCOL.md，本轮未执行其中的真实角色命令。

## 3. 实际执行与原始证据

| 验证 | 实际结果与等级 |
|---|---|
| 主审新建干净 SDK | **681 passed，0 failure/error/skip**；完整安装/静态/格式/覆盖、原环境包/旧 Ref 重放、数据/因子/研究 smoke、数学参考和扫描控制成功 |
| 安装环境 | Windows 11 build26300，CPython3.13.16 标准 GIL、AMD64；使用主审独立 Python，新 venv、hash 锁依赖及真实安装 wheel |
| 两项主审修复控制 | 12 次采集拒绝、2 个完整 phase 正例、44 个负向控制及目录列举失败控制通过；全部 ACL/token/access 明确模型 |
| 官方 run39796378880 | Windows/Ubuntu 各681；API job/run 成功，原 ZIP 内 JUnit 无失败/跳过，complete=true |
| 源码身份 | 本机和双 CI wheel 各47模块及 reviewed_code.json 与固定 checkout 逐字节一致 |
| 原 ZIP/SDK 内容 | Windows211、Ubuntu210、本机211选择项全部 hash；精确成员、CRC、数据 manifest/八表、终态链及因子工件核验 |
| SDK/CI 模型原证据 | 对三个环境 before/after 权威清单、closed ACL、三角色全部 mask/错误码/实际成员和内容记录、结果 digest 与 phase receipt独立重算；仍是 MODEL_ADAPTER |
| 新九文件 | 16011 bytes，SHA256 `f6c91a84821aac94d840295230eecb088e936c80f5e8a37ce36979b02e1e1783`；实际 Parquet/表内 ID/摘要核验并在新安装 wheel 重跑四因子 |
| 四因子独立答案 | momentum=21/100、reversal=−21/100、volume=3/5、price_volume=3/50，绝对容差1e−12；期望仅由原数据及 Fraction 公式得出 |
| 开发证据包 | 395473620 bytes，276清单项，精确成员/CRC/全部 hash 通过；源 ZIP3110成员逐字节匹配 |
| 旧独立原包 | SHA256仍为 `2c8ec67ac22dbcc722e73d49461b926ea51bda93e7bc23ae7fe42209fc9dc6e2`，原位不改 |
| 当前账户 | 独立只读 Get-LocalUser：aqrp_research/evaluator/auditor 均 Enabled=false；未启用或改 ACL |

计数有重叠：681 包含原628及新增53，专项103不能再与681相加。Ubuntu 由 GitHub runner 执行；主审本机会话只在 Windows 验证其原证据，没有声称另跑 Linux 原生权限隔离。

本机关键覆盖：windows_acl.py line96.18% / branch91.89%；engineering_input.py line97.01% / branch91.67%，满足既定95%/90%门槛。probe 工具不属于47模块 wheel 覆盖对象，其行为另由专项测试及主审流程控制验证。

本机 wheel SHA256：`3dc49c186357b0eb4ced933a2330ea5ddc5cbe6e86f107da7f099512b1835336`。

Windows 原 ZIP：95627613 bytes；SHA256 `1f8f3b3eaea8bf66abb4cfbc40849262435079790c54b5d92f3834114dcb94d9`。

Ubuntu 原 ZIP：136899984 bytes；SHA256 `1fff6d92b311b92e35fef3a579a4cd3b49040e628d12d4f6d7ba8bd0e5b7d880`。

开发证据包 SHA256：`75f2ac1aa0469a4b8ce95b7db615579e5a7217965fbee7120ca0f827a6294f66`。

**工件来源限制：** 初次 PR/run 连接器读取成功；随后工件列表和 jobs 连接器出现传输错误。改用 GitHub 公开 API 取得官方 artifact ID/大小/digest、run/head/job，封存原响应。两份 ZIP 从开发方封存包取出，逐字节重算后与独立取得的官方 digest/大小一致，再核全部内部证据。本轮没有完成“通过连接器重新下载 ZIP”，未作此声明。详见 OFFICIAL_ARTIFACT_PROVENANCE.json；这不影响对已验证同摘要原字节的内容复核。

核心实际命令为独立 checkout 下 `python -I tools/ci.py`，AQRP_RUN_ROOT 使用新的短工程目录；其后的独立控制与四因子重跑均使用该 SDK 安装解释器。每次 argv/cwd/UTC起止/退出码及 stdout/stderr 见 `*.command.json` 和 `REVIEW_EXECUTION.json`。源码保持干净，未改开发 checkout。

开发方中间679/最终681及分类失败历史、before2失败和旧报告保持原样，没有用本次成功改判历史。审查辅助首次账户查询存在输出表达式转义问题，仅 SID 显示 null；纠正为直接读取 SID 对象后确认 SID.Value，两个原始查询日志均保留。Enabled 状态一直为false，没有账户变更。

## 4. 原 R2 仍缺条件、P4 与授权边界

| 原事项 | 仍需的实际证据 |
|---|---|
| WI-R2-001 | 新固定集成版本的真实 ACL/祖先/继承链，真实非提权三主体 before/after，单次/并发、崩溃恢复、重复拒绝及完整动态产物；模型不替代原生访问 |
| WI-R2-002 | 可信 operator 对实际部署输入执行预建/复制发布，真实 auditor 读取实际九文件与 sidecar，完整权威清单和三结果 fresh reconcile；新公开九文件不是原旧不可读输入恢复 |
| 跨阶段覆盖 | 本分支只有 P3 隔离代码。若最终合并到 P4 或更后版本集中验证，必须锁定新的集成 SHA，纳入新增组合/风险/建议等产物及目录，不能自动把本次代码结论登记为 P4 隔离通过 |

整体 Windows 隔离、正式 Test、金融批准及完整历史宿主复现继续 NOT VERIFIED/DEFERRED；原 R2 184=183PASS/1FAIL 与旧九文件不可读等历史事实不变。正式 Test/金融门禁未解除，VALID-004 不全项标完成。Windows 本机代码复核也不代表其他 OS 权限隔离通过。

遵照本轮范围，未启用账户、修改真实 ACL/服务/调度、重跑管理员脚本、执行真实角色 probe、部署、正式 Test、金融批准、合并、打标签、实盘或进入 P5。此前对 PR #6 的发布授权没有被扩大为 PR #7 的合并授权。

本次可登记两项 R3 代码/工具修复已关闭，实际隔离验证可按用户安排保留到最终集成版本集中执行。

## 5. 封存

EVIDENCE.zip 包含报告/发现关闭记录、固定源码子集、独立脚本及原脚本适配收据、12/44控制与 before/after模型原工件、四因子/九输入、实际命令和原日志、官方 API 响应及绑定官方摘要的两份原始 ZIP、主审 SDK 全部 upload-selection 成员。EVIDENCE_MANIFEST.json 逐成员 SHA256；RECEIPT.json 记录总包大小/hash/CRC及逐成员复核。

明确省略 venv/cache/pytest临时目录和展开源码副本；开发方395MB原包和上一轮330MB独立原包保留外部原件，以独立重算摘要绑定，不重复塞入本包。封存收据是内容一致性记录，不是身份签名、完整宿主镜像或金融批准。
