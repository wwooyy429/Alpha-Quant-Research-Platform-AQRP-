# 19研究点／10执行点的预登记绑定 · G1候选

原P6 Task默认仍令P5对全部P3研究决策运行。P7主层不能在原T+1规则下逐日强求每日新买仓次日收盘立即卖出；必须预先分离研究与执行时钟。拟新增可选Task草案字段 `execution_sessions`，只适用于 `engineering_pipeline`，缺省仍为原全部研究决策，不改变旧默认API、旧零决策P5 API或既有已冻结请求。

本主层固定P3完整19点：2024-01-04至2024-01-22每天已有工程session。P5只选下列10个原始P3决策点：2024-01-04、06、08、10、12、14、16、18、20、22。日期对应原可信P1日历，禁止按真实交易所weekday重解释；1月6日存在仅因这是公开合成日历。所有日期及选取规则在任何结果前冻结，不能动态按风险拒绝/收益/目标是否变化跳日。

共享builder校验：必须为非空、无重复、严格按可信日历排序的ASCII ISO session字符串列表；每项必须是本次P3 config.decisions中已有且落入start/end范围的唯一session。未知/越界/乱序/重复/零点全部明确拒绝，不静默过滤、排序或扩成默认全部。research/replay kind带此字段拒绝。网页只提交上述会话列表，不允许自填decision_time或来源hash；时间从原P3决策解出。

冻结后 `EffectiveRequest.payload.research` 全19点原样保留。`payload.execution`增加服务生成的selection结构：模式ALL_RESEARCH_DECISIONS或EXPLICIT_SESSIONS、原始显式列表、原研究决策列表hash、完整解析列表（原ordinal/session/decision_time）、selection hash；所有内容进入canonical request/config_hash及Task原始字节。来源Ref、可信catalog版本、P1/暴露/coverage及完整研究配置仍由服务核实。现有campaign变体仍按研究配置预登记；执行选择作为不可变经济配置同样完整记录，但不生成family或重置共享预算。

`TaskService._pipeline_request`以完整真实P3终态为父源，复制原研究配置，仅在构造P5 INPUT时替换decisions为上述已核执行子集，再调用原execution_requests/bind_research。P3原config、所有五阶段行/统计/OOS/报告不改、不重算、不裁剪旧工件。每条P4分数必须来自该P3真实终态对应原时点行，记录P3原ordinal与execution ordinal的一一映射；原manifest/阶段hash/Ref/available_at和snapshot绑定全部继续由原门禁校验。禁止从主层19日结果挑出成功日或将事后训练结果回填决策。

resolved-plan在P5调用前冻结：完整研究列表hash、选择hash、实际P5请求原字节/sha、decision_count=10、R/B slots及10个真实P4 slot的index/time/source hash/owner/root。P5自身仍按原事件顺序逐点调用P4，不能创建外层假P4；P4 physical root仍在对应B run下portfolio-runs。Task成功仍需R、B、全部10个required P4和全局completion回执一致。R19成功不等于B10成功，P4缺任一点/风险拒绝/unknown或selection与resolved-plan不一致都失败关闭。

恢复不重新选点：核对原request、冻结selection、resolved-plan及实际原P3/B/P4绑定；重放保持已冻结执行点和原P5原始请求、重新绑定新Task所有权，不写原源。篡改合法session、错序/删点/用另一合法time、旧policy或defaults变化不能悄悄改变已提交请求。公开UI、TaskCLI和SDK使用同一builder；旧研究/回测CLI使用同一已冻结研究及P5请求原字节，不各自猜步长。

精确范围：execution_sessions本身仅对task_requests字段/规范化、tasks的P5输入接线/plan证明、TaskCLI与UI薄字段及相关证据作必要变更；本轮另将共同预算准入/ledger/Research/Task事务接线显式列为C-P7-003修订提案，具体路径见COMMON_BUDGET_ADMISSION_DESIGN与COMPATIBILITY_IMPACT。P1/P3因子/预处理/标签/统计、P4权重风险、P5事件/执行/账本不改。字段缺省兼容、旧config_hash/原Task完成屏障需回归，细节见COMPATIBILITY_IMPACT.md。

兼容限定：旧布局缺省比较只在同一新P7 bundle/catalog、相同输入与defaults下进行。原P6 raw内含旧bundle/catalog，原地在新P7宿主解析可能按原门禁拒绝，不能为“兼容”放宽检查；其恢复与声明重放在已审原包/锁/独立原工件路径。新的共同准入控制记录不混进旧raw，不修改金融或时序答案。
