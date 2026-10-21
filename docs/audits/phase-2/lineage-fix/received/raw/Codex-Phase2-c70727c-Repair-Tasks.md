# 给Codex的Phase2固定集成版复核任务

目标：c70727c39182f81ee142730da9a9833a51581cd1；GPT Work补充审核；整体仍BLOCKING。

- WORK-P2-001：补充复核通过。三处共享源码等于发布main及已审8902ba0，新bundle及双父集成正确；原16全部通过、原UNKNOWN日历到因子反例已通过。
- WORK-P2-002：OPEN / Medium阻断。格式化但语义相同的JSON被接受，write_run保存原字节却hash canonical投影。统一config/batch/实际文件/manifest，或明确拒绝非canonical输入；保留原正负控制。
- WORK-P2-003：OPEN / Medium阻断。config.params由lookback2改1而旧hash/0.21结果仍被接受，真实1是0.1。按schema重算并交叉核对参数hash；不为旧结果改贴标签。
- 本轮新SDK392通过、原16通过、原四探针2失败/2通过；当前最终头双OS原ZIP已真实核验。不要用392/CI绿代替修上述两项。
- 保留Golden/容差/锁、P1修复与历史原件。修改P2源码后实际重审并更新全bundle/准入回执，提交新40位SHA及差异，运行完整适用验证及未改原16/四探针。
- 只登记真实GPT Work证据；本报告未改正式状态，不代表用户验收、合并/标签/发布或Phase3授权。
