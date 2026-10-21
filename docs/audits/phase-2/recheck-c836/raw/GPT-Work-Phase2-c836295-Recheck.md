# GPT Work 补充审核 — Phase2 修复固定版本复核

**固定目标：c8362953f555606795b6804cdfe28ff690c2364d。本轮补充技术复核通过，未发现阻断问题。**

**WORK-P2-001、002、003均通过本轮适用复核；002/003在本报告中记为CLOSED — GPT Work supplemental recheck PASS。** 本轮真实新安装包全套417通过，未编辑原16项通过，未编辑原四项P2探针全部通过。该结论仅属于实际审核范围，不表示Gemini本人执行、用户阶段验收、合并/发布或Phase3启动授权。

## A. 审核对象、权限、方法与范围

| 项目 | 本轮事实 |
|---|---|
| 仓库 / PR | [AQRP PR #3](https://github.com/wwooyy429/Alpha-Quant-Research-Platform-AQRP-/pull/3)，Draft/Open、未合并 |
| 固定目标 | **c8362953f555606795b6804cdfe28ff690c2364d**；开始/结束与PR、远端Phase2分支、开发副本HEAD一致 |
| base/main | fb1ba4fd51202a303115e4449ee49db09ccc071c，已登记P1补丁v0.1.1 |
| 上轮目标 | c70727c39182f81ee142730da9a9833a51581cd1 |
| 修复业务锚点 | 708b83be1dd597395b41f2ff6e10702749175bbf；业务到最终目标的src/tests/tools/CI/构建/锁无差异 |
| 独立副本 | `C:/Users/11638/AppData/Local/Packages/OpenAI.Codex_2p2nqsd0c76g0/LocalCache/Local/AQRP/reviews/p2-c836295`，detached/clean，Git longpaths仅在审核副本设置 |
| 开发副本 | C:/Users/11638/AppData/Local/AQRP/checkouts/phase1-57461d5d-5de2-4c78-9b4e-5fad2b5ccb29；开始/结束clean，未修改 |
| 本轮新SDK run | aqrp-a4001fd1-4cd2-499a-bd40-3e6be14af9fe；标准CPython3.13.16/x64/GIL、全新隔离venv、实际0.2.0 wheel |
| 时间 | 2026-10-22 00:54:35+08:00开始；核验完成2026-10-22T00:59:28.662224+08:00；报告2026-10-22T01:03:09.763504+08:00，Asia/Shanghai |
| 权限/工具 | 只读Git/原件、GitHub PR/Actions读取、PowerShell及精确Python隔离执行；输出/环境/缓存/数据均为非同步审核目录 |

重新读取AGENTS最新状态、lineage-fix授权/范围/开发方逐项响应/接收索引/代码审查证据，逐行检查两处实现差异与25项新增正式回归，核对既有准入及P1修复边界。此前已读的治理/契约/10项Phase2范围与未改实现，以差异、冻结文件和实际执行重新核实，不宣称穷尽所有潜在输入或重审全部Phase0及后续阶段。

执行原版tools/ci.py完整新安装/检查、原16回归、原四探针、最终目标双平台原ZIP下载与深度核验、数据/因子重放、原query身份重算和原证据字节核对。正式源码、测试、Golden、锁、项目状态、Gemini原件和PR未修改；未提交、推送、合并、打标签、发布或向其他聊天/人员发送消息。

## B. 授权及阶段边界

- 用户本轮指定修复后的完整SHA请求复核。开发与修复沿既有Phase2范围，未新增需求或引入真实账户/订单；本轮不登记用户验收或发布。
- 远端main/v0.1.1仍fb1ba4fd51202a303115e4449ee49db09ccc071c；v0.1.1附注对象6611ca42e213c78be5155cba702ae789d48aab24不变。原phase0-baseline对象/7de1d0e目标、phase1-baseline对象/f579目标均不变。
- 候选包保持0.2.0，10项Phase2范围保持；ENGINEERING_APPROVED / TEST_ONLY / financial_approval=NONE仍是工程准入限定，不构成研究/策略/金融批准或OS沙箱。
- 开发方、CI、既有Gemini报告与本次GPT Work真实执行分别记录。本报告不补记Gemini本人运行，也不把历史缺原件/未执行限制抹成已经完成。Phase2验收、接受限制、合并/标签/发布及Phase3启动按各自事实处理。

## C. 问题逐项复核

以下三项均限定目标 **c8362953f555606795b6804cdfe28ff690c2364d**。CLOSED指本补充审核对已报告技术问题的处置，未直接修改仓库问题/批准记录。

| ID / 原严重度 | 原问题与本次实际结果 | 本轮处置 |
|---|---|---|
| WORK-P2-001 / High | 已审P1三处共享源码与发布main/业务8902ba0保持相同；原16及UNKNOWN日历正式PIT→因子反例通过，六项host集成边界继续通过 | CLOSED / 补充复核通过保持 |
| WORK-P2-002 / Medium阻断 | 合法缩进/键顺序/尾空白统一为canonical不可变配置；batch/config/content_hash与实际文件一致；实际落盘SHA256逐项匹配，重复JSON对象键拒绝 | CLOSED / 本轮补充复核通过 |
| WORK-P2-003 / Medium阻断 | 按配置FactorSpec重建既有schema并冻结实际params；重算hash同时核对config/每行；旧hash换lookback及为旧Signal重贴新hash均拒绝，正常lookback1/2分别0.1/0.21 | CLOSED / 本轮补充复核通过 |

**002代码依据：** [contracts.py第251行](C:/Users/11638/AppData/Local/Packages/OpenAI.Codex_2p2nqsd0c76g0/LocalCache/Local/AQRP/reviews/p2-c836295/src/aqrp/factors/contracts.py:251)按唯一JSON对象键解析，[第290行](C:/Users/11638/AppData/Local/Packages/OpenAI.Codex_2p2nqsd0c76g0/LocalCache/Local/AQRP/reviews/p2-c836295/src/aqrp/factors/contracts.py:290)保存规范配置；[engine.py第137行](C:/Users/11638/AppData/Local/Packages/OpenAI.Codex_2p2nqsd0c76g0/LocalCache/Local/AQRP/reviews/p2-c836295/src/aqrp/factors/engine.py:137)直接对实际落盘文件做SHA256。原样格式化JSON反例通过，其本轮[真实成功manifest](C:/Users/11638/AppData/Local/Packages/OpenAI.Codex_2p2nqsd0c76g0/LocalCache/Local/AQRP/reviews/work-p2-c836295/new-probe-tmp/test_work_p2_reformatted_valid0/roundtrip-runs/4170f712-8546-49e7-a6d1-765e327247a8/manifest.json)与config/signals/events文件hash精确匹配。合法往返批次内容hash保持一致；非法编码、非有限数和重复键有结构化拒绝。没有通过放松校验或更换原探针期望来消除失败。

**003代码依据：** [contracts.py第270行](C:/Users/11638/AppData/Local/Packages/OpenAI.Codex_2p2nqsd0c76g0/LocalCache/Local/AQRP/reviews/p2-c836295/src/aqrp/factors/contracts.py:270)按既有schema冻结实际参数并计算checksum，再验证参数列表是唯一、完整的冻结投影、config哈希及每行血缘一致。原canonical参数反例已拒绝；重复/缺键/未知/非法类型/范围、新hash与旧Signal矛盾均由25项正式回归覆盖。正确值来自手工121/110−1与121/100−1，没有用待测因子生成期望。

相对上轮，Python实现仅contracts.py、engine.py变化，receipt随实际代码重审更新；P1数据/时间/PIT、因子公式/窗口/只读输入、Golden、锁和候选版本保持原字节。完整26模块bundle独立重建后与active CODE_BUNDLE.json及随库回执一致：**51933fe2508e61a25fef53ea73b4210a67cb19d6531e1bf614e206db32a1d62d**。未发现新增需编号的实质缺陷。

## D. 需求→实现/测试→证据→状态

| 需求 | 本轮实现/测试及证据 | 状态 |
|---|---|---|
| DATA适用修复与P2依赖 | 共享源码等价、132项数据修复回归、原16和六项host边界 | 已测范围通过，001保持通过 |
| FACTOR-001 | FactorSpec/参数schema/Context，配置schema恢复及正常/非法参数控制 | 通过 |
| FACTOR-002 | SignalBatch/逻辑键/血缘/配置字节，原反例和25项新回归、实际文件hash | 002/003修复通过 |
| FACTOR-003 | 精确Ref、注册幂等/冲突、兼容、停用/旧pin/紧急停用/rollback | 已测P2范围通过 |
| FACTOR-004/005/006 | Momentum/Reversal/Volume手算Golden、逐证券窗口、零量/行动、三端真实回放 | 通过；公式与容差未改 |
| FACTOR-010 | 不可变参数/版本pin/权重仅元数据、配置hash与参数血缘 | 通过 |
| FACTOR-011 | 只改精确Ref的注册替换/API版本兼容 | 已测P2范围通过，不扩大到研究/回测/E2E |
| FACTOR-012 | 每decision可见数据、只读副本、mutation和有效正控、host拒绝异常 | 通过 |
| SEC-001 | 26模块bundle/审查回执、固定内置准入、共享源码漂移拒绝 | 限工程TEST_ONLY范围通过，不是OS沙箱 |
| ENV-001/002、SEC-002 | 精确解释器、新venv原锁/真实wheel、最终头双平台原件、扫描正负控制 | 实际核验范围通过 |
| QA-002 | 417正式+原16+原四项、逐模块行/分支门槛、独立参考与原始证据 | 通过；不以测试数量单独证明正确性 |

正式需求目录仍106项、Phase2仍10项，50项P0冻结文件hash匹配。原报告路径/职责/术语勘误按此前对账披露，不为迎合错误文字新增源码、DAG或未来能力。

## E. 本轮实际执行、原始证据与限制

| 项目 | 本轮实际结果 |
|---|---|
| 完整新SDK | **417通过/0失败/0错误/0跳过，exit0**；aqrp-a4001fd1-4cd2-499a-bd40-3e6be14af9fe，固定目标、dirty=false、complete=true |
| 安装与来源 | 标准CPython3.13.16/x64/GIL；新venv按原锁require-hashes/only-binary安装，22活动锁包版本相符；真实0.2.0 wheel的26模块/准入JSON与源码一致 |
| 本地wheel SHA256 | `c856ab38fdc2452f623e1434aa8e7c8399bd737adf35028ecff5ffa1aa115a33`；与CI原wheel分别记录/核对 |
| 原两轮16项 | **16通过，exit0**，两份原脚本hash不变 |
| 原四项P2探针 | **4通过，exit0**，与最初报告脚本逐字节相同；未改正确答案/容差 |
| 静态/覆盖/参考/数据/扫描 | ruff/格式、逐模块行与分支门槛、数学参考、数据与因子smoke、固定秘密扫描器正负控制实际通过 |
| 保护与接收 | 本轮清单335项hash匹配、50冻结资产匹配；旧c707原248项尺寸/hash重新核对，245项短路径归档同字节，3项省略明确，原清单字节一致 |

当前最终目标的[CI run39637043080/attempt1](https://github.com/wwooyy429/Alpha-Quant-Research-Platform-AQRP-/actions/runs/39637043080)两份原ZIP均实际下载、校验和解包。本轮使用最终头新原件，仓库已归档的708b83b业务轮次原件保持原身份：

| 原件 | Artifact | ZIP字节 | 与GitHub官方digest匹配的SHA256 |
|---|---|---|---|
| phase2-ubuntu-24.04-1 | 12363175606 | 149725 | 1df7d45c6fe543b48ed36b116687a7932b84db9defada2b72061dd0269298637 |
| phase2-windows-latest-1 | 12363130787 | 149909 | b3491d86f641ada3e579d36e08a8b94fe0b4a218fcd81afadd8ab1d0ee542bcf |

两端环境均complete=true、dirty=false、Python3.13.16、GitHub run39637043080/attempt1，JUnit各417通过。实际CI checkout **d1feaae218b25741e57fdfa024c0072f87f32e67** 的Git父为main fb1和目标c836，tree **6023eca7e69ab480341f3f5af0df8177b5d6d0d0** 与目标一致；这是临时PR合并，main没有纳入本修复。

每端安全路径/CRC/无重复名/无符号链接、46项选择文件hash与14项上传根hash、实际wheel/准入JSON/.coverage、JUnit、覆盖率门槛及空扫描报告通过；2项工具字节的省略按原上传政策保留。data与factor-data各八表的分片及独立manifest digest核验、读取/查询、三因子实际回放均通过；原run/computation UUID保留后完整Signal行原字节一致。两端及本轮本地的两套逻辑数据、查询与配置、三因子结果一致。

比较仅排除表行snapshot_id和data config的snapshot_id/manifest_hash，未改写原件；另外使用各原存储root重算**12项原query_hash全部匹配**，不把路径迁移后的query_hash误要求为相同。重放一致性与手算/Golden验证分别说明，不单靠同一SDK重复结果证明数学正确。

**失败保留：** 上轮c707两项失败日志、错误成功产物、旧392/原16等均按原字节接收，不改成新版成功。本轮项目SDK/原16/原四项均无失败。审核辅助核验第一次把原清单路径误写为received/raw，实际文件位于received；只修正外置审核脚本路径后全部核验通过。第一次脚本、JSON、stdout/stderr、exit1均保留为attempt1-*，未改项目代码、证据原件或答案；该路径错误不作为项目缺陷。

证据入口：[全部核验结果](C:/Users/11638/AppData/Local/Packages/OpenAI.Codex_2p2nqsd0c76g0/LocalCache/Local/AQRP/reviews/work-p2-c836295/evidence-verification.json)、[SDK完整命令/输出](C:/Users/11638/AppData/Local/Packages/OpenAI.Codex_2p2nqsd0c76g0/LocalCache/Local/AQRP/reviews/work-p2-c836295/runs/aqrp-a4001fd1-4cd2-499a-bd40-3e6be14af9fe/commands.log)、[新环境](C:/Users/11638/AppData/Local/Packages/OpenAI.Codex_2p2nqsd0c76g0/LocalCache/Local/AQRP/reviews/work-p2-c836295/runs/aqrp-a4001fd1-4cd2-499a-bd40-3e6be14af9fe/environment.json)、[原16日志](C:/Users/11638/AppData/Local/Packages/OpenAI.Codex_2p2nqsd0c76g0/LocalCache/Local/AQRP/reviews/work-p2-c836295/original16.stdout.log)、[原四项日志](C:/Users/11638/AppData/Local/Packages/OpenAI.Codex_2p2nqsd0c76g0/LocalCache/Local/AQRP/reviews/work-p2-c836295/new-probe.stdout.log)、[12项原query身份](C:/Users/11638/AppData/Local/Packages/OpenAI.Codex_2p2nqsd0c76g0/LocalCache/Local/AQRP/reviews/work-p2-c836295/original-query-identity.json)、[逐问题处置](C:/Users/11638/AppData/Local/Packages/OpenAI.Codex_2p2nqsd0c76g0/LocalCache/Local/AQRP/reviews/work-p2-c836295/finding-disposition.json)、[总证据清单](C:/Users/11638/AppData/Local/Packages/OpenAI.Codex_2p2nqsd0c76g0/LocalCache/Local/AQRP/reviews/work-p2-c836295/REVIEW_EVIDENCE_MANIFEST.json)。

**NOT VERIFIED与边界：** 新的Linux本地安装（本轮是Ubuntu CI原件在新Windows SDK核验/回放）；Gemini本人新的完整SDK执行；旧P1历史未上传原字节；旧综合AST/math/hash工具原件；转交聊天的外部身份认证；后续新SHA、用户Phase2验收/接受限制/合并/标签/发布和Phase3启动。当前技术修复通过不追溯改写这些历史或批准事实。

## F. 给Codex的接收与后续复核清单

1. 对完整SHA **c8362953f555606795b6804cdfe28ff690c2364d** 接收“WORK-P2-001–003经GPT Work补充复核通过”；002/003本轮可记录CLOSED（补充技术复核），关联真实417/16/4与最终头原ZIP证据，不写成Gemini本人执行或用户已验收。
2. 保留已审bundle **51933fe2508e61a25fef53ea73b4210a67cb19d6531e1bf614e206db32a1d62d**、旧Ref/失败原件、正确Golden/容差/锁和P1集成。此后修改相关源码或准入策略时，应实际重审bundle并给出新完整SHA及受影响验证，不能浮动沿用本次PASS。
3. 本轮没有新的业务修复任务。旧历史未上传字节/未提供工具等限制按原范围保留，不借本次新包成功宣称恢复旧原件。
4. 用户Phase2人工验收、接受相关限制、main合并、标签/发布及Phase3启动分别处理；本报告未执行或代签这些动作，未改正式状态。

**最终结论：本轮补充技术复核通过，未发现阻断问题；WORK-P2-001–003全部通过适用复核。仅为GPT Work补充审核，不表示Gemini本人执行、用户验收或发布授权。**
