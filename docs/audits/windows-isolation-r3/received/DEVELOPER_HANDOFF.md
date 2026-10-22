开发 Codex 交接：Windows R2 工程隔离复核

固定业务 SHA：9ac5db069287a6e4a095e25ae8c3cc8fa229cded；尝试 e6968f1c-3552-4a98-af61-98a5194dafea。

GPT Work 已读用户管理员执行的原始日志并独立复核：三真实非提升主体、并发单预算、崩溃恢复、重复拒绝及代表性读写权限控制已执行；184 条检查 183 PASS、1 FAIL。两个运行时各6250文件和固定Git对象45模块、四因子答案/成员及逻辑哈希、两条账本链均通过；三个账户已禁用。

整体 Windows profile 仍 NOT VERIFIED / BLOCKED。请保留两项 OPEN：
1. WI-R2-001：运行后 verify_host 返回 UNVERIFIED_ISOLATION；42 个新对象继承权限，与 evaluator.py:61 每对象 protected 要求冲突。已测实际权限边界通过，不等于全配置通过。不能删除安全检查或事后补 ACL 后改写原失败。请提出安全创建/发布策略或可证明的继承验证设计，固定候选及回归范围后交审。
2. WI-R2-002：P1 mkdtemp 的 owner-only 临时发布目录保留 OW/SYSTEM/Administrators ACL，实际生成快照未列 auditor，且未执行 auditor 对此快照的真实探针。当前 reviewer 无法读九个原始文件；actor 报告的 snapshot manifest hash 未独立重算。canary 不能代替真实文件覆盖。建议可信 operator 预建并审定工程输入权限，或评审完整存储适配层，再覆盖真实输入/侧车/缓存/日志/输出生命周期。

REPORT.md、INDEPENDENT_VERIFICATION.json、ACL_INCOMPATIBILITIES.json、OMISSIONS.json 及 ZIP/RECEIPT 为本次依据。九个不可读输入文件未装进证据包，必须保留这一限制；原始37个导出文件及24个可读工程产物均已封存。

本交接不是业务修改或部署授权。请勿凭此启动真实正式 Test、授金融批准、标记 VALID-004 全项、宣称完整历史宿主复现，也不改变已受限验收的 P3 和 P4 G1 计划结论。不合并、打标签、部署、进入 P5；本次未启动 P4 实现。先给出具体设计/修复候选及影响范围，再按用户授权继续。
