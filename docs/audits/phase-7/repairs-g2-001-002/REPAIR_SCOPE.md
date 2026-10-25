# Phase7 G2 001 / 002 修复候选范围

原独立审查对象为 ec6bfcedc0c424b6fa3e817c9a094385bd971d6f，结论 G2 BLOCKED。原件、反例和逐字节接收核验保留于 ../g2-ec6bfce/；该审查结论不因开发方修复候选而改写。

## 受限实现

- WORK-P7-G2-001：受管研究从已验证共同 authority 的 ADMISSION 提交顺序取得当前准入之前、同数据且实际扣额的跨家族历史。它包含 R 前取消或失败、尚无 TRIAL 的消耗；不是从调用方 TaskContext 或仅从 TRIAL 投影推断。原家族预算、幂等、repeat_of、失败/取消不退款规则保留。TRIAL 增加 admission_history 审计字段，原污染字段与已有研究访问历史合并，原已冻结 TRIAL 不回写。
- WORK-P7-G2-002：迁移按实际 P5 / P5_REPLAY 子运行及可信 source 核对物理财务前缀与事务原字节，不以父 Task 的 SUCCEEDED / FAILED / CANCELLED 决定是否检查。已认证的原 FAILED / 未知财务结果保留不透明失败语义，不给出账户认证；不能通过伪装未知结果携带现金或替换后来的损坏。迁移清单明确记录前缀是否获验证。

版本为 0.7.0.dev2。因子算法及语义版本 1.2.1 未改变；生产包 hash 随已授权服务修复和版本元数据变化，形成不同完整 FactorRef。工程代码收据限 TEST_ONLY / financial NONE，不构成独立 G2 或金融批准。没有修改金融数学内核、Golden、依赖锁、原 106 需求和五项定义，302 原设计与 5016 保护文件保持原字节。

## 验证和后续门禁

新增两个针对性回归文件，对照真实公开入口与真实金融提交；期望来自独立原反例和既有契约，不用待测函数生成答案。开发方 RED / GREEN 原始命令、输出、环境及快照与原主审证据分列。新完整安装 SDK、双系统官方 CI 原始 ZIP、适用真实浏览器/完整协议必须绑定修复后的完整40位 SHA；旧 ec6 的通过数不能认证新候选。实际完成后通过 PR #10 唯一 AQRP_FIXED_REVIEW_SHA 和外部不可变证据索引交 GPT Work 独立复核。

001 / 002 均保持 OPEN — FIX CANDIDATE / PENDING INDEPENDENT VERIFICATION，不能由开发方自行关闭。未 ACCEPTED / RELEASED；不合并、不打标签、不部署、不实盘、不运行正式 Test、不授予金融批准。WI-R2-001 / 002 和真实隔离继续 DEFERRED / NOT VERIFIED，原历史宿主边界保留；正式入口继续失败关闭。

## Received audit scan provenance

The byte-exact incoming reports produced 12 generic-api-key matches in the original failed precommit scan. A stdlib-only reconstruction proved all seven distinct values: five public synthetic configuration SHA256 identifiers and two deterministic local ledger/run identifiers. The original failed logs, original 32 archived files, parent policy and scanner binary pins remain unchanged. scan-policy/PROOF.json, seven canonical preimages and recompute.py make the proof reproducible. Seven added exceptions each require the exact full public value, its exact original report path and the generic-api-key rule together. All original 17 controls remain; 56 additional actual scanner controls and the complete source scan are required. This archive handling changes no trading, finance, quota, budget or phase scope and is subject to fixed-version GPT Work review.
