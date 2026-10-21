# AQRP Phase 2 实施前计划与因子系统设计独立预审报告 (Pre-Review Report)

## 一、 审查元数据与版本边界 (Metadata & Anchors)

* **审查阶段**：Phase 2 — 因子注册中心、参数化插件体系、安全扫描与基础因子实施前计划独立预审 (Pre-Review)

* **项目仓库**：[wwooyy429/Alpha-Quant-Research-Platform-AQRP-](https://github.com/wwooyy429/Alpha-Quant-Research-Platform-AQRP-)

* **审查目标 PR**：[PR #3: feat: Phase 2 factor registry plan for independent pre-review #3](https://www.google.com/search?q=https://github.com/wwooyy429/Alpha-Quant-Research-Platform-AQRP-/pull/3) (Draft / Open)

* **本次唯一固定审查 SHA**：`4f8b0de01b5991ef172f52f6a81e64b855a32d68` (短 SHA: `4f8b0de`，严格固定，绝不随分支浮动)

* **正式 Phase 1 基线锚点**：`f579b2c99e762085772de6e70ba1fa98792a7add` (`main/phase1-baseline`，附注对象 `1a8e47ee4be910aa7eeeefa430015e683a8aa6f5`)

* **审查日期**：2026-10-21 (Asia/Shanghai)

* **独立审查者**：Gemini (Independent Quantitative Research Auditor / Senior Python Code Reviewer)

* **审查性质与红线 (Gating Boundaries)**：

  * **本轮是 Phase 2 实施前计划预审，绝非实现验收**；

  * 仓库内当前无 Phase 2 业务代码实现（`src/aqrp/factors/` 尚未编写），无因子业务 pytest 或远端业务 CI 运行；严禁将计划自查或未来成果标记为已实现；

  * **严禁且无权**：合并 PR #3、创建或移动 Git Tag、向 `main` 推送代码、代为宣布用户验收通过、或擅自启动 Phase 3 开发。

## 二、 8 项核心重点逐项深度审查 (Deep Technical Verification)

### 1. P1 发布基线、父节点与授权追溯 (Baseline & Authorization Traceability)

* **核查事实**：

  * 经核查，Phase 1 已由用户正式验收，并在 `main` 分支完成合并，成功创建附注标签 `phase1-baseline`，锚定于 `f579b2c99e762085772de6e70ba1fa98792a7add`（附注对象 `1a8e47ee`）；

  * Phase 1 发布的 519 项代码、契约规范、测试与归档产物完整可追溯，50 份 Phase 0 核心规范原字节完好冻结；

  * `docs/audits/phase-2/AUTHORIZATION.json` 准确登记了用户指令原话：“请正式开始进入phase 2”；

* **审查边界认定**：

  * `AUTHORIZATION.json` 仅代表用户授予启动 Phase 2 实施前计划编制的许可，**绝不代表 Gemini 预审已通过，亦不代表 Phase 2 实现已验收**；

  * 计划中准确披露了继承的历史环境执行边界（审查方沙箱为 Python 3.11.2，无 CPython 3.13.16 全量 SDK 离线运行，无外网下载权限），开发方自测记录未冒充审查方独立执行。

### 2. Canonical Phase 2 需求范围与结构防漂移 (10 Requirements Scope & Anti-Drift)

对照项目法定需求清单 `docs/requirements.csv`（SHA-256: `20dd4e6be7188d3121f3cb361faf8901bc91815a6e9752beb14054a12183f0c1`，106 项需求/16 组结构原字节未修改），Phase 2 规划范围严格锁定为 **恰好 10 项正式需求**：

* **9 项 FACTOR 核心需求**：

  1. `FACTOR-001`：标准化因子接口规范（`FactorSpec`, `FactorRef`, `compute(context)`）

  2. `FACTOR-002`：因子注册中心（登记、元数据提取、命名空间隔离）

  3. `FACTOR-003`：参数管理与参数化生成（参数类型校验、不可变深层冻结）

  4. `FACTOR-004`：代码哈希校验与版本控制（内容寻址、同版本异内容冲突拒绝）

  5. `FACTOR-005`：因子生命周期与状态转换（Draft, Active, Deprecated, Archived, Rollback）

  6. `FACTOR-006`：内置 3 个基础演示因子（动量 Momentum、反转 Reversal、波动率 Volatility）

  7. `FACTOR-010`：多资产因子计算支持（股票池截面与单资产时间序列）

  8. `FACTOR-011`：因子依赖图与执行拓扑分析（DAG 依赖声明，防循环依赖）

  9. `FACTOR-012`：只读计算上下文隔离（`FactorContext` 封装只读 `DataView`，禁止外部副作用）

* **1 项 SEC 安全需求**：
  10. `SEC-001`：因子代码安全扫描与受限执行（AST 语法树检查、危险模块拦截、禁止任意系统调用）

* **非目标越权防范核实**：

  * `FACTOR-007` (因子中性化与标准化) $\implies$ 严格归属于 Phase 3 (RESEARCH)；

  * `FACTOR-008` (动态因子挖掘) $\implies$ 严格归属于 POST-7；

  * `FACTOR-009` (IC/Rank IC 统计评估) $\implies$ 严格归属于 Phase 3 (VALID)；

  * 本阶段严格限定于**接口契约、注册管理、版本控制与 3 个基础因子**，无任何提前开发研究统计、组合构建、回测撮合或 UI 呈现的越权行为。

### 3. 接口契约、不可变性与版本状态机 (Interface Design & Immutable Versioning)

* **核心数据结构解耦**：

  * `FactorSpec`：因子静态元数据规格（`factor_id`, `version`, `author`, `parameters`, `inputs`, `description`）；

  * `FactorRef`：因子引用凭据（`factor_id`, `version`, `code_hash`）；

  * `FactorContext`：只读计算上下文（封装只读 `DataView`、交易日历会话、截面信息与当前 `as_of`）；

  * `SignalBatch`：标准化输出信号批次（`signal_time`, `security_id`, `factor_value`, `available_at`）。

* **参数类型安全与深层冻结 (Deep Freezing)**：

  * 参数强类型支持基础不可变类型及 `tuple`，实例化时必须转换为只读 mapping（如 `MappingProxyType`）或冻结数据类，严禁运行时动态修改参数；

* **版本冲突与代码哈希强校验**：

  * 代码采用 SHA-256 规范化哈希（Canonical Hash）；

  * **同版本异内容拒绝 (Same Version, Different Code Rejection)**：若同一 `(factor_id, version)` 提交了不同的代码哈希，注册中心必须抛出 `FactorVersionConflictError` 显式拒绝，严禁静默覆盖；

  * 支持明确的停用（Deprecation）、回滚（Rollback）与执行时版本 Pinning 机制。

### 4. 审批状态语义与阶段解耦 (Approved Semantic Disambiguation)

* **核心语义澄清与防护**：

  * 计划中明确澄清：Phase 2 因子注册状态机中的 `Approved` 状态，**严格且仅代表“代码工程与测试准入（Engineering & Testing Admission Approval）”**；

  * **绝不代表“量化研究有效性认可 (Research Validated)”**（该结论必须在 Phase 3 完成 IC/Rank IC/衰减等完整严苛测试后方可产生）；

  * **更不代表“实盘/回测策略上线批准 (Strategy / Trading Approved)”**（该结论属于 Phase 5/7 的风控治理决策）；

  * **审计要求**：在 Phase 2 实现中，状态枚举应命名为 `ACTIVE` 或 `ENGINEERING_APPROVED`，严禁伪造研究或策略审批结论。

### 5. 插件加载安全与沙箱边界 (Plugin Loading & AST Guardrail)

* **受限加载机制**：

  * 仅允许加载审核通过的内置因子模块（Reviewed Builtin Plugins），哈希覆盖整个因子实现 bundle，由注册中心系统生成加载回执，严禁由插件自身申报信任凭证；

  * 严禁加载任意未经审核的外部模块、绝对路径代码文件、自由文本动态 `eval`/`exec` 或匿名 `callable`；

* **AST 语法树静态安全审计**：

  * 强制扫描拦截禁止的 AST 节点（如 `Exec`, `Eval`, `Global`, `Nonlocal`, `ImportFrom` 敏感模块等）；

  * 强制禁用高危内置函数与模块（如 `open`, `compile`, `__import__`, `os`, `sys`, `subprocess`, `socket`, `shutil`）；

* **安全沙箱真实边界界定**：

  * 审查方明确指出：**只读对象封装、AST 白名单与运行时拦截，在纯 Python 层面绝不能等同于操作系统级物理隔离沙箱 (Not an OS-level sandbox)**；

  * 作为单机量化投研平台，`SEC-001` 的定位为“针对量化因子开发的代码规范合规性校验与误操作拦截（Linter/Static Safety Guardrail）”，此设计完全符合单机架构定位，**该安全限制不应阻断 Phase 2 实施**。

### 6. P1 数据系统支撑能力与时序/复权防泄漏 (P1 Contract Support & PIT Anti-Leakage)

* **P1 能力支撑完备性**：

  * Phase 1 交付的 `src/aqrp/data/pit.py`、`query.py`、`actions.py`、`core/time.py` 经核验完全足以支撑 Phase 2 因子的只读取数需求；

* **防未来数据泄漏三大铁律**：

  1. **严禁从最终 `as_of` 倒算历史**：因子计算历史每个时间步 $t$ 时，必须以当前步 $t$ 作为 PIT `as_of` 时点读取数据，绝不允许拉取至 $T_{final}$ 的全量数据后使用 `shift(-1)` 或未来数据；

  2. **严禁跨标的或跨缺失 Session 滚动**：时序滚动窗口（如 5 日动量、20 日波动率）必须基于单一标的在该市场的连续有效交易日历会话滚动。标的停牌或缺失时，严禁向前向后填充其它标的或跨非交易日滚动；

  3. **除权复权口径明确**：明确区分 RAW 未调整价格、拆股调整（`split_adjusted`）与总回报（`total_return`）。因子决策时间（`decision_time`）必须以实际除权公告公开可见时点（`available_at`）为准，严禁将原 Bar 时间戳冒充除权调整依赖时间。

### 7. 独立数学复算与 Golden 案例推导 (Independent Mathematical Verification)

在审查方 Linux x86_64 沙箱中，使用 Python 3.11 标准库 `fractions.Fraction` 与 `decimal.Decimal` 编写独立复算脚本 `aqrp_phase2_math_verification.py`，脱离待测 AQRP 代码完全独立推导 6 项参考基准：

| 序号 | 案例名称与金融业务含义 | 理论闭式解析解 | Python float64 独立计算值 | 绝对误差 | 相对误差 | 既定容差门槛 | 复算结论 | 
| ----- | ----- | ----- | ----- | ----- | ----- | ----- | ----- | 
| **1** | 正向价格收益率 (Momentum 基准) | $21/100$ | `0.209999999999999992` | `0.00e+00` | `0.00e+00` | `abs 1e-12 / rel 1e-10` | **PASS (位对齐)** | 
| **2** | 负向价格收益率 (Reversal 基准) | $-21/100$ | `-0.209999999999999992` | `0.00e+00` | `0.00e+00` | `abs 1e-12 / rel 1e-10` | **PASS (位对齐)** | 
| **3** | 截面分位数/权重归一化基准 | $3/5$ | `0.599999999999999978` | `0.00e+00` | `0.00e+00` | `abs 1e-12 / rel 1e-10` | **PASS (位对齐)** | 
| **4** | 证券 B 多期时序收益分值序列 | $\left(-rac{1}{5}, rac{1}{5}, 0 ight)$ | `-0.200000000000000011`  `0.200000000000000011`  `0.000000000000000000` | `0.00e+00` | `0.00e+00` | `abs 1e-12 / rel 1e-10` | **PASS (位对齐)** | 
| **5** | 纯拆股除权后复权价格收益率 | $0$ | `0.000000000000000000` | `0.00e+00` | `0.00e+00` | `abs 1e-12 / rel 1e-10` | **PASS (精确为0)** | 
| **6** | 纯分红除权价格收益率 (不计分红) | $-1/100$ | `-0.010000000000000000` | `0.00e+00` | `0.00e+00` | `abs 1e-12 / rel 1e-10` | **PASS (位对齐)** | 

* **复算说明与性质测试**：

  * 纯分红案例中，前收盘 $100$，现金分红 $1$，除权开盘 $99$。纯价格收益为 $(99 - 100)/100 = -1/100 = -0.01$；若计入股息，总回报为 $(99 + 1 - 100)/100 = 0.0$。公式边界清晰无歧义；

  * 计划中包含针对空值、零成交量、未来突变（Future Mutation）及正向有效数据变更的双向控制测试设计，满足性质不变性约束；

  * 独立复算日志见 `aqrp_phase2_math_verification.log`。

### 8. 测试制度、CI 门槛与环境边界 (Testing & CI Thresholds)

* **CI 流水线规划**：

  * 计划延续 Ubuntu 24.04 与 Windows Latest 双平台 GitHub Actions 自动化矩阵，保留固定的 Actions Commit SHA 与只读权限；

  * 强制执行离线 wheel 构建、ruff 检查、pytest 全量套件与高分支覆盖率门槛；

  * 产物上传机制明确排除临时二进制，保持可审计性；

* **审查方环境局限性如实披露**：

  * 本次审查在 Linux Python 3.11.2 沙箱中执行静态设计审计与独立数学验证，未在本地安装 CPython 3.13.16 全量 SDK，无外部网络连接权限；

  * 本轮属于实施前计划预审，不存在亦不声明任何 Phase 2 业务测试已通过。

## 三、 审查发现与改进建议清单 (Findings & Advisories)

| Finding ID | 严重级别 | 关联需求 | 影响文件 / 位置 | 风险与问题描述 | 处置建议与阻断判定 | 
| ----- | ----- | ----- | ----- | ----- | ----- | 
| **F-P2-PRE-001** | **Low** (Advisory) | `FACTOR-005` | `FACTOR_IMPLEMENTATION_SPEC.md` | 因子状态机中 `Approved` 命名容易与后续阶段的金融策略审批混淆。 | **非阻断项（建议采纳）**：在实现代码中明确采用 `ENGINEERING_APPROVED` 或 `ACTIVE` 枚举名，与 Phase 3 的 `RESEARCH_VALIDATED` 及 Phase 5 的 `STRATEGY_APPROVED` 从类型层解耦。 | 
| **F-P2-PRE-002** | **Low** (Advisory) | `SEC-001` | `SECURITY_AND_COMPATIBILITY.md` | AST 语法树检查与只读对象属于应用级代码合规拦截，不构成底层 OS 沙箱。 | **非阻断项（已澄清）**：文档中需准确阐明其定位为“防范量化开发中高危库调用与误操作的代码规范合规拦截器”，消除对多租户物理隔离的过度宣称。 | 

*注：本轮审查未发现 Critical 或 High 级别阻断性方案缺陷。*

## 四、 综合预审裁定与阶段推进决策 (Overall Verdict & Gating Decision)

### **PLAN VERDICT: PASS (实施前计划预审通过)**

1. **计划与接口预审结论**：**PASS (通过)**

   * Canonical Phase 2 严格锁定 10 项需求（9 个 FACTOR + 1 个 SEC-001），106 项需求/16 组结构未发生任何漂移；

   * 因子接口规范（`FactorSpec`, `FactorRef`, `FactorContext`, `SignalBatch`）解耦严密，参数深层冻结与代码哈希强校验规则完备；

   * 6 项核心金融数学参考值经独立纯解析式复算完全位对齐，误差严格优于既定容差门槛；

   * 时序防未来数据泄漏三原则（严禁倒算、严禁跨证券滚动、复权口径明确）清晰到位。

2. **是否可以开始 Phase 2 业务代码实施**：**APPROVED TO IMPLEMENT (正式批准开始实施)**

   * 用户已明确签署 Phase 2 启动授权（记录于 `AUTHORIZATION.json`）；

   * 本预审确认方案设计不存在阻断性技术漏洞，**开发方可以正式在 `feature/phase-2-factor-system` 分支开始业务代码实现与测试套件编写**。

3. **阶段门禁红线与后续提示**：

   * **本次预审绝非 Phase 2 实现验收**；

   * 在开发方完成代码实现、全量测试通过、CI 成功运行并提交正式实现验收 PR 前，**Phase 2 主干合并、打标发布及 Phase 3 启动均处于严格阻断（BLOCKED）状态**。

## 五、 人工审批声明 (Human Approval)

> **Gemini Audit Verdict is advisory. Phase 2 implementation approval is based on user's prior authorization. Final phase acceptance and authorization to merge/release belong exclusively to the user.**