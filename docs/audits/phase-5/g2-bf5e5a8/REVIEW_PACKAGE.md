# 003原始执行背书修复的固定版本独立G2入口

仅取PR #8 AQRP_FIXED_REVIEW_SHA完整40位，并核远端head一致，detached检出，不审漂移HEAD。对照bf5e5a89209f2dd24042cd806626f832b531de52：001/002保持CLOSED，003 High PARTIAL FIX/OPEN，整体BLOCKED；开发方不自行关闭。

重点重跑settled_short_backing_probe的真实公共服务，在session2交收AFTER_COMMIT把asset lot.price与已交收cashlot.amount同时99.9→98.9，原始Fill/Journal/payload/children不改；应有C997.8/S99.9/A797.9，旧错报798.9。要求ContractError和KeyboardInterrupt均变UNKNOWN/FAILED、无已知账户，原commit/原因/终态getter证据保留。检查新重建是否只取已验证durable prefix的原始Fill、MarketConfirmed、SPLIT、FIFO cover、DELIST和SETTLEMENT；不能用缓存Fill或两个可变状态字段自证。进一步伪改post_state Fill复制件仍须拒绝。正常/异常/取消公开财务前共用完整projection，含经济与归因门禁，不只修一个捕获类型。

正控包括未损坏同边界、T+1前后部分cover、multi-entry FIFO、两方向跨零、拆股/公司回收、合法margin loss；负控包括缺来源、冲突来源、单字段/成对字段、归因池损坏、原六方向桶/RP以及001/002原全部回归。旧正确expected不得调整来迎合实现。原20+4/91、原Ref66字节/三run、P1九输入/P3/P4/P5两因子与重放、完整SDK及原line/branch门槛保持。

接收原件/176文件封存见received和RECEIVED_IDENTITY；处理/输出勘误/工程自查分别见同目录文件。新原始命令/环境/SDK/官方双OS ZIP/API digest/CRC/精确成员/hash/wheel69/锁/实际CI执行SHA-tree-parent/终态链与当前副本补充子树证明，按PR描述外置封存独立核对。开发方复跑仅是开发证据；请GPT Work另行独立执行并给003关闭或仍OPEN依据、新40位G2结论及未验证条件。1116旧通过不覆盖新候选。

WI-R2两项/真实隔离DEFERRED / NOT VERIFIED；正式Test未运行、金融批准NONE、完整历史宿主未验证（已接受包/锁/Ref重放范围不变）。无账户/真实ACL/部署/实盘/正式Test/金融批准/合并/标签/P6。G2通过仍非用户验收或发布许可。
