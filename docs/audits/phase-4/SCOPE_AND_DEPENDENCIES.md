# Phase4依赖与受限工程输入

本文件落实用户2026-10-22的范围决定，不修改独立审查原结论。

| 依赖 | 已有工程证据 | 未满足/延期 | P4处理及影响 |
|---|---|---|---|
| FACTOR-009、VALID-008 → PORT-001 | 精确Ref、准入hash及终态manifest绑定的审批实现、工程正负例 | 真正金融标准、最终独立Test与正式ResearchValidated证据 | 正式ApprovedScores仍拒绝；显式EngineeringScores只用于合成工程测试，无收益/投资有效性结论 |
| VALID-004/005 | 封存接口/协议/逻辑拒绝工程测试 | 四主体真实权限隔离、正式Test、金融批准 | 不部署，不调账户/ACL/服务/调度；不能把本地逻辑校验叫真实隔离 |
| DATA-005、DATA-012 → RISK-003/002 | P1状态/主档及P3 PIT暴露侧车 | 真实市场、借券/交收/费用规则接入 | 使用显式合成profile与夹具，真实市场另审；缺数据拒绝，不填0 |
| EXP-003 | 已验证wheel、锁、旧Ref及结果投影重放 | 历史完整宿主/安装器全字节复刻 | P4仍记录软件包/锁/数据/结果hash；不宣称宿主等同 |
| 账户状态及OrderEvent | 接口设计、合成AccountSnapshot | P5真实模拟账本与成交再检查 | P4纯输入快照/目标/建议，不写账本；调仓建议不可执行且不创建订单 |

EngineeringScores必须携带scope=ENGINEERING_TEST_ONLY、dataset_kind=SYNTHETIC、明确fixture_manifest/hash、来源run和精确FactorRefs（若来自真实P3合成运行，校验终态工件hash及时间）；接受手写合成夹具时明确source_kind=DECLARED_FIXTURE，不冒充实际研究运行。金融approval必须NONE。纯工程输出不得转换正式批准对象，不导出可执行订单。业务签名显式分开construct_engineering与construct_approved；共享同一计算内核和风险顺序，禁止默认engineer回退或布尔skip_approval。审批文件/终态清单不可后补绕过。正式入口将来依既有审批验签和证据域校验，无正式批准返回APPROVAL_REQUIRED，不能自动接受测试公钥签名为真实金融审批。

当前授权不允许为打通正式入口而建立真实保管主体/权限或重新使用最终Test。P4工程验收若完成只能证明契约、算术和约束行为；正式策略可用性及金融批准仍待上述延期门禁。独立审查须分别报告工程闭环与正式依赖阻断，不把延期能力伪装已实现。
