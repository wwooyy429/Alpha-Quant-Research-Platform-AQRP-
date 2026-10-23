# GPT Work G2 实现复核资料索引

仓库：https://github.com/wwooyy429/Alpha-Quant-Research-Platform-AQRP- 。PR #9：https://github.com/wwooyy429/Alpha-Quant-Research-Platform-AQRP-/pull/9 。开发交接文本和PR描述提供同一个完整40位 AQRP_FIXED_REVIEW_SHA；必须先取该提交，HEAD漂移单列，不能默认继承任何审核通过结论。

1. 需求和授权：REQUIREMENTS_SNAPSHOT.json（原8项、5MVP/3CR）、IMPLEMENTATION_AUTHORIZATION.json（用户原话、三个条件均明确接受）；原G1固定e71f6f090b102e4abfd70a5999e495f49546a1b5和原报告见g1-e71f6f0。
2. 设计到实现：IMPLEMENTATION.md、IMPLEMENTATION_TRACEABILITY.md、COMPATIBILITY_IMPACT.md/json、IMPLEMENTATION_IDENTITY.json。原G1合同/答案不改；实现和现行证据在这些增量资料中说明。
3. 实际接口：services/tasks、task_state、task_context、task_requests、task_inputs、task_history、task_cli、task_worker；ui/app、numbers、environment、launch。仅八项受限工程，旧金融算法原模块及core锁保留。
4. 测试：tests/ui和全部原tests；tools/ci.py干净wheel/锁安装/完整SDK/覆盖、原参考与各阶段真实烟测；tools/ui_smoke.py实际SDK/旧CLI/新CLI/AppTest两个因子完整链及原包/Ref执行。tools/ui_reference.py只用stdlib核字节/清单/来源和明确数值投影，不导入AQRP。真实浏览器另附原始交互、截图、下载/取消/失败/重放、实际启动argv与安装包身份。
5. 重点独立反例：不能从一个P3成功提升全任务；P4内部真实父/目录/索引/时间/来源/适配raw/hash与代码锁；10并发同key唯一claim；P3/P4/P5崩溃/取消/成功提交竞争和未知状态；completion/SQLite双断点；重封装清单删项/重复/路径别名、初始记录与金融对账篡改；默认revision/旧请求/旧Ref只读；4096/4098数值边界与保留原文。
6. 证据需核官方run/attempt/job/head SHA、干净SDK实际代码40SHA/dirty=false、Python3.13.16/interpreter/distribution+RECORD、原core+UI锁/29原始UI wheel、项目wheel和bundle、所有原始ZIP/API摘要/长度/CRC/精确成员及pytest current复制子树。开发方封存索引及原始日志实际路径在交接文本中，不把开发自测冒充独立审查。证据索引不嵌入自身提交SHA来制造循环哈希，固定身份由Git提交、外置封存收据与PR描述关联。

请按完整固定版本独立执行必要的干净SDK、数学/性质和新反例；保留原始日志和NOT VERIFIED边界。Windows R2两项继续 DEFERRED / NOT VERIFIED，正式 Test未运行、金融批准NONE、完整历史宿主边界保留。不能因工程测试关闭延期。此次不合并、打标签、部署、实盘、运行正式Test、授金融批准或进入P7；G2结论也不替代用户阶段验收。
