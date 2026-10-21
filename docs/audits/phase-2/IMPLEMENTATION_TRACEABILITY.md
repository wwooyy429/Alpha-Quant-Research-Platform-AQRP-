# Phase 2 实现追踪

2026-10-22 新一轮共享代码集成已完成开发方验证：业务566f0ece4175fddb2703daab3b5b26ff0e4e245f，完整SDK/双OS各392项，原始外置16项，原始ZIP与新准入receipt核对通过。最新资料及新固定SHA审查范围见 integration-011/README.md、REVIEW_REQUEST.md、EVIDENCE_INDEX.json。以下254项/旧bundle均为此前轮次，不代表新版本独立审查。

固定业务版本：8183b3762b56c466b989d9062a720b5f0d31172a。以下是开发方实现/测试记录，状态 Implemented — independent implementation review pending；不是用户验收。canonical requirements.csv 仍106条/16组。REQUIREMENTS_TRACEABILITY.md 是4f8b0de计划快照，其拟定测试文件名不冒充实际文件。

| ID | 实际实现 | 实际测试（tests/factors/） |
|---|---|---|
| FACTOR-001 | contracts.py FactorSpec/FactorContext/Factor Protocol；versions.py；admission.py | test_contracts_registry.py 的 test_factor_001_required_metadata、test_factor_001_invalid_parameters、test_parameter_defaults_and_mutation、test_ref_and_spec_immutability；test_input_security.py 的 test_deep_context_contract |
| FACTOR-002 | contracts.py Signal/SignalBatch；engine.py write_run | test_contracts_registry.py 的 test_factor_002_signal_key_idempotency_and_conflict、test_signal_rejects_bad_output、test_signal_time_and_readonly；test_lineage_controls.py 的 test_batch_cannot_launder_lineage |
| FACTOR-003 | registry.py；versions.py；admission.py | test_contracts_registry.py 的 test_factor_003_registry_idempotency_conflict_and_precise_ref、test_new_version_compatibility_and_auditable_rollback、test_registry_rejects_missing_review_incompatible_and_false_pins、test_api_range_boundaries |
| FACTOR-004 | builtins.py Momentum；input.py | test_numerical.py 的 test_factor_004_005_006_independent_golden、test_factor_action_basis、test_history_boundaries、test_lookback_extreme_252、test_ratio_scaling_property |
| FACTOR-005 | builtins.py Reversal（单次负号） | test_numerical.py 的 test_factor_004_005_006_independent_golden、test_factor_011_only_ref_changes；direction只元数据，不再次反向 |
| FACTOR-006 | builtins.py Volume（历史L日均量不含当期） | test_numerical.py 的 test_factor_004_005_006_independent_golden、test_zero_volume_distinctions、test_ratio_scaling_property |
| FACTOR-010 | registry.py 精确pin/停用/回滚；contracts.py 不可变参数及权重元数据 | test_pipeline_controls.py 的 test_factor_010_weight_is_only_metadata、test_factor_010_old_pin_runs_after_disable、test_invalid_weight_metadata；test_contracts_registry.py 的 test_new_version_compatibility_and_auditable_rollback |
| FACTOR-011 | engine.py 更换精确FactorRef不改P1数据/账户模块 | test_numerical.py 的 test_factor_011_only_ref_changes；同QuerySpec/快照/参数只改ref；API区间上下界及新旧版本测试 |
| FACTOR-012 | input.py PIT/连续窗口；engine.py host查询；contracts.py 冻结/两类hash | test_input_security.py 的 test_factor_012_view_copies_and_reproducibility、test_forged_future_row_rejected；test_numerical.py 的 test_future_mutations_and_positive_control；test_pipeline_controls.py 的 test_future_action_and_calendar_do_not_change_past |
| SEC-001 | admission.py 加载前审查receipt/hash；core/security 静态辅助规则；固定内置白名单 | test_input_security.py 的 test_unknown_code_rejected_before_loading、test_code_receipt_denial、test_factor_hash_mismatch_wrong_metadata_and_runtime、test_sec_001_static_rules_are_supplemental、test_no_unapproved_execution_modes；test_lineage_controls.py 的 test_standard_gil_and_64bit_are_required |

关键数学：实现用Decimal输入转Fraction作比值，输出float64。答案在实施前4f8b0de人工固定，tests/golden/phase2_answers.json与golden_cases.json逐字节一致；独立标准库参考及float相对有理数误差见reference_arithmetic.*及MATH_PRECISION_RECHECK.json。固定容差abs1e-12 / rel1e-10，不用待测函数生成期望值。Hypothesis正缩放性质、L=1/252边界、零量、缺口、拆股/分红及未来数据mutation均有负例/正控制。

SEC-001本阶段结论仅限“受审内置在受控工程测试环境准入”，外部不可信插件和OS沙箱 Unsupported。同进程Python不是恶意代码安全隔离，不能据测试宣称全部生产安全能力完成。FACTOR-009金融批准、007 Price-Volume及研究、组合、回测、UI仍Planned。
