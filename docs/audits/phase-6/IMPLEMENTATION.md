# Phase6 八项受限工程实现候选

本次依据 IMPLEMENTATION_AUTHORIZATION.json 记录的用户实施授权，落实 G1 固定 e71f6f090b102e4abfd70a5999e495f49546a1b5 的八项范围。G1 原件、127 组设计答案及独立复核原文保持原字节；本文件记录实现，不修改原设计审查历史。当前 G2 PENDING，不是阶段验收。

## 真实调用链和完成条件

services/tasks.TaskService 是 SDK、aqrp-tasks 与六个 Streamlit 页面的共享入口。受信任本地初始化只生成固定公开合成输入/目录，不执行研究。页面不能提供文件根、代码、解释器、TaskContext 或权限布尔。冻结请求绑定输入目录 revision、精确 FactorRef、原始参数文本、P3/P5 配置、完整代码 SHA、core bundle、core/UI 锁与实际环境标识；默认配置 revision 仅影响新请求。

research 运行实际 P3；engineering_pipeline 运行 P3 和实际 P5。P4 仍由 P5 Simulator 内部调用，不额外运行一个独立 P4 充数。至少一个决策；全部必需 R/B/P:i 都成功、原工件/来源/事务/金融结果与预先绑定一致，且 completion 与 SQLite 终态提交闭环，Task 才成功。合法 P4 风险拒绝保留原 REJECTED 与 P5 原结果，整体 Task FAILED。P3 成功、P5 文件存在或单个状态字符串均不足以宣告 Task 成功。

## 持久化和恢复

SQLite WAL/FULL、BEGIN IMMEDIATE、唯一幂等键、owner+epoch、固定槽位与追加事件。每个核心 start 之前持久化预分配 UUID 和初始绑定；适配后的内部 P4 原始请求与 hash 在调用前持久化，父运行、实际物理根、决策、来源、锁、代码均绑定。authority 是本地可信启动器完整性接口，不是对任意 Python 的防伪沙箱或真实 Windows 权限隔离证明。

恢复须显式释放已确认退出的旧 claim，再用 recover 创建新 epoch；不从 PID/mtime 自动接管。已验证 P3/P4 终态只复用原运行，试验不重复登记或退款；确定未启动的后续槽位可首次执行。半初始化 P4 失败关闭；P5 保留原严格 resume 及部分发布拒绝规则。completion 写后 SQL 前崩溃保留原 completion.json，恢复另写带前件 hash 的 completion-epoch.json，不改原失败/回执。查询成功任务时重新验证全部证明，损坏显示 INTEGRITY_ERROR，原数据库历史状态仍保留。

取消先持久化意图，在 P3 阶段边界和 P5 完整原子事务边界生效。先取消则不能提交成功；成功提交先发生则 TOO_LATE。提交后读取实际持久状态，未知金融状态 FAILED / COMMITTED_STATE_UNVERIFIED，不展示可信旧余额。原失败与取消证据不改判。

## 页面及精确数值

Dashboard 展示真实任务和运行入口；Factor Library 读取实际目录/Ref/schema，可选择增删、配置 revision/回滚及版本参数比较；Alpha Research 直接读取 P3 IC/Rank/ICIR/分层/衰减/OOS/试验/提案与各预处理原工件；Strategy Backtest 读取 P5 原账户桶、订单/成交/持仓、净值/回撤、对账及 P4 来源；Experiment Manager 按任务/运行及状态筛选，比较、原报告下载及声明范围重放；Settings 保存追加式默认配置、显示输入/依赖与日志入口。HTML 报告作为原始下载/代码展示，不执行任意 HTML/Python。

数值适配按已审整数 coefficient/scale 与 HALF_EVEN，最长4096数字位/4098字符。权重除100不经 ambient Decimal。原始请求/金融数量和金额不回写为显示舍入值；图表仅近似显示并保留原值 tooltip/原表，无法表示时明确警告。词法通过仍须接受原 P3/P4/P5 领域校验。

## 重放和兼容边界

新 P5 数值重放在新执行 UUID/新内部 P4 根完成，原源只读。历史目录只允许可信本地启动器注册已验收的软件包/锁/旧 Ref/发布原文，实际调用旧环境重放三组已发布运行；浏览器不能选择路径或解释器。仍不代表完整历史宿主复现。

原金融算法和 core requirements.lock 保留；既有公开无 context API 继续原行为。既有文件仅适配显式上下文、协作检查点、初始绑定和重放归属。研究试验 fingerprint 排除新增 task_binding/task_binding_hash 运维元数据，避免同一金融实验因 Task UUID 不同失去重复试验识别；共享家族根、次数、预算和重复记录不重置。明细见 COMPATIBILITY_IMPACT.md 和 IMPLEMENTATION_IDENTITY.json。

## 证据等级

AppTest 是真实服务驱动的组件测试，不能代替真实浏览器。独立投影核对 tools/ui_reference.py 不导入 AQRP；逐一验证原清单/来源/hash，再仅规范预先声明的实际运行/根/来源哈希元数据，保留全部金融字段。tools/ui_smoke.py 实际执行 Momentum 与 Reversal 的 SDK、旧 CLI、新 CLI 及组件链和旧 Ref 执行。最终干净 SDK、双 OS 官方 ZIP 与固定版真实浏览器证据须全部完成后才交 G2；开发自测不称独立复核。

WI-R2-001/002 持续 DEFERRED / NOT VERIFIED。正式 Test 未运行，金融批准 NONE，完整历史宿主限制保留。未合并、打标签、部署、实盘或进入 P7。
