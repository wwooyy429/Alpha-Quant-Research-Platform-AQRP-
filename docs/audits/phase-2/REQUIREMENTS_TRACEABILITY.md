# Phase 2 需求追踪（计划快照）

全部10项为MVP / Phase2，状态Planned；下列是拟定实现与预期测试，非已实现能力。原正式目录106条/16组保持不变。

| ID | 原需求 | 依赖 | 拟文件 / 测试 |
|---|---|---|---|
| FACTOR-001 | 统一Factor协议及12项元数据、参数schema、数据与API兼容声明 | DATA-002;DATA-008 | src/aqrp/factors/contracts,registry,engine,builtins,input,admission,versions（按项）；tests/factors/test_factor_001.py |
| FACTOR-002 | 信号时间/证券/ID版本/值、快照参数任务/可用时间/有效性及唯一键 | FACTOR-001 | src/aqrp/factors/contracts,registry,engine,builtins,input,admission,versions（按项）；tests/factors/test_factor_002.py |
| FACTOR-003 | 注册/resolve/兼容校验/停用/精确版本/回滚/参数校验 | FACTOR-001;SEC-001 | src/aqrp/factors/contracts,registry,engine,builtins,input,admission,versions（按项）；tests/factors/test_factor_003.py |
| FACTOR-004 | Momentum基础因子 | FACTOR-002 | src/aqrp/factors/contracts,registry,engine,builtins,input,admission,versions（按项）；tests/factors/test_factor_004.py |
| FACTOR-005 | Reversal基础因子 | FACTOR-002 | src/aqrp/factors/contracts,registry,engine,builtins,input,admission,versions（按项）；tests/factors/test_factor_005.py |
| FACTOR-006 | Volume基础因子 | FACTOR-002 | src/aqrp/factors/contracts,registry,engine,builtins,input,admission,versions（按项）；tests/factors/test_factor_006.py |
| FACTOR-010 | 配置选因子/参数/增删/停用/权重/版本/回滚，新运行pin不可热替换 | FACTOR-003 | src/aqrp/factors/contracts,registry,engine,builtins,input,admission,versions（按项）；tests/factors/test_factor_010.py |
| FACTOR-011 | P2注册替换和版本兼容测试 | FACTOR-004;FACTOR-005 | src/aqrp/factors/contracts,registry,engine,builtins,input,admission,versions（按项）；tests/factors/test_factor_011.py |
| FACTOR-012 | 因子隔离/确定性/不修改资金持仓费用或其他代码 | FACTOR-001;SEC-001 | src/aqrp/factors/contracts,registry,engine,builtins,input,admission,versions（按项）；tests/factors/test_factor_012.py |
| SEC-001 | 新因子审查后才入批准环境，隔离最小权限/不可信代码禁执行 | ENV-001 | src/aqrp/core/security与factors/admission；tests/security/test_sec_001.py |

FACTOR-003/012→SEC-001的依赖在同阶段先实现准入，再允许测试执行。DATA-002/008及ENV-001来自核实的Phase1；FACTOR-009的研究批准依赖VALID-008，留P3；不为满足未来依赖提前实现。

本阶段相关QA/ENV/GOV支持沿既有ID回归，不新增条目或将所有未来功能标Completed。实际实现后在此快照之外增加真实文件/测试ID、固定SHA、结果和独立审查证据。
