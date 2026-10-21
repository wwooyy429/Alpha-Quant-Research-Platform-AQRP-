# G1当前设计决定与独立复核范围

GPT Work固定e26：PLAN BLOCKED；003/004仅设计CLOSED，001/002/005 OPEN。报告不覆盖ff4；当前新SHA另审，不能仅因内容延续宣布整体PASS。

| 项目 | 当前设计 / 证据 | 剩余条件 |
|---|---|---|
| P3-D01 | 合成/PIT侧车/原8表不变 | 实施后完整性/PIT/需求验收 |
| P3-D02 / 001 | TEST_ISOLATION_PROFILE+USER_DECISIONS U-001为具体账户/路径/保管/权限候选 | 用户明确确认方案/责任主体，实际部署另授权；真实SID/UID/ACL及双OS负例仍NOT VERIFIED，formal fail closed |
| P3-D03 | 正式样本/阈值/金融预算等D-004未获批准 | 用户协议与实际证据；不能用显著p自动ResearchValidated |
| P3-D04 / 002 | SYNTHETIC_V1_LABEL_1及新label_visibility_v2完整输入；原15/28正确答案不改 | U-002经济口径确认、完整输入主审复核；不是已执行P1真实快照/权限测试 |
| P3-D04 / 005 | 固定q通用formal候选已撤回，改P3-HAC-GROWING-MDEP-2；q=max(h-1,m0,floor(N^(1/5)))，预定N，受限有界平稳m-dependent及定理/CLT特化 | 主审核方法与能力边界，具体过程依赖论证/正式protocol与真实隔离；有限N误差没有校准保证，不自签关闭 |
| P3-D05 | 既有22包NumPy+stdlib有限方法，不安装新包 | 若新增库另列精确版本/hash/双OS方案；原架构未来库能力不删除 |
| P3-D06 / 004 | REPRODUCTION_PROFILE原wheel独立env/原Ref方案在e26设计CLOSED，文件不改 | G2完整EnvironmentArchiveRef、原三Ref真实路由重放/负例；不能全Unsupported称通过 |
| P3-D07 / 003 | COMPOSITE_RESEARCH固定合成/冗余设计在e26 CLOSED，文件不改；26项23MVP+3CR保持 | 未来真实研究服务/报告/ledger/INT001验收，不是P4账户组合 |

具体设计确认不等于部署执行或金融批准；当前仍未G1放行，不进入业务实现/合并/标签/P4。历史主审分工及报告真实身份保持。
