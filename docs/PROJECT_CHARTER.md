# 项目章程 V3.2（Phase0已获用户验收）

日期：2026-10-20（Asia/Shanghai）。来源：V3.0 全文、V3.1 §§1–8、V3.2 §§1–9；修订只覆盖明确变更，其余原要求保留。项目仓库：<https://github.com/wwooyy429/Alpha-Quant-Research-Platform-AQRP->。

目标是可维护、可复现的因子研究及比赛模拟平台：历史数据 → 插件信号 → 统计/样本外验证 → 批准 → 组合/风险 → 独立事件回测 → 报告和实验记录。平台后续可接比赛接口及 GPT 候选挖掘，但当前不实现这些扩展。

架构固定 Python、Pandas、NumPy、SciPy、statsmodels、DuckDB、Parquet、Streamlit、Plotly、pytest、ruff、Git/GitHub Actions；静态类型/结构验证工具按风险选型。新增大型框架、重复回测引擎、微服务、Qlib/vectorbt/LEAN/Polars/scikit-learn/PyTorch 必须有收益、代价、兼容和迁移风险评估及用户批准。

质量顺序：数据与时间 → 数学统计 → 撮合账本 → 因子解耦 → 测试审查复现 → 维护扩展 → 界面。历史结果不代表未来收益，平均 IC 为正或 UI 正常不构成有效性证明。

当前用户已授权Phase1，首版限合成数据及通用契约，并批准Python3.13.16；详见audits/phase-1/AUTHORIZATION.json。先完成阶段计划/接口/答案和Gemini预审，再实施范围内数据、环境/CI及测试。未授权后续阶段、真实源/账户接入或P1合并发布；计划准备不等同预审通过。

角色按AGENTS：GPT Work开发，Gemini独立审查，用户拥有最终决定权。GitHub固定Commit、PR、可信记录为事实源。Phase0已验收，main/标签已核实，Gemini主干门禁PASS，基线7de1d0e已RELEASED；报告及批准见BASELINE。后续归档不移动稳定标签，不自动获下一阶段授权。

阶段完成需范围内交付、适用测试、Gemini 固定 SHA 审查、阻断问题闭环、人工批准。合并、发布、下一阶段分别需明确授权。不可用口头 AI 共识替代证据，不可把同一模型另一会话当作独立正确性保证。

用户补充Phase0 Main Baseline Release Gate：AUDIT PASSED、ACCEPTED、RELEASED分别记录。当前三者齐备、F-001 CLOSED，用户现另行授权Phase1；本阶段仍遵守计划预审→实施→独立复核→人工验收→授权发布制度，不沿用P0报告代替P1审查。

四级范围以 REQUIREMENTS 为准：MVP（最小可研究/模拟主链及质量治理）、Competition Ready（完整 V3.0 功能和已知比赛规则）、Advanced Research（公式/机器学习/自动挖掘）、Production Extensions（真实执行等另行授权）。分级不删除 V3.0 必须需求，也不改变 Phase 0–7 固定阶段。

所有依赖未具备的测试仅Planned，未实现能力标Planned、Deferred或Unsupported。禁止模拟数据冒充真实市场接入或比赛认证。Phase0设计已验收发布；后续实施标准、阈值与未决事项按对应文档及阶段另行批准，基线门禁通过不代替未来能力验证。
