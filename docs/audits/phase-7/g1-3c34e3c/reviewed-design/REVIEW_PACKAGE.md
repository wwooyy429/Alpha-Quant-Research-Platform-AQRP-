# Phase7 固定版本 G1 资料导航 · 草案待整合

仅用于设计预审，主审GPT Work。正式Phase6基线：**d563347ad11e1f26e131dc06e343250282c05c33**；计划PR与AQRP_FIXED_REVIEW_SHA：待主开发实际创建和核实，不使用漂移HEAD。

| 审查内容 | 资料 |
|---|---|
| 目标、授权、范围和实施顺序 | PLAN.md、SCOPE_AND_DEPENDENCIES.md、AUTHORIZATION.json |
| 精确5项原需求、3MVP/2CR、跨阶段追踪 | REQUIREMENTS_SNAPSHOT.json、REQUIREMENTS_TRACEABILITY.md、CROSS_CUTTING_REQUIREMENTS.json、SOURCE_EXCERPTS.md |
| 适配器/能力报告/原服务调用/真实血缘、19研究点/10执行点 | INTERFACE_DRAFT.md、EXECUTION_SELECTION_CONTRACT.md、COMPATIBILITY_IMPACT.md、BASELINE_FACTOR_REFS_CANDIDATE.json |
| 数学/经济不变、比较白名单、独立候选与容差 | MATH_AND_COMPARISON_CONTRACT.md、GOLDEN_CANDIDATES.json、MAIN_REFERENCE_METHOD.md、MAIN_PIPELINE_CANDIDATES.json、draft-origin/MAIN_REFERENCE_EXECUTION.json、E2E_PROTOCOL_CANDIDATES.json |
| 自动化/实际浏览器/故障/双OS原包与seal要求 | TEST_AND_EVIDENCE_PLAN.md |
| 旧P6包守门/83模块及禁止competition约束的阶段兼容、新P7 gate与双OS上传接线 | PACKAGE_GATE_AND_CI_PLAN.md、PACKAGE_GATE_SOURCE_SNAPSHOT.json、COMPATIBILITY_IMPACT.md |
| 预设主层金融可行性、原失败夹具和有限顺序模型 | FINANCIAL_FEASIBILITY.md、FINANCIAL_REFERENCE_METHOD.md、FINANCIAL_REFERENCE_EXECUTION.json、FINANCIAL_FEASIBILITY_CANDIDATES.json、FINANCIAL_MODEL_BOUNDS.json、SUPERSEDED_FINANCIAL_COUNTEREXAMPLES.json；115MB逐步路径外部保留，不进Git |
| 具体设计提案、外部阻断与延期 | OPEN_QUESTIONS.md、STATUS.json |

请主审重点核对：(1)所有原需求/Phase7十项交付有具体映射；(2)通用工程适配必需能力充分，未知比赛不被悄悄填默认；(3)全链各阶段和全Task完成屏障无遗漏；(4)候选版本/参数/研究预算与Strategy精确pin、旧实验不互相污染；(5)替换测试不只检验符号或复用产品expected；(6)不导入AQRP的独立参考/原始字节证明能验证金融与来源；(7)工程干净环境运行与真实部署/隔离/金融批准分列，既有延期不被P7工程PASS覆盖。

本轮只有开发方有限字面设计算术和独立于产品导入的参考候选，没有P7产品测试或独立审计结论。设计参考40条有限算术核对、19截面171条OLS正交/反向性质、768条有限模型路径/109350条开发模型检查均不并入SDK测试数，不证明真实账本或产品正确。G1建议通过不等于实现许可；任何C-P7设计边界接受与后续实现授权仍由用户明确决定。若主审发现技术缺口，应给固定SHA/复现或设计反例、严重度、需求ID、预期与修订要求，不审漂移分支头部。
