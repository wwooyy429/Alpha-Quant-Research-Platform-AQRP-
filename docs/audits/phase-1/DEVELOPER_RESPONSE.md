# Phase 1 计划预审：开发方处理意见

2026-10-21。原报告按字节归档，hash及固定审查SHA见gemini/PRE_REVIEW_EVIDENCE_INDEX.json。报告PASS仅覆盖380d9f86467db874033a06a9e6487fd3998e205f计划；不能外推到后续代码。依据用户既有授权及此次继续开发指令，进入M1.1，尚无阶段验收/合并/标签/P2权限。

| 原报告表述 | 正式口径 / 处理 |
|---|---|
| src/data/*.py、storage.py等缩写 | 包前缀src/aqrp；具体模块以预审DATA_IMPLEMENTATION_SPEC及实际清单为准 |
| event_timestamp | 契约字段event_time |
| calendar (market, session_date) | P0固定(calendar_id, session_date)，日历修订以版本/快照承载 |
| 最大available_at“或”最高版本 | 先双时间可见过滤，再选可见最新修订；同可用时刻冲突拒绝，绝不读取未来版本 |
| 拒绝一切纯日期 | 仅timestamp字段；session_date是合法date |
| TimestampResolutionError | ContractError兼容子类，保留结构化code/field/request_id/retryable |
| 迟到停牌10:30才生效 | effective_from仍可为10:00，10:30才可见；有效时间与可用时间分离 |
| 已排除venv/cache | Git忽略不等于物理迁移；当前尚未创建业务venv，实际路径在M1.1核实 |
| tzdata>=2026.5仅Windows | 保留更严格候选tzdata==2026.5，两平台固定包数据，不依赖系统数据库漂移 |
| G-RET 100→105=.05 | 作为新增独立参考案例；不替换原100→110=.10，容差仍abs1e-12/rel1e-10 |
| 时区“Section三.2脚本”及误差0 | 原文给出说明但未附完整运行脚本/stdout；记为审查方报告的独立执行，开发方未复现其沙箱；不能断言浮点普遍零误差 |
| 彻底消除泄漏 | 设计通过；实际防泄漏仍需实现、反例/性质/独立参考及固定SHA复核 |
| P1-PATH/P1-ISOLATION | 补充测试别名，不新增或改写106项需求 |

F-P1-PRE-001为实施前置要求而非设计阻断：优先生成全传递哈希锁，做双平台干净安装。F-P1-PRE-002执行非同步物理venv/cache/产物路径，源码工作区仍在同步目录。F-P1-PRE-003按精确包版验证DST和时区。F-002/F-003在代码、真实测试/CI与审查闭环前保持OPEN。

未附原始独立运行产物的证据限制予以保留。既有PLAN/SELF_CHECK/COMMAND_LOG/MANIFEST作为380d9f8历史快照保留，不覆盖为实现验证。后续实际失败/成功日志另存实施证据目录。
