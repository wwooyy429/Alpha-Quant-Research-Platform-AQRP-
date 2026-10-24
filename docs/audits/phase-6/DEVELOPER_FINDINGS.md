<!-- Phase6 release-publication override -->
2026-10-24 最新人工验收及发布覆盖说明：Phase6八项受限工程范围已由用户ACCEPTED，GPT Work固定3017a097b49ecdae68228ca9a417fcd03c313200 G2 PASS及三项修复关闭维持。PR #9批准归档头a4d650d5d15e814600fde0bb6858fe97f14e5229只改文档/审计存储/身份元数据，双系统实际CI各1567通过；旧H1扫描失败及原证据保留，7份外部原件位置/哈希明确，扫描规则未改。实际普通合并7b4864f4d750fa96b5b5634c4bba0cd84b5b077f整树等于批准头；开发方合并后新干净SDK1567、原20＋4及数学91通过。发布证据提交仅文档及其身份元数据，main/phase6-baseline/v0.6.0原子同点核验后才RELEASED，旧标签不移动，已审包仍0.6.0.dev5。仅授权其后Phase7 G1计划，不授权业务实现。WI-R2两项和真实隔离持续DEFERRED / NOT VERIFIED，正式Test未运行、金融批准NONE、历史宿主边界及原native原因NOT VERIFIED维持；无部署/实盘/真实权限操作。详docs/audits/phase-6/BASELINE.md。以下既有轮次为历史，不覆盖本次最新人工决定。

> 2026-10-24 当前独立结论：GPT Work 对固定 `3017a097b49ecdae68228ca9a417fcd03c313200` 的 **Phase6八项受限工程范围G2 PASS**，WORK-P6-G2-001/002/003均CLOSED — FIX VERIFIED，无新增阻断；DEV002/003/004按主审工程范围关闭，旧原生精确原因仍NOT VERIFIED。独立SDK1567、已核验双OS原包各1567；原始报告、失败及辅助执行勘误完整保留。**等待用户阶段验收，未ACCEPTED / RELEASED，未获合并/基线/标签或P7授权。** WI-R2-001/002及真实Windows隔离DEFERRED / NOT VERIFIED；正式Test未运行、金融批准NONE、完整历史宿主边界保持。已审实现与后续文档归档SHA分列，PR9审查锁保持3017完整SHA。以下旧OPEN/BLOCKED及待审状态仅作原轮历史，由本条更新当前状态。 [本轮接收与处置](g2-3017a09/DEVELOPER_RESPONSE.md)。

> 2026-10-24 当前修复记录：更新：GPT Work在eae807f已将DEV-P6-001确认CLOSED — FIX VERIFIED。新增WORK-P6-G2-001/002/003保持OPEN待修复新固定版本复核；下文是原dev2开发记录，不覆盖当前独立状态。 八项受限P6工程范围；不合并、标签、部署、实盘、正式Test、金融批准或P7。WI-R2-001/002和真实Windows隔离DEFERRED / NOT VERIFIED；完整历史宿主限制保留。

# 真实浏览器补充发现及开发修复（待固定版本G2）

DEV-P6-001：固定 C1 `f03ebe7c65117e082608a82474461d876265bf7e` 的完整 SDK 1486 与双OS CI均成功，真实浏览器后续发现 Settings 连续保存 `lookback=3`、再输入 `2`，实际数据库却保存 `[3,3]`；安装包上的独立字面回归也失败复现。页面显示 Saved revision2 时仍显示旧 Current revision1。原网页状态、截图、数据库核对、失败日志、原始SDK/官方ZIP保留，事实/哈希见 C1_BROWSER_FINDING_EVIDENCE.json。该C1不作为完整实现交付，CI成功不覆盖反例。

原因是文本区以变化的默认payload参与组件身份，下一次编辑被新的默认值替换；保存动作还使用执行时最新revision而非编辑器加载时revision，不能阻止另一个会话的旧编辑覆盖新配置。

0.6.0.dev2候选改为稳定编辑器key、绑定加载时base revision、显式Reload latest、保留拒绝后的原文。成功保存/回滚后立即显示自己的新不可变revision；若之后另一个会话修改，显示过期警告并按CAS拒绝，不自动采纳对方的新revision。历史默认配置读取增加原payload/hash核验。因子选择保存只更新因子字段并保留费用/风险/其他默认值，回滚同步恢复选择及版本显示。

回归覆盖连续两个不同输入、即时版本显示、双会话过期CAS拒绝/保留文本/显式重载、非法文本不落库、历史快照损坏与回滚拒绝、因子选择保留其他字段、旧冻结请求不改。原字面期望 `[3,2]` 保留，不通过增加手工rerun或改变正确答案迎合旧实现。

处置为 **FIX_IMPLEMENTED / PENDING_FIXED_SHA_G2**，不冒充GPT Work独立关闭。本次修复只属P6配置/视图/非金融状态，不修改金融算法、core锁、原Golden及既有延期。新完整SHA必须重跑干净SDK、双系统原ZIP与真实浏览器，C1通过记录不能移作新版证明。


DEV-P6-002：C3固定418c17fad8fefe50dedc866f95c14ccf0fa433ca的1558项预检及覆盖率门禁通过，安装包测试亦已1558通过；收尾发现只读SQLite连接未显式关闭造成资源警告。dev4改用closing确保正常/异常路径均关闭，增加两项实际连接生命周期回归，不降低检查、不改变金融数学或预算。C3原日志/工件/浏览器前缀保留，不能移作dev4证明；最终重新锁完整SHA执行SDK/双OS/原ZIP/真实浏览器。见RESOURCE_LIFECYCLE_REPAIR.json。三项独立G2仍OPEN，DEV-P6-001独立关闭结论保留，DEV-P6-002是开发自查修复待主审。

## DEV-P6-003 — candidate Windows abrupt-death harness

C3 CI 40069640065 Windows failed 1/1558 with child native exception 0xC0000005; Ubuntu and local installed SDK passed 1558. Original failure is retained, not reclassified. Exact native fault cause is not proven. The new harness records/fsyncs the reached boundary, enables native traceback capture and uses Windows self-TerminateProcess(73), retaining exact exit and every recovery assertion. See g2-eae807f/CANDIDATE_CI_FAILURE.json. Pending new same-SHA SDK/dual OS and GPT Work review.

### DEV-P6-003 follow-up — all six abrupt-death boundaries

C4 CI 40072608848 Windows failed on another remaining os._exit P4_PARTIAL control (1559/1560); Ubuntu passed1560. Previous repair covered only two boundaries and was incomplete. All six P6 deliberate death controls now share fsynced point/PID/Task/code/method records, native diagnostics and strict exact exits73/74/75. No recovery assertion or original answer removed; no business source change vs C4. See SECOND_CANDIDATE_CI_FAILURE.json. Native cause is not proven; both old failures retained. New fixed-version full evidence and independent review still required.

## DEV-P6-004 — simultaneous first-open WAL admission

C5 local clean SDK failed the existing required ten-process test (1559/1560) before transaction entry: journal_mode=WAL reported database locked. Added bounded native lock waiting before BEGIN, verified wal mode and retained FULL durability/remaining busy timeout. Body and commit are never rerun. Seven deterministic native-contention/fail-closed controls and unchanged ten-process outcomes cover this. All child outputs are now drained before reporting failures; missing outputs from the old failure are not invented. Original failure, C5 Ubuntu success and Windows environment refusal/retry remain separate. See SQLITE_INITIALIZATION_REPAIR.json. New version0.6.0.dev5 still requires fixed-SHA full SDK/dual OS/browser and GPT Work review.
