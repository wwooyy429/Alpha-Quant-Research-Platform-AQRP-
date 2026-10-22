# GPT Work · G2 修复固定版本复核

仓库 https://github.com/wwooyy429/Alpha-Quant-Research-Platform-AQRP- ，PR #5。从 PR 描述读取新的完整40位 `AQRP_FIXED_REVIEW_SHA` 并按该提交检出，记录开始与结束的固定值，禁止改用漂移 HEAD。原 G2 审查范围为5a5e093c2e9b39abe1332e49d1df40d20f9fd33f；G1 PLAN PASS不变。三项发现尚未由独立主审确认关闭，开发方自测不代验收。

先核 RECEIPT.json、原字节 received/ 报告/修复任务/清单、DEVELOPER_RESPONSE.md、validation-1b4be23/VALIDATION.json 和 ORIGINAL_ZIP_INDEX.json，再核根 IMPLEMENTATION_IDENTITY.json。封存ZIP319项逐字节核验已完成，仓库原报告子集及新SDK的26份选择文件均明确列出；完整SDK/159份未复制项和官方原ZIP仍在记录位置，不能把仓库子集当完整运行或原ZIP。

请逐项复核：

1. **WORK-P3-IMPL-001 / High**：实际选中 security_master 的 event/available、修订及行hash进入标签依赖、可用时间、信息区间；晚到上市/退市更正不能被1月4日fit使用。读旧原四失败与新原四/新增边界，并独立检查 AFTER_CAUSAL_PROBE.json：收益0.1、最早可用2024-01-05T00:00:00Z、Jan4 fit train_count=0。检查相等/±1us、PIT修订及原17组答案不变，确认未通过改金融expected规避。
2. **WORK-P3-IMPL-002 / Medium**：proposal必须来自已验证终态manifest的唯一approvals条目，hash与解析使用同一次读取原字节；原无工件/后补、替换、非映射、不匹配拒绝。保留正常签封正向路径与终态不变，不把旁注文件提升为运行证据。核读取时替换的负例，不仅检查path.exists。
3. **WORK-P3-IMPL-003 / Medium**：直接调用公开compose及pipeline，必需两时钟，规范化同一UTC瞬间，session内全因子共同decision，拒绝未来available、混合cutoff及重复键；合成分数/血缘有可用时间和输入hash。核正常同刻、交集重新z、方向只一次、跨session网格及输入不变。旧fixture仅补显式公共时钟，冻结数字/原期望不变。

重新实际运行原字节 received/test_review_regressions.py（四项），集成 tests/research/test_g2_regressions.py 和10项 test_g2_boundaries.py。业务执行提交1b4be236e888805f5c4e45357b158fcdb6058df0已做新干净SDK与双OS各578、原16+4、原四、原91数学、扫描3控制及完整研究/替换/旧三Ref重放；实际命令/JUnit/coverage/wheel/数据/环境/hash在回执。若最终证据提交与业务执行不同，必须核src/tests/tools/workflow/锁/构建/扫描配置完全相同，并独立核最终CI的执行提交/原ZIP，不以旧564外推。

原91脚本字节未改，但其中硬编码的旧审查SHA/GPT Work执行字符串只作为源标签保留；本轮开发方复跑的真实执行者、业务提交与命令在 EXTRA_VERIFICATION.json，不能算本轮GPT Work本人执行。所有辅助测试失败与原四产品失败保留，首次直接pytest缺旧环境的5个setup errors不计通过，最终SDK自行配置原环境后578通过。

同时回归完整26项、五stage、全检验族/失败记录、ledger/cache/OOS/JSON+HTML、研究替换和原0.2三Ref正向重放。旧0.2锁和已归档旧0.3 wheel、1957冻结资产不变。实际部署/权限隔离、真正封存Test、真实生成过程证明/正式统计协议/金融标准、完整历史宿主/安装器字节仍分别NOT VERIFIED；不要求越权部署来关闭代码修复。

输出每项CLOSED或仍OPEN的代码行、反例、实际环境与独立执行证据，区分仅审阅和本人新执行；列出剩余技术/部署/金融/人工验收条件。无用户Phase3验收、main合并、标签或P4授权，不代用户批准这些动作。
