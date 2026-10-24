# 范围、依赖与阶段边界

| 层级 | P7适用范围 | 当前权限/能力结论 |
|---|---|---|
| MVP | INT-003/004/005：完整工程链、状态版本隔离、干净环境/全入口/完整因子替换、文档与证据 | 全部是本阶段必需；当前仅G1设计，不用占位、空报告或Unsupported替代未来实现 |
| Competition Ready | DATA-013/INT-006：通用离线模拟适配、能力矩阵、规则校验；具体比赛映射 | 通用接口必须真实实现；具体比赛与数据源未指定属于外部待决，不能宣称真实接入或比赛认证 |
| Advanced Research | 财务扩展、机器学习、公式/自动挖掘、优化等 | 维持原POST7/Deferred，不增加本阶段业务 |
| Production Extensions | 真实账户、订单、网络连接、常驻服务、凭证/部署运维 | 无本次授权，不实现/启用/运行 |

依赖有向图：P6已发布基线 → INT-003 → INT-004 → INT-005；DATA-008 + INT-002 → INT-006 → DATA-013。原目录DATA-013依赖INT-006；适配接口说明源和规则属于互相参考，不把它写成可执行构建循环。通用规则模板先冻结并校验，再允许已验证工程源绑定；具体源与比赛规范缺失时中止具体映射，不触发下载或真实执行。

已具备的前置业务按P1–P6验收基线复用：八表/双时点/历史股票池、Registry精确引用、完整研究/统计/OOS、受限组合风险、独立事件/账本/绩效、统一Task及三入口。P7编排代码不得在adapter/UI重写收益、IC、OLS/HAC、权重、风险、撮合或资金计算。合成开盘价/容量与P1日频行情是不同输入，保留原声明和来源，不能把日收盘字段重新标为开盘可见。

当前G1只允许docs/audits/phase-7设计资料、规范状态/追踪与必要文档自查工具；不得添加src业务、pytest产品测试、新依赖、UI启动或工程worker。未来单独授权后的预期允许：competition薄适配包、integration/e2e测试、证据运行器、手册、必要服务接线；任何旧模块修复先列影响、范围及回归，不能夹带新算法。core/UI依赖锁及Python3.13.16原样固定，无新库需求。

工程运行报告须分别列 ENGINEERING_E2E、REAL_WINDOWS_ISOLATION、FORMAL_TEST、FINANCIAL_APPROVAL、HISTORICAL_HOST、SPECIFIC_COMPETITION、DEPLOYMENT，不给一个全局PASS覆盖不同边界：

- WI-R2-001/002和整体真实Windows隔离：DEFERRED / NOT VERIFIED；代码模型/CI成功不关闭。所有开发完成后锁最终40SHA，相关各阶段真实输入、侧车、目录、动态产物与全生命周期统一真实验证；具体方案、账户/ACL操作另行授权。
- 正式Test：NOT RUN；正式入口仍失败关闭，工程流程不能访问私有Test或借用其验证结果。
- 金融批准：NONE；TEST_ONLY/ENGINEERING_APPROVED制品不等于金融或正式Strategy批准。
- 历史复现：限已验证软件包、依赖锁、旧Ref、声明结果重放；缺制品或超出声明投影明确不可复现，不能说完整历史宿主已还原。
- 具体比赛/真实源：EXTERNAL_DEPENDENCY_BLOCKED；真实市场、数据许可、规则都不能凭经验填入。
- 真实部署/实盘：NOT AUTHORIZED / NOT PERFORMED；受控本地工程运行的验收另列，不冒充部署。

原R2/R3失败、SDK/CI失败、无效控制及执行勘误按原字节保留。P6通过数仅作P6前置回归；G1期间即使文档CI重跑1567项也不能写成P7实现或P7金融/隔离验证通过。
