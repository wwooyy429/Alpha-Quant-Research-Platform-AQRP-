# Phase 0 Review Package（计划/架构预审草案）

开发方：GPT Work。日期2026-10-20，Asia/Shanghai。**包状态：REVIEW REQUIRED；已取得Gemini对固定设计SHA的PASS WITH CONDITIONS原报告，条件/管理资料差异及人工批准/发布仍未闭环。PHASE 1 STATUS = BLOCKED。**

1. **Phase/目标**：仅P0，将V3.0完整需求、V3.1/V3.2和Main Baseline Release Gate形成待审规范；计划见PLAN。
2. **仓库/PR**：用户仓库 <https://github.com/wwooyy429/Alpha-Quant-Research-Platform-AQRP->；草稿PR <https://github.com/wwooyy429/Alpha-Quant-Research-Platform-AQRP-/pull/1>，base=main，未合并。main=e87d0082a5e448e9550129a486ba965f13a155f8为空初始化，默认main；不是稳定设计发布。
3. **已审设计SHA**：Gemini原报告明确head为 `ed6666985bfac8cc94fa302c72e2e6333c679a6f`，base为e87d0082a5e448e9550129a486ba965f13a155f8；与PR#1字段AQRP_FIXED_REVIEW_SHA一致并保持锁定。新PR头只增加报告/状态/证据处理，不自动继承已审结论；差异应另行核对。原报告在gemini目录，EVIDENCE_INDEX记录来源hash；旧04deecc锚点仅历史。禁止用移动分支头/临时合并SHA替代原报告目标，最终发布仍须按条件核对main。
4. **已完成需求**：GOV（新增GOV-010发布门禁）/ARCH/ENV-003/SEC-004/QA-001/005–007的设计资料已编写；106条需求均有设计及阶段映射，业务未实现。
5. **未完成**：所有业务代码/测试Planned；Advanced Deferred，真实交易Unsupported；Gemini已完成上述设计SHA的有条件审查，但F-001发布门禁、报告澄清、后续管理资料差异、用户批准及最终main复核未闭环。具体比赛/市场profile/环境/阈值等见DECISIONS。
6. **文件清单**：MANIFEST.json（核查工具执行后生成）；修改为新增P0规范、契约、来源、模板、目录说明和文档工具；无src业务实现。
7. **接口及影响**：INTERFACES/DATA_CONTRACT/BACKTEST_CONTRACT为初始提案，无已运行接口迁移。CHANGE_IMPACT列V3.2角色/流程影响。
8. **环境**：本地Windows，Python3.10.11，Git2.47.1.windows.2；用于文档检查。业务环境/依赖锁文件尚无，不声称P1环境验收。
9. **实际测试命令**：`python docs/audits/phase-0/tools/build_catalog.py`生成106条；文档核查实际结果以COMMAND_LOG和SELF_CHECK为准；main/历史/标签/默认分支/PR观察见RELEASE_GATE_AUDIT与GITHUB_GATE_OBSERVATION。未执行业务pytest、回测、网页或安装；不声称它们0失败。
10. **CI**：尚未建立，无run/attempt/job；按V3.0从P1正式代码起建CI。无CI通过声明。
11. **Golden**：文档自查仅为开发方算式复核。Gemini原报告声明独立计算两组IC和一个资金算式；原脚本/输出未附，Pearson以舍入值及±1e-4核对，不能据此宣称项目1e-8/1e-12容差及全部边界/性质案例已获核验；详见DEVELOPER_RESPONSE。业务Golden仍按阶段实现。
12. **已知问题**：原报告F-001–004保留原严重度及状态，开发方处理意见见gemini/DEVELOPER_RESPONSE；报告需求编号/脚本路径/容差待Gemini澄清。main无获批设计、无phase0-baseline，未RELEASED，P1 BLOCKED。设计参数及用户验收待批准，历史PIT与执行规则风险仍待实施核验。
13. **复现**：读取AGENTS与正式文档→确认P0授权及Git状态→运行编制工具→运行文档核查工具→检查SELF_CHECK/原始命令/manifest→Gemini对最终指定SHA阅读实际文件并填其原报告。该路径只核查文档，不启动业务执行。
14. **重点风险**：原文逐条覆盖、阶段依赖、PIT修订/行动、订单可用时序与逐笔原子账本、Test封存及family、Golden独立性、MVP未删强制项、安全隔离不能靠协议；初始化与正式发布不混淆，标签/main及合并后内容核验门禁完整。
15. **标准批准情况**：用户授权P0设计、空main/建PR并新增发布门禁，明确不是P0验收；提供Gemini原报告也不构成用户验收/设计合并/发布授权。已有Gemini PASS WITH CONDITIONS仍须处理条件，不可跳过用户ACCEPTED、main稳定发布及最终复核；当前不得RELEASED或启动P1。

Gemini必须从固定SHA读取原文、全部规范与实际自查工件，不仅依据本文总结。其报告使用templates/DUAL_AI_AUDIT_REPORT，GPT不代填结论；补充测试须安全环境及明确权限。资料变化生成新版本并重新审查。
