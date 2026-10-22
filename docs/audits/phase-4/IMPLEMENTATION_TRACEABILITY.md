# Phase4七项实际实现追踪 · 待G2

原106目录不改，本阶段4MVP/3Competition Ready。当前只标IMPLEMENTED_PENDING_G2，不是独立通过/阶段验收；原G1两项只CLOSED_DESIGN，G2仍须检验运行时。

| ID | 实际代码 | 实际验证及独立答案 |
|---|---|---|
| PORT-001 MVP | portfolio/contracts,construct,service,research_input；共同工程服务、原字节请求/工件、完整目标/数量/诊断/不可执行建议 | test_contracts,test_construct,test_research_input；账户原值不改、P3原终态分数实际读取、正式审批拒绝、原始失败/manifest |
| PORT-002 MVP | weights.allocate；共同交集、单/多因子固定系数、等权/分数权、LongOnly、零负分/现金/lot | 独立G01–06/10与冻输入base/odd_hold；test_construct多因子与性质、test_risk_service三资产/顺序 |
| PORT-003 Competition Ready | weights真实双腿/gross/net/中心化，construct数量，risk资金/许可 | test_construct两种真实双腿，test_risk_service G08/G19的0.7/-0.5及资金-200、三资产7/16/1/16/-1/2；空腿/重叠拒绝 |
| RISK-001 MVP | risk/checks逐票/gross/net/leverage/全额及半额turnover，所有pre/post | x04独立.6→1.1，所有限额真实服务负例与固定容差边界，不夹紧或松绑 |
| RISK-002 Competition Ready | contracts强制PIT暴露/限额，checks行业净总及signed Beta | x03独立0→-.5，G16 Beta1.1、两行业与净总分离；缺失/未来/重复/过期/错父拒绝 |
| RISK-003 Competition Ready | 精确lot、可交易/short许可/借券总额度/可售，完整全平不豁免其他限制 | x01、short_close、G1矩阵、borrow不足精确边界、停牌全平/可售拒绝、局部不动照计风险 |
| RISK-004 MVP | 公开check_target重构candidate，service只消费本次风险结果，失败无target并封存失败ledger | 候选/request篡改、各拒绝/非法输入/内部故障/终态写入与后补工件拒绝、不可执行建议、结果原字节重放 |

金融金额/风险的已知答案、边界、性质和独立参考保持分层。开发方自测不是GPT Work独立审查，正式Test/真实隔离/金融批准延期不因本实现消失。真正订单提交/撮合再查属于P5，没有提前创建模块。
