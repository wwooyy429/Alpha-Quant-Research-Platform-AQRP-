# Phase 3 开发方源码审查

执行身份：Codex 开发方。此文件与 `reviewed_code.json` 是开发环境内置因子的工程准入记录，不是 GPT Work 独立实现审查、金融批准或阶段验收。G1 通过及用户实施授权见 IMPLEMENTATION_AUTHORIZATION.json；本轮限26项、23MVP/3 Competition Ready。

审查覆盖整个 `src/aqrp/**/*.py`（包含新增研究、验证、实验和服务模块），新 bundle 由包内实际文件路径/字节、原依赖锁及API/契约版本计算，最终数值见 IMPLEMENTATION_IDENTITY.json。最终提交前重新核对 bundle 与 receipt；后续任何源码改变必须重新审查，旧0.2 receipt/wheel/原审计不移动或重签。

已逐项检查的约束：

- 固定内置 allowlist 增加 price_volume，输入 close+volume；当前新 Ref 默认1.1.0，原三因子公式/DTO兼容范围保留。精确原1.0.0 Ref由原0.2 wheel及独立旧venv执行，不以新hash替换旧制品。Registry仍只有工程状态，不授权任意插件/执行字符串。
- 新服务只调用 P1 快照验证、历史股票池与 FactorEngine；行业/市值/命名风险暴露为独立 Parquet 侧车，parent/币种/身份/hash强绑定，不扩充P1八表。可见性先于最新修订，旧冲突被后来唯一修订修复时不能提前拒绝；最新仍冲突则失败。
- 时序算子使用完整预定session网格，不删缺失压缩窗口；条件为封闭比较白名单。五stage各有工件、计数、fit_scope/hash/输入引用及无效原因；未启用为SKIPPED。中性化是当时截面行业虚拟变量+log正市值OLS，记录秩亏/排除项，不能复制原值。
- 行动标签遵守(entry,exit]、同刻先拆股后分红、PER_OLD_SHARE日锚点、应收且不再投资。标签使用完整日bar的event/available，coverage修订和逐日独立水位分开；历史拟合只接受当时已可用标签，purge为闭区间信息接触，walk-forward保护先前held-out并计其embargo；最终Test不得进入fit。
- 合成只用预先指定权重/方向和共同交集重新样本z；相关与冗余只诊断，不自动调权/写账户。每个因子/参数候选、合成候选与每个预测期限均计入预注册family，失败/缺结果仍保留m，不只检验赢家。
- HAC实际算术与正式资格分开；增长带宽整数根规则、完整冻结网格、模型/证明/主审方法记录/用户协议及样本门槛均受检。工程近似p不得自动进入正式批准。Holm/BY及需前置依赖依据的BH保留原始null失败槽位。
- 每次运行 UUID、实际环境包版本/RECORD元数据及解释器hash、完整配置、版本/seed/成本不适用说明、开始/终态/错误事件和工件hash；缓存包含全配置与权限域，命中时保留原计算的原始config/signals与origin_run_id。RECORD摘要不是依赖全部文件字节证明；干净SDK另保存安装wheel hash。
- TestEvaluator在私有数据加载前检查实际SID/UID、非提权token、owner/mode/DACL、链接/硬链接、管理员封存授权、部署证据及runtime工件。原子RESERVED先于执行，失败/断进程不返预算，私有根的统一控制索引不能因结果目录/family/run改名重置。研究端不接收Test标签/统计/错误细节。
- OS权限验证代码存在；本轮没有账户、ACL、服务、调度配置变更，也没有真实独立Test环境。单用户/模拟权限单测只证明代码路径，不证明部署。正式入口缺可核实部署即拒绝；不将此拒绝处理冒充金融通过。
- 预定标准、冻结时间、候选/期限身份、实际验证及独立证据不足则拒绝审批；人类决策必须签封且匹配终态运行中已有proposal，再追加到独立决策链，不能改写运行或升级为策略批准。
- CLI为同一研究服务的JSON入口。HTML转义所有报告字符串。没有eval、自定义模块/工厂、pickle、任意子进程命令或真实交易接入。旧环境子进程为固定审查过的脚本，`-I`、清理凭据/Python配置、独立cwd及严格原制品字节核对；它不是恶意插件沙箱。

新增测试及清洁SDK检查结果以 IMPLEMENTATION_VALIDATION.json、原始JUnit/coverage/log及Actions ZIP为准。开发迭代失败全部单列留存，不删除失败用例或修改金融正确答案迎合实现。固定SHA实现审核仍交GPT Work，不能引用本文件作为独立PASS。

追加源码复查发现并修复四主体约束遗漏：强制research/evaluator/auditor/owner互异、授权签封绑定主体；auditor对数据及制品只读且不能读operator key。POSIX对未经解析的扩展/default ACL拒绝，防止只检查mode而漏掉额外授权；本轮不创建或修改ACL。详implementation/ROLE_REVIEW_RESPONSE.md。该修复重新生成整个包receipt，不把前一实现的成功SDK/CI外推为新bundle验证。


2026-10-22 G2修复全bundle重审：3项代码变化和直接调用者已核，详情g2-5a5e093/DEVELOPER_RESPONSE.md。原45模块其余字节连续性保持，工程receipt重签仅TEST_ONLY/NONE；不是GPT Work独立复核或金融批准。
