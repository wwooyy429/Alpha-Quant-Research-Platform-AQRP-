# Windows R3 增量修复：REQUEST CHANGES / 独立复核待办

按PR #7 AQRP_FIXED_REVIEW_SHA完整40位检出。本轮只处理WORK-WI-R3-001/002，不代表原WI-R2-001/002关闭或整体隔离通过；P4 PR6另案不纳入。原报告、模型反例、封存收据原件在received/，开发方处理及代码审查另列。先在旧实际wheel与旧工具上复现两项未拒绝，before2.log保留；首次测试导入错误before.log也保留，不倒写成功。

完整干净SDK与双OS CI必须新固定版本实际执行，下载原ZIP核大小/hash/CRC/精确清单、JUnit、47模块wheel、P1/P3工件及新九文件。额外windows-probe-model文件是明确模型适配器输出，只证明代码/覆盖编排，不能写成真实三主体访问。最终日志/环境/制品封存在外置资料包，PR登记完整SHA和路径，不通过重复提交漂移审查头。

请独立重演真实os.walk PermissionError前/后捕获、FileNotFound/I/O/完整树与集合变化；对权威清单删除一个实际动态文件/目录而保持SHA必须拒绝，检查目录0x40及私钥角色期望。核实原生CLI的freeze→三个probe→operator reconcile链，最后必须重新采树，不能用旧清单填充；before/after与原实际输入/sidecar/所有动态对象及目录完整对账。命令和配置字段见OPERATOR_COVERAGE_PROTOCOL.md，本轮不运行这些真实角色命令。

仍未验证：新profile真实operator预建/发布、before/after真实三主体全域、工程并发/崩溃/恢复/重复的真实隔离执行、正式Test、金融批准、VALID-004全部和完整历史宿主。当前账户保持禁用；不重跑管理员脚本、不部署、不合并/标签/实盘/P5；原失败不能补ACL后改判。
