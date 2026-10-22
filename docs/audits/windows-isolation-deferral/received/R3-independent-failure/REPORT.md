# GPT Work 补充审核：Windows 隔离 R3 固定版本复核

**候选结论：REQUEST CHANGES / BLOCKED（代码与验收工具仍有两项 Medium 问题）。整体 Windows 隔离：NOT VERIFIED。** 原 WI-R2-001、WI-R2-002 本轮均不登记完全关闭。新方向确实处理了旧问题的成因，且独立 SDK、输入与证据核验通过；但新门禁存在可复现的漏检，验收探针尚不足以证明完整覆盖。下面的反例使用明确标注的模型适配器，不是本机三主体越权复现。

## A. 对象、权限与版本事实

- PR #7：https://github.com/wwooyy429/Alpha-Quant-Research-Platform-AQRP-/pull/7 。描述锁定及本轮实际检出：**b3d9aef79396db948d326f5ce247131f96739d9d**。起止核对均为 draft/open、未合并，固定 SHA 未漂移。
- base main：0a57dccb5618ba08cd3572d6d6b78fec963a3041；原隔离业务 SHA：9ac5db069287a6e4a095e25ae8c3cc8fa229cded；旧 R2 attempt：e6968f1c-3552-4a98-af61-98a5194dafea。
- 独立工作副本：`C:/Users/11638/AppData/Local/AQRP/reviews/wi-r3-b3d9aef-review`；detached、干净。只在独立副本配置 Git 长路径支持、取得固定对象；旧开发副本未改。
- 本轮输出：本目录。日期2026-10-22，Asia/Shanghai；实际命令含UTC起止、argv、cwd、退出码、stdout/stderr。执行人 GPT Work 补充审核，不冒称 Gemini 或开发方执行。
- 实际运行 Windows 11 build26300、CPython3.13.16 standard GIL x64。最终新 SDK 目录见 SDK_LOCATION.json；测试真实安装新 wheel，不使用开发方 venv。
- 只读/本机工程验证授权：未启用任何账户，未修改真实 ACL、服务或调度；未运行实际正式 Test、未授金融批准、未合并/标签/部署/实盘/P5。模型控制仅在本审核目录创建普通工程文件，用假 ACL 适配器及模拟访问结果，不安装这些 ACL。

版本范围核验：47模块 bundle=`4e657dea368b50b083030dbad32821683735be420f727b1db26ac2ba60e82dd5`；锁=`86c7bf65c9a9690036006360062c8cd10a91279705b4070af7033d7699abffeb`。2,970个受保护旧文件匹配；42个旧Python模块原字节不变，旧模块仅包版本、admission默认版本、evaluator显式新分支有变。P1 snapshot.py、依赖锁、106条需求目录均与基线字节相同，逐项变更清单匹配。没有纳入P4 portfolio/risk代码；这不是 P4 G2 修复复核，P4上轮两项发现不由本报告关闭。main/Phase3标签解引用目标仍为上述base。

## B. 原两项修复候选的判断

| 原发现 | 已独立确认 | 尚未关闭原因 |
|---|---|---|
| WI-R2-001：动态继承与严格门禁不兼容 | 原严格protected路径保留；新策略opt-in，四主体/root/key绑定；闭合ACE集合、OWNER RIGHTS拒改权、operator-owned anchor、逐级父ACE投影、外部可信祖先和新授权binding均有代码/测试；旧无OW形状继续拒绝 | 新全域遍历发生错误时可漏掉后代仍返回成功（R3-001）；实际新profile与三主体before/after尚未执行 |
| WI-R2-002：实际输入审计读取及证据不足 | P1 private mkdtemp/rename未改；operator预建readonly anchor后复制九文件、源目标校验、最后sidecar及消费校验有实现；新九文件已实际独立读取、散列、Parquet核验并运行四因子 | 验收清单/目录探针不足（R3-002）；真实operator发布、auditor读这份已部署输入及全部动态产物未执行。新导出不是旧输入恢复 |

新设计采用创建并复制文件而非移动P1私有目录，方向合理：Windows默认安全描述符在新建对象时继承，重命名/移动本身不会重新赋予该默认描述符。[Microsoft 文件安全文档](https://learn.microsoft.com/en-us/windows/win32/fileio/file-security-and-access-rights)。本轮不能把模型中的复制成功写成实际NTFS角色权限成功。

TrustedInstaller只进入外部祖先信任集合，不作为sealed域owner/额外ACE；本机已实际只读执行 `sc.exe showsid TrustedInstaller`，返回精确SID `S-1-5-80-956008885-3418522649-1831038044-1853292631-2271478464`。该限定符合信任OS维护/管理员的边界，未见扩展为任意service SID；这不是部署批准，也未证明实际新祖先链已通过。

## C. 发现及修复要求

### WORK-WI-R3-001 — Medium / 门禁代码缺陷 / OPEN / 阻断候选放行

固定位置：`src/aqrp/validation/windows_acl.py:142`、`:157`，WindowsTreePolicy.verify 的前后两次 os.walk。

两次遍历均没有 onerror 失败处理。os.walk默认忽略scandir错误，因此“两个已观察集合相同”不能证明集合完整；verify_rows只核对该不完整集合所提供的描述符。参见 [Python 3.13 os.walk 文档](https://docs.python.org/3.13/library/os.html#os.walk)。

独立复现：创建 root/work/unseen.json 三个真实普通文件系统对象，提供符合本profile的模型描述符。正常时verify返回objects=3。只对work的scandir注入PermissionError，使用真实os.walk行为；两次都不列出其后代，verify仍成功返回objects=2，unseen.json确实存在且未接受ACL检查。全部发生在本审核目录，未设置真实ACL、未切换身份。见 `INDEPENDENT_COUNTEREXAMPLES.json` 的 tree_positive/tree_enumeration_error、`independent_counterexamples.py` 和原始日志。

影响：全域证明可能退化为对子集的证明。未证明真实部署中存在某个可读泄漏文件，也未声称绕过了实际NTFS权限；问题是遇到无法完整采集时门禁没有fail closed。对于将来放行整个sealed树，该缺陷必须先修。

最小修复：两次遍历的目录打开/枚举错误均应立即结构化拒绝，保留路径、errno/winerror及失败阶段。不能跳过、重用已采集子集或把空目录与无法读取目录混同。保留对象identity/类型/link/ACL二次捕获校验；补前次与后次遍历分别失败、子树持续报错、暂时消失/I/O错误、正常完整树及集合变化的正负控制。无需改真实ACL或旧失败证据。

### WORK-WI-R3-002 — Medium / 验收工具覆盖缺口 / OPEN / 完整验收前必须补齐

固定位置：`tools/windows_access_probe.py:101–108`、`:110`、`:114–119`、`:148`。

本工具能检查传入对象的访问位与文件字节，但不能自行证明清单完整：只要求9个snapshot_input、至少1个sidecar及非空operator_inventory_sha256；未将该hash与权威清单/对象集合对账。独立模型中，11个真实普通文件（9输入、sidecar、1动态产物）正常控制通过；从after清单删去仍存在的动态文件、保持完整清单hash字段不变，三种模拟角色都仍返回all_pass=true。此结果只能说明“列出的检查通过”，不能用于“全部实际产物覆盖通过”。外层 --sha256 能锁定配置字节，不能证明配置没有漏项；本轮未发现篡改该外层校验的证据。

目录也不能作为完整边界纳入当前检查：auditor模型的目录六个访问打开结果均正确，随后统一path.read_bytes仍报错；工具没有目录类型/列举成员的分支，也未申请FILE_DELETE_CHILD=0x40。该权限与对象自身DELETE=0x10000不同，不能以文件DELETE探针替代。[Microsoft 文件访问位定义](https://learn.microsoft.com/en-us/windows/win32/fileio/file-access-rights-constants)。独立结果在同一JSON的 truncated_inventory/directory_probe 中。

影响与限制：这不是实际三主体越权，也不是说可信operator提供的完整清单必然错误。开发文档要求主审对operator清单交叉核对，方向正确；但当前未交付强制对账/目录控制，且工具输出all_pass没有覆盖资格标识，不能据它关闭原覆盖发现或宣称新验收入口已完整就绪。

修复可以在探针或独立的强制编排/对账阶段完成：以可信operator冻结的、绑定attempt/phase/root及before/after全域结果的权威清单，核对实际九文件、sidecar、全部动态文件和目录边界，验证清单hash与集合相等；漏项、多项、错误hash或不完整遍历必须拒绝。research不应被要求自行枚举私域；它应消费经可信方审定的清单。明确区分listed_checks_pass与coverage_verified，整体验收必须同时满足。目录按类型检查列举/创建子项/删除子项/改权等访问，文件才做字节hash；不可读私钥等对象采用各角色明确期望或另行强制探针。补删一个动态文件、遗漏目录、hash不符、目录类型错误及完整正例。若保留人工对账，应交付明确可重复命令、原始清单和强制验收条件，不能仅依赖文字承诺。

## D. 实际独立执行与证据核验

1. **最终干净SDK：628 passed，0 failed/error/skipped。** 新hash锁安装、真实wheel、静态/格式/包身份、逐模块覆盖、原包环境及旧Ref重放、数据/因子/研究smoke、新输入导出、原数学参考及秘密扫描正负控制均实际完成。标准628包括50项新针对性测试，但模型ACL/假token检查不算真实三主体执行。
2. 首次SDK在旧包重放阶段失败，未到测试汇总。独立追加诊断得到PyArrow _parquet DLL加载“文件名或扩展名太长”；未改源码/锁/系统设置，改用更短的独立非同步输出路径后，从头新建SDK通过。首轮commands/environment、诊断argv及原始stdout/stderr保留。反例最初使用该首轮已安装的新47模块wheel；最终SDK及官方wheel与固定源码的字节身份另独立验证，不把首轮记为成功。
3. **官方CI run39772759502**：Windows job119804113317、Ubuntu job119804112931，均628通过。主审经GitHub连接器重新下载原ZIP，核对官方大小/SHA、CRC、精确成员、逐选择成员hash、JUnit、47模块coverage、wheel/receipt与固定源码字节、P1表分片、研究终态账本/产物及新九文件ZIP。实际临时集成SHA b7ed8fbd6538f3edc3d99d7251cb2d6d3c83628e的tree与固定头相同，父节点为base和固定SHA；实际checkout见官方解码job日志及环境。不是main合并。
   - Windows artifact12423636536：95,598,546 bytes，SHA256 `1a0caa05773cc9bb893792efcb0c53dbb918b5628572518e5ae3c56190775302`，198成员/197选择项。
   - Ubuntu artifact12422952856：136,870,907 bytes，SHA256 `9aeba331abcac4a66ca75bf135631ad7afe7e9d047b0d6277f0a933cd841e799`，197成员/196选择项。
   - 本机最终SDK197选择项也逐项核验。Linux由GitHub runner执行；主审在Windows核验原始字节，不冒称另跑了GPT Work Linux隔离环境。
4. 开发329,420,052-byte完整证据包SHA256=`a27ef6ca5e899cda4baee3a1c212eaafc9555d1566adb41ec613f88597c049fd`，102个清单文件/103成员全部重算hash/CRC；交接各外置文件也核验。完整开发原包保留原位置，主审包不重复嵌套。
5. 新九文件ZIP 16,011 bytes，SHA256=`1391bdd7f75e05d8cdbccf5d641b4398f2c0b5eceac2593f8dae440490f697c7`；精确9成员、P1 manifest/八表SHA、行数、snapshot_id、时间/证券范围及质量计数均独立核验。新snapshot=`wi-r3-public-engineering-20261022`，manifest hash=`edd5bc05cc2ddd29740db95c95270e0c3004217712feb2421234107c2f7c9031`。从Parquet读出价格100/110/121、量100/150/200；以Fraction独立推导Momentum=21/100、Reversal=−21/100、Volume=3/5、PriceVolume=(121/110−1)×3/5=3/50。用新安装wheel实际执行四因子，绝对容差1e-12内通过，工件已封存。此输入未发布到实际三主体目录，auditor读取仍未执行。
6. 原发布66文件逐一独立重算大小/hash，三旧Ref重放完成。原R2包仍与主审旧原包逐字节一致：771,260 bytes、SHA256 `802c216672cef0cc9b922194f4f25f5c8ff45e7c61cb3f7df11b5ce6831f070e`，100清单项；旧184=183PASS/1FAIL及九文件OMISSIONS均未改。旧cb10857f文件没有恢复、读取或替代；旧bd7ebd...hash仍未独立复算。
7. 当前三个旧账户经Get-LocalUser只读复核全部Enabled=false。未对新profile执行真实operator发布/NTFS角色访问/全生命周期；未开启或删除账户、未Set-Acl、未take ownership。已保存的真实token捕获只属于当前用户，不能当成三个受限账户的执行证据。

关键原始记录：`SCOPE_VERIFICATION.json`、`ARCHIVE_VERIFICATION.json`、`NINE_INPUTS_VERIFICATION.json`、`OLD_EVIDENCE_VERIFICATION.json`、`OLD_REF_FILE_VERIFICATION.json`、`INDEPENDENT_COUNTEREXAMPLES.json`、`current-accounts.json`及各步骤command/stdout/stderr。SDK目录内commands.log与environment/JUnit/coverage一并按选择清单封存。官方job日志是连接器解码文本；官方artifact ZIP保留实际下载原字节。

## E. 未验证、责任与后续

代码修复责任：开发Codex；两项新发现须新固定SHA交GPT Work确认。原WI-R2-001/002的最终实际条件由可信operator在用户具体授权后执行：审定新attempt/anchor/运行时/入口/config→预建并核实际输入→完整before gate和真实三主体探针→并发单次/崩溃/恢复/重复→原地不改ACL的after gate与全清单探针→原始证据封存。当前无需重跑管理员脚本，先补候选缺口。

持续NOT VERIFIED：完整Windows隔离、真实三主体全域生命周期、实际独立正式Test、正式金融批准/ResearchValidated、VALID-004全项、完整历史宿主/安装器字节复刻、部署/实盘。受限P3验收及P4上轮状态保持原范围；新包/新代码无用户验收或发布含义。修复后仍须提交新40位SHA、最小变更清单、正负控制、完整SDK/双OS原始证据和失败历史。不得自行改判发现关闭、整体隔离通过或用户已验收。
