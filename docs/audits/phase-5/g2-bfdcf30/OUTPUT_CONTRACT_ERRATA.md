# Phase5 未发布输出契约勘误

适用于0.5.0.dev2修复候选，原0.5.0.dev1/bfdcf30实验、失败和原报告原字节保留。不是修改P0冻结金融契约、输入 schema、G1合成经济口径或市场费用规则。

## 失败/取消

只有验证过的磁盘提交前缀可称 last_committed。`committed_state_verification.status=VERIFIED_COMMITTED_PREFIX` 给出commit_count、state_sha256、prefix_sha256；failed-state.json、transactions.json、transaction-files.json和committed-trace.json来自同一锁内恢复快照。trace.json仅为实际调度观察记录，可能晚于/漏掉已落盘但未来得及观察的最后commit，以明确的提交链为准。

`UNVERIFIED_COMMITTED_STATE`表示链/读取/资金对账无法确认。status必须FAILED，reasons含COMMITTED_STATE_UNVERIFIED、financial_state_known=false，并保留failure-recovery.json及原事务。不输出已知last_committed_account/failed-state/transactions替代未知状态。尚未建立事务目录的输入拒绝为NOT_STARTED。终态失败不提供成功performance，也不因已终态而允许再次扣费。

## Fill 暴露方向与两腿

| 字段 | 含义 |
|---|---|
| execution_side | BUY/SELL，由整笔 signed_qty 的符号确定 |
| direction | 单一持仓暴露方向为LONG/SHORT；跨零同时含两种暴露为MIXED |
| position_before / position_after | 实际成交前后精确有符号持仓 |
| position_legs | 1或2条，按先CLOSE后OPEN列明effect、direction、正quantity、signed_qty、fee、realized_gross |

纯开多BUY：OPEN LONG；空头回补BUY：CLOSE SHORT；跨零BUY：CLOSE SHORT + OPEN LONG。SELL对称。每腿 signed_qty 之和等于整笔成交量；fee按绝对腿数量比例精确分配，不再次分币舍入，总和等于唯一实际Fill费用；realized_gross仅在CLOSE腿归属。分腿不生成第二笔真实Fill/手续费或Journal。

原Fill.direction对空仓买入错误标SHORT，现已更正；跨零新增MIXED枚举，消费端须读取position_legs，不得把MIXED自动投给LONG/SHORT一方。FIFO片段及performance.contribution的原经济计算保持，不用修复字段回填历史实验。显式公司现金回收仍单列liquidations，采用同样腿说明，并不改称市场Fill。
