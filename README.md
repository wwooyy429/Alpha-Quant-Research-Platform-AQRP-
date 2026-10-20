# Alpha Quant Research Platform（AQRP）

Phase 0 已发布。Phase 1 计划经 Gemini 对固定380d9f8预审PASS，现已实现合成日频数据基础，已收到Gemini对74bdb92的实现PASS报告，正在核对报告勘误/执行证据。阶段验收、main合并、发布及Phase 2均尚未获授权。

本阶段提供稳定证券标识、Decimal单位、UTC微秒时间与固定IANA规则、日历、PIT可见修订、历史股票池/状态、拆股与分红研究视图、质量报告、不可变Parquet快照和可重建DuckDB索引。首版只支持明确的SYNTHETIC_V1测试profile，真实市场接入另行确定。

当前范围和真实验证见[Phase1实现审查包](docs/audits/phase-1/IMPLEMENTATION_REVIEW_PACKAGE.md)、[数据SDK使用说明](docs/audits/phase-1/DATA_SDK.md)和[进度](docs/PROGRESS.md)。[独立计划预审原件及索引](docs/audits/phase-1/gemini/PRE_REVIEW_EVIDENCE_INDEX.json)保持原字节。380d9f8中的PLAN、SELF_CHECK、MANIFEST和COMMAND_LOG仍为历史计划快照，不能当作当前实现测试结果。

业务环境精确CPython3.13.16标准GIL/x64，直接与传递依赖固定在requirements.lock。安装及完整验证入口为`python tools/ci.py`，须在干净、已提交工作区和已核实解释器下运行；它把venv/构建/缓存/测试产物放入非同步临时路径，哈希安装依赖，从固定Commit离线构建并安装本项目wheel，执行静态/单元/性质/契约/集成/泄漏/覆盖率/秘密扫描及数据smoke。详见[复现说明](docs/audits/phase-1/REPRODUCE.md)。

因子Registry、因子研究、组合/风险、回测账本、网页及对应业务CLI仍Planned；高级扩展Deferred，真实交易与任意外部代码执行Unsupported。不存在真实凭证、供应商或订单接入。


本轮报告原件、审查方发现关闭记录及开发方核对见[实现审计接收索引](docs/audits/phase-1/gemini/IMPLEMENTATION_AUDIT_EVIDENCE_INDEX.json)与[实现报告勘误/处理意见](docs/audits/phase-1/IMPLEMENTATION_AUDIT_RESPONSE.md)。原报告500/1000、文件和独立测试执行表述待Gemini确认，不能将其直接变成用户验收通过。
