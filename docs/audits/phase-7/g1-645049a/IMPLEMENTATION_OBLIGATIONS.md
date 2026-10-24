# 已审设计的后续实现与 G2 证据记录（待单独授权）

依据：GPT Work 对固定 `645049ae9b08710ed93189b80547d14c87d80584` 的 REPORT.txt 第2～4、6节，以及该固定版本的下列设计。当前仅归档已审要求；不修改设计、不新增未审义务、不授权实现。三项非阻断精度要求均未执行产品验证。

| 非阻断实施精度 | H 已审设计对应 | 候选/原测试计划追溯 | 后续实际固定实现的 G2 证据 |
|---|---|---|---|
| 两事务依次 commit、逆序取得 trials-lock，outbox/JSONL仍按确定 seq/previous_hash 发布 | COMMON_BUDGET_ADMISSION_DESIGN.md:32～36 规定 monotonic seq、冻结 outbox 与 previous_hash；:86～98 规定 authority先提交、单一锁序、精确投影/恢复与并发线性化 | BUD-003 混合并发、BUD-010/011 幂等、BUD-015/016 崩溃与投影恢复、BUD-017 缺损失败关闭；TEST_AND_EVIDENCE_PLAN.md:8 T7-ADMISSION | 保留实际 authority 提交次序及冻结 payload/seq/hash、投影顺序、完整原 JSONL链和恢复原字节。应能核对逆序抢锁没有乱序/重复/丢失；不得把错序当允许损坏后继续，也不能截断失败日志或重置预算 |
| 原 legacy 进程仍活，exact retry拒绝重复或通过排他恢复fencing，不能同run并行执行 | COMMON_BUDGET_ADMISSION_DESIGN.md:45、:59、:80 规定分配 UUID 前查询原 slot owner、同run恢复或显式拒绝；:32～34 唯一owner/claim；:98 相同幂等并发只一份 admission | BUD-011、BUD-033 及 T7-ADMISSION 原owner/并发/幂等要求 | 实际两个调用/进程身份、原 owner/run/key/slot、准入/claim/执行记录、退出码与完整输出；仍活旧owner时重复调用明确拒绝，或有排他恢复fencing证据，不能只证明最终debit=1就允许同run重复观察研究结果 |
| actor推进后迟到旧key/session只能返回原核验owner或拒绝，不认领下一个同canonical actor | COMMON_BUDGET_ADMISSION_DESIGN.md:58～59、:66～70 可信CAS顺序及 activation_id/epoch、无caller选slot；:72 exact retry优先原owner；:80～81 不新UUID/换key抢其他slot | BUD-012、BUD-014、BUD-033/034/035，T7-ADMISSION 与原真实入口身份链 | 保留旧/新 actor、key/owner、activation/epoch、原始请求/根/服务绑定及前后计数；真实旧session/迟到key复现应返回原核验owner或拒绝，不能自动绑定新actor。原BUD-035预期的stale rejection不得被迟到请求改判成功 |

以上证据具体形式沿现行原始日志/身份/manifest/哈希规则记录，表格不规定新的产品API或新经济口径。若实现需要改变已审幂等、激活、恢复或错误顺序语义，先提出新设计差异，不从“非阻断”推定豁免。

其余已审 G2 范围按 H 原 TEST_AND_EVIDENCE_PLAN.md、COMMON_BUDGET_ADMISSION_CANDIDATES.json 与 BROWSER_NEGATIVE_PROTOCOL.md 原字节延续：

- 全部36个预算候选与原“12个取消后旧入口”反例、双向顺序、剩1混合并发、N=2整体拒绝、可信父子不双扣、direct ledger/公共research/旧CLI强制共同准入、改域/家族/配置不逃逸、历史缺损/外来写入失败关闭；该36仅设计已审，实际仍待执行。
- 真实浏览器 BR-RISK-ORIGINAL-01：在事前冻结的独立原风险夹具消耗1研究单位；R成功、P4 REJECTED/GROSS且原ledger FAILED、B成功但无fills现金/权益1000、整Task FAILED/REQUIRED_STAGE_REJECTED；不得以预算拒绝/字段错误代替真正风险拒绝；第二新key在1-slot限制下拒绝。
- 真实浏览器 BR-CANCEL-REPLAY-01：SDK只排队预指定源replay，真实浏览器选择精确Task取消；QUEUED→CANCELLED须满足原财务门禁；无R/P4/B/E或新研究，随后实际worker no-op/同key复用及源原件不变。SDK入队不得称浏览器提交。
- 真实浏览器 BR-REPLAY-01：真实Replay按钮提交/运行新E与十个P4，比较声明投影，零新研究；不能以重放替代主研究actor。MAIN12、风险1、取消0、正常replay0分别记账，完整SDK独立夹具另列；禁止失败后换根补成功或声称新金融独立样本。
- 完整干净安装SDK、旧20+4/91、旧Ref/包声明重放、全部旧业务及新增P7用例；同一完整40位固定实现、独立答案/原失败、实际环境/源/wheel/RECORD/锁/命令/JUnit/coverage；双OS官方原ZIP/原日志/API身份/digest/CRC/精确成员/逐项hash；真实浏览器AX/截图/任务及进程/下载原件。API success不能替代官方原包核验，模型/CI不能替代真实浏览器。
- C-P7-004的19研究/10执行、fee50工程夹具、新全bundle与新阶段package gate/CI选集，以及原P6固定环境checker、原5016/正确答案/锁/旧回归均不放宽。旧包在独立原根，不以新包hash冒充旧Ref。

当前状态：G1 PLAN PASS WITH CONDITIONS；001/002 CLOSED_DESIGN；C-P7-001～004用户接受 PENDING；单独实施授权 PENDING；P7产品测试/真实浏览器/G2 NOT PERFORMED。R2 DEFERRED / NOT VERIFIED，正式Test NOT RUN，金融批准 NONE，既有历史宿主边界保留。无实施、合并、标签、部署或真实权限操作。
