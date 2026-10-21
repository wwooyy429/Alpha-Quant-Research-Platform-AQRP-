# 可直接交给Gemini的Phase3计划预审指令

仓库 https://github.com/wwooyy429/Alpha-Quant-Research-Platform-AQRP- 。Phase3 PR完整固定SHA由PR描述AQRP_FIXED_REVIEW_SHA锁定，先记录40位值并checkout该版本，禁止审漂移HEAD。

用户已明确验收Phase2并授权合并/标签后启动P3；main/phase2-baseline/v0.2.0同点f26255fc40a3080bfa883ad64938f60036a14759，PR #3 merge bb6076f，发布后SDK417+原16/4通过，证据在../phase-2/BASELINE.md和publication/。这不是请求再次批准P3启动，而是必需G1计划预审；目前无P3业务实现。

请审：

1. 26项canonical phase3（23 MVP/3 Competition Ready）逐项来源/依赖/接口/测试映射；特别DATA-012、FACTOR-007/009、QA-004、INT-001不能遗漏，106条/16组目录及P0冻结文件不可静默改写；后续组合/回测/UI不得提前实现。
2. PLAN/INTERFACE_DRAFT/STATISTICAL_CONVENTIONS/TEST_PLAN：时间/标签与stage/拟合隔离、PIT侧车及缺失语义、PriceVolume公式和P2加法兼容、全bundle新代码准入/旧Ref重现；没有DAG/外部任意插件范围扩张。
3. 独立复算golden_cases.json每个输入/公式/答案/容差，尤其PriceVolume的t-1、Pearson/Spearman ties、OLS残差、label/action边界、purge接触、HAC尺度/小样本说明和Holm/BY全部family。参考脚本是开发方标准库复算，不能替代你自己的QA-004核验；不得用未来AQRP实现生成expected。
4. 明确DESIGN_DECISIONS中Test真正权限边界、正式标准缺失、min_hac_n/lag/依赖假设/库选择是否阻断G1。只用role/API对象或同OS用户不等于真正独立Test隔离；无部署能力时正式Test必须fail closed且不得把VALID-004全项标完成。Formal ResearchValidated需用户标准及证据，不以正IC/统计显著代替金融批准。
5. 26项和五stage/全部试验ledger/cache/OOS/复现/报告的真实实现与适用验收可达性，不能靠Planned/Unsupported静默删掉本阶段必须能力；提出必要的设计选择及批准人/阻断理由。Python/22锁包保持，新增依赖必须先锁候选及双OS兼容验证，不猜最新版本已安装。
6. 核对本轮仅计划/文档及独立答案候选；src/tests/tools/CI/锁/版本/已发布业务与main基线完全相同。现有CI417是P2基线回归，不是P3测试通过。旧执行身份/历史限制保留，不把P2 GPT Work复核补写为Gemini执行或P3预审已完成。

输出指定完整SHA、范围/需求覆盖、接口/数学/安全/阶段依赖意见、每个发现严重度/位置/依据/处置、你的实际执行与原始命令/环境/日志/hash、未验证与待用户决定、PLAN PASS/PASS WITH CONDITIONS/BLOCKED。无权执行明确NOT VERIFIED；计划PASS不等于实现通过或用户验收，不合并、不打标签、不进入P4。

## 后续修订入口

收到GPT Work对d10的PLAN BLOCKED后，新增五专项具体设计与原件归档；本轮优先使用GEMINI_INCREMENTAL_PRE_REVIEW.md审PR新固定SHA，不能将旧d10挂成新方案已审。
