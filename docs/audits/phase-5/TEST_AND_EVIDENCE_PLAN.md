# 自动化测试及独立证据计划

2026-10-22 用户已明确确认：WI-R2-001、WI-R2-002持续 DEFERRED / NOT VERIFIED，统一延期至所有开发完成、最终集成版本完整40位SHA锁定后真实环境验证，届时执行方案/权限操作另行授权。R3代码、模型或CI通过不能关闭两项；原失败证据保留，各阶段既定回归和固定版本独立审核继续。详 docs/audits/windows-isolation-deferral/DEFERRAL_POLICY.md。本次只确认延期，不启用账户/修改真实ACL/部署/正式Test/金融批准，不扩大既有开发或合并发布权限。


现阶段所有P5产品测试PLANNED / NOT RUN；G1只核设计、候选答案与冻结输入。最少覆盖下列**测试类别**（计数不是已通过的产品用例）：

| 类别 | 已知答案/边界/性质及负向控制 | 需求 |
|---|---|---|
| T01时序 | close→available→decision→submit→next合法open；晚到1us/开盘同刻、假日；未来整日量/修订mutation正负控制 | BT001/002 QA003 |
| T02事件/订单 | 全部合法/非法转移；稳定排序、同ID同字节幂等/异字节冲突；取消/到期后拒填 | BT001/003 |
| T03执行模型 | 双边slippage tick；每Fill最小费；同证券多单共享10股；LIMIT保护，DAY/GTC跨session重查 | BT003/004 |
| T04资金与原子性 | 799/210/1009；多单预留不能超买；未交收不能买/卖；注入每个事务边界崩溃，全成或全无，重启不重扣 | BT005 QA003 |
| T05成本/归因 | 平均成本、减仓/跨零/short cover、entry/exit费用一次；分账重建独立于AccountState；每事件借贷=0 | BT005/007/008 |
| T06行动 | split/cash dividend/pay、oldshare/same时点entry/exit、short应付、支付后不重复；迟到修订失败；未定义碎股拒绝 | BT006/007 |
| T07可交易与估值 | suspended/borrow缺失/额度下降/市场gap/margin breach/缺open/退市；stale0/1/2session，持仓不丢 | BT004/006/007/008 |
| T08绩效 | 单调/全现金/亏损/零方差/非正权益/外部流，TWR/ddof1/A252/rf/净费用；long+short归因 | BT008/009 |
| T09替换 | 真正P1九文件+P3终态原engine+P4真实工件，仅改精确Ref，完整两次模拟；旧Ref/wheel重放与核心hash不变 | BT010 INT002 |
| T10身份/失败关闭 | 一致篡改合法parentUUID、终态后补文件、读取时换字节、发布前后/返回金额损坏、混合decision、未知schema/路径；正式入口拒绝 | BT001/005/010 INT002 QA003 |
| T11性质/大数 | 资金/费用/股数守恒、总容量/lot、拆股权益连续、同配置投影重放、极大整数/小金额与Decimal context不变；随机种子/失败样例封存 | QA003 +全范围 |
| T12独立参考 | 审查方从raw fill/action/cashflows重建而非调用production ledger；预定答案无需生产函数；统计用独立有理数/高精度参考 | QA003 BT005/009 |

关键backtest/execution/ledger/risk/performance业务模块行≥95%、分支≥90%，每个资金/时序关键不变量100%有明示案例；其他service/cli沿已批准测试策略门槛。总体覆盖率不能掩盖关键分支缺口。hypothesis已在锁内，仅在后续实现测试中使用；不新增依赖。性能阈值未获用户指定，先记录明确合成规模/环境耗时，不捏造SLA。

实施后完整SDK从干净提交构建真实wheel并在独立venv安装，回归实际已发布P4套件（目前844，后续收集数量以真实报告为准）、旧20/原四/91及旧因子重放；不因新增P5测试重写旧金融答案或删旧失败。Windows/Ubuntu官方CI各保留run_id/attempt/job、真实执行SHA（PR临时merge与head整tree/parents关系）、原始artifact ZIP/API digest/size、精确成员CRC/hash、JUnit/coverage/安装wheel/依赖锁/源码bundle/P1九文件/原始事件与账户/配置/结果manifest。不能用下载后重打ZIP冒充官方ZIP。

每个命令记录真实executor/cwd/argv/UTC起止/exit、完整stdout/stderr和首次失败；唯一run_id与不可变config、clean commit、environment/OS/Python/installer/lock哈希。封存manifest排除自身，外层receipt绑定ZIP与manifest并说明非数字签名。Git不能容纳的依赖或日志逐文件列省略理由/size/hash并留外置完整原字节，不能称仓库子集为完整证据。

G2须独立审核固定完整SHA及实际输出/落盘/返回字节，复现旧P4两缺陷与扩展金额/血缘控制；外置自查不能改名独立测试。正式Test/真实权限/金融批准保持延期，engineering SDK成功不改变该状态。所有High/Critical及金融安全Medium未闭环阻断。G1与G2、用户验收、合并标签分别记录。
