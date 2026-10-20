# V3.1 六项专项审计（开发方设计自查，待Gemini核实）

范围仅设计；“已覆盖”指有明确设计条款，不代表实现/测试/独立审查通过。关联QA-005及TRACEABILITY。

| 专项 | 需求映射 | 实际设计位置及检查要点 | 当前判断/后续证据 |
|---|---|---|---|
| 1 阶段依赖一致性 | GOV-004、FACTOR-011、RESEARCH-009、BT-010、UI-007、INT-005 | ROADMAP/TESTING：P2 Registry、P3研究、P5组合回测、P6网页CLI、P7全链；CSV依赖图作无环/阶段自查 | 设计已列；自动核查结果见SELF_CHECK；未执行任何未来测试 |
| 2 数据契约完整性 | DATA-001–013、ARCH-003 | DATA_CONTRACT逐项覆盖标识/市场、货币单位、时区日历、三时间、行动复权、停退市/历史池、缺失重复异常、快照校验 | 8类均有规则；源PIT真实性/具体市场profile未定，不宣称数据验收 |
| 3 回测事件时序 | BT-001–009、QA-003 | BACKTEST_CONTRACT：确认→信号→决策→风控→订单→撮合→Fill→原子资金→估值；eligible限制、同刻顺序/部分成交/公司行动/交收 | 设计已列；P5自动边界/不变量/Golden才证明实现 |
| 4 样本外/多重检验 | VALID-003–008、EXP-001–004 | RESEARCH_PROTOCOL：预注册方向参数处理期限、Test封存/访问、标签区间purge、试验family和全部候选、HAC/校正/过拟合风险 | 实际日期/阈值/预算待批准，技术隔离P3实现，不能提前批准因子 |
| 5 MVP与完整分级 | 每条需求tier/phase/dependencies、GOV-003、INT-006 | requirements.csv/REQUIREMENTS/ROADMAP：四级、固定阶段、未来路径与状态；高级/生产另授权 | 分级提案待批准；V3.0必须项不因非MVP而豁免 |
| 6 自动测试/人工证据 | QA-001–007、GOV-008–009 | TESTING/GOLDEN/ACCEPTANCE与模板：独立答案/依据/容差、边界/性质/独立参考，实际命令/日志/CI与SHA，Gemini复核和用户批准 | 证据要求已列；当前只有文档自查，未有Gemini或用户批准 |

需Gemini核实本自查是否存在语义遗漏或不可实施条件；实际审计结论由其原始报告给出，不能将此文件称双AI审查已通过。
