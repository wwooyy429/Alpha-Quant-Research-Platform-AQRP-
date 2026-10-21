# Phase1环境、依赖及CI方案（待Gemini预审）

用户已明确选择CPython **3.13.16**；实际安装/验证尚未开始。本文及DEPENDENCY_CANDIDATES.json是计划证据，不是已完成的锁文件、安装或CI记录。

## 版本及安装边界

- 业务运行时：CPython 3.13.16，标准GIL、x64，不使用free-threaded或实验JIT。与现有Python 3.10.11文档工具隔离，不改其全局site-packages或系统默认Python。
- 官方发布页列出该版本及Windows x64安装器：[Python 3.13.16](https://www.python.org/downloads/release/python-31316/)。预审后安装需验证实际下载文件、签名/校验与sys.version_info，记录来源及hash；本次只读核对，未下载执行安装器。
- 官方Windows x64安装器公告SHA-256候选为 `fb4f9f5d438b2396da0086dc70b935c530cb578e37adc6d354f7ad2037fee83b`；必须在实际下载时重新比对，不以本段抄录代替校验。
- P0曾建议评估3.12；其安全更新已为源码形式、无新版官方Windows安装器，见[官方3.12.13说明](https://www.python.org/downloads/release/python-31213/)。用户现明确选3.13.16，属于环境决策更新，不改核心架构；实际依赖兼容仍待验证。
- 本机只读探测：python可运行3.10.11；py注册的3.11启动失败；uv未发现。记录为环境现状，不把注册项当作业务可用环境。
- 业务venv、DuckDB可变缓存、测试临时产物优先置于解析后确认的本地非同步目录（如LOCALAPPDATA下AQRP专用目录）。源代码工作区仍在百度同步目录，不能因此称整套开发环境已物理隔离。项目和快照路径必须显式记录，不依赖当前Shell cwd。

## 精确依赖候选

来源为2026-10-20直接读取的PyPI元数据；选中的wheel路径/hash及依赖声明保存在DEPENDENCY_CANDIDATES.json。下列是待预审的候选，不声称全部传递依赖已解析，不能将该JSON当requirements.lock。

| 用途 | 候选版本 |
|---|---|
| 数组 / 表格 | numpy 2.5.4；pandas 3.0.6 |
| Parquet / 查询 | pyarrow 26.0.0；duckdb 1.5.6 |
| 跨平台IANA数据 | tzdata 2026.5 |
| 测试 / 覆盖率 | pytest 9.1.1；pytest-cov 7.1.0 |
| 性质测试 / 静态检查 | hypothesis 6.170.5；ruff 0.17.1 |
| 安装/锁解析 | pip 26.2.1；uv 0.13.4 |
| 构建后端 | setuptools 84.2.0；wheel 0.48.0 |

仅安装本阶段需要的基础/开发工具，不提前安装SciPy/statsmodels/Streamlit/Plotly或高级研究框架。Hypothesis只用于QA-002的性质测试，不改变产品架构。pandas不启用test/all等extras，其内部测试依赖限制不代表本项目默认依赖；最终统一解析并验证真实组合。

预审后：pyproject记录精确直接依赖和requires-python；uv固定版本解析CPython3.13.16及Windows/Linux标记，生成含所有传递版本和wheel hash的requirements.lock。若某平台无法共同解析，列明原因和显式平台锁方案再复核，不静默放宽版本。安装用固定pip、require-hashes和only-binary策略，拒绝隐式源码构建或自动浮动latest。构建工具本身也需固定hash引导安装；项目从固定Git SHA构建本地wheel、记录wheel hash，再离线no-deps安装，不在构建隔离中重新联网解析依赖。

将在实际实施时核对uv编译参数和完整锁语义；[uv锁文件说明](https://docs.astral.sh/uv/concepts/projects/layout/)可供审查。当前没有生成锁文件、安装矩阵或成功记录。

## CI与秘密扫描

M1.1开始正式代码时同步提交GitHub Actions，目标Windows x64与Ubuntu 24.04 x64，Python精确3.13.16。checkout/setup-python等第三方Actions固定完整Commit SHA，预审后从其官方仓库核验；不把版本标签写成不可变锁。记录runner实际ImageOS/ImageVersion及OS/编译器/解释器信息，不把托管runner名称当成完整不可变OS镜像。

工作流使用contents:read、无真实凭证；PR使用pull_request，不用有写权限的pull_request_target执行外部代码。步骤：固定工具与锁文件安装→导入/版本/数据smoke→ruff检查及格式→pytest单元/契约/性质/P1集成/泄漏→覆盖率关键模块阈值→秘密扫描→上传脱敏的原始日志、JUnit、coverage及环境/数据/结果manifest。缓存键包含OS/Python及锁hash，至少一个干净安装路径不依赖缓存。

秘密扫描器候选：[gitleaks v8.30.1](https://github.com/gitleaks/gitleaks/releases/tag/v8.30.1)，官方GitHub release元数据读取到：

- Windows x64 zip：sha256 `d29144deff3a68aa93ced33dddf84b7fdc26070add4aa0f4513094c8332afc4e`。
- Linux x64 tar.gz：sha256 `551f6fc83ea457d62a0d98237cbad105af8d557003051f41f3e7ca7b3f2470eb`。

实施时实际下载/校验并验证固定版本CLI及正负控制；开启脱敏，不上传原始敏感匹配值；任何白名单须逐项理由，不能通过忽略全部fixture或失败返回码让扫描通过。无真实API密钥或账户接入。

## 存储语义与版本验证

[DuckDB timestamp官方说明](https://duckdb.org/docs/current/sql/data_types/timestamp.html)区分naive timestamp和微秒TIMESTAMPTZ；后者表达时点，不替代source_timezone/IANA及session_date字段。Parquet使用显式Arrow timestamp[us, UTC]及decimal128，测试源→Arrow→Parquet→DuckDB→结果的类型和值，禁止依赖库自动推断。

Decimal金额/单位转换放显式Decimal运算，不依赖SQL除法或Pandas自动转换保持精度。跨平台分别保存实际环境hash；同一逻辑Golden结果一致不等于两个OS环境hash必须相同。

F-002只有实际CI run/attempt/job及所有适用检查真实通过后才可申请关闭；ENV-001只有完整锁与干净安装证据齐全后才可标完成。当前二者均Planned。
