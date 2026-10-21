# P3-ISO-OS-1：最终 Test 的单一原生多主体部署提案

对应 WORK-P3-001 / VALID-004/006/008、FACTOR-009、EXP-004。**DESIGN PROPOSED / USER CONFIRMATION AND FIXED-SHA REVIEW REQUIRED**；未部署、未创建账户/服务、未改 ACL。G1须确认方案和责任人；实施验收另须真实权限正负证据。

选定方案：同一受信任主机上的三个不同非管理员 OS 主体 + 管理员保管者，Windows 11 本地 NTFS 为首要可部署目标，Ubuntu24本地文件系统同构验证。研究主体 `aqrp_research`、评估主体 `aqrp_evaluator`、审查主体 `aqrp_auditor`；以实际 SID/UID 校验，名称不是身份。现有11638管理员/账户不得假扮受限研究主体。实际用户SID/UID、路径、可信保管者和批准人需用户确认。G1仅提交方案；操作系统账户、ACL和调度配置另行获得具体部署授权后执行。

可信边界：管理员/root/宿主所有者、评估器已审查代码、制品保管者和审查人可信；不能防管理员读盘、管理员注入进程、审查人主动泄露或恶意内核。研究用户无管理员/备份/调试/提权/切换到其他主体能力，无evaluator凭证，不共享可写Python、环境、PATH、启动配置、temp、工作目录或继承句柄。若当前开发身份保留管理员token，该会话不适用本profile，正式Test拒绝。仅运行完整hash批准的内置因子，**不是任意恶意Python沙箱**。尚未实现的额外隔离不宣称存在。

| 资产（本地非同步盘；禁止放Git、共享盘、公开CI artifact） | 研究主体 | 评估主体 | 审查主体 | 所有者/可信保管者 |
|---|---|---|---|---|
| Train/Validation物理投影：其原始行情、行动、行业/市值/股票池、配置 | R；个人工作目录可写 | R | R | 管理员发布只读投影 |
| Test原始输入/行动/暴露、标签、完整源快照、seed/生成器私参、可重建Test的备份/缓存 | 无读/列目录/遍历/改权 | R | R | 管理员；研究及普通Users不在授权ACL |
| evaluator批准wheel/22锁包wheelhouse/Python/receipt/启动配置 | 无写；公开代码可读副本 | RX | R | 管理员写，部署后不可由研究/评估器改 |
| 候选请求暂存 | 只写自己的暂存，不是真实inbox | 无直接执行 | R | 研究用户；保管者验证后复制至sealed inbox |
| sealed inbox：hash绑定候选/协议/授权、非路径输入、不含脚本 | 无 | R；消费状态另记 | R | 管理员；避免研究者检查后替换TOCTOU |
| 评估temp/缓存、错误/日志、原始结果、控制ledger与预算/污染索引 | 无 | RW | R | 管理员建根，evaluator数据子目录写 |
| released审查结果/评价摘要 | 无，直到用户决定公开且该Test退休 | 只追加到私有结果 | R | evaluator写、审查人只读，管理员控制发布 |
| 开发run ledger/cache | RW | 无需访问 | R（按批准） | 研究用户；不得包含最终Test输入/反馈 |

输入投影必须是保管者创建的独立分片快照及独立manifest，移除Test区间行、跨区间行动/修订及未来曝光，不把完整含Test的P1 Parquet连同路径交研究端再靠where过滤。Train/Validation投影不能包含足以恢复Test的生成seed、私有公式/参数、备份、压缩包、日志、memory dump。已经公开的15组Golden/已知seed合成数据永久标ENGINEERING_DEMO，不能重新标正式独立Test；正式Test必须在协议/candidate冻结后由保管者使用私有新seed生成并封存，泄露即污染并退休该数据身份。即使新UUID/路径也按私有原始manifest内容+保管者登记的holdout lineage判断同一Test。

部署路径示例 `C:\AQRP-Sealed\<evaluation_id>` / `/var/lib/aqrp-sealed/<evaluation_id>` 均是提案，需用户选定真实本地路径和权限拥有者。Windows：管理员创建独立标准账户，独占NTFS目录/禁不安全继承，保存SID、Get-Acl/`icacls /save`及`/verify`输出；Task Scheduler只允许管理员定义的hash批准入口，以evaluator主体非交互执行，研究人没有修改任务/启动任意参数/读取账户凭据权限。Ubuntu：不同非root UID/组，本地owner/mode/ACL及default ACL，保管者专有调度入口以evaluator运行；研究人不在sudo/ptrace/相关组。两OS都关闭不必要网络及凭据注入，不以防火墙替代文件权限。拒绝路径逃逸、reparse/symlink/hardlink替换；只读sealed副本，运行前后重新验manifest/receipt/锁/hash。Windows与Ubuntu各自保存主体命令+token/UID+真实读拒绝及正向执行记录；仅GitHub hosted runner普通同用户测试不能算生产profile已验证。

调度流程：审查人/用户批准exact candidate+protocol+code/data/env，保管者复制不可变请求，单个evaluator串行处理。控制ledger、预算与结果位于私有目录：OS独占文件锁（Windows锁字节/POSIX flock）保护read-check-append，先写一次性访问RESERVED和所有身份、flush/fsync，再运行；预算固定为每个真实Test身份一次，成功/崩溃/取消/重复都不能返还或改名重试。启动恢复先重放校验hash链，RESERVED无终态转FAILED_CONSUMED；有歧义/落盘失败/损坏则禁止评估。全局身份索引由保管者登记原始Test lineage，跨family/protocol/run_id/目录共享污染记录。普通申请失败只回常量REJECTED，不回是否命中某个Test、指标或依赖内容；控制结果和运行时细节只给审查主体。缓存命中也先过权限/预算检查。该文件锁和恢复流程仍Planned，不能把设计当已通过的原子性测试。

实施必须存证：真实研究主体对Test行/完整快照/私有seed/label/cache/report/temp/log/备份/控制ledger均PermissionDenied；无法改批准制品/任务；评估主体正向读取并一次成功；并发双请求仅一条RESERVED；在预留前/后/结果写前后断进程及重启均不增加预算；family/run/路径/参数改名及cache绕过拒绝；泄露或外部反馈标污染拒绝；两OS分别记录。若任一主体/ACL/私有生成或防重建证据缺失则 `UNVERIFIED_ISOLATION`，不执行formal Test，不验收完整VALID-004，不批准ResearchValidated。

依据：[Windows DACL保存/核验与继承](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/icacls)。这是基于权限能力拟定的工程方案，不是本机部署事实；文件ACL本身不覆盖上述管理员信任边界。
