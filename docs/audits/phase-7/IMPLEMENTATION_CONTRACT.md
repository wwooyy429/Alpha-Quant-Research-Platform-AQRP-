# Phase7 受限工程实现契约

授权原文、已审G1固定645049ae9b08710ed93189b80547d14c87d80584及C-P7-001～004接受见 IMPLEMENTATION_AUTHORIZATION.json。原G1设计、独立答案、失败记录保持原字节；本文件说明新增实现，不改写旧计划或旧审计结论。

- 共同预算：受管物理W及其可信data_hash共享12研究单位。Task、旧CLI、公开ResearchService和direct-ledger无法靠省略context、换family/参数/输出目录逃逸；全部候选×期限在观察结果前原子预留。失败、取消和风险拒绝不退款，原family限额与重复污染仍有效。真正独立standalone输入保留原契约。
- 恢复与归属：Task+预算同一SQLite事务；R子运行只claim已预留单位。确定性outbox按提交顺序投影trials，原字节、previous/hash、缺失/外来历史均核对。活legacy进程持排他锁，预算幂等不授权第二个进程执行同一R；恢复按可信原身份/epoch进行。
- 执行计划：输入、catalog、代码、运行器源和每个actor身份在任何输出前冻结，按CAS严格激活。UI不填写slot、purpose或token；旧会话/旧key无法认领下一actor。派生replay只将预登记source_slot的已核真实Task UUID替换模板占位，不能事后编辑plan。
- 双时钟：显式execution_sessions只允许engineering_pipeline非空、唯一、可信排序的原研究会话子集。P3完整19截面不裁剪，P5固定10决策通过原P5内部真实P4执行；来源ordinal、hash、物理目录、resolved-plan及全部required P4完成屏障继续有效。缺省字段在同一新bundle/catalog下保持旧请求布局。
- 通用适配：只接受公开合成P1八表、真实sidecar/catalog/锁/包身份和完整显式规则的恒等映射，通过原TaskService运行。缺失、冲突、未知真实源、正式Test或实盘要求明确拒绝；不另建风控、账本或撮合引擎。

主协议预算为同一W的12单位：SDK2、TaskCLI2、AppTest2、legacy研究+回测CLI2、透明答案SDK2、真实浏览器2。运行时顺序在输出前冻结为上述顺序，保留原设计12单位分配；CI执行前10后必须停在真实浏览器待执行，不能把AppTest当浏览器。独立风险负例在任何主输出前登记原单独工程夹具1单位；主根queued取消与数值重放各零研究单位。完整报告分别列MAIN12、风险1、replay/cancel0及独立回归夹具，不能混称全部只用了12。

独立数值依据为原G1 MAIN_PIPELINE_CANDIDATES、FINANCIAL_FEASIBILITY_CANDIDATES和GOLDEN_CANDIDATES原字节。研究浮点采用既定绝对1e-12/相对1e-10或更严格原Golden；数量、现金桶、费用、账本及风险边界按原精确值核对。数值相等前必须验证真实来源与终态清单，不能通配忽略hash/血缘。
