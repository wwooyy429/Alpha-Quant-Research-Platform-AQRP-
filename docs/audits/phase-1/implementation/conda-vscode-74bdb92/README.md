# Conda / VS Code 本地执行与证据归档

2026-10-21（Asia/Shanghai）。用户明确授权配置 `aqrp-p1`、运行完整 SDK / Actions 原始 ZIP 校验并更新 PR #2。本轮由 Codex 在用户 Windows 本机执行，**不属于 Gemini 独立执行**；未验收、未发布，不合并、不打标签、不进入 Phase 2。

## 固定版本与实际结果

- 业务代码固定 `74bdb9216c585d27de91123605aff0266ca028cc`，干净独立检出；此前归档 `7f4981b86fae7e293de8424a2631a873d90a62f3`。本轮只新增环境/执行证据和状态记录，不修改业务、测试、CI、依赖锁或 Golden。
- 现有 `E:\WORK\Anaconda\envs\aqrp-p1\python.exe` 为 CPython **3.13.16**、Anaconda 构建、AMD64/标准 GIL。解释器安装前后 SHA256 相同；22 项锁定依赖按 hash 安装并核对版本，pip check 通过。其他 Conda 环境未修改。
- 正式完整入口 `tools/ci.py` 从 Conda 启动，再按既有设计创建干净 venv，完成 hash 安装、静态/格式、离线 wheel 构建安装、102 测试、分支覆盖率门槛、独立参考数学、SDK 冒烟及固定 gitleaks 正负控制。`formal-sdk/` 原始结果为 **102/0失败/0错误/0跳过**。
- 将该次 wheel 装入 `aqrp-p1` 本身后，确认 import 来自该环境 site-packages；直接在 Conda 中运行相同 102 测试、覆盖率/参考数学/SDK 冒烟也全部通过。见 `conda-direct/` 与 setup 对应日志。
- 修正本机 MSIX 路径后，实际执行工作区两项任务的完整 process 配置（命令、参数、cwd、env），再次通过：`workspace-sdk/` 同样 102/0/0/0，`workspace-zip/` 校验通过。记录在 `setup/workspace-task-results.json`，**未声称在 GUI 点击运行任务**。以上是同一组 102 测试的重复验证，不能合计为 306 项独立测试。
- 两份原始 Actions ZIP 仍引用 `sdk-hash-74bdb92/12288989083.zip`（Ubuntu）和 `12288679676.zip`（Windows），对应 Run 39476825340/attempt 1。实际 SHA256 分别 `73385602dad830f3157dba8f5629616127777511830b02675fd06df517f93e7c`、`8f092b7214202292995276a4dab3187063cd481d8a6556ac342e450738b64ea5`。Conda 实际验证 ZIP 原字节、每平台 11 个已上传根文件、8 表 Parquet hash/schema/值及 Manifest、跨平台逻辑值和 smoke、SDK 回放；两轮 `verification.json` 保留结果。
- smoke 结果 SHA256 为 `70202a124f458f829caa5ac72e136d9c40c76801a63f113aec9863d3bed864d6`。Git 实际核对临时合并提交 `f093faca9a9dd4977caa1142267ff494766d3c7e` 父节点和 tree，与业务固定 SHA tree 相同。

## VS Code 使用

本机独立工作区已生成，配置副本见 `setup/workspace-final.json`。用 VS Code 的“文件 → 从文件打开工作区”打开以下实际路径，然后“终端 → 运行任务”，选择 `AQRP: 完整 SDK 验证（固定 74bdb92）` 或 `AQRP: Actions 原始 ZIP 校验`：

`C:\Users\11638\AppData\Local\Packages\OpenAI.Codex_2p2nqsd0c76g0\LocalCache\Local\AQRP\vscode\AQRP-Phase1-aqrp-p1.code-workspace`

默认解释器是上述 Conda Python，新终端 profile 调用该环境 activate.bat。激活探针已确认解释器/前缀/版本，见 `setup/terminal-profile-probe.json`。已向 VS Code CLI 提交打开请求并记录版本/扩展；窗口状态输出不足以证明工作区与解释器已在 GUI 中选中，因此 GUI 加载状态不作已验证声明。若已打开同名未保存文件，应使用上述“从文件打开工作区”载入实际文件。

工作区使用非同步检出，不覆盖原 B 盘旧工作树或用户全局 VS Code 设置。`setup/physical-paths.json` 解释 Codex MSIX 路径映射；外部 VS Code 使用实际 Packages 路径。完整运行目录也在该文件中。任务仍固定 74bdb92，归档提交后不会自动变为新业务版本。

## 证据范围及仍未闭环条件

原始命令/退出码、依赖安装、版本探针及任务日志在 `setup/`；两次正式入口的原始清单和已归档数据在 `formal-sdk/`、`workspace-sdk/`。`ARCHIVE_POLICY.json` 逐项核对本地完整清单：scanner/bootstrap wheel/venv/cache 留在非同步完整运行目录，不把这些大型第三方文件提交仓库；`.coverage` / `coverage.xml` 原字节分别以 `coverage.sqlite` / `coverage-report.xml` 归档，原清单不改。

远端原始 ZIP 每平台仍有根清单 **3 项未上传**（`.coverage`、scanner、bootstrap pip wheel），项目 wheel 原始字节也未上传。新本地 wheel/文件不补齐旧远端字节，不宣称 14/14 全部复算；本地两次项目 wheel 的不同构建 hash 仅归属各自运行。Gemini 七项 AGREE 保留，但本轮执行不能登记成 Gemini 运行；完整独立执行缺口仍须补齐或由用户明确接受限制。此后仍需人工 Phase 1 验收、分别授权 main 合并/标签、最终 main 检查和稳定基线核验；Phase 2 需单独启动授权。用户当前没有作出这些批准。

## 本轮 CI 路径修正

初次归档85bcb34触发Run39576582339：Ubuntu通过，Windows在checkout因新增解包副本路径过长失败，业务步骤未执行；随后无产物上传为连带失败。原始job记录和解码日志见CI_FAILURE_39576582339.json。将本轮两组ZIP解包目录的artifact/run_id前缀缩短为ubuntu/windows，文件内容及原ZIP不变，映射在ARCHIVE_POLICY.json；不改CI或业务代码、不掩盖该次失败。修正提交须重新核对远端CI。
