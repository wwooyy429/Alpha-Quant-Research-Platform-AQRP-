# 报告事实与待闭环条件（本轮不替独立审查者裁定）

| 项目 | 可核事实 / 本轮状态 | 尚待闭环 |
|---|---|---|
| 001 PR标题/BASELINE | PR #3仍为feat: Phase 2 Factor Registry and reviewed builtin signals；docs/BASELINE.md属于受保护P0原件，未改 | Gemini修正旧报告说明并确认范围 |
| 002需求职责 | FACTOR-011=P2注册替换/API兼容；Volatility=FACTOR-008、POST7、Deferred；106条16组不变 | Gemini对齐原条目，而非仅写AGREE |
| 003协议及血缘 | compute(view,context)；manifest/query hash在context/config，Signal有snapshot/params/implementation hash，无虚构input_data_hash字段 | 原方向已接受，按当前源码复核，不新增字段迎合误写 |
| 004源码/coverage | core/security/__init__.py与factors/contracts.py；三行Protocol排除不在protocols.py | 核对真实路径及当前coverage配置 |
| 005/008准入与时间 | state ENGINEERING_APPROVED；environment TEST_ONLY；financial_approval NONE；合成available_at=冻结decision_time | 不能推定真实市场盘后时刻或金融批准 |
| 006/007数学核心 | 修订脚本已正确区分两套Volume输入、B推导及非零浮点误差，旧数学缺陷已由真实资料纠正 | 新代码/本轮独立执行的范围须分开标注 |
| 010执行工具 | 修订数学原件已归档；旧综合AST/math/hash工具原件仍未收到 | NOT VERIFIED；不得用数学脚本或本轮开发方工具顶替Gemini原件 |
| 009安全边界 | AST/只读对象不提供OS沙箱或全部漏洞不存在的证明；外部不可信插件Unsupported | 原范围澄清已接受，新bundle继续保持该限制 |
| 011证据等级 | 原ZIP本轮为Evidence Reviewed Only、完整SDK为NOT VERIFIED的披露已接收 | 本轮新执行仍按实际操作者/权限分层；开发方不得补记Gemini执行 |
| 012权限 | 人工验收、main合并、标签发布、下一阶段启动分别授权 | 原原则已接受，本次仅集成交审，无P2验收/发布或P3授权 |
| 两项Low | 原结论限受审内置ENGINEERING_APPROVED/TEST_ONLY/NONE，代码逻辑不变；本轮重审共享依赖并更换bundle | Gemini对新bundle确认，不能外推外部不可信插件/OS沙箱 |
| 新技术集成 | 开发方完整SDK与双OS各392通过、原始外置16通过，原始ZIP/hash/回放通过 | 新固定SHA独立复核，真实执行级别明确 |
| 独立执行 | 目前Gemini完整SDK独立执行仍NOT VERIFIED；新ZIP是开发方核验 | 补原始执行证据，或用户明确决定是否接受限制；当前无此批准 |
| 人工阶段门禁 | 用户仅授权集成后交审 | Phase2人工验收、main合并、标签/发布、最终基线核验均未授权/未完成；P3须另获启动授权 |

本轮开发方校验器首次失败为错误假定查询hash不含路径，已按既有query契约纠正并保留原脚本/失败日志；产品和金融答案未为迎合校验而改变。具体见CHECKER_CORRECTION.json。
