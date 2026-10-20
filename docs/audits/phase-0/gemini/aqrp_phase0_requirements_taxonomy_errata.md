# AQRP Phase 0 需求分类与编号勘误对照表 (Requirements Taxonomy Errata)

## 一、 勘误背景与核实结论
在针对 PR #1 的复核过程中，前版审查报告在需求结构归纳中存在以下两项事实偏差，现正式勘误：
1. **分组数量**：前版报告误写为 12 组，经核实正式 `requirements.csv` 实际包含 **16 个专业需求组**；
2. **前缀命名**：前版报告推测使用的 `FREG`、`VAL`、`BACK` 前缀在正式 CSV 中**并不存在**，正式需求统一使用项目规范定义的真实前缀（如 `BT` 代表回测引擎等）。

---

## 二、 正式 16 组需求架构对照表 (16 Requirement Domains)

| 序号 | 需求专业组 | 规范职责范围 | 涉及阶段 | 交付与契约对应文件 |
| :---: | :--- | :--- | :---: | :--- |
| 1 | **系统基础架构 (Architecture)** | 核心解耦设计、模块边界、DuckDB/Parquet 底层存储契约 | Phase 0~7 | `docs/ARCHITECTURE.md`, `INTERFACES.md` |
| 2 | **数据系统 (Data System)** | OHLCV、Point-in-Time 时间戳、交易日历、复权与质量检查 | Phase 1 | `docs/DATA_CONTRACT.md` |
| 3 | **因子管理中心 (Factor Registry)** | Alpha 因子独立注册、参数管理、原始因子值输出 | Phase 2 | `docs/INTERFACES.md` |
| 4 | **因子统计验证 (Alpha Validation)** | 截面预处理、IC/Rank IC、ICIR、分位数组合收益计算 | Phase 3 | `docs/RESEARCH_PROTOCOL.md` |
| 5 | **样本外与防止过拟合 (OOS & Anti-Overfitting)** | Purge/Embargo、Walk-Forward、样本外检验防数据泄漏 | Phase 3 | `docs/RESEARCH_PROTOCOL.md` |
| 6 | **投资组合构建 (Portfolio Construction)** | 单/多因子组合、等权/分位数加权、Long-Only/Long-Short | Phase 4 | `docs/INTERFACES.md` |
| 7 | **独立风险控制 (Risk Management)** | 杠杆限制、净敞口/总敞口控制、最大持仓上限、可行性检查 | Phase 4 | `docs/INTERFACES.md` |
| 8 | **事件驱动回测引擎 (Backtest Engine / BT)** | 事件状态机驱动、严格时序撮合、无未来数据保证 | Phase 5 | `docs/BACKTEST_CONTRACT.md` |
| 9 | **订单生命周期 (Order Management)** | 新订单、已接受、部分成交、已撤销、已拒绝状态转换 | Phase 5 | `docs/BACKTEST_CONTRACT.md` |
| 10 | **资金账本与资产对账 (Accounting & Cash Ledger)** | 双重记账、资金守恒、佣金滑点扣除、逐日盯市权益计算 | Phase 5 | `docs/BACKTEST_CONTRACT.md` |
| 11 | **绩效统计与归因 (Performance & Analytics)** | Sharpe、最大回撤、年化收益/波动率、多空收益统计 | Phase 5 | `docs/BACKTEST_CONTRACT.md` |
| 12 | **实验跟踪管理 (Experiment Management)** | 参数追踪、实验重现、版本元数据存储、产物追溯 | Phase 5~7 | `docs/RESEARCH_PROTOCOL.md` |
| 13 | **可视化交互界面 (Streamlit Dashboard)** | 纯呈现层调用后端服务、因子库管理、回测展示 | Phase 6 | `docs/ARCHITECTURE.md` |
| 14 | **比赛适配层 (Competition Interface)** | 交易规则、证券池范围、撮合规则与策略导出适配 | Phase 7 | `docs/ACCEPTANCE.md` |
| 15 | **环境与安全性 (Security & Environment)** | 依赖锁定、隔离沙箱、凭证隔离、防止任意代码执行 | Phase 0~7 | `docs/ENVIRONMENT_AND_SECURITY.md` |
| 16 | **质量保证与治理门禁 (Governance & QA)** | 106项需求闭环、测试规范、主干基线门禁 (`GOV-010`) | Phase 0~7 | `docs/BASELINE.md`, `TESTING.md` |

---

## 三、 结构编号区分说明
- **V3.0 设计规范 66 小节**：对应原始技术方案与论证章节（`docs/sources/AQRP_V3.0.md`）；
- **106 条正式需求清单**：对应 `requirements.csv` 中涵盖 V3.0、V3.1、V3.2 及 `GOV-010` 基线发布门禁的正式跟踪条目；
- 本对照表已作为勘误附录归档，原审计报告字节保持完整不变。
