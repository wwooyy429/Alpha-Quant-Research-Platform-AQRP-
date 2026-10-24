# P7 可选执行子集接线的兼容影响 · 待G1

此为尚未实现的明确范围，不修改任何已审正确答案或P6已审业务。未来实现须用户单独授权，候选完整SHA重新SDK/双OS/原包/真实浏览器及GPT Work G2。

| 允许文件/类别 | 必要变化 | 不变条件/回归 |
|---|---|---|
| src/aqrp/services/task_requests.py | 新可选execution_sessions词法/可信日历子集校验，pipeline的服务生成selection进入新请求字节 | 同一新bundle/catalog、相同输入未给字段时的原task-request/1布局、原字节及config_hash保持；不得强加新字段到旧请求；unknown/research/replay字段拒绝；研究19点及campaign控制不变 |
| src/aqrp/services/tasks.py | 由冻结selection构造P5输入、冻结原ordinal→执行ordinal/hash映射、resolved-plan及读取校验 | 原P5内P4分配/physical root/全required屏障不放宽；无新金融逻辑，同一新bundle/catalog内旧布局恢复/重放按原schema；跨包回原包隔离路径 |
| src/aqrp/services/task_cli.py | 如需新增原命令参数，仅将显式列表传统一builder | 原JSON request入口在同包catalog匹配时继续接受缺省旧布局；旧包跨bundle仅原环境只读/声明重放，不在CLI挑选日期或计算时点 |
| src/aqrp/ui/app.py | pipeline新增可选执行session表单；只传draft和展示已核解析结果 | 原默认页面/配置/CAS/旧请求不改；不以结果动态改执行点 |
| 新src/aqrp/competition/薄适配 | 已核离线输入/规则/能力报告映射到相同原服务请求 | 不得新增另一风控、模拟器、账户或任意Python/网络真实源 |
| tests/integration、tests/e2e、tests/competition及受影响UI任务测试 | 新字段/双时钟/全链/合法风险拒绝/错血缘/恢复/重放/入口一致 | 旧单元/故障/原Golden全部保留，不把新通过覆盖旧失败或真实R2 |
| tools/e2e工程运行器/独立reference/既有UI参考与smoke必要扩展 | 19→10映射、12预算、逐桶/前后完整原字节/每入口对照与工件选择 | reference不得导入被测产品生成expected；旧比较白名单不扩大成忽略所有hash/lineage |
| src/aqrp/__init__.py、pyproject.toml、reviewed_code.json及新身份清单 | 新实现版本/83+新模块bundle/受审receipt与原制品对应 | 不编造未来hash，不以旧bundle收据批准新代码；core/UI lock不升级，旧软件包/Ref保留 |
| 新tools/check_phase7_package.py、tools/ci.py及P7 e2e/competition smoke/reference工具 | 明确阶段包准入、既有完整回归之后新增P7真实链/参考/证据目录，上传选择器与错误完整性 | 旧check_phase6_package原字节保留用于固定P6源/旧wheel环境；不在P7新bundle上硬套旧83/禁止competition约束，不取消原5016/旧正确答案保护；详PACKAGE_GATE_AND_CI_PLAN |
| .github/workflows/ci.yml及必要安装身份断言 | 明示phase7阶段/工件名，补e2e/competition路径和新版本安装身份 | 固定Actions SHA/两OS/Python/锁/只读/无秘密及失败上传不放宽；exact-member/whole-subtree校验含新目录，旧业务tests全部保留 |

Task optional字段兼容策略：缺省请求保留原task-request/1布局，原payload.execution键集合和raw hash不改。显式execution_sessions请求在payload.execution增加版本化selection（如execution-selection/1），只允许新实现按已审规范解析；旧实现遇新字段明确不支持，不能丢弃后按全部日期执行。validate_effective必须从原raw_draft和可信catalog重建完全一致字节。旧已提交请求不经defaults或新增字段迁移；旧重放直接按其原请求及原schema解释。

原P6发布Refs固定包bundle28c3cc049efcce8fc3e55b4056e8e116f98deca39eeb1d2c8822799c8e98855b与factor_version1.2.1。未来新增模块/接线导致新bundle是预期，**不能在新bundle宿主伪称旧implementation_hash仍可加载**。INT-003旧pin验证采用原包/依赖锁/旧已审制品的独立安装路径和声明重放；新P7 runtimeRefs只能在真实实现固定SHA核实。原包路径不是完整历史宿主复现，也不是任意候选代码沙箱。

上述业务/实施模式接线须G1闭环和用户单独实施授权。计划模式仅限当前已授权G1所需文档/包范围校验及明确CI接线，源bundle/业务保持P6，不得据此运行或开发P7业务；实际采用时同样列明工具hash、差异和原始CI证据供G1审查。此刻该子任务只交外部设计，不执行任何R修改。真实Windows隔离R2、正式Test、金融NONE、历史宿主及不部署边界不受此接线改变。

计划PR文档CI与实施CI分模式：P7只有设计时不增加competition业务，仅以独立PLAN_DOCUMENTS准入证明P6源bundle/核心不变和明确文档差异；实际P7实现模式须另核G1和用户实施授权。二者不得共享一个含糊PASS，旧P6历史identity/checker不因当前文档变更被抹改。具体stage gate、精确允许工具路径和证据选择见PACKAGE_GATE_AND_CI_PLAN.md。

## C-P7-003 共同准入新增接线与兼容收紧（仍待G1和用户接受）

原Task预留不能覆盖无TaskContext旧入口，必须显式增加以下范围，不用“原控制不变”掩盖缺口：新 `src/aqrp/experiments/admission.py`；原 `experiments/ledger.py`、`services/research.py`、`services/task_state.py`、`services/task_campaigns.py`、`services/task_context.py`、`services/tasks.py`，必要 `services/cli.py`拒绝显示；P7受信E2E runner的plan激活/受控launcher证据；相关实验/CLI/Task/UI/集成回归及原包身份/version/gate。其完整逐路径允许表以COMMON_BUDGET_ADMISSION_DESIGN第7节为准，与既有execution_sessions/adapter/gate/CI允许表取并集，不能扩大到P1/P3数学、P4风险或P5账本算法。

包内所有受管W入口强制共同事务准入与完整历史核验，不能让调用者选择省略receipt而走旧逻辑。旧函数/CLI签名及非受管standalone family/budget语义保留；受管W省略context/绕输出/跨plan的旧错误放行行为明确拒绝，不声称行为完全兼容。原旧P6包没有新门禁，只能在其原包/锁/独立冻结路径回归或声明重放，不承诺旧进程与新P7包并发写同W；外来写入被发现后失败关闭，不据此宣称真实ACL已验证。

“缺省字节兼容”只是在**同一新P7 bundle及同一catalog、相同输入和defaults**中，不提供execution_sessions时不注入selection或其他隐含预算字段。新bundle自身会改变catalog/Ref，不能许诺与旧P6全部raw/config_hash跨bundle相同；更不能为原地恢复关闭catalog检查。实际准入凭证/plan/claims使用单独版本化控制记录，不重写旧Task请求/已审答案/历史工件。旧包旧pin受原INT-003边界限制。
