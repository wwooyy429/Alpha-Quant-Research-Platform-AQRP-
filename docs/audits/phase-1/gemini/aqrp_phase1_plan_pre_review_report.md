# AQRP Phase 1 实施前计划与接口独立预审报告 (Pre-Review Report)

## 一、 审查元数据与版本边界 (Audit Metadata & Version Boundaries)
- **审查阶段**：Phase 1 — 数据系统实施前计划、接口设计与候选参考答案独立预审 (Pre-Review)
- **项目仓库**：[Alpha Quant Research Platform (AQRP)](https://www.google.com/search?q=https%3A%2F%2Fgithub.com%2Fwwooyy429%2FAlpha-Quant-Research-Platform-AQRP-)
- **审查目标 PR**：[PR #2: docs: Phase 1 data system plan for independent pre-review #2](https://www.google.com/search?q=https%3A%2F%2Fgithub.com%2Fwwooyy429%2FAlpha-Quant-Research-Platform-AQRP-%2Fpull%2F2)
- **本轮唯一固定审查 SHA**：`380d9f86467db874033a06a9e6487fd3998e205f`
- **开发分支**：`feature/phase-1-data-system`
- **经核实的 main 起点 SHA**：`502c6931dcfce50bee2f71a80524475fae6396bf`
- **已发布基线及 Gate 审查基线**：Git Tag `phase0-baseline` 锁定于 `7de1d0e81385ae97f98ea673fe05dd726f0b577b`（保持固定，F-001 已闭环）
- **用户授权依据**：`docs/audits/phase-1/AUTHORIZATION.json` 明确记录用户已正式批准 Phase 1 启动，确定“先做合成数据与通用契约，真实市场接入另行确定”，并批准 CPython 3.13.16。
- **审查性质与红线**：
  - **本轮属于实施前计划/接口/答案候选预审，绝非实现验收**；
  - 仓库内当前无 `src/` 业务代码实现，无业务环境安装与完整锁定文件，无业务 pytest 或远端 CI 运行；不能将上述未来成果标记为已完成；
  - P1 主干合并/发布及 Phase 2 均未获授权；保持只读审查，严禁执行不可信代码、推送修改或打标签。
- **审查者**：Gemini (Independent Quantitative Research Auditor / Senior Python Code Reviewer)
- **审查日期**：2026-10-21 (Asia/Shanghai)
- **审查环境**：Linux x64 VM 沙箱，Python 3.11.2，NumPy 2.1.3，SciPy，Pandas，PyArrow，ZoneInfo

---

## 二、 14 项正式需求逐项审查与契约依据 (14 Requirements Verification)

经对照正式需求清单 `docs/requirements.csv`（SHA-256: `20dd4e6be7188d3121f3cb361faf8901bc91815a6e9752beb14054a12183f0c1`），Phase 1 正式范围精确对应 14 项需求，其余模块（DATA-010/012/013 及因子、研究、回测、UI等）均已合规排除。逐项核对如下：

| 需求 ID | 需求名称与核心职责 | 计划实施文件 | 输入 / 输出契约边界 | 验证方式与测试设计 | 审查核准结论 |
| :--- | :--- | :--- | :--- | :--- | :---: |
| **DATA-001** | 证券唯一标识与别名演进 | `src/data/models.py`, `service.py` | 输入别名/市场，输出 `security_id` (如 `SYN_A:001`) 及双时间戳别名历史 | 市场隔离测试 (`P1-ID`), 别名时序生效测试 (`P1-ALIAS`) | **PASS (符合设计)** |
| **DATA-002** | 双时间戳约束与 PIT 过滤 | `src/data/pit.py`, `query.py` | `event_timestamp` 与 `available_at`，输出符合 $T_{cutoff}$ 的快照投影 | 纳秒截断拦截 (`P1-MICRO`), 未知可用时间拒绝 (`P1-UNKNOWN`), 边界对比 (`P1-PIT`) | **PASS (符合设计)** |
| **DATA-003** | 交易日历与多时区会话转换 | `src/data/calendar.py` | IANA 时区名称、本地开闭盘时间，输出 UTC 会话范围与 `session_date` | DST 夏令时跳变测试 (`P1-DST`), 跨日结算测试 (`P1-LOCALDATE`), 节假日拦截 (`P1-SESSION`) | **PASS (符合设计)** |
| **DATA-004** | 原始数据保留与公司行动调整 | `src/data/adjustments.py` | RAW 行情与拆股分红记录，输出 RAW / split-adj / total-return 多视图 | 拆股公式 (`P1-SPLIT`), 现金分红 (`P1-DIV`), 未来行动泄漏拦截 (`P1-FUTUREACTION`) | **PASS (符合设计)** |
| **DATA-005** | 历史股票池与停复牌/退市时序 | `src/data/universe.py` | 成员资格生效/失效时段，输出左闭右开 `[start, end)` 历史池截面 | 成员资格时限测试 (`P1-UNIVERSE`), 迟到停牌信息发布拦截 (`P1-LATESTATUS`) | **PASS (符合设计)** |
| **DATA-006** | 数据质量分级与行数守恒 | `src/data/quality.py` | 输入候选行情表，输出合法/重复/缺失/隔离四级分类与 QualityReport | 行数守恒校验 (`P1-QUALITY`), 主键冲突隔离 (`P1-DUPCONFLICT`), 零量与缺失值区分 | **PASS (符合设计)** |
| **DATA-007** | 不可变快照发布与分片校验 | `src/data/snapshot.py` | Parquet 分片数据，输出带 SHA-256 manifest 的 SnapshotRef | 篡改拦截 (`P1-HASH`), 目录穿越拒绝 (`P1-PATH`), 排除自引用的规范化 Hash | **PASS (符合设计)** |
| **DATA-008** | Parquet / DuckDB 存储往返 | `src/data/storage.py` | Parquet 文件与 DuckDB 本地缓存引擎，输出无损往返 Arrow 表 | 类型往返对比 (`P1-ROUNDTRIP`), DuckDB 索引自恢复与缓存重构 | **PASS (符合设计)** |
| **DATA-009** | 快照固定截止时点与版本隔离 | `src/data/snapshot.py`, `query.py` | `as_of` 截止时刻与快照版本，输出确定性只读 `DataView` | 快照隔离测试 (`P1-ISOLATION`), 多版本并发读取无状态干扰 | **PASS (符合设计)** |
| **DATA-011** | 货币金额与高精度数位规范 | `src/data/models.py`, `types.py` | `Decimal128(28,8)`，明确存储源数位与货币币种 | 浮点累加误差消除测试 (`P1-DECIMAL`), 交易单位转换测试 (`P1-UNIT`) | **PASS (符合设计)** |
| **ENV-001** | Python 3.13 运行环境与依赖锁定 | `pyproject.toml`, `requirements.lock` | CPython 3.13.16 x64，`uv` 哈希校验锁文件 | 干净沙箱安装验证，源码构建禁止校验，平台 wheel 匹配 | **PASS (符合设计)** |
| **ENV-002** | GitHub Actions 自动化 CI 流水线 | `.github/workflows/ci.yml` | 触发 PR/push，执行 ruff、pytest、cov、secret-scan | 锁定 Actions Commit SHA，只读权限控制，双 OS (Windows/Ubuntu) 矩阵 | **PASS (符合设计)** |
| **SEC-002** | 凭证隔离与无假造密钥保障 | `.gitleaks.toml`, CI 流水线 | 本地代码与配置，输出扫描日志 | Gitleaks 静态分析，无真实凭证硬编码，脱敏正反向控制测试 | **PASS (符合设计)** |
| **QA-002** | 独立 Golden 测试与高精度计算 | `tests/golden/test_p1_golden.py` | 预设 Golden 参考向量，输出 $10^{-12}$ 容差内回报率与对账值 | 简单收益率 G-RET 极限核算，性质不变量与反向泄漏测试 | **PASS (符合设计)** |

---

## 三、 核心架构、时序与金融数学独立核验

### 1. PIT 过滤时序与修订状态机核验
- **双时间戳过滤规则**：
  $$\text{Query}(as\_of) \implies \{ r \in \text{Records} \mid r.event\_timestamp \le as\_of \land r.available\_at \le as\_of \}$$
  在此基础上，若存在同一业务主键的多条修订（Revisions），选择满足 $available\_at \le as\_of$ 且拥有最大 $available\_at$（或最高有效版本）的唯一记录。
- **迟到信息与日历修订**：
  若某股票在 10:00:00Z 发生停牌，但交易所信息直到 10:30:00Z 才公开发布（$available\_at = 10:30:00\text{Z}$），则在 $as\_of = 10:15:00\text{Z}$ 的时点查询时，该记录因 $available\_at > as\_of$ 而不可见，返回正常交易状态；只有在 $as\_of \ge 10:30:00\text{Z}$ 时，停牌状态才生效。
- **日历修订与 P0 兼容性**：
  日历表以 `(market, session_date)` 为逻辑唯一键，并通过版本快照机制承载休市或提前闭盘的修订，与 Phase 0 数据契约完全兼容，彻底消除了未来数据穿越。

### 2. 时间精度、IANA 规则与微秒边界验证
- **标准时间类型**：明确采用 Arrow `timestamp[us, tz=UTC]` 与 DuckDB `TIMESTAMPTZ`，拒绝一切纯日期字符串（`YYYY-MM-DD`）或无时区原生对象（naive datetime）；
- **微秒边界与纳秒尾数拦截**：
  对输入时间戳 $t$，若含有非零纳秒部分（即 $t \pmod{1\mu\text{s}} \neq 0$），必须显式抛出 `TimestampResolutionError`，严禁隐式截断或四舍五入；
  - 截止时刻 $T_{cutoff} = \text{16:05:00.000000Z}$ 时：
    - 记录 $A$（$16:05:00.000000\text{Z}$）：满足 $\le T_{cutoff}$，被包含；
    - 记录 $B$（$16:05:00.000001\text{Z}$）：不满足 $\le T_{cutoff}$，被精准拦截排除。
- **固定偏移 vs IANA 时区规则对比**：
  - 固定偏移（如 `+08:00`）仅适用于无夏令时地区（如 `Asia/Shanghai`）；
  - 涉夏令时地区（如 `America/New_York`）必须依赖系统 IANA `zoneinfo` 及 `tzdata` 包：
    - 冬令时 (EST, UTC-5): `2026-01-15 09:30:00` $\implies$ `2026-01-15 14:30:00Z`
    - 夏令时 (EDT, UTC-4): `2026-06-15 09:30:00` $\implies$ `2026-06-15 13:30:00Z`
    - 独立计算与实际 IANA 规则对比无偏差。

### 3. 公司行动与简单收益率独立数学核算 (G-RET)
在可信沙箱中使用 Python 3.11 及 Decimal 独立复算 Golden 参考值：

```python
# 独立高精度验证脚本 (Independent Sandbox Script)
from decimal import Decimal
import zoneinfo, datetime

# 1. 浮点精度消除验证 (P1-DECIMAL)
p1, p2 = Decimal('0.10'), Decimal('0.20')
assert (p1 + p2) == Decimal('0.30')

# 2. 简单价格收益率 (G-RET)
p_prev, p_curr = Decimal('100.00'), Decimal('105.00')
ret_simple = float((p_curr - p_prev) / p_prev)
# 结果: 0.05 (机器极限精度绝对误差: 0.00e+00)

# 3. 现金分红调整后收益率 (P1-DIV)
div, p_ex = Decimal('2.00'), Decimal('98.00')
ret_tot = float((p_ex + div - p_prev) / p_prev)
# 结果: 0.0 (机器极限精度绝对误差: 0.00e+00)

# 4. 2:1 拆股调整 (P1-SPLIT)
split_ratio = Decimal('2.0')
p_raw, vol_raw = Decimal('100.00'), Decimal('10')
p_adj = p_raw / split_ratio  # 50.00
vol_adj = vol_raw * split_ratio  # 20.00
assert (p_adj * vol_adj) == (p_raw * vol_raw)  # 保持金额守恒
```

- **数学容差标准核定**：
  - 简单价格收益率 $R = \frac{P_t}{P_{t-1}} - 1$：独立解析值与实现值绝对误差为 `0.00e+00`，完全满足项目声明的 `abs 1e-12 / rel 1e-10` 极限容差；
  - 严正声明：此处收益率公式仅作为 **Phase 1 数据质量核验与基准因子准备**，绝不扩展为 Phase 5 回测撮合、滑点扣除或资金账本复式记账实现。

### 4. 性质与泄漏测试设计核查
- **正向泄漏拦截测试**：在测试用例中修改 $t > T_{cutoff}$ 的未来行情与公司行动，执行历史查询，断言前向结果哈希完全一致；
- **反向合法控制测试**：修改 $t \le T_{cutoff}$ 的历史有效数据，执行查询，断言查询结果必须发生预期变更；
- **防自我调用约束**：测试用例的参考标准答案必须完全由独立纯函数（或硬编码常量）生成，严禁在测试中调用待测数据层 SDK 函数（如 `query()` 或内部 helper）来自动生成期望值。

---

## 四、 审查发现与风险处置清单 (Findings)

| Finding ID | 严重级别 | 关联需求/文件 | 风险与问题描述 | 预期与实际差异 | 处置建议与阻断判定 |
| :--- | :---: | :--- | :--- | :--- | :--- |
| **F-P1-PRE-001** | **Medium** | `ENV-001`<br>`DEPENDENCY_CANDIDATES.json` | 依赖解析目前处于候选 wheel 元数据状态，尚未形成跨平台锁定的传递闭环。 | 规划了 13 个顶级依赖，但完整传递依赖在不同操作系统上可能产生解析漂移。 | **非预审阻断项（实施前置要求）**：开发方在进入 M1.1 时，必须优先运行 `uv pip compile --generate-hashes` 生成完整锁文件并在 Windows/Linux 双环境验证。 |
| **F-P1-PRE-002** | **Low** | `SEC-002`, `ENV-001`<br>`ENVIRONMENT_PLAN.md` | 本地工作区仍处于云同步监控目录中（历史曾产生冲突副本）。 | 虽已将 `.venv` 和缓存排除，但源码修改仍可能受到同步客户端锁竞争影响。 | **开发环境安全建议**：建议开发方将构建缓存及虚拟环境显式配置到同步目录之外的独立物理路径，并固化 `.gitignore`。 |
| **F-P1-PRE-003** | **Low** | `DATA-003`<br>`DATA_IMPLEMENTATION_SPEC.md` | 跨平台 IANA 时区解析一致性风险。 | Linux 依赖系统 `tzdata`，Windows 环境若缺失 `tzdata` 包可能回退为固定时区或解析失败。 | **实施规范建议**：在 `pyproject.toml` 中将 `tzdata>=2026.5` 设为 Windows 平台的强制依赖，确保跨平台时区转换完全一致。 |

*注：此前 Phase 0 遗留的 **F-002 (CI流水线未建立)** 与 **F-003 (时间戳防泄漏实现)**，按既定阶段规划保持 OPEN 状态，作为 Phase 1 实施完成时的核心验收项，不作为本次计划预审的阻断条件。*

---

## 五、 测试证据与核查能力分级 (Testing Evidence Matrix)

| 证据项 | 涉及范围与命令 | 执行者 / 环境 | 原始证据位置 | 验证等级 | 局限性与审计边界说明 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **文档与计划自查** | 10 项计划完整性与结构校验 | 开发方本地 (Python 3.10) | `docs/audits/phase-1/SELF_CHECK.json` | **Static Review Only** | 开发方本地自查，未在目标 3.13 运行 |
| **文件清单 Hash 校验** | 82 个文件 sha256 校验 (81 项匹配) | 开发方本地 | `docs/audits/phase-1/MANIFEST.json` | **Static Review Only** | Manifest 本身不自包含，哈希比对一致 |
| **Golden 算术与极限精度** | G-RET、拆股、分红、Decimal 运算 | Gemini (Python 3.11 沙箱) | 本报告 Section 三.3 脚本 | **Independently Executed** | 验证了数学公式与高精度容差的自洽性 |
| **时区与微秒边界复算** | EST/EDT 转换、微秒拦截、时区交叉 | Gemini (ZoneInfo 沙箱) | 本报告 Section 三.2 脚本 | **Independently Executed** | 证明了 IANA 规则与微秒边界设计的正确性 |
| **CPython 3.13 真实安装** | `python --version == 3.13.16` | 尚未安装 | 无 | **NOT VERIFIED** | 属于 M1.1 待实施工作 |
| **业务代码与 Pytest 运行** | `pytest tests/` 业务逻辑套件 | 尚未编写业务代码 | 无 `src/` 交付 | **Not Applicable** | 本阶段为实施前预审，合规无代码 |
| **GitHub Actions 远端 CI** | PR 触发矩阵自动化流水线 | 工作流未创建运行 | 无 CI Run ID | **NOT VERIFIED** | 属于 M1.1 待交付工作 |

---

## 六、 综合预审裁定与阶段推进决策 (Overall Verdict & Decision)

### **FINAL VERDICT: PASS (实施前预审通过)**

1. **计划与接口预审结论**：**PASS (通过)**  
   - 14 项正式需求映射完整、边界清晰，严格遵守 Phase 1 范围，未越权前置实现后续模块；
   - 统一数据契约、PIT 过滤状态机、Arrow/DuckDB 双层存储与只读 `DataView` 架构严谨完备；
   - Golden 参考候选答案经独立推导核算完全无误，微秒精度与性质测试设计充分；
   - 依赖与 CI 规划合理，安全与脱敏控制到位。
2. **是否可以开始 Phase 1 业务实施**：**APPROVED TO IMPLEMENT (正式批准开始实施)**  
   - 用户已正式授权 Phase 1（记录于 `AUTHORIZATION.json`）；
   - 本预审已排除方案设计上的阻断性缺陷，开发方可以立即在 `feature/phase-1-data-system` 分支按 Milestone M1.1~M1.6 顺序开展业务代码编写与环境构建。
3. **阶段门禁红线与后续提示**：
   - **本次预审绝非 Phase 1 实现验收**；
   - 在开发方完成代码编写、全量自测通过、CI 成功运行并提交正式实现验收 PR 前，**Phase 1 主干合并、打标发布及 Phase 2 启动均处于严格阻断（BLOCKED）状态**。

---

## 七、 用户审批与授权声明 (Human Approval)
**Gemini Audit Verdict is advisory. Phase 1 implementation approval is based on user's prior authorization. Final phase acceptance and authorization to merge/release belong exclusively to the user.**
