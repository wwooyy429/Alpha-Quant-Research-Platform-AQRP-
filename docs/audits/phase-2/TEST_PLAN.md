# Phase 2 自动化与独立核对计划

以下全部是预审目标，尚未执行Phase2业务测试。Golden期望来自预先封存的手算常量/有理数，不能用待验证factor函数生成；参考脚本只用标准库、不import AQRP。Gemini独立核对与开发方执行分别保留原始脚本/命令/环境/退出码，不以PASS摘要、硬编码打印或缺输入仍exit0作为完整证据。

| 组 / 对应需求 | 必要正例 | 必要负例 / 性质 |
|---|---|---|
| 元数据/参数 FACTOR-001 | 完整schema、默认值规范化、不同参数不同hash | 缺字段/错频率/bool lookback/越界/未知键/非有限值拒绝；原mapping突变不改变已pin参数 |
| Signal FACTOR-002 | 字段/唯一键/排序/有效有限值/完整血缘 | 同键冲突/错snapshot/cutoff/market/hash/乱序时点拒绝；invalid null+reason，禁止null填0 |
| Registry FACTOR-003 | 同artifact重复注册幂等、新版本并存、精确resolve、停用与显式rollback | 同ID/version异hash/spec拒绝，unknown/latest/range不支持/major不兼容/无receipt拒绝；回滚不改旧run |
| Momentum FACTOR-004 | 121/100−1=21/100、拆股中性、纯分红价格收益 | L+1边界/缺目标/缺日/多证券交错/非法价格，绝不跨证券；正比例价格缩放不改结果 |
| Reversal FACTOR-005 | 同输入−21/100，factor_direction=+1 | 不重复反号；有效窗口上R=−M，缺失reason一致 |
| Volume FACTOR-006 | 200/mean(100,150)−1=3/5 | 当前量不得进入分母；历史0/缺失/负数输入、手股/拆股量；同倍缩放不改有效比率 |
| 配置/pin FACTOR-010 | 替换/停用/rollback只影响新run，权重只保存元数据 | 未授权strategy拒绝；不得实际分配权重、创建账户/订单或更新运行中的pin |
| T-REPL-2 FACTOR-011 | 同固定view仅改Momentum精确Ref为Reversal，+0.21→−0.21 | 核心hash不变，形状/元数据仍匹配，无research/backtest导入；factor名不在data层分支 |
| 隔离 FACTOR-012 | 输入和已发布快照/hash不被合法factor修改，确定性重跑 | 修改视图副本不污染后续查询；无账户/网络入口；外部未知代码先拒绝而不是导入后拒绝 |
| 审查准入 SEC-001 | 与receipt完全匹配的reviewed builtin仅TEST_ONLY执行 | 代码/依赖bundle hash改变、伪receipt来源、未审Candidate、任意路径/factory/config表达式全部在加载前拒绝 |

T-LEAK-P2：分别改变未来event_time、晚到available_at修订、未来行动/成员/状态/日历，逐decision重查询再计算；过去逻辑数值/validity必须不变。独立正向控制修改cutoff前合法可见close或volume，应改变对应结果；不能只比较“结果相同”而没检查非常量控制。不要求不同快照ID/完整config hash或路径敏感query hash相同。

边界包括L=1/252及超界、恰好L+1/少一条、target恰好available_at/cutoff相等、未来一微秒、跨市场ID、重复证券/行、退市历史窗口、停牌空档、0当前量（历史均量>0时−1）、0历史均量（invalid）及P1已拒负价负量。手造非法输入用于测试失败，不将其绕过P1发布为合法快照。

数值容差沿用abs=1e-12/rel=1e-10；版本/参数/hash/状态/时点/整数/Decimal比较精确相等。不调宽容差迎合实现，不用被测函数产生expected。必要性质使用既有Hypothesis；保存最小失败例、seed和原日志。

数学与时间/准入关键模块行95%/分支90%，其他核心/Registry行90%/分支85%；既有P1门槛不降低，关键规则正负案例必须全覆盖。预审批准后改tools/check_coverage.py显式纳入新关键模块，不能借同名文件遗漏门槛。保持P1的102项既有测试回归，不把既有CI通过报成新增P2测试通过；P2测试数以实际JUnit为准，不预先捏造数量。

CI：继续3.13.16锁定安装、离线项目wheel构建安装、ruff/pytest/branch coverage/数学与data+factor smoke/gitleaks正负控制，两OS全部成功。实施后将workflow名称/feature分支触发纳入P2；不更换已有pin的第三方Action或依赖。原始上传策略需明确列出实际已上传文件，新增coverage原数据库、项目wheel与上传清单；scanner/bootstrap等大型第三方文件如不上传必须在清单标明，不能宣称全部本地根文件均远端可复核。旧P1未上传字节保持原事实。

实施审查包至少含：完整固定SHA与差异、10项需求真实文件/测试映射、独立Golden核对、准入审查receipt/完整bundle版本、102项P1回归与实际新增P2 JUnit、Windows/Ubuntu实际run/attempt及checkout SHA/tree、日志/coverage/快照/wheel/配置/hash、错误与不足、人工核查记录。没有原始数据、测试未运行或只能静态查看均明确NOT VERIFIED。
