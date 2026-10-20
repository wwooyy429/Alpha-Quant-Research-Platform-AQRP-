# 环境、版本与安全方案

关联ENV-001–003、SEC-001–004、EXP-001。Phase0仅方案；当前Phase1已授权且用户选Python3.13.16，实施前环境/CI计划见audits/phase-1/ENVIRONMENT_PLAN.md，尚未安装/升级业务运行库。

| 项目 | 当前实际 | 拟定/验收要求 |
|---|---|---|
| 本次文档核查 Python | 3.10.11 | 仅标准库审计脚本使用；不是业务批准基线 |
| Git | 2.47.1.windows.2 | 保存所有审查与批准对应完整 SHA |
| 业务 Python | 用户已选CPython3.13.16，尚未安装验证 | 选择原话见P1 AUTHORIZATION；标准GIL x64，预审后核验安装/依赖组合，不能称已兼容 |
| 依赖锁 | 尚未生成 | Phase 1 解析直接/传递精确版本及 wheel 哈希；Windows 与 Linux CI 均验证 |
| CI | 未建立 | Phase 1 开始代码时建立 GitHub Actions |

Phase1产物须含精确Python/OS/架构、完整传递依赖/hash锁、安装器版本和环境清单，不浮动latest。按阶段加入必要库，不提前安装高级研究/生产依赖。environment_hash包含Python patch、锁和原生依赖/OS，升级需影响分析、回归及审批。D-003的Python选择已获用户确认，锁/兼容/干净安装仍待实际验证；DEPENDENCY_CANDIDATES只是元数据候选。

CI 从已锁定来源安装，执行格式/静态检查、分阶段单元/契约/集成/性质/回归及覆盖率，上传原始日志、JUnit/coverage、manifest 与失败工件。第三方 Actions pin 完整 SHA；外部 PR 使用无密钥只读 token，不用有写权限的工作流直接执行不可信 PR。缓存包含锁文件和 OS 哈希，不能掩盖干净安装失败。

新因子流程：提交代码/声明 → 静态及人工代码审查 → 内容哈希白名单 → 隔离低权限测试 → API/数学/泄漏测试 → Candidate 验证 → 研究批准 → 策略证据批准。未审代码不得进入已批准环境；元数据 Approved 或 Python 类型约束不能阻止插件读文件/网络。具体 sandbox 需评审，未具备时仅允许审查过的内置因子。

默认模拟经纪，无真实凭证/真实账户入口。环境变量或凭证库仅在未来获批后使用，日志脱敏；`.gitignore` 不是防泄密保证，提交前和 CI 需秘密扫描。真实执行另列 Production Extensions，当前 Unsupported，不能因为比赛适配自动开启。外部数据授权/下载条件必须记录。

不可变 run 配置与数据/代码版本见 INTERFACES；只追加状态与产物哈希。配置不含密钥，敏感引用使用不泄露值的 identifier。失败、不可复现及脏代码状态保留。历史实验的重现不能覆盖旧产物，也不应重新读取供应商最新数据。

GitHub 初始 Gemini 只读；需要独立测试写入时由用户授权 audit 分支和 PR。main 保护/required checks/CODEOWNERS 为拟配置项，未核实权限设置前标 NOT VERIFIED。不得把本地流程文档视为 GitHub 已强制执行。
