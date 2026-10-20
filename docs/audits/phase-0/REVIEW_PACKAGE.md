# Phase 0 Review Package（计划/架构预审草案）

开发方：GPT Work。日期2026-10-20，Asia/Shanghai。**包状态：REVIEW REQUIRED；完整内容提交后另附固定SHA锚点，PR基线及Gemini记录仍缺，不申请正常人工通过。**

1. **Phase/目标**：仅P0，将V3.0完整需求和V3.1/V3.2修订形成待审架构；计划见PLAN。
2. **仓库/PR**：用户仓库 <https://github.com/wwooyy429/Alpha-Quant-Research-Platform-AQRP->；已克隆并核实初始为空，尚无稳定main和PR。D-010需处理；不虚构PR。
3. **完整待审SHA**：内容提交后以本目录 `REVIEW_ANCHOR.json` 补充固定的 `review_content_commit`、tree及manifest哈希（该元数据在后续提交加入，避免文档自引用SHA）。Gemini须读取这个完整内容SHA，不能读取漂移分支头；锚点未生成前不得称固定版本材料齐全。MANIFEST只能核对文件，不能代替Commit。正式最终验收还需记录Gemini实际签署的最终SHA。
4. **已完成需求**：GOV/ARCH/ENV-003/SEC-004/QA-001/005–007的设计资料已编写；其余需求已有设计与阶段映射，未实现。
5. **未完成**：所有业务代码/测试Planned；Advanced Deferred，真实交易Unsupported；Gemini预审/独立审查/用户批准未发生。具体比赛/市场profile/环境/阈值等见DECISIONS。
6. **文件清单**：MANIFEST.json（核查工具执行后生成）；修改为新增P0规范、契约、来源、模板、目录说明和文档工具；无src业务实现。
7. **接口及影响**：INTERFACES/DATA_CONTRACT/BACKTEST_CONTRACT为初始提案，无已运行接口迁移。CHANGE_IMPACT列V3.2角色/流程影响。
8. **环境**：本地Windows，Python3.10.11，Git2.47.1.windows.2；用于文档检查。业务环境/依赖锁文件尚无，不声称P1环境验收。
9. **实际测试命令**：`python docs/audits/phase-0/tools/build_catalog.py`（已生成105条）；文档核查执行后以COMMAND_LOG和SELF_CHECK记录为准。未执行业务pytest、回测、网页或安装；不声称它们0失败。
10. **CI**：尚未建立，无run/attempt/job；按V3.0从P1正式代码起建CI。无CI通过声明。
11. **Golden**：GOLDEN_DATASET有公式/中间量/容差候选；文档核查仅复算候选算式，不是业务Golden执行结果或Gemini独立核验。Gemini需核对来源和容差。
12. **已知问题**：ARCHITECTURE_REVIEW、DECISIONS；Gemini/PR外部前提阻断正常验收，设计参数待批准，历史PIT与执行规则风险未解决。
13. **复现**：读取AGENTS与正式文档→确认P0授权及Git状态→运行编制工具→运行文档核查工具→检查SELF_CHECK/原始命令/manifest→Gemini对最终指定SHA阅读实际文件并填其原报告。该路径只核查文档，不启动业务执行。
14. **重点风险**：原文逐条覆盖、阶段依赖、PIT修订/行动、订单可用时序与逐笔原子账本、Test封存及family、Golden独立性、MVP未删强制项、安全隔离不能靠协议。
15. **标准批准情况**：用户原指令授权P0和V3.2规则，未批准具体设计提案/覆盖率/统计阈值；ACCEPTANCE的P0标准供审查，最终人工验收待独立审查和关键决策闭环。

Gemini必须从固定SHA读取原文、全部规范与实际自查工件，不仅依据本文总结。其报告使用templates/DUAL_AI_AUDIT_REPORT，GPT不代填结论；补充测试须安全环境及明确权限。资料变化生成新版本并重新审查。
