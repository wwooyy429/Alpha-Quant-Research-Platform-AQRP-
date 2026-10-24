# P7 设计测试矩阵与原始证据计划

当前仅G1，无P7业务实现、测试通过、真实浏览器或部署结论。P6固定3017的独立/双OS各1567只属于既有前置范围；归档/发布回归也不能算P7能力验证。实现后必须运行以下矩阵，开发方必要自测与GPT Work独立固定SHA审核分开记录。

| 测试组 | 正例 / 独立期望来源 | 必需负例和边界 | 原需求 |
|---|---|---|---|
| T7-REPLACE | 固定P1/侧车/精确Ref，Momentum与Reversal分别完整研究→组合风险→订单撮合→资金/绩效→报告→Task；逐阶段原始工件独立读取，透明层字面答案+主层独立参考 | 仅改显示名而未改代码Ref；同UUID换父源；不同core/数据/风险偷偷夹带；某子阶段缺失但整任务成功；订单未变化却不按预期解释 | INT-005 |
| T7-ADMISSION | Task/旧CLI/公共research/direct ledger同域共同原子准入；32+候选与原审反例；同key去重、N单位完整预留、可信R认领、不退款、恢复/历史清单 | 12取消后旧入口拒绝；剩余1混合并发；输出/上下文/家族绕过；DB/投影缺损；UI随机key/旧CLI slot去重；原失败完整保留 | INT-003/004/005 + EXP/UI-007 |
| T7-BROWSER-NEGATIVE | 原风险夹具真实UI提交gross_max=0；主根排队replay由UI取消及正常UI重放，逐案例原字节 | 不能用预算拒绝冒充P4拒绝；risk第二attempt拒绝；worker不得在取消前偷跑；source不变，零研究必须真实无R | INT-004/005 + UI-007/008 |
| T7-MODES | 研究候选参数/受审版本/停用回滚变更，固定工程strategy pin与历史快照不变；新candidate结果应受已知变更影响（反向控制） | 自动latest升级、改旧config或历史manifest；新family/新adapter绕共享12预算；失败/取消退款；未审任意代码执行；formal/FINAL_TEST改字段强行通过 | INT-003 |
| T7-CLEAN | 全新源checkout→3.13.16→固定hash依赖→build/install wheel→数据→全部测试→CLI研究/回测→真实网页→数值→日志，实际路径/RECORD/环境 | editable包、脏tree、假Python版本、lock/RECORD篡改、host/OS/machine缺失、复用旧site-packages、只起UI无任务/对比 | INT-004 |
| T7-PARITY | 旧研究CLI/旧回测CLI/TaskCLI/SDK/AppTest/真实浏览器按同canonical请求，同核原字节投影与来源证明 | 过宽排除hash/lineage/null；精确资金被显示舍入覆盖；旧defaults影响既有请求；相同错误输入入口不一致拒绝 | INT-004/005 |
| T7-LEAK | 已可见/未来event/未来available/历史主档修订/行动/股票池/暴露/coverage/标签/fitting cutoff逐一mutation；先冻结过去投影再比较 | 未来信息提前可见、缓存键不含PIT/Ref/池、行内信号available早于依赖、标签训练边界漏主档；改变已可见依赖需有非恒定反向控制 | INT-003/005 + DATA/VALID |
| T7-LEDGER | 独立读取所有提交事务/链/清单，逐现金桶+short backing+position+journal+fees+equity重建，原P5答案与G2反例全回归 | 提交后cancel/exception回退旧余额；可抵消桶错误；两个short字段同错；损坏事务仍known/CANCELLED；原R2对象枚举/缺清单作为代码回归而非真ACL通过 | INT-004/005 + QA-003 |
| T7-TASK | 原3kind完整completion屏障/所有P4成功、可信TaskContext/原子claim/实际目录绑定/恢复/重放、10进程同key、真实崩溃与WAL准入 | orphan child/全子成功无completion、合法风险拒绝被计成功、半初始化重复执行、提交后映射缺失、错误所有权/目录/parent；固定原生错误控制不改判任意退出码为预期崩溃 | INT-003/004/005 |
| T7-EXEC-SELECTION | 原P3完整19点/统计/报告，预冻结隔日10执行点→真实B10/P4十slot/源时点hash；旧缺省行为/字节回归 | 动态按风险/收益跳日；删required slot、合法但错误时点、乱序/重复/零点/越界、恢复时重新挑点、P3被悄悄裁成10点、旧请求自动添加新字段 | INT-003/004/005 + UI-007/008 |
| T7-ADAPTER | 已审合成profile/原始8表及manifest/侧车、精确标准请求、能力矩阵、原服务真实运行与结果绑定 | 缺规则/冲突/不支持/未知比赛/真实provider一律明确拒绝；无license声明/时区/单位/available_at/历史池；输入hash或source错；不可静默猜T+1、税、borrow或currency | DATA-013/INT-006 |
| T7-BOUNDARY | 原formal/Test失败关闭、无网络/实盘/账户/ACL/服务变更；证据审计确认scope | 页面/CLI/SDK改profile布尔、非法路径/任意代码/真实连接字段、外部provider偷偷下载；不把工程结果当金融批准 | 全部 + GOV/QA |
| T7-OPS | 手册逐步命令与版本/目录/数据/运行/失败/恢复/下载/校验/停止，以及真实部署未授权的明确边界 | 文档命令未运行却称部署成功；缺运行前提/身份；清理失败证据；旧标签移动或默认branch漂移 | INT-004 + GOV |
| T7-PACKAGE | P7分模式准入、P6原checker在旧源码/旧wheel环境实际执行、原5016/新G1答案保护、新bundle与安装模块、真实阶段CI命令/完整选集 | 删除旧禁止competition检查、沿用旧83约束或旧receipt批准新包、漏列新增源码、忽略额外Git差异、P7输出未上传、整段省略旧测试却报complete | INT-004/005 + ENV/QA |

所有关键金融/时间/权限边界必须有已知答案、边界、性质、独立参考及错误注入；正确预期不能来自待测函数。覆盖率沿现行分类和门槛，不降低旧文件标准；纯adapter若包裹状态/金融逻辑必须按更严格类别，关键用户路径100%有用例。无有据规模/硬件目标不虚构性能SLA；记录实际资源/耗时，可重现并发案例不能省略。

独立答案冻结：本目录GOLDEN_CANDIDATES.json有限手算候选经G1主审核对后，实施前冻结版本/sha256、推导、容差、适用profile。主层中性化、多决策/交收/回测系列引用原独立Golden并增加不导入产品的独立参考，保留参考源码和原始输出；不能从产品首次结果拷贝expected。若新增候选发现规范冲突先重新审核设计，保持已审旧答案原字节。

完整SDK与双OS：必须在同一40位候选上构建安装wheel，运行全部原单元/金融/集成/属性/故障/回归，以及新P7用例和可实际运行的旧20+4/91、旧Ref/软件包声明重放。记录实际通过/失败/跳过数而非预定数量，所有关键失败阻断。保留源码archive、构建wheel、实际installed distribution+RECORD、core/UI锁和所有轮子、解释器/OS/machine/环境、开始结束UTC、argv/cwd/stdout/stderr/退出码/JUnit/coverage及上传选择器清单。

官方Actions证据须关联run_id/attempt/job/head_sha与平台，下载原ZIP及原日志，保存API artifact ID/size/digest、实际长度/SHA256、CRC/精确成员、每个声明成员实际hash。上传工具对pytest-current等别名复制的子树必须全量字节对账，不把复制品说成原symlink/ACL。失败attempt不可被retry新包覆盖；runner故障原因无法证明时明确NOT VERIFIED，不能靠猜测免除代码缺陷。

新的P7工具/CI/工件选择接线按PACKAGE_GATE_AND_CI_PLAN执行：当前P7树用新阶段准入，旧P6 checker原字节仅用于其固定基线包/源码；原P6全部业务回归与正确答案仍保留。e2e/competition新输出同时进入tools/ci上传选择器和workflow原包路径，并纳入exact-member/whole-subtree字节审计。阶段文档模式成功只证明P6回归和允许文档范围，不称P7实现通过。

真实浏览器实施后必须按 [BROWSER_NEGATIVE_PROTOCOL.md](BROWSER_NEGATIVE_PROTOCOL.md) 与结构化CANDIDATES逐案执行，不再把负例留到主12耗尽后临时安排。MAIN-12原actor/原答案不变；原P6风险故障夹具在任何结果前单独冻结根/来源/purpose/1-slot，使用现有Risk overrides真实提交gross_max=0，需R成功、真实P4 REJECTED/FAILED、B成功无fills现金1000、整Task FAILED REQUIRED_STAGE_REJECTED。负例消耗1独立故障单位，明确分列，不声称主预算只有12却暗中执行13次研究，不用于补主成功数或金融推断。

主根取消案例由可信SDK仅排队固定源的replay，再真实浏览器点击Cancel safely；无新研究/无新R、P4、B或E，之后真实worker no-op及同key重试证明。正常重放由真实UI按钮提交，零新研究但会有新E及P4执行，必须正确记录。主成功actor不能用replay替代。记录六页面/两因子/股票池/campaign/风险/取消/replay/下载/比较/defaults CAS与回滚、AX/截图、进程/URL/解释器/Task及run身份；AppTest/SDK准备步骤不得冒充browser提交。所有主体与工件前后hash、原账本及审计清单保留，只停止本次自有进程。

最终证据清单为不可变配置、数据/代码/环境/规则/旧制品/输入/输出/失败原件的大小与SHA256；清单自身/外层ZIP/外部seal边界明确，避免循环hash。独立主审可读取所有工程输入和原始工件；真实ACL验证另授权且R2延期未关闭。最终工程报告列每项需求/测试/缺口/实际命令、四种关卡状态，不能将设计/代码自查/CI/独立审查/用户验收混成一个PASS。
