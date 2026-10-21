# c836295 补充技术复核接收与剩余关卡

报告固定c8362953f555606795b6804cdfe28ff690c2364d，真实来源GPT Work。报告技术PASS、未发现阻断，WORK-P2-001–003均CLOSED（GPT Work supplemental recheck PASS）。只登记该版本、已报告问题和实际复核范围，不登记Gemini本人执行、用户验收或发布。

| 问题 | 接收处置及实际依据 |
|---|---|
| WORK-P2-001 | 补充PASS保持：P1三处源码与发布main一致，132项及原16/6项host边界继续通过 |
| WORK-P2-002 | CLOSED—本次GPT Work补充复核：等价JSON规范化，批次/config/content_hash/实际文件/manifest一致，重复键及非法编码拒绝，原格式化反例通过 |
| WORK-P2-003 | CLOSED—本次GPT Work补充复核：按schema冻结实际参数并重算hash，与配置及每条Signal核对；保留旧hash换参数/新hash重贴旧Signal负例、0.1/0.21正控 |

开发方接收实际核对256条源清单的大小/hash、原报告/接收单、原四探针逐字节保持、335条上轮lineage-fix清单、上轮248条原输入及50项冻结资产。复制253份原件，3项大源码ZIP/固定scanner和pip工具明确省略；原件保留外部源目录，完整hash/大小已核对，未宣称已入库。映射详见RECEIPT_INDEX.json；原清单原字节保留。

报告新SDK run aqrp-a4001fd1-4cd2-499a-bd40-3e6be14af9fe，dirty=false、complete=true、Python3.13.16、实际0.2.0 wheel；原始JUnit417/16/4均无失败/错误/跳过。26模块及准入JSON逐字节匹配固定源码，新bundle51933fe2508e61a25fef53ea73b4210a67cb19d6531e1bf614e206db32a1d62d不改。

重新读取官方run39637043080/attempt1产物元数据，与收到Windows12363130787（149909bytes，b3491d86f641ada3e579d36e08a8b94fe0b4a218fcd81afadd8ab1d0ee542bcf）、Ubuntu12363175606（149725bytes，1df7d45c6fe543b48ed36b116687a7932b84db9defada2b72061dd0269298637）原ZIP匹配。CRC/安全路径、全部内部字节/46选择项/根清单、实际wheel/.coverage/覆盖门槛均通过。CI临时merge d1feaae218b25741e57fdfa024c0072f87f32e67父为main fb1+目标c836，tree与目标一致，不是main合并。

本轮用已安装且源码相同的开发方SDK读取三套原数据，验证两组各八表快照并实际重放数据查询/3因子完整Signal行；保留原run/computation UUID，未改原件。按记录的原存储root独立重算12项query_hash全匹配，不要求迁移路径后query身份相同。接收核对未重新建立完整SDK或重跑417/16/4；表中的测试数属于所附本轮审查原件，接收操作不冒充报告执行。

审核辅助attempt1的路径错误有原脚本/输出/exit1和正确版本对应；保留原件，未视为项目缺陷。旧c707真实两失败、错误成功产物、原数学/旧报告与历史限制均不改，不能把新PASS追填旧历史。

## 仍未闭环

- 本次是GPT Work补充技术复核。Gemini本人新的完整SDK执行仍NOT VERIFIED；旧Gemini报告事实说明/执行范围与缺失综合AST/math/hash原件保留历史边界，不把该报告冒称Gemini新复核。若需接受角色/执行限制，由用户明确决定；当前未记录此项批准。
- 用户Phase2人工验收尚未取得；main合并、标签/发布及获批范围合并后基线核验均未授权/未完成；Phase3须另行明确授权。
- 本次无新业务修复，不改src/tests/tools/CI/构建/锁/Golden/准入receipt；新交付提交只归档和更新状态，不能将本报告称为审了之后漂移的新业务版本。
