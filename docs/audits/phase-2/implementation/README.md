# Phase2 原始执行证据

执行者为Codex开发方；CI为GitHub hosted runners，独立Gemini实现审查尚未收到。固定实现8183b3762b56c466b989d9062a720b5f0d31172a。

- EVIDENCE_INDEX.json为当前总索引；local-verification.json为实际全SDK核对；local-archive-map.json逐个对应原始本地文件路径/归档名/hash。local/driver.log为启动完整日志，commands.log保留内部命令、输出及失败退出。
- ci/12342621298-ubuntu.zip、12342066424-windows.zip是GitHub原始ZIP压缩字节，未经重打包；API元数据与*-verification.json分开存。上传工具和pip bootstrap字节明确省略，不声称原件齐备。新P2归档不修补旧P1原始上传的缺项。
- verify_archive_executed.py是开发方实际执行归档脚本，保留当时绝对路径；重跑须在副本中调整ROOT/RUN/DEST，避免覆盖归档。它依赖安装0.2 wheel的正式venv；不要改原件使其伪装通用新工具。校验快照调用现有P1 verify_snapshot，并独立逐字节核对所有上传文件/运行产物。
- development/保留233及243项阶段的实际日志/JUnit/覆盖率；243项中间coverage gate失败由终端输出发现（未单存该命令原始stdout，不补造日志），后修复并增加负例至254。最终覆盖率及所有执行结果以local/与CI原件为准。
- 本地原始. coverage数据库（实际文件名.coverage）归档为coverage.sqlite、coverage.xml为coverage-report.xml，以避免Git忽略；字节不改。其余selected文件原名。项目wheel/两快照/因子运行产物保留，venv/source/cache/下载工具不入库。
- FILE_MANIFEST.json覆盖当前全项目可交付文件（排除自身）。FINAL_CHECKS.json记录保护资产/版本核验；后续提交只归档证据和文档，源码、测试、CI及锁与8183一致。

当前不是人工验收或发布凭据；不合并main、不打标签、不进入P3。
