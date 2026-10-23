# Phase5 稳定基线 · 十二项受限工程验收

用户明确 ACCEPTED 十二项（10 MVP / 2 Competition Ready），并授权本次合并与基线标签。GPT Work 对 `1c5a7e62cace7c3e66b7cc7f12fd564cb0013654` 的 G2 PASS，001/002/003 均 CLOSED — FIX VERIFIED。原始审计、接收校验与封存收据见 [g2-1c5a7e6](g2-1c5a7e6/DEVELOPER_RESPONSE.md)，人工原话见 [publication/APPROVAL.json](publication/APPROVAL.json)。

PR #8 获准归档头为 `c43b594f2f427e8a7b3614518b84aa00502365f2`，相对已审实现仅 161 个审计归档和状态文档变化；源码/测试/工具/CI/依赖锁、3444 冻结文件、92 实现身份和 12 已审设计身份均未变。PR 归档头官方双系统 CI run39931047567 各 1158 项通过，两个原始 ZIP 身份、digest、CRC、成员及哈希核验通过。普通合并 `36c26911afb47ff68544e4bf64f060504dfdd94d` 整树等于该归档头，保留历史，不强推。

合并后全新干净已安装 wheel SDK 1158 项通过，0 失败/错误/跳过；原 20 + 4 回归及 91 项数学由开发方重执行通过。实际环境、完整命令、原始日志和工件哈希见 [publication/VALIDATION.json](publication/VALIDATION.json)、[SDK_ARCHIVE.json](publication/SDK_ARCHIVE.json)。独立 G2、PR CI、合并后开发验证是不同执行事实；它们均不属于 Phase6 测试。

发布登记只增加证据及状态，不改已审业务版本。阶段里程碑标签 `phase5-baseline`、`v0.5.0` 与 main 原子发布并核验同点后为 RELEASED；已审 Python 包仍为 `0.5.0.dev5`，69 模块 bundle `68d723fd865a59ad843d0be096e841d1e56005907bb8783037a784c8159eda3e`，锁 `86c7bf65c9a9690036006360062c8cd10a91279705b4070af7033d7699abffeb`。旧标签不移动。最终基线完整 40 位 SHA 由 `git rev-parse 'phase5-baseline^{}'` 和 PR #8 实际发布回执核实，避免文档自包含自己的提交 SHA；本次发布提交不得混入业务变更。

WI-R2-001/002 及真实 Windows 隔离继续 DEFERRED / NOT VERIFIED，正式 Test 未运行、金融批准 NONE，完整历史宿主仍未验证，沿用软件包/依赖锁/旧因子/结果重放验收边界；正式入口继续 APPROVAL_REQUIRED。独立 Windows PR #7 未集成，不启用账户、不改真实 ACL/服务/调度、不部署、不实盘。

仅在发布核验后从此 main 基线创建 Phase6 独立 G1 计划分支，范围为原需求 UI-001–008（5 MVP / 3 Competition Ready）；业务实现、Phase6 验收/合并/发布及 P7 均须后续明确授权。计划 PR 以 AQRP_FIXED_REVIEW_SHA 锁定新完整 SHA 交 GPT Work 独立预审。
