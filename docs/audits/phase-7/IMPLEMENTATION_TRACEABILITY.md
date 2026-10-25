<!-- Phase7 G2 repair candidate 001/002 -->
当前固定旧版本 ec6bfcedc0c424b6fa3e817c9a094385bd971d6f 的独立 G2 为 BLOCKED，001 Medium blocking、002 High 均 OPEN。0.7.0.dev2 仅为两项修复候选；原报告在 g2-ec6bfce/，范围、原始反例与开发验证分层见 repairs-g2-001-002/。新已提交完整40位SHA的完整SDK、双系统原包、真实浏览器及独立G2必须重新核实；不得沿用ec6通过数。开发自测不关闭发现，main/旧标签与全部延期和操作限制保持。以下原轮记录按时点保留。

# P7 五项实现与证据映射

原需求目录106项、原业务分类和G1五项范围保持，未新增真实数据、实盘或正式Test范围。以下是开发方实现定位，实际通过数以固定SHA命令/日志为准；G2仍待GPT Work。

| 原需求 | 级别 | 实现/验证位置 |
|---|---|---|
| INT-003 | MVP | 原FactorRegistry/Candidate/Strategy状态门禁全部回归；新共同authority与Task可信归属；original_replay_smoke原0.2三Ref与published runs；released_p6_smoke原P6源码/wheel/锁/checker及四Ref实际执行；独立root/旧包边界 |
| INT-004 | MVP | tools/ci.py新干净wheel SDK、完整pytest及覆盖；原P1–P6 reference/smoke；e2e_smoke SDK/旧CLI/TaskCLI/AppTest/真实浏览器一致；IMPLEMENTATION_MANUAL和原六页面手册；原始证据精确选集 |
| INT-005 | MVP | tools/e2e_smoke.py完整19研究/10执行、Momentum/Reversal替换、12单位同根控制；e2e_reference原冻结独立答案与真实血缘/金融对账；预算并发/取消/恢复/篡改与缺项负例 |
| DATA-013 | Competition Ready | competition.adapter完整P1八表/sidecar/catalog/来源和规则恒等映射、能力清单；tests/competition正负例与competition_smoke实际同核执行链接 |
| INT-006 | Competition Ready | adapter-spec/capabilities/freeze/submit/result均薄调度原服务；缺失/冲突/未知真实赛事明确不可执行；完整实际输入、请求、终态和哈希证据 |

交叉质量：experiments/admission.py、ledger、Task状态/归属及Research服务保留95%行/90%分支门槛；适配器至少现行90/85，其余原门槛不降低。原5016保护文件、G1设计/答案和原P6检查器逐字节核对，新模块/源码/安装wheel/RECORD成员集合精确一致。

源码/测试的最终精确路径、包内全部Python模块及字节见 IMPLEMENTATION_ALLOWED_PATHS / IMPLEMENTATION_IDENTITY。固定SHA、实际日志、环境、双OS官方ZIP身份/摘要/CRC/成员和真实浏览器收据在PR #10外部封存索引定位，不以本表宣称独立通过。
