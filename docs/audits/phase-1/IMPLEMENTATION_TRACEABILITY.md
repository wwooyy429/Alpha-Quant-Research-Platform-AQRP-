# Phase1实际实现追踪（待独立实现验收）

规范总目录仍106条/16组。requirements.csv、REQUIREMENTS及P0契约是冻结设计目录，能力状态不能代替本增量的实际文件/证据。以下14项均已实现并有测试，正式验收尚未发生。

| ID | 实际文件（src/aqrp前缀） | 实际自动化证据 |
|---|---|---|
| DATA-001 | data/schemas.py,quality.py,query.py；core/units.py | test_data_001_002_pit_microseconds_and_revisions、test_data_011_source_units_survive_pipeline；双市场同symbol隔离 |
| DATA-002 | core/time.py；data/pit.py,query.py | test_data_002_*、test_revision_ids_are_monotonic、test_data_005_late_status_universe_and_alias；双时间/微秒/未知/迟到修订 |
| DATA-003 | core/time.py；data/synthetic.py,quality.py | test_data_003_dst_and_local_date、test_data_003_cross_relations、test_data_003_008_cross_timezone_roundtrip；DST/半日/假日/日期边界 |
| DATA-004 | data/actions.py,query.py | test_data_004_split_dividend_and_future_action、test_data_004_action_edges、test_data_004_split_exact_conservation、test_adjustment_lineage |
| DATA-005 | data/pit.py,query.py | test_data_005_late_status_universe_and_alias、test_data_005_overlapping_alias_and_universe；历史退出/别名/停牌可见生效分离 |
| DATA-006 | data/quality.py | test_data_006_*、test_schema_inputs、test_required_security_fields；六行计数守恒/冲突隔离/零量不补缺 |
| DATA-007 | data/snapshot.py；core/canonical.py | test_data_007_*；篡改/路径/符号链接或junction/完整manifest与质量/原子失败/不覆盖 |
| DATA-008 | data/snapshot.py,store.py,synthetic.py | test_data_007_008_roundtrip_and_rebuild、test_data_008_frozen_input_pipeline；DuckDB/Arrow/Parquet类型与值 |
| DATA-009 | data/pit.py,query.py；core/contracts.py | test_data_009_*；未来行情/迟到修订/成员/行动/日历变化不可改历史，正向控制与顺序性质；DataView副本隔离 |
| DATA-011 | core/units.py；data/quality.py | test_data_011_*、test_data_011_source_units_survive_pipeline；Decimal/源单位/溢出/混币拒绝 |
| ENV-001 | pyproject.toml,.python-version,requirements.lock；tools/ci.py | test_env_001_exact_runtime_and_imports、真实双OS干净哈希安装/pip check/固定wheel和环境证据 |
| ENV-002 | .github/workflows/ci.yml；tools/ci.py,check_coverage.py | 真实Windows/Ubuntu CI run/attempt/jobs和原始日志；固定Actions SHA、只读权限、失败产物 |
| SEC-002 | tools/secret_scan.py,.gitleaks.toml；.gitignore | 固定gitleaks8.30.1下载hash/版本、正负控制和项目脱敏报告；无账户/真实源调用 |
| QA-002 | tests/data,environment,integration,golden；tools/independent_reference.py,data_smoke.py | 102项含边界/性质/固定答案/独立Fraction参考；逐模块覆盖率门槛；完整smoke数据/配置/结果版本 |

完整nodeid及执行结果由JUnit保留；规划test_data_NNN.py缩写已映射到以上真实文件，未创建空测试以凑目录。多项安全/时间入口通过集成测试验证，不把静态文件存在当通过。
