# Phase 3 实际实现追踪（26项）

2026-10-22 最新独立复核：**G2 TECHNICAL PASS WITH CONDITIONS / HUMAN ACCEPTANCE PENDING**。GPT Work已对固定9ac5db069287a6e4a095e25ae8c3cc8fa229cded确认001 High、002/003 Medium均CLOSED，无新增阻断代码问题；独立SDK578、原四/旧16+4/91数学/扫描3及双OS各578与原ZIP核验通过。原报告/关闭/26项覆盖/390件hash核验见docs/audits/phase-3/g2-9ac5db0/。真实隔离/正式Test/金融批准/完整历史宿主仍未验证；Phase3未人工验收/发布，无部署、合并、标签或P4。以下旧状态按其原轮次保留。


固定需求目录仍为106项；本阶段只取原phase=3的26项（23 MVP、3 Competition Ready），没有变更原业务分类或新增后续阶段范围。原G1需求/追踪快照保持原字节。本表把规划路径映射到实际代码/测试；它不是独立审查、金融批准或用户验收。

代码均位于src/aqrp，下表测试均为真实tests/路径。精确源码bundle/完整文件hash见 IMPLEMENTATION_IDENTITY.json；实际SDK/JUnit/coverage/原始ZIP及固定提交关系见 IMPLEMENTATION_VALIDATION.json。开发迭代失败亦保留。

| ID / 级别 | 实际实现 | 实际验证与证据 |
|---|---|---|
| DATA-012 / CR | data/exposures.py，parent绑定的PIT Parquet侧车、行业/市值/命名风险暴露与null语义 | research/test_pipeline.py、test_boundary_controls.py：身份/币种/版本、未来/过期/冲突/修订顺序/缺失/hash |
| FACTOR-007 / CR | factors/admission.py、contracts.py、builtins.py；新price_volume精确Ref及新工程receipt | factors/test_price_volume.py：0.06与-0.1；原三因子回归、旧wheel执行与原发布运行重放 |
| FACTOR-009 / MVP | 原FactorRegistry工程域独立；validation/approvals.py研究proposal/人工签封；无策略批准 | research/test_evaluator.py：证据/标准/数值/冻结时间/终态proposal绑定拒绝，人工决策仅ResearchValidated |
| RESEARCH-001 / MVP | services/research.py的research与evaluate_sealed，统一编排 | research/test_service.py、test_service_guards.py；tools/research_smoke.py实际贯通 |
| RESEARCH-002 / MVP | research/numerics.py、pipeline.py：MAD/线性分位裁剪/null/平均秩/样本z | research/test_numerics.py、test_frozen_golden.py、test_pipeline.py；常数/极端/缺失/性质测试 |
| RESEARCH-003 / CR | pipeline.py：PIT行业虚拟变量+log市值OLS，固定rcond、秩/排除/拟合诊断 | test_numerics.py独立正常方程/正交；test_pipeline.py真实侧车与残差、缺暴露/秩亏 |
| RESEARCH-004 / MVP | numerics.rolling，按完整session网格Delay/Delta/Mean/Std/Correlation/Sum/Min/Max | test_numerics.py各算子独立答案；test_pipeline.py整日缺口不压缩，时间/证券对齐 |
| RESEARCH-005 / MVP | ranks、ts_rank、conditional封闭比较白名单及pipeline算子链 | test_numerics.py、test_frozen_golden.py平均并列秩与5/6；拒绝未知表达式 |
| RESEARCH-006 / MVP | pipeline五stage真实工件/计数/无效原因/fit_scope/input_ref/hash；ledger存JSON | test_service.py各工件实际存在；test_pipeline.py实际中性化与SKIPPED引用 |
| RESEARCH-007 / MVP | pipeline.compose：共同交集再z、预注册权重/方向、原与方向后相关、冗余诊断 | test_pipeline.py、test_frozen_golden.py独立答案；test_service.py及research_smoke真实合成报告，合成×期限计入m |
| RESEARCH-008 / MVP | experiments/ledger.py全配置/权限/版本缓存，hypotheses及参数候选/重复指纹 | test_ledger.py、test_service.py参数网格/缓存/重现；test_service_guards.py冻结后改变拒绝 |
| RESEARCH-009 / MVP | 同一research服务只替换Momentum→Reversal Ref | test_service.py完整替换；research_smoke.py真实五stage/统计/OOS/报告/实验替换，未依赖P4/P5 |
| VALID-001 / MVP | numerics IC/RankIC/Mean/std(ddof1)/非年化ICIR/正值与零值比例；labels真实next-open行动口径 | test_numerics.py、test_frozen_golden.py及17组test_labels.py，均使用独立预定答案 |
| VALID-002 / MVP | group_metrics及services.measurements：分层/TMB/单调/期限衰减/年度与stage/split | test_frozen_golden.py冻结组均值/TMB；test_service.py全链实际多期限/年度结果及无效n |
| VALID-003 / MVP | validation/splits.py：半开范围、信息闭区间purge、session embargo、保守跨fold保护与去重 | test_splits.py、test_boundary_controls.py、test_service_guards.py真实OOS和fit/Test边界 |
| VALID-004 / MVP | evaluator.py、evaluate_sealed、冻结配置/期限方向；真实OS验证入口、统一私有控制索引、原子预算/污染 | test_evaluator.py、test_host_controls.py、test_service_guards.py验证逻辑及正负控制；**实际多主体部署未授权/NOT VERIFIED，正式Test未执行** |
| VALID-005 / MVP | inference.py增长带宽HAC、完整网格/资格/拒绝原因；工程近似p不当正式p | test_inference.py、test_frozen_golden.py、hac_growth_cases及原参考日志；正式模型证明/主审方法及用户协议仍需真实证据 |
| VALID-006 / MVP | 注册先于计算，全部候选×期限（含合成）、失败/重复/访问与预算hash链 | test_ledger.py、test_service.py检验族6槽位、test_evaluator.py失败/崩溃/并发/路径改名不重置 |
| VALID-007 / MVP | inference.adjust_pvalues及冻结全family定义/失败null/保守校正槽位 | test_inference.py、test_frozen_golden.py Holm/BY/BH与m=4失败项；BH缺预定依据拒绝 |
| VALID-008 / MVP | approvals.py核预定标准/冻结/实际指标/完整family/独立证据，返回实际拒绝原因 | test_evaluator.py后设标准/缺证据/NaN/原run无proposal拒绝；无金融自动批准 |
| EXP-001 / MVP | ledger UUID/不可变配置与版本/实际环境/seed/成本不适用/UTC事件/终态工件hash | test_ledger.py及完整SDK environment.json、原始commands/JUnit/coverage、research runs |
| EXP-002 / MVP | 每候选×期限注册、失败run、参数网格、重复/先前数据尝试数、超预算仍留痕 | test_service.py多参数同因子真实计算；test_ledger.py全部尝试与不可删改终态；无赢家筛选自动化 |
| EXP-003 / MVP | reproduction.py当前投影重现、manifest只读比较、原0.2独立环境与原发布运行核对 | test_reproduction.py原wheel实际执行与66原文件/3原运行，篡改/缺制品/漂移/不同身份拒绝；old SDK raw证据 |
| EXP-004 / MVP | approvals.py标准/冻结/候选期限身份与真实proposal；签封人工决策另append，不改终态 | test_evaluator.py审批边界、缺原proposal拒绝、终态原manifest不变；**本轮无真实金融批准** |
| QA-004 / MVP | G1独立答案原件与版本保留，新增测试对接待测实现，不用待测函数生成期望 | 原15/28组、visibility17、growth冻结文件不改；test_frozen_golden/test_labels及原参考脚本。按用户最新职责，**GPT Work主审新固定SHA实现尚待进行** |
| INT-001 / MVP | 数据→PIT股票池→精确Ref/参数→五stage→标签/IC/分组/OOS→JSON/HTML→实验，全用真实实现 | test_service.py/guards及干净wheel research_smoke、CLI同服务、原始SDK与双OS证据 |

CR表示Competition Ready三项，其余23项为MVP。本表没有把P4/P5成本/风险/回测、P6网页或P7完整替换当成本阶段依赖。

U-001要求的真实OS权限证据须有单独部署授权后取得；本轮模拟Host policy控制和公开合成链路不冒充它。正式Test、金融批准、独立实现审核及人工阶段验收都是未被G1或开发方自测替代的门禁。尚未取得的这些证据需在主审结论中明确保留。


G2修复增量：VALID-001/002/003、QA-004、INT-001主档时钟及fit边界；FACTOR-009、VALID-008、EXP-001/004终态proposal成员/原字节；RESEARCH-007、QA-004、INT-001公共合成共同cutoff/未来可用拒绝及血缘。实际新增测试research/test_g2_regressions.py（4原期望）和test_g2_boundaries.py（10边界），原发现仍待GPT Work确认关闭，开发自测不代验收。完整原26项表不删除。
