# V3.1/V3.2 变更摘要及影响分析

V3.0核心架构、业务功能、Phase0–7及人工审批保留。V3.1增加/澄清时间、账本、样本外、分级、独立答案和安全；V3.2固定GPT开发与Gemini独立审查协作。

| 变更 | 受影响文件/需求 | 行为及阶段影响 |
|---|---|---|
| 双AI角色与GitHub事实源 | AGENTS/CHARTER/PROGRESS；GOV-007–009、SEC-004 | 本地自查不能记独立审查；空仓库初始化/固定SHA/PR缺项显式披露 |
| 计划预审和固定版本复审 | ROADMAP/ACCEPTANCE；GOV-004–006/008 | 每阶段实施前交计划，测试后交精确SHA，修复新SHA复核；未完成不能申请正常人工验收 |
| 15项审查包与审计模板 | audits/templates/phase-0；QA-006–007 | 模板只是模板；要求实际日志/CI/Golden、缺项及安全权限，不能文字总结冒充证据 |
| 阻断问题与人工权力 | ACCEPTANCE/TESTING/DECISIONS；GOV-005/009 | 严重问题阻断，Medium按金融风险决定，争议保留；验收/合并/发布/下阶段分开授权 |
| 分阶段替换 | ROADMAP/TESTING/TRACEABILITY；FACTOR-011等 | P2不提前回测；P3/P5/P6/P7逐步扩大适用验收，不增加未授权模块 |
| 数据及回测统一契约 | DATA_CONTRACT/BACKTEST_CONTRACT/INTERFACES；DATA/BT | P0设计，P1数据与P5金融自动化证明；profile未知项待批准 |
| OOS和全部试验 | RESEARCH_PROTOCOL；VALID/EXP | 方向参数处理期限预注册，Test不复用，全部候选可追查，多重检验/过拟合风险显式 |
| 需求四级与安全版本 | REQUIREMENTS/TRACEABILITY/ENVIRONMENT；ENV/SEC | 每条具tier/phase/deps，未实现状态明确，锁版本与隔离在对应阶段实现 |
| P0 main稳定发布门禁 | BASELINE/AGENTS/ROADMAP/ACCEPTANCE/PROGRESS/CHANGELOG；GOV-010 | 初始化main和设计PR不代表ACCEPTED/RELEASED；P0发布需批准内容main、固定SHA、phase0-baseline及证据核实；P1未满足条件即BLOCKED，须从核实main独立分支 |

当前无业务代码，因此无运行API迁移/数据库迁移、无回测结果变化，也没有可声称通过的回归测试。后续各阶段必须以批准契约为基线并同步实现测试；未决设计变更需新影响分析。V3.2增加独立审查等待及证据工作，但不授权自动进入Phase1、不建立已验收稳定版本。
