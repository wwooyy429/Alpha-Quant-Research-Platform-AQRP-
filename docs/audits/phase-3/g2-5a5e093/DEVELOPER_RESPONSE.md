# G2 开发方处理意见 · 5a5e093 修复

原主审固定5a5e093c2e9b39abe1332e49d1df40d20f9fd33f，GPT Work G2 REQUEST CHANGES：1 High、2 Medium。G1 PLAN PASS及U-001/U-002设计确认不变。319项封存文件逐字节核验、ZIP CRC/精确成员/hash均通过，原报告、任务、脚本、失败JUnit/命令按字节归档；received/和RECEIPT.json明确列出仓库子集及仍在原完整ZIP内的SDK/原ZIP，未将子集冒充完整包。

## WORK-P3-IMPL-001 · High

开发方在A1e旧安装wheel复跑原四用例，4 failed已保留。选中的security_master用于市场/日历与上市退市资格，原deps漏了它。现在该完整PIT行进入deps，event/available参与label_available_at、information_interval与dependency_hash；输出security_master_ref绑定修订/行hash/两时钟。审计其余直接依赖：entry/exit bars、两个日历端点、状态选中版本、coverage水位/修订、经济行动及股单位anchor/关联split均已在deps。不改原17组可见性答案。新增真实P1快照覆盖晚到上市/退市更正、1月4日fit拒绝、1月5日恰时/±1us边界与选中主档hash。

## WORK-P3-IMPL-002 · Medium

record_decision必须先从ledger.verify返回的终态manifest取得唯一approvals.json条目，再对单次读取的同一原字节核hash并解析/匹配proposal。原清单未列出时，缺文件和后补文件均拒绝；补文件不能成为原运行证据。正常写入后finish的审批正向路径保留；额外无关文件可作为旁注存在，但不自动获得研究证据资格。新增读取期间替换字节、非映射内容及不匹配proposal拒绝检查；批准记录仍是独立追加，不改终态工件。哈希一致性不是OS权限或真实人签名批准的替代。

## WORK-P3-IMPL-003 · Medium

公共pipeline和compose共用严格_stage_times：decision_time/available_at均必填、UTC微秒规范化，session内所有因子必须同一决策时点，任一输入未来可用即拒绝；compose同时拒绝重复分数键。输出分数及session血缘保留共同decision、保守的最大available、实际交集输入hash、原mask/spec hash。正权重公共交集、重新z和只应用一次方向公式不改。

原旧测试fixture只补显式公共合成时钟以满足收紧的入口契约；独立冻结JSON/数学expected/旧失败原件不改。原四回归按正确expected集成，只有代码风格和变量名适配，原脚本另按原字节归档。新增跨时区同瞬间兼容、缺字段/null、时间边界、重复键、输入不变、跨session网格及血缘变化检查。

## 执行与门禁

源码3模块变化触发全45模块bundle及仅TEST_ONLY/ENGINEERING_APPROVED/NONE工程receipt重审；旧0.2 wheel/Ref、已归档0.3旧wheel及22锁完整保留。独立审查者仍为GPT Work；本轮Codex自测不自判三项CLOSED。实际多主体部署、正式Test/过程证明/正式统计协议与金融批准仍NOT VERIFIED。无账户/ACL/服务/调度修改，无main合并、标签或P4。完整新SDK、原16/4、原91数学、双OS/原ZIP和扫描控制以最终验证回执的真实执行记录为准，旧564/原独立审查成功不外推为修复通过。

开发迭代失败保留：第一次新增row_hash测试误将P1规范化前的Python输入dict当成发布行；已改为独立读取P1发布行核hash，金融期望和原四测试不变；Ruff初始copy样式错误通过格式/局部变量名调整修正。辅助失败与原四真实产品失败分别归档。

首次完整源码检查为573 passed/5 setup errors：该直接pytest调用遗漏AQRP_ORIGINAL_ENV_ARCHIVE，5个原0.2重放夹具明确拒绝运行，未记为通过。原输出保留，接下来正式tools/ci.py干净SDK会自行创建原wheel/锁环境再执行全部578项。
