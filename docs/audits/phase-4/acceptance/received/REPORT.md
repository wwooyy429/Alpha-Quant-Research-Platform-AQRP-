# Phase4 G2 独立修复复核

审查者：GPT Work / 本会话 Codex 补充审核执行。日期：2026-10-22。

**固定审查 SHA：`3c8757949b0fd5c97953b06a74ebc2d0e56676e4`。结论：G2 PASS — 七项受限工程范围。**

原 `WORK-P4-G2-001`（High）和 `WORK-P4-G2-002`（Medium）均 **CLOSED — FIX VERIFIED**。本轮未发现新增阻断。该结论可提交用户进行 Phase4 工程验收，尚不构成用户验收、金融批准或合并/发布授权。Windows 隔离 PR #7 不在本次修复内，其独立结论不变。

## 固定身份与范围

实际读取 PR #6 描述的 AQRP_FIXED_REVIEW_SHA，记录完整 40 位值，创建独立 checkout 并 detached checkout 该提交；开始及收尾的 PR 描述/head 均一致，状态 open、merged=false。没有审查漂移 HEAD。源码树 `1a087395191c251992446d7fe7a87f6cac24009b`。

CI 实际运行临时 PR 集成提交 `354c931ef05d8d16237efac5826ae47302175f4f`，独立核对其父提交为 P3 main `0a57dccb5618ba08cd3572d6d6b78fec963a3041` 与本固定 SHA，整树相同。临时 CI 集成引用不表示已合并 main。

实际核对 canonical 106 项目录，P4 七项 = 4 MVP / 3 Competition Ready；3,440 项保留文件、七个冻结输入、G1 答案与原 P3 发布工件哈希均一致。P3 原有 43 个业务模块字节不改，另两模块仅包版本/默认因子身份变化。P4 修复限定四个组合/风险模块及对应测试、版本准入元数据和工具/审计资料，没有 P5 业务模块。

版本 `0.4.1.dev1`；53 模块全 bundle `0ccd7642b3c69d06c552bc328195387f0a9ec8a06a45398df0076bde8f81cdf7`；默认内置因子身份 `1.2.1`，公式不变。依赖锁 `86c7bf65c9a9690036006360062c8cd10a91279705b4070af7033d7699abffeb` 与 P3 基线逐字节相同，无新增依赖。

| 需求 | 本轮核对的实现及证据 | 结论 |
|---|---|---|
| PORT-001 MVP | contracts/construct/service/research_input，共同服务、真实 P3 来源、原字节请求/结果/失败证据、不可执行建议 | 受限工程实现通过 |
| PORT-002 MVP | weights，单/多因子、固定有符号系数、等权/分数权、LongOnly、交集/并列/现金 | 174 组独立服务参考及完整测试通过 |
| PORT-003 CR | 真实 LongShort 双腿、gross/net、中心化、空腿/重叠和资金限制 | 独立有理数参考及大数双腿通过 |
| RISK-001 MVP | 逐票、gross/net/leverage、全额/半额换手，取整前后完整检查 | 六冻结输入、174 参考和数值边界通过 |
| RISK-002 CR | PIT 暴露、signed Beta、行业净/总敞口、缺失/未来/错父拒绝 | 原 x03/相关控制及父工件复核通过 |
| RISK-003 CR | 目标和 delta 双 lot、可交易/可售/借券、原仓/全平例外 | x01/odd_hold/short_close、独立负向和数值测试通过 |
| RISK-004 MVP | candidate 重构、风险拒绝无 target、实际发布审计、失败终态及完整性重放 | 原故障与新增字节控制通过 |

G1 设计通过状态保持。此次 G2 结论是实现/工程证据复核，未将正式市场、真实订单或延期能力补写为已实现。

## 原发现的关闭依据

### WORK-P4-G2-001 · High → CLOSED — FIX VERIFIED

位置：`src/aqrp/portfolio/contracts.py:82`、`:103`、`:114`；`src/aqrp/risk/checks.py:192`；`src/aqrp/portfolio/service.py:96`、`:108`、`:141`。

原因：旧实现精确验证后统一 Decimal34 投影，合法 E=10^35、price=1、lot=3 输入的 q=10^35−1 被舍入为 10^35，破坏整手与资金恒等式却成功发布。

修复使用整数分母分解无损输出有限小数；只有非终止展示值固定 Decimal34 HALF_EVEN。输入域仍为原 34 位有效系数和指数边界，不把更长输出重新误当合法输入。成功前从真实序列化字节重建数量/delta/资金、pre/post 风险、上下文、hash 和建议；落盘后再读 result.json，审计原字节 SHA；返回值去掉附加 manifest 后逐字节对应落盘结果。

主审独立执行 25 组完整服务数值案例，期望值由自有 Fraction 参考给出，未调用生产计算生成期望。包括 E=10^0/3/33/34/35/40/67/99/100、分数价格和 lot、极大/极小价格/资金、非终止权重、两种双腿权重、正负旧仓及低 Decimal context。逐一检查 candidate.json、risk.json、result.json、实际返回字节、建议、资金恒等式和审计 hash。

关键结果：E=10^35 和 10^40、price=1、lot=3 均精确 q=E−1、cash=1；E=10^35、price=.01、lot=.03 为 q=10^37−.01、cash=.0001；E=10^100、price=10^-100、lot=7 为 q=10^200−2、cash=2×10^-100。大数双腿空头资金/受限现金/保证金保持小额余额。

另执行三项服务级故障注入：发布前序列化现金错误被拒绝且无 target；落盘现金损坏保留错误原字节与 publication-failure，终态 FAILED，禁止成功重放；仅最终返回线缆字节变化抛出 PUBLISHED_RETURN_BYTES_CHANGED，不返回错误值。最后一种情形的磁盘原结果正确且终态 SUCCEEDED，符合有效原工件仍可重放的语义，不能误称磁盘发布失败。

原始结果见 `REPAIR_RECHECK_RESULTS.json`、`repair-runs/`、`publication-controls/`。修复处置：关闭原发现；继续保持所有工程输出 executable=false、financial_approval=NONE。

### WORK-P4-G2-002 · Medium → CLOSED — FIX VERIFIED

位置：`src/aqrp/portfolio/research_input.py:19`、`:41`、`:111`、`:174`。

原因：旧检查仅核 data hash。P1 manifest 的逻辑摘要明确排除 snapshot_id，故一致改写请求和全部 envelope 的合法 UUID 仍被接受。

新校验以原 P3 成功终态 manifest 中的 engine.json 原字节为锚，交叉检查原 config UTF-8/SHA、嵌套配置、内容 hash、信号 ID 和唯一父 ID/hash，再校验实际 SnapshotRef、manifest 原字节 SHA、八个真实表及表内 snapshot_id。默认只在既有 SDK 布局定位；自定义存储必须显式给 source_snapshot，缺失拒绝。

主审未使用新增测试 helper 构造父身份：从上一轮独立正控制的原请求恢复投影，读取原 P3 run `0c902a7a-6e21-4003-9e18-365bf8bc3b68`，独立复算 engine 配置/信号摘要、终态成员 hash、manifest 逻辑摘要、八表原字节及其内部 ID。真实父为 `9e3a5971-d66e-4aee-bdb4-1082c6907e02`。

共 13 项控制：默认真实九文件、显式迁移真实九文件通过；仅改所有上下文 ID、连新 binding ID 一起改、跨 data hash、伪造 manifest 原字节 hash、缺 snapshot/raw hash、缺路径、物理 manifest ID 改写、表字节改写、表内 ID 改写并重算描述、缺表等均拒绝。原 P3 工件和九文件前后哈希完全一致；试验仅改新建副本。

新增字段不足的旧草稿请求重新执行明确 REJECTED。另将六个旧 P4 结果用新版本执行完整性重放，原字节/历史状态保持，financial_approval=NONE；包括历史缺陷的 SUCCEEDED 结果也只证明原件完整，绝不重新判定其金融正确。旧反例及其原失败报告没有被覆盖或洗白。

原始结果见 `REPAIR_RECHECK_RESULTS.json`、`OLD_REPLAY_VERIFICATION.json`、`parent-original/`、`parent-copies/`。修复处置：关闭原发现。

## 实际执行与证据可信度

本机实际环境：Windows 11 build 26300、CPython 3.13.16 标准 GIL、AMD64；主审独立解释器位于 `C:/Users/11638/AppData/Local/AQRP/runtime/Python31316/python.exe`。新建干净 venv，实际运行安装后的 wheel，没有把源码导入冒充 wheel 测试。

| 执行/核验 | 结果 |
|---|---|
| 主审干净 SDK（含安装、静态、覆盖、旧 Ref、服务 smoke、扫描） | 完整成功；844 tests，0 failure/error/skip |
| 独立完整服务参考 | 174/174 一致，23 个 PIT/候选篡改负向控制通过 |
| 本轮独立修复控制 | 25 数值、13 父工件、3 发布控制通过 |
| 原脚本原字节重执行 | 主审原四、旧 16＋4、91 数学、3 扫描控制通过 |
| 官方 Windows / Ubuntu run39778988451 | 各 844；实际下载两个原始 ZIP，核 CRC/精确成员/全部选择清单 hash/JUnit/覆盖/wheel/工件 |
| wheel 源码绑定 | 本机/两个 CI 各 53 Python 模块及准入收据与固定 checkout 逐字节一致 |
| 六个 SDK 组合场景 | 对真实返回/持久化风险与结果再次独立复算，成功工件 audit hash 对应实际 result.json |
| 开发方证据包 | 401144916 bytes；1796 清单项，CRC/全部成员 hash/精确源 ZIP 均核验 |

上述计数有覆盖/重复，不相加为独立测试总数。Ubuntu 测试由 GitHub runner 执行，本审核员在 Windows 独立核验其原工件；没有声称本机会话执行了 Linux。

P4 非空业务模块覆盖满足 line≥95%、branch≥90%；空 __init__ 模块无可执行语句，不以空文件 0% 报误判未过门槛。完整各模块结果在 RAW_EVIDENCE_VERIFICATION.json。

本机 wheel SHA256：`f5013e99ddb0482ecd3ab4a443a03c5b8595421a4c77ada7768122c120ddadb5`。

官方 Windows ZIP：95687881 bytes，SHA256 `20a64487fb5e334c57c383a77716e720122dbb525d728fd1ac0f367c2c7839fc`。

官方 Ubuntu ZIP：136959579 bytes，SHA256 `512abd5db094f2d968b7198df9506692084a22f38b3cf5450dc744f844c38151`。

开发方外置 ZIP：SHA256 `cafad304d48d62c85134938835f76c1bfb75b696d66975c0af71d97512014850`；原独立 BLOCKED 证据 ZIP 仍为 `6ee677b012669dc2cd9f47598386baeef2da453d40767447497abe571d86a170`。

原命令/开始结束 UTC/退出码见各 `*.command.json`、`REVIEW_EXECUTION.json`；标准输出/错误日志逐项保留。核心命令是新 checkout 的 `python -I tools/ci.py`，环境 AQRP_RUN_ROOT 指向短的外部目录；独立脚本由该 SDK 安装解释器执行。完整 argv 和 cwd 已保存，避免仅报告通过数字。

审查辅助的一次失败保留：原脚本批次在 SDK 尚未下载 gitleaks.exe 时提前运行扫描，FileNotFoundError；前面的四/20/91 已过。待 SDK 扫描阶段产生固定工具后，仅重新运行扫描三控制成功。这是本次审查调度错误，不是产品测试失败；未删失败日志或重跑已通过用例。原脚本内的旧 SHA/执行者标签保留，外层命令记录绑定本次实际身份；不改写成 Gemini 执行或正式 Test。

## 限制、后续及封存

真实三主体 OS 隔离、正式 Test、金融批准、完整历史宿主重建仍按既有范围 **NOT VERIFIED / DEFERRED**；PR #7 的 Windows 隔离发现未在本次关闭。工程角色/API 或同一用户下运行不代表真实独立权限边界。哈希/终态链保证内容一致性，不能替代外部审批签名或受信部署。工程服务正式入口仍拒绝 APPROVAL_REQUIRED，未执行真实正式 Test。

原 G1 答案及历史实现说明保持历史字节；当前输出/API修复以本固定提交 g2-18439f3/REVIEW_PACKAGE、DEVELOPER_RESPONSE 和代码为准。旧说明的 0.4.0/Decimal34 记录不冒充本轮现状。

下一步需用户对七项受限工程范围作阶段验收；合并/标签/部署须另有明确授权。未合并、打标签、部署、实盘、进入 P5，未改账户/ACL/服务/调度。

本目录 EVIDENCE.zip 收录本报告、发现关闭记录、独立脚本与预存答案、实际命令/成功和失败日志、两份官方原始 ZIP、主审 SDK 全部 upload-selection 成员、固定源码子集及父工件/反例。明确省略 venv/cache/临时目录和展开源码副本；开发方 401MB 原 ZIP 与上一轮完整独立 ZIP 保留外部原件并绑定验证 hash，不重复封装。封存清单逐成员 SHA256，RECEIPT.json 记录总包大小/hash/CRC/全成员重核结果。收据是内容封存记录，不是数字签名。
