# 当前真实项目状态

日期2026-10-20（Asia/Shanghai）。Phase0批准/Gate记录在audits/phase-0；当前Phase1启动及范围/Python选择原话见audits/phase-1/AUTHORIZATION.json。

- **Phase0 = RELEASED**。用户已ACCEPTED；PR#1已合并；phase0-baseline已推送；Gemini已对固定基线完成Baseline Verification Gate并给出PASS。
- **F-001 / GOV-010 = RESOLVED / CLOSED**，按Gemini门禁报告登记，不再沿用此前等待最终复核的状态。
- **发布基线SHA：7de1d0e81385ae97f98ea673fe05dd726f0b577b**。
- 附注标签：phase0-baseline；对象0b2230cd4861ca3b47fa30fc30dae9f4dc4109d0，目标为上述发布基线。该标签不移动、不重建。
- PR#1获批head：228190a0c46595cf2927125fdc7d4f1c51b39ccf；实际merge：8c37e952be61054c6c72b5aaf573026c0355647b；merge tree与获批版本一致。
- Gemini此前设计审查版本1830b15给PASS/READY；本次独立主干核验明确覆盖发布基线7de1d0e，原报告按字节归档。
- 门禁原报告：audits/phase-0/gemini/aqrp_phase0_baseline_verification_gate_report.md；SHA-256：aa9761ef9ef20a5645d22297ab2ef9ee18455521c912226a2e342c1ff65129b1。
- **Phase1已获用户正式启动授权；执行状态 = PLAN REVIEW REQUIRED**。已确认首版仅合成数据/通用契约、真实源另定，业务Python精确3.13.16；当前Gemini计划预审尚未收到，业务实现未开始。
- 已从核实main 502c6931dcfce50bee2f71a80524475fae6396bf建立feature/phase-1-data-system；14项P1需求及预期接口/测试/风险见audits/phase-1/PLAN.md。启动许可不重复请求，仍须遵守本阶段Gemini预审及后续独立实现复核。
- P0稳定基线7de1d0e及标签不动；main上的502c693仅归档门禁与状态，本分支再追加P1计划与授权资料，不把当前计划提交冒充P0/P1已审版本。
- 核心需求保持106条/16组；CSV hash为20dd4e6be7188d3121f3cb361faf8901bc91815a6e9752beb14054a12183f0c1，核心金融/数据/接口契约不变。
- F-002 CI、F-003时间戳实现及测试留在P1；F-004物理云同步隔离未验证，原始Gemini执行脚本/日志未附等已披露限制保留。本次门禁PASS不自动验证这些其他能力。
- 数据、Registry、研究、组合、风控、回测、网页及业务测试仍Planned；高级扩展Deferred，真实执行Unsupported。P1合成范围及Python版本已批准，真实市场/profile和研究阈值仍按各阶段确定。
- P1计划文档核查见audits/phase-1的SELF_CHECK/COMMAND_LOG/MANIFEST；P0自查、原报告和已发布快照不重写。依赖候选仅元数据，不是锁/安装/CI成功；开发方文档核查不是业务测试或Gemini独立执行。

## 停止点

Phase0已发布；Phase1当前执行步骤为实施前计划/接口/答案预审资料准备。将固定SHA草稿PR和可直接交Gemini的指令交付，收到计划预审原报告并处理阻断事项后开展已授权P1实现。尚未创建业务包、安装业务环境或执行CI；P1验收/合并/发布及P2另行控制。

## 2026-10-21：Phase1计划预审归档

Gemini对380d9f8计划预审PASS；原始字节与SHA-256见audits/phase-1/gemini/PRE_REVIEW_EVIDENCE_INDEX.json，勘误/逐项处置见DEVELOPER_RESPONSE.md。当前状态IMPLEMENTING，按M1.1开始环境锁、隔离及真实CI验证；上述旧日期PLAN REVIEW REQUIRED已由本记录替代。业务验收尚未发生，所有未验证条件仍OPEN。main/稳定标签不变，禁止合并、标签、Phase2。
