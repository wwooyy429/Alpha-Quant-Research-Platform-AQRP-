# Phase 3 Alpha Research & Validation 计划（待Gemini预审）

当前修订：**PLAN BLOCKED / DESIGN REVISED / FIXED-SHA RE-REVIEW REQUIRED**。GPT Work d10五项设计发现及处理见DEVELOPER_RESPONSE.md；以下初始计划由文末专项设计补充，未获Gemini G1放行。

启动已授权，起点为已验收发布main/phase2-baseline/v0.2.0同点f26255fc40a3080bfa883ad64938f60036a14759。本轮仅文档、需求映射和独立手算候选，不新建P3业务包，不改发布源码/正式测试/工具/CI/锁/Golden/旧审计原件。状态PLAN PRE-REVIEW REQUIRED；不得把启动授权当Gemini计划PASS。

范围固定canonical phase=3共26项：23 MVP、3 Competition Ready，逐项见REQUIREMENTS_TRACEABILITY.md及原条目快照；不删除DATA-012、FACTOR-007、RESEARCH-003三项Competition Ready，不增加研究DAG或外部插件执行需求。阶段支持日频SYNTHETIC_V1，真实市场/源仍另行确定；Python仍3.13.16标准GIL/x64、既有22包requirements.lock。拟先用既有NumPy做OLS/数值、标准库做明确统计投影；是否需另锁SciPy/statsmodels由预审评估，任何安装/升级均先列候选和兼容证据，不在计划轮静默改锁。

G1后实施顺序：

1. P3.1：冻结本轮独立输入/答案、协议/分割/访问与实验状态契约；先建全部实验与失败ledger，再运行候选；先建立标签/最终Test的分离权限入口再评估。
2. P3.2：DATA-012的PIT行业/市值/可选Beta侧车快照；只追加接口，不给P1严格8表快照偷偷加第9表。Price-Volume按P0公式、独立答案和代码审查准入实现，不拿Volume冒充。新增源码后重审完整bundle/receipt，未经审查不执行因子。
3. P3.3：逐证券session算子、白名单条件和五阶段处理链，记录拟合区间、缺失/去极值/标准化/中性化诊断，未启用阶段为SKIPPED并指向输入，不假造计算。
4. P3.4：Validation标签端独立生成next-open→horizon-open含行动收益，IC/Rank/ICIR/分组/TMB/衰减/年度/因子相关，严格按同cutoff/股票池/stage对齐。
5. P3.5：时序split、purge/embargo与walk-forward、受控Test访问；HAC及多重检验/全部候选记录/重复指纹/预算和污染门禁；预先标准缺失则正式审批拒绝，不能自动ResearchValidated。
6. P3.6：统一research服务及最薄CLI、静态JSON/HTML研究报告和实验重现，Momentum→Reversal只改精确Ref跑完整研究；真实错误/失败落账，不靠mock或占位成功。P4组合/风险、P5订单账本回测、P6网页、P7全链/比赛仍Planned。
7. P3.7：独立答案+边界/性质、已发布417基线回归和原16/4、干净wheel/双OS/原始ZIP核验、冻结完整SHA给Gemini实现复核，再申请用户验收；P3合并/标签与P4启动另行授权。

预计改动范围（预审后）：data/exposures.py与独立sidecar快照；factors的Price-Volume及必要兼容元数据；research/{contracts,operators,pipeline,neutralize,cache,engine}、validation/{labels,metrics,splits,inference,approvals}、experiments/{contracts,ledger,reproduce}、研究专用services/cli/reports，按最终接口精简，不能为了目录填空。相关tests和新P3 Golden、CI覆盖/上传/版本候选0.3.0仅实施时变更。原factor数据API签名/三公式不能破坏；必要修改先记录影响、兼容/原Ref重放及全bundle审查，不重写P1数学。

当前关键待决见DESIGN_DECISIONS.md：真实Test评估权限部署、正式研究通过门槛、HAC小样本/lag与统计依赖假设必须明确；本轮提供可审建议与失败门禁，不代用户批准。本地工程逻辑隔离不得冒充独立OS权限隔离，所有未实现能力保持Planned/Unsupported/Conditional。

## GPT Work补充G1审查后的修订状态

旧固定d10a55a被判PLAN BLOCKED（2High/3Medium），原件与ZIP完整归档g1-d10/。本轮仅设计修订，五项逐条处理及外部批准边界见DEVELOPER_RESPONSE.md；没有开发方代审查方CLOSED。

实施顺序补充：P3.1先落实获批P3-ISO-OS-1主体/输入投影/预算原子性及LabelCoverageRef；标签按SYNTHETIC_V1_LABEL_1。P3.3后实施compose固定研究分数与冗余报告并接INT-001。P3.5按P3-HAC-BARTLETT-1显式工程门槛且正式标准缺失拒绝批准。P3.6采用P3-REPRO-ARTIFACT-1旧wheel独立环境重放，不原地迁移旧Ref；全部业务仍Planned。只有G1固定新SHA预审通过、High设计闭环及所需用户决定到位后才实施。
