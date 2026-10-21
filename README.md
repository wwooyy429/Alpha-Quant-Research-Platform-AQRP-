# Alpha Quant Research Platform（AQRP）

2026-10-21 当前：**Phase2 = INCREMENTAL AUDIT PASS AS REPORTED / CORE MATH VERIFIED / REPORT ALIGNMENT AND EXECUTION LIMITS OPEN**。Gemini对0b5107f增量报告PASS、十二项AGREE/CLOSED及两项Low继续CLOSED已接收；修订数学.py/.log原件已收到，Volume两输入、证券B推导、非零浮点误差经开发方复跑/独立核算通过，旧数学错误不再作为当前未修项。报告解释仍有PR标题/BASELINE、FACTOR-011、源码路径等事实冲突，详见docs/audits/phase-2/MATH_INCREMENTAL_RECONCILIATION.md及gemini/MATH_INCREMENTAL_INDEX.json。SDK独立执行仍NOT VERIFIED、ZIP本轮Evidence Reviewed Only；未人工验收/接受限制，main/稳定标签不动，不合并、不打标签、不进入Phase3。

以下保留历轮状态，当前以上述实现复核状态及固定SHA资料为准。

2026-10-21 Phase2计划预审接收：Gemini对4f8b0de报告PLAN PASS、无阻断项；用户明确允许继续已授权范围。报告原件/需求职责与分支/数学勘误见docs/audits/phase-2/gemini/PRE_REVIEW_INDEX.json及PRE_REVIEW_RESPONSE.md。当前IMPLEMENTING；只实现10项既定需求和Momentum/Reversal/Volume，不按报告误写新增Volatility/DAG。未验收/合并/发布，不进入P3。

以下为历史状态，当前以上述预审接收为准。

2026-10-21 最新授权：用户明确“请正式开始进入phase 2”。已从核实main / phase1-baseline f579b2c99e762085772de6e70ba1fa98792a7add创建feature/phase-2-factor-registry；**Phase2 = PLAN PRE-REVIEW REQUIRED**。计划与10项需求映射见docs/audits/phase-2/PLAN.md和AUTHORIZATION.json；Gemini计划预审前不编写本阶段业务实现。Phase1已发布，既有执行限制保留；P2验收/合并/标签及P3尚未授权。此前“Phase2未授权”仅为历史。

以下各轮状态保留历史来源；当前阶段权限以上述启动记录为准。

2026-10-21 最新发布状态：**Phase1 ACCEPTED / RELEASED**。用户已分别完成验收并授权“请开始合并并打标签”；PR #2已合并（9b843b17ccf362cf5b7a5351269559a627c55b32），稳定标签phase1-baseline指向含发布登记的main版本，远端原子发布后核验生效。原话和合并/SDK证据见docs/audits/phase-1/publication/；基线见docs/audits/phase-1/BASELINE.md。Gemini独立执行及旧远端缺字节事实保留，未声称新增Gemini审查。Phase2尚未授权，不自动启动。

以下既有未合并/未发布/未授权文字为之前各轮历史，当前以本次发布登记和实际Git核验为准。

2026-10-21 最新人工决定：用户明确表示“phase 1验收已完成”，现登记 **Phase1 = ACCEPTED，尚未 RELEASED**。验收对应接收时PR #2的71cc044d5f4e2079426049c0f7c6f747fee01692（业务74bdb92），原话与范围见 docs/audits/phase-1/acceptance/ACCEPTANCE.json。此前“等待验收/未ACCEPTED”仅为历史；Gemini独立执行和原远端缺字节事实继续保留，本次未伪造逐项限制豁免。合并main、打标签及Phase2均未授权。

以下既有状态段落保留为各轮历史，当前人工验收状态以上述记录为准。

2026-10-21 最新本地验证：已按用户授权配置 Conda aqrp-p1（CPython3.13.16）和独立 VS Code 工作区；完整 SDK、Conda 直接运行的同一组102测试、两份 Actions 原始ZIP/八表/SDK回放均通过。实际命令配置与原始日志见 docs/audits/phase-1/implementation/conda-vscode-74bdb92/README.md。执行者为 Codex 开发方，不能补记为 Gemini 独立执行；远端3项根文件及项目wheel原字节缺口、独立执行/人工验收/发布门禁保留。未合并、未打标签、不进入Phase2。


最新补充包：[脚本/日志接收核对](docs/audits/phase-1/VERIFICATION_PACKAGE_RECONCILIATION.md)。文件hash子项材料已补齐，完整SDK/原始产物独立执行仍未闭环；七项认可保留，未验收/发布、不进入Phase2。下列“未附脚本”是此前接收状态。

最新增量：Gemini已认可七项SDK/hash勘误、技术审查建议PASS；[本轮核对](docs/audits/phase-1/SDK_HASH_INCREMENTAL_RECONCILIATION.md)保留独立SDK/产物执行证据缺口及新报告细节勘误。用户未接受限制、未验收/发布；PR保持Draft，不合并、不打标签、不进入Phase2。以下各轮文字作为历史，当前以本轮核对为准。

最新核对：Phase1实现审查建议PASS；[SDK/hash专项](docs/audits/phase-1/SDK_HASH_VERIFICATION_RECONCILIATION.md)仅部分完成，Gemini实际SDK/ZIP验证受阻。开发方已补充原始ZIP/hash/八表及SDK冒烟证据，不替代独立执行；等待用户验收，未合并/发布，不进入Phase2。以下历史状态以最新专项记录为准。

Phase 0 已发布。Phase 1 计划经 Gemini 对固定380d9f8预审PASS，现已实现合成日频数据基础，已收到Gemini对74bdb92的实现PASS报告及独立勘误确认PASS，当前等待人工验收。阶段验收、main合并、发布及Phase 2均尚未获授权。

本阶段提供稳定证券标识、Decimal单位、UTC微秒时间与固定IANA规则、日历、PIT可见修订、历史股票池/状态、拆股与分红研究视图、质量报告、不可变Parquet快照和可重建DuckDB索引。首版只支持明确的SYNTHETIC_V1测试profile，真实市场接入另行确定。

当前范围和真实验证见[Phase1实现审查包](docs/audits/phase-1/IMPLEMENTATION_REVIEW_PACKAGE.md)、[数据SDK使用说明](docs/audits/phase-1/DATA_SDK.md)和[进度](docs/PROGRESS.md)。[独立计划预审原件及索引](docs/audits/phase-1/gemini/PRE_REVIEW_EVIDENCE_INDEX.json)保持原字节。380d9f8中的PLAN、SELF_CHECK、MANIFEST和COMMAND_LOG仍为历史计划快照，不能当作当前实现测试结果。

业务环境精确CPython3.13.16标准GIL/x64，直接与传递依赖固定在requirements.lock。安装及完整验证入口为`python tools/ci.py`，须在干净、已提交工作区和已核实解释器下运行；它把venv/构建/缓存/测试产物放入非同步临时路径，哈希安装依赖，从固定Commit离线构建并安装本项目wheel，执行静态/单元/性质/契约/集成/泄漏/覆盖率/秘密扫描及数据smoke。详见[复现说明](docs/audits/phase-1/REPRODUCE.md)。

因子Registry、因子研究、组合/风险、回测账本、网页及对应业务CLI仍Planned；高级扩展Deferred，真实交易与任意外部代码执行Unsupported。不存在真实凭证、供应商或订单接入。


本轮报告原件、审查方发现关闭记录及开发方核对见[实现审计接收索引](docs/audits/phase-1/gemini/IMPLEMENTATION_AUDIT_EVIDENCE_INDEX.json)与[实现报告勘误/处理意见](docs/audits/phase-1/IMPLEMENTATION_AUDIT_RESPONSE.md)。上述核心勘误已获Gemini确认；最新[补充确认与状态核对](docs/audits/phase-1/ERRATA_CONFIRMATION_RECONCILIATION.md)保留本地SDK未验证及远端产物未重算等非阻断限制。当前审查通过、等待人工验收；不能将用户转交报告当作验收、合并或发布授权。
