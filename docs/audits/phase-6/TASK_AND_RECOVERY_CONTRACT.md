# 持久化任务、完成屏障与安全恢复

当前为G1修订候选，三项原发现OPEN_PENDING_RECHECK，P6业务未授权/未实现。TaskService使用stdlib SQLite（BEGIN IMMEDIATE、workspace/idempotency_key唯一约束、WAL、同步提交）持久化分配/claim/追加事件，P3/P4/P5原实验账本及事务仍是核心事实来源。任务元数据目录分开，P3共享研究家族根；P5内部P4保留原P5 run下portfolio-runs。详细且唯一的完成/恢复与目录规范分别见[TASK_COMPLETION_CONTRACT](TASK_COMPLETION_CONTRACT.md)、[NESTED_CONTEXT_CONTRACT](NESTED_CONTEXT_CONTRACT.md)。

状态QUEUED→RUNNING→SUCCEEDED/FAILED/CANCELLED；CANCEL_REQUESTED是待执行意图而非已取消。单个slot终态只更新slot，不能直接提升Task。仅冻结kind全部required slots、实际工件/父链/完整金融验证、全局completion回执和SQLite终态闭环才SUCCEEDED。原G16–G19单状态模型只说明孤立slot的终态单调性，不是多阶段Task归并规则；本轮另增多阶段答案。

同key同有效config_hash返回原task，不再调用；同key异hash拒绝。相同配置新key是新实验，继续写同一P3家族/次数/预算；取消/失败不退款、不丢试验。并发只有一份有效claim，恢复epoch只追加、旧handle失效。网页和JSON不能提供context/root/归属布尔。

取消先持久化，在P3阶段间或P5完整原子事务边界检查，禁止中途kill并伪称安全取消；提交后继续原重读对账。取消先于全局成功提交则不提升成功；成功提交先完成则取消TOO_LATE。未知金融状态FAILED+COMMITTED_STATE_UNVERIFIED，不显示旧余额、不认证CANCELLED known=true。一次完整事务或既定阶段是取消响应边界，不虚构延迟SLA。

崩溃恢复只恢复已核slot；后续未执行阶段仅在原计划、有效claim和“确定未启动”证据齐全时继续。P5只能使用既有严格resume条件，同slot原P4终态可复用但不重算；不明/半初始化/部分发布进入RECOVERY_REQUIRED。最终Task屏障重新验证，不从PID/mtime、一个成功P3或文件存在推定成功。失败、首次异常、磁盘提交、原始日志及旧hash完整保留。

G2须实际覆盖SQLite/真实核心服务及磁盘的每阶段提交/映射、内部P4绑定、取消/成功竞争、completion与索引断点、同key并发和跨Task家族预算。模型通过只是G1参考，不是实际实现/并发/隔离验证。真实Windows R2两项及正式Test/金融批准/历史宿主限制不变。
