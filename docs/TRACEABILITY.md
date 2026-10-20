# 双向需求追踪矩阵（待审）

源要求→需求ID→设计/未来实现→分阶段测试；实际实现后须把规划路径替换/补充为真实文件、测试ID、Commit及证据。空缺不能当已实现。需求的完整输入输出/验收定义见 REQUIREMENTS 和 requirements.csv。

当前实施跟踪：用户已授权Phase1，其14项需求与拟实现/测试映射见[audits/phase-1/PLAN.md](audits/phase-1/PLAN.md)。计划预审已PASS；实际14项实现/测试见[audits/phase-1/IMPLEMENTATION_TRACEABILITY.md](audits/phase-1/IMPLEMENTATION_TRACEABILITY.md)，当前已收到74bdb92实现PASS原报告，报告勘误/执行证据澄清OPEN；详见audits/phase-1/IMPLEMENTATION_AUDIT_RESPONSE.md。下表保留冻结设计目录；其Planned/设计待审是原编制时状态，不代表当前P0/P1进展；P0已发布基线版本保持不变。

| ID | 来源 | 等级/阶段 | 前提需求 | 设计 | 未来代码 / 测试 | 状态 |
|---|---|---|---|---|---|---|
| GOV-001 | V3.0§1.1;V3.0§1.2;V3.0§1.3;V3.0§22;V3.1§5;V3.2§9 | MVP / 0 | NONE | [PROJECT_CHARTER.md](PROJECT_CHARTER.md) | `docs/PROJECT_CHARTER.md` / `docs/audits/phase-0/` | Planned，设计待审 |
| GOV-002 | V3.0§14.1;V3.0§14.2;V3.2§2 | MVP / 0 | GOV-001 | [PROJECT_CHARTER.md](PROJECT_CHARTER.md) | `docs/PROJECT_CHARTER.md` / `docs/audits/phase-0/` | Planned，设计待审 |
| GOV-003 | V3.0§14.3;V3.0§14.4;V3.0§14.5;V3.1§8 | MVP / 0 | GOV-001 | [REQUIREMENTS.md](REQUIREMENTS.md) | `docs/REQUIREMENTS.md` / `docs/audits/phase-0/` | Planned，设计待审 |
| GOV-004 | V3.0§15.1;V3.0§15.2;V3.0§15.3;V3.0§15.4;V3.0§15.5;V3.0§18;V3.1§1 | MVP / 0 | GOV-001 | [ROADMAP.md](ROADMAP.md) | `docs/ROADMAP.md` / `docs/audits/phase-0/` | Planned，设计待审 |
| GOV-005 | V3.0§19;V3.2§4.7;V3.2§4.9 | MVP / 0 | GOV-004 | [ACCEPTANCE.md](ACCEPTANCE.md) | `docs/ACCEPTANCE.md` / `docs/audits/phase-0/` | Planned，设计待审 |
| GOV-006 | V3.0§17.1;V3.0§17.2;V3.0§17.3;V3.2§3;V3.2§4.8 | MVP / 0 | GOV-005 | [ACCEPTANCE.md](ACCEPTANCE.md) | `docs/ACCEPTANCE.md` / `docs/audits/phase-0/` | Planned，设计待审 |
| GOV-007 | V3.0§21;V3.2§2 | MVP / 0 | GOV-002 | [PROJECT_CHARTER.md](PROJECT_CHARTER.md) | `docs/PROJECT_CHARTER.md` / `docs/audits/phase-0/` | Planned，设计待审 |
| GOV-008 | V3.0§16;V3.2§1;V3.2§4;V3.2§5;V3.2§7 | MVP / 0 | GOV-004 | [ACCEPTANCE.md](ACCEPTANCE.md) | `docs/ACCEPTANCE.md` / `docs/audits/phase-0/` | Planned，设计待审 |
| GOV-009 | V3.0§16;V3.0§20;V3.2§4.6;V3.2§6;V3.2§8 | MVP / 0 | GOV-008 | [ACCEPTANCE.md](ACCEPTANCE.md) | `docs/ACCEPTANCE.md` / `docs/audits/phase-0/` | Planned，设计待审 |
| GOV-010 | V3.2-Baseline§1;V3.2-Baseline§2;V3.2-Baseline§3;V3.2-Baseline§4;V3.2-Baseline§5;V3.2-Baseline§6 | MVP / 0 | GOV-005;GOV-006;GOV-008 | [BASELINE.md](BASELINE.md) | `docs/BASELINE.md` / `docs/audits/phase-0/` | Planned，设计待审 |
| ARCH-001 | V3.0§2.1;V3.0§2.3;V3.0§9 | MVP / 0 | GOV-001 | [ARCHITECTURE.md](ARCHITECTURE.md) | `docs/ARCHITECTURE.md` / `docs/audits/phase-0/` | Planned，设计待审 |
| ARCH-002 | V3.0§2.2 | MVP / 0 | ARCH-001 | [ARCHITECTURE.md](ARCHITECTURE.md) | `docs/ARCHITECTURE.md` / `docs/audits/phase-0/` | Planned，设计待审 |
| ARCH-003 | V3.0§2.4;V3.1§2;V3.1§3 | MVP / 0 | ARCH-001 | [INTERFACES.md](INTERFACES.md) | `docs/INTERFACES.md` / `docs/audits/phase-0/` | Planned，设计待审 |
| DATA-001 | V3.0§4.1;V3.0§4.3;V3.1§2 | MVP / 1 | ARCH-003 | [DATA_CONTRACT.md](DATA_CONTRACT.md) | `src/aqrp/data/` / `tests/data/test_data_001.py` | Planned，设计待审 |
| DATA-002 | V3.0§4.2;V3.0§4.3;V3.1§2 | MVP / 1 | DATA-001 | [DATA_CONTRACT.md](DATA_CONTRACT.md) | `src/aqrp/data/` / `tests/data/test_data_002.py` | Planned，设计待审 |
| DATA-003 | V3.0§4.1;V3.0§4.4;V3.0§18 | MVP / 1 | DATA-002 | [DATA_CONTRACT.md](DATA_CONTRACT.md) | `src/aqrp/data/` / `tests/data/test_data_003.py` | Planned，设计待审 |
| DATA-004 | V3.0§4.1;V3.0§4.4;V3.1§2 | MVP / 1 | DATA-002 | [DATA_CONTRACT.md](DATA_CONTRACT.md) | `src/aqrp/data/` / `tests/data/test_data_004.py` | Planned，设计待审 |
| DATA-005 | V3.0§4.1;V3.0§4.4;V3.1§2 | MVP / 1 | DATA-002 | [DATA_CONTRACT.md](DATA_CONTRACT.md) | `src/aqrp/data/` / `tests/data/test_data_005.py` | Planned，设计待审 |
| DATA-006 | V3.0§4.4;V3.1§2 | MVP / 1 | DATA-001 | [DATA_CONTRACT.md](DATA_CONTRACT.md) | `src/aqrp/data/` / `tests/data/test_data_006.py` | Planned，设计待审 |
| DATA-007 | V3.0§4.3;V3.0§13;V3.1§2;V3.1§7 | MVP / 1 | DATA-001 | [DATA_CONTRACT.md](DATA_CONTRACT.md) | `src/aqrp/data/` / `tests/data/test_data_007.py` | Planned，设计待审 |
| DATA-008 | V3.0§18;V3.0§2.2 | MVP / 1 | DATA-001;DATA-007 | [DATA_CONTRACT.md](DATA_CONTRACT.md) | `src/aqrp/data/` / `tests/data/test_data_008.py` | Planned，设计待审 |
| DATA-009 | V3.0§4.5;V3.0§11.2 | MVP / 1 | DATA-002 | [DATA_CONTRACT.md](DATA_CONTRACT.md) | `src/aqrp/data/` / `tests/data/test_data_009.py` | Planned，设计待审 |
| DATA-010 | V3.0§4.1;V3.0§4.2;V3.0§3.4 | Advanced Research / POST7 | DATA-002 | [DATA_CONTRACT.md](DATA_CONTRACT.md) | `src/aqrp/data/` / `tests/data/test_data_010.py` | Deferred，设计待审 |
| DATA-011 | V3.1§2 | MVP / 1 | DATA-001 | [DATA_CONTRACT.md](DATA_CONTRACT.md) | `src/aqrp/data/` / `tests/data/test_data_011.py` | Planned，设计待审 |
| DATA-012 | V3.0§4.4;V3.0§7.3 | Competition Ready / 3 | DATA-002 | [DATA_CONTRACT.md](DATA_CONTRACT.md) | `src/aqrp/data/` / `tests/data/test_data_012.py` | Planned，设计待审 |
| DATA-013 | V3.0§4.1;V3.0§18;V3.1§5 | Competition Ready / 7 | DATA-008;INT-006 | [DATA_CONTRACT.md](DATA_CONTRACT.md) | `src/aqrp/competition/` / `tests/competition/test_data_013.py` | Planned，设计待审 |
| FACTOR-001 | V3.0§3.1;V3.0§3.3 | MVP / 2 | DATA-002;DATA-008 | [INTERFACES.md](INTERFACES.md) | `src/aqrp/factors/` / `tests/factors/test_factor_001.py` | Planned，设计待审 |
| FACTOR-002 | V3.0§3.2 | MVP / 2 | FACTOR-001 | [INTERFACES.md](INTERFACES.md) | `src/aqrp/factors/` / `tests/factors/test_factor_002.py` | Planned，设计待审 |
| FACTOR-003 | V3.0§2.1;V3.0§3.5;V3.1§1 | MVP / 2 | FACTOR-001;SEC-001 | [INTERFACES.md](INTERFACES.md) | `src/aqrp/factors/` / `tests/factors/test_factor_003.py` | Planned，设计待审 |
| FACTOR-004 | V3.0§3.4;V3.0§18 | MVP / 2 | FACTOR-002 | [INTERFACES.md](INTERFACES.md) | `src/aqrp/factors/` / `tests/factors/test_factor_004.py` | Planned，设计待审 |
| FACTOR-005 | V3.0§3.4;V3.0§18 | MVP / 2 | FACTOR-002 | [INTERFACES.md](INTERFACES.md) | `src/aqrp/factors/` / `tests/factors/test_factor_005.py` | Planned，设计待审 |
| FACTOR-006 | V3.0§3.4;V3.0§18 | MVP / 2 | FACTOR-002 | [INTERFACES.md](INTERFACES.md) | `src/aqrp/factors/` / `tests/factors/test_factor_006.py` | Planned，设计待审 |
| FACTOR-007 | V3.0§3.4 | Competition Ready / 3 | FACTOR-003 | [INTERFACES.md](INTERFACES.md) | `src/aqrp/factors/` / `tests/factors/test_factor_007.py` | Planned，设计待审 |
| FACTOR-008 | V3.0§3.4 | Advanced Research / POST7 | FACTOR-003;INT-004 | [ROADMAP.md](ROADMAP.md) | `src/aqrp/factors/` / `tests/factors/test_factor_008.py` | Deferred，设计待审 |
| FACTOR-009 | V3.0§1.3;V3.0§3.5;V3.0§12.3;V3.0§18 | MVP / 3 | FACTOR-003;VALID-008 | [RESEARCH_PROTOCOL.md](RESEARCH_PROTOCOL.md) | `src/aqrp/factors/` / `tests/factors/test_factor_009.py` | Planned，设计待审 |
| FACTOR-010 | V3.0§3.5;V3.0§13 | MVP / 2 | FACTOR-003 | [INTERFACES.md](INTERFACES.md) | `src/aqrp/factors/` / `tests/factors/test_factor_010.py` | Planned，设计待审 |
| FACTOR-011 | V3.0§3.6;V3.1§1;V3.2§7 | MVP / 2 | FACTOR-004;FACTOR-005 | [TESTING.md](TESTING.md) | `src/aqrp/factors/` / `tests/factors/test_factor_011.py` | Planned，设计待审 |
| FACTOR-012 | V3.0§3.3;V3.0§11.2;V3.1§7 | MVP / 2 | FACTOR-001;SEC-001 | [ENVIRONMENT_AND_SECURITY.md](ENVIRONMENT_AND_SECURITY.md) | `src/aqrp/factors/` / `tests/factors/test_factor_012.py` | Planned，设计待审 |
| RESEARCH-001 | V3.0§5.1;V3.0§12.1 | MVP / 3 | FACTOR-003 | [INTERFACES.md](INTERFACES.md) | `src/aqrp/research/` / `tests/research/test_research_001.py` | Planned，设计待审 |
| RESEARCH-002 | V3.0§5.1 | MVP / 3 | RESEARCH-001 | [RESEARCH_PROTOCOL.md](RESEARCH_PROTOCOL.md) | `src/aqrp/research/` / `tests/research/test_research_002.py` | Planned，设计待审 |
| RESEARCH-003 | V3.0§5.1;V3.0§18 | Competition Ready / 3 | RESEARCH-002;DATA-012 | [RESEARCH_PROTOCOL.md](RESEARCH_PROTOCOL.md) | `src/aqrp/research/` / `tests/research/test_research_003.py` | Planned，设计待审 |
| RESEARCH-004 | V3.0§5.2 | MVP / 3 | RESEARCH-001 | [RESEARCH_PROTOCOL.md](RESEARCH_PROTOCOL.md) | `src/aqrp/research/` / `tests/research/test_research_004.py` | Planned，设计待审 |
| RESEARCH-005 | V3.0§5.2 | MVP / 3 | RESEARCH-004 | [RESEARCH_PROTOCOL.md](RESEARCH_PROTOCOL.md) | `src/aqrp/research/` / `tests/research/test_research_005.py` | Planned，设计待审 |
| RESEARCH-006 | V3.0§5.3 | MVP / 3 | RESEARCH-002 | [INTERFACES.md](INTERFACES.md) | `src/aqrp/research/` / `tests/research/test_research_006.py` | Planned，设计待审 |
| RESEARCH-007 | V3.0§5.1 | MVP / 3 | RESEARCH-006 | [RESEARCH_PROTOCOL.md](RESEARCH_PROTOCOL.md) | `src/aqrp/research/` / `tests/research/test_research_007.py` | Planned，设计待审 |
| RESEARCH-008 | V3.0§5.1;V3.0§13 | MVP / 3 | EXP-001;RESEARCH-001 | [ARCHITECTURE.md](ARCHITECTURE.md) | `src/aqrp/research/` / `tests/research/test_research_008.py` | Planned，设计待审 |
| RESEARCH-009 | V3.1§1;V3.0§3.6 | MVP / 3 | RESEARCH-001;VALID-001 | [TESTING.md](TESTING.md) | `src/aqrp/research/` / `tests/research/test_research_009.py` | Planned，设计待审 |
| VALID-001 | V3.0§6.1;V3.0§6.2;V3.0§10.2 | MVP / 3 | RESEARCH-006 | [RESEARCH_PROTOCOL.md](RESEARCH_PROTOCOL.md) | `src/aqrp/validation/` / `tests/validation/test_valid_001.py` | Planned，设计待审 |
| VALID-002 | V3.0§6.1;V3.0§6.2 | MVP / 3 | VALID-001 | [RESEARCH_PROTOCOL.md](RESEARCH_PROTOCOL.md) | `src/aqrp/validation/` / `tests/validation/test_valid_002.py` | Planned，设计待审 |
| VALID-003 | V3.0§6.3;V3.1§4 | MVP / 3 | VALID-001 | [RESEARCH_PROTOCOL.md](RESEARCH_PROTOCOL.md) | `src/aqrp/validation/` / `tests/validation/test_valid_003.py` | Planned，设计待审 |
| VALID-004 | V3.0§6.4;V3.1§4 | MVP / 3 | VALID-003;EXP-002 | [RESEARCH_PROTOCOL.md](RESEARCH_PROTOCOL.md) | `src/aqrp/validation/` / `tests/validation/test_valid_004.py` | Planned，设计待审 |
| VALID-005 | V3.0§6.1;V3.0§6.5 | MVP / 3 | VALID-001 | [RESEARCH_PROTOCOL.md](RESEARCH_PROTOCOL.md) | `src/aqrp/validation/` / `tests/validation/test_valid_005.py` | Planned，设计待审 |
| VALID-006 | V3.0§6.4;V3.1§4 | MVP / 3 | EXP-002;VALID-004 | [RESEARCH_PROTOCOL.md](RESEARCH_PROTOCOL.md) | `src/aqrp/validation/` / `tests/validation/test_valid_006.py` | Planned，设计待审 |
| VALID-007 | V3.0§6.4;V3.1§4 | MVP / 3 | VALID-005;VALID-006 | [RESEARCH_PROTOCOL.md](RESEARCH_PROTOCOL.md) | `src/aqrp/validation/` / `tests/validation/test_valid_007.py` | Planned，设计待审 |
| VALID-008 | V3.0§6.5;V3.1§4 | MVP / 3 | VALID-004;VALID-007 | [RESEARCH_PROTOCOL.md](RESEARCH_PROTOCOL.md) | `src/aqrp/validation/` / `tests/validation/test_valid_008.py` | Planned，设计待审 |
| PORT-001 | V3.0§7.1 | MVP / 4 | FACTOR-009;VALID-008 | [INTERFACES.md](INTERFACES.md) | `src/aqrp/portfolio/` / `tests/portfolio/test_port_001.py` | Planned，设计待审 |
| PORT-002 | V3.0§7.2;V3.0§3.4 | MVP / 4 | PORT-001 | [INTERFACES.md](INTERFACES.md) | `src/aqrp/portfolio/` / `tests/portfolio/test_port_002.py` | Planned，设计待审 |
| PORT-003 | V3.0§7.2;V3.0§18 | Competition Ready / 4 | PORT-001;RISK-003 | [INTERFACES.md](INTERFACES.md) | `src/aqrp/portfolio/` / `tests/portfolio/test_port_003.py` | Planned，设计待审 |
| PORT-004 | V3.0§7.2 | Advanced Research / POST7 | PORT-001;INT-004 | [ROADMAP.md](ROADMAP.md) | `src/aqrp/portfolio/` / `tests/portfolio/test_port_004.py` | Deferred，设计待审 |
| RISK-001 | V3.0§7.3 | MVP / 4 | PORT-001 | [INTERFACES.md](INTERFACES.md) | `src/aqrp/risk/` / `tests/risk/test_risk_001.py` | Planned，设计待审 |
| RISK-002 | V3.0§7.3 | Competition Ready / 4 | PORT-001;DATA-012 | [INTERFACES.md](INTERFACES.md) | `src/aqrp/risk/` / `tests/risk/test_risk_002.py` | Planned，设计待审 |
| RISK-003 | V3.0§7.3 | Competition Ready / 4 | PORT-001;DATA-005 | [INTERFACES.md](INTERFACES.md) | `src/aqrp/risk/` / `tests/risk/test_risk_003.py` | Planned，设计待审 |
| RISK-004 | V3.0§7.3;V3.0§11.2 | MVP / 4 | RISK-001 | [INTERFACES.md](INTERFACES.md) | `src/aqrp/risk/` / `tests/risk/test_risk_004.py` | Planned，设计待审 |
| BT-001 | V3.0§8.1;V3.1§3 | MVP / 5 | PORT-001;RISK-004;DATA-002 | [BACKTEST_CONTRACT.md](BACKTEST_CONTRACT.md) | `src/aqrp/backtest/` / `tests/backtest/test_bt_001.py` | Planned，设计待审 |
| BT-002 | V3.0§8.2;V3.1§3 | MVP / 5 | BT-001 | [BACKTEST_CONTRACT.md](BACKTEST_CONTRACT.md) | `src/aqrp/backtest/` / `tests/backtest/test_bt_002.py` | Planned，设计待审 |
| BT-003 | V3.0§8.3 | MVP / 5 | BT-002;RISK-004 | [BACKTEST_CONTRACT.md](BACKTEST_CONTRACT.md) | `src/aqrp/execution/` / `tests/execution/test_bt_003.py` | Planned，设计待审 |
| BT-004 | V3.0§8.2;V3.0§8.3 | MVP / 5 | BT-003 | [BACKTEST_CONTRACT.md](BACKTEST_CONTRACT.md) | `src/aqrp/execution/` / `tests/execution/test_bt_004.py` | Planned，设计待审 |
| BT-005 | V3.0§8.4;V3.0§10.3;V3.1§3 | MVP / 5 | BT-003;DATA-011 | [BACKTEST_CONTRACT.md](BACKTEST_CONTRACT.md) | `src/aqrp/backtest/` / `tests/backtest/test_bt_005.py` | Planned，设计待审 |
| BT-006 | V3.0§2.1;V3.0§8.4;V3.0§10.3 | Competition Ready / 5 | BT-005;DATA-004;DATA-005 | [BACKTEST_CONTRACT.md](BACKTEST_CONTRACT.md) | `src/aqrp/backtest/` / `tests/backtest/test_bt_006.py` | Planned，设计待审 |
| BT-007 | V3.0§8.4;V3.0§10.3 | Competition Ready / 5 | BT-005;PORT-003;RISK-003 | [BACKTEST_CONTRACT.md](BACKTEST_CONTRACT.md) | `src/aqrp/backtest/` / `tests/backtest/test_bt_007.py` | Planned，设计待审 |
| BT-008 | V3.0§8.4;V3.0§8.5 | MVP / 5 | BT-005 | [BACKTEST_CONTRACT.md](BACKTEST_CONTRACT.md) | `src/aqrp/performance/` / `tests/performance/test_bt_008.py` | Planned，设计待审 |
| BT-009 | V3.0§8.5 | MVP / 5 | BT-008 | [BACKTEST_CONTRACT.md](BACKTEST_CONTRACT.md) | `src/aqrp/performance/` / `tests/performance/test_bt_009.py` | Planned，设计待审 |
| BT-010 | V3.1§1;V3.0§3.6;V3.0§12.2 | MVP / 5 | BT-009;FACTOR-004;FACTOR-005 | [TESTING.md](TESTING.md) | `src/aqrp/backtest/` / `tests/backtest/test_bt_010.py` | Planned，设计待审 |
| UI-001 | V3.0§9.1 | MVP / 6 | BT-009;RESEARCH-001 | [INTERFACES.md](INTERFACES.md) | `src/aqrp/ui/` / `tests/ui/test_ui_001.py` | Planned，设计待审 |
| UI-002 | V3.0§9.2;V3.0§3.5 | Competition Ready / 6 | FACTOR-010;UI-001 | [INTERFACES.md](INTERFACES.md) | `src/aqrp/ui/` / `tests/ui/test_ui_002.py` | Planned，设计待审 |
| UI-003 | V3.0§9.3 | MVP / 6 | RESEARCH-009;UI-001 | [INTERFACES.md](INTERFACES.md) | `src/aqrp/ui/` / `tests/ui/test_ui_003.py` | Planned，设计待审 |
| UI-004 | V3.0§9.4 | MVP / 6 | BT-010;UI-001 | [INTERFACES.md](INTERFACES.md) | `src/aqrp/ui/` / `tests/ui/test_ui_004.py` | Planned，设计待审 |
| UI-005 | V3.0§9.5 | Competition Ready / 6 | EXP-003;UI-001 | [INTERFACES.md](INTERFACES.md) | `src/aqrp/ui/` / `tests/ui/test_ui_005.py` | Planned，设计待审 |
| UI-006 | V3.0§9.6 | Competition Ready / 6 | UI-001;ENV-001 | [INTERFACES.md](INTERFACES.md) | `src/aqrp/ui/` / `tests/ui/test_ui_006.py` | Planned，设计待审 |
| UI-007 | V3.0§9.7;V3.1§1 | MVP / 6 | UI-002;UI-003;UI-004 | [TESTING.md](TESTING.md) | `src/aqrp/ui/` / `tests/ui/test_ui_007.py` | Planned，设计待审 |
| UI-008 | V3.0§9;V3.0§18;V3.0§2.1 | MVP / 6 | UI-001;EXP-001 | [INTERFACES.md](INTERFACES.md) | `src/aqrp/services/` / `tests/services/test_ui_008.py` | Planned，设计待审 |
| EXP-001 | V3.0§13;V3.1§7 | MVP / 3 | DATA-007;FACTOR-003 | [INTERFACES.md](INTERFACES.md) | `src/aqrp/experiments/` / `tests/experiments/test_exp_001.py` | Planned，设计待审 |
| EXP-002 | V3.0§6.4;V3.0§13;V3.1§4 | MVP / 3 | EXP-001 | [RESEARCH_PROTOCOL.md](RESEARCH_PROTOCOL.md) | `src/aqrp/experiments/` / `tests/experiments/test_exp_002.py` | Planned，设计待审 |
| EXP-003 | V3.0§13;V3.0§9.5 | MVP / 3 | EXP-001 | [INTERFACES.md](INTERFACES.md) | `src/aqrp/experiments/` / `tests/experiments/test_exp_003.py` | Planned，设计待审 |
| EXP-004 | V3.1§4;V3.1§7 | MVP / 3 | VALID-008;EXP-001 | [RESEARCH_PROTOCOL.md](RESEARCH_PROTOCOL.md) | `src/aqrp/experiments/` / `tests/experiments/test_exp_004.py` | Planned，设计待审 |
| ENV-001 | V3.0§18;V3.1§7 | MVP / 1 | GOV-004 | [ENVIRONMENT_AND_SECURITY.md](ENVIRONMENT_AND_SECURITY.md) | `pyproject.toml;requirements.lock;.github/workflows/ci.yml` / `tests/environment/test_env_001.py` | Planned，设计待审 |
| ENV-002 | V3.0§11.4 | MVP / 1 | ENV-001 | [ENVIRONMENT_AND_SECURITY.md](ENVIRONMENT_AND_SECURITY.md) | `pyproject.toml;requirements.lock;.github/workflows/ci.yml` / `tests/environment/test_env_002.py` | Planned，设计待审 |
| ENV-003 | V3.0§11.3 | MVP / 0 | ARCH-001 | [TESTING.md](TESTING.md) | `docs/TESTING.md` / `docs/audits/phase-0/` | Planned，设计待审 |
| SEC-001 | V3.0§3.3;V3.0§9.2;V3.0§20;V3.1§7;V3.2§3 | MVP / 2 | ENV-001 | [ENVIRONMENT_AND_SECURITY.md](ENVIRONMENT_AND_SECURITY.md) | `src/aqrp/core/security/` / `tests/security/test_sec_001.py` | Planned，设计待审 |
| SEC-002 | V3.0§20;V3.1§7;V3.2§3 | MVP / 1 | ENV-001 | [ENVIRONMENT_AND_SECURITY.md](ENVIRONMENT_AND_SECURITY.md) | `src/aqrp/core/security/` / `tests/security/test_sec_002.py` | Planned，设计待审 |
| SEC-003 | V3.0§20;V3.1§7;V3.1§5 | Production Extensions / POST7 | INT-004 | [ENVIRONMENT_AND_SECURITY.md](ENVIRONMENT_AND_SECURITY.md) | `src/aqrp/core/security/` / `tests/security/test_sec_003.py` | Unsupported，设计待审 |
| SEC-004 | V3.2§1;V3.2§3;V3.2§8 | MVP / 0 | GOV-008 | [ACCEPTANCE.md](ACCEPTANCE.md) | `docs/ACCEPTANCE.md` / `docs/audits/phase-0/` | Planned，设计待审 |
| QA-001 | V3.0§10.1;V3.0§10.2;V3.0§10.3;V3.1§6 | MVP / 0 | ARCH-003 | [GOLDEN_DATASET.md](GOLDEN_DATASET.md) | `docs/GOLDEN_DATASET.md` / `docs/audits/phase-0/` | Planned，设计待审 |
| QA-002 | V3.0§10.4;V3.0§11.1;V3.1§6 | MVP / 1 | QA-001;DATA-008 | [TESTING.md](TESTING.md) | `tests/（对应模块）` / `tests/quality/test_qa_002.py` | Planned，设计待审 |
| QA-003 | V3.0§11.2;V3.1§3 | MVP / 5 | BT-009;QA-002 | [TESTING.md](TESTING.md) | `tests/（对应模块）` / `tests/quality/test_qa_003.py` | Planned，设计待审 |
| QA-004 | V3.0§10.4;V3.1§6;V3.2§1 | MVP / 3 | QA-001;VALID-001 | [GOLDEN_DATASET.md](GOLDEN_DATASET.md) | `tests/（对应模块）` / `tests/quality/test_qa_004.py` | Planned，设计待审 |
| QA-005 | V3.1§8 | MVP / 0 | GOV-003;ARCH-003;QA-001 | [audits/phase-0/SPECIAL_AUDITS.md](audits/phase-0/SPECIAL_AUDITS.md) | `docs/audits/phase-0/SPECIAL_AUDITS.md` / `docs/audits/phase-0/` | Planned，设计待审 |
| QA-006 | V3.2§5;V3.2§6 | MVP / 0 | GOV-008 | [audits/phase-0/REVIEW_PACKAGE.md](audits/phase-0/REVIEW_PACKAGE.md) | `docs/audits/phase-0/REVIEW_PACKAGE.md` / `docs/audits/phase-0/` | Planned，设计待审 |
| QA-007 | V3.0§16;V3.0§19;V3.2§4;V3.2§6 | MVP / 0 | GOV-008;GOV-009 | [ACCEPTANCE.md](ACCEPTANCE.md) | `docs/ACCEPTANCE.md` / `docs/audits/phase-0/` | Planned，设计待审 |
| INT-001 | V3.0§12.1;V3.1§1 | MVP / 3 | RESEARCH-009;VALID-003;EXP-001 | [TESTING.md](TESTING.md) | `src/aqrp/services/;tests/integration/;tests/e2e/` / `tests/integration/test_int_001.py` | Planned，设计待审 |
| INT-002 | V3.0§12.2;V3.1§1 | MVP / 5 | BT-010;INT-001 | [TESTING.md](TESTING.md) | `src/aqrp/services/;tests/integration/;tests/e2e/` / `tests/integration/test_int_002.py` | Planned，设计待审 |
| INT-003 | V3.0§12.3;V3.0§11.2 | MVP / 7 | INT-002;UI-007 | [TESTING.md](TESTING.md) | `src/aqrp/services/;tests/integration/;tests/e2e/` / `tests/integration/test_int_003.py` | Planned，设计待审 |
| INT-004 | V3.0§12.4;V3.0§18 | MVP / 7 | INT-003;ENV-002 | [TESTING.md](TESTING.md) | `src/aqrp/services/;tests/integration/;tests/e2e/` / `tests/integration/test_int_004.py` | Planned，设计待审 |
| INT-005 | V3.0§3.6;V3.1§1;V3.2§7 | MVP / 7 | INT-004;FACTOR-011;RESEARCH-009;BT-010;UI-007 | [TESTING.md](TESTING.md) | `src/aqrp/services/;tests/integration/;tests/e2e/` / `tests/integration/test_int_005.py` | Planned，设计待审 |
| INT-006 | V3.0§1.2;V3.0§2.3;V3.0§18;V3.1§5 | Competition Ready / 7 | INT-002 | [INTERFACES.md](INTERFACES.md) | `src/aqrp/competition/` / `tests/competition/test_int_006.py` | Planned，设计待审 |
| EXT-001 | V3.0§18;V3.0§1.2 | Advanced Research / POST7 | INT-004;FACTOR-008 | [ROADMAP.md](ROADMAP.md) | `后续单独批准的扩展模块（尚未选型）` / `tests/extension/test_ext_001.py` | Deferred，设计待审 |

## 来源反查索引

分组需求的 definition 明列子能力；本索引是节覆盖证据，不能单凭“节已映射”证明语义无遗漏，仍须 Gemini 对原文逐项审读。V3.1专项要求全部保留在契约和审计。

| 原文条款 | 需求ID |
|---|---|
| V3.0§1.1 | GOV-001 |
| V3.0§1.2 | GOV-001, INT-006, EXT-001 |
| V3.0§1.3 | GOV-001, FACTOR-009 |
| V3.0§10.1 | QA-001 |
| V3.0§10.2 | VALID-001, QA-001 |
| V3.0§10.3 | BT-005, BT-006, BT-007, QA-001 |
| V3.0§10.4 | QA-002, QA-004 |
| V3.0§11.1 | QA-002 |
| V3.0§11.2 | DATA-009, FACTOR-012, RISK-004, QA-003, INT-003 |
| V3.0§11.3 | ENV-003 |
| V3.0§11.4 | ENV-002 |
| V3.0§12.1 | RESEARCH-001, INT-001 |
| V3.0§12.2 | BT-010, INT-002 |
| V3.0§12.3 | FACTOR-009, INT-003 |
| V3.0§12.4 | INT-004 |
| V3.0§13 | DATA-007, FACTOR-010, RESEARCH-008, EXP-001, EXP-002, EXP-003 |
| V3.0§14.1 | GOV-002 |
| V3.0§14.2 | GOV-002 |
| V3.0§14.3 | GOV-003 |
| V3.0§14.4 | GOV-003 |
| V3.0§14.5 | GOV-003 |
| V3.0§15.1 | GOV-004 |
| V3.0§15.2 | GOV-004 |
| V3.0§15.3 | GOV-004 |
| V3.0§15.4 | GOV-004 |
| V3.0§15.5 | GOV-004 |
| V3.0§16 | GOV-008, GOV-009, QA-007 |
| V3.0§17.1 | GOV-006 |
| V3.0§17.2 | GOV-006 |
| V3.0§17.3 | GOV-006 |
| V3.0§18 | GOV-004, DATA-003, DATA-008, DATA-013, FACTOR-004, FACTOR-005, FACTOR-006, FACTOR-009, RESEARCH-003, PORT-003, UI-008, ENV-001, INT-004, INT-006, EXT-001 |
| V3.0§19 | GOV-005, QA-007 |
| V3.0§2.1 | ARCH-001, FACTOR-003, BT-006, UI-008 |
| V3.0§2.2 | ARCH-002, DATA-008 |
| V3.0§2.3 | ARCH-001, INT-006 |
| V3.0§2.4 | ARCH-003 |
| V3.0§20 | GOV-009, SEC-001, SEC-002, SEC-003 |
| V3.0§21 | GOV-007 |
| V3.0§22 | GOV-001 |
| V3.0§3.1 | FACTOR-001 |
| V3.0§3.2 | FACTOR-002 |
| V3.0§3.3 | FACTOR-001, FACTOR-012, SEC-001 |
| V3.0§3.4 | DATA-010, FACTOR-004, FACTOR-005, FACTOR-006, FACTOR-007, FACTOR-008, PORT-002 |
| V3.0§3.5 | FACTOR-003, FACTOR-009, FACTOR-010, UI-002 |
| V3.0§3.6 | FACTOR-011, RESEARCH-009, BT-010, INT-005 |
| V3.0§4.1 | DATA-001, DATA-003, DATA-004, DATA-005, DATA-010, DATA-013 |
| V3.0§4.2 | DATA-002, DATA-010 |
| V3.0§4.3 | DATA-001, DATA-002, DATA-007 |
| V3.0§4.4 | DATA-003, DATA-004, DATA-005, DATA-006, DATA-012 |
| V3.0§4.5 | DATA-009 |
| V3.0§5.1 | RESEARCH-001, RESEARCH-002, RESEARCH-003, RESEARCH-007, RESEARCH-008 |
| V3.0§5.2 | RESEARCH-004, RESEARCH-005 |
| V3.0§5.3 | RESEARCH-006 |
| V3.0§6.1 | VALID-001, VALID-002, VALID-005 |
| V3.0§6.2 | VALID-001, VALID-002 |
| V3.0§6.3 | VALID-003 |
| V3.0§6.4 | VALID-004, VALID-006, VALID-007, EXP-002 |
| V3.0§6.5 | VALID-005, VALID-008 |
| V3.0§7.1 | PORT-001 |
| V3.0§7.2 | PORT-002, PORT-003, PORT-004 |
| V3.0§7.3 | DATA-012, RISK-001, RISK-002, RISK-003, RISK-004 |
| V3.0§8.1 | BT-001 |
| V3.0§8.2 | BT-002, BT-004 |
| V3.0§8.3 | BT-003, BT-004 |
| V3.0§8.4 | BT-005, BT-006, BT-007, BT-008 |
| V3.0§8.5 | BT-008, BT-009 |
| V3.0§9 | ARCH-001, UI-008 |
| V3.0§9.1 | UI-001 |
| V3.0§9.2 | UI-002, SEC-001 |
| V3.0§9.3 | UI-003 |
| V3.0§9.4 | UI-004 |
| V3.0§9.5 | UI-005, EXP-003 |
| V3.0§9.6 | UI-006 |
| V3.0§9.7 | UI-007 |
| V3.1§1 | GOV-004, FACTOR-003, FACTOR-011, RESEARCH-009, BT-010, UI-007, INT-001, INT-002, INT-005 |
| V3.1§2 | ARCH-003, DATA-001, DATA-002, DATA-004, DATA-005, DATA-006, DATA-007, DATA-011 |
| V3.1§3 | ARCH-003, BT-001, BT-002, BT-005, QA-003 |
| V3.1§4 | VALID-003, VALID-004, VALID-006, VALID-007, VALID-008, EXP-002, EXP-004 |
| V3.1§5 | GOV-001, DATA-013, SEC-003, INT-006 |
| V3.1§6 | QA-001, QA-002, QA-004 |
| V3.1§7 | DATA-007, FACTOR-012, EXP-001, EXP-004, ENV-001, SEC-001, SEC-002, SEC-003 |
| V3.1§8 | GOV-003, QA-005 |
| V3.2-Baseline§1 | GOV-010 |
| V3.2-Baseline§2 | GOV-010 |
| V3.2-Baseline§3 | GOV-010 |
| V3.2-Baseline§4 | GOV-010 |
| V3.2-Baseline§5 | GOV-010 |
| V3.2-Baseline§6 | GOV-010 |
| V3.2§1 | GOV-008, SEC-004, QA-004 |
| V3.2§2 | GOV-002, GOV-007 |
| V3.2§3 | GOV-006, SEC-001, SEC-002, SEC-004 |
| V3.2§4 | GOV-008, QA-007 |
| V3.2§4.6 | GOV-009 |
| V3.2§4.7 | GOV-005 |
| V3.2§4.8 | GOV-006 |
| V3.2§4.9 | GOV-005 |
| V3.2§5 | GOV-008, QA-006 |
| V3.2§6 | GOV-009, QA-006, QA-007 |
| V3.2§7 | GOV-008, FACTOR-011, INT-005 |
| V3.2§8 | GOV-009, SEC-004 |
| V3.2§9 | GOV-001 |

## 实际文件反向追踪

| 已创建文件类别 | 授权需求 |
|---|---|
| AGENTS、README、章程、进度、决策、变更 | GOV-001–009 |
| REQUIREMENTS、requirements.csv、TRACEABILITY、编制工具 | GOV-003 |
| ARCHITECTURE、INTERFACES、DATA_CONTRACT、BACKTEST_CONTRACT | ARCH-001–003，DATA-001–013，FACTOR-001–012，PORT-001–004，RISK-001–004，BT-001–010 |
| RESEARCH_PROTOCOL、GOLDEN_DATASET | RESEARCH-001–009，VALID-001–008，QA-001–004 |
| ROADMAP、ACCEPTANCE、TESTING、ENVIRONMENT_AND_SECURITY | GOV-004–009，ENV-001–003，SEC-001–004，QA-001–007 |
| docs/sources、audits/phase-0与templates、文档核查工具/证据 | GOV-003，GOV-008，QA-005–007 |
| tests/golden、integration、e2e说明 | GOV-002，QA-001–002，INT-001–005 |
| .gitignore | SEC-002（辅助措施，非已完成秘密扫描） |
| .gitattributes | DATA-007，EXP-001（固定字节避免检出换行转换破坏hash） |

P0文件的精确列表/hash以审查包 MANIFEST.json 为准。源文件、作者工具和自查不是独立审计；任何新增业务模块必须有已批准需求，当前不存在业务实现。


2026-10-21状态增量：Gemini对380d9f8计划预审PASS，当前Phase1 IMPLEMENTING。原文/证据索引及报告勘误在audits/phase-1/gemini/PRE_REVIEW_EVIDENCE_INDEX.json和DEVELOPER_RESPONSE.md。此状态替代此前等待计划预审描述；验收、main合并、打标、Phase2仍未授权。
