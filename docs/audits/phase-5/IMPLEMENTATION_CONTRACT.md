# Phase5 工程实现契约 simulation/1.0.0

当前0.5.0.dev5增补：[003处理](g2-bf5e5a8/DEVELOPER_RESPONSE.md)、[输出/恢复元数据](g2-bf5e5a8/OUTPUT_CONTRACT_ERRATA.md)、[独立复核入口](g2-bf5e5a8/REVIEW_PACKAGE.md)。固定bf5e5a8原001/002保持关闭，同一003 High为PARTIAL FIX / OPEN，整体BLOCKED；以下旧状态/旧候选说明保留历史，不代替本轮固定版本验证。


当前0.5.0.dev4增补：[003处理](g2-bf5e5a8/DEVELOPER_RESPONSE.md)、[输出/恢复元数据](g2-bf5e5a8/OUTPUT_CONTRACT_ERRATA.md)、[独立复核入口](g2-bf5e5a8/REVIEW_PACKAGE.md)。固定bf5e5a8原001/002保持关闭，同一003 High为PARTIAL FIX / OPEN，整体BLOCKED；以下旧状态/旧候选说明保留历史，不代替本轮固定版本验证。


当前0.5.0.dev3增补：[003处理](g2-35f93d6/DEVELOPER_RESPONSE.md)、[输出/恢复元数据](g2-35f93d6/OUTPUT_CONTRACT_ERRATA.md)、[独立复核入口](g2-35f93d6/REVIEW_PACKAGE.md)。固定35f93d6原001/002已独立关闭，新003 High仍OPEN，整体BLOCKED；以下旧状态/旧候选说明保留历史，不代替本轮固定版本验证。


当前0.5.0.dev2修复勘误以[g2-bfdcf30/OUTPUT_CONTRACT_ERRATA.md](g2-bfdcf30/OUTPUT_CONTRACT_ERRATA.md)及[修复复核入口](g2-bfdcf30/REVIEW_PACKAGE.md)为准：原bfdcf30独立G2为BLOCKED，两项仍待新固定版本独立确认；以下原实施说明及正确经济口径保留，不把旧PENDING或正常SDK通过改称G2通过。


本文件是已审固定5262032、用户明确接受C-P5-001及P5-D01–D10、单独授权12项实施后的实现说明。原G1十二份设计文件及P0/P1/P3/P4金融契约保持原字节。本文件不授金融批准、真实Test、部署或阶段验收；实际开发方执行结果以指定完整SHA的SDK/CI原包及外置封存收据为准，G2仍待GPT Work。

## API与身份

`EngineeringBacktestRequest(raw: bytes)`冻结完整JSON，`simulate_engineering(request, ledger_root, code_commit)`返回不可变`BacktestResult.raw`；状态、结果、数值重放分别由`result_engineering`、`replay_engineering`实现。`resume_engineering`只恢复未终态的原工程run，校验起始config/lineage链、相同软件包与protocol；部分发布需要保留证据并审查，不能覆盖其原文件后伪称成功。同步运行被中断时保留已提交状态并发布CANCELLED，失败/取消没有成功收益报告。

原始请求按hex与SHA保存在config，非法UTF-8也能保留原字节。run_id由既有ExperimentLedger生成唯一UUID；调度/订单/Fill以request_id命名空间生成可重放UUID，与run_id共同标识事件。请求冻结资产、CCY单币种、SYNTHETIC_V1工程日历、初始现金、每决策费用预算、ADV参数与历史版本、开盘/收盘侧车、P3/P4原始输入、行动、外部流及控制。该profile从现金开始，持仓完全由真实模拟成交/行动产生；原运行恢复保留完整既有账户。

生产回测核心没有具体因子分支、Registry、插件执行或Streamlit。应用侧SignalProvider只释放注册时间的原P3标准分数；P4适配生成新、明确记录的预算请求，原分数/父ID/Hash与终态engine/P1九文件链重新验证。源码/配置不以调用者传入金融批准标志取得正式许可。`simulate_approved`独立拒绝APPROVAL_REQUIRED，无工程路径回退，不读取正式Test。

## 时序与原子性

全局队列仅有外层信封(time,phase,seq)：10交收/拆股/ex/支付（按规定子顺序）及明确外部资金流、20行情、30信号、40组合候选与预算、50真实P4风险服务、60原子篮子提交、65取消/到期、70逐单MatchTransaction、95借费、100估值。Fill80、Account90只在70事务内部。订单和每次实际Fill均核对真实P4终态清单/返回原字节；实际Fill再读最新状态，执行真实E_total/A与P4保守投影完整风险。

一份不可变commit文件绑定pre/post版本、hash、原始输入、内部子记录、全部资金/持仓/订单/费用/共享容量及Journal。准备文件不是提交；fsync后原子发布commit。恢复以原始请求确定性重执行，并逐个比对既有提交前后hash、子记录、payload及序号；已提交事务不再次扣费/消费容量，未提交准备文件继续留作失败证据。目录和文件链接/硬链接替代拒绝，链损坏失败关闭。此机制不宣称硬件掉电、远程文件系统或真实Windows三主体权限已经验证。

所有可执行订单必须eligible_at严格晚于submitted_at，并属于下一合法日历开盘；available<=decision<=submit，开盘同刻提交也顺延。晚到开盘侧车不倒填。GTC重新查许可、借券、风险、容量、价格域和可见历史量；DAY/GTC在约定session收盘到期。控制的received_phase区分65前输入与70中到达：后者下一UTC微秒确认，available_at早于实际接收时刻的迟到取消拒绝。成交不可被取消抹去。

## 执行与历史量

固定合成最大容量每证券每开盘10share，所有订单共享。请求显式冻结lookback_sessions和minimum_adv；工程样例为1个已完成session、10share门槛。每个历史量修订包含security/session/revision_id、event_time、available_at、标准share数量；按当前时点选择可见的最新修订，不能用当日未完成/未发布成交量。实际P3来源的历史量必须与原P1八表中对应所有修订原值/时刻完整匹配，不允许挑选有利版本。量缺失、发布未到或不足窗口不成交；实际可用容量还取min(固定10,可见ADV)，再按lot截断。参数不在运行中自动改变。

所有BUY/SELL及MARKET/LIMIT，decision冻结原价p0，raw和滑点后实际价均在双边[ceil(.95p0),floor(1.05p0)]中；LIMIT只收紧。买上取分、卖下取分，10bps；逐Fill佣金HALF_UP_cent(max(1,n*p*.001))。累计已付+所有余单逐share最坏上界必须≤固定F。每篮子提交资金/最坏费/ADV全部检查，失败整篮REJECTED；实际风险失败取消余单，不把ACCEPTED回退REJECTED。每Fill只付款一次；取消/到期不退已付费用。

## 账本与行动

精确Fraction贯穿数量、货币、均价、费用池和风险；只在指定实际费用事件舍入一次。有限十进制原值完整输出，非终止比例包含numerator/denominator与独立展示值，不能用显示舍入值做判断。交易、费用、应收应付、支付和逐时点估值均有经济科目复式分录，数量另按证券单位平衡。独立读侧只用原Journal重建现金与股数；原始Fill/action/flow另由标准库参考工具重建，不能把AccountState用作答案。

P4已验证的宽位数输出使用其独立输出域解析器消费，不拿34位输入校验器去截断输出。账户适配采用无损科学记数编码，保持原P4输入域不变；无法在原域精确表达的投影明确P4_PROJECTION_NUMERIC_DOMAIN_EXCEEDED失败，绝不近似成另一个合法账户。P4保守预算的风险比率/目标换手估计与P5按真实decision前权益计算的已成交换手分别保留；即使P5通过，P4预算限制仍可拒绝，必须报告真实A、H、两种权益及原始失败检查，不能称为真实资金不足。

C_set/U_free/U_short互斥，S_set只在C_set内；真实A=C_set−S_set−M−O−P_res−Z。T+1由实际工程日历推进；short未平所得从U_short进入C_set/S_set，A不变。cover按原始FIFO gross cashlot解除限制，未交收款仍不能提前花。P4free=A−F_unused−max(V−S_set,0)，H仅投资预算保守量，不写真实现金分录或制造流动性。

持仓平均成本不含费用；FIFO统计另以CLOSED_FIFO_FRAGMENT计数，历史入场费/借费/long红利/short应付按当时未平lot和实际平仓比例精确归属，支付不再计收益。split保持总成本/权益/历史金额池，非整数证券或lot余量拒绝；取消原活单后才允许新决策。PER_OLD_SHARE以前一session收盘股数锚定。明确合成退市现金回收是公司行动，按声明回收值关闭持仓并单列liquidations，不伪造市场Fill/滑点/交易佣金；未明确回收事件的已退市持仓失败UNRESOLVED_DELISTING，绝不以零代缺失。显式已知零回收与未知值不同。真实税、券商和碎股规则不在本profile。

## 报告与验收

成功结果包含精确账户、历史订单/Fill/资金/Journal、每日估值、风险原始检查、FIFO片段、收益/波动/Sharpe/MDD/TWR/换手及多空净贡献。A252、ddof1、rf_daily0；样本不足、零方差、非正权益、无赢家/亏损/完成样本均给明确undefined原因。外部流按发生前后分段TWR，不作为净收益；费用/滑点已经入账，绩效不得再扣一次。

业务实现、开发方SDK/CI、GPT Work G2、用户阶段验收及main发布是不同事实。WI-R2-001/002持续DEFERRED / NOT VERIFIED；最终集成40位SHA真实验证另行授权。正式Test、金融批准、完整历史宿主的既有延期/软件包+锁+旧Ref+结果重放边界保持。当前不授权合并/标签/部署/实盘或P6。
