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
