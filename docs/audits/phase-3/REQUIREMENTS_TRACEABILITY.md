# Phase3需求→接口→计划实现/测试（26项）

全部为预审提案，未Implemented；正式106条需求目录和等级不变。

| ID | 等级 | 原依赖 | 接口 | 计划实现 / 测试 |
|---|---|---|---|---|
| DATA-012 | Competition Ready | DATA-002 | INTERFACE_DRAFT.md / ExposureSnapshotRef | src/aqrp/data/exposures.py / tests/data/test_data_012.py |
| FACTOR-007 | Competition Ready | FACTOR-003 | INTERFACE_DRAFT.md / Price-Volume | src/aqrp/factors/price_volume.py + admission/contracts / tests/factors/test_factor_007.py |
| FACTOR-009 | MVP | FACTOR-003;VALID-008 | INTERFACE_DRAFT.md / ApprovalProposal | src/aqrp/validation/approvals.py + experiments / tests/factors/test_factor_009.py |
| RESEARCH-001 | MVP | FACTOR-003 | INTERFACE_DRAFT.md / ResearchRequest, StageScores, research | src/aqrp/research/ / tests/research/test_research_001.py |
| RESEARCH-002 | MVP | RESEARCH-001 | INTERFACE_DRAFT.md / ResearchRequest, StageScores, research | src/aqrp/research/ / tests/research/test_research_002.py |
| RESEARCH-003 | Competition Ready | RESEARCH-002;DATA-012 | INTERFACE_DRAFT.md / ResearchRequest, StageScores, research | src/aqrp/research/ / tests/research/test_research_003.py |
| RESEARCH-004 | MVP | RESEARCH-001 | INTERFACE_DRAFT.md / ResearchRequest, StageScores, research | src/aqrp/research/ / tests/research/test_research_004.py |
| RESEARCH-005 | MVP | RESEARCH-004 | INTERFACE_DRAFT.md / ResearchRequest, StageScores, research | src/aqrp/research/ / tests/research/test_research_005.py |
| RESEARCH-006 | MVP | RESEARCH-002 | INTERFACE_DRAFT.md / ResearchRequest, StageScores, research | src/aqrp/research/ / tests/research/test_research_006.py |
| RESEARCH-007 | MVP | RESEARCH-006 | INTERFACE_DRAFT.md / ResearchRequest, StageScores, research | src/aqrp/research/ / tests/research/test_research_007.py |
| RESEARCH-008 | MVP | EXP-001;RESEARCH-001 | INTERFACE_DRAFT.md / ResearchRequest, StageScores, research | src/aqrp/research/ / tests/research/test_research_008.py |
| RESEARCH-009 | MVP | RESEARCH-001;VALID-001 | INTERFACE_DRAFT.md / ResearchRequest, StageScores, research | src/aqrp/research/ / tests/research/test_research_009.py |
| VALID-001 | MVP | RESEARCH-006 | INTERFACE_DRAFT.md / LabelBatch, SplitSpec, MetricResult, TestEvaluator | src/aqrp/validation/ / tests/validation/test_valid_001.py |
| VALID-002 | MVP | VALID-001 | INTERFACE_DRAFT.md / LabelBatch, SplitSpec, MetricResult, TestEvaluator | src/aqrp/validation/ / tests/validation/test_valid_002.py |
| VALID-003 | MVP | VALID-001 | INTERFACE_DRAFT.md / LabelBatch, SplitSpec, MetricResult, TestEvaluator | src/aqrp/validation/ / tests/validation/test_valid_003.py |
| VALID-004 | MVP | VALID-003;EXP-002 | INTERFACE_DRAFT.md / LabelBatch, SplitSpec, MetricResult, TestEvaluator | src/aqrp/validation/ / tests/validation/test_valid_004.py |
| VALID-005 | MVP | VALID-001 | INTERFACE_DRAFT.md / LabelBatch, SplitSpec, MetricResult, TestEvaluator | src/aqrp/validation/ / tests/validation/test_valid_005.py |
| VALID-006 | MVP | EXP-002;VALID-004 | INTERFACE_DRAFT.md / LabelBatch, SplitSpec, MetricResult, TestEvaluator | src/aqrp/validation/ / tests/validation/test_valid_006.py |
| VALID-007 | MVP | VALID-005;VALID-006 | INTERFACE_DRAFT.md / LabelBatch, SplitSpec, MetricResult, TestEvaluator | src/aqrp/validation/ / tests/validation/test_valid_007.py |
| VALID-008 | MVP | VALID-004;VALID-007 | INTERFACE_DRAFT.md / LabelBatch, SplitSpec, MetricResult, TestEvaluator | src/aqrp/validation/ / tests/validation/test_valid_008.py |
| EXP-001 | MVP | DATA-007;FACTOR-003 | INTERFACE_DRAFT.md / ExperimentLedger, reproduce, ApprovalProposal | src/aqrp/experiments/ / tests/experiments/test_exp_001.py |
| EXP-002 | MVP | EXP-001 | INTERFACE_DRAFT.md / ExperimentLedger, reproduce, ApprovalProposal | src/aqrp/experiments/ / tests/experiments/test_exp_002.py |
| EXP-003 | MVP | EXP-001 | INTERFACE_DRAFT.md / ExperimentLedger, reproduce, ApprovalProposal | src/aqrp/experiments/ / tests/experiments/test_exp_003.py |
| EXP-004 | MVP | VALID-008;EXP-001 | INTERFACE_DRAFT.md / ExperimentLedger, reproduce, ApprovalProposal | src/aqrp/experiments/ / tests/experiments/test_exp_004.py |
| QA-004 | MVP | QA-001;VALID-001 | GOLDEN_REFERENCE.md / independent answers | docs/audits/phase-3/golden* + future tests/golden / tests/quality/test_qa_004.py |
| INT-001 | MVP | RESEARCH-009;VALID-003;EXP-001 | INTERFACE_DRAFT.md / complete research service | src/aqrp/services/research.py + cli/reports / tests/integration/test_int_001.py |

## 补充行为追踪（不改变canonical）

- RESEARCH-007：compose(CompositeSpec,StageScoreRefs)->CompositeScores+RedundancyReport，固定w/d、共同交集z、相关/冗余诊断；COMPOSITE_RESEARCH.md；未来research/composite.py、test_research_007.py、INT001。
- VALID-004/006/008、FACTOR-009、EXP-004：P3-ISO-OS-1真实主体/ACL/封存输入与预算；部署证据未验证，不判需求已完成。
- VALID-001/002/003、QA-004、INT-001：SYNTHETIC_V1_LABEL_1及LabelCoverageRef/label_available_at/fit/purge，新行动边界候选。
- FACTOR-007、RESEARCH-008、EXP-003：P3-REPRO-ARTIFACT-1原0.2制品/环境路线及明确失败/投影。
- VALID-005/007/008、QA-004：HAC-BARTLETT-1固定候选/拒绝、非零p/全family失败项。
