# 修订设计必须落实到真实G2的专项矩阵（全部Planned）

当前32+95是设计参考，以下真实服务/SQLite/磁盘/并发/浏览器均未执行；不能以模型成功关闭发现。

| 断点/反例 | 要求的真实验收结果 |
|---|---|
| P3 start前、初始记录后、试验登记后、终态后/slot映射前后 | 未启动可首次调用；不明中间态失败关闭；原终态只恢复R，家族记录不重做/退款，Task不提前成功 |
| R成功、PLAN未冻/已冻，P5未启动 | 保留R；纯来源/请求组装可重验证；只执行确定未启动的后续slot |
| P4预分配/BOUND提交前后、核心半初始化、真实P4终态后/映射前 | 调用前已有元组/适配raw hash；合法终态仅复用原child；半初始化无新恢复许可，不新建第二P4 |
| P5内部P4错Task/slot/服务/decision/time/source/adapted/parent/run/root/config/code/bundle/锁/epoch | 即使UUID和manifest合法也拒绝；不全局切换context或事后补归属 |
| 枚举报错、链接/reparse、重复alias、缺必需slot/未知额外child | 失败关闭，不当空目录/完成覆盖；原根/manifest/candidate/risk/发布审计不删 |
| P5同原请求resume再次到已完成P4 | 在原严格resume条件下复用同slot/result，真实核心构造调用次数不增加；旧无contextSDK保持原行为 |
| P3/P4成功但B未启动/缺失/FAILED/取消/unknown | 无全Task成功；不输出旧账户认证；原001/003提交后故障例继续回归 |
| B已SUCCEEDED但必需P4或最终工件/来源缺失 | RECOVERY_REQUIRED，不在B结束后补跑孩子或删slot |
| 全子run成功，completion未写/写后SQL前/SQL后回执损坏 | 只有全量重验证+回执/SQL闭环才成功；损坏显示不可用完整性错误并留原记录 |
| 取消排队、R后B前、P5完整事务后、成功/取消竞争 | 意图与实际取消分开；先成功提交则TOO_LATE，先接受取消则不成功；unknown始终FAILED |
| replay只核原源、已重放但未比较、真实比较及目标封存 | 原源成功不代表新重放成功；新目标/context/内部P4正确，原源只读，声明范围不扩大宿主复现 |
| 同key10并发、异hash碰撞、不同Task并发与claim接管 | 一任务/一有效claim，异hash冲突，旧epoch无效，研究家族根/计数不按Task重置 |
| 精确长权重、大金额/正负HALF_EVEN/4096位与超限 | 端到端精确传递与原始显示，数值词法通过不替代后端领域约束；超限明确拒绝不截断，正确原答案不改 |

全SDK、旧20+4/91/G2反例、双OS原ZIP完整身份/成员/环境/终态链、六页面实际浏览器、同核两因子与正式拒绝仍按原TEST_AND_EVIDENCE_PLAN执行；真实Windows隔离/正式Test/金融批准不在授权中。
