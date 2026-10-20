# Phase1实施前Review Package

本包由开发方准备，**PLAN REVIEW REQUIRED**；用户已授权P1及合成范围/Python版本，Gemini尚未预审。不得把文档准备当成数据模块已实现。

1. **Phase/目标**：P1合成数据与通用数据契约、PIT、快照/存储、环境/CI及安全测试。详见PLAN.md。
2. **仓库/PR**：https://github.com/wwooyy429/Alpha-Quant-Research-Platform-AQRP-；在本功能分支提交后建立草稿PR。实际URL由PR及外部Gemini指令给出，不能填造编号。
3. **固定版本**：从main 502c6931dcfce50bee2f71a80524475fae6396bf创建feature/phase-1-data-system；P0发布标签固定7de1d0e81385ae97f98ea673fe05dd726f0b577b。预审精确SHA以新PR描述AQRP_FIXED_REVIEW_SHA为准，不审漂移head。
4. **已完成**：仅启动授权登记、14项P1需求计划映射、接口/Golden候选/环境与CI方案及只读元数据调查；业务需求尚未实现。
5. **未完成**：全部P1代码/锁文件/安装/业务测试/CI及Gemini计划预审；P2–7和真实源接入不在当前范围。
6. **文件清单**：本包MANIFEST.json及Git diff；P0原报告/已批CSV/核心契约保持原字节，稳定标签不动。
7. **接口**：DATA_IMPLEMENTATION_SPEC.md对P1实现细化，保持P0data/1.0.0及Data API边界；存在冲突时先做变更影响审批。
8. **环境**：用户批准CPython3.13.16；尚未安装。Python3.10.11只运行文档/元数据工具。DEPENDENCY_CANDIDATES是版本候选和公开wheel哈希，不是完整lock或兼容证明。
9. **实际检查**：本次只有文档计划结构/14项覆盖/基线一致/本地链接/预期算式参考核查；命令与结果见COMMAND_LOG.txt、SELF_CHECK.json。未运行业务pytest或安装，不填业务通过数字。
10. **CI**：未创建/未运行；M1.1正式代码同步建立。没有run/attempt/job或CI PASS。
11. **Golden**：GOLDEN_REFERENCE.md为开发方独立手算候选；未调用待测包，无已签署独立执行/业务测试结果，需Gemini核对后冻结。
12. **已知阻断与风险**：Gemini计划预审未取得；运行环境/锁和CI尚未实现；F-004物理云同步隔离未完成；真实市场/源另行确定。无权限或未核查项须标NOT VERIFIED，不能扩大已有Gate结论。
13. **复现**：读取固定SHA的AGENTS、基线及本包各文档→核对14条P1 CSV映射→复算小型Golden/边界→检查环境主源及wheel元数据→填写独立计划审查报告；不需要运行尚未存在的src。
14. **重点审查**：双时间过滤顺序、晚到修订/区间、DST/微秒、RAW与研究行动视图、重复/缺失语义、快照hash自引用、不可变读写边界、跨平台类型/锁、安全及不提前开发后续模块。
15. **标准批准情况**：P0契约/阶段边界已通过；用户明确授权P1并选合成范围、Python3.13.16。本文具体接口细化、Golden及执行标准需Gemini预审，若产生设计变更按影响另行审批，不伪称所有候选已获独立确认。

本次没有Gemini可调用连接，沿用人工传递原始报告流程。PR及固定SHA准备好后向用户交付审查指令；收到原报告后逐项处理阻断，再开展已授权P1业务实现，不重复请求已有启动授权。
