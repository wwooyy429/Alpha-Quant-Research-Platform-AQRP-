# AQRP 项目执行规则（V3.0 + V3.1 + V3.2）

## 当前权限

当前仅Phase 0范围。用户已于2026-10-20明确验收Phase0并授权PR#1合并main及创建phase0-baseline，批准记录见docs/audits/phase-0/publication/APPROVAL.json。当前状态以docs/PROGRESS.md为准；未授权Phase1–7业务开发，未来阶段未决事项仍按各自前置条件批准。

Phase0已ACCEPTED并RELEASED，Gemini对7de1d0e81385ae97f98ea673fe05dd726f0b577b的Baseline Verification Gate给PASS、F-001 CLOSED；原件及索引见docs/audits/phase-0/gemini/GATE_EVIDENCE_INDEX.json。phase0-baseline保持固定，不因后续报告归档移动。Phase1基线阻断已解除，执行状态为AWAITING USER AUTHORIZATION / NOT STARTED，尚无Phase1启动授权。发布登记见docs/BASELINE.md。

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

Phase0须区分 AUDIT PASSED（Gemini建议通过）、ACCEPTED（用户明确批准）、RELEASED（获批内容已在main形成核实稳定版）。空main初始化是一次性授权例外，不算RELEASED。仅在Gemini证据、用户阶段批准及合并/发布授权齐全后更新main，创建 `phase0-baseline`，维护BASELINE/PROGRESS/CHANGELOG并核对标签与main目标一致；合并新SHA须核对范围及适用检查。不得强推/重写现有历史。Phase1需Phase0为RELEASED、标签/main/文件及证据可核实，并另获Phase1授权，必须从核实main创建独立分支。

每项实现必须追溯 REQUIREMENTS 中的 ID；新范围列变更，不扩大阶段。关键金融计算须已知答案、边界、性质测试及独立参考核对。不能用待测函数生成期望值；不删失败测试、不迎合错误实现修改正确答案、不隐藏 CI 失败。

运行记录含唯一 run_id、不可变配置、代码/数据/环境哈希、完整失败记录；最终 Test 不用于反复调参。修改方向、期限、预处理均算实验。锁定依赖并审查升级。

每阶段更新追踪、进度、变更、Review Package、实际命令/输出和人工验收记录。无法运行仅标 NOT VERIFIED。未获用户批准不得把状态设为 ACCEPTED/RELEASED；“继续”等模糊用语不等于验收或下一阶段授权。

## 自动生成的同步冲突副本

用户于2026-10-20明确要求：“以后出现自动生成的冲突副本请删除它”。后续工作中发现此类副本，应核对正式文件：纯重复或仅换行/编码差异的副本直接删除，无需逐件询问；如有独有有效内容，先以可追溯方式保留差异或在授权范围内合并，再删除自动副本，不能覆盖正确的正式文件或扩大已批准范围。仅清理已确认自动生成的副本，不删除正式需求、历史审计原文或用户独立编辑文件。不据此启动后台监控、移动工作区或改变阶段授权。
