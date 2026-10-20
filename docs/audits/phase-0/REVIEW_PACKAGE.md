# Phase 0 Review Package（计划/架构预审草案）

开发方：GPT Work。日期2026-10-20，Asia/Shanghai。**包状态：REVIEW REQUIRED；main空初始化和草稿PR#1已落实，Gemini记录与正式批准仍缺，不申请正常人工通过。PHASE 1 STATUS = BLOCKED。**

1. **Phase/目标**：仅P0，将V3.0完整需求、V3.1/V3.2和Main Baseline Release Gate形成待审规范；计划见PLAN。
2. **仓库/PR**：用户仓库 <https://github.com/wwooyy429/Alpha-Quant-Research-Platform-AQRP->；草稿PR <https://github.com/wwooyy429/Alpha-Quant-Research-Platform-AQRP-/pull/1>，base=main，未合并。main=e87d0082a5e448e9550129a486ba965f13a155f8为空初始化，默认main；不是稳定设计发布。
3. **完整待审SHA**：由PR#1描述 `AQRP_FIXED_REVIEW_SHA` 字段在最终内容提交后填写完整SHA，必须与明确指定的本轮审查目标一致；在提交外记录避免自引用。`REVIEW_ANCHOR.json`说明当前记录位置，旧04deecc锚点移至history，仅为历史，不是当前目标。Gemini须检出PR描述的完整固定SHA，不能自动审查移动的分支头或GitHub临时测试合并SHA；如未填/不一致则BLOCKED。MANIFEST是该内容快照的文件校验，不代替SHA。正式验收还需Gemini实际签署SHA。
4. **已完成需求**：GOV（新增GOV-010发布门禁）/ARCH/ENV-003/SEC-004/QA-001/005–007的设计资料已编写；106条需求均有设计及阶段映射，业务未实现。
5. **未完成**：所有业务代码/测试Planned；Advanced Deferred，真实交易Unsupported；Gemini预审/独立审查/用户批准未发生。具体比赛/市场profile/环境/阈值等见DECISIONS。
6. **文件清单**：MANIFEST.json（核查工具执行后生成）；修改为新增P0规范、契约、来源、模板、目录说明和文档工具；无src业务实现。
7. **接口及影响**：INTERFACES/DATA_CONTRACT/BACKTEST_CONTRACT为初始提案，无已运行接口迁移。CHANGE_IMPACT列V3.2角色/流程影响。
8. **环境**：本地Windows，Python3.10.11，Git2.47.1.windows.2；用于文档检查。业务环境/依赖锁文件尚无，不声称P1环境验收。
9. **实际测试命令**：`python docs/audits/phase-0/tools/build_catalog.py`生成106条；文档核查实际结果以COMMAND_LOG和SELF_CHECK为准；main/历史/标签/默认分支/PR观察见RELEASE_GATE_AUDIT与GITHUB_GATE_OBSERVATION。未执行业务pytest、回测、网页或安装；不声称它们0失败。
10. **CI**：尚未建立，无run/attempt/job；按V3.0从P1正式代码起建CI。无CI通过声明。
11. **Golden**：GOLDEN_DATASET有公式/中间量/容差候选；文档核查仅复算候选算式，不是业务Golden执行结果或Gemini独立核验。Gemini需核对来源和容差。
12. **已知问题**：ARCHITECTURE_REVIEW、DECISIONS、BASELINE；Gemini与用户批准尚缺，main无获批设计、无phase0-baseline，未RELEASED，P1 BLOCKED。设计参数待批准，历史PIT与执行规则风险未解决。
13. **复现**：读取AGENTS与正式文档→确认P0授权及Git状态→运行编制工具→运行文档核查工具→检查SELF_CHECK/原始命令/manifest→Gemini对最终指定SHA阅读实际文件并填其原报告。该路径只核查文档，不启动业务执行。
14. **重点风险**：原文逐条覆盖、阶段依赖、PIT修订/行动、订单可用时序与逐笔原子账本、Test封存及family、Golden独立性、MVP未删强制项、安全隔离不能靠协议；初始化与正式发布不混淆，标签/main及合并后内容核验门禁完整。
15. **标准批准情况**：用户授权P0设计、空main/建PR并新增发布门禁，明确不是P0验收；未批准具体设计提案/覆盖率/统计阈值或设计合并/发布。ACCEPTANCE/BASELINE供审查；无Gemini通过、用户ACCEPTED及main已核实发布，不得RELEASED或启动P1。

Gemini必须从固定SHA读取原文、全部规范与实际自查工件，不仅依据本文总结。其报告使用templates/DUAL_AI_AUDIT_REPORT，GPT不代填结论；补充测试须安全环境及明确权限。资料变化生成新版本并重新审查。
