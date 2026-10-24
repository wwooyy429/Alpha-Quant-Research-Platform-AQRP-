# C2固定版本G2接收与开发处理

独立审查版本 `eae807f957f178d19bc55dcfbd668caff5470c6e`，主审GPT Work：G2 BLOCKED / REQUEST CHANGES。原SDK1496与双系统通过不关闭三个反例。原文在 received/，接收核验见 RECEIPT_VERIFICATION.json：原ZIP902364045 bytes / SHA256 086c0a1d7128c241bff30cfed32f9d5178940c9decf3942cd462021f30983b3c，304声明文件+manifest，全成员逐字节哈希及CRC已核。原失败记录和原C2证据不覆盖。DEV-P6-001由主审确认CLOSED — FIX VERIFIED。

| 发现 | 开发处理 | 审核状态 |
| --- | --- | --- |
| WORK-P6-G2-001 High | 引入不可变预登记campaign及完整variant集合、全局别名和共同Holm声明。首次有限默认计划只登记一次；之后未登记参数明确拒绝。显式新计划保留此前数据访问污染，不能补充同数据预算。Task提交在SQLite事务中预留candidate×horizon单位，预算固定12，所有计划共享、失败及取消不退、幂等不重复预留；登记、请求、保留记录均有原始字节/哈希和清单绑定。原P3试验记录继续保留，Task拥有的R不重复计数。 | OPEN / FIX IMPLEMENTED, PENDING INDEPENDENT RECHECK |
| WORK-P6-G2-002 Medium blocking | 取消收尾重新读取实际P5/重放物理事务链、初始锚、原文件集合和完整逐桶projection，含已SUCCEEDED子运行。缺失/损坏/枚举或读取错误则FAILED / COMMITTED_STATE_UNVERIFIED，保留取消意图、原错误、原子阶段结果和失败字节。成功取消后再损坏则公开INTEGRITY_ERROR，不改历史终态。 | OPEN / FIX IMPLEMENTED, PENDING INDEPENDENT RECHECK |
| WORK-P6-G2-003 Medium blocking | 新P6可信合成目录含SYN_U、SYN_CORE4、SYN_TAIL4；克隆原历史成员时序并保留有效/可用时间、修订与P1快照校验。网页双表单、CLI及SDK同入口绑定universe_ref，实际P3成员筛选及P5输入in_universe逐时点调用P1 universe_at。未知ID、任意路径或伪造ref拒绝。 | OPEN / FIX IMPLEMENTED, PENDING INDEPENDENT RECHECK |

必要自测、新固定SHA、安装包及两系统官方原ZIP、真实浏览器证据在交接包另列。草稿期间无同SHA完整验证通过声明；最终以PR9唯一AQRP_FIXED_REVIEW_SHA和该版本封存收据为准。独立主审决定是否关闭发现，开发方不自判G2通过。

旧catalog/1工程目录及dev2轮次保持只读历史，不原地迁移或改写旧family。dev3新工程目录使用catalog/2；共享预算/污染控制边界为一个工程workspace内同数据身份，不能冒充跨机器、跨数据克隆的真实隔离或金融批准。默认计划公开其有限集合，不能把first-use登记描述成用户正式预注册研究或正式Test。其余金融数学和原G1 Golden答案不变。

八项受限P6工程范围；不合并、标签、部署、实盘、正式Test、金融批准或P7。WI-R2-001/002和真实Windows隔离DEFERRED / NOT VERIFIED；完整历史宿主限制保留。


DEV-P6-002：C3固定418c17fad8fefe50dedc866f95c14ccf0fa433ca的1558项预检及覆盖率门禁通过，安装包测试亦已1558通过；收尾发现只读SQLite连接未显式关闭造成资源警告。dev4改用closing确保正常/异常路径均关闭，增加两项实际连接生命周期回归，不降低检查、不改变金融数学或预算。C3原日志/工件/浏览器前缀保留，不能移作dev4证明；最终重新锁完整SHA执行SDK/双OS/原ZIP/真实浏览器。见RESOURCE_LIFECYCLE_REPAIR.json。三项独立G2仍OPEN，DEV-P6-001独立关闭结论保留，DEV-P6-002是开发自查修复待主审。
