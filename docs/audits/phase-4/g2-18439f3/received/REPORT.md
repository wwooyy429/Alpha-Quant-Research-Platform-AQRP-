# GPT Work 补充审核：Phase4 G2 固定版本

**结论：G2 BLOCKED / REQUEST CHANGES。发现两项阻断问题：WORK-P4-G2-001 High、WORK-P4-G2-002 Medium，均 OPEN。** 七项工程能力有实际实现，常规验证和原始证据总体充分，但不能将 799 项通过或 G1 PLAN PASS 替代下述缺陷闭环。未修改源码、测试、Golden、依赖、状态或原审查件；未提交/推送/修改 PR。

## A. 对象、权限与方法

- 仓库：wwooyy429/Alpha-Quant-Research-Platform-AQRP-；PR #6，当前 draft/open，未合并。
- PR 描述 AQRP_FIXED_REVIEW_SHA 与用户给定值一致：**18439f31536295aea42e57e566d07cce345a35cf**。
- G1：265af16353d85ce8c2d229a7517809d707498da8；已验证业务源：b3be62439d8d0877478b7105d68863fcb2a108a0。
- P3/main 基线：0a57dccb5618ba08cd3572d6d6b78fec963a3041。远端 main、phase3-baseline、v0.3.0 的解引用目标已只读核对。
- 审核日期：2026-10-22，Asia/Shanghai；每条实际命令另含 UTC 起止。
- 独立副本：`C:/Users/11638/AppData/Local/AQRP/reviews/p4-g2-18439f3-review`，detached HEAD 固定上述完整 SHA，开始时干净。克隆复用已有只读 Git 对象，新增对象向官方仓库获取；未修改旧副本。
- 独立输出：本目录。实际解释器 CPython 3.13.16 standard GIL x64；本机 Windows 11；干净 SDK 使用新 venv、哈希安装及真实 wheel，未使用开发方 venv。准确路径和安装环境见 SDK environment.json 与各 *.command.json。
- 已读取 AGENTS、基础架构/接口/数据/回测/需求/追踪/验收约定、G1 方案及反例、实施授权/映射/说明/身份/冻结输入/审查包，以及新增八个 portfolio/risk 模块和相关测试。没有启动子代理。

## B. 授权、版本与范围

原106项目录未改，本阶段仍7项（4 MVP、3 Competition Ready），无优化器、外部插件/DAG、撮合、账户账本或 UI 范围扩张。实施授权单独存证，旧计划轮授权/状态仅按历史解释，不重复要求实施许可。G1 两项的 CLOSED_DESIGN 保留，本报告评价新实现，不把设计结论改写为运行时通过。

独立逐项核对：3,130 个受保护旧文件、7 个冻结输入/答案清单项匹配；450 个 P4 FILE_MANIFEST 成员匹配。45 个旧 Python 模块中43个与 P3基线 Git blob 字节一致，另外两处仅包版本和默认因子版本元数据，admission 的 1.1.0→1.2.0 单字面值差异已独立比较。旧精确 Ref/旧 wheel 和工件未覆盖；数学公式及锁不变。

53模块 bundle：`3cac05089e64c420b128496d98748879ec553f2d97f66a0474c718365e8a2f41`；锁：`86c7bf65c9a9690036006360062c8cd10a91279705b4070af7033d7699abffeb`。审查 SHA 相对业务 b3 的差异没有 src/tests/tools/CI/构建/锁/扫描配置变更。新 receipt 标明开发方工程准入，未冒称 GPT Work G2 已通过。

正式入口 financial policy=NONE 的拒绝负控制返回 APPROVAL_REQUIRED，无工程自动回退。本次仅合成工程数据和负控制，没有实际正式 Test、金融批准、账户/ACL/服务/调度变更、实盘、合并、标签、部署或 P5。

## C. 发现及最小修复要求

### WORK-P4-G2-001 — High / 代码缺陷 / OPEN / 阻断

关联：PORT-001/002、RISK-003/004，并影响发布目标的风险与资金一致性。

位置：`src/aqrp/portfolio/contracts.py:82`（尤其85–87）；`src/aqrp/risk/checks.py:168`；`src/aqrp/portfolio/service.py:70`。

输入是当前 parser 明确接受的有限 Decimal 字符串：权益与现金 `1e35`，零原仓，两证券价格均1、lot均3，LongOnly score、top_k=1，A分数3、B分数1，其余冻结 base 约束保持。`1e35` 只有一个有效数字，指数35在现有允许范围内，不是非法 NaN/超长字符串。

精确算术：A理想数量=10^35，向零整手应为10^35−1，现金=1；正确目标及delta均可被3整除。内部 Fraction 风险检查通过后，通用 project 又用34位 HALF_EVEN 将该35位整数舍入成10^35，服务直接发布其结果，仍为 SUCCEEDED、risk.passed=true。发布的 target/delta 数量除3余1；按发布字节复算 cash+市值−equity=1 CCY，超过1e-8资金容差。预期是精确发布实际通过风险检查的数量，或在无法按输出契约无损表示时结构化拒绝，不能成功返回另一份未验证目标。

实际坏例 run_id：`302558c7-a597-4f45-9d52-bbc33e0bb9c4`；1e40坏例也复现。正常对照1e3与1e34均成功、整手且权益误差0。见 `ADVERSARIAL_RESULTS.json`、`adversarial.stdout.log`、`adversarial-runs/<run_id>/` 原请求、candidate、risk、result 和终态清单。

影响：风险检查针对内部精确数量，调用者得到的目标和建议却是舍入后的另一组数量。ENGINEERING_TEST_ONLY 不消除本阶段要求的精确lot及资金不变量；这不是要求更大真实账户范围，也不能以普通金额用例/覆盖率通过豁免。

修复：区分近似展示的比率/理想数值与必须精确的最终数量、delta及金额；可无损序列化最终有限十进制，或明确限制并拒绝无法表示的计算结果。必须从最终持久化/返回字节重新验证目标与delta整手、现金/权益、必要资金及风险一致性。不要放大容差、只修改显示或增加“已验证”标记。增加34位边界及跨界、正负数量、非10幂lot、极端价格/数量的服务级回归，保留普通输入成功对照和失败 ledger。新 bundle/receipt 须重新审查。

### WORK-P4-G2-002 — Medium / 输入血缘与测试缺口 / OPEN / 阻断

关联：PORT-001、RISK-004；依据 G1 INTERFACE_DRAFT 的统一父快照/版本及真实 P3 原工件绑定要求。

位置：`src/aqrp/portfolio/research_input.py:62`（62–73检查字段）；`src/aqrp/portfolio/contracts.py:176`附近 envelope 同 context 校验；`src/aqrp/portfolio/service.py:77` 发布该 context。

正向控制：使用原封存 P3 成功运行 `0c902a7a-6e21-4003-9e18-365bf8bc3b68`，bind final momentum 原字节，原数据快照 ID=`9e3a5971-d66e-4aee-bdb4-1082c6907e02`，hash=`0367ceacfd8df9feea752858dd93c2fca0a10bd9fa7bc442f2c43e57a2707004`，完整服务成功。

负向控制：只把本次 context 和各 envelope 的 snapshot_id 一致改成另一合法 UUID `00000000-0000-4000-8000-000000000001`，保留原 P3 run/stage/manifest、原数据 hash 与全部原分数，按公开请求格式重算 envelope/fixture hashes。服务仍 SUCCEEDED，输出 target.context 宣称新 ID 与原数据 hash 属同一快照。

实际坏例 run_id=`880b2e74-2bbc-4321-b058-301fb40ae0b2`。本次另独立核验原 P1 manifest 和八个表文件 hash，确认实际源仍为原 ID，见 `PARENT_BINDING_PROOF.json`、`original-p3-snapshot-manifest.json`、`parent-binding-runs/`。该负例不能用 UUID 格式校验解决；原自测仅检查修改单份 envelope 的 context 或改 snapshot_sha256，未覆盖整份请求一致错误的真实来源 ID。

根因：_projection 对比真实 lineage.data_hash，却未绑定 context.snapshot_id 与实际源 SnapshotRef。P1 外层 manifest_digest 按既有设计排除 snapshot_id，故不能把外层hash相同自动当作已验证 ID 对应关系；真实表文件与其ID一致性须按原契约验证。没有观察到原分数篡改、不同数据表被混入、未来数据泄漏或正式批准绕过，不作这些扩大结论。

修复：绑定并核实实际 SnapshotRef/manifest及表内ID与原研究源的对应关系，拒绝错误父 ID。若确需独立“投影 ID”，应使用明确分开的字段和血缘，保留经验证的真实 source snapshot ID，不能把投影名称混写为原父快照。新绑定须进入冻结请求/工件哈希；覆盖原合法来源、错误但合法UUID、ID/hash交叉混配、整份请求一致改写及只改单 envelope 等正负例。不能关闭真实来源绑定、降级成 DECLARED_FIXTURE 或重算原 P3 工件规避。无需改写旧 P3 工件。

## D. 七项需求 → 实现 → 测试 → 证据

| ID / 等级 | 实现与实际覆盖 | 本轮处置 |
|---|---|---|
| PORT-001 / MVP | contracts/construct/service/research_input；真实P3终态输入、不可变请求/输出、目标和不可执行建议；test_contracts/test_research_input；独立服务与父快照探针 | 真实路径存在；001/002阻断完整通过 |
| PORT-002 / MVP | weights；单/多因子固定系数、共同有效交集、等权/score、LongOnly、并列/现金/整手；test_construct及独立2–6资产样本 | 常规算术已验证；最终数量表示受001影响 |
| PORT-003 / Competition Ready | 真正双腿、G/N预算、中心化分数、空腿/重叠拒绝；资金/short冻结/额外保证金；真实完整服务与性质测试 | 常规及资金拒绝通过；最终输出统一受001影响 |
| RISK-001 / MVP | checks pre/post 单票/gross/net/leverage/双边及半额turnover；x04 .6→1.1、限额等号/容差边界 | 已验证常规门禁；不能替代发布字节一致性 |
| RISK-002 / Competition Ready | PIT 行业净/总暴露和 signed Beta；缺暴露/重复/未来拒绝；x03 0→−.5、独立多行业样本 | 常规完整服务及取整后复检通过 |
| RISK-003 / Competition Ready | 目标/delta分别lot、不动/全平/跨0、tradable、sellable、short/borrow总额度；13项局部矩阵及服务用例 | 原G1普通反例正确；001揭示序列化后失效，阻断 |
| RISK-004 / MVP | check_target重新构建及原candidate字节比对；任何风险失败无target；失败/终态账本及原结果重放 | 常规防篡改及失败存证通过；001/002仍可成功返回不合契约结果 |

测试组织集中在 tests/portfolio，并无 tests/risk 目录；实际测试函数已覆盖 risk/checks，不能按拟定目录名误报未实现。未来订单接线仍属P5，不要求提前实现。正式ResearchValidated依赖未满足时保持拒绝，受限工程路径不能冒充金融批准。

## E. 实际执行、原始证据与限制

1. **GPT Work新干净SDK：799 passed，0 failed/error/skipped**。哈希安装→固定Git归档→真实wheel→静态/格式/包校验→旧Ref实际重放→全部测试/覆盖→数据、因子、研究、组合smoke→原P3参考脚本→固定扫描及正负控制，全部完成。SDK环境complete=true、dirty=false、code_commit等于固定审查SHA。
2. 独立 `independent_reference.py` 仅stdlib Fraction，不导入AQRP或调用产品生成期望。通过已安装wheel运行174个完整服务案例：6个冻结输入、160个确定性2–6证券/单双因子/正负系数/两种模式/旧仓/许可/风险组合、8个明确Golden族场景；所有已比对状态、排名、pre/post指标及失败代码匹配。另23个时间/候选篡改负控制通过。随机域属中小数值，后续专门的高数量探针才暴露001，不把174组通过外推整个数值域。
3. 原20项（旧16+4）、原主审四项、原91数学、原三扫描控制在新wheel重执行通过。脚本原字节及历史硬编码SHA/身份保留，由 LEGACY_REEXECUTION.json 和新命令记录绑定真实当前执行身份；这些计数与SDK可能重叠，不相加。
4. 官方最终 CI run39767677018：Windows job119787073393、Ubuntu job119787073718，均799通过。主审通过GitHub连接器重新下载两份官方原ZIP；独立重算官方大小/digest、完整CRC、精确成员集合、每项选择hash、JUnit/覆盖、53模块wheel与固定源码逐字节相同、P1表manifest/分片hash、P3及组合终态事件链/产物、三旧Ref答案、六组合案例和正式拒绝负控制。
   - Windows artifact12420583496：95,677,867 bytes；SHA256 `822615a76897a5932caa683513595adaddffd838c242d4083956eafca6c85ce9`；248成员/247清单项。
   - Ubuntu artifact12420714006：136,949,682 bytes；SHA256 `0a95a836d282ad2cec28087e4dffcd90c4f0b044592c8d988acf7d299ebbf7b4`；247成员/246清单项。
   - 实际PR临时集成提交 b79f2bd4aff65971bb2f65797cb3e47a5494f2cf 的父提交为P3 main与固定审查SHA，tree与固定审查SHA一致；官方job日志和Git对象均核验。不是main合并。Ubuntu执行者是GitHub runner，本机审核原始字节，不冒称GPT Work已在Linux另跑一遍。
5. 开发交接ZIP 332,323,047 bytes，SHA256 `9bed16392eea721e7036e362f23ca0191f341691e8ebe10c8ac46e29d12f6947`，490个manifest文件/491成员，全部重算hash/CRC；内含官方ZIP与本次独立下载字节一致。原完整文件保留原位置，见 DEVELOPER_ARCHIVE_VERIFICATION.json；本封存包不再重复嵌套这份332MB包。
6. 三套验证的53模块覆盖存在；portfolio/contracts行98.91%/分支97.79%，risk/checks行与分支100%。这些数字仍未覆盖001/002的关键不变量，不能据此关闭发现。
7. 两个缺陷的原请求、计算候选、风险结果、返回结果/终态账本均保存在独立目录；未迎合实现改Golden。共有6个首轮定向探针和1个合法UUID补充负例，不能把它们记为“7个通过”，其观察支持两项 OPEN。

实际命令：run_capture.py保存每个步骤的argv、cwd、UTC起止、退出码和原始stdout/stderr；其中 clean-sdk、independent-behavior、adversarial、parent-binding、legacy-wrapper、evidence、developer-archive、scope均有各自command.json。SDK内 commands.log 保留子步骤原命令。Git源身份/只读命令见 SCOPE_VERIFICATION.json；目录权限及当前身份见 REVIEW_EXECUTION.json。

审核过程故障如实保留：首次检出因Windows长路径失败，启用仅本独立仓库core.longpaths后完成固定检出；初版原始包核验器错误地把snapshot_id纳入P1外层manifest哈希，按既有源码契约修正后通过。前次命令、脚本与失败日志单独保留，没有改产品或原证据以消除失败。

**NOT VERIFIED / 延期继续保留：**完整真实隔离，正式最终Test，金融标准/金融批准/正式ResearchValidated，完整历史宿主/安装器逐字节复刻，真实供应商/市场/账户/部署，P5撮合账本与真实订单接线。本次没有重跑或关闭Windows WI-R2-001/002，旧业务中相关模块保持原字节。已验证的是包/锁/旧Ref执行与原结果完整性重放；登记哈希不等于系统权限隔离或数据真实性签名。

## F. 开发修复与复核条件

请开发Codex修复001和002，保留既有G1正确答案、P0冻结契约、旧Ref/原审计和失败历史；增加针对最终返回/落盘字节及真实父快照绑定的回归。重新审查全bundle及工程receipt，从干净固定版本执行适用SDK、双OS、原始ZIP与新增反例验证，完整保留失败与环境记录。完成后提交新40位固定SHA、变更范围、原始日志和封存证据，仍由GPT Work确认关闭，不能自行改判G2通过。

本轮证据充分支持“发现阻断问题”，不是因缺执行权限而无法给结论。G1 PLAN PASS 保持设计范围；G2未通过，P4尚不具备无阻断实现验收条件。用户验收、合并、标签、部署及下一阶段各自需独立授权；本报告不授予上述权限。

封存说明：GitHub job 日志为连接器返回的解码文本；两份官方 artifact ZIP 保留实际下载原字节。独立证据包包含本轮日志/脚本/固定源码参考、全部独立服务运行产物、官方原ZIP及本地SDK完整upload-selection集合；不含venv、源码展开副本、缓存/临时测试目录及开发方332MB外部原包，排除项与引用hash在封存manifest中明列。
