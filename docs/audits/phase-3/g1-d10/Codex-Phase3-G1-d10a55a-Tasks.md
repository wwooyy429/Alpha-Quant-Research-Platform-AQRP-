# 转交Codex：GPT Work补充G1审核任务

固定SHA：`d10a55a7dd4bc9ca7793ed474bdc1b056916e96e`；PR #5；基线`f26255fc40a3080bfa883ad64938f60036a14759`。结论 **PLAN BLOCKED**。P3启动已授权，无须重复请求；本轮不要求/允许合并、打标签或P4。

15组Golden/75断言全部通过，50冻结资产、106/16目录、26项23MVP+3CR、P2源码/锁/版本/原件保持。当前双OS417仅P2基线回归。

## WORK-P3-001 · High · 正式 Test 隔离仍未选定可部署、可验证的权限 profile

位置：docs/audits/phase-3/DESIGN_DECISIONS.md:6；需求：VALID-004, VALID-006, VALID-008, FACTOR-009, EXP-004。
处置：开发方提交单一可部署方案及资产/权限矩阵，覆盖原始 Test 输入、标签、缓存、ledger、报告/反馈、访问预算存储和已批准代码身份；明确普通研究身份和管理员/存储拥有者的信任边界。用户确认评估主体/部署权限与批准人；没有条件时显式保留阻断，不删需求。
复核：固定新 SHA 审方案；实施时用真实不同权限主体验证读标签/可重建标签的原始数据/缓存/结果均被拒，授权评估成功、并发/崩溃/重复/改名访问受控。双 OS 支持或已批准的能力边界分别存证。
权限/负责人：开发方方案；用户批准主体/权限；审查方核验。
门禁：阻断完整 G1 实施基线；无需在本轮部署，但必须选定可达方案。无部署能力只能继续 fail closed，不能全项验收 VALID-004。

## WORK-P3-002 · High · next-open 行动标签尚缺权益时序与信息可用边界

位置：docs/audits/phase-3/INTERFACE_DRAFT.md:12；需求：VALID-001, VALID-002, VALID-003, QA-004, INT-001。
处置：冻结 SYNTHETIC_V1 的明确行动标签协议，沿用 RAW 并显式转换 P1 PER_OLD_SHARE 与本案例 post-split 单位；规定公司行动排序、evaluation_cutoff/available_at 与 price holding interval、purge interval 的关系。新增带 UTC 微秒及 session 日历的独立答案，保留当前正确算术原件。
复核：入场/退出同刻拆股或除息、端点前后1微秒、晚到/修订、支付在退出后、P1日bar直到收盘才可见、train label 延迟发布、purge闭区间接触；每案列预期股数/应收/收益/可用时点。
权限/负责人：开发方协议与候选；审查方独立复算；用户确认合成经济假设。
门禁：阻断标签/切分的 G1 定义；这是待定设计，未指控不存在的 P3 实现已泄漏。

## WORK-P3-003 · Medium · RESEARCH-007 的因子合成和冗余分析只有目录映射

位置：docs/audits/phase-3/REQUIREMENTS_TRACEABILITY.md:16；需求：RESEARCH-007, INT-001。
处置：选择最小研究级合成接口与冗余诊断输出：精确Ref、stage、预注册因子方向/权重、同样本交集及缺失政策、合成分数/血缘、相关和预注册冗余规则。若使用学习权重须只在Train拟合，否则选择固定权重。补手算/性质/失败测试映射。
复核：固定2因子独立数值、符号/不同scale、缺失交集、零权重或无有效组合、冗余规则及未来数据变更；所有权重/规则选择进ledger，无账户写入。
权限/负责人：开发方补设计，审查方核覆盖；范围变更仅用户批准。
门禁：阻断26项覆盖的 G1 完整性；不要求提前实现 P4 账户、资金权重或风险模块。

## WORK-P3-004 · Medium · 旧 FactorRef 重现尚未选择具体运行与制品方案

位置：docs/audits/phase-3/DESIGN_DECISIONS.md:10；需求：FACTOR-007, RESEARCH-008, EXP-003, INT-001。
处置：选择经哈希核对的旧0.2.0源/原wheel+原锁独立运行方案，或具有等价安全证据的多版本路由；列旧3因子/Ref/API与新PriceVolume/API矩阵、制品保管及缺失拒绝语义、可允许不同的run_id/墙钟/路径身份投影；新bundle完整重审，不重写旧receipt或Ref。
复核：新P3 runtime运行新Ref；原精确Ref在其原0.2.0环境重放；原manifest原字节hash及声明数值投影核对；旧制品缺失/篡改明确不可复现；老接口与三公式回归不变。
权限/负责人：开发方选择方案，审查方核验；破坏契约或架构变更由用户批准。
门禁：阻断兼容/重现的G1设计闭环；这是P3变更前需要选定的机制，不是要求旧P2准入当前支持未知新代码。

## WORK-P3-005 · Medium · HAC 正式推断 profile 与最小样本准入尚未冻结

位置：docs/audits/phase-3/STATISTICAL_CONVENTIONS.md:10；需求：VALID-005, VALID-007, VALID-008, QA-004。
处置：开发方提出带依据的统计profile与拒绝契约，明确min_hac_n是保守工程门槛而非有限样本保证；不由审查者凭空拍一个通用数字。保留Bartlett、gamma除n、Var(mean)=S/n、correction=none及已算正确答案；新增非零均值/多个lag/缺失/不足样本及全family失败项候选。
复核：独立复算新非零均值SE/p；样本/lag边界与拒绝路径；全family有效边际p要求、Holm/BY/BH假设及污染门禁。NumPy/stdlib可维持22锁；若加SciPy/statsmodels，先精确候选/哈希/3.13.16双OS方案。
权限/负责人：开发方提出方法与profile；统计预审核验；用户批准正式样本/经济阈值/实验预算。
门禁：正式推断的G1子门禁未闭合；可设计/实现显式fail-closed原语，但不得把本包视作正式统计准入已批准。无用户金融阈值本身只阻断Formal ResearchValidated，并不要求停止无关纯计算模块。

后续只提交设计闭环的新固定SHA，逐条引用本报告发现ID；不改旧正确Golden、不覆盖历史执行身份、不把Planned/Unsupported当本阶段需求豁免。用户正式研究标准缺失时，设计/实现可拒绝金融批准，但不得登记Formal ResearchValidated。详细证据和独立数学程序随本报告归档。
