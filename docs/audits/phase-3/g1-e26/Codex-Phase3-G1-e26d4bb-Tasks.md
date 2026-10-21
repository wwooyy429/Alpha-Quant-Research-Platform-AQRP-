# 转交Codex：P3 G1 e26增量复核

固定SHA：`e26d4bbfe28262c35396f66daa183771573a988e`；旧版d10；基线f26255fc40a3080bfa883ad64938f60036a14759。**PLAN BLOCKED**。
复核期间PR更新ff4c546b9a8f6652ff70804055d9435ac08f63b3；该新提交未被本报告覆盖，不据此回退/覆盖新工作。

- WORK-P3-003 Medium：CLOSED，仅设计。compose/共同交集z/方向/固定权重/冗余/INT001映射与答案已核；实现待后续。
- WORK-P3-004 Medium：CLOSED，仅设计。原wheel真实保管与hash/26模块已核，旧wheel独立env路由/API矩阵/投影原则明确；完整EnvironmentArchiveRef和实际旧三Ref重放尚未验证，不能全部Unsupported后报验收。
- WORK-P3-001 High：OPEN。方案在声明信任模型下可行，但e26无用户实际主体/保管/审查/路径/部署授权决定。请给具体配置表供用户确认；本轮未部署。正式Test fail closed，VALID004不可全项完成。
- WORK-P3-002 High：OPEN。时序/old-share锚点/coverage/fit/purge与新答案一致，但待用户确认合成经济假设；普通行动case需显式给event/available默认或界限/coverage修订，不靠reference隐藏fallback确定最大可用时点。旧正确Golden保持。
- WORK-P3-005 Medium：OPEN。28组146断言虽全通过，固定q=max(h−1,5)的正式推断依据仍不充分。独立有界MA1反例gamma0=.5/gamma1=.25，其真LRV=1，而q5 Bartlett极限11/12（q9=19/20，q19=39/40）；增加n门槛不消除固定窗taper偏差。提出开发期预注册且可论证的带宽/推断规则、限制模型/替代法，或具体可验证的偏差/误差校准；否则只保留非formal模式。不能以用户批准252/20/5替代数学依据。

本人真实执行：旧15组75断言、新28组146断言，共43组221断言；非零HAC p由独立高精度数值积分核；另实际重放开发方122断言。状态码仅设计谓词，不是未来API测试。旧66项证据/9份接收原件/50冻结资产/106目录/26需求/两OS当前原ZIP各417及原wheel核验通过。审查helper首轮类型错误保留，未改正式输入答案/容差。

正式金融日期/样本/预算/阈值协议仍需用户及证据；无ResearchValidated/StrategyApproved。下一步复核新固定SHA，不合并、不标签、不进入P4；不把本补充审核写成Gemini执行或P3验收。
