# G1预审须明确的设计决定与外部依赖

| ID / 事项 | 预审提案 / 当前边界 | 通过前需核实 |
|---|---|---|
| P3-D01 数据范围 | 沿用已授权合成日频与通用契约，DATA-012侧车行业/市值/可选Beta按PIT和currency单位冻结；真实数据未接入 | 原8表契约不破坏，侧车有独立manifest/父快照/版本/缺失与修订测试 |
| P3-D02 Test权限 | 默认工程profile可测权限API和单次预算/污染拒绝；正式独立Test要求可验证的独立评估主体/进程及存储权限，开发任务不能读标签或反馈。提议可替换本地evaluator接口，由专用OS主体部署，主研究进程无Test路径/句柄 | 未配置/证明权限隔离时正式Test操作fail closed（Unsupported/UNVERIFIED_ISOLATION），绝不把同OS用户role字符串、隐藏属性或数据路径约定称为物理隔离。不得用逻辑单测宣称正式隔离完成；完整VALID-004验收依赖隔离profile获批，若无条件须明确列阻断/待决，不静默延期 |
| P3-D03 正式标准D-004 | 样本日期/范围、min_n、min_hac_n/lag、alpha、实际研究通过门槛/稳定性与预算尚无用户数值批准；预注册字段全校验，缺项只允许EXPLORATORY，ApprovalProposal拒绝 | 合成手工答案只验证计算，不是金融通过阈值。需用户/预审确认标准后才可实际ResearchValidated；P3不凭空等待P5回测才能研究，但StrategyApproved继续禁止 |
| P3-D04 统计定义D-005 | 既有P0定义加显式提案见STATISTICAL_CONVENTIONS；HAC不自动lag/有限样本修正，分组不拆tie，OLS固定rcond并拒绝秩亏 | Gemini独立复算case/假设，若提出变更先记录新答案/影响，不改旧正确Golden迎合实现 |
| P3-D05 库/环境 | 先保持22锁包、3.13.16；NumPy+标准库为现有轻量实现候选，SciPy/statsmodels如有必要作为后续明确锁定变更，不在本轮安装或猜版本 | Gemini核对原架构适配及独立参考充分性；任何新依赖需精确候选/wheel哈希/3.13.16双OS验证方案，不能把网页版本当已安装 |
| P3-D06 P2兼容 | Price-Volume及新审批域/侧车需要加法元数据与allowlist扩展；旧三因子/已存Ref不能静默改标签或新hash，完整bundle任何新增/共享变更都重审 | 提供新旧API范围、精确artifact/ref迁移/旧wheel重现测试；预审认为破坏性则先提高major/列变更批准，不在计划轮改P0或P2源码 |
| P3-D07 能力等级 | 26条全部仍Planned，含3条Competition Ready；本轮不因复杂性删除或私自降级；真实源/OS隔离/正式标准有外部条件 | QA-004须Gemini独立核对候选答案；本开发方脚本不是独立批准，未完成只标REVIEW REQUIRED |

本文件列出方案和阻断条件供G1审查，不是向用户重复索取Phase3启动许可。已有启动授权继续有效；预审和具体外部设计/数值标准是另一个关卡，不能默认因时间流逝已批准。
