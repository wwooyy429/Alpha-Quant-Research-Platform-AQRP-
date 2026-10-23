# AQRP Phase6 G1 三项修订独立复核

固定完整 SHA：**e71f6f090b102e4abfd70a5999e495f49546a1b5**。PR #9；审查者为本会话 GPT Work 补充审核员；2026-10-23。

**结论：PLAN PASS WITH CONDITIONS（受限工程设计）。WORK-P6-G1-001／002／003 均 CLOSED_DESIGN；无新增阻断技术发现。** 条件为用户明确接受下文三项新增应用设计选择，并另行授权 P6 实施。当前实施仍 NOT AUTHORIZED / NOT STARTED。本结论不是 G2、阶段验收、合并发布或部署许可，不向后续漂移 SHA 外推。

## 版本、范围及历史证据

PR 起止读取的描述 AQRP_FIXED_REVIEW_SHA、实际 head、detached 检出均为上述完整 SHA。独立副本为 E:/WORK/AQRP-audits/p6-e71f6f0/src，无共享 alternates，工作树干净。直接父提交为上一轮已审 f7a1a68c5f747090f8c8a0e934f2fea859aec998。

P5 main / phase5-baseline / v0.5.0 peeled targets 仍为 59246f9fd391c1713b6bed65dd22280f4d248493；旧标签对象及目标未移动。P5 已验收受限发布事实保持。实际 merge 36c26911afb47ff68544e4bf64f060504dfdd94d 与获批归档头 c43b594f2f427e8a7b3614518b84aa00502365f2 整树一致，已审实现 1c5a7e62cace7c3e66b7cc7f12fd564cb0013654 为祖先。

对 P5 基线共 171 个变更文件，均限七份允许的治理状态文档和 docs/audits/phase-6；本轮相对 f7 增量 135 文件，主要是三项设计、模型及原审计归档。4738 份冻结 P5 文件逐项 SHA256 及基线 Git blob 身份匹配；src/tests/tools/.github/pyproject.toml/requirements.lock 与基线及已审 P5 业务完全一致，没有 src/aqrp/ui。106 条 canonical 目录、P6 八条逐字段快照、5 MVP/3 Competition Ready 不变。不能把全为 Planned 理解成删减交付。

13 份先前 G1 数据/锁资产（含原32组答案整个文件）逐字节对父提交核验。GOLDEN_CANDIDATES.json SHA256 仍为 efe19655aca6f47e040d21f137511b012e4b789bb4732ef114245257d23354c2。当前 phase-6 FILE_MANIFEST 的163声明文件加自身，与164个实际跟踪文件精确对账，所有大小/hash通过。

开发修订 Evidence.zip：87,180,048 字节，SHA256 **1badc883042b069dd68ceb97d286e21d152efe4c002eff45e94613b9b5970dd7**；206声明文件加manifest，CRC、唯一/精确207成员及全部大小/hash核验通过；内含 Fixed-Source.zip 的4909个跟踪文件对固定检出逐文件原字节相同。

上一轮独立 EVIDENCE.zip 的584,855,382字节及 SHA256 22cc883e7bd46f2b83ce4e5251505776862dedde3c532e15eddb5a8e07854273、105声明文件加manifest的CRC/精确106成员/全部hash重新核验；Git归档的70份接收文件与原件逐字节一致。原 BLOCKED、两条数值失败、原日志和执行身份保留，没有改写成新轮 PASS。

## 三项发现处置

| 发现／原严重度 | 本次处置 | 固定版本位置与依据 |
|---|---|---|
| WORK-P6-G1-001 High | CLOSED_DESIGN | TASK_COMPLETION_CONTRACT.md:9、15、20、24、26、34；TASK_AND_RECOVERY_CONTRACT.md:5；G2_FAULT_MATRIX.md |
| WORK-P6-G1-002 Medium | CLOSED_DESIGN | NESTED_CONTEXT_CONTRACT.md:7、11、13、15、30、34、36、38、45；DEPENDENCY_AND_COMPATIBILITY_PLAN.md:11 |
| WORK-P6-G1-003 Medium | CLOSED_DESIGN；参考算术修正已实际执行核实 | NUMERIC_REFERENCE_CONTRACT.md:5、7、9、11；reference_check.py:15、40、55；SUPPLEMENTAL_CANDIDATES.json |

001：三种固定 kind 的研究、流水线、重放阶段均已定义，真实 P5 的完整决策集合先冻结，再逐决策预分配内部 P4。完成须全部必需 slots、真实终态/manifest/金融证明/父链、全局 completion.json 和 SQLite 终态事务闭环；R 或任一 P4 成功只恢复对应 slot。SQL 前崩溃必须全量重验证，SQL 后回执损坏对外 INTEGRITY_ERROR/usable=false，不能计成功。取消意图和全局完成在同一事务序列裁决，unknown 财务状态失败关闭。没有用文件和数据库“天然原子”或任意 DAG 来替代协议。

独立核对 R 成功而 B 未开始、P4 成功而 B 失败/取消/unknown、B 声称成功却缺 P4、全部孩子成功而回执/SQL 未闭环、原源成功但本次 replay/CV 缺失，均不能 Task 成功。已提交子阶段只复用，不重做研究或退还试验；START_INTENT 后目录缺失/半初始化/部分发布进入 RECOVERY_REQUIRED。G2 已列真实断点，不再以原 G16–G19 孤立 slot 的 SUCCESS 模型证明 Task 完成。技术设计缺口已闭环；严格全链状态口径及 N>=1 仍属下文用户选择。

002：按固定源实际调用图核过 services/backtest.py:191、206、257、339、364，engine.py:321、324、327、350，provider.py:191。候选现在显式涵盖 TaskService→P5 service→Simulator 实例→内部 P4→ledger.start，两处 provider 验证同时接收 expected binding。完整19字段元组绑定 task/plan/slot/decision/time/source/adapted request/parent/UUID/root/config/code/bundle/两套锁；真实适配请求在账户投影产生后、construct 前一次性持久化。epoch 接管追加授权，旧 handle 失效。

P3 共享家族预算根与 P5 父执行根下 portfolio-runs 明确区分，不移动现有内部 P4。合法 UUID、完整 manifest 都不足以证明归属。resume 只在原 P5 严格条件下复用同一已登记/已核 P4 终态，半初始化不自动新建；replay 使用新执行 UUID、根与孩子，原 request_id 的金融确定性及原源只读保持。非金融适配表已补齐 engine/provider/服务/ledger，原来源、manifest、candidate、risk、发布字节门禁不删，旧无 context SDK 行为不变。

此为可实施的本地工程完整性设计，尚未实现真实 TaskAuthority/SQLite 并发。Python 参数/对象和同 OS 用户不构成真实隔离；没有因此关闭 Windows R2，也没有声称对象不可伪造。

003：默认 Decimal 除法/normalize/quantize 已替换为整数 coefficient/scale 和 HALF_EVEN 商余计算。主审另用 Fraction、精确 Fraction round 及独立格式化生成 expected，先算答案，再导入候选参考作为被测对象；未导入 AQRP 产品或使用未来 UI 生成答案。

两条原反例本轮重新执行旧 helper，仍分别静默舍入和 InvalidOperation；相同合法输入在新 helper 得到以下独立精确答案：

| 输入／动作 | 新结果 |
|---|---|
| 0.123456789012345678901234567890123456789 百分比除100 | 0.00123456789012345678901234567890123456789 |
| 999999999999999999999999999999.995 金额显示到分 | 1,000,000,000,000,000,000,000,000,000,000.00 |

还核正负 HALF_EVEN 奇偶临界、跨位进位、负零、极小小数、4096位有效边界、4097位与过长文本拒绝、指数/非有限/Unicode/空白/非字符串拒绝。6种 ambient Decimal 精度/陷阱设置下结果一致，不改全局 Decimal 或 int_max_str_digits。原输入/输出不经显示舍入回写。量程只限制新 P6 薄适配，不放宽旧金融校验；两条原合法反例未被新范围拒绝掩盖。raw 保留仍是未来 G2 持久化/下载要求，有限模型中的 raw_retained=true 不能当实际落盘证据。

## 需求、接口与验收可达性

| ID／等级 | 设计覆盖及实施后必须验证 |
|---|---|
| UI-001 MVP | 真实任务/因子数/最近研究回测/错误；坏回执和 manifest 不计成功；本次全 Task 屏障适用 |
| UI-002 CR | 精确 Ref/参数/选择/权重/版本比较/配置 revision 回滚；不上传任意 Python；精确转换和原始值展示 |
| UI-003 MVP | 真实 P3 研究配置、IC/Rank/ICIR/分层/衰减/OOS/NA 原因；时间/PIT/拟合隔离及家族预算不改 |
| UI-004 MVP | P3→真实内部 P4→P5 工程链，订单/Fill/逐桶资金/风险/绩效；unknown 不显示旧可信余额，正式入口后端拒绝 |
| UI-005 CR | manifest 所属/唯一成员/hash/父链核验、只读原工件、声明范围实际 replay 和独立比较；不冒称完整旧宿主 |
| UI-006 CR | CAS 默认值新 revision，rollback 也追加，只影响新请求；显示 core/UI 锁及安全日志，不操作凭证或 ACL |
| UI-007 MVP | 原 CLI、新任务 CLI、SDK、真实 Streamlit 走同一请求/内核，Momentum/Reversal 各跑完整链；金融精确投影相等，元数据差异逐项映射 |
| UI-008 MVP | 幂等键绑定 config、唯一 claim、协作取消、全阶段完成/恢复、真实日志与图表；SQLite/磁盘/并发的实际 G2 故障矩阵仍必需 |

六页面、全部8项均具接口/依赖/测试映射；CR 未被静默延期。Task kind 仍只有 research/engineering_pipeline/replay，无任意 DAG、任意插件、P7 竞争接口或新金融内核。前端不接受 root/authority/私有 FINAL_TEST/真实密钥；工件与缓存不能替代后端完整性检查。历史重放限定已登记包/锁/oldRef/投影，source 验证不等于本次执行。

G2 必须落实 G2_FAULT_MATRIX 和 TEST_AND_EVIDENCE_PLAN 的真实服务/SQLite/磁盘断点、同key10并发/epoch接管、取消竞争、跨任务/根/UUID/适配hash错误、原子金融事务/原P5反例、六页面真实浏览器、两因子三入口、完整SDK与双OS原始证据。AppTest为模拟组件检查，不能替代浏览器、权限或实盘。计划可达不等于实际实现已通过。

## 本次实际独立执行及边界

环境为 CPython3.13.16 标准 GIL x64、Windows-11-10.0.26300-SP0；解释器 C:/Users/11638/AppData/Local/AQRP/runtime/Python31316/python.exe 的 SHA256 为 31fe10b4ed82a2f960af0ef9931f46a4b84ff286f8b6ffd9dee098cf4f10f17f。没有安装 UI 扩展或启动 Streamlit/worker。

独立核验结果：

- 原32组及新增95组全部正确，新增包括完成31/绑定30/有效数值24/拒绝10；每项输入、独立答案、容差及比较在 INDEPENDENT_127_ANSWERS.json。
- 额外817条数值/拒绝输入，加原35条有效数值，共852条在6种 Decimal context/traps 下5112次观察一致。
- 3456组完整阶段子集/验证证据/封闭集合/回执/SQL屏障组合，仅全部所需条件齐备才可成功；明确以经过验证的有限模型前提为限。
- 25条额外所有权/顺序/目录/半初始化负控均拒绝；两条原数值失败先重现、后核修正。
- 上述是独立设计答案/有限模型/参考 helper 检查，数量互有重叠，**不是 P6 产品、实际并发/SQLite/authority/隔离测试数量**。

开发方模型日志的真实身份为 f7 父版本加 dirty 设计；COMMITTED_MODEL_BINDING 与每份命令的模型/输入 SHA 对本固定提交一致。没有把开发方32+95/270/35改名为独立执行，也没有补写成新 SHA 干净 SDK。主审本轮另写并实际运行的记录独立保存。

P5 发布前置证据原 ZIP 499154943字节及原合并后 SDK 115510697字节，CRC、成员/hash、环境、1158 testcase/0失败错误跳过、69个wheel模块对当前源均重新核验；它们仍是开发方历史实际回归，本轮没有重跑完整SDK。原20+4/91的前轮已核历史与字节保留，不冒充本轮新执行。

依赖方面，13份候选数据/锁资产完全不变，继承上一轮主审对固定 Streamlit1.66.1/Plotly7.1.0、Python3.13.16 的官方元数据和双OS metadata-only 解析证据。Windows51=core22+扩展29，Linux50=core21+扩展29；core requirements.lock SHA256仍为 86c7bf65c9a9690036006360062c8cd10a91279705b4070af7033d7699abffeb。**本轮没有重新解析、安装或验证UI runtime；双OS实际wheel安装/import/UI兼容 NOT VERIFIED，留待获授权实施后的 G2，不单独阻断 G1。** 不得实施时漂移版本或扩大 core wheel hash 集。

新 CI run39946297503 的官方 API 已核：Windows/Ubuntu 两 job 完成且 success，两个工件对应本 head。Ubuntu digest=4b961780a5928f1207e64ac7b8cd7ef558b5955d2f27a2853296147170e8b309，Windows digest=f67cdf6e1ec61f061ad480325dde95eb77dded8cc404323844973e8667a4348d。**本轮未下载这两份新 CI 原始 ZIP，原字节、成员/环境及测试计数 NOT VERIFIED；API success 只属继承 P5 回归，不是 P6 测试通过。** 封存时仍 running 的旧快照作为历史保留。

所有主要原始 argv/cwd/UTC/退出码/stdout/stderr 由 run_capture.py 保存（init-00至06、scope-archives、scope-archives-rerun、independent-recheck、independent-recheck-rerun、final-details、identity/status/revision-stat/core-diff/remote-final）。冻结比对用一次 ls-tree 加逐文件 SHA256/Git blob 身份，没有逐文件启动 Git。REF/完整 diff、编号源码及当前契约另保存。

审查辅助程序更正也保留原记录：首次 scope 完整4909源文件比较已通过，但报告变量被29个上下文文件名覆盖，改名后全量重跑；首次扩展 replay 生成器漏设 comparison_verified=True，却预期成功，两个模型均正确拒绝，补齐前提后3456组合通过。首次封存检查比较远端 refs 两份文本的原字节，因保存文本的CRLF与Git原stdout的LF不同而停止；尚未复制输入或建包，随后改为逐ref名称与完整SHA精确字典对账，全部一致。没有改变候选代码、正确答案或删除失败日志。一次只读查询误找不存在的 DESIGN_DECISIONS.md，实际选择在 OPEN_QUESTIONS 和新契约。详 EXECUTION_DISPOSITIONS.json。

## 条件、待用户决定与未验证

建议在用户单独实施授权中逐项明确接受：

1. **C-P6-001 严格全链成功口径**：所有必需 P4 均须真实 SUCCEEDED。合法风险拒绝保留 P4/P5 原始事实，但整个 Task 为 FAILED/REQUIRED_STAGE_REJECTED，不改风险算法、不强迫下单或收益为正。
2. **C-P6-002 新流水线 N>=1**：工程流水线完整决策集合不得为空，空区间明确 NO_REQUIRED_DECISIONS；旧 P5 合法零决策 SDK/API 不变。
3. **C-P6-003 新精确薄适配范围**：ASCII 普通有限十进制字符串最多4096数字位/4098原文字符；保留 raw/hash，超限/语法/类型明确拒绝；只显示时 HALF_EVEN，不改变 P1–P5 API 或金融域校验。

这三项方案已达到可审查的技术设计程度，主审予以有条件计划通过；**本报告不代用户批准这些选择或授权实现**。在选择确认及单独实施授权前，开发方仅可归档复核资料和保留状态；不得启动 P6 业务或 UI 安装/运行。未来若改变上述设计、锁版本或增加既有适配文件/金融语义，须列明影响并提交新固定 SHA 适用审核。

WI-R2-001/002、整体真实 Windows 隔离继续 DEFERRED / NOT VERIFIED，最终集成固定 SHA 的真实权限验证另行授权；正式 Test 未运行，金融批准 NONE；完整历史宿主仍 NOT VERIFIED，仅保持已接受 package/lock/oldRef/result replay 边界。本轮未启用账户、改真实 ACL/服务/调度、部署、实盘、运行正式 Test、授金融批准、合并、打标签或进入 P7。P6 G2/用户阶段验收及发布仍待后续。

本轮独立证据封存的大小、SHA256、完整成员清单与核验见同目录 RECEIPT.json；收据只证明字节身份，不是数字签名或阶段许可。

