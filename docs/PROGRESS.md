# 当前真实项目状态

日期2026-10-20（Asia/Shanghai）。用户批准见publication/APPROVAL.json，独立门禁结论见gemini/GATE_EVIDENCE_INDEX.json。

- **Phase0 = RELEASED**。用户已ACCEPTED；PR#1已合并；phase0-baseline已推送；Gemini已对固定基线完成Baseline Verification Gate并给出PASS。
- **F-001 / GOV-010 = RESOLVED / CLOSED**，按Gemini门禁报告登记，不再沿用此前等待最终复核的状态。
- **发布基线SHA：7de1d0e81385ae97f98ea673fe05dd726f0b577b**。
- 附注标签：phase0-baseline；对象0b2230cd4861ca3b47fa30fc30dae9f4dc4109d0，目标为上述发布基线。该标签不移动、不重建。
- PR#1获批head：228190a0c46595cf2927125fdc7d4f1c51b39ccf；实际merge：8c37e952be61054c6c72b5aaf573026c0355647b；merge tree与获批版本一致。
- Gemini此前设计审查版本1830b15给PASS/READY；本次独立主干核验明确覆盖发布基线7de1d0e，原报告按字节归档。
- 门禁原报告：audits/phase-0/gemini/aqrp_phase0_baseline_verification_gate_report.md；SHA-256：aa9761ef9ef20a5645d22297ab2ef9ee18455521c912226a2e342c1ff65129b1。
- **Phase1基线前置门禁 = UNBLOCKED**；**Phase1执行状态 = AWAITING USER AUTHORIZATION / NOT STARTED**。用户尚未单独授权Phase1，本次仅归档及更新状态，不创建P1分支、环境或业务模块。
- 获得Phase1授权后，仍须完成阶段计划、适用前置决策及Gemini预审，从核实main创建独立分支；不能把基线门禁通过解释为所有实施条件自动满足。
- 当前main仅追加本次报告/状态/自查记录；经审发布基线仍为7de1d0e。新归档提交不自动计入Gemini已审范围，不能再宣称后续main head永远等于旧标签目标；逐文件版本见当前MANIFEST和Git diff。
- 核心需求保持106条/16组；CSV hash为20dd4e6be7188d3121f3cb361faf8901bc91815a6e9752beb14054a12183f0c1，核心金融/数据/接口契约不变。
- F-002 CI、F-003时间戳实现及测试留在P1；F-004物理云同步隔离未验证，原始Gemini执行脚本/日志未附等已披露限制保留。本次门禁PASS不自动验证这些其他能力。
- 数据、Registry、研究、组合、风控、回测、网页及相应业务测试仍Planned；高级扩展Deferred，真实执行Unsupported。市场/profile、精确环境版本、研究阈值仍按DECISIONS和阶段条件确定。
- 本次文档自查见当前SELF_CHECK/COMMAND_LOG/MANIFEST；合并后原始17项检查证据及先前报告保持原状。开发方文档核查不是业务测试或Gemini独立执行。

## 停止点

Phase0已正式发布并完成独立主干门禁闭环。本次按用户授权归档门禁原报告、更新状态及PR审查记录后停止；等待Phase1单独启动授权。
