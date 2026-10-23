# 阶段依赖与边界

2026-10-22 用户已明确确认：WI-R2-001、WI-R2-002持续 DEFERRED / NOT VERIFIED，统一延期至所有开发完成、最终集成版本完整40位SHA锁定后真实环境验证，届时执行方案/权限操作另行授权。R3代码、模型或CI通过不能关闭两项；原失败证据保留，各阶段既定回归和固定版本独立审核继续。详 docs/audits/windows-isolation-deferral/DEFERRAL_POLICY.md。本次只确认延期，不启用账户/修改真实ACL/部署/正式Test/金融批准，不扩大既有开发或合并发布权限。


| 前置 | 可用事实 | P5 设计如何消费 / 未满足影响 |
|---|---|---|
| P1 DATA-002/004/005/011 | 已验收合成八表 + 原始manifest，带时区微秒 PIT | 原 security/calendar/status/actions/exposure 都按 event/available 双约束；每日 bar 收盘才可用，不能用其 open 字段当作盘前可见数据 |
| P2 FACTOR-004/005 | 精确 Ref、注册替换、已审内置因子 | 应用编排器解析 Ref 并生成 contract SignalBatch；BT 内核不导入插件/Registry/Streamlit，不根据因子名分支 |
| P3 INT-001 / 研究来源 | 已验收受限工程结果与终态清单 | 真正 P3 engine/config + P1九文件原字节链；每次决策单独 PIT 投影，不把带未来拟合的整期 final 数据直接回填历史 |
| P3 FACTOR-009/VALID-008 | 正式金融依赖仍不满足 | formal strategy 入口 APPROVAL_REQUIRED；明确独立的 synthetic engineering simulation，不能产生 StrategyApproved 或金融批准 |
| P4 PORT-001/003、RISK-004/003 | 七项受限工程实现 RELEASED | 不可执行 RebalanceProposal 只是输入；P5 校验实际终态 P4 result/candidate/risk/request/audit，再生成模拟订单并重新检查，不信任 risk_passed 布尔 |
| QA-002 | Golden 独立答案原则 | 预先冻结本阶段答案/容差，审查方另写参考；禁止从待测函数生成期望 |
| P5 内部 | BT001→002→003→004/005→006/007/008→009→010，QA003 与 INT002 | 先具备前置再执行测试；不把尚无引擎的 G1 算术/既有 P4 CI写成集成通过 |

BT-010 必须在 P5 真实实现之后仅改精确因子配置各跑完整链，包含组合/风险/撮合/账本及绩效；记录核心模块哈希相同、实际信号和订单有预定差异且各自对账。P6 的网页/CLI研究一致与 P7 全替换 E2E 不在本轮，不能为其验收提前写界面。

真实 Windows 隔离（含独立 PR7）、真实最终 Test、金融批准和完整历史宿主继续延期/未验证。可接受重放范围仍为已验证软件包、锁、旧因子版本及声明结果投影；不可声称操作系统/安装器字节复刻。工程 SDK/Hosted CI不证明三主体权限隔离。没有管理员脚本、ACL、账户/服务/调度变更或部署授权。

Planned：本阶段全部12项业务能力尚待实现授权。Deferred：上述明确延期。Unsupported（未来实现时显式错误）：真实市场 profile、真实下单、多币种/融资、未定义税/碎股处理、非本阶段订单类型。此能力边界仅适用于未知外部规则，不能用于替代明确合成多空/行动/交收/部分成交的必需实现。
