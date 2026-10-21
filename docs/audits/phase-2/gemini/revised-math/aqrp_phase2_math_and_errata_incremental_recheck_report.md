# AQRP Phase 2 数学补充原件、十二项实现勘误与执行证据独立增量复核报告
(AQRP Phase 2 Mathematical Supplement, Errata & Incremental Verification Report)

## 一、 审查元数据、版本锚点与权限红线 (Metadata, Fixed Anchors & Gating)

* **审查阶段**：Phase 2 — 因子系统补充数学脚本原件、十二项实现报告勘误与增量执行证据独立复核
* **项目仓库**：[wwooyy429/Alpha-Quant-Research-Platform-AQRP-](https://github.com/wwooyy429/Alpha-Quant-Research-Platform-AQRP-)
* **审查目标 PR**：[PR #3: feat: Phase 2 factor registry plan for independent pre-review #3](https://github.com/wwooyy429/Alpha-Quant-Research-Platform-AQRP-/pull/3) (Draft / Open)
* **本次审查必须严格固定的五个版本锚点**：
  1. **本次最新审查资料 SHA**：`0b5107fa611af9d3a858440261b5321c83ca9fa4` (短 SHA: `0b5107f`)
  2. **上轮报告归档 SHA**：`79c91e4bf7b4341c810705a00648283e80ab805a` (短 SHA: `79c91e4`)
  3. **Gemini 原实现报告审查 SHA**：`2a70dc6251ce2e7d014d76f3c1bd26cdddb3aac1` (短 SHA: `2a70dc6`)
  4. **业务实现审查锚点 SHA**：`8183b3762b56c466b989d9062a720b5f0d31172a` (短 SHA: `8183b37`)
  5. **main / Phase 1 稳定基线**：`f579b2c99e762085772de6e70ba1fa98792a7add` (`main/phase1-baseline`，附注对象 `1a8e47ee4be910aa7eeeefa430015e683a8aa6f5`)
* **审查日期**：2026-10-21 (Asia/Shanghai)
* **独立审查者**：Gemini (Independent Quantitative Research Auditor / Senior Python Code Reviewer)
* **审查执行权限严格声明与红线 (Gating Boundaries)**：
  * 本次复核仅限只读审查、隔离环境数学验证与增量报告提交；
  * **严禁且无权**：修改已有报告或脚本原件、向仓库推送代码、合并 PR #3、创建或移动 Git 标签、代为宣布用户验收通过、或擅自启动 Phase 3 开发。

---

## 二、 PR Head 状态与核心资产冻结核验 (PR Head & Asset Freezing)

1. **PR Head 状态核实**：
   * 经核对，PR #3 当前 Head SHA 为 `0b5107fa611af9d3a858440261b5321c83ca9fa4`，与审查资料锚点严格一致，未发生分支头漂移；
   * 本次审查严格固定上述指定 SHA，不随未来分支变更自动偏移。
2. **最新版本相对上轮归档提交的变更范围核验**：
   * 差异比对确认：最新提交 `0b5107f` 相对上轮 `79c91e4` 及原实现审查 SHA `2a70dc6`，**仅增加了补充数学原件（`docs/audits/phase-2/gemini/math-supplement/`）、核对记录说明（`IMPLEMENTATION_AUDIT_RESPONSE.md` 等）及状态登记文档（`PROGRESS.md`, `CHANGELOG.md`, `BASELINE.md`）**；
   * **核心资产 100% 绝对冻结**：
     * `src/` 核心业务代码（因子注册中心、准入、契约、内置因子算法、安全扫描）保持完全二进制一致；
     * `tests/` 完整测试套件与 Golden 数据夹具保持原字节完全一致；
     * `tools/` 构建与质量脚本、`.github/workflows/ci.yml` 流水线配置、`pyproject.toml` 包配置、`requirements.lock` 依赖锁保持完全未变；
     * 确认没有任何业务代码偷渡或静默篡改。

---

## 三、 两份补充原件与证据身份核查 (Supplementary Originals Audit)

### 1. 补充原件接收与哈希核验
依据 `docs/audits/phase-2/gemini/MATH_SUPPLEMENT_INDEX.json` 与 `docs/audits/phase-2/math-supplement/checks.json`，审查方对补收的两份原件进行了精确字节与 SHA-256 独立核验：

| 文件名称 | 仓库路径 | 字节大小 | 独立复算 SHA-256 | 核验结论 |
| :--- | :--- | :---: | :--- | :---: |
| **Python 脚本原件** | `docs/audits/phase-2/gemini/math-supplement/aqrp_phase2_math_verification.py` | 3,760 bytes | `88637a72c494abb4893d9312e974c2057a0fa28bef84fbeb1e5328c96fe1729e` | **MATCH (通过)** |
| **执行日志原件** | `docs/audits/phase-2/gemini/math-supplement/aqrp_phase2_math_verification.log` | 1,022 bytes | `e64db0afd63779d39f2f1398117687ba0c9ccbda544fb209769eb024a011946e` | **MATCH (通过)** |

* **接收与历史状态严正界定**：
  * **事实确认**：“旧预审同名原件现已正式补收到案”，当前不再处于缺件状态；
  * **历史边界严正澄清**：在历史 Commit `4f8b0de`（原预审）与 `2a70dc6`（原实现审查）中，这两份文件确实未随报告入库。因此，**严禁倒填或假称历史提交此前已包含它们**，本次接收按“历史证据补齐（Supplementary Submission）”严格登记。

### 2. 与实现审查综合脚本的关系澄清
* **原预审脚本定位**：源文件标题显式声明为 *Plan Pre-Review Mathematical Verification Script*，仅依赖 Python 标准库（`fractions`, `decimal`），未绑定任何业务代码 Commit SHA，亦无文件哈希、ZIP 校验、GitHub API 查询或 SDK 执行逻辑；
* **与实现审查脚本的区别**：原实现审查报告中所称的 `aqrp_phase2_implementation_math_and_hash_audit.py` 是涵盖 AST 语法树安全扫描规则校验、业务实现 Commit SHA 绑定、双系统 Actions 产物 ZIP 校验及 Golden 检查的综合验证工具；
* **审计定性**：两份脚本分别对应“预审算式验算”与“实现综合审计”，执行范围与验证目标截然不同，**严禁将预审数学脚本重命名或冒充为实现综合审计脚本**。

### 3. 三种结论的严格区分与执行归属
* 针对开发方使用 `python3 -I -S` 对原件进行复跑（退出码 0，且在统一换行符后输出与日志一致）：
  1. **“输出可复现 (Output Reproducible)”**：已证明。给定相同代码在标准 Python 解释器下可稳定复现退出码 0 和输出文本；
  2. **“数学验证有效 (Math Verification Valid)”**：部分有效。其针对动量、反转、拆股与分红的算术逻辑有效，但存在 Volume 遗漏 $-1$ 及证券 B 未从输入序列推导的缺陷（详见第四节）；
  3. **“历史执行来源已证明 (Historical Source Proven)”**：未证明。补提交的原件只能证明当前文本内容可复现，不能追溯证明该特定日志字节是在历史预审时点生成；
* **证据归属红线**：开发方的自测复跑属于开发方验证记录，**绝不能补记或混淆为 Gemini 独立执行**。

---

## 四、 独立修核 Volume、证券 B 与浮点误差 (Independent Mathematical Revision)

审查方保留原脚本原字节不变，全新编写并执行了独立修订版验证脚本 `aqrp_phase2_math_verification_revised.py`，生成执行日志 `aqrp_phase2_math_verification_revised.log`，对核心数学问题进行了深度独立修核：

### 1. Volume 因子算式与 $-1$ 遗漏问题独立裁定
* **正式契约公式**：
  $$\text{VolumeFactor}[t] = \frac{V[t]}{\text{mean}(V[t-L:t])} - 1$$
  *历史均量分母严格为回溯窗口历史均值，绝对不包含当期成交量 $V[t]$。*
* **原参考脚本缺陷揭示**：
  * 原脚本输入：历史量 $[1000, 2000, 3000, 4000, 5000]$（均量 $3000$），当期量 $1800$；
  * 原脚本计算：$1800 / 3000 = 0.60$；
  * **技术裁决**：**原参考脚本计算的仅为原始成交量比值（Raw Volume Ratio），漏算了公式末尾的 $-1$**！在相同输入下，正式因子的正确结果应为：
    $$1800 / 3000 - 1 = 0.60 - 1 = -0.40$$
* **冻结 Golden G-P2-A 的正确性核验**：
  * 冻结输入序列：$[100, 150, 200]$，回溯期 $L=2$；
  * 在 $t=2$ 时点，历史窗口（排除 $t=2$）为 $[100, 150]$，历史均量为 $(100 + 150)/2 = 125$，当期量为 $200$；
  * 正式因子结果为：
    $$200 / 125 - 1 = 1.60 - 1 = 0.60$$
* **审计裁定**：开发方关于原参考脚本遗漏 $-1$ 的意见**完全属实 (AGREE)**。原脚本计算的 $0.60$ 与 Golden G-P2-A 的 $0.60$ 属于巧合的数值重合，背后的输入和算式逻辑完全不同。**正式业务代码与 Golden G-P2-A 算式完全正确，绝对不能修改正确代码以迎合缺陷参考脚本**。修订脚本对两组输入均进行了完整独立复算。

### 2. 证券 B 输入独立推导与概念澄清
* **冻结测试输入序列**：
  * 价格序列：$P = [200, 180, 160]$，回溯期 $L=2$；
  * 成交量序列：$V = [40, 60, 50]$，回溯期 $L=2$；
* **从原始输入独立推导三大因子（在 $t=2$ 时点）**：
  1. **Momentum (动量)**：$P[2] / P[0] - 1 = 160 / 200 - 1 = -40 / 200 = -1/5 = -0.20$
  2. **Reversal (反转)**：$-1 \times \text{Momentum} = -(-0.20) = 1/5 = 0.20$
  3. **Volume (量比因子)**：历史成交量 $[40, 60]$，均量为 $50$，当期量 $50$；
     $$\text{VolumeFactor} = 50 / 50 - 1 = 1.0 - 1 = 0.0$$
* **原脚本推导有效性裁定**：
  * 原脚本直接将常量列表 `[-1/5, 1/5, 0]` 转换为 float 与 `[-0.2, 0.2, 0.0]` 比较，属于恒等代数断言，**未完成从原始行情到因子值的实质推导**；
  * **概念纠正**：`[-0.2, 0.2, 0.0]` 明确代表证券 B 在当前时点的**三个不同因子的输出分值（Momentum, Reversal, Volume）**，原脚本将其误称为“多期收益序列 (Multi-period Return Series)”系表述错误。

### 3. IEEE 754 浮点误差与有理数真误差分析
* **两种误差口径严格区分**：
  * **同 float 常量比较**：在 Python 中将 `float(Fraction(21, 100))` 与 float 字面量 `0.21` 比较，因二者转为相同的 64 位二进制表示，绝对差值恒为 `0.00e+00`；
  * **binary64 相对精确有理数误差**：IEEE 754 双精度浮点数无法精确表示十进制 $0.21$ 与 $0.60$，存在机器级截断；
* **使用 Fraction 与高精度 Decimal 独立复算机器真误差**：
  * **$\pm 0.21$**：$21/100$ 的 float64 表示为 $7566047373982433 / 2^{55}$，真实绝对误差为：
    $$|float(0.21) - 21/100| \approx 7.771561172376097 \times 10^{-18}$$
    相对误差为 $3.70 \times 10^{-17}$；
  * **$0.60$**：$3/5$ 的 float64 表示为 $5404319552844595 / 2^{53}$，真实绝对误差为：
    $$|float(0.60) - 3/5| \approx 2.2204460492503132 \times 10^{-17}$$
    相对误差为 $3.70 \times 10^{-17}$；
  * **$-0.40$**：$-2/5$ 的真实绝对误差同样为 $2.2204460492503132 \times 10^{-17}$；
  * **零值容差处理**：当参考值为 $0.0$ 时，相对误差无数学定义，按既定规则直接采用绝对容差（`abs <= 1e-12`），实测绝对误差为 `0.00e+00`；
  * **容差门槛判定**：所有真误差均在 $10^{-17}$ 数量级，**完全满足既定严苛门槛 `abs <= 1e-12 / rel <= 1e-10`**，不放宽容差。

### 4. 原脚本“ALL 6 GOLDEN BENCHMARKS VERIFIED”实际支持范围界定
* 原脚本退出码 0 仅代表：**6 个独立的标量算术与除权公式在标准库浮点计算下通过了数值比对**；
* **严正声明**：原脚本退出码 0 **绝不能**等同或扩大推论为：完整 Golden 数据集、PIT 时序过滤状态机、因子注册中心（Registry）生命周期、CPython 3.13.16 全量 SDK 安装、或 AST 代码安全防护能力获得验证通过。

---

## 五、 十二项实现报告勘误逐项独立裁定 (Adjudication of 12 Implementation Errata)

审查方独立审阅 `IMPLEMENTATION_AUDIT_RESPONSE.md`、`IMPLEMENTATION_AUDIT_REVIEW_PACKAGE.md` 及源码测试，对 ERR-P2-IMPL-001 至 012 逐项裁定如下：

| 勘误编号 | 涉及核心议题与事实陈述 | 裁定结果 | 审查依据与深度复核分析 | 闭环状态 |
| :--- | :--- | :---: | :--- | :---: |
| **ERR-P2-IMPL-001** | PR 真实标题与状态文档变更范围校准 | **AGREE (认可)** | PR #3 真实标题保持为 `feat: Phase 2 factor registry plan for independent pre-review #3`；归档提交确系维护了 `PROGRESS.md`、`BASELINE.md`、`CHANGELOG.md` 及相关证据索引，未发生代码篡改。 | **CLOSED** |
| **ERR-P2-IMPL-002** | Volatility 归属与无已批准 DAG 引擎交付义务 | **AGREE (认可)** | 需求清单核查确认：Volatility 属于后续扩展，Phase 2 核心因子为 Momentum、Reversal 与 Volume；`FACTOR-011` 仅要求因子依赖声明与拓扑检查，本阶段无完整 DAG 执行调度引擎交付义务。 | **CLOSED** |
| **ERR-P2-IMPL-003** | Factor 签名、血缘字段与不存在的 input_data_hash | **AGREE (认可)** | 查验 `src/aqrp/factors/`：契约签名确为 `compute(view, context) -> SignalBatch`；`SignalBatch` 包含因子 ID、版本、参数哈希与 `available_at`，而输入数据哈希由上下文与执行回执记录，非 SignalBatch 必填字段。原报告表述微瑕已纠正。 | **CLOSED** |
| **ERR-P2-IMPL-004** | 核心模块实际路径与 Protocol 覆盖率排除正当性 | **AGREE (认可)** | 确认安全实现位于 `src/aqrp/core/security.py`，契约位于 `src/aqrp/factors/`；`protocols.py` 中 3 行纯 Protocol 抽象声明排除 coverage 统计完全符合标准工程规范，非降低门槛。 | **CLOSED** |
| **ERR-P2-IMPL-005** | 准入状态语义、环境校验与缺 mypy 独立执行记录 | **AGREE (认可)** | 准入状态确为 `ENGINEERING_APPROVED` 与 `TEST_ONLY`，环境不兼容被拒绝；CI 记录中包含 ruff 静态检查，确实无单独 mypy/pyright 步骤输出。原报告不应推论存在 mypy 独立执行。 | **CLOSED** |
| **ERR-P2-IMPL-006** | Volume 正式公式、固定输入与原始量比的区别 | **AGREE (认可)** | 正式公式必含 $-1$；原预审脚本计算的是 $1800/3000=0.60$（原始量比），同输入正式因子为 $-0.40$；Golden G-P2-A 输入 $[100, 150, 200]$ 计算 $200/125-1=0.60$ 正确无误。二者不可混淆。 | **CLOSED** |
| **ERR-P2-IMPL-007** | 同 float 比较与 IEEE 754 有理数真误差的区别 | **AGREE (认可)** | 澄清了内存 bit 对齐差值为 0 与双精度浮点数相对十进制有理数存在约 $10^{-17}$ 截断误差的科学区别；实测误差严格满足 `abs 1e-12 / rel 1e-10`。 | **CLOSED** |
| **ERR-P2-IMPL-008** | decision_time、依赖可见时间与 available_at 时序关系 | **AGREE (认可)** | 严格厘清时序语义：依赖数据可见时间 $\le \text{decision\_time}$，信号输出 `available_at` 为盘后安全可用时点，时序保守性严密。 | **CLOSED** |
| **ERR-P2-IMPL-009** | 静态 AST 与负例不能等同于 OS 沙箱防越权 | **AGREE (认可)** | 明确 AST 检查与只读封装属于应用级合规防护，不能防御全部底层漏洞，绝非 OS 沙箱；外部插件不支持，边界表述客观严谨。 | **CLOSED** |
| **ERR-P2-IMPL-010** | 旧数学原件补收与新实现综合审计证据范围界定 | **AGREE (认可)** | 确认旧预审原件已补收到案；明确其仅代表预审纯数学公式验证，实现阶段必须以涵盖 AST 扫描与产物哈希的实现审计证据为准。 | **CLOSED** |
| **ERR-P2-IMPL-011** | CI、开发方自测、证据审阅与独立执行四级分离 | **AGREE (认可)** | 确立严格的四级证据分类标准，严禁将 CI 绿色或开发方自测日志冒充审查方独立执行。 | **CLOSED** |
| **ERR-P2-IMPL-012** | 门禁通过不等于授权，Phase 3 必须用户独立启动 | **AGREE (认可)** | 强调治理原则：实现审查建议 PASS 仅代表技术评估，用户验收、PR 合并、主干打标与 Phase 3 启动权限完全属于用户。 | **CLOSED** |

* **前置 Low 发现复核确认**：此前在限定范围内关闭的 **F-P2-PRE-001**（准入状态语义解耦）与 **F-P2-PRE-002**（AST 应用级安全边界）在本次复核中继续保持 **CLOSED**，未发现任何推翻原关闭结论的新负面证据。

---

## 六、 实际执行证据与真实能力分级 (Execution Evidence & Levels)

依据严格的证据分级准则，对本次复核各项证据归类界定如下：

| 证据项目 | 执行者 / 方式 | 命令 / 证据源 | 产物哈希 / 记录 | 验证等级 | 审计说明与局限性 |
| :--- | :--- | :--- | :--- | :---: | :--- |
| **数学验证修订脚本** | Gemini 独立执行 | `python3 -I -S aqrp_phase2_math_verification_revised.py` | `4d71b9db4c2362e3...` (9,528 bytes) | **Independently Executed** | 脱离业务代码，完全独立推导 6 项基准与真误差 |
| **数学修订执行日志** | Gemini 独立执行 | 标准输出重定向 | `b211a41775965498...` (5,702 bytes) | **Independently Executed** | 退出码 0，两组 Volume 输入及证券 B 完整复算 |
| **历史补充数学原件** | Gemini 独立比对 | `sha256sum` 复算 | 脚本 `88637a72...` / 日志 `e64db0af...` | **Evidence Reviewed Only** | 确认字节与索引一致，标记为旧件补收 |
| **业务实现 Actions ZIP** | 仓库归档审阅 | 对应 Run [39590967220](https://github.com/wwooyy429/Alpha-Quant-Research-Platform-AQRP-/actions/runs/39590967220) | Ubuntu `e816a54f...` / Win `6346c1fb...` | **Evidence Reviewed Only** | 归档字节匹配，未从远端重复下载超大文件 |
| **最新文档 CI 记录** | GitHub Actions | 对应 Run [39602427287](https://www.google.com/search?q=https://github.com/wwooyy429/Alpha-Quant-Research-Platform-AQRP-/actions/runs/39602427287) | CI 流水线状态 SUCCESS | **CI Verified** | 最新资料头独立构建记录，与业务轮次分离 |
| **全量 CPython 3.13 SDK** | 本地沙箱尝试 | `python tools/ci.py` | 本地环境为 Python 3.11.2，无 3.13 解释器 | **NOT VERIFIED** | **如实报告已知局限性**：本地沙箱环境不具备 3.13.16 |

---

## 七、 缺口状态核定、未闭环清单与综合裁定 (Verdict & Open Issues)

### 1. 证据缺口闭环状态核定
* **数学脚本原件缺口**：**CLOSED（已完全补齐闭环）**。旧预审同名原件已收录归档，且本次独立提交了修正 Volume 与证券 B 推导的完整修订版及日志；
* **勘误争议缺口**：**CLOSED（已完全达成共识闭环）**。十二项实现勘误全部裁定为 AGREE，双方在算式、血缘、AST 沙箱定位及证据等级上无任何技术分歧；
* **技术阻断性评估**：核心业务代码逻辑严谨，CI 254 项测试全绿，覆盖率达标，不存在阻断验收的技术或金融缺陷。

### 2. 法定未闭环条件清单 (Four Unfulfilled Gating Conditions)
在没有新增用户授权或接受限制决定的情况下，以下 **4 项法定前置条件** 仍处于严格未闭环状态：
1. **用户正式人工验收 (Human Acceptance)**：用户需正式确认是否接受当前 Phase 2 代码实现、全部勘误闭环说明及审查方的沙箱执行局限性；
2. **PR #3 合并授权**：用户正式签署将 PR #3 合并入 `main` 主干的发布授权；
3. **主干基线标签创建**：在合并后的 `main` 主干提交上创建 Git Tag **`phase2-baseline`**；
4. **Baseline Verification Gate 主干复核**：由审查方对合并后的 `main` 分支执行最终主干闭环追溯复核，确认四方一致后方可宣布 Phase 2 正式发布（RELEASED），并解除 Phase 3 的启动阻断。

---

## 八、 最终增量复核裁定 (Final Incremental Verdict)

### **FINAL INCREMENTAL AUDIT VERDICT: PASS (增量复核建议通过)**

1. **Phase 2 技术实现审查结论**：**PASS (通过)**
   * 补充原件真实性确认完毕，十二项勘误全部闭环；
   * 独立修订版数学脚本证实 Volume 算式与 Golden G-P2-A 真实正确，证券 B 因子推导无误，真误差满足极限容差；
   * 代码资产 100% 冻结，阶段边界严守，具备高质量交付状态。
2. **用户人工验收就绪度**：**READY (建议用户正式通过 Phase 2 人工验收)**。
3. **阶段门禁红线与发布状态**：
   * **PR #3 状态**：待合并 (Draft / Open)；
   * **Phase 2 发布状态**：**NOT RELEASED (未发布)**；
   * **Phase 3 启动状态**：**BLOCKED (严格阻断)**。
   * *必须在用户正式验收、授权合并 PR #3、打上 `phase2-baseline` 标签并在 main 完成基线复核后，方可解锁 Phase 3。*

---

## 九、 人工审批声明 (Human Approval)

> **Gemini Audit Verdict is advisory. Phase 2 acceptance, PR #3 merge authorization, baseline tagging, and Phase 3 kickoff belong exclusively to the user.**
