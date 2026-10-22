GPT Work 补充审核结论：Phase4 G2 BLOCKED / REQUEST CHANGES。固定审查 SHA：18439f31536295aea42e57e566d07cce345a35cf。七项工程能力已有真实实现；独立干净SDK799、双OS官方原ZIP各799、174组完整服务独立复算及23项负控制、原20/四/91/三扫描均通过，但新增两项阻断缺陷仍OPEN：

1. WORK-P4-G2-001（High，contracts.py:82–87、risk/checks.py:168、service.py:70）：权益/现金1e35、价格1、lot3、零原仓、LongOnly score top_k1是当前允许输入。内部正确整手数量10^35−1在34位输出投影后变成10^35，仍SUCCEEDED/risk.passed=true；发布的target/delta除3余1，现金+市值比权益多1，超过资金容差。1e3/1e34对照正常、1e40也复现。请保证最终数量/delta/金额无损表示，或结构化拒绝不能表示的结果，并从最终返回和落盘字节验证lot、资金与风险一致性；不能放大容差或只改显示。补数值域边界、正负数量/非10幂lot及服务级回归。

2. WORK-P4-G2-002（Medium，research_input.py:62–73）：真实P3原工件的snapshot_id未绑定。保持原P3 run/stage/manifest/data hash和原分数不变，将所有请求context的snapshot_id一致改成另一合法UUID并重算envelope/fixture hashes，服务仍成功并发布错误父快照ID。主审已独立核对原manifest及八表hash。请核实实际SnapshotRef/manifest/表内ID与原研究来源的对应关系；如需投影身份须独立字段，保留真实source snapshot身份。补合法原来源、合法但错误UUID、ID/hash交叉混配、整份请求一致改写和单envelope改写的正负控制。不能仅校验UUID格式、降级为手写fixture或改写旧P3工件来通过。

详细输入、run_id、原始命令/结果和依据见本轮REPORT.md、ADVERSARIAL_RESULTS.json、PARENT_BINDING_PROOF.json及证据包。请最小修复、保留既有正确Golden/旧Ref/审计/失败历史，更新全bundle工程准入，执行干净SDK、双OS和适用新增/旧回归，完成后提交新40位固定SHA及完整原始证据供GPT Work复核。不得自行关闭发现或宣告G2通过。G1仅设计通过；本报告不改变P3受限验收，也不关闭Windows隔离缺口。仅工程数据；不运行正式Test、不授金融批准、不合并、不打标签、不部署、不实盘、不进入P5。
