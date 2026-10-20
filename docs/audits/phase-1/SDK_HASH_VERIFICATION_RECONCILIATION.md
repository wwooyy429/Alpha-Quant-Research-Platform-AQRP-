# Phase1 SDK执行与远端哈希报告接收、勘误及补充验证

2026-10-21（Asia/Shanghai）。本文件由开发方编写，不是Gemini签署的更正报告，也不代表用户验收。用户本次授权核对、归档、处理问题并更新PR #2；明确不合并、不打标签、不进入Phase2。

## 原件与版本

原报告按字节归档在gemini/aqrp_phase1_sdk_and_remote_hash_verification_report.md，SHA-256为`9fff9ee3da601e31aac5f2bbc77b09c38c5aa1050359d9c1513025c5824f5933`。同送的5份证据在gemini/aqrp_phase1_sdk_hash_evidence/；逐文件hash、来源和证据分级见gemini/SDK_HASH_VERIFICATION_INDEX.json。原件不作改写，附带JSON中的PASS/READY保留为审查方原始主张。

业务执行锚点仍`74bdb9216c585d27de91123605aff0266ca028cc`，报告审查资料锚点`d82536ae9ac7f61153747e63d044a640fea17b50`匹配。保护范围src/tests/tools、requirements.lock、pyproject.toml、.python-version、CI和扫描配置两版本无差异。原报告称全部变更“严格局限于docs/audits/phase-1/”不准确：AGENTS、README、CHANGELOG、DECISIONS、PROGRESS、ROADMAP、TRACEABILITY也有状态更新；完整路径差异在implementation/sdk-hash-74bdb92/archive-checks.json。

## 核对结论与当前状态

**实现技术审查建议PASS保留；本次专项验证仅部分完成，不登记成专项整体PASS。** Gemini明确未安装/运行CPython3.13.16 SDK，未下载ZIP，也未执行原始产物内部及跨平台数据比较。这些独立执行项仍BLOCKED / NOT RUN；静态审计不能替代它们。Gemini建议可人工验收是咨询意见，用户尚未接受剩余限制或验收/发布。

开发方本次成功下载目标Run #9的两个原始ZIP，独立重算哈希、验证实际存在文件及快照，复放查询并运行一次新SDK冒烟。开发方验证可以补足可复现证据，不能追认Gemini已执行。用户要求的“由Gemini实际执行”仍未闭环；需有执行能力的独立审查环境补做，或用户另行明确决定如何接受限制。本次不请求或推定此类豁免。

## 原报告勘误与开发方处理

| ID | 核对发现 | 处理 / 状态 |
|---|---|---|
| ERR-P1-SDK-001 | A.1/A.2/B.3承认BLOCKED/NOT RUN，结尾整体PASS及READY容易被误读为两项执行已完成；B.4/B.5仅静态分析却写PASS | 实现审查建议与专项实际完成度分开记录；Gemini SDK/ZIP/内部数据/跨平台执行仍未完成。OPEN：独立执行证据缺口，未发现据此必须修改业务代码的缺陷 |
| ERR-P1-SDK-002 | 声称74bdb92→d82536a变更只在审查目录 | 已核实保护目录不变，同时列出审查目录以外状态文档差异；开发方勘误已记录 |
| ERR-P1-SDK-003 | Findings中再次将依赖描述为“离线安全安装通过” | 正确为PyPI联网、require-hashes/only-binary安装锁定依赖；项目wheel才no-index构建/安装。F-P1-PRE-001的原审查关闭不依赖“整套离线”断言；实现/锁不变 |
| ERR-P1-SDK-004 | 数学脚本用float(Fraction)与同值float字面量相减，得到0，不能证明对精确实数零误差，也没有调用SDK | 精确Fraction复算：0.05误差1/360287970189639680≈2.77555756e-18，0.1误差1/180143985094819840≈5.55111512e-18，均满足既定abs1e-12/rel1e-10。原正确答案/阈值不改 |
| ERR-P1-SDK-005 | B.4泛称排除“易失字段”、统一时间/Decimal“完全杜绝”风险 | Manifest顶层只排除snapshot_id和manifest_hash；表内snapshot_id仍受Parquet hash保护。Schema另有string/int64/date32；日期字段不同于event/available时间戳。声明只适用于明确字段及已测试边界，不能推导普遍无风险 |
| ERR-P1-SDK-006 | 静态说明只提扫描器/引导wheel未上传，没有实际缺项枚举 | 原始ZIP实际每平台缺3项：.coverage、gitleaks或gitleaks.exe、pip-26.2.1-py3-none-any.whl。14项根清单中11项实际hash通过；不能宣称14/14。项目wheel仅有environment中的声明hash，原始wheel字节未上传，仍不能复算 |
| ERR-P1-SDK-007 | B.5静态等价分析不能证明双平台全部表数据一致；数学脚本smoke部分只是打印硬编码预期 | 已由本次开发方读取原始ZIP实际验证8表schema及逻辑值、smoke字节和SDK回放；Gemini对应实际执行仍NOT RUN。原数学脚本不计SDK测试，也不计对fixture执行PIT查询 |

本次附送数学脚本/日志比前轮自述多出原始资料；已逐字节归档并检查脚本。开发方另用3.13.16重跑该脚本exit0，输出单独归档，不能冒称重现了审查方Linux3.11环境或证明原始执行来源。环境探测/下载失败日志仍按审查方提供的记录登记，不将其网络错误推断成GitHub产物不存在。

## 开发方实际补充执行

目标运行：[Run #9 / 39476825340](https://github.com/wwooyy429/Alpha-Quant-Research-Platform-AQRP-/actions/runs/39476825340)，pull_request、attempt1、head74bdb92、success。下载及核对由开发方本机执行；证据在implementation/sdk-hash-74bdb92/，ZIP为原字节。

| Artifact | ID | 实际ZIP SHA-256（与官方digest一致） |
|---|---|---|
| phase1-ubuntu-24.04-1 | 12288989083 | 73385602dad830f3157dba8f5629616127777511830b02675fd06df517f93e7c |
| phase1-windows-latest-1 | 12288679676 | 8f092b7214202292995276a4dab3187063cd481d8a6556ac342e450738b64ea5 |

实际environment记录的执行Commit为PR临时合并提交`f093faca9a9dd4977caa1142267ff494766d3c7e`，不是直接74bdb92。开发方已取回该Git对象，核实父提交为main502c693和74bdb92，完整tree均为`66dc03a5cf38e8db9968873f2a0f1349b45eda09`。因此执行内容与审查目标完全相同，但不把Run head SHA与checkout SHA混写。

实际完成：
- 安全检查ZIP路径/重复成员/链接/展开体积后解压，原ZIP保留；两平台各11个可用根文件hash匹配，3个未上传项明确登记；额外dataset文件经Manifest逐个保护，artifacts.json自身由ZIP digest保护。
- 两平台各8个Parquet的文件hash、schema、行数、Manifest规范化hash、质量/范围/血缘及SDK verify_snapshot通过。
- 固定fixture hash、配置hash、结果hash核对通过；两个结果原字节一致，SHA-256均为`70202a124f458f829caa5ac72e136d9c40c76801a63f113aec9863d3bed864d6`。
- 每平台原始JUnit均102测试/0失败/0错误/0跳过，原始coverage.json经既定逐模块行/分支门槛通过；扫描报告为空。这是读取既有CI原始产物，不是本轮重新执行102测试。
- 两平台八表仅剔除snapshot_id后schema/逻辑记录一致；对比在内存副本中进行，未修改任何封存数据。配置只剔除snapshot_id/manifest_hash；未要求ZIP、wheel、全部Parquet字节相同。
- 使用现有锁定3.13.16环境，从git archive导出的74bdb92源码验证下载快照、复放查询，并新发布一次合成快照/查询，结果与两平台逐字节一致。迁移目录后的query_hash包含路径而变化，不误判为业务漂移。
- 这是开发方定向复核/SDK冒烟，不是Gemini本地执行，也没有重跑全套干净安装入口tools/ci.py。该入口原始双平台结果仍由既有Run #9提供。

复现补充校验：在锁定Python环境执行`verify_artifacts.py <含目标Git对象的仓库> <两个ID.zip所在目录> <新外部输出目录>`。脚本自行git archive固定版本；需要本地有f093faca对象，可只读fetch该SHA。源代码/ZIP不修改，输出目录必须新建于源码外。

## 发布前条件及停止点

- 本次报告/5份原始资料/实际下载证据已归档；报告勘误以开发方单独记录处理，没有伪造Gemini更正签名。
- 原审查关闭F-002/F-003/F-P1-PRE-001/PRE-003按其固定范围保留；PRE-002仍MITIGATED，.gitignore不证明整个Baidu源码已物理迁移。
- Gemini指定环境SDK、ZIP哈希、内部数据/跨平台实际执行未完成；本次开发方补充证据可供独立核对，不能自动豁免用户指定的独立执行要求。是否接受限制由用户决定。
- Phase1仍未ACCEPTED、未RELEASED；PR保持Draft/Open。人工验收、授权合并/标签、main最终范围/检查核实、基线发布和独立主干核验是后续门禁，Phase2还须单独启动授权。
- 本轮不修改src/tests/tools/CI/依赖锁/Golden及50份P0冻结资产；106项/16组目录不变。主干502c693和phase0-baseline固定目标7de1d0e不动，无phase1-baseline。
