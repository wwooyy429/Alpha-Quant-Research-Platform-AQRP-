# Phase2 数学脚本/日志补充接收与核对

最新增量：修订数学源/日志与增量报告已收到，Volume/证券B/非零误差核心问题核对通过；本文件以下旧版缺陷或“未收到”表述按历史时点解释，不代表当前仍未修。Gemini十二项均标AGREE/CLOSED，但部分解释仍与真实标题/需求职责/路径冲突，最新事实及执行限制见MATH_INCREMENTAL_RECONCILIATION.md和gemini/MATH_INCREMENTAL_INDEX.json；尚未人工验收/发布。

用户在前轮实现报告核对后提供aqrp_phase2_math_verification.py及.log，并答复“已提供”。两文件已按原字节归档，未改写、未更名冒充其他原件。当前固定入站PR head为79c91e4bf7b4341c810705a00648283e80ab805a；本次只是补充接收，不能倒填此前提交已经包含这些文件。

| 文件 | 原始来源 | bytes | SHA256 |
|---|---|---:|---|
| aqrp_phase2_math_verification.py | B:\BaiduSyncdisk\学习\投资\量化\量化交易比赛\审查\aqrp_phase2_math_verification.py | 3760 | 88637a72c494abb4893d9312e974c2057a0fa28bef84fbeb1e5328c96fe1729e |
| aqrp_phase2_math_verification.log | B:\迅雷下载\aqrp_phase2_math_verification.log | 1022 | e64db0afd63779d39f2f1398117687ba0c9ccbda544fb209769eb024a011946e |

原件位于gemini/math-supplement/，接收索引gemini/MATH_SUPPLEMENT_INDEX.json。本轮开发方复跑/校核位于math-supplement/，不能混称Gemini本次新执行。此前PRE_REVIEW_INDEX和IMPLEMENTATION_AUDIT_INDEX的缺件字段是各自接收时点的历史快照，当前接收事实以本补充索引为准。

## 实际验证与证据边界

完整阅读源文件后确认仅sys、decimal、fractions和算术/print/assert，无网络、文件访问或动态执行。开发方使用CPython3.13.16以-I -S在仓库外目录复跑原字节，退出0、stderr空；stdout与用户日志只统一CRLF/LF和末尾换行后一致。原日志原字节保留，归档不做统一换行处理。实际参数、环境、执行输出/hash和run_id见math-supplement/checks.json。

复跑相符只证明该脚本可复现相同输出，不能证明历史作者/时间/原运行环境。源文件标题明确自述“Plan Pre-Review”，未绑定任何完整代码SHA、数据/输入文件hash或不可变run配置；它不读取AQRP、不执行SDK、不读取ZIP、不计算任何文件hash、不请求GitHub元数据。故“旧预审同名原始两文件已收到”可关闭接收缺件；不能把它们改称aqrp_phase2_implementation_math_and_hash_audit.py/.log，或把实现报告所称新数学/hash执行证据一并标已匹配。

## 核对发现

| 项 | 源文件实际行为 | 处理与结论 |
|---|---|---|
| MATH-SUP-001 Volume公式/输入 | 历史量[1000,2000,3000,4000,5000]均量3000，当期1800，算1800/3000=3/5，漏掉正式公式-1；注释仍有Cross-sectional Quantile | 同输入正式Volume应3/5-1=-2/5=-0.4。正式G-P2-A是[100,150,200]、L2，200/125-1=3/5=0.6。相同输出常量来自不同公式/输入，不能证明正确因子验证。原件不改，需Gemini出具绑定正确公式/输入的新修订证据。业务与Golden正确，不迎合错误脚本改答案。 |
| MATH-SUP-002 证券B | 将[-1/5,1/5,0]直接转float并和相同常量列表比较，没有从价格/量计算 | 这不是多期收益序列的独立推导。冻结G-P2-B价格[200,180,160]、量[40,60,50]应分别推导momentum=-1/5、reversal=1/5、volume=0；开发方另以Fraction实际推导匹配，不冒充Gemini补测。 |
| MATH-SUP-003 零误差/容差 | abs差是相同float表示比较，relative差直接打印常量0，没有实际相对误差计算或断言 | 同float相等成立；相对精确有理数，±0.21误差7.771561172376097e-18，0.6误差2.2204460492503132e-17。容差abs1e-12/rel1e-10不变，不能把脚本“0”解读为实数误差0或已实际检查两种容差。 |
| MATH-SUP-004 验证范围 | Momentum/Reversal从100和121推导；拆股仅核价格；分红比较纯价格与总回报；末行总报6项PASS | 可以支持其中显式算术的有限范围，不能证明数据PIT、分证券窗口/缺失/边界/性质、Signal血缘、Registry、准入或SDK正确。“ALL6”是脚本自述，不等于完整Golden/业务测试通过。 |
| MATH-SUP-005 新报告文件身份 | 此文件名/标题为旧预审数学脚本，不含任何hash/ZIP代码；实现报告另称新implementation_math_and_hash_audit文件 | 记录用户已交数学两原件，不否认接收；新实现数学/hash证据身份与实际执行范围仍需Gemini澄清。无运行命令/版本/SHA的原始提供日志不能替其证明完整实现或远端hash执行。 |

开发方独立正确公式核算、精确浮点误差及原脚本复跑都保存在checks.json和开发方stdout/stderr，出处清晰。原脚本返回0的事实与其不适合作为正式Volume验证的结论同时保留，不隐去失败语义、不修改原件使其“正确”。

## 更新后的闭环状态

- CLOSED（接收事实）：旧预审所命名数学.py/.log现在确已收到，按本次时间归档；不倒改以前未收到的事实。
- PARTIAL：原脚本算术可复跑且日志相符；Volume与证券B独立推导、精度口径等仍需修订，不能宣告六项正确业务Golden全部独立通过。
- OPEN：12项实现报告勘误待Gemini确认；上述脚本问题需新修订证据；实现报告“新数学/hash脚本”与实际交付的对应关系、ZIP/远端hash独立执行原始记录仍待澄清。
- NOT VERIFIED：Gemini在规定CPython3.13.16上的完整SDK独立执行；本轮仅开发方标准库复跑，不能补记为该SDK执行。原开发方/CI 254项通过保持。
- 用户未人工验收或明确接受独立执行限制；合并、标签、main基线发布/核验以及Phase3独立启动均未授权完成。不合并、不打标签、不进入Phase3。

本轮不改src/tests/tools/CI/包配置/锁/正确Golden/审查报告原件，不自封Gemini新结论；当前仍AUDIT PASS AS REPORTED / REPORT ERRATA AND EXECUTION EVIDENCE OPEN。
