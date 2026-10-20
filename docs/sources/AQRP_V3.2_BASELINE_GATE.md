# AQRP V3.2 补充修正 — Phase 0 Main Baseline Release Gate

本指令用于修正 AQRP 阶段验收流程中 Phase 0 缺少 main 稳定基线的问题。

## 1. 强制基线规则

Phase 0 的设计文档和项目规范是后续全部开发阶段的正式依据。

即使 Phase 0 没有业务代码，也必须建立可追踪的 Git main 基线。

**Phase 0 审查通过并不等于基线已发布。**

必须区分：

- AUDIT PASSED：Gemini 审查建议通过。
- ACCEPTED：用户明确批准。
- RELEASED：已批准的成果在 main 中形成经过核实的稳定版本。

Phase 1 只能在 Phase 0 达到 RELEASED 状态后启动。

## 2. 当前修复任务

请首先检查：

1. GitHub 仓库是否已有 main 分支。
2. 当前默认分支和已有 Git 历史。
3. Phase 0 的实际开发 Commit。
4. Gemini 审查所对应的 Commit SHA。
5. 用户是否已经正式批准 Phase 0。
6. main 当前是否包含已批准的 Phase 0 文档。
7. 是否已经存在 Phase 0 稳定版本标签。

如果 Phase 0 尚未经过用户正式批准，不得自行发布基线。

## 3. 创建 main 基线

如 main 已存在：

- 不得覆盖或强制重写历史。
- 从经过批准的 Phase 0 内容准备 Pull Request。
- 检查合并差异。
- 确认适用的文档和配置检查通过。
- 按用户授权合并到 main。

如 main 尚不存在：

- 在保留已有 Git 历史和审查证据的前提下，建立正式 main 分支。
- 将已经批准的 Phase 0 项目文件作为初始稳定内容。
- 设置正确的默认分支。
- 不得使用强制推送覆盖现有工作。

## 4. 发布 Phase 0 基线

经授权完成 main 更新后：

- 核实 main 对应的 Commit SHA。
- 创建 Git Tag：phase0-baseline。
- 建立 docs/BASELINE.md。
- 记录已批准需求与架构文件的版本。
- 记录 Gemini 审计报告及审查 Commit。
- 记录用户批准信息。
- 更新 PROGRESS.md。
- 更新 CHANGELOG.md。
- 验证 Git Tag 与 main 的目标版本一致。

如果合并产生了新的 Commit SHA，必须确认合并后的最终内容没有超出已批准范围，并根据变更影响重新执行适用检查。

## 5. Phase 1 启动限制

Phase 1 必须从已核实的 main 基线创建独立开发分支。

不得以尚未合并的 Phase 0 草稿分支作为未经说明的正式基线。

如果 Phase 0 的 main 基线缺失或无法验证：

**PHASE 1 STATUS = BLOCKED**

不得继续开发。

## 6. 最终交付

请提交：

- main 分支状态。
- main Commit SHA。
- Phase 0 Git Tag。
- BASELINE.md 的实际路径。
- Gemini 审计证据。
- 用户批准状态。
- 已验证的项目文件列表。
- 是否满足 Phase 1 启动条件。

不得虚构 Git 操作、提交、标签或测试结果。

本任务仅用于补齐 Phase 0 版本基线，不得自动开发 Phase 1。
