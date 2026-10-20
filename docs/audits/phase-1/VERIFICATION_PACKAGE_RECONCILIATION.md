# Phase1补充验证包接收与证据等级更新

2026-10-21（Asia/Shanghai）。用户提供补充文件，沿用正在进行的Phase1审查归档/PR #2更新授权；不合并、不打标签、不进入Phase2。包内报告/脚本是审查材料，不是新的验收、发布或执行授权。

## 原包与内容

源文件为用户Downloads目录的aqrp_phase1_verification_package (1).zip，33832字节、10个成员。原字节归档为gemini/verification-package-8bf189d/aqrp_phase1_verification_package.zip，SHA-256：

`318323ff77651537cc47470fe20d32930bb07495bb51fd71f0772f80c11c023d`

这个hash只核对补充包，不能代替两个GitHub Actions原始ZIP的hash验证。包内4条hash清单均与成员实际字节/大小匹配；完整10成员清单与原件引用在gemini/VERIFICATION_PACKAGE_INDEX.json。安全检查路径、重复成员、链接、CRC及展开大小后处理，未修改用户原ZIP或删除Downloads副本。

新增原始资料为：
- aqrp_phase1_recheck_execution.py（4034字节，fdfedf7e5330f8f7d7555f9f4a9f13a196b597bf395e07dc1dc971454ee5a560）
- aqrp_phase1_recheck_execution.log（2417字节，a39e0845cd7ea6f934180a53b14075dcb91adaf29d9da1b12add2d748983439a）
- aqrp_phase1_recheck_hash_manifest.json
- aqrp_phase1_sdk_hash_incremental_recheck_evidence.json

以上四份在归档目录contents中可直接查看，保持原字节。包内四个与现有归档完全相同的旧报告/数学文件仍保存在完整原ZIP中，并引用既有规范原件，不用重复文件替代新证据。

## 报告副本与版本关系

包内增量报告SHA256为`49447c478c8524b45ca08676b817539810675df032061f4e791cdfc85a85a17b`，15110字节；此前独立提交的规范原件SHA256仍`725557d5ff2fc1c94d03c614bf7e40706f33aa0422c6b44f80289806b2e69cf0`，15246字节。精确比较确认内容差异仅为3个Google搜索包装链接改成直接GitHub链接；二者分别保留，不覆盖历史原件。

包内早期勘误确认副本SHA256为`def0b8b149e520bba1e8d78a6adc1af9c178cf515c038a3bc4e09ce371bcdcc1`，既存规范原件仍`9eccef880347de87ea7256ebf2ae4c4cc0121912f6492ddb32d3ab2117918c18`。差异为Markdown排版、列表/分隔及公式加粗，不形成新的业务裁决；保留两个版本及完整差异文件。

本包仍针对Gemini固定审查8bf189d76f15273a89eb4c2672c86e05a81aa148、业务74bdb9216c585d27de91123605aff0266ca028cc，不扩展为Gemini已审本轮新增归档Commit。七项AGREE及技术咨询PASS不变；此前清单名称、缺项层级、浮点误差等勘误继续以SDK_HASH_INCREMENTAL_RECONCILIATION.md为准，本包没有修正这些原文细节。

## 新脚本和日志实际支持的范围

**旧报告和五份证据hash的审查方脚本/日志现已提供。** 这补齐了此前“尚未附送脚本/原始日志”的一部分资料缺口；旧记录描述的是收到本包之前的状态，不能继续把当前说成没有任何附送执行材料。

源码核对：
1. 本地读取旧SDK/hash报告及五份证据，在文件存在时实际计算SHA-256并断言；所列期望值与仓库原件一致，提供的日志列出六个MATCH。
2. Git运行/父提交/tree均写在字典或字符串中直接打印，没有Git调用、对象读取、网络查询或树比较。不能把该段输出登记为脚本独立验证了Git拓扑。开发方此前实际Git核对仍是另一证据来源。
3. 七项AGREE也是固定文本输出，作为审查方裁定记录，不是七项功能测试。
4. 没有读取/解压12288989083.zip或12288679676.zip，没有遍历其artifacts.json、Parquet或跨OS结果；没有导入AQRP、运行tools/ci.py、pytest或安装3.13.16。日志环境是Linux Python3.11.2，不能补齐目标SDK执行。
5. 输入不存在时只是打印MISSING或not found，仍正常结束并输出“ALL ASSERTIONS PASSED”。因此单独exit0/成功页脚不能证明全部输入存在和验证完成；不修改原脚本掩盖这一限制。

本包实际只含五份输入中的数学脚本与数学日志，缺env_probe.log、remote_download_attempt.log、task_status_matrix.json；三份规范原件在仓库中已有且hash一致。日志可能来自审查方原先完整工作目录，不能因包内没这3个文件断言原日志虚假；也不能称补充包自身已经包含完整六个hash输入。

## 开发方受控复跑

审查源码后，在外部临时目录使用CPython3.13.16做三次受控复跑，只在内存AST中把out_dir指向测试输入目录，原脚本和原包不修改。没有修改平台输出或伪装原Linux3.11环境；全部明确属于开发方复现。

| 输入目录 | 实际输出 / 退出码 | 含义 |
|---|---|---|
| 原包所含文件 | 旧报告和2个数学文件匹配，3个MISSING；exit0 | 证明原包单独运行并非五份输入全验证 |
| 加入仓库已有3个规范原件 | 六个目标hash均匹配；exit0 | 复现脚本的文件hash计算范围，不证明原始执行来源或SDK正确性 |
| 空目录负向对照 | 旧报告不存在、5个MISSING；exit0并打印成功页脚 | 确认缺失输入未导致失败，不能把页脚当完整验证证明 |

检查、复跑stdout/stderr、重定向包装器、变体差异与执行回执见implementation/verification-package-52ab650/。此前52ab650的233项文件hash在本轮更新前全部匹配，50份P0冻结资产及src/tests/tools/CI/依赖锁/Golden未变。本轮未重跑SDK或102项业务测试；既有CI/SDK冒烟不改变执行归属。

## 当前证据等级与未闭环条件

| 项目 | 接收本包后的当前状态 |
|---|---|
| 七项勘误处理认可 | Gemini AGREE，有报告及新增裁定JSON；不等于实际测试全部完成 |
| 旧报告/5证据文件hash | REVIEWER-SUPPLIED SCRIPT AND LOG RECEIVED；输入hash可核、开发方完整输入受控复跑匹配；原审查环境未另行认证 |
| Git拓扑 | 新脚本只打印常量，不能提供新的Git执行证明；此前开发方Git对象核对保留 |
| 审查方Actions原始ZIP重算/内部数据/跨OS实际执行 | 本包未增加对应代码、命令或日志，仍NOT VERIFIED |
| 审查方完整CPython3.13.16 SDK入口 | 仍NOT RUN / NOT VERIFIED，不能用3.11文件hash脚本替代 |
| 用户验收/限制接受/发布/Phase2授权 | 均未发生；本包元数据也明确NOT ACCEPTED、UNMERGED、NOT RELEASED、Phase2 BLOCKED |

P1-SDK-EXEC-OPEN仍需独立执行证据补齐或用户明确决定接受限制。之后仍需用户Phase1人工验收、分别授权main合并/标签、最终main范围/适用检查/追溯与稳定基线核验；Phase2单独启动授权不可省略。原辅助字节未上传限制、PRE-002 MITIGATED及此前报告勘误保持披露。

停止于归档与PR #2审查记录更新。main仍502c6931dcfce50bee2f71a80524475fae6396bf，phase0-baseline目标7de1d0e81385ae97f98ea673fe05dd726f0b577b保持不动，无phase1-baseline；本次不合并、不打标签、不进入Phase2。
