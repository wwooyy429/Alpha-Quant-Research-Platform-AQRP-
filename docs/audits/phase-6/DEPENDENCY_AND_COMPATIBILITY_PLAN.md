# 固定依赖候选及兼容影响（尚未安装/批准）

元数据候选：Streamlit==1.66.1、Plotly==7.1.0；来源与轮子SHA见DEPENDENCY_METADATA_CANDIDATES。使用已验收uv0.13.4、Python3.13.16目标分别解析Windows x64与Linux x64，得到51/50个包的完整hash候选锁，原21个通用core依赖及Windows colorama版本逐项固定，未升级NumPy/Pandas/PyArrow/DuckDB或既有测试/构建工具。

**当前仅metadata解析成功，不是实际安装、浏览器、双OS UI或安全验收通过。** UI_CANDIDATE_*.lock只在审查资料目录，不替换根requirements.lock。已从各组合解析候选中导出UI_EXTENSION_WINDOWS/LINUX.lock，各恰好29个额外包、不含任何core包项；实现授权后使用原core锁 + 对应扩展锁安装，避免重复core条目扩大原批准wheel哈希集合（保留core锁原字节），`--require-hashes --only-binary=:all:`干净安装，逐包核真实兼容wheel、官方SHA、Requires-Python、pip check与实际import/版本；失败禁止静默降级/换版本。G1候选锁变动需新固定SHA，不能在实现时漂移latest。

拟采用同一Python3.13.16工程虚拟环境的core+UI扩展组合，避免第二套数值内核。core原锁和core环境核验仍按原精确包执行；TaskService另记录并校验完整UI扩展distribution/version/RECORD与扩展锁hash，绑定任务/图表/报告来源，不能把旧core manifest冒充完整UI环境身份。额外UI包不得授予因子或金融权限。不启用Streamlit云部署、auth/pdf/SQL/Snowflake等extras，也不引入第二回测引擎或新Web微服务。

实施期预期允许的包装兼容变更需独立审查：pyproject的可选UI依赖/入口、src/aqrp/__init__.py版本、当前bundle准入收据、tools/ci.py的新增UI验证/工件选择、覆盖门槛适配、安装元数据测试、新UI扩展锁和新增ui/services/任务CLI模块。原FactorRef不可重写；旧wheel/锁/原答案保留。root core lock/admission LOCK_HASH保持原值；若实际设计需改变，则作为契约/兼容变更重新提交预审，不能悄悄放宽verify_runtime或reviewed_policy。

明确的既有服务兼容适配为：experiments/ledger.py 的可选可信预分配run_id/TaskContext，以及services/research.py、portfolio/service.py、services/backtest.py的可选context转交和协作取消检查点。它们必须校验持久化task/slot所有权，不能信任网页伪造context；属于应用编排，禁止改变数值计算。上述适配（见TASK_AND_RECOVERY_CONTRACT），旧调用不传参数应完全保持行为和结果；必须列出每处差异与原SDK及G2故障回归。P1/P2算法、P3统计/标签/OOS、P4构造/风险、P5订单/时序/逐笔账本/绩效不在UI重写范围。不得删除旧完整性、安全门禁或降低覆盖率来迁就界面。

主要资料：[Streamlit发行](https://pypi.org/project/streamlit/1.66.1/)、[Plotly发行](https://pypi.org/project/plotly/7.1.0/)、[AppTest官方说明](https://docs.streamlit.io/develop/api-reference/app-testing/st.testing.v1.apptest)、[AppTest覆盖范围](https://docs.streamlit.io/develop/concepts/app-testing/cheat-sheet)。AppTest是模拟执行检查页面元素；不把它写成实际浏览器/网络或部署验证。
