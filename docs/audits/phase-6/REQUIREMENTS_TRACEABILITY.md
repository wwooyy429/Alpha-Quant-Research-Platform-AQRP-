# 原需求逐项映射

原始目录106项保持不变，逐字段快照见 REQUIREMENTS_SNAPSHOT.json；以下为设计映射，不是完成声明。

| ID | 等级 | 交付 | 既有/拟增接口 | 验收与风险 | 测试 |
|---|---|---|---|---|---|
| UI-001 | MVP | Dashboard | tasks/list + immutable result catalogue | 真实状态/因子数/当前任务/最近研究和回测/完整性错误分别计数；状态不从文件存在或图表推断 | T6-DASH / T6-TASK |
| UI-002 | Competition Ready | Factor Library | approved builtins catalogue + versioned configuration store | 精确FactorRef、参数模式、TEST_ONLY/金融NONE、配置增删/权重/比较与回滚；不能上传或执行任意Python | T6-FACTOR / T6-CONFIG |
| UI-003 | MVP | Alpha Research | P3 request builder → research | 股票池/区间/期限/预处理/方向冻结；IC/Rank/ICIR/分层/衰减/OOS均读原始后端报告，null与拒绝原因完整 | T6-RESEARCH / T6-PARITY |
| UI-004 | MVP | Strategy Backtest | P3/P4真实来源 → P5 services | 明确独立工程模式与正式拒绝；原始净值/回撤/订单/Fill/持仓/逐桶对账；未知财务状态不回退旧余额 | T6-BT / T6-FORMAL / T6-PARITY |
| UI-005 | Competition Ready | Experiment Manager | ledger verify/catalogue/compare + declared replay APIs | run_id/代码与数据/环境/参数及版本比较、原始报告下载、声明投影重放；终态清单外文件禁止读取，不覆盖旧实验 | T6-ARTIFACT / T6-REPLAY |
| UI-006 | Competition Ready | Settings | append-only validated defaults snapshots | 合成数据目录、允许参数/费用/风险默认值、依赖与日志；只影响新请求，旧快照不改；无凭证/ACL/服务配置 | T6-SETTINGS / T6-SAFE |
| UI-007 | MVP | CLI / SDK / UI parity | one canonical effective request + existing services | 相同精确因子/数据/代码/seed/defaults，config_hash与语义数值相同；只忽略预先枚举的run_id/墙钟等元数据 | T6-PARITY / T6-REPLACE |
| UI-008 | MVP | Task orchestration | durable TaskService + safe cooperative checkpoints | 任务提交/查询/取消/恢复/日志/图表；幂等键与请求绑定；失败和取消不报成功；原子账本之后恢复真实状态 | T6-TASK / T6-CRASH / T6-IDEMP |

统一最早阶段为P6；每项开发前提为P5 RELEASED、P6 G1闭环和单独实施授权。全部Planned；MVP与CR均是本阶段必需能力，不以延期/Unsupported占位。
