# 兼容性增量及冻结范围

IMPLEMENTATION_IDENTITY.json 以归档起点0242db37b4c822e7c73ef6c17faf104bcea54892为逐文件事实来源，分别列出全部原字节保留文件和本轮明确变更/新增文件；原 G1 FROZEN_INPUTS/FILE_MANIFEST 是当时的历史记录，不冒充实现后全文件未改。新增根/UI包内扩展锁与已审G1锁逐字节一致，原core锁和全部既有金融数学/Golden/审计原文保留。

既有适配：experiments/ledger 的 start 记录预分配归属，trial fingerprint 排除新增 task_binding/task_binding_hash 运维元数据，但继续共享次数/预算并记录重复；research/portfolio/backtest services 传递显式 context、增加检查点与重放目标封存；Simulator 仅增加实例上下文、内部P4调用前绑定及原终态复用；provider 在原全部来源/manifest/candidate/risk/发布字节检查之前加绑定核验。无context旧API行为保持。沒有改数据、标签/拟合、推断、构造/取整、风险、撮合、金融账本和绩效公式。

包装：版本0.6.0.dev1、新可选UI依赖/两个入口、准入bundle工程收据、CI扩展依赖/烟测/工件、安装元数据测试。CI使用实际安装包目录测覆盖，确保Streamlit以__main__编译的脚本也被计入；不排除任何代码，不降低已审行/分支门槛。Task/context/state为95/90，普通服务90/85，纯UI/CLI80/70。

首批开发失败日志全部保留，包括多日策略合法SELLABLE拒绝、视图导入遗漏、错误组件断言、未知状态错误归类、CLI冻结输出格式及编辑期间语法失败。错误测试接口字段按已有契约校正（重复试验字段为repeat_of）；没有从被测函数生成正确期望值、删除失败反例或更改原Golden答案。

Windows真实隔离R2两项、正式Test、金融批准和历史宿主限制保持；源码适配及所有工程自测均不关闭这些延期。
