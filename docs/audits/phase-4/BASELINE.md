# Phase4 稳定基线 · 七项受限工程验收

用户已明确 ACCEPTED，GPT Work 对 `3c8757949b0fd5c97953b06a74ebc2d0e56676e4` 作 G2 PASS，两项发现 CLOSED — FIX VERIFIED。PR #6 普通合并提交 `d3993d07e5df1b5c2f7acd30cb628226f7b1fc09` 的完整 tree 等于该已审 SHA，父提交为 `0a57dccb5618ba08cd3572d6d6b78fec963a3041` 和 `3c8757949b0fd5c97953b06a74ebc2d0e56676e4`。原件及封存核验见 acceptance/，人工原话见 publication/APPROVAL.json。

发布登记仅归档证据和更新状态，业务源码、测试、工具、CI、锁、构建及扫描配置不变。登记提交与 main、附注标签 `phase4-baseline` 和 `v0.4.0` 原子发布并核验同点后为 RELEASED；最终 40 位 SHA 以 `git rev-parse 'phase4-baseline^{}'` 及 PR #6 发布回执解析，避免文档自包含自己的提交 SHA。旧标签不移动。

基线里程碑标签 v0.4.0 与已审 Python 包版本 0.4.1.dev1 分别是阶段版本和制品版本；不为标签改写未经复核的业务版本或准入收据。53 模块 bundle 保持 `0ccd7642b3c69d06c552bc328195387f0a9ec8a06a45398df0076bde8f81cdf7`，依赖锁保持 `86c7bf65c9a9690036006360062c8cd10a91279705b4070af7033d7699abffeb`。

七项：PORT-001/002/003、RISK-001/002/003/004，4 MVP、3 Competition Ready。合并后全新干净 SDK 实际 844 项通过，0 失败/错误/跳过；原 20/四项及 91 项数学脚本由开发方原字节复执行通过。环境 Python3.13.16、真实 wheel/快照/结果及完整原始选择 ZIP 见 publication/VALIDATION.json、SDK_ARCHIVE.json。原双 OS 各 844 的官方 ZIP 属合并前 G2 证据，未冒称合并后 CI 或 P5 测试。

真实 Windows 隔离、正式 Test、金融批准及完整历史宿主仍延期/未验证；软件包、锁、旧 Ref 与结果重放按既有有限范围验收。正式入口 APPROVAL_REQUIRED、financial_approval=NONE。独立 Windows PR #7 未纳入本次发布。无部署、实盘或真实正式 Test。

本阶段 RELEASED 后只允许从核实 main 基线创建 Phase5 G1 计划分支；P5 实现、其验收/合并/发布及 P6 均未授权。独立预审仍须锁定新的完整 SHA；P4 回归不得写成 P5 测试通过。
