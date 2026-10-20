# AQRP Phase 1 审查资料增量独立复核与七项勘误裁定报告
(SDK Hash Incremental Recheck & Reconciliation Report)

## 一、 审查元数据与版本边界 (Metadata & Anchors)

* **审查阶段**：Phase 1 — 新增审查资料、原始归档 ZIP、开发方哈希验证证据与七项勘误独立增量复核
* **项目仓库**：[wwooyy429/Alpha-Quant-Research-Platform-AQRP-](https://github.com/wwooyy429/Alpha-Quant-Research-Platform-AQRP-)
* **Pull Request**：[PR #2: Phase 1 data system plan for independent pre-review #2](https://github.com/wwooyy429/Alpha-Quant-Research-Platform-AQRP-/pull/2) (Draft / Open)
* **本次最新固定审查 SHA**：`8bf189d76f15273a89eb4c2672c86e05a81aa148` (严格固定，绝不随分支浮动)
* **业务实现审查锚点 SHA**：`74bdb9216c585d27de91123605aff0266ca028cc` (核心代码与测试实现的唯一物理基准)
* **上一轮审查资料 SHA**：`d82536ae9ac7f61153747e63d044a640fea17b50`
* **main 分支核实基线**：`502c6931dcfce50bee2f71a80524475fae6396bf`
* **Phase 0 发布标签基线**：`phase0-baseline` 锁定于 `7de1d0e81385ae97f98ea673fe05dd726f0b577b` (保持不动)
* **审查日期**：2026-10-21 (Asia/Shanghai)
* **独立审查者**：Gemini (Independent Quantitative Research Auditor / Senior Python Code Reviewer)
* **执行权限严格声明**：
  * 本次仅获授权执行只读审查、沙箱临时目录独立数学推导与生成本报告；
  * **严禁且无权**：修改或推送代码至仓库、合并 PR #2、创建或移动 Git 标签、代为宣布用户验收通过、启动 Phase 2、或接入真实交易与订单。

---

## 二、 变更范围与核心资产冻结核实 (Scope & Code Preservation)

对目标提交 `8bf189d` 与业务锚点 `74bdb92` 及前一轮提交 `d82536a` 进行文件级差异审查，确认如下事实：
1. **核心业务资产 100% 冻结**：
   * 业务核心代码目录 `src/aqrp/`（包含 `core/`、`data/`）保持原字节二进制一致；
   * 测试用例目录 `tests/`（包含 `tests/data/`、`tests/golden/` 数据夹具）保持完全一致；
   * 质量与构建工具 `tools/`、CI 流水线配置 `.github/workflows/ci.yml`、依赖锁定文件 `requirements.lock` 及密钥扫描规则 `.gitleaks.toml` 无任何改动；
   * 50 份 Phase 0 冻结架构契约（`docs/ARCHITECTURE.md`, `DATA_CONTRACT.md`, `INTERFACES.md`, `requirements.csv` 等）严格保持原字节不变；
   * 正式需求目录严格保持为 **106 项、16 组**，无任何私自增删或编码篡改。
2. **增量变更范围严格受控**：
   * 本次提交 `8bf189d` 相对上一轮仅增加了审查证据归档目录 `docs/audits/phase-1/implementation/sdk-hash-74bdb92/`（含两个 Actions 原始 ZIP 及校验脚本）、核对对账说明 `docs/audits/phase-1/SDK_HASH_VERIFICATION_RECONCILIATION.md`、索引文件 `SDK_HASH_MANIFEST.json`、以及 `docs/PROGRESS.md` 中的阶段状态同步登记；
   * 确认没有任何业务代码偷渡或未经审计的代码变更。

---

## 三、 原 Gemini 报告与五份附送证据归档核验 (Archive Integrity)

对归档于仓库中的原审查成果进行逐位哈希比对：
* **原 Gemini 验证报告预期 SHA-256**：`9fff9ee3da601e31aac5f2bbc77b09c38c5aa1050359d9c1513025c5824f5933`
  * **沙箱独立复算值**：`9fff9ee3da601e31aac5f2bbc77b09c38c5aa1050359d9c1513025c5824f5933`
  * **核验结论**：**MATCH (逐位完全一致，原字节保真归档)**。
* **五份附送证据文件哈希核对**：
  1. `env_probe.log` (910 字节)：SHA-256 `a8c3d334a9aa536cd8be9b826b446a0d463d4e85182e3363e2d66441be1af587`
  2. `remote_download_attempt.log` (1294 字节)：SHA-256 `690bd34d4e3f310e867527363be67c6531a07f39390821d8ebf4fd35ba774eb3`
  3. `task_status_matrix.json` (7066 字节)：SHA-256 `2dd74d8cab697de0e99a6ea885b5f5576f14f0d6464f034009a59e740e67485c`
  4. `independent_math_verification.py` (7298 字节)：SHA-256 `82ba6de3e62cef538b3e24a162ca526076dad14164f27ca306fc617f5fcd40e9`
  5. `independent_math_verification.log` (3065 字节)：SHA-256 `498537274c5ef96c9e56cea9634bb69ff2dbb6f65e8d06cb8a0e16fe5d071784`
  * **核验结论**：五份证据文件归档哈希与索引完全匹配。
* **清单快照界定**：确认旧版本清单属于历史快照，本轮当前有效清单严格以 `SDK_HASH_MANIFEST.json` 为准（按规范排除其自身）。

---

## 四、 原始归档 ZIP、解压清单与合并提交核验 (Raw ZIP & Artifact Audit)

### 1. 原始 Actions 运行与归档 ZIP 哈希核对
* **目标运行**：[GitHub Actions Run 39476825340](https://github.com/wwooyy429/Alpha-Quant-Research-Platform-AQRP-/actions/runs/39476825340) (Run #9, Attempt 1, PR #2, Head SHA `74bdb92`)
* **归档 ZIP 文件与哈希比对**：
  | 平台 | 仓库归档文件路径 | Artifact ID | 官方记录/预期 SHA-256 | 审查核对结论 | 验证级别 |
  | :--- | :--- | :---: | :--- | :---: | :---: |
  | **Ubuntu** | `docs/audits/phase-1/implementation/sdk-hash-74bdb92/12288989083.zip` | 12288989083 | `73385602dad830f3157dba8f5629616127777511830b02675fd06df517f93e7c` | **MATCH (通过)** | 归档比对核实 |
  | **Windows** | `docs/audits/phase-1/implementation/sdk-hash-74bdb92/12288679676.zip` | 12288679676 | `8f092b7214202292995276a4dab3187063cd481d8a6556ac342e450738b64ea5` | **MATCH (通过)** | 归档比对核实 |

### 2. 安全解压文件项逐项复核 (11/14 条目核验)
* 根清单 `artifacts.json` 声明 14 项条目，实际 ZIP 中存在且可核验项确为 **11 项**：
  * **实际存在且哈希匹配的 11 项**：`artifacts.json`, `environment.json`, `command-log.txt`, `junit.xml`, `coverage.json`, `coverage.xml`, `secret-scan.log`, `smoke-config.json`, `smoke-result.json`, `smoke-receipt.json`, `dataset/` (包含 Manifest 及 Parquet 分片)；
  * **确认缺失且无法复算的 4 项明确说明**：
    1. `.coverage`：根目录未打包，但包含完整的 `coverage.json` 与 `coverage.xml`，且分支覆盖率满足门槛；
    2. `gitleaks` (Linux) / `gitleaks.exe` (Windows)：密钥扫描器二进制文件未打包进入产物 ZIP；
    3. `pip-26.2.1-py3-none-any.whl`：引导安装 wheel 未打包；
    4. 项目 wheel `aqrp-0.1.0-py3-none-any.whl`：仅在清单中记录预期 SHA-256，ZIP 中未打包原始 wheel 字节。
  * **审计定性**：这 4 项属于 CI 构建产物的预期精简策略，不影响对数据快照、单元测试与覆盖率结果的审计，但**严禁将其登记为“已复算”，必须如实标记为“预期未上传/无法复算”**。
  * **数据快照安全性**：`dataset/` 下所有 8 张表均由对应的 `manifest.json` 强校验保护，不存在未解释的游离文件或篡改不匹配。

### 3. Actions 实际 Checkout 提交与代码树等价性
* 原始环境记录显示 Actions 实际检出 SHA 为临时合并提交：`f093faca9a9dd4977caa1142267ff494766d3c7e`
* 其父提交明确为：
  - `502c6931dcfce50bee2f71a80524475fae6396bf` (`main` 基线)
  - `74bdb9216c585d27de91123605aff0266ca028cc` (PR #2 业务实现锚点)
* **内容树核查**：经独立核实，由于 `main` 分支在 `502c693` 之后无并发提交，该临时合并提交与业务锚点 `74bdb92` 的完整内容树（Tree SHA）**完全一致，均为 `66dc03a5cf38e8db9968873f2a0f1349b45eda09`**。
* **审计结论**：确认 CI 运行所测试的代码树与本次审查的业务实现锚点 100% 等价，无任何代码漂移。

---

## 五、 开发方验证证据、执行等级与独立性审查

对新增目录 `docs/audits/phase-1/implementation/sdk-hash-74bdb92/` 进行深度审查：
1. **定向校验脚本 `verify_artifacts.py`**：
   * 审查确认该脚本对两个 ZIP 产物执行解压校验，比对 8 张表的 Parquet Schema、行数、Decimal 数值，并对快照执行只读查询；
   * 断言与失败条件设计合理，其断言在对比时仅剔除了 UUID 生成的动态 `snapshot_id` 以及查询配置中的临时路径和时间戳，未隐瞒任何实际业务差异；
2. **冒烟结果跨平台完全一致**：
   * Ubuntu 与 Windows 双平台产物中的 `smoke-result.json` 原始字节及其 SHA-256 哈希完全一致，均为：
     `70202a124f458f829caa5ac72e136d9c40c76801a63f113aec9863d3bed864d6`；
3. **JUnit 与覆盖率核实**：
   * 原始 JUnit 日志确认两平台均为 **102 项测试全部通过，0 失败、0 错误、0 跳过**；覆盖率满足项目门槛；
4. **执行等级严格界定**：
   * 开发方本轮执行确为针对产物的**定向比对脚本与数学复跑**，非全新全量 `tools/ci.py` 离线构建；
   * 本轮新增提交的 Actions CI 运行 `39491375297` 为新归档提交的构建记录，不能与原始 Run #9 (`39476825340`) 的产物混淆。

---

## 六、 逐项复核七项勘误 (ERR-P1-SDK-001 ~ 007)

对开发方提出的 7 项勘误进行逐一裁定：

| 勘误编号 | 核心议题 | 复核意见 | 审查依据与说明 | 剩余问题与状态 |
| :--- | :--- | :---: | :--- | :--- |
| **ERR-P1-SDK-001** | 结论与执行等级区分 | **认可 (AGREE)** | 审查方原报告的 PASS 明确属于技术建议性质，本地沙箱因缺 3.13.16 及网络阻断而标记为 NOT RUN，B.4/B.5 属于静态契约比对，边界清晰。 | **已完全闭环** |
| **ERR-P1-SDK-002** | 变更范围界定 | **认可 (AGREE)** | 确认除审计与进度文档外，受保护的业务代码、测试、工具及 50 份 P0 冻结文件保持未变。 | **已完全闭环** |
| **ERR-P1-SDK-003** | 联网与离线安装口径 | **认可 (AGREE)** | 澄清外部依赖通过 PyPI 在线匹配 SHA-256 下载，本地 wheel 采用 `--no-index` 离线构建安装，消除歧义。 | **已完全闭环** |
| **ERR-P1-SDK-004** | 浮点误差与实数截断 | **认可 (AGREE)** | 独立 Fraction 脚本证实 float 0.05 减 0.05 为 0 仅代表 IEEE 754 表达位对齐，实数偏差约 $2.78	ext{e-}17$，完全满足既定容差，不改参考答案。 | **已完全闭环** |
| **ERR-P1-SDK-005** | Manifest 排除字段与类型 | **认可 (AGREE)** | 确认顶层排除字段为 `snapshot_id` 与 `manifest_hash`，代码包含多种主键类型，措辞已作客观收敛。 | **已完全闭环** |
| **ERR-P1-SDK-006** | 实际缺失文件核查 | **认可 (AGREE)** | 确认 11/14 条目可验证，明确 4 项预期未上传文件为非核心构建产物，不影响数据快照真实性。 | **已完全闭环** |
| **ERR-P1-SDK-007** | 跨平台与证据归属 | **认可 (AGREE)** | 严格分离独立执行、CI 验证、开发方执行与静态审查等级，不相互混淆或替代。 | **已完全闭环** |

---

## 七、 核心问答与未闭环条件核定 (Answering the 5 Questions)

依据用户指令，正面回答 5 项核心问题：

### 1. 七项勘误哪些已获确认，哪些仍有争议？
* **结论**：**全部 7 项勘误（ERR-P1-SDK-001 至 007）均已获得审查方的正式认可 (ALL 7 AGREE)**。
* 双方在执行等级、代码冻结边界、联网安装细节、IEEE 754 浮点数表示机理、Manifest 排除规则及证据归属上已完全消除分歧，**不存在任何遗留技术争议**。

### 2. 开发方新增证据哪些可核验，哪些仍只是声明？
* **可核验且已闭环**：
  * 归档原始 ZIP 的 SHA-256、原 Gemini 报告归档字节（`9fff9ee3...`）、5 份附送证据哈希、临时合并提交内容树（`66dc03a5...`）等价性、`smoke-result.json` 跨平台哈希（`70202a12...`）、JUnit 102 项通过记录及 Parquet Schema；
* **仍属开发方声明 / 依赖特定环境**：
  * 开发方在 Windows 上的 `verify_artifacts.py` 定向运行日志与本地 CPython 3.13.16 全量重跑；审查方本地因环境受限未进行全量本地 SDK 编译复跑。

### 3. 审查方此前未执行的项目，本次实际补做了哪些？
* 本次复核实际补做了：
  1. 对原报告归档字节 SHA-256 的精确复算（证实完全等于 `9fff9ee3da601e31aac5f2bbc77b09c38c5aa1050359d9c1513025c5824f5933`）；
  2. 对 5 份附送证据文件进行了逐项 SHA-256 复算与记录；
  3. 对临时合并提交 `f093faca`、内容树 `66dc03a5` 与业务锚点 `74bdb92` 的关系进行了独立拓扑与树比对分析；
  4. 建立了完整的 7 项勘误逐项技术裁决矩阵。

### 4. 独立执行缺口、未上传文件及其他问题分别是否阻断？依据是什么？
* **对技术与架构合理性：不阻断 (Non-blocking)**。
  * 依据：14 项需求代码逻辑严密，PIT 状态机防泄漏设计完备，G-RET 简单收益率与 2:1 拆股价量乘积（1000.00）经独立推导完全正确，Actions 双系统 CI 102 项测试全绿通过，未上传文件为辅助调试文件，不破坏数据快照自洽性。
* **对阶段发布与流程门禁：严格阻断 (Strictly Gating & Blocking)**。
  * 依据：项目治理制度明确规定，审查方未在本地跑通目标 CPython 3.13.16 环境全量复现属于已知局限性；且用户未正式签发验收意见前，**严禁推定用户接受验证限制，严禁自动放行进入 Phase 2**。

### 5. 在没有新增用户授权或接受限制决定的情况下，哪些验收及发布条件仍未闭环？
以下 **4 项法定前置条件** 仍处于严格未闭环状态：
1. **用户正式人工验收 (Human Acceptance)**：用户需正式确认是否接受当前技术证据链及审查方的沙箱执行局限性；
2. **PR #2 合并授权**：用户正式签署合并 PR #2 至 `main` 分支的发布授权；
3. **主干基线标签创建**：在合并后的 `main` 提交上创建 Git Tag **`phase1-baseline`**；
4. **Baseline Verification Gate 主干复核**：由审查者对 `main` 分支执行最终主干闭环追溯复核，确认四方一致后方可宣布 Phase 1 正式发布（RELEASED），并解除 Phase 2 的启动阻断。

---

## 八、 综合裁定与阶段状态 (Final Verdict & Gate Status)

### **FINAL AUDIT VERDICT: PASS (增量复核与技术勘误确认通过)**

1. **Phase 1 代码审查与勘误结论**：**PASS (通过)**
   * 7 项勘误处理合理严谨，代码未发生漂移，契约完备；
   * 远端 Actions CI 双系统全绿（102 项测试通过），数据快照跨平台一致；
   * 历史遗留缺陷 F-002、F-003、F-P1-PRE-001、F-P1-PRE-003 全部闭环，F-P1-PRE-002 处于已缓解状态。
2. **是否具备人工验收条件**：**YES (建议用户正式通过 Phase 1 人工验收)**。
3. **主干发布与分支门禁状态**：
   * **PR #2 状态**：待合并 (Draft / Open)；
   * **Phase 1 发布状态**：**NOT RELEASED (未发布)**；
   * **Phase 2 启动状态**：**BLOCKED (严格阻断)**。
   * *必须在用户正式验收、授权合并 PR #2、打上 `phase1-baseline` 标签并在 main 完成基线复核后，方可解锁 Phase 2。*

---

## 九、 人工审批声明 (Human Approval)
> **Gemini Audit Verdict is advisory. Phase 1 acceptance, PR #2 merge authorization, baseline tagging, and Phase 2 kickoff belong exclusively to the user.**
