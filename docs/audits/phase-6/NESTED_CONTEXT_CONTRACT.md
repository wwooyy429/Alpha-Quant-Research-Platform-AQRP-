# 可信上下文到P5内部P4的传播与物理目录（G1候选）

本文件处理WORK-P6-G1-002，状态OPEN_PENDING_RECHECK。源事实：P5 Simulator._risk_portfolio现在调用construct_engineering(request, self.root/portfolio-runs, code_commit)，provider.verify_portfolio_result在同根核验，_submit还会复核；P5 replay又创建独立Simulator。因此只有外层service参数不足，以下为明确且非金融的适配设计。

## 注入链与绑定

采用显式可选keyword参数，不使用全局变量、thread-local/contextvars、monkeypatch或事后从UUID猜所有权：TaskService/可信worker → services.backtest的simulate/_execute/resume/replay → Simulator实例的execution_context → 每次_risk_portfolio的P4 child context → portfolio.service/ExperimentLedger.start。_risk_portfolio和_submit的verify_portfolio_result同时取得对应expected child binding。上下文只提供登记/解析/验证/安全取消能力，不选择因子、不改风险或记账。

TaskAuthority由可信本地launcher连接既定workspace任务库并在worker进程内创建；前端/JSON/普通用户draft不能提供authority、context、run_id、root或trusted=true。核心入口拿到上下文后必须用已配置authority核实际持久化记录和当前claim，不能接受调用者自报布尔或任意duck-typed函数返回“可信”。此为本地工程应用完整性协议，不是OS隔离/密码签名；任意拥有进程/磁盘写权的主体隔离仍属延期事项，不声称Python对象不可伪造。

每个绑定的不可变元组为(workspace_id, task_id, task_kind, plan_hash, slot_id, service_kind, decision_index, decision_time_UTC, source_request_hash, adapted_request_hash, parent_slot_id, parent_execution_run_id, child_run_id, physical_ledger_root, core_config_hash, code_sha, code_bundle, core_lock_hash, ui_lock_hash)。不适用字段显式null。P4的parent是实际当前B执行UUID；重放时是新的replay执行UUID，原source P5 UUID另列source_ref，绝不冒用原任务的孩子。

初始Task事务先登记R/B（或replay执行）固定slot和UUID。ResolvedPlan封闭时，从P5请求的完整有序decision集合预分配P[i] slot、UUID、预期parent及root。P4实际适配请求依赖当时真实账户，不能提前伪造hash：_risk_portfolio获得原adapt_portfolio返回的request后、调用construct之前，authority在SQLite事务中以同一task/parent/index/time/source hash核对预分配记录，保存适配raw bytes/hash和core_config_hash，状态由ALLOCATED一次性变BOUND/START_INTENT，提交后才能创建P4目录/初始事件。已绑定的不同hash、时间、root或父run拒绝；不能在P4返回后补填原来不存在的登记。

新的可选TaskRunContext将不可变binding_hash写入核心初始lineage并由start核配置/UUID/root/服务匹配。当前worker claim/epoch每次由authority验证：不可变孩子归属不随接管重写；恢复新claim追加授权接管事件，旧handle epoch失效。禁止两个并发claim执行同一slot；不同task/P5实例有各自不可变context引用，SQLite事务约束和原文件锁互补，不以全局“当前任务”切换。

## 固定目录，不移动原P5内部P4

```text
workspace/
  task-control/tasks.sqlite
  tasks/<task_id>/request,plan,completion,task-events...
  research-runs/<P3_uuid>/                 # 所有研究Task共享家族/试验预算根
  backtest-runs/<B_uuid>/                 # P5原物理根
    portfolio-runs/<P4_uuid>/             # 继续使用P5现有内部根
  replay-runs/<new_replay_execution_uuid>/
    portfolio-runs/<new_replay_P4_uuid>/   # 新执行的内部P4，绝不写原run
```

“共享根”要求准确收窄到P3研究家族/预算，不强迫P5内部P4移到全局目录。任务库维护全局索引，但必须记录并验证上图真实物理根。P5的P4 root恒等于guard_path(parent_execution_root / portfolio-runs)，不能由网页传路径或从合法UUID拼另一个任务根；原终态manifest、candidate/risk/result原字节与发布审计、P1/P3原输入来源的所有检查全部保留。目录枚举/权限错误、链接或reparse逃逸不能当空目录成功。

## 内部断点与恢复/重放

内部P4合法终态已写但slot映射未写：只可找到原先已BOUND/START_INTENT的slot，核全部元组、初始binding/config/lineage、物理根及原始终态门禁后追加该slot VERIFIED，不新建P4、不提升Task。若无预登记或binding缺失，即使UUID和manifest合法也RECOVERY_REQUIRED。相同UUID换根、换parent/decision/请求、其他task的合法P4、重复别名、未知子目录都拒绝。

P5按原resume条件重放已提交事务prefix时，execution_context先解析同一index的原P4 slot。已有已核终态且适配raw request相同则返回原P4结果，经原provider校验后继续原事务比较；不能再调construct创建第二个P4。若尚未启动且可证明ALLOCATED则首次调用；半初始化/非终态P4无现成恢复协议，一律RECOVERY_REQUIRED，不借P5 resume重做P4。适配request与旧绑定不同则拒绝，不改输入迎合重放。已提交Fill及原错误记录不覆盖。

replay_engineering使用新的Task replay context/预分配目标根和内部P4 slots，原P5 source只读；原金融request_id仍保持以维持原确定性订单/事件算法，任务执行UUID另行绑定。完成后Task层封存本次返回、比较证据、目标事务和内部P4清单；仅NUMERICAL_REPLAY_VERIFIED字符串而缺本次目标/所有权/比较证据不足以使Task成功。旧无context的所有公开API继续原随机UUID、原目录/验证流程与行为，不连接任务数据库、不改旧结果/Ref或强迫旧run迁移。

## 实施后的完整非金融适配文件表

| 文件 | 允许的适配 | 禁止变化 |
|---|---|---|
| 新services/tasks.py、task_context.py、task_state.py / 请求builder | 固定kind、SQLite分配/claim/完成屏障、authority/上下文、请求及结果封存 | 无任意DAG/脚本；不实现第二套金融内核 |
| experiments/ledger.py:start | 可选预分配UUID和binding初始记录、独占创建/验证 | 无context原行为完全保持；不覆盖旧run |
| services/research.py | 可选上下文/协作取消，P3共享家族根绑定 | 不改fit/标签/推断/试验预算语义 |
| portfolio/service.py:construct_engineering | P4孩子context转交start和来源绑定 | 不改构造/风险/取整/发布数值 |
| services/backtest.py:simulate/_execute/resume/replay | 传递/恢复上下文、原resume条件再加绑定验证、replay目标归属和封存 | 不放宽原金融/状态/部分发布拒绝 |
| backtest/engine.py:Simulator.__init__/_risk_portfolio/_submit | 实例context、调用前P4登记/原终态复用、把expected binding传入两处验证 | 不改事件排序、预算、交易、风险算法或事务数学 |
| backtest/provider.py:verify_portfolio_result | 可选expected binding与authority核元组/根/初始记录，再执行全部原门禁 | 不移除prepare/guard_sources/manifest/candidate/risk/发布字节校验 |
| 构建/准入/CI/覆盖与UI新模块 | 原兼容计划列明的版本/新bundle/扩展依赖/证据测试 | core锁、旧制品、答案、金融公式不改 |

G1仅列设计，不修改上述业务文件。未来若需其他既有文件适配或金融计算变化，应先列影响并取得适用批准/新固定SHA审查，不能以本表泛化许可。
