# Phase 2 Factor Registry 开发计划（待 Gemini 计划预审）

状态：**启动已授权 / PLAN PRE-REVIEW REQUIRED / 业务实现尚未开始**。用户原话“请正式开始进入phase 2”见 AUTHORIZATION.json。起点为已核实 main 与 phase1-baseline 同指 f579b2c99e762085772de6e70ba1fa98792a7add；使用独立分支 feature/phase-2-factor-registry。Phase1 已验收/发布，旧审计执行边界保留；不把其独立执行补记为已完成。

## 范围与阶段依赖

本阶段严格覆盖 canonical requirements.csv 中 phase=2 的10项：FACTOR-001～006、FACTOR-010～012、SEC-001，均为 MVP。逐项来源/依赖/测试在 REQUIREMENTS_TRACEABILITY.md；106条/16组正式目录及P0契约保持原字节。ENV/QA/治理是已有能力的回归和本阶段适用支持，不新增需求条目。

交付目标为统一 Factor API、带精确版本及hash的注册/选择/停用/回滚、不可变运行参数和信号元数据、Momentum/Reversal/Volume三个基础因子、已审内置代码准入及只读输入。替换验收只要求同一DataView/配置骨架下改变精确FactorRef后接口/注册/参数/兼容性仍成立，信号按独立答案改变。

P3完整研究/样本外/统计/预处理、P4权重消费/组合风险、P5资金账户/订单/撮合/成本/回测、P6网页/CLI一致性、P7全链替换仍Planned。Price-Volume属于P3；外部任意插件/网络/OS沙箱、真实源与真实订单Unsupported；Advanced Research及Production Extensions不在范围。未实现功能不通过mock或占位返回宣称可用。

## 实施顺序（仅在 Gemini 预审 PASS 后）

1. P2.1 先封存本阶段手算输入/独立答案与兼容/安全负例；核对P1基线回归。新因子不得在独立预审前进入批准执行环境。
2. P2.2 实现最小factors/contracts与参数/版本校验，复用P1 canonical、UTC、错误基类及DataView，不重写PIT或复权数学。
3. P2.3 建立固定随库代码bundle、hash/审查回执准入与append-only Registry记录；先检查准入，再导入/实例化已知内置实现。禁止外部路径/URL/Python表达式或任意callable注册执行。
4. P2.4 通过P1 query获取单个decision_time的受限视图与可见日历；实现三个独立公式，信号和窗口严格按证券/目标session隔离。
5. P2.5 只改FactorRef的注册替换/版本/停用回滚测试、未来mutation/正向控制、参数/输出/只读/确定性/身份和失败路径测试。
6. P2.6 在Windows/Ubuntu运行完整安装wheel/静态/测试/覆盖率/秘密扫描/数据与因子smoke，留存原始产物与失败；固定实现SHA提交Gemini复核，再申请人工验收。合并/标签与P3启动分别另行授权。

## 文件与变更边界

当前计划轮只允许 docs/audits/phase-2/*、AGENTS/README/PROGRESS/ROADMAP/CHANGELOG/DECISIONS 等状态资料；不修改 src、tests、tools、CI、锁文件、P0冻结资产或P1发布原件。

预审后计划允许 src/aqrp/factors/{contracts,versions,registry,admission,input,engine,builtins}.py 与 __init__.py、SEC-001 对应 src/aqrp/core/security/最小准入子集，tests/factors/test_factor_001～006及010～012.py、tests/security/test_sec_001.py、独立tests/golden/phase2、tests/integration/Phase2；必要工具/CI/包版本0.2.0与说明。目录名是拟定位置，不是已实现文件。

Python继续精确3.13.16标准GIL/x64及既有22项锁定依赖，不增加运行库。SemVer只支持本方案的有限规范而不引入新解析框架。禁止降低P1覆盖阈值、改正确Golden答案、屏蔽失败或改写旧Gemini报告。已有VS Code两项任务固定旧74bdb92，不能把它们的结果当Phase2；P2将从新固定提交运行tools/ci.py创建干净环境并安装本次wheel。

## 验收与证据

接口、参数、registry与兼容测试逐项见 TEST_PLAN.md；数学先验见 GOLDEN_REFERENCE.md/JSON和不导入AQRP的参考脚本。关键数值与时间/准入模块拟行95%/分支90%；Registry及其余模块行90%/分支85%，关键不变量均有正负案例；不以总体覆盖替代必要负例。预审后工具显式纳入新模块，保留原门槛。

每次新run_id、不可变config、精确FactorRef/代码bundle/hash、review_ref、P1快照manifest、query/cutoff/日历/参数hash、Python/锁/OS、实际命令/退出码、原始JUnit/coverage/数值/失败清单相互追溯。不同run或快照的元数据不能错误地要求全字节一致；比较投影先声明。计划文档检查通过不等于业务测试通过，已有102项P1测试的CI也不等于P2验收。

## 审查前须明确的细化事项

1. P0 INTERFACES中的generic Approved与P3 ResearchValidated/P5 StrategyApproved需按独立域理解：P2只作审查代码在测试环境的CodeApproval；不制造研究/策略批准。回滚须已有兼容CodeApproval；是否充分符合原契约须Gemini明确确认。
2. L+1“有效session”采用保守连续可见交易日历窗口；缺session/质量不合格不跳过补齐，返回invalid。不同于按L+1条任意历史观测拼接，须审查其与P0定义一致性。
3. 可用时间采用保守decision_time（逻辑计算延迟固定0），不用P1调整后bar的原始available_at冒充全部行动依赖时间。历史逐日信号必须逐日as_of查询，不能一次最终快照倒算过去。
4. SEC-001只批准已审随库代码测试，DataView/AST/monkeypatch均不算OS安全边界；不可信代码拒绝导入、外部插件Unsupported。Gemini须评估该受限范围能否满足本阶段验收，不能声称拥有尚未实现的低权限OS隔离。

这些是待审实施细化，不在本轮静默修改P0契约。若审查判定存在破坏性变化或越界，先列影响并取得用户设计变更批准，再实施。启动授权不代替Gemini计划预审；不得重复索取已获Phase2启动许可。
