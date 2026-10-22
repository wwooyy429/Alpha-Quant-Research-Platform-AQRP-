# 可直接交给GPT Work的Phase4 G1增量复核指令

请作为主要独立审查方，复核AQRP Phase4 G1两项设计修订，不启动P4实现。

- 仓库：https://github.com/wwooyy429/Alpha-Quant-Research-Platform-AQRP-.git
- PR #6：https://github.com/wwooyy429/Alpha-Quant-Research-Platform-AQRP-/pull/6
- **新固定SHA：`265af16353d85ce8c2d229a7517809d707498da8`**
- 原已审SHA：`e40ddd0009cc30664c3a0fe0b74c4a497a541d77`，结论PLAN BLOCKED，P4-G1-001 High及P4-G1-002 Medium均OPEN。
- Phase3已发布main/phase3-baseline/v0.3.0：`0a57dccb5618ba08cd3572d6d6b78fec963a3041`，受限工程验收及延期决定保持，不重新要求批准已明确的P3范围。

请保存PR描述、初始和结束head，校验AQRP_FIXED_REVIEW_SHA并detached checkout完整新SHA；新HEAD漂移不在本次范围，不能以分支头替代。所有材料在固定版本`docs/audits/phase-4/`。

先读`DEVELOPER_RESPONSE.md`、`STATUS.json`及`g1-e40ddd0/FINDING_DISPOSITION.json`。原报告/交接/65项成员及原manifest、原receipt和完整ZIP均在`g1-e40ddd0/`，原文件按字节归档，无省略，含attempt-1失败。原ZIP269458 bytes，SHA256 `2e81fcfb77e83a51c802acc662edb6ed58d6cb25e2612bf540c47f38745c5d4d`；原manifest SHA256 `86f6daff0a5f33c4cdaeef2a7021468390eb7f02222d46636964ba880ac994cd`。请独立核对，不把开发接收结果当主审新执行。

重点复核：

1. **001 High：** `INTERFACE_DRAFT.md §3.1`、`SYNTHETIC_PROFILE.json.quantity_policy`、`ROUNDING_REFERENCE.md`及`rounding_reference.py`的R01–R13/R17。仍对绝对目标向零取整；理想数量恰等于原仓时精确保留，可不动奇零股，不生成零量建议；所有变化非零目标和所有非零delta分别整手。仅target=0、delta=-完整原仓、原full-close flag=true可对非整手delta全平豁免，正负仓一致，不免任何其他风险。部分奇零股及非整手跨0拒绝，不自动拆单，不换成交易增量格点。请确认X01 target10/90、delta -5/+90被明确拒绝；X02不动奇零股没有自相矛盾；关闭flag、加减原long/short、跨0和外部非整手目标各边界一致且不能由公开service绕过或推到P5。
2. **002 Medium：** `TEST_AND_EVIDENCE_PLAN.md`及R14–R16。性质仅覆盖固定正价格、正权益及固定行业映射下各绝对目标数量/名义金额、gross与行业gross不增；不能推广至Beta绝对值、signed净额/行业净、换手、现金/许可。请独立复算X03的q*=(25/3,-10)→(0,-10)，Beta与行业净0→-.5、abs0→.5，区间[-.1,.1]pre过/post拒；X04当前(10,0)、cash400、p=(60,50)、等权目标，turnover .6→1.1，cap.8先过后拒。确认保留全部前后风险检查，未削弱正确expected。
3. **原经济口径不变：** free_cash=E*(1-gross)-nonshort_restriction-fee_reserve，100%短卖冻结加额外100%短仓保证金、无融资，因此gross cap1.5不意味着资金允许gross>1。G08预算算术与G19拒绝均不改，不擅自放宽交易权限。
4. 原G01–G20、`golden_reference.py`、canonical106及本期七项4MVP/3CR、P0–P3原审计、源码/正式测试/工具/CI/构建/锁/扫描配置、1957冻结资产仍应未变。请查需求增量映射、全部FILE_MANIFEST与`validation-revision-e40ddd0/`命令/环境/hash。新增17组仅为开发方设计算术/整除候选，不是P4产品测试或独立审查。请用自己的原始输入与推导核对，而非只跑开发参考脚本。
5. 原e40的双OS CI成功，但前次主审只核API/日志/集成tree/上传digest文本，未下两份原ZIP、未独立核内部JUnit或重数578。请保留该证据限制。新CI若成功亦仅为现有P3业务回归，不能作为P4实现通过、G1自动PASS或补写原ZIP独立验证。本轮没有必要重复运行未改P3全SDK；你若实际新增执行，应保存真实命令/环境/输出并正确归属。

请给出固定SHA、实际权限/执行范围、65件原证据与变更完整性核对、独立复算结果、001/002分别OPEN或CLOSED及理由、新发现/尚缺条件，最终PLAN PASS或PLAN BLOCKED。请明确工程计划门禁与真实隔离/正式Test/金融批准NOT VERIFIED的区别。

报告及原始脚本、日志、输入/答案/环境/hash请另存独立目录并封存，不覆盖开发方候选、原报告或失败记录。G1通过后实际P4实现仍须用户单独授权；本轮不实现、不合并、不打标签、不部署、不改账户/ACL/服务/调度，不实盘，不进入P5。
