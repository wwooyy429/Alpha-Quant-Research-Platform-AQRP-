# 可直接交给GPT Work的Phase4 G1计划预审指令

请作为AQRP主要独立审查方，对以下固定版本执行Phase4 G1计划预审。请实际读取资料、独立复算并记录证据；本指令不是预设PASS。

- 仓库：https://github.com/wwooyy429/Alpha-Quant-Research-Platform-AQRP-.git
- 待审PR #6：https://github.com/wwooyy429/Alpha-Quant-Research-Platform-AQRP-/pull/6
- **固定审查SHA：`e40ddd0009cc30664c3a0fe0b74c4a497a541d77`**
- 已发布Phase3 main基线：`0a57dccb5618ba08cd3572d6d6b78fec963a3041`
- 已发布标签：`phase3-baseline`、`v0.3.0`，必须剥离附注标签后核对目标，不能把tag对象当commit。
- G1资料入口：`docs/audits/phase-4/REVIEW_PACKAGE.md`，所有资料均从上述完整固定SHA读取。

首先保存PR描述和初始/收尾head，核对`AQRP_FIXED_REVIEW_SHA`及实际detached checkout。若PR已漂移，只覆盖上述指定版本，并明确新提交未审，不用分支HEAD替代。请核对源码/测试/工具/CI/构建/锁/扫描配置及原P3审计相对发布基线逐字节未变；核对canonical106项不变、本期7项=4 MVP+3 Competition Ready。不要把旧文件中的阶段未授权文字覆盖最新用户明确授权记录。

用户已明确按受限工程范围验收并授权发布Phase3：金融批准、真实隔离、正式独立Test延期；历史复现按已验证软件包、依赖锁、旧因子版本和声明投影结果重放验收。用户只授权本次启动Phase4计划预审，不授权真实部署或实盘。请核对`AUTHORIZATION.json`、`PHASE3_RELEASE_RECEIPT.json`及Phase3的`publication/APPROVAL.json`、`DEFERRED_CONDITIONS.json`和`BASELINE.md`。这不是金融批准或对真实隔离/Test的验证，不应重新要求用户重复批准已明确的工程范围，也不能将延期条件写成已闭环实现。

请依次审查：

1. `PLAN.md`、`REQUIREMENTS_SNAPSHOT.json`、`REQUIREMENTS_TRACEABILITY.md`。逐项核对PORT-001/002/003、RISK-001/002/003/004是否完整、可实施、符合本阶段依赖；3项Competition Ready不能以占位或Unsupported替代。P5订单/撮合/资金账本、P6网页与P7完整替换不应提前实现。
2. `SCOPE_AND_DEPENDENCIES.md`。检查PORT-001对FACTOR-009/VALID-008的正式批准依赖被保留：正式ApprovedScores缺金融批准时必须拒绝；单独命名、显式SYNTHETIC/ENGINEERING_TEST_ONLY的入口只支持纯工程验证，不能伪造ResearchValidated、默认降级或借测试公钥取得正式金融批准。两条路径应共享同一组合与风险内核。请判断该设计能否在本次受限授权下推进工程验证，以及正式路径还缺什么。
3. `INTERFACE_DRAFT.md`、`SYNTHETIC_PROFILE.json`。核对证券/市场/币种、父快照/hash、所有输入PIT及共同决策时点；账户估值与当前持仓、非入选持仓平仓；精确数量、资金及不可变契约。核对单/多因子权重、交集、零负分和并列规则；LongShort真实双腿、G/N预算、中心化与空腿/重叠拒绝；整手向零取整后重查全部约束；gross/net/leverage/全额和半额turnover、行业净/总暴露及Beta；borrow总额度、sellable、跨零、停牌及平旧空；现金/短卖冻结/额外保证金/费用缓冲不能重复扣算或误用权益。候选规则仅合成profile，不能推断为真实市场规则。
4. 公开入口与风险不可绕过：失败应保留诊断，但不能生成成功/可执行目标；不得信任调用者risk_passed或陈旧对象；RebalanceProposal须不可执行，不写订单或账本。分析缺输入、未来/混合时点、NaN/重复键、篡改来源、错误审批域等反例。
5. `GOLDEN_REFERENCE.md`与`golden_reference.py`的G01–G20。请按原始输入独立复算，尤其G08/G11/G14/G15/G17/G18/G19及容差。开发方20组算术校对只属设计候选，不能当P4业务实现或独立正确性证明；不要仅重跑开发方参考脚本便认为答案已独立核对。可编写自己的stdlib Fraction/Decimal参考，保留推导、输入、容差、真实输出和命令。
6. `TEST_AND_EVIDENCE_PLAN.md`、`BASELINE_VERIFICATION.json`、`validation/`及`FILE_MANIFEST.json`。核对未来已知答案、边界、性质、独立参考、干净wheel SDK、双OS官方原ZIP及内部hash/源码/环境/数据/重放证据计划充分；新源码须重新准入审查，不复用P3 receipt。逐项核对资料hash。若运行PR CI，它只是现有P3 578项回归，不能算P4实现或G1结论。

既有Phase3主审G2只覆盖`9ac5db069287a6e4a095e25ae8c3cc8fa229cded`，三缺陷已CLOSED，578独立SDK和双OS原ZIP证据保留；Phase3合并SHA为`70086a74a632c73a2769ec24901ec47babfa8976`，发布登记为证据/状态增量。本轮开发方对合并版本实际重执行SDK578、旧20、原四、数学91，不是新独立主审，计数不相加。完整本地开发方SDK选择包位置和sha见`docs/audits/phase-3/publication/SDK_ARCHIVE.json`；仓库副本显式省略22个依赖wheel及1个原cache日志，不能当完整原包。原扫描命中/处理保留在SCAN_DISPOSITION.json，不新增扫描豁免。请分别报告你实际新执行、只核对原日志、静态审查和NOT VERIFIED的范围。

请输出：固定SHA及环境/实际权限；7项覆盖与依赖结论；Golden独立答案/容差/真实执行证据；逐项发现ID、严重性、需求、准确文件位置、独立反例及建议；仍需用户决定；正式Test/真实隔离/金融批准未验证及对未来阶段的影响；最终**PLAN PASS**或**PLAN BLOCKED**。G1通过不等于P4实现通过、金融批准、用户阶段验收或P4实际实施授权。

请将报告、开发方修复清单、原始脚本/命令/日志/环境及结果hash封存到独立审查目录，明确这是GPT Work实际审查，不能覆盖开发方Golden或旧报告。不合并PR、不打标签、不部署、不改账户/ACL/服务/调度、不接实盘、不执行正式最终Test，不进入P5。
