# Phase3验证计划（未来测试，未执行业务）

计划覆盖26项需求，必须先独立核对Golden。沿用关键数学/时间/标签/split/准入/审批/完整性行95%分支90%，其余核心行90%分支85%；每条关键不变量有正负控制，不能用总体百分比替代负例。P1/P2已发布417项及原16/4回归保持，未来新增数以真实JUnit为准，不预测虚假通过数。

| 验证面 | 正常答案 / 必要反例 |
|---|---|
| DATA-012 | 不同证券/历史industry修订与cap，available=decision边界；未来一微秒、缺暴露/单位或market冲突、修订逆序、重复键/损坏manifest，禁最新数据回填 |
| FACTOR-007/009 | PriceVolume0.06等手算、三内置回归，缺价量/历史0/拆股/证券交错，未准入加载前失败；研究/策略/工程批准域分离，缺标准/证据/审批拒绝 |
| 算子/处理 | delay/delta/rolling/std/pairedcorr/平均秩/条件白名单；session缺口、小n/零variance/NaN/inf、MAD0/极端值、fit界越界；正比例/单调rank性质与独立答案共同核对 |
| 五stage/中性化 | 原始→clean→standardized→neutralized→final各自产物/fit lineage；禁复制原列冒充处理、OLS残差与暴露正交、rank deficiency/缺行业或cap失败；SKIPPED显式 |
| 标签/IC | next-open边界、晚到/修订/停牌/退市未知、拆股与分红；P0 Pearson/Rank/Tie/ICIR已知答案、n/reason、分组tie最小规模、年度/期限对齐；原始stage不可混当final |
| OOS/Test | 闭标签区间接触边界purge、embargo和滚窗去重；不能看未来拟合、开发cache拿不到Test、越权/重复访问/改名family/改参数后Test重用拒绝；正式隔离须独立进程/权限证据，不只mock角色 |
| 统计/多试验 | HAC手工gamma/S/SE、h重叠lag不足/缺样本/空洞/非正方差；Holm/BY精确p已知答案、BH无依赖依据拒绝、m含淘汰/失败、全部候选与预算/重复配置指纹留痕 |
| ledger/repro/cache | UUID唯一、配置封存、终态不回退、原文件hash一致（包括非canonical往返反例）、崩溃/失败不丢记录；code/data/cutoff/stage/split/params/权限变化均cache miss；旧数据/新路径按声明投影重现 |
| INT-001/RESEARCH-009 | 固定合成数据+协议仅换Momentum→Reversal精确Ref，完整计算/五stage/IC/分组/OOS/报告/实验均真实；预注册方向+1下raw及正向线性处理后的final相反，相关符号/组别按独立答案，核心统计/账户代码不改；不得要求未实现回测 |

G1后每次完整SDK从干净Git归档构建安装真实wheel，Ruff、pytest+branch coverage、独立参考、data/factor/research smoke、秘密扫描正负控制、Windows/Ubuntu都运行；原ZIP官方digest/每文件清单、真实wheel/.coverage/全部运行config/数据/失败及精确SHA/tree相互核对。长路径预检，不把临时CImerge当main，省略工具字节必须明确披露。

## 五项修订的实施验收映射（仍Planned）

| 发现 | 具体资料 / 未来代码与测试 | 必要断言 |
|---|---|---|
| WORK-P3-001 | TEST_ISOLATION_PROFILE；validation/evaluator+experiments控制ledger；tests/validation/test_valid_004.py及双OS受管profile实证 | 真SID/UID及权限拒绝原始Test/seed/label/cache/log/report，批准evaluator正向；并发/断进程/改名/反馈泄露拒绝；同用户mock不替代 |
| WORK-P3-002 | LABEL_ACTION_PROFILE；validation/labels,splits；test_valid_001/002/003及QA004 | 两端同刻/±1us，old-share转换/日锚点，晚到修订/coverage/支付应收，日barclose及fit1us/闭区间purge |
| WORK-P3-003 | COMPOSITE_RESEARCH；research/composite；test_research_007及INT001 | 固定两因子/尺度/方向/交集重新z/缺失/零权重/阈值未定，冗余原/方向后矩阵，未来变化不改过去 |
| WORK-P3-004 | REPRODUCTION_PROFILE；experiments/reproduce；test_exp_003及P2回归 | 原0.2环境3原Ref重放/原字节manifest，P3新Ref；缺失篡改/旧receipt配新bundle/不同路径投影拒绝 |
| WORK-P3-005 | HAC_INFERENCE_PROFILE；validation/inference；test_valid_005/007/008与QA004 | 非零均值q1/q2及高精度p；251/252、399/400、lag/空洞/假设/未批拒绝；m4含失败项且批准拒绝 |

新增supplemental_cases.json在业务实现前手工定义；supplemental_reference.py仅开发方标准库核算，新候选QA-004独立复核待办，不能代为签收。旧15组/75断言是GPT Work补充执行记录；新开发方复算不冒充该身份。

## 当前e26之后的实施映射（仍Planned）

001以USER_DECISIONS具体方案及真实双OS主体证据验收；002以label_visibility_v2显式数据边界验收（禁止reference补时点）；005以HAC_GROWING_MDEP_2的新冻结N/整数根/q/依赖证明/不匹配拒绝验收，另独立核反例及有限N误差声明。003/004是e26设计关闭，完整INT001合成与旧三Ref真实重放仍是未来必交，不重复声明设计未补齐，也不提前宣称实现完成。
