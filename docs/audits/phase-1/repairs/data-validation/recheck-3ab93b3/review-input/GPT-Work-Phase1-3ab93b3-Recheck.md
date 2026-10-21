# GPT Work 补充审核 — Phase1 指定修复版本复核

**结论：发现阻断问题。** 首轮001–003已通过本轮补充复核；第二轮006–009在指定版本仍可复现，不能据“Phase1已完成核对”推定全部问题关闭。没有修改任何项目状态、源码、测试、Golden、锁或原审计报告。

## A. 审核对象、权限、范围

- 用户提供39位前缀：`3ab93b35c0b5e4e7b5e85c27f641748aa86cb24`。
- GitHub及已有修复工作副本唯一解析为40位提交：**`3ab93b35c0b5e4e7b5e85c27f641748aa86cb24f`**，提交说明为“docs: archive repair SDK CI and original ZIP verification evidence”。未任意补猜提交号。
- 仓库：[AQRP](https://github.com/wwooyy429/Alpha-Quant-Research-Platform-AQRP-)；[修复PR #4](https://github.com/wwooyy429/Alpha-Quant-Research-Platform-AQRP-/pull/4)，Draft/Open、未合并；base为`f579b2c99e762085772de6e70ba1fa98792a7add`。
- 本轮实际固定副本：`C:/Users/11638/AppData/Local/AQRP/reviews/p1-3ab93b3`，detached、运行前clean。阅读归档和验证产物均在本报告所在非同步审核目录；Windows应用解析路径见environment.json。
- 审核时间：2026-10-21，Asia/Shanghai；固定副本记录22:28:17+08:00，完成时间见末尾。
- 只读范围：修复授权与设计、源码/测试/CI/构建工具差异、46项新增语义回归、原始审查用例、80项证据清单、50项P0冻结资产、原始双平台ZIP及其GitHub元数据。
- 实际执行：审阅验证入口后，在独立副本由CPython3.13.16/x64/标准GIL新建venv，哈希锁安装、构建并安装0.1.1 wheel，运行原版完整SDK，再运行两轮未编辑的16项外置审查用例；校验CI原始ZIP及重放八表/查询。
- 本轮对源码/测试/工具/CI/构建/锁/扫描配置做Git核对，确认指定提交与业务锚点`cdb11cd913e965a43572ceb86efb0a39d1f618df`相同。旧CI依据这项受保护范围等价关系引用，不冒称它的完整tree等于新增资料提交。

**版本漂移已发现并分开：** PR #4当前head为`16083e151e3dadc11981c878f5aa90b7b09e9ac4`，比本轮目标多两个提交，包括`8902ba00a818150bf00af8d051a3837bc79e6bfc`的第二轮修复。当前head已改变time.py、pit.py、quality.py并新增第二轮测试。本轮没有把它当作指定版本运行；**本轮失败不能外推为16083e1仍失败，也不能用16083e1的234测试/16通过声明关闭3ab93b3的问题。**

## B. 授权及阶段边界

修复材料中有用户授权“核对、归档并修复，提交独立修复PR”的记录，允许的当时范围为三项首轮数据校验修复。固定提交内容与这一时序一致，没有把尚未进入该提交的后续修复说成已存在。

本轮仅履行补充审核和隔离验证，不发送其他对话消息、提交/推送、改PR、合并main、打标、发布或进入Phase2–7。“已完成核对”在本轮作为版本交接信息，**不是修复交付用户ACCEPTED/RELEASED或新增合并发布授权**。

既有Phase1发布历史与稳定标签保留；Phase2另分支未被本轮修改或业务复审。50个冻结P0文件hash、Golden四文件、requirements.lock、106条需求目录均未改变。完整Gemini SDK/ZIP独立执行缺口继续与开发方/CI/GPT Work证据分开登记。

## C. 按严重度排序的未关闭问题

沿用原ID，以下全部针对完整SHA **`3ab93b35c0b5e4e7b5e85c27f641748aa86cb24f`**。没有以“7个失败断言”虚增为7个不同缺陷。

### WORK-P1-006 — High — 未知历史可得性仍可进入正式PIT

- 类别：代码缺陷；需求DATA-002、DATA-006、DATA-009、QA-002。
- 位置：quality.py `validate_dataset`267–268行仅查available_at是否None；`normalize`111–113行及`validate_table`243行附近允许已有UNKNOWN_AVAILABILITY标记。[固定源码](C:/Users/11638/AppData/Local/Packages/OpenAI.Codex_2p2nqsd0c76g0/LocalCache/Local/AQRP/reviews/work-p1-recheck-3ab93b3/source/src/aqrp/data/quality.py:267)
- 复现：固定合法输入保留非空available_at，把bars_daily/master/calendar/membership首行改为UNKNOWN_AVAILABILITY。各自调用正式publish_snapshot。
- 预期：正式PIT拒绝未知可得性，exploratory只留原件；实际：四项断言均失败，发布未拒绝。此前复现的PIT_VERIFIED/正式查询穿透原因代码仍在。
- 影响/阻断：数据质量标记不能被一个声称的时间戳覆盖，正式PIT准入被绕过；**阻断技术完整通过**。
- 最小修复/复核：正式发布及读取对八表统一拒绝未知标记或缺available_at，保留exploratory身份；四负例/已知正例及正式SDK入口复核。新head是否满足须单独固定SHA验证。

### WORK-P1-007 — Medium — Windows文件路径可绕过IANA键

- 类别：代码缺陷；需求DATA-003、ENV-001、DATA-007、QA-002。
- 位置：time.py `iana`11–16行未改变。[固定源码](C:/Users/11638/AppData/Local/Packages/OpenAI.Codex_2p2nqsd0c76g0/LocalCache/Local/AQRP/reviews/work-p1-recheck-3ab93b3/source/src/aqrp/core/time.py:11)
- 输入/步骤：复制合法UTC TZif到独立tmp文件，把Windows绝对路径传给iana。
- 预期：只接受固定tzdata包内的IANA键；实际：未拒绝，原审查断言失败。第二轮已演示的外部文件改变导致同快照验证变化的根因仍存在；本轮未再重复该破坏性输入演示，仅运行受控路径反例。
- 影响/阻断：引入未封存的外部时区依赖，违反package-only和可复现性契约；**阻断该契约完整通过**，不等同于任意代码执行。
- 修复/复核：拒绝绝对路径/盘符/反斜杠并约束资源范围，合法IANA/DST/固定快照正向控制保留；针对修复新SHA复核。

### WORK-P1-008 — Medium — int64上溢仍抛裸OverflowError

- 类别：代码缺陷；需求DATA-006、QA-002。
- 位置：quality.py `normalize`60–62行无int64上界；`validate_table`250行在逐行捕获范围外构建Arrow表。[固定源码](C:/Users/11638/AppData/Local/Packages/OpenAI.Codex_2p2nqsd0c76g0/LocalCache/Local/AQRP/reviews/work-p1-recheck-3ab93b3/source/src/aqrp/data/quality.py:250)
- 输入/步骤：合法bar设置revision_id=2**63，调用validate_table。
- 预期：QualityReport input=1/rejected=1、字段原因清楚；实际：裸OverflowError，未形成报告，原断言失败；2**63-1正例通过。
- 影响：异常输入中断整批分类，计数守恒证据缺失；不据此推定正常价格计算错误，但质量错误语义尚未满足。
- 修复/复核：按Arrow位宽在规范化阶段拒绝越界并归类，不吞异常返回空成功表；上下界/类型/计数守恒在新SHA验证。

### WORK-P1-009 — Medium — 纳秒精度仍可被第二小数段绕过

- 类别：代码缺陷；需求DATA-002、DATA-003、QA-002。
- 位置：time.py `utc`24–30行未改变。[固定源码](C:/Users/11638/AppData/Local/Packages/OpenAI.Codex_2p2nqsd0c76g0/LocalCache/Local/AQRP/reviews/work-p1-recheck-3ab93b3/source/src/aqrp/core/time.py:24)
- 输入/步骤：utc('2024-01-02T16:00:00.000000+00:00:00.000000001')。
- 预期：无法用微秒精确表示应明确拒绝；实际：未抛TimestampResolutionError，原断言失败。
- 影响/阻断：只检查第一段小数允许后续offset精度被datetime截断；**阻断时间精度要求完整通过**，不外推普通微秒输入错误。
- 修复/复核：校验完整timestamp/offset语法及所有非零纳秒尾数，合法微秒/零尾数/DST行为保持；在修复新SHA复核。

### WORK-P1-004 — Medium — 指定Gemini执行证据仍未完成

类别为证据缺口，关联QA-002、ENV-001、ENV-002。位置：本版本`docs/audits/phase-1/repairs/data-validation/DEVELOPER_RESPONSE.md`的004行及EXECUTION_EVIDENCE.md剩余条件明确保留OPEN。

预期为指定角色在固定SHA的真实SDK/ZIP命令、解释器、原始日志及产物；实际没有新增此类Gemini执行原件。新开发方执行、CI及本轮GPT Work不能代签。此项不证明业务计算错误，但阻断“Gemini专项完整完成”的声明；由指定角色补证或用户另行决定，本轮不代作豁免。

## D. 已修复问题与需求追踪

| 问题 | 实现/需求 | 本轮结果及限定状态 |
|---|---|---|
| 001 / High | quality.normalize148–163；DATA-001/006/011、QA-002 | 字段单位集合及目标股数增量检查存在；原2项负例通过；合法share/lot/currency换算、null单位、边界覆盖在46项新增语义用例中。**本轮GPT Work复核通过，非Gemini全局关闭。** |
| 002 / High | validate_action_sessions196–218；DATA-002/004/006、QA-002 | 按证券市场日历及源IANA解释ex-date，拒绝未知/歧义ex-session及不支持隔夜行动，检查effective不晚于收盘；原冲突日期反例通过，正常100→98+2、晚到修订、本地/UTC错日边界通过。**本轮复核通过。** |
| 003 / Medium | quality.normalize138–146；DATA-006、QA-002 | 已知OHLC五组关系逐对验证；原部分缺失矛盾反例通过，全部16种合法缺失掩码/质量计数测试通过。**本轮复核通过。** |
| 005 / Medium证据 | CI上传32行起、ci.py上传选择；ENV-001/002、QA-002 | 两份原始业务CI ZIP各23选定文件hash、12上传根文件、实际wheel/.coverage、八表及查询回放通过；新上传策略补证已核实。**历史CI缺字节仍NOT VERIFIED，不能完全关闭历史限制。** |
| DATA-003/007/009 | time及正式PIT/资源边界 | 006/007/009仍OPEN，已有DST/快照/mutation通过不能替代本轮反例 |
| DATA-005/008 | 历史成员/存储与回放 | 148套件正常历史查询/存储案例通过，但成员未知标记准入属于006 |
| ENV-001/002、SEC-002 | 精确环境、CI、扫描 | 全量SDK固定安装/环境/覆盖率/扫描正负控制通过；不因此关闭上述语义缺陷或Gemini角色要求 |

保留14项Phase1需求范围，没有新因子、研究、组合、账本、CLI/网页能力。没有改Golden答案、容差或依赖锁来消除失败。

## E. 实际验证、原始证据与限制

| 项目 | 实际结果 |
|---|---|
| 本轮完整SDK | **148测试/0失败/0错误/0跳过，exit0，complete=true**；run_id `aqrp-693e8864-c8ff-4369-86c3-defabf81dffd`；目标3ab93b35c0b5e4e7b5e85c27f641748aa86cb24f、dirty=false |
| 解释器/包 | CPython3.13.16/x64/标准GIL，锁定安装+pip check，构建/安装aqrp0.1.1；17个安装模块与目标源逐字节匹配 |
| 本轮wheel | `d99d7ffc508db253c85459cea40a7b1a1813bea937f14e3f32df15dd56e9510d`；本轮新构建，不冒充原CI字节 |
| 额外原始审查用例 | **16项，7失败/9通过，exit1**；四个006参数用例+007/008/009失败，共4个缺陷。首轮6项均通过，第二轮其余3项正控通过；脚本未编辑、hash已记录 |
| 修复资料及冻结资产 | 80项修复证据hash、50项P0冻结文件匹配；Golden四文件、锁和需求CSV与已发布基线字节相同 |
| 当前目标CI | GitHub run39613355124，Windows job119267773049/Ubuntu job119267772505均success；本轮仅核对该run API，不冒称下载其ZIP |
| 实际核验CI原件 | 业务run39612329694/attempt1：Windows12351655951、Ubuntu12350412606；各148/0/0/0；保留其业务SHA和checkout SHA，不混写当前目标 |
| Git等价 | 业务CI checkout ccf0e9f1861a83a6995be10149239737a85214ec，父为main f579及业务cdb11cd，tree等于业务tree；业务→指定目标保护范围diff为空 |
| ZIP核验 | Windows SHA256 098ad1a3ecebfe8e71fee739d7b116fdd75631e4d8a5148e1c6a84a6887fae35；Ubuntu 54e013322b660832d3707097513306fe6f7a0502d83c69800490e506916b236b；与GitHub官方digest/字节数一致 |
| ZIP内部 | CRC/路径/链接/重复/体积检查；23选定文件及12上传根文件hash、实际wheel及模块、原coverage数据库、JUnit/覆盖门禁、八表/Manifest/查询重放通过。两工具明确省略；同run跨OS逻辑数据/结果/固定配置一致 |

原始日志与JSON快捷入口：

- [16项原始失败日志](C:/Users/11638/AppData/Local/Packages/OpenAI.Codex_2p2nqsd0c76g0/LocalCache/Local/AQRP/reviews/work-p1-recheck-3ab93b3/original16-regression.log) / [JUnit](C:/Users/11638/AppData/Local/Packages/OpenAI.Codex_2p2nqsd0c76g0/LocalCache/Local/AQRP/reviews/work-p1-recheck-3ab93b3/original16-junit.xml)
- [本轮环境与测试汇总](C:/Users/11638/AppData/Local/Packages/OpenAI.Codex_2p2nqsd0c76g0/LocalCache/Local/AQRP/reviews/work-p1-recheck-3ab93b3/verification-summary.json)
- [完整SDK命令输出](C:/Users/11638/AppData/Local/Packages/OpenAI.Codex_2p2nqsd0c76g0/LocalCache/Local/AQRP/reviews/work-p1-recheck-3ab93b3/runs/aqrp-693e8864-c8ff-4369-86c3-defabf81dffd/commands.log) / [环境原件](C:/Users/11638/AppData/Local/Packages/OpenAI.Codex_2p2nqsd0c76g0/LocalCache/Local/AQRP/reviews/work-p1-recheck-3ab93b3/runs/aqrp-693e8864-c8ff-4369-86c3-defabf81dffd/environment.json)
- [双平台ZIP实际校验](C:/Users/11638/AppData/Local/Packages/OpenAI.Codex_2p2nqsd0c76g0/LocalCache/Local/AQRP/reviews/work-p1-recheck-3ab93b3/zip-verification.json)
- [SHA及保护文件核对](C:/Users/11638/AppData/Local/Packages/OpenAI.Codex_2p2nqsd0c76g0/LocalCache/Local/AQRP/reviews/work-p1-recheck-3ab93b3/facts.json)
- [PR当前版本快照](C:/Users/11638/AppData/Local/Packages/OpenAI.Codex_2p2nqsd0c76g0/LocalCache/Local/AQRP/reviews/work-p1-recheck-3ab93b3/github-pr4.json)

NOT VERIFIED：更晚16083e1/8902ba0的代码修复效果与234测试声明；完整Gemini SDK/ZIP执行；历史旧CI未上传字节；本轮新Linux独立安装（Linux只核验既有CI原件）；修复交付用户验收及发布授权。本轮失败日志全部保留，无删除/改期望/改阈值。

## F. 给Codex的复核任务单

1. 001–003可以登记“指定3ab93b3经GPT Work补充复核通过”，保留Gemini及用户关卡，不冒充全阶段验收。
2. 006–009在指定旧SHA维持OPEN；现在已有更晚修复提交，**无需为了该旧版本重复开发**，应交付当前修复的完整40位SHA、base及001–009处置矩阵，在另一轮固定新SHA验证。
3. 新SHA复核应至少包含未编辑16项原始审查用例全部满足预期、各新增语义测试、全量安装SDK及Windows/Linux CI的真实run/attempt/head/checkout、wheel/覆盖率/八表hash和原始失败记录。不得把新SHA的通过回填为本轮旧SHA通过。
4. 005保留新证据策略通过与历史缺字节两个状态；004由指定Gemini补真实执行或用户另行裁定，GPT Work不能代签。
5. 不修改稳定标签、历史原报告/正确Golden，不据本轮报告合并发布或自动纳入Phase2；本轮未向其他对话发送任务，由用户转交。

**补充审核最终选择：发现阻断问题。仅对3ab93b35c0b5e4e7b5e85c27f641748aa86cb24f及上述范围有效，不代表Gemini通过、用户验收或发布授权。**

报告时间：2026-10-21T22:35:08.447097+08:00（Asia/Shanghai）。
