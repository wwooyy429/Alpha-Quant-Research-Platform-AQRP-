# 固定bf5e5a8的003部分修复复核接收与继续修复

GPT Work对`bf5e5a89209f2dd24042cd806626f832b531de52`判G2 BLOCKED / REQUEST CHANGES；001、002保持CLOSED — FIX VERIFIED，003 High为PARTIAL FIX / OPEN。原逐桶/RP反例已独立通过，1116及官方双OS原包通过不抵消新反例。589653932字节原EVIDENCE.zip、176声明文件+manifest的CRC/精确成员/全部大小与hash接收核验见RECEIVED_IDENTITY.json；137份原件和reviewer-production-artifacts.zip原字节归档received/，大原包外部保留。旧报告/错误余额/错误认证不回写。

新反例只将已交收SHORT cashlot.amount及asset FIFO lot.price同时99.9→98.9，原Fill/Journal/children不变；旧版FAILED和CANCELLED都将S_set98.9/A798.9误标known=true，正确为S_set99.9/A797.9。上一版只是同一可变post_state自证，未绑定真实原始Fill。这是003未闭环，不新编编号、不自行关闭。

本候选0.5.0.dev5：verify_execution_backing只从TransactionStore在writer锁下读取、完整验证过的durable prefix的原始children/payload重建，禁止post_state/缓存fills/缓存lot价格成为重建输入。按实际成交逐证券重建FIFO开平/跨零、均价、剩余股数/原价/settles/at；按原始SPLIT调整股数/价格，按MarketConfirmed重建mark，按真实DELIST恢复及SETTLEMENT重建原始所得cashlot/释放/到期/限制。未交收cover仅释放到原due的FREE，已交收cover只减少限制。逐项核对现金lot、持仓lot、复制的Fill/恢复记录、数量/成本/mark/估值调整及交收元数据；来源缺失或冲突一律拒绝。不再由两个关联状态字段互为original。

正常输出、异常/取消已知账户及数值重放都经过同一projection：逐桶/RP/Journal、durable来源重建、经济恒等式和绩效归因完整必要门禁。失败快照只公开通过此证明的account，不公开失败研究指标；任一失败均FAILED+COMMITTED_STATE_UNVERIFIED/known=false、无last_committed_account和已知快照，原commit/首个异常保留。成功发布也重新读取磁盘verified_snapshot，记录与返回使用同一durable prefix；缓存与磁盘不一致拒绝发布。财务证明hash附于已知失败前缀的证据。哈希链完整不等于财务一致性或OS隔离/金融批准。

新增反例覆盖两种捕获类型、成对字段及进一步伪改post_state的Fill复制件、单字段与未损坏正控；新增多entry FIFO、两方向跨零、T+1前后cover、拆股/公司回收、缺失/冲突来源及归因池损坏。原43项正确金额/拒绝语义保持；低层正控现在明确供应执行来源与实际settlement/mark，缺上下文不再认证。expected仍为预先字面值797.9/99.9、1108/100、-1001等，不能用生产函数生成正确expected。原001/002六边界、真实进程原run恢复、坏链/读拒绝/总额差及全部旧回归保留。

初始自测错误同样保留：第一次新反例7失败/3通过含3个KeyboardInterrupt原因字符串假设错误（实际原有契约用类名，不用消息）；只纠正测试的错误原因断言、未动正确财务预期后，在原业务版本重跑为4失败/6通过，四项均为成对损坏。ruff首次命名检查失败与修正保留。最终只有新固定提交干净SDK/双OS官方原ZIP和原始命令/环境/hash封存才能作为开发证据，不能冒充GPT Work独立关闭。原错误Phase0脚本的历史失败/修复仍在上一轮档案，本轮不运行该写回脚本，不修改历史审计。

追踪：BT-005/007/008对应ledger.verify_execution_backing与services.projection/_failure_snapshot；BT-001对应durable snapshot及原run恢复；BT-006对应拆股/公司行动原始来源；QA-003/INT-002对应test_g2_execution_backing、完整已安装wheel SDK/双OS原始证据。其余十二项映射与3444冻结文件、12 G1设计/答案、四因子/依赖锁不变。001/002保持关闭，003 OPEN_PENDING_INDEPENDENT_RECHECK，G2 BLOCKED，阶段未验收。

WI-R2两项与真实Windows隔离DEFERRED / NOT VERIFIED，正式Test未运行，金融批准NONE，完整历史宿主只限已接受包/锁/旧Ref/结果重放。main/旧标签不改，无账户/真实ACL/服务/调度/部署/实盘/合并/标签/P6。

额外实际负控：d7b7eaa的完整SDK/双OS1152通过后，使用已安装旧候选wheel复现初始资金+现金同时加1及固定Z限制改为-1，两种捕获类型共4项仍失败（错误known/798.9）。日志/命令/原始工件保留；不能把1152旧通过说成新候选通过。新verified_snapshot在writer锁内从不可变initial.json验证initial_cash/other_restriction锚点，防止post_state自行设定重建基数。当前profile两字段原本无合法交易变更，不改变经济口径；缺失/变化一律拒绝。新增42项而非36项，含旧锚点临时改写后再恢复仍须拒绝的两项prefix负控；最终版本0.5.0.dev5必须重新完整SDK/双OS，G2同一003仍OPEN待独立复核。

最终必要自测development-018为73项通过，包括4个额外实际锚点反例、原成对字段及新2个临时改写后恢复prefix负控。最终完整SDK/双OS在新提交单独运行；d7b7eaa旧1152原始成功和额外失败都保留。
