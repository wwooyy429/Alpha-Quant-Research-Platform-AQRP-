# 十二项实现与验收证据索引

当前0.5.0.dev2修复勘误以[g2-bfdcf30/OUTPUT_CONTRACT_ERRATA.md](g2-bfdcf30/OUTPUT_CONTRACT_ERRATA.md)及[修复复核入口](g2-bfdcf30/REVIEW_PACKAGE.md)为准：原bfdcf30独立G2为BLOCKED，两项仍待新固定版本独立确认；以下原实施说明及正确经济口径保留，不把旧PENDING或正常SDK通过改称G2通过。


原106条目录及本阶段12条（10MVP、2Competition Ready）快照不改。下表为工程实现候选，独立G2及用户阶段验收尚未完成；任何开发方PASS不得自动更新为ACCEPTED/RELEASED。

| ID / 等级 | 实际代码 | 主要验证入口与独立答案 |
|---|---|---|
| BT-001 MVP | backtest/engine.py、transactions.py | test_engine_service、test_atomic_risk、test_recovery_publication：事件总序、80/90原子子记录、真实进程崩溃、SDK原run恢复、链损坏 |
| BT-002 MVP | contracts.py、provider.py、engine.py | test_engine_service：可得/决策/提交/严格未来开盘、晚到1us、未来切片mutation；test_liquidity：历史量修订/发布边界 |
| BT-003 MVP | execution/model.py、engine.py | test_public_lifecycle：真实partial/DAY/GTC/到期；test_engine_service取消前/中/迟到、状态与幂等；test_atomic_risk共享容量 |
| BT-004 MVP | execution/model.py、liquidity.py | G09–G12/G19及N12–N17；test_liquidity实际门槛/历史可得性/P1原值绑定；价格域/限价/滑点/费用/容量/停牌 |
| BT-005 MVP | backtest/ledger.py、transactions.py | G01–G08/G24/G25；test_exact_ledger边界/性质/大数/资金守恒；原始Journal与tools/backtest_reference独立重建 |
| BT-006 Competition Ready | ledger.py、engine.py | G13–G17；test_boundaries与test_engine_service拆股/ex/pay/迟到修订/未知退市/已知回收/不可用碎股 |
| BT-007 Competition Ready | ledger.py、risk.py | G05–G08/G16–G18及N04–N11/N18–N25；short交收前后A899、partial cover、历史借费反例、short应付、保证金失败原状态 |
| BT-008 MVP | performance/metrics.py、服务projection | 真实每日账户/持仓/敞口、Journal资金重建、多空归因；实际输出/落盘/返回字节篡改控制 |
| BT-009 MVP | performance/metrics.py | G21/G22/G23、FIFO片段1/2与5/9、TWR21%、ddof1/A252/rf0、undefined、外部流不作利润、费用不二扣 |
| BT-010 MVP | provider.py、services/backtest.py | test_phase5_pipeline及backtest_smoke：真实P1九文件→P3终态→P4服务→订单/撮合/账本/绩效，仅替换精确Ref，核对核心包Hash不变及完整数值重放 |
| QA-003 MVP | 上述模块及全部P5测试/参考工具 | 至少10类不变量：PIT/合法状态/幂等/容量/lot/佣金预算/现金桶/复式/成本池/权益归因/发布原字节/重放；95%行90%分支，预注册字面答案与独立原始事件核算 |
| INT-002 MVP | services/backtest.py、backtest_cli.py | 完整SDK安装真实wheel、薄CLI同服务、真实P1/P3/P4原始输入与终态绑定、原Ref环境重放、正式入口拒绝；双OS官方原ZIP与环境/源码/工件Hash |

代码路径均以src/aqrp/为前缀；测试以tests/backtest/或tests/integration/为前缀。tests/portfolio、原P4全部金融源码及答案保持，版本身份断言仅按新包版本更新。原G1的25/70、补充25/209输入/答案/容差及参考脚本保持原字节；其设计结论不能代替这些实现验证。

开发探索期失败/修复、实际命令/输出、固定提交干净SDK、CI执行SHA与PR head关系、原始ZIP/摘要/CRC/成员Hash、源代码/数据/环境版本在PR #8固定版本外置封存包逐项列出。Git仓库提供规范/原始审计和身份索引；完整依赖wheel/大型工件留外置原字节，不冒称仓库包含完整原包。最终事实只接受实际执行记录，不把本计划表当通过结果。
