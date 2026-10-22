# Windows隔离R3修复候选审查入口

本轮依据用户明确两项修复指令，独立分支codex/fix-windows-isolation-r3从main0a57dccb5618ba08cd3572d6d6b78fec963a3041开始，不修改P4 PR6。发布P3基线及所有既有审查证据保持原字节。用户不授权部署/真实ACL/账户变更/正式Test/金融批准/合并标签；本轮不重复执行管理员脚本。

先读DEVELOPER_RESPONSE.md及原received/REPORT.md、DEVELOPER_HANDOFF.md、OMISSIONS.json、ACL_INCOMPATIBILITIES.json、EVIDENCE.zip；原R2的184检查183PASS/1FAIL不可改。发现两项仍OPEN_PENDING_INDEPENDENT_RECHECK，整体NOT VERIFIED。

变更：windows_acl.py封闭角色ACL和可信祖先/继承投影证明，原严格门禁不删除，OperatorPolicy仅显式绑定新policy后使用；新profile要求新封印binding。engineering_input.py仅可信operator在既有审定readonly anchor下复制P1九文件并以sidecar为最终标记，不改P1 mkdtemp语义。两个tools分别生成可独立读取的新公开工程输入、在实际SID下逐文件只读探针。无自动账户/ACL配置脚本。

测试分别标明模型adapter、真实P1字节生命周期、当前开发身份只读Windows元数据与token捕获；均不是三主体执行。既有单次并发、崩溃恢复、重复拒绝在完整SDK回归。完整SDK/CI结果与固定SHA见后续VALIDATION和PR字段，不能预填PASS。

新工程输入为100/110/121、100/150/200公开参数，固定新snapshot_id wi-r3-public-engineering-20261022。实际九文件、SOURCE、manifest和zip将在SDK及单独封存包提供，可独立核验。原cb10857f...九文件仍不可读，旧hash未独立重算，绝不把新导出替换旧遗漏或宣称auditor已读原件。

## GPT Work复核要求

按PR描述AQRP_FIXED_REVIEW_SHA完整40位获取，核查变更范围与旧原件hash，独立审核closed ACL数值rights、OWNER RIGHTS隐含owner权限抑制、未知ACE/传播规则/readonly/key、祖先删除改权防护、所有子对象继承链及双次捕获；验证默认严格路径/新profile封印binding不绕过正式批准。

独立执行Python3.13.16 standardGIL x64的`python -I tools/ci.py`：全新锁hash安装、真实wheel、旧Ref/结果重放、完整测试/逐模块覆盖，保留失败、命令、环境与工件。双OS CI属于普通runner开发回归，不是实际三主体隔离。必须区分本轮开发方与独立审核执行者，不把报告复制当新执行。

独立逐文件核验九输入、sidecar、所有动态产物，并以真实三主体记录实际SID/token、原始argv/进程退出/完整日志、READ/WRITE_DATA/APPEND/WRITE_DAC/WRITE_OWNER/DELETE探针；拒绝必须native ERROR_ACCESS_DENIED=5，文件不存在/共享冲突不算。实际输入读取必须重算全bytes/hash，不能用canary。before/after对象清单都由operator冻结，新增对象必须完整枚举，输入及sidecar不得漂移；审查config原字节SHA和父manifest/代码环境身份。

但本轮不授权实际配置或再跑管理员脚本：请先审核候选设计/代码和原始证据覆盖。未来真实生命周期回归若需新目录/预建ACL或启用账户，必须另取得用户具体授权，由可信operator在运行前完成配置，不能运行后补ACL。新attempt完整执行before gate→operator预建实际input确认→三主体before probes→工程动态运行（并发单次/崩溃/恢复/重复）→after完整gate→三主体after全路径probes→封存；失败留原值，不重用旧attempt改判。

输出：两项分别的代码修复评估、设计可接受性、独立执行等级和仍缺实际证据；不能自行宣告完整Windows隔离/VALID-004通过、正式Test、金融批准或用户验收。保留P3受限发布/P4G1结论原范围；不合并/标签/部署/P5。
