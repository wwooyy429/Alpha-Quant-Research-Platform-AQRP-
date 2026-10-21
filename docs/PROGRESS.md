# 当前真实项目状态

2026-10-21 第二轮补充审查：报告目标是已发布 f579，不是 PR #4。开发方在上一修复 SDK 复现新增 WORK-P1-006–009（16 项外置用例 7 失败/9 通过，旧三项回归保持通过）；现于同一独立修复 PR 按既有 Phase1 数据契约纠正，源代码全套 234 项通过，新的完整 SDK/CI/独立复核待补。详情 docs/audits/phase-1/repairs/data-validation/round2/。修复版本尚未验收/发布；main、稳定标签和 Phase2 分支不变，不合并、不打标签、不进入Phase3。以下各轮数字/状态保留其时点。

2026-10-21 补充审查修复状态：用户已明确授权“核对、归档并修复，提交独立修复 PR（推荐）”。独立分支 fix/phase-1-data-validation 从已发布 main f579b2c99e762085772de6e70ba1fa98792a7add 起步；三项数据校验缺陷已实现并通过开发方验证，固定 SHA 独立复核待完成，候选版本 0.1.1，尚未验收/发布。原 Phase1 ACCEPTED/RELEASED 历史与标签不变。Phase2 已在另一分支获授权并实施（PR #3，核对头部 947467b9d094905cab0af37ec5cc53f1d187e755），但继承的数据层缺陷须在修复经审查、纳入后重新验证，当前不能给予正常技术通过。该分支不修改 Phase2，不合并、不打标签、不进入 Phase3。最新记录见 docs/audits/phase-1/repairs/data-validation/；以下旧状态为历史，若冲突以本段和实际 Git 为准。

2026-10-21 最新发布状态：**Phase1 ACCEPTED / RELEASED**。用户已分别完成验收并授权“请开始合并并打标签”；PR #2已合并（9b843b17ccf362cf5b7a5351269559a627c55b32），稳定标签phase1-baseline指向含发布登记的main版本，远端原子发布后核验生效。原话和合并/SDK证据见docs/audits/phase-1/publication/；基线见docs/audits/phase-1/BASELINE.md。Gemini独立执行及旧远端缺字节事实保留，未声称新增Gemini审查。Phase2尚未授权，不自动启动。

以下既有未合并/未发布/未授权文字为之前各轮历史，当前以本次发布登记和实际Git核验为准。

2026-10-21 最新人工决定：用户明确表示“phase 1验收已完成”，现登记 **Phase1 = ACCEPTED，尚未 RELEASED**。验收对应接收时PR #2的71cc044d5f4e2079426049c0f7c6f747fee01692（业务74bdb92），原话与范围见 docs/audits/phase-1/acceptance/ACCEPTANCE.json。此前“等待验收/未ACCEPTED”仅为历史；Gemini独立执行和原远端缺字节事实继续保留，本次未伪造逐项限制豁免。合并main、打标签及Phase2均未授权。

以下既有状态段落保留为各轮历史，当前人工验收状态以上述记录为准。

2026-10-21 最新本地验证：已按用户授权配置 Conda aqrp-p1（CPython3.13.16）和独立 VS Code 工作区；完整 SDK、Conda 直接运行的同一组102测试、两份 Actions 原始ZIP/八表/SDK回放均通过。实际命令配置与原始日志见 docs/audits/phase-1/implementation/conda-vscode-74bdb92/README.md。执行者为 Codex 开发方，不能补记为 Gemini 独立执行；远端3项根文件及项目wheel原字节缺口、独立执行/人工验收/发布门禁保留。未合并、未打标签、不进入Phase2。


最新补充：用户提供10成员验证包，外包SHA256为318323ff77651537cc47470fe20d32930bb07495bb51fd71f0772f80c11c023d。Gemini旧文件hash脚本/日志现已附送，六个输入hash在完整输入复跑中一致；包自身缺三份输入，脚本缺文件仍返回0，Git/七项裁定为常量输出，未运行Actions ZIP或SDK。完整独立执行仍NOT VERIFIED，用户未接受限制/验收/发布；不合并、不打标签、不进入Phase2。最新索引audits/phase-1/gemini/VERIFICATION_PACKAGE_INDEX.json及核对audits/phase-1/VERIFICATION_PACKAGE_RECONCILIATION.md；当前清单implementation/VERIFICATION_PACKAGE_MANIFEST.json。以下旧轮“未附新记录”等为接收本包前的状态，不是当前没有脚本日志。

2026-10-21（Asia/Shanghai）。**Phase1技术审查建议PASS，Gemini已明确认可七项SDK/hash勘误；完整专项独立执行仍NOT VERIFIED，等待人工验收。** 用户未接受执行限制、未ACCEPTED/RELEASED；PR #2继续Draft/Open，不合并、不打标签、不进入Phase2。

Phase0已RELEASED。main仍502c6931dcfce50bee2f71a80524475fae6396bf；phase0-baseline目标7de1d0e81385ae97f98ea673fe05dd726f0b577b、对象0b2230cd4861ca3b47fa30fc30dae9f4dc4109d0保持不变，无phase1-baseline。

最新Gemini增量报告固定审查8bf189d76f15273a89eb4c2672c86e05a81aa148，业务锚点74bdb9216c585d27de91123605aff0266ca028cc，原报告SHA256为725557d5ff2fc1c94d03c614bf7e40706f33aa0422c6b44f80289806b2e69cf0，原字节已归档。接收索引audits/phase-1/gemini/SDK_HASH_INCREMENTAL_INDEX.json，逐项确认/新报告细节更正/剩余门禁见audits/phase-1/SDK_HASH_INCREMENTAL_RECONCILIATION.md；旧报告与索引保持历史来源。

七项AGREE仅关闭相应说明/处理意见争议，不关闭实际执行缺口。增量报告自述旧报告及5文件hash复算，ZIP列MATCH，但本次未附新脚本/命令/输出；SDK全量执行仍明确未做，ZIP/内部数据/跨OS独立执行方法尚无新原始记录支撑。不能用技术PASS、静态阅读或开发方结果追认Gemini实际运行。

开发方本轮再次核对两个原始ZIP、14条根清单中的11个可用文件、Manifest及每平台8表文件hash、smoke原字节、JUnit及Git树，通过；8bf189d清单223个hash在更新前全匹配。原ZIP/SDK回放/新冒烟资料仍在implementation/sdk-hash-74bdb92/，本轮检查在implementation/sdk-hash-incremental-8bf189d/。未重跑SDK/全量102测试，不改变其既有真实CI及上轮执行事实。

新报告文件名/11条列表、根清单3缺项与项目wheel单独缺失、0.05实数误差应为约2.7756e-18、配置比较未排除固定as_of、变更范围及本地执行归属等已独立注明，不修改原件，不改正确答案/容差。三个未上传根文件及项目wheel原始字节仍不可复算；Gemini对其非阻断意见不等于用户接受限制。

14项Phase1实现/102项测试的实际映射和来源保留。src/tests/tools/CI/依赖锁/Golden及50份P0冻结文件不变，106项/16组目录不变。本轮当前文件清单为implementation/SDK_HASH_INCREMENTAL_MANIFEST.json，旧清单属于各固定SHA历史快照。F-002/F-003/PRE-001/PRE-003限定范围CLOSED；PRE-002仍MITIGATED，原Baidu源码/锁/未提交内容未重置或自动迁移。

停止于审查记录更新。尚需独立执行补齐或用户明确接受限制、用户阶段验收、分别授权合并/标签、最终主干内容及检查/追溯和稳定基线核验；Phase2须单独启动授权。任何报告建议均不代替这些决定。
