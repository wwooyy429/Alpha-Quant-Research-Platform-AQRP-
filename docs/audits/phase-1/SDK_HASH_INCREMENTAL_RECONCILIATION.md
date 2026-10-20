# Gemini SDK/hash增量复核接收与开发方事实核对

2026-10-21补充包已接收：现已取得Gemini文件hash校验脚本/日志/清单，补齐此前未附送原始材料的子项；脚本不执行Actions ZIP/SDK/Git拓扑核验，缺输入也返回0。完整独立执行仍未闭环，用户未接受限制/验收/发布。最新依据VERIFICATION_PACKAGE_RECONCILIATION.md及gemini/VERIFICATION_PACKAGE_INDEX.json；以下“未附脚本”等描述保留收到本包前的历史范围。

2026-10-21（Asia/Shanghai）。本记录由开发方编写，不是修改后的Gemini报告或用户验收。用户授权核对、归档并更新PR #2，明确不合并、不打标签、不进入Phase2。

## 原件及锚点

原件：gemini/aqrp_phase1_sdk_hash_incremental_recheck_report.md，15246字节，SHA-256 `725557d5ff2fc1c94d03c614bf7e40706f33aa0422c6b44f80289806b2e69cf0`，已与用户文件逐字节核对。索引为gemini/SDK_HASH_INCREMENTAL_INDEX.json。

Gemini固定审查`8bf189d76f15273a89eb4c2672c86e05a81aa148`，业务实现锚点`74bdb9216c585d27de91123605aff0266ca028cc`，前轮资料`d82536ae9ac7f61153747e63d044a640fea17b50`。原件保留Google搜索包装链接和历史PR标题；本交付使用直接GitHub链接，不将搜索链接或旧标题当执行证据。

## 核心结论

**七项勘误均已获Gemini明确AGREE，增量技术审查咨询结论PASS；独立执行要求仍未全部闭环。** 七项说明的审查认可与实际执行是否完成分开登记。审查方认为技术层面不阻断、流程门禁仍阻断，并建议可提交人工验收；用户尚未接受执行限制、尚未ACCEPTED/RELEASED。

原报告第三节自述独立复算旧报告及五份证据hash；第四节对ZIP给出MATCH，第七节本次补做清单却未明确列出ZIP重算/SDK运行。随本次交付未见新的独立校验脚本、命令、退出码或stdout附件，不能据此签署全部二进制/SDK执行已验证。SDK全量执行仍由审查方明确承认未做；ZIP/内部快照/跨OS独立执行方法与原始输出尚不可核验。新报告本身已收到，不能将未附执行原件补造为存在。

开发方本轮只重新核对封存字节/清单/拓扑/数学；既有开发方SDK回放及冒烟证据属于上一轮，不冒称本轮重新执行或Gemini执行。完整事实检查与执行脚本在implementation/sdk-hash-incremental-8bf189d/。

## 七项认可与实际关闭范围

| ID | Gemini第六节裁定 | 当前登记 / 仍需保留的边界 |
|---|---|---|
| ERR-P1-SDK-001 | AGREE，称说明闭环 | 结论分级/措辞认可已确认；另列独立执行缺口P1-SDK-EXEC-OPEN，不因说明获认可而关闭SDK/ZIP任务 |
| ERR-P1-SDK-002 | AGREE | 核心代码/测试/工具/50份P0资产不变获认可；原件第二节仍把变更范围列窄，实际36文件还含AGENTS/README/CHANGELOG/DECISIONS/ROADMAP等 |
| ERR-P1-SDK-003 | AGREE | 联网PyPI依赖/离线项目wheel口径确认；原件第五节仍使用“全量tools/ci.py离线构建”的缩写，以明确的两段安装口径为准 |
| ERR-P1-SDK-004 | AGREE | 参考差0与实数误差的区分确认；原件新增0.05误差2.78e-17的数量级笔误，应为约2.77555756e-18，0.1约5.55111512e-18；答案和容差不变 |
| ERR-P1-SDK-005 | AGREE | Manifest顶层仅排除snapshot_id/manifest_hash、其余类型及边界确认；不推导全部金融/时序风险消除 |
| ERR-P1-SDK-006 | AGREE | 认可11/14和未上传字节不可复算的原则；但原件所列11个文件名及清单层级不准确，按下表/真实ZIP更正，不能视为该列表已逐项执行吻合 |
| ERR-P1-SDK-007 | AGREE | 开发方/CI/独立/静态证据归属原则确认；第五节又误称配置剔除临时路径/时间戳，真实脚本只排除snapshot_id及manifest_hash，固定as_of仍参与比较 |

上述“AGREE”如实来自Gemini，不冒称开发方代其签署；数值/文件名/方法仍按可核验事实注明，不自动启动新一轮完整业务代码审计，也不修改正确实现来迁就报告。

## 原始ZIP、开发方证据再次核对

本轮开发方标准库检查结果在implementation/sdk-hash-incremental-8bf189d/checks.json；原ZIP和上轮SDK执行资料均保留在implementation/sdk-hash-74bdb92/。

| 内容 | 本轮核对 |
|---|---|
| 原报告及5份旧资料 | 6个hash与原索引完全一致 |
| 8bf189d当前清单 | 原SDK_HASH_MANIFEST.json全部223项hash一致；该清单随本轮状态更新成为历史快照，新的当前清单为SDK_HASH_INCREMENTAL_MANIFEST.json |
| Ubuntu ZIP 12288989083 | 实际SHA256 73385602dad830f3157dba8f5629616127777511830b02675fd06df517f93e7c，保留原字节 |
| Windows ZIP 12288679676 | 实际SHA256 8f092b7214202292995276a4dab3187063cd481d8a6556ac342e450738b64ea5，保留原字节 |
| 根清单/数据 | 每平台14条中11个存在文件hash匹配，3个未上传；各8个Parquet按Manifest的文件hash匹配，Manifest规范化hash通过 |
| 跨OS smoke | 原始smoke-result.json字节一致，SHA256均70202a124f458f829caa5ac72e136d9c40c76801a63f113aec9863d3bed864d6 |
| JUnit | 原ZIP各102测试/0失败/0错误/0跳过；本轮读取原证据，不冒称重新跑102测试 |
| PR临时合并提交 | f093faca父提交为main502c693与74bdb92，完整tree均66dc03a5cf38e8db9968873f2a0f1349b45eda09 |
| 源码/契约 | src/tests/tools/CI/锁等与74bdb92无差异；50份P0冻结资产、106项/16组目录保持不变 |

### 原件第四节清单更正

实际根清单中可核验的11个文件为：

`commands.log`、`coverage.json`、`coverage.xml`、`environment.json`、`junit.xml`、`scan-findings.json`、`secret-scan.log`、`smoke-config.json`、`smoke-result.json`、`smoke-run.json`、`smoke-snapshot.json`。

根清单内缺3项：`.coverage`、`gitleaks`或`gitleaks.exe`、`pip-26.2.1-py3-none-any.whl`。项目wheel字节也未上传，但它不是该14条根清单中的第4个缺项：wheel hash声明位于environment.json。原件列出的`command-log.txt`及`smoke-receipt.json`不存在；`artifacts.json`虽在ZIP内却未列入自身清单，`dataset/`亦非根清单条目，其文件由Manifest保护。不能用原件的11项列表替代真实文件清单。

原件第五/七节再次提到“开发方本地全量重跑”，需限定历史：8bf189d本轮RUN_RECEIPT明确full_ci_entry_rerun=false；对应开发方执行是定向校验、SDK新冒烟及数学复跑。更早完整安装/测试和真实CI证据保持各自固定SHA来源，不能移植成本轮新执行事实。

## 证据分级与剩余条件

| 项目 | 目前可登记的等级 |
|---|---|
| Gemini七项认可/技术PASS | 用户提供的正式审查原件；已核实文字及目标SHA |
| Gemini旧报告/5文件独立hash复算 | REVIEWER REPORTED EXECUTED；报告列值吻合，未新增附送原始执行记录，不冒称已重现审查方执行 |
| Gemini原始ZIP hash | REVIEWER REPORTED MATCH；未明确披露本次实际取得二进制/计算方法及输出，独立执行METHOD NOT EVIDENCED |
| Gemini SDK全量入口 | NOT RUN / NOT VERIFIED；报告明确承认环境限制 |
| Gemini快照内部/跨OS执行 | 未附可核验的新执行过程；静态审阅、引用开发方证据与实际独立运行分别记录 |
| 开发方ZIP/Manifest/根文件/拓扑/固定数学核对 | DEVELOPER EXECUTED；本轮新检查通过，旧SDK回放/冒烟记录保留 |
| 未上传字节 | 仍不可复算；Gemini认为技术层面非阻断是其风险意见，不登记为文件存在或hash执行完成 |

未闭环的门禁：
1. P1-SDK-EXEC-OPEN：指定SDK与原始产物等独立执行证据缺口，须补齐或由用户明确决定接受限制；本次未发生该决定。
2. 用户正式Phase1人工验收，当前false；报告PASS/YES/AGREE及用户转交报告不代替验收。
3. PR #2合并main、标签发布各需明确授权；当前均无，本次也不得执行。
4. 获授权后核对最终main内容范围、适用检查、版本/批准/审计追溯，发布及核验phase1-baseline；不能只创建标签就视为RELEASED。
5. Phase2仍需单独的用户启动授权，不能因为主干Gate通过就自动开工。

原报告所谓“4项法定前置条件”按本项目治理条件记录，不作外部法律要求解读。原历史F-002/F-003/PRE-001/PRE-003按限定审查范围保持CLOSED；PRE-002仅MITIGATED，Baidu工作区不据此冒称已迁移。

## 当前状态与停止点

技术审查及七项说明确认PASS / ALL SEVEN AGREED；完整专项独立执行仍NOT VERIFIED，人工验收/发布均未发生。PR #2保持Draft/Open；main仍502c6931dcfce50bee2f71a80524475fae6396bf，phase0-baseline仍7de1d0e81385ae97f98ea673fe05dd726f0b577b，无phase1-baseline。本轮只归档/核对/更新记录，原件、ZIP、SDK代码/答案/阈值和P0冻结资产不修改。
