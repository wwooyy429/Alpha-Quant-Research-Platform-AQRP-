# 六页面的完整工程交付

| 页面 | 必需交互与数据 | 拒绝与证据 |
|---|---|---|
| Dashboard | 已核因子目录数、各真实task状态、最近研究/回测及错误警告，链接真实run | 损坏manifest独立标INTEGRITY_ERROR；不计为成功；无任务显示空状态 |
| Factor Library | 目录/详情、精确Ref、参数schema、工程/金融状态；选择增删、配置权重、版本与参数比较、配置revision回滚 | 增删是选择/配置而非代码执行。仅当前catalog允许Ref可执行；旧制品原Ref可读且按声明范围重放；撤销/缺包不冒充可执行 |
| Alpha Research | 股票池/因子/区间/期限/已审预处理、提交与取消、原始/Rank IC、ICIR、分层/衰减/OOS表和图 | 有效样本/NA原因/切分/多重检验/试验记录均可见；无正式Test选择；原始报告及校验下载 |
| Strategy Backtest | 显式工程模拟、精确因子权重/仓位/风险/费用，研究/组合来源、净值/回撤、订单/Fill/持仓/逐桶资金表 | 正式策略与候选正式调用后端拒绝，无隐式工程回退。known=false不显示可信余额/权益/绩效；工程结果不称金融批准 |
| Experiment Manager | 按run_id/状态筛选、版本/参数/数据/代码/环境差异，原报告/日志下载，已声明重放及结果比较 | 只读原终态；未知/缺包/锁不一致/投影以外给明确原因，旧run及原报告不覆盖 |
| Settings | 合成源目录状态、默认字段/费用/风险、core与UI扩展依赖、原始/安全日志、revision保存与回滚 | 只影响新有效请求；旧snapshot/hash保持；不存真实密钥，不操作账户/ACL/服务，不提供任意文件根 |

版本回滚指可审计配置revision回退；不自动批准已撤销代码或篡改FactorRef。执行目录必须来自真实已审制品，旧Ref不能改成当前implementation hash。历史复现延续已验收的package/lock/oldRef/result projection边界，展示明确能力及证据，不以“历史版本存在”声称任何宿主能重新执行完整研究。

UI-007额外验收：Momentum与Reversal各按同一数据/配置，通过实际旧CLI、新TaskCLI/SDK及真实Streamlit事件各跑研究和工程回测；保存请求config_hash、P1/P3/P4/P5来源与各声明数值投影，逐入口相等且两因子的预定差异真实存在。不要求两种因子收益相同。只展示预先计算示例、只比较截图或mock service不算通过。
