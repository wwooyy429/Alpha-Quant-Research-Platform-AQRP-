# 拟新增薄适配接口（设计签名，尚未实现）

实际既有核心：`ResearchRequest.create(config, snapshot, exposures, coverage, code_commit)` 与 `research(request, output_root)`；`PortfolioRequest` / `construct_engineering`；`EngineeringBacktestRequest.create(data)` / `simulate_engineering`、`result_engineering`、`replay_engineering`；`ExperimentLedger.verify/catalogue/compare`。P6不得在页面复制其数值逻辑。

拟统一接口：`catalogue() -> verified resource/version/status records`；`freeze_request(kind, draft, defaults_revision, catalogue_revision) -> EffectiveRequest(raw_bytes, config_hash, lineage_refs)`；`submit(effective_request, idempotency_key) -> TaskReceipt`；`task_status(task_id)`；`cancel(task_id)`；`task_result(task_id)`；`artifact(task_id, artifact_name)`；`compare(run_ids, declared_projection)`；`replay(run_id, destination_catalog_id)`；`save_defaults(expected_revision, patch)` / `rollback_defaults(target_revision)`。新TaskCLI和Streamlit使用同一入口；旧CLI的同核兼容测试不可删除。

EffectiveRequest只允许已知schema/kind（research/engineering_pipeline/replay）和已审参数。服务端解析可信catalog ID到真实SnapshotRef/ExposureRef/CoverageRef/源run，校验字节、双时点、终态和代码/环境身份；来源hash、批准状态、code_commit、worker路径不能信任网页字段。未知字段/NaN/Infinity/重复键/伪造精确Ref/路径穿越拒绝。整数、价格、权重使用明确字符串/精确单位，转换只在共享builder中执行；UI不可归一化或改变经济profile。

`engineering_pipeline`由共享应用编排器顺序调用既有P3/P4/P5与PIT输入构造，必须生成真实源run/终态文件/manifest hash链；不能创建假P3/P4回执或把同UUID当证明。每次决策继续按P5数据可用性投影，不把研究期末整段结果提前回填历史。表单仅提供原契约允许的字段（股票池、区间、因子/权重、允许仓位/费用/风险设置）；组装代码属于services，页面只传draft与展示结果。

TaskReceipt包含task_id、预分配child slot/run_id及已核TaskContext绑定、canonical config_hash、defaults/catalogue版本、完整源/环境hash、当前状态和已绑定run IDs。任务元数据路径由服务生成的UUID+可信根确定，P3共享家族根不按task重置；P5内部P4根保留其父执行run下portfolio-runs（详NESTED_CONTEXT_CONTRACT）。输出run_id与随机时间可以不同，输入配置/语义数值不可因入口变化。

Artifact API先验证服务所属workspace、task/run绑定、原始账本终态和manifest，再按唯一条目读取原字节并复核hash。清单外追加proposal/同名替代/侧车篡改/别的run的合法UUID都拒绝。运行中可读追加日志须带明确prefix和非终态标识，不允许把部分result.json当SUCCEEDED。渲染器转义文本，结构化图表只消费白名单字段；不执行存储HTML/任意Markdown脚本。下载原始工件时保留媒体类型、文件名白名单和校验值。

Settings只能保存经共享schema校验的新默认配置revision，CAS冲突拒绝，rollback也新增revision并记录target；不可原地改旧配置或历史实验。catalog由可信本地启动配置限定工程根；网页不能任意切换根、上传代码、改Registry批准收据、启用formal或私有operator配置。

允许本地受控worker子进程，固定解释器/模块/argv（shell=False）、最小工程环境，无任意命令/插件路径。无新Web API微服务、Redis/Celery、后台常驻服务或调度部署。单工程用户模型不宣称多主体OS隔离。当前G1不启动worker/Streamlit。

时间表单保留证券市场/交易日历/时区与UTC微秒语义；共享builder按既定DATA_CONTRACT转为带时区时间，页面不以本机时区、weekday或当前墙钟推测交易日/decision_time/available_at。日期区间、拟合截止、期限、purge/embargo仍交P3原校验，不暴露私有FINAL_TEST。

页面缓存只用于明确不可变键（数据/侧车/Ref/bundle/锁/config/defaults revision）对应的已核只读投影；提交与claim不能放进缓存。每次状态/终态/原工件读取仍重新验证服务来源与manifest，不因session_state或缓存命中跳过完整性门禁。会话仅存draft/幂等键，不能作为真实任务/金融状态来源。

TaskReceipt还绑定固定kind、初始TaskPlan/ResolvedPlan hashes、完整required slot集合与各slot状态；研究/流水线/replay的全局完成条件见TASK_COMPLETION_CONTRACT。任何子run成功只改变该slot，Task成功须completion回执和终态事务全闭环。工程流水线真实P4为P5内部逐决策调用，不新增假外层P4；显式上下文传播、调用前登记、目录布局与原resume/replay兼容见NESTED_CONTEXT_CONTRACT。
