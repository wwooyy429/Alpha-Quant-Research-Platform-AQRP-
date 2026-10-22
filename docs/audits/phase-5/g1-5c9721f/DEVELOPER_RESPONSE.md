# 四项G1设计发现的开发方处理意见

原独立报告只审5c9721f96679f4d495b7b3b93af3e2e31e66ae62，结论PLAN BLOCKED / REQUEST CHANGES。收尾bd18d1b98b5647f4f4b6345ffe73dca40acaf038未被该报告覆盖。接收已核原96,239,761字节封存ZIP、CRC/246精确成员/245项hash；原报告、初稿/最终反例、原日志逐字节保留。开发方对比发现三个受影响核心草案从5c到bd未改，本轮在bd之上修订；这是开发方对比，不冒称审查方审了bd。

| 发现 | 原级别/状态 | 本轮设计修订 | 新预设答案/验收 | 当前关闭权 |
|---|---|---|---|---|
| WORK-P5-G1-001 | High / OPEN | EVENT_TRANSACTION_ADDENDUM：外层信封总序、70每笔原子、80/90子记录、最新pre/post版本与commit序、65/95/100及恢复边界 | N01/N02/N03，A后B风险拒绝，前/后崩溃快照；未来产品需真正故障注入和重放 | OPEN_PENDING_GPT_WORK_RECHECK；C-P5-001还需明确用户接受冻结契约细化 |
| WORK-P5-G1-002 | High / OPEN | CASH_BUCKETS_AND_PROJECTION：C_set/U_free/U_short互斥，S_set是子集；trueA不重复冻结；P4free=A−F_unused−H，H仅预算保守量 | N04–N11，min-fee short交收前后A899不变、partial cover、cross-zero、红利支付与合法新short | OPEN_PENDING_GPT_WORK_RECHECK |
| WORK-P5-G1-003 | Medium / OPEN | EXECUTION_PRICE_AND_FEES：买卖/Market/Limit统一固定双边价格域，所有余单上界+累计paid≤F，取消不退已付费 | N12–N17，极端有利sell gap无Fill/fee、limit滑点、partial最低费/预算拒绝/取消释放 | OPEN_PENDING_GPT_WORK_RECHECK；新经济选择待后续用户接受 |
| WORK-P5-G1-004 | Medium / OPEN | FIFO_ATTRIBUTION：CLOSED_FIFO_FRAGMENT、历史lot费用/红利池精确分配，pay不重计、未平单列、undefined原因唯一 | N18–N25，+2.5/−4.5与5/9、A borrow.08→net−.01、partial/cross-zero、红利及精确分摊 | OPEN_PENDING_GPT_WORK_RECHECK；统计口径待用户接受 |

原GOLDEN_CANDIDATES.json与reference_check.py（25组/70项）保持原字节，不迎合修订修改正确答案。G25仅静态子例补语义说明：U_free50/U_short0/S_set200，不再冒充新short全生命周期。新增SUPPLEMENTAL_CANDIDATES与supplemental_reference_check为纯设计标准库参考，不导入AQRP、不实现业务引擎，不等于独立审查或P5产品通过。

冻结契约/源码/测试/依赖/CI不改，C-P5-001影响与批准在CONTRACT_CHANGE_IMPACT。四项不自行CLOSED或PLAN PASS，候选待新完整40位SHA审查；PR描述AQRP_FIXED_REVIEW_SHA锁定，历史锁与包不覆盖。P4验收/发布、R3代码独立PASS与原WI-R2延期均不变。P5业务仍未授权，未合并、标签、部署、正式Test、金融批准、实盘或P6。

## 一并保留的既有静态回归修复

本轮首次P4静态冻结检查因docs/REVIEW_PROTOCOL.md失败；该文件在此前1ab819a延期记录提交中被加了提示，已存在于bd18d1b。现恢复为已发布32ea基线原字节，不改检查/期望hash；延期原话与义务仍完整保留于AGENTS及windows-isolation-deferral专项记录。首次失败原命令/stdout/stderr和处置在developer-validation/PREEXISTING_REGRESSION_DISPOSITION.json；仅重新执行受影响检查，通过3440冻结文件核对，没有重复已通过的算术或改写失败。此恢复是文档一致性修复，需随新固定SHA复核，不改变main/旧标签。
