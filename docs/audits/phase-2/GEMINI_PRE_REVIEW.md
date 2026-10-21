# 给 Gemini 的 Phase 2 计划预审指令

角色：独立计划/架构/数学与安全审查者。本轮是Phase2实施前预审，不是实现验收；不要合并、打标签、写main或开发Phase3。仓库：https://github.com/wwooyy429/Alpha-Quant-Research-Platform-AQRP- 。本轮Draft PR与完整固定SHA以开发方交接回执和PR描述AQRP_FIXED_REVIEW_SHA为准，打开后先核对其头部，不审漂移的分支latest；如果不是指定SHA应停止并列出差异。

正式起点main/phase1-baseline=f579b2c99e762085772de6e70ba1fa98792a7add，附注对象1a8e47ee4be910aa7eeeefa430015e683a8aa6f5。用户明确授权“请正式开始进入phase 2”；AUTHORIZATION.json仅登记原话与范围，不能当Gemini预审已通过或Phase2验收。

请读取 docs/audits/phase-2/ 中 AUTHORIZATION、PLAN、REQUIREMENTS_SNAPSHOT/TRACEABILITY、FACTOR_IMPLEMENTATION_SPEC、SECURITY_AND_COMPATIBILITY、TEST_PLAN、GOLDEN_REFERENCE、golden_cases.json、reference_arithmetic.py及开发方自查/manifest。对照冻结docs/INTERFACES、ARCHITECTURE、DATA_CONTRACT、TESTING、requirements.csv，以及实际P1 src/aqrp/core/contracts.py、data/query.py、actions.py、pit.py，不能只审开发方摘要。

重点核对：
1. 519项P1发布清单、main/tag/合并父节点和授权是否可追溯；继承执行边界仍准确披露，开发方结果未冒充Gemini。
2. canonical phase=2恰好10项（9个FACTOR+SEC-001），106条/16组不漂移；P2只做接口、注册替换、版本及三基础因子，不提前研究/组合/回测/UI。
3. FactorSpec/Ref/Context/SignalBatch、唯一键、参数类型与深层冻结、范围解析、代码hash/精确版本pin、同版本异内容拒绝、停用/rollback/运行中pin是否一致。
4. Approved术语在代码测试准入和P3/P5金融审批之间是否清楚且符合冻结接口；无研究证据不得伪造ResearchValidated/StrategyApproved。
5. 只有reviewed builtin才能加载；hash覆盖完整影响bundle，receipt不是插件自报；外部module/path/callable/表达式在导入前拒绝。只读对象/AST/monkeypatch不等于OS沙箱，SEC-001限定范围是否足够，限制是否应阻断本阶段。
6. P1 PIT/公司行动/query/view的真实能力是否足以支持计划；不得从最终as_of倒算过去、跨证券/跨缺失session滚动，拆股量单位正确。decision_time保守available_at/零模拟延迟是否明确，不将原bar时间冒充调整依赖时间。
7. 独立重算21/100、−21/100、3/5、B证券−1/5/1/5/0、拆股0及纯分红价格收益−1/100；Golden固定答案是否独立，缺失/零量/非法输入/未来mutation与正向控制是否充分。代码脚本只标准库不import待测AQRP，执行它不是运行尚不存在的因子实现。
8. 测试/覆盖率门槛、Windows/Ubuntu锁定wheel验证、实际原始产物/hash/失败留存与选择性上传清单是否可审；不把计划自查或旧102测试称P2业务通过。

请报告固定SHA、环境/工具/权限、实际已读取文件与命令、独立数学输入/结果/容差，按逐项证据分Static Review/Independently Executed/NOT VERIFIED。缺文件或未执行不能打印全通过；仅文字PASS不替代原日志。请按Finding ID/严重性/需求ID/路径定位/影响/建议逐条输出，并判断PLAN VERDICT=PASS/PASS WITH CONDITIONS/FAIL、阻断项及哪些须用户设计决定。

保留Phase1历史限制，不索要真实密钥，不运行真实订单，不修改旧报告；如不能执行3.13.16只说明实际使用的数学环境与局限，不假称跑SDK。开发方会归档原件、处理阻断项及固定新SHA复核；计划通过不代表实现通过、人工验收或合并/发布授权。
