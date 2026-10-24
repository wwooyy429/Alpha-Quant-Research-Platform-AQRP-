# Phase6 稳定基线 · 八项受限工程验收

用户明确 ACCEPTED 八项 UI-001–008（5 MVP / 3 Competition Ready），授权本次条件核验后的普通合并与基线标签。GPT Work 固定 `3017a097b49ecdae68228ca9a417fcd03c313200` G2 PASS，三项原发现和 SQLite 并发修复已独立确认关闭；独立报告原文见 [g2-3017a09/received/REPORT.md](g2-3017a09/received/REPORT.md)，原始封存、7份外部附件位置及哈希见 [EVIDENCE_INDEX.json](g2-3017a09/EVIDENCE_INDEX.json) 与 [EXTERNAL_ORIGINALS.json](g2-3017a09/EXTERNAL_ORIGINALS.json)，人工原话见 [publication/APPROVAL.json](publication/APPROVAL.json)。

PR #9 实际批准归档头 `a4d650d5d15e814600fde0bb6858fe97f14e5229` 相对已审实现仅文档、审计存储和身份元数据变化：11个既有文档/元数据及388个新增归档文件；源码、测试、工具、CI、构建、核心/UI锁、原106需求目录和5016冻结文件不变。旧归档 H1 的完整1567产品断言通过但 secret scan 失败，整体CI为失败；原 run40087892421 的日志、ZIP和判定完整保留，不改判通过。7份扫描涉及的工程身份哈希原件逐字节留在外部原包及可直读路径，Git收明确索引，原manifest和扫描规则未改。实际 H2 双系统 CI run40089881581 各1567项通过，官方原始ZIP、摘要、大小、CRC、精确成员及逐项哈希核验通过。

普通合并 `7b4864f4d750fa96b5b5634c4bba0cd84b5b077f` 具有原 main 和 H2 两个父提交，整树等于 H2，保留完整历史。开发方随后在实际 M 上新建干净环境并安装 wheel：完整 SDK1567通过、0失败/错误/跳过；原20＋4回归及91项独立参考数学脚本重新执行通过。环境、原始命令、日志、工件与哈希见 [publication/VALIDATION.json](publication/VALIDATION.json)、[SDK_ARCHIVE.json](publication/SDK_ARCHIVE.json)。完整SDK选择集在外部ZIP逐项封存，Git保留明确静态子集；其余原件没有改写或替换。原 C 的独立审核/真实浏览器、H2的官方CI、M的开发验证是不同执行事实，不互换SHA，也不作为Phase7产品测试。

发布登记只增加证据、状态文档及明确列出的文档身份哈希。已审 Python 包保持 `0.6.0.dev5`，83模块 bundle `28c3cc049efcce8fc3e55b4056e8e116f98deca39eeb1d2c8822799c8e98855b`，核心锁 `86c7bf65c9a9690036006360062c8cd10a91279705b4070af7033d7699abffeb`。`phase6-baseline` 与 `v0.6.0` 为阶段里程碑标签，和main原子发布并核对同点后为 RELEASED；旧标签对象及peeled SHA不移动。最终发布P的完整SHA由 `git rev-parse 'phase6-baseline^{}'`、远端main/新标签和外部发布回执确定；本文件不自包含自己的提交SHA。实际执行M与证据发布P分开记录，不能将M日志改成P执行。

WI-R2-001/002及整体真实Windows隔离继续 DEFERRED / NOT VERIFIED；最终全部开发完成后仅在另行授权的最终集成40位SHA上做真实权限与生命周期验证。正式Test未运行，金融批准NONE；完整历史宿主仍NOT VERIFIED，只沿用软件包、依赖锁、旧因子版本和结果重放的受限验收。正式入口保持失败关闭；不启用账户、不改真实ACL/服务/调度、不部署、不实盘。原native crash精确原因仍NOT VERIFIED，不能因工程harness修复关闭而扩大结论。

仅在基线发布与远端三点核验后，从该main创建独立Phase7 G1计划分支，覆盖原五项需求（DATA-013、INT-003–006；3 MVP / 2 Competition Ready），提交映射、接口、数学/独立候选答案、测试证据和阶段依赖，计划PR以AQRP_FIXED_REVIEW_SHA锁定完整40位SHA交GPT Work独立预审。Phase7业务实现、验收、合并、发布及真实部署均未授权；未知比赛/真实数据规则保持外部待决。
