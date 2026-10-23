# Phase5 G1 四项设计缺口独立复核

审查执行者：GPT Work / 本会话 Codex 补充审核；日期：2026-10-23，Asia/Shanghai。所有本轮独立脚本位于本报告目录，不写入业务仓库。

**固定完整 SHA：`5262032bee4f631f68763e57510e1878945f6b8c`。结论：PLAN PASS WITH CONDITIONS（受限工程设计）。**

原 WORK-P5-G1-001/002 High、003/004 Medium 四项均 **CLOSED_DESIGN — FIX VERIFIED AT G1**，未发现新增阻断性技术设计缺陷。关闭的是固定候选的设计歧义，不是未来代码或实际恢复/权限测试。事件契约细化 C-P5-001 及更新后的 P5-D01–D10 合成执行/经济/统计规则仍需用户明确接受，并单独授权实现；在此之前不得启动 P5 业务。这一条件尚未满足，不得简写为无条件 G1/阶段验收通过。

原固定 `5c9721f96679f4d495b7b3b93af3e2e31e66ae62` 的 BLOCKED 报告、原始失败与发现保持历史原文。本轮新结论仅适用于上述5262032；不补写为曾独立审查 bd18d1b。P4 已验收发布及 Windows R2 延期决定保持原有效范围。

## 固定对象、基线与范围

起止两次实际读取 PR #8 描述 AQRP_FIXED_REVIEW_SHA，均与用户指定值、PR head 相同；PR open/draft、未合并。独立 detached checkout 的 HEAD 为5262032，最终无跟踪或未跟踪改动，没有采用漂移 HEAD。起止原响应在 PR8_START.json/PR8_FINAL.json。临时 merge 元数据8407dce不是本次审查对象。

main / phase4-baseline / v0.4.0 仍同点 `32ea5d6b75c84c07017d87377eeabd2f78207c5c`，旧远端标签/引用逐项与上一轮封存表相同。相对32ea仅 AGENTS、README 与 docs 计划/状态/审计资料变动；src、tests、tools、CI、依赖锁及构建配置完全一致，没有 P5 业务实现。Python/锁包未升级，无新增依赖、DAG、任意外部插件或 P6 界面范围。

独立逐字节校验：canonical106条原目录和 P5快照一致；131个冻结输入与发布基线一致；P4严格身份中的3440个保留文件及7个冻结文件哈希一致；当前计划 FILE_MANIFEST 和 DESIGN_REVISION_IDENTITY 逐项 size/hash 一致；原 GOLDEN_CANDIDATES.json 与 reference_check.py 和旧审查5c9721f原字节相同。

保护文件 docs/REVIEW_PROTOCOL.md 已恢复到32ea原字节；bd18d1b中的前缀记录污染不再存在。首次严格检查失败日志与 PREEXISTING_REGRESSION_DISPOSITION.json 实际保留，未放宽检查或替换期望哈希。完整用户延期决定仍在 AGENTS 和独立延期档案内。这是冻结内容恢复，不是撤销延期。

## 四项发现处置

下列位置均为固定5262032源码；精确带行号原文及hash见 REVIEWED_LOCATIONS.json。开发方候选文件的旧 OPEN_PENDING_RECHECK 是交审状态，本报告作为新的独立处置，原件无需改写。

| 发现 / 原严重度 | 固定位置 | 依据与独立结果 | 本轮处置及实施后仍须验证 |
|---|---|---|---|
| WORK-P5-G1-001 / High | EVENT_TRANSACTION_ADDENDUM.md:5、:7、:9、:11、:13；CONTRACT_CHANGE_IMPACT.md:7 | 外层(time,dispatch_phase,dispatch_seq)与事务子记录(commit_seq,child_seq)分离。每个70出队后读最新提交状态，80/90不再进入外层队列；取消65、借费95和估值100有规则，迟到取消不得回插。N01–N03独立复算通过：A后E999，B候选E998、200/998>15%，故只有1次成交、容量9；预/后提交状态唯一 | CLOSED_DESIGN。用户接受C-P5-001前不得实现；G2必须实际验证队列、持久化、每个边界故障注入、崩溃恢复与幂等，不能用N03算术快照声称已做恢复测试 |
| WORK-P5-G1-002 / High | CASH_BUCKETS_AND_PROJECTION.md:3、:5、:7、:25、:27、:31、:33、:35 | C_set/U_free/U_short互斥，S_set仅为已交收现金子集。short1@100 fee1交收前后真实A均899，消除原799→899的虚假解冻。partial cover交收前A818、交收后918，增量来自已解限但到期的U_free。P4free=A−F_unused−H，H=max(V−S_set,0)仅预算保守性，不入真实Journal。N04–N11通过，并覆盖跨零、应付支付、fee/O分割 | CLOSED_DESIGN。用户需接受保守预算对可行性的影响；G2仍须真实原P4 API接线、账户桶/现金lot与原settlement绑定、双权益及风险完整对账。不得把H改称真实缺现金或拒绝全部合法short |
| WORK-P5-G1-003 / Medium | EXECUTION_PRICE_AND_FEES.md:5、:7、:9、:11 | BUY/SELL、MARKET/LIMIT统一冻结双边[L,U]，raw与实际价都受限；LIMIT买收紧上界、卖仅加下界。余单H=q×ceil_cent(max(1,Ueff×.001))覆盖整数partial最小费与舍入；累计paid+所有余单H≤F，撤单不退已付费。N12–N17通过：原有利SELL gap现在无Fill/无费用，F2不能提交最坏费3的订单 | CLOSED_DESIGN。该有限价格域会拒绝有利极端gap，须用户接受；G2必须实际边界±tick/四种side-type/GTC冻结域、全单联合预留及逐Fill故障注入，无自动扩大F |
| WORK-P5-G1-004 / Medium | FIFO_ATTRIBUTION.md:3、:5、:7、:9、:11、:13 | 每(close_fill,entry_fill)非零交集计CLOSED_FIFO_FRAGMENT。费用/借费/股息按发生时未平lots精确归属，partial消耗历史池，跨零费只分一次，pay不再次计收入。N18–N25通过：+2.5/−4.5胜率1/2、盈亏比5/9；历史A借费.08后净−.01，B保留.04；.01借费三分为各1/300不丢分 | CLOSED_DESIGN。用户需接受新统计convention，不回填旧实验。G2需真实输出/落盘/返回字节、历史lot池/多entry单close/跨零/split/undefined与独立原始事件重建 |

001的方案改变了冻结P0总序的解释，不能称原文件早已批准此含义。当前 CONTRACT_CHANGE_IMPACT 明列语义细化提案，冻结原件未动，技术上可以按该候选实施，但批准人是用户。如果实施中需要正式改P0文本/schema或兼容规则，须另列版本、迁移与批准，不能凭本报告自动修改。

002另作重要限制：P4预算E_alloc及保守H与真实账户E_total/A属于不同投影；H改变预算不等于创造真实流动性。P5每提交/实际Fill的真实资金和全风险检查不可被P4旧pass替代。该方案并未以Unsupported删去多空、交收、行动或部分成交能力。

## 十二项 canonical 需求与阶段依赖

12条=10 MVP+2 Competition Ready，原始输入/输出/依赖/等级与目录逐行一致，未删减范围。本轮全部是计划，产品状态仍 PLANNED / NOT RUN。

| 需求 | 设计/未来验证映射 | G1复核意见 |
|---|---|---|
| BT-001 MVP | 外层/子事务/Journal因果；T01/T02/T04，N01–03 | 001设计闭环；未来真实恢复、不可变trace待G2 |
| BT-002 MVP | PIT、严格未来eligible、独立open侧车；T01 | 时序/可见性规则保留，不能读当日未来整日量；未来mutation控制待实施 |
| BT-003 MVP | 完整状态、partial/cancel/expire、幂等；T02/T03/T04，N01–03/N12–17 | 风险失败从accepted/partial合法cancel，不伪造rejected；价格skip另有状态后果 |
| BT-004 MVP | 滑点/tick/费用、共享10股、限价/期限/停牌；T03/T07，N12–17 | 价格域/费界已唯一；容量与原风险不得绕过 |
| BT-005 MVP | 复式/移动均价、现金桶、原始重建；T04/T05/T11/T12，N01–25适用部分 | 账户均价与FIFO统计分层；双账/原始重建/守恒须实际实现 |
| BT-006 CR | T+1、split、ex/pay、stale/delist；T06/T07，N04–09/N22–23 | 缺规则失败而不造零价；旧股/同刻时序和修订重跑边界保持 |
| BT-007 CR | short所得、margin、borrow、股息应付；T05/T06/T07，N04–11/N19–25 | 定义内多空为必做能力；无融资/自动强平是明示合成边界 |
| BT-008 MVP | RAW mark、每日账户/风险/订单/Fill；T05/T07/T08 | 报告真实A/E及预算H/E_alloc，不能混用为实际权益 |
| BT-009 MVP | A252/ddof1/rf/TWR/MDD/换手/净成本/贡献；T08/T12，N18–25 | 原统计答案未改；新FIFO计数/收益归属闭环，实际输出待G2 |
| BT-010 MVP | 真实P1/P3/P4、仅替换精确因子配置；T09/T10 | 完整两次模拟/核心hash与预期差异、旧Ref/wheel重放仍是实现验收项 |
| QA-003 MVP | ≥10类别核心不变量、T01–T12独立参考 | 新25/209只补设计答案；必须继续真实原始账本重建、负控、覆盖率/故障测试 |
| INT-002 MVP | provider→组合/风险→订单/撮合→账户/绩效；T09/T10 | 真实九文件/父UUID+hash及P3终态接线、正式入口失败关闭必须保留 |

上游P4发布32ea为唯一已批准业务起点；PR7的R3修复在另一个分支6207450，未集成进该P4/P5分支，不能因本轮G1将它当已集成。后续若集成要固定新SHA并做适用回归。真正OS隔离/正式Test/金融批准/完整历史宿主限制没有被删除，也不要求现在提前验证已明确延期事项。

## 实际独立执行与证据

环境：CPython3.13.16，标准GIL开启，AMD64，Windows11 build26300；可执行文件、完整版本、UTC时间在 ENVIRONMENT.json。真实执行身份为本会话 GPT Work 审查方，没有Gemini、代理或开发方冒名主审。

| 本轮实际工作 | 结果/范围 |
|---|---|
| verify_scope.py，stdlib+Git | 固定/干净版本、106/12、131冻结、P4保留3440+冻结7、两套manifest、原25/70字节、旧报告原字节、旧refs、保护文件恢复：PASS |
| independent_original_math.py | 审查方原独立Fraction/整数公式重新执行；25组70项PASS，G22仅sqrt用90位Decimal且按原容差；未将旧反例机械标成新版本缺陷 |
| independent_revision_math.py | 审查方另写Cash/Lot与FIFO池模型、精确Fraction和整数舍入；新增25组209个叶断言全部PASS，容差0；未导入AQRP或开发方checker，也未用未来生产函数生成expected |
| 6组独立扩展设计检查 | 2349个模型情景：short交收/cover顺序、一般S/V投影与应付、partial费界、历史费用池、split、多entry FIFO；均PASS。这不是2349个产品测试 |
| 原开发方reference_check.py及补充checker | 作为辅助再执行；25/70、25/209均PASS。其内置“Codex developer”字段原样保留，实际本轮执行者以外层command.json为准；不是独立答案核验的替代 |
| 开发方交审Evidence.zip | 168344241bytes，SHA256 `131f02b58473c01bb96e9fb32f59965fe6d72f3a516331984b61614d9addbadc`；132声明文件+manifest、CRC/精确成员/全部size/hash通过；Fixed-Source.zip全部4052跟踪文件与固定checkout一致 |
| 原独立BLOCKED封存ZIP | 96239761bytes，SHA256 `60d16ecfe7f7663282506b9c250878c2f3d6fc61e630dbcd656a950c93855075`；与审查方原ZIP逐字节一致；245成员+manifest再核通过，Git内received的可比原件也一致 |
| 最终固定身份/差异检查 | PR锁/head未漂移，工作树干净，git diff --check通过；未创建分支/提交或写GitHub评论/审批 |
| CI状态只读核对 | run39817052064，head元数据5262032，Ubuntu/Windows两job success。名称Phase4 quality；仅现有P4回归。此轮未下载该run官方原ZIP、未核实际执行mergeSHA/JUnit/coverage，均不能称P5产品测试已通过 |

所有受控执行完整argv/cwd/UTC起止/exit保存在 `*.command.json`，原stdout/stderr同名保存。主要原始命令格式（完整绝对值在command文件中，不依赖此简写）：

```text
Python31316/python.exe -X utf8 run_capture.py scope-rerun-1 <fixed-checkout> Python31316/python.exe -X utf8 verify_scope.py
Python31316/python.exe -X utf8 run_capture.py independent-original-math <fixed-checkout> Python31316/python.exe -X utf8 independent_original_math.py
Python31316/python.exe -X utf8 run_capture.py independent-revision-math <fixed-checkout> Python31316/python.exe -X utf8 independent_revision_math.py
Python31316/python.exe -X utf8 run_capture.py final-checks <fixed-checkout> Python31316/python.exe -X utf8 final_checks.py
```

首次失败透明保留：审查方scope初稿仅允许AGENTS/docs，漏列README而断言失败，修正为允许README后全量重跑通过；这是审查脚本范围假设错误，不是开发缺陷。开发方补充checker首次执行漏传其必需外部输出路径，算术后输出参数断言失败，补参重跑通过。原checker生成的唯一untracked REFERENCE_CHECK.json已原字节移到外部工件，最终checkout干净。详 EXECUTION_DISPOSITIONS.json，未删除任何失败日志。

## 待用户决定、未验证与门禁

1. **C-P5-001需用户明确接受**：外层信封总序、70内原子80/90、提交重放key、65/95/100及同刻迟到取消规则；接受设计不等于部署。若不同意，应先修订设计再锁SHA。
2. **P5-D01–D10/C-P5-002–004合成规则需用户接受**：尤其互斥桶与P4预算H、固定双边域/有利gap拒绝、固定佣金预算及partial最小费、T+1、short/margin/borrow/红利、closed-fragment统计及精确归属。这是工程模型选择，不是现实交易/金融批准；P3旧U-002不能代为批准。
3. **实施仍未授权**：两项设计接受及明确实现授权齐全后，才可开发既定12项。完成后新的完整固定SHA交G2，不以本报告覆盖后来业务代码/依赖/契约变化。
4. **P5产品、真实崩溃恢复、真实P1/P3/P4端到端、输出/落盘/返回字节、产品覆盖率/双OS SDK：NOT IMPLEMENTED / NOT VERIFIED。** T01–T12仍是未来必须执行计划，不能用Planned/Unsupported静默删除当前承诺。
5. **WI-R2-001/002及整体真实Windows隔离：DEFERRED / NOT VERIFIED。** 用户已延期到最终集成完整SHA，账户/ACL/受管执行入口真实方案另行授权；本轮未启用账户、未查询或修改真实ACL、未运行受管入口，不因G1或CI关闭R2。
6. **正式最终Test、金融批准、完整历史宿主复现：DEFERRED / NOT VERIFIED。** 正式入口继续APPROVAL_REQUIRED、financial_approval=NONE；包/锁/旧Ref重放不能改名完整旧宿主复现。
7. 未合并、未打标签、未部署、未实盘、未进入后续阶段；没有向开发Codex或GitHub发送消息。报告与封存仅供用户审阅/转交。

本结论是固定5262032的有条件技术计划通过，不是实现通过、正式金融批准或用户阶段验收。原四项关闭理由和剩余人类批准条件分别记录，避免把“无新增技术阻断”误记成“已经允许开始业务”。
