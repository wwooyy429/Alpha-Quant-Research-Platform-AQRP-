# AQRP 项目执行规则（V3.0 + V3.1 + V3.2）

## 当前权限

只授权 Phase 0 需求审计与架构设计。当前状态以 `docs/PROGRESS.md` 为准。全部设计是待审提案；不得开发 Phase 1–7 业务软件。不得将文件存在等同于阶段已验收。

开始任务先读本文件及 docs 中的 PROJECT_CHARTER、ARCHITECTURE、INTERFACES、REQUIREMENTS、TRACEABILITY、ROADMAP、PROGRESS、DECISIONS，再检查实际 Git 状态和上一阶段批准记录。发现文档与代码冲突先报告，不覆盖既有修改。

## 权威及角色

用户最新明确指令优先；V3.2 修订协作流程，V3.1 修订阶段依赖及质量契约，其余保留 V3.0。原文见 `docs/sources/`。GitHub 仓库及与固定 SHA 关联的可信证据为项目事实来源；未推送的本地成果只能称待同步草案。

- GPT Work：主要开发、测试、文档、功能分支及 PR、修复审查缺陷。
- Gemini：独立计划预审、指定 SHA 审查、独立核对答案及有权限时补充测试。初始只读；独立测试分支与 PR 须用户授权。不能用 GPT 自查、GPT 子代理或模板冒充 Gemini 审查。
- 用户：批准需求/架构变更、阶段验收、main 合并、发布及下一阶段启动。各项授权分别记录，不推定相互包含。

## 必经关卡

阶段计划与接口草案 → Gemini 计划预审 → 解决阻断设计问题 → 已授权范围实现/自测 → PR + 完整 Commit SHA → Gemini 固定 SHA 审查 → 修复新 SHA 并复核 → 人工验收 → 按授权合并/标签 → 停止等待下一阶段明确授权。

Phase 0 可以准备待审设计和资料包；Gemini 预审前不得宣称正式设计基线已批准或开始业务实现。审查者不得审查漂移的分支头部。Critical/High 未解决则阻断；Medium 根据金融正确性、安全与验收标准判定是否阻断。CI、Gemini 和用户批准是不同事实。

## 架构与安全

固定 Python Quant Core + Streamlit + Factor Registry + 独立事件驱动回测。插件只计算信号；界面/CLI 通过同一个应用服务；回测不得依赖具体因子或 Streamlit。所有模块遵守 DATA_CONTRACT 和 BACKTEST_CONTRACT。

仅审查过、哈希批准的因子可进入批准的执行环境；候选因子在隔离、最小权限、无真实凭证环境中测试。Registry 校验不等于沙箱。禁止从网页输入直接执行任意 Python。无明确授权不得连接真实账户或提交真实订单；不提交真实密钥。

不提前实现后续依赖：P2 只测注册/替换/API 兼容；P3 研究替换；P5 组合回测替换；P6 CLI/网页一致；P7 完整替换 E2E。尚未实现能力标记 Planned、Deferred、Unsupported，不伪造结果。

## 开发与证据

分支：main 为已验收稳定版本；feature/phase-X-*、fix/*；audit/phase-X-* 仅经授权的独立测试。不得未经批准合并 main、发布标签或修改 Gemini 原报告。空仓库基线建立方式见 DECISIONS，不自动建立已验收稳定版本。

每项实现必须追溯 REQUIREMENTS 中的 ID；新范围列变更，不扩大阶段。关键金融计算须已知答案、边界、性质测试及独立参考核对。不能用待测函数生成期望值；不删失败测试、不迎合错误实现修改正确答案、不隐藏 CI 失败。

运行记录含唯一 run_id、不可变配置、代码/数据/环境哈希、完整失败记录；最终 Test 不用于反复调参。修改方向、期限、预处理均算实验。锁定依赖并审查升级。

每阶段更新追踪、进度、变更、Review Package、实际命令/输出和人工验收记录。无法运行仅标 NOT VERIFIED。未获用户批准不得把状态设为 ACCEPTED/RELEASED；“继续”等模糊用语不等于验收或下一阶段授权。
