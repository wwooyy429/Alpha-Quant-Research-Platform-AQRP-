# Phase2 计划预审接收、勘误及开发方处理

最新补充：旧预审数学.py/.log已收到并复跑日志相符；参考Volume错式、证券B常量比较及无hash/SDK/ZIP验证等详见MATH_SUPPLEMENT_RECONCILIATION.md。原接收记录保留历史事实；新增核对仍待Gemini确认，不能据此关闭全部实现执行缺口。

当前增量：Gemini已在2a70dc6实现报告中认可八项勘误，并关闭F-P2-PRE-001/002（限定受审内置工程范围）。以下“待确认”等为此前开发方处理快照；当前原件、12项新增事实更正与执行证据缺口见IMPLEMENTATION_AUDIT_RESPONSE.md及gemini/IMPLEMENTATION_AUDIT_INDEX.json，不能据PASS宣告全部证据闭环或用户验收。

用户转交Gemini报告，原字节保存在gemini/aqrp_phase2_plan_pre_review_report.md，hash及来源见PRE_REVIEW_INDEX.json。固定4f8b0de正确，正式基线f579b2c正确，报告PLAN PASS且仅两项Low、没有Critical/High；用户本次明确允许无阻断继续已授权开发。状态进入IMPLEMENTING，不等于实现审查或人工验收。正文错误单独纠正，不修改报告原件或正确Golden答案。

| 项 | 报告文字 | 规范/处理 |
|---|---|---|
| FACTOR-001 | compute(context)及简化规格 | 仍按冻结compute(view,context)及完整12项元数据，不删available_at/血缘 |
| FACTOR-002 | Registry | 实际是SignalBatch字段/唯一键/血缘；Registry为003 |
| FACTOR-003 | 参数管理 | 实际涵盖Registry/resolve/兼容/停用/回滚/参数；不缩减 |
| FACTOR-004 | 代码hash版本 | 实际是Momentum；hash/准入关联003/SEC-001 |
| FACTOR-005 | 生命周期 | 实际是Reversal；F-P2-PRE-001的语义建议应关联003/010，不改变005公式 |
| FACTOR-006 | Momentum/Reversal/Volatility | 实际是Volume；不新增波动率，三内置仍momentum/reversal/volume |
| FACTOR-010 | 多资产 | 实际是配置/选择/版本pin/回滚，权重只元数据，留P4消费 |
| FACTOR-011 | DAG拓扑 | 实际是P2注册替换/API兼容测试；不新增DAG系统 |
| FACTOR-007/009 | 中性化/IC | 007是Price-Volume，009是金融批准证据隔离，均P3；阶段虽同，职责不可重写 |
| SEC-001 | AST等同防系统调用 | 只准入已审内置代码，静态规则辅助；Python对象/AST不构成OS边界，不承诺阻止恶意同权限代码 |
| AST节点Exec/Eval | 作为Python3强制节点 | Python3为Call(Name/Attribute)语法；检测eval/exec/compile/__import__等调用和危险导入，不使用不存在的ast.Exec/ast.Eval |
| 3/5名称 | 截面分位/权重 | 是Volume 200/mean(100,150)-1；无P4权重计算 |
| float误差0 | 数学有理数误差均0 | 位对齐可能仅比较同一float舍入，不等于相对精确有理数误差0；开发方另存Fraction.from_float核对，不改abs1e-12/rel1e-10 |
| decision_time | 以除权公告时间为准 | decision_time为请求冻结决策时点，公告/生效为依赖；必须依赖可见且生效，signal available_at保守=decision_time，不把决策等同公告 |
| 分支/PR标题 | feature/phase-2-factor-system / feat标题 | 实际feature/phase-2-factor-registry / docs计划PR；不另建错误分支 |
| 数学原脚本/日志 | 声称附两命名文件 | 本次只收到报告，未附aqrp_phase2_math_verification.py/.log。记录为审查方自述执行，不能伪造原件或报已独立复跑 |
| 启动授权范围 | 仅许可计划编制 | 用户原始启动+本次继续开发授权有效；Gemini不拥有批准用户范围的权力 |

F-P2-PRE-001采纳：代码枚举使用ENGINEERING_APPROVED，批准用途严格TEST_ONLY，Financial approval为NONE，不产生ResearchValidated/StrategyApproved。F-P2-PRE-002采纳：仅审查内置与加载前hash白名单，补充AST linter，明确不可信插件Unsupported及OS沙箱未实现。两项现为DEVELOPER CLOSED — GEMINI CONFIRMATION PENDING，仅限本阶段受控内置范围。证据：registry.py EngineeringState及三因子receipt显式ENGINEERING_APPROVED/TEST_ONLY/NONE；test_no_unapproved_execution_modes、test_unknown_code_rejected_before_loading、test_code_receipt_denial、test_sec_001_static_rules_are_supplemental及完整SDK/双OS CI通过，见IMPLEMENTATION_TRACEABILITY.md和implementation/EVIDENCE_INDEX.json。不把AST或Python对象称为OS沙箱，不把工程审批当金融批准。Gemini尚未复核本次实现，不代替审查方关闭发现。

以上均属对原方案的事实更正/术语细化，未扩大范围或破坏P0/P1契约，未发现需阻断整个阶段的设计冲突。错误需求分类不用于实现；以canonical CSV及本阶段10项追踪为准。报告PASS不覆盖新实现，完成后固定新SHA送Gemini实现复核。不得合并、打标签或进入P3。

实施增量：业务固定8183b3762b56c466b989d9062a720b5f0d31172a，254测试及双OS CI通过，原始ZIP/hash检查通过。完整实现审查入口IMPLEMENTATION_REVIEW_PACKAGE.md；上述表的勘误为开发方意见，尚待Gemini逐项确认。原4f计划/SELF_CHECK/MANIFEST保持历史原件，不以旧“未实现”字段覆盖当前状态。
