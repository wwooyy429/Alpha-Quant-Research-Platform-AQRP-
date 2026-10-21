# GPT Work · Phase3 固定提交实现审核包

仓库： https://github.com/wwooyy429/Alpha-Quant-Research-Platform-AQRP-

PR： https://github.com/wwooyy429/Alpha-Quant-Research-Platform-AQRP-/pull/5

开始审核时必须记录PR描述中 `AQRP_FIXED_REVIEW_SHA` 的完整40位值，并按该提交检出，不使用漂移HEAD。G1已由用户确认固定3861 PLAN PASS，U-001/U-002设计与责任/合成经济口径已确认；本次为新增实现复核，不能用G1审查替代。

固定范围为26项、23 MVP/3 Competition Ready。请逐行核对 IMPLEMENTATION_TRACEABILITY.md 的实际代码、实际测试、边界及证据，特别检查是否有将必需能力替换为占位结果或遗漏检验族的情况。现有P1/P2原三因子与已发布版本继续回归。

先读 IMPLEMENTATION_AUTHORIZATION.json、IMPLEMENTATION_NOTES.md、IMPLEMENTATION_IDENTITY.json、CODE_REVIEW.md及本轮 IMPLEMENTATION_VALIDATION.json。验证代码bundle、receipt、requirements.lock、每份实际运行environment.code_commit/完整工件清单及原始wheel相互一致。开发方自测、旧G1独立答案与本轮主审执行分别标明身份和权限，不将复制日志作为本人执行。

建议重点复核：

1. PIT身份/币种/侧车parent/修订与可用时间；日bar直到close可见；coverage同一水位修订和独立每日水位；entry/exit同刻及±1us、分红旧股单位与日锚点、支付应收、停牌/退市、label_available及fit/purge闭接触。
2. 每个算子、MAD/线性分位、样本z/平均并列秩与OLS正常方程/秩亏；五阶段真实工件/诊断/无效原因/计数；完整日历缺口不压缩。独立核对冻结答案和容差，不以待测函数生成期望。
3. 合成的共同交集重新z、权重/方向只应用一次、源stage/缺失/零方差/阈值边界；全部候选/参数/方向/处理链/期限、**合成候选×每个期限**计入预注册family。失败/未完成槽位保留，重复试验与Validation使用次数可追溯。
4. Train/Validation/Test边界与当时label_available，walk-forward保守保护先前held-out/purge/embargo和评价去重；Test不能用于fit。增长HAC的N/h/m0/整数根/完整网格、有限样本局限、受限依赖证明/方法认可/用户协议与拒绝条件；确认性p与工程p_approx不可混用。Holm/BY/BH边界及全部m。
5. TestEvaluator在私有数据读取前的实际主体/token/owner/DACL/mode/运行制品只读/hash/部署证据检查；同一私有根统一holdout预算，目录/family/run改名、并发、失败/断进程和缓存不能返预算；开发端成功/失败均只收到CONSUMED，私有错误/结果不泄露。
6. 全配置不可变、原始FactorEngine config字节/signals与content_hash可复算，cache origin不伪造；真实参数网格与Momentum→Reversal完整研究及符号性质；原0.2 wheel/原22锁独立环境、66原文件/3原运行按声明投影真实重放。跨OS差异、缺安装器原字节不包装为完全相同环境。
7. 审批数值NaN/无效阈值、后设标准、非独立Test、family不完整/污染、独立证据/hash不全均拒绝。人工签封必须对应不可变运行中已有proposal，终态文件不变；不得自动StrategyApproved。

执行资料：implementation/developer-iterations保存所有开发迭代成功/失败和旧检查器误运行的原输出；旧560项源环境自测保留为历史；四主体修复后干净SDK/双OS各564项及原16/4、原始参考重算属于开发方证据。最终干净SDK、两OS Actions及官方原ZIP的实际运行ID/提交/日志/路径/hash以 IMPLEMENTATION_VALIDATION.json 和PR回执为准；如新文档提交与业务执行提交不同，必须逐文件核范围，不能自动外推。

**本轮没有实际账户/ACL/服务/调度部署授权，也没有执行真实独立Test或金融批准。** Host控制模拟、普通Hosted CI和公开合成Test不是实际多主体隔离证据。请把“实现代码与工程控制是否正确”和“真实部署/正式统计协议/独立Test是否已验证”分别裁定，列明未闭环条件。不得代用户接受这些限制、验收阶段、合并、打标签或启动P4。

请输出：固定40位SHA与环境/权限；26项覆盖；逐项发现（严重性、实际行号、可复现实例、影响与修复建议）；独立执行与仅审阅证据的区别；剩余部署/正式推断/金融/人工验收条件；最终G2技术建议。主审建议不等于用户验收或发布。
