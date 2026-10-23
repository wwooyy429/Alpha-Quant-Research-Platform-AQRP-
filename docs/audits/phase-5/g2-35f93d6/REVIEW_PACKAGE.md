# Phase5 003新固定版本独立复核入口

审查对象仅为PR #8描述AQRP_FIXED_REVIEW_SHA的完整40位SHA，须与远端head一致并detached检出；不得以漂移HEAD替代。原35f93d6整体BLOCKED；001/002独立关闭，新003 High仍OPEN，开发方仅提供修复候选和必要自测。

重点003：用真实公共服务LONG_SHORT重现原cash_set+1/U_short−1，原Journal897.9/99.9/797.9、旧误报798.9；要求新包返回未知财务状态、无已知账户、原提交/原原因不变。检查所有方向恒总额桶重分类、分开R/P符号核验、现金lot非负/原始所得/FIFO剩余/拆股/T+1、S_set子集。测试真实已交收/未交收部分cover、合法margin loss、正常projection及异常恢复，不可只确认外层FAILED或只比较总额。交收session元数据必须绑定实际原子Journal，不用后补标志作为证明。实际SDK/官方原ZIP及脚本复跑证据见PR描述外置封存包；开发方复跑不能写成GPT Work已独立执行。

保留已关闭001/002的六边界、原run真进程恢复、坏链/读错误/总额差、腿/方向/费用/序列化/数学与旧20+4/91、原Ref66字节/三run、P1九输入/P3/P4/P5两因子链及replay。核原12设计与3444冻结文件。新SDK完整测试与line/branch门槛；双OS官方run、执行SHA/tree/parents、原ZIP/API digest/CRC、精确成员/hash/wheel69/锁/终态链；上传pytest current副本必须有补充全子树字节核验，不能虚构symlink权限身份。

原独立报告与150文件封存身份见RECEIVED_IDENTITY；开发处理/输出勘误/工程自查分别见DEVELOPER_RESPONSE、OUTPUT_CONTRACT_ERRATA、ENGINEERING_CODE_REVIEW。需要GPT Work另写/运行必要反例，给003关闭或仍OPEN依据和新固定SHA的G2结论。G2通过仍不是阶段验收、合并或发布许可。

WI-R2两项及真实隔离DEFERRED / NOT VERIFIED，正式Test未运行、financial_approval NONE、完整旧宿主未验证（限既有包/锁/Ref重放）。不部署、启用账户、改真实ACL/服务/调度、实盘、运行真实正式Test、授金融批准、合并、打标签或进入P6。
