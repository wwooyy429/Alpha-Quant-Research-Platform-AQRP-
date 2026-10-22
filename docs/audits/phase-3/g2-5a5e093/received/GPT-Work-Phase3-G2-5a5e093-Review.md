# AQRP Phase 3 固定SHA实现主审（G2）

固定完整SHA：**5a5e093c2e9b39abe1332e49d1df40d20f9fd33f**。本次从PR #5描述读取AQRP_FIXED_REVIEW_SHA并记录，独立副本detach检出该版本。

**最终技术建议：REQUEST CHANGES / IMPLEMENTATION BLOCKED。**
新增3项实现发现：1 High、2 Medium，均待修复；审查方新增4个回归用例全部失败。开发方原564项、双OS CI及本轮干净SDK通过属实，但不足以关闭这些新反例。G1 PLAN PASS及U-001/U-002设计批准保持有效，本结论不追溯否定计划通过。

本轮不修改业务源码/测试/旧审计/Golden，不合并、不标签、不部署、不进入P4。审查产物和公开测试输入写在独立审查目录。无真实独立Test、金融批准或用户阶段验收。

**A · 固定范围与完整性**

[PR #5](https://github.com/wwooyy429/Alpha-Quant-Research-Platform-AQRP-/pull/5)起止描述锁值、head及独立检出版本均为上述SHA，未审漂移HEAD。PR仍open/未合并；收尾UTC为2026-10-22T04:29:11.906392+00:00，独立副本和开发方工作副本均干净。main与phase2-baseline/v0.2.0解析后仍为P2基线f26255fc40a3080bfa883ad64938f60036a14759；附注标签对象与其提交分开记录。原G1设计SHA为3861ef1637bc2b4c28725d7afc5f2e1f02242e80。

canonical仍106条/16个ID前缀组、26项phase3=23 MVP+3 Competition Ready。原需求CSV SHA256为20dd4e6be7188d3121f3cb361faf8901bc91815a6e9752beb14054a12183f0c1，和G1原件字节相同。开发方1957项冻结资产与323项本轮审计清单均独立核bytes/hash通过；原15/28/17组与growth输入、参考脚本均未静默修改。

整个45模块bundle、receipt、lock逐字节核对。代码bundle=a1e52e1744d604976f1ebfdd4275bf02b4ff8a1927c73972f72cc4b284623ce4，requirements.lock=86c7bf65c9a9690036006360062c8cd10a91279705b4070af7033d7699abffeb。最终提交与业务07e7c88745c031feeaee5d1e374a02caada77777的src/tests/tools/workflow/pyproject/锁字节完全相同；最终新增扫描配置例外另行独立验证，没有用旧业务CI外推替代本轮执行。

静态审核读取新增研究/验证/实验/服务代码及原模块差异，结合完整源码清单、原已审未变模块的hash连续性和安装wheel核验。版本为0.3.0候选，原三公式/API保持，新1.1.0默认Ref绑定新bundle；旧精确Ref实际在原0.2.0 wheel独立环境重放，不把旧receipt贴给新代码。新增运行依赖packaging26.3已在原锁，不是安装未锁新库。无P4持仓/风险、P5撮合账本、P6网页或任意DAG/外部插件扩张。

**B · 新发现、实际位置与可复现证据**

**WORK-P3-IMPL-001 · High · OPEN / BLOCKING G2。label_available_at遗漏决定标签资格的证券主档修订。**

位置：[src/aqrp/validation/labels.py:186](https://github.com/wwooyy429/Alpha-Quant-Research-Platform-AQRP-/blob/5a5e093c2e9b39abe1332e49d1df40d20f9fd33f/src/aqrp/validation/labels.py#L186)。关联需求：VALID-001, VALID-002, VALID-003, QA-004, INT-001。

依据：make_labels按evaluation_cutoff选择security_master并以listing/delisting判断资格，但deps未包含该已选security记录，available_at与dependency_hash遗漏这项因果依赖。

实际反例：有效P1快照：旧主档称2024-01-04 08:00退市；1月5日00:00才可见的revision2撤销该记录。1月4日cutoff标签无效，1月5日cutoff标签变为0.1，程序却标available_at=1月4日12:05。实际调用purged_train(fit_cutoff=1月4日12:10)会把该后来才有效标签纳入train。

应有行为：标签最早可用时间不得早于1月5日00:00；同一fit cutoff须拒绝/使用当时版本，选中主档版本进入依赖hash/血缘。

处置：把所有实际决定资格/单位的已选主档依赖纳入deps/label_available_at和版本血缘；审计其他元数据依赖，增加晚到上市/退市更正、fit截止及purge回归，不改变旧正确Golden。

原始证据：late-master-causal-results.json, fit-leak-results.json, reviewer-regressions.xml, test_review_regressions.py。

**WORK-P3-IMPL-002 · Medium · OPEN / BLOCKING G2。终态manifest未包含的审批文件仍可用于ResearchValidated签封。**

位置：[src/aqrp/validation/approvals.py:125](https://github.com/wwooyy429/Alpha-Quant-Research-Platform-AQRP-/blob/5a5e093c2e9b39abe1332e49d1df40d20f9fd33f/src/aqrp/validation/approvals.py#L125)。关联需求：FACTOR-009, VALID-008, EXP-001, EXP-004。

依据：ledger.verify只校验manifest列出的文件；record_decision随后读取固定路径approvals.json却不要求它在该manifest中。

实际反例：结束一个原manifest仅含config/lineage的公开测试run；缺approvals时正确拒绝。随后直接在测试目录添加未列入manifest的approvals.json，verify仍通过，record_decision接受测试签封并返回ResearchValidated。

应有行为：审批proposal必须来自终态manifest已列出且原字节hash相符的approvals.json；新增文件不能倒填原运行证据。

处置：从verify返回的manifest定位并校验approvals条目后再读取/匹配proposal；考虑对不允许的额外工件检测或明确扩展策略，检查签封与读取的一致性；保留原终态无文件和后补文件两个负例。

复现范围：使用审查方公开临时ledger和合成测试key；未绕过真实OS权限、未伪造真实人工签名、没有实际金融批准。当前服务正常成功路径会先写approvals；本反例针对导入/受损/后改运行的证据完整性保证。

原始证据：adversarial-results.json, reviewer-regressions.xml, test_review_regressions.py。

**WORK-P3-IMPL-003 · Medium · OPEN / BLOCKING G2。compose只对齐session/stage，未拒绝未来或混合decision cutoff输入。**

位置：[src/aqrp/research/pipeline.py:206](https://github.com/wwooyy429/Alpha-Quant-Research-Platform-AQRP-/blob/5a5e093c2e9b39abe1332e49d1df40d20f9fd33f/src/aqrp/research/pipeline.py#L206)。关联需求：RESEARCH-007, QA-004, INT-001。

依据：G1 COMPOSITE_RESEARCH要求统一可见cutoff和拒绝未来available。公开compose函数只验证stage并按session pivot，忽略提供的decision_time/available_at。

实际反例：同一2024-01-04 session的a/b三证券输入；b.available_at改为1月5日，或b.decision_time改为1月5日，均照常生成三条1月4日合成分数。正常同刻输入控制也通过。

应有行为：合成前统一时点并验证available_at<=共同decision_time；不同时点/未来输入明确拒绝，输出保留对应血缘。

处置：在compose入口及公共stage契约中校验共同cutoff和可见性，明确缺必需时点的策略；保留两个负例及正常交集/重新z/方向控制，不删时点字段来绕过校验。

复现范围：已复现于公开SDK compose入口。统一research服务当前产生的同一decision网格受上游pipeline校验；未声称普通成功服务请求已经触发该未来输入。

原始证据：adversarial-results.json, reviewer-regressions.xml, test_review_regressions.py。

001同时已实际调用purged_train证明影响：fit_cutoff=2024-01-04T12:10Z，旧标签train_count=0，而用1月5日修订产生的标签却train_count=1、split_reason=NONE。因此不是只缺一项审计字段，而是后续训练可用性判断会被错误时钟放行。公开输入已通过真实P1 publish_snapshot验证，非绕过数据校验的mock反例。

002证明的是“proposal确属不可变原运行”的校验缺口，不声称持测试key就能突破真实人工签名或OS隔离。修复时需要manifest成员及原字节hash绑定；仅增加path.exists或再次遍历当前文件内容仍不足。

003复现范围是公开compose SDK接口。当前统一research服务按同一decision网格产生输入，pipeline已有逐输入可见性检查；未把直接API反例夸大为普通成功服务请求已发生泄漏。G1明确要求合成自身拒绝不同时间/未来available，公共入口缺该约束仍须修复。

新增回归test_review_regressions.py位于审查目录，原始JUnit reviewer-regressions.xml记录4 failed、0 errors：available_at未来、decision_time不一致、终态清单外proposal、晚到主档因果依赖。没有删除失败或修改正确expected。源环境564项/覆盖率高不能替代这些语义反例。

**C · 26项覆盖、接口与验收边界**

完整逐行映射见canonical-phase3-implementation-coverage.csv及requirement-coverage.json，包含原来源、定义、依赖、输入/输出、acceptance、实际代码与测试、独立判断。本表表示本轮技术覆盖，不是用户验收；工程verified也不自动授予正式金融批准。

| ID | 级别 | 当前实现/证据判断 |
|---|---|---|
| DATA-012 | Competition Ready | ENGINEERING VERIFIED / 本轮未发现新缺陷 |
| FACTOR-007 | Competition Ready | ENGINEERING VERIFIED / 本轮未发现新缺陷 |
| FACTOR-009 | MVP | BLOCKED / WORK-P3-IMPL-002 |
| RESEARCH-001 | MVP | ENGINEERING VERIFIED / 本轮未发现新缺陷 |
| RESEARCH-002 | MVP | ENGINEERING VERIFIED / 本轮未发现新缺陷 |
| RESEARCH-003 | Competition Ready | ENGINEERING VERIFIED / 本轮未发现新缺陷 |
| RESEARCH-004 | MVP | ENGINEERING VERIFIED / 本轮未发现新缺陷 |
| RESEARCH-005 | MVP | ENGINEERING VERIFIED / 本轮未发现新缺陷 |
| RESEARCH-006 | MVP | ENGINEERING VERIFIED / 本轮未发现新缺陷 |
| RESEARCH-007 | MVP | BLOCKED / WORK-P3-IMPL-003 |
| RESEARCH-008 | MVP | ENGINEERING VERIFIED / 本轮未发现新缺陷 |
| RESEARCH-009 | MVP | ENGINEERING VERIFIED / 本轮未发现新缺陷 |
| VALID-001 | MVP | BLOCKED / WORK-P3-IMPL-001 |
| VALID-002 | MVP | BLOCKED / WORK-P3-IMPL-001 |
| VALID-003 | MVP | BLOCKED / WORK-P3-IMPL-001 |
| VALID-004 | MVP | 代码及模拟控制已实现；实际隔离NOT VERIFIED，不全项验收 |
| VALID-005 | MVP | 实际算术/拒绝分支已验证；正式过程证明/Test仍未验证 |
| VALID-006 | MVP | ENGINEERING VERIFIED / 本轮未发现新缺陷 |
| VALID-007 | MVP | ENGINEERING VERIFIED / 本轮未发现新缺陷 |
| VALID-008 | MVP | BLOCKED / WORK-P3-IMPL-002 |
| EXP-001 | MVP | BLOCKED / WORK-P3-IMPL-002 |
| EXP-002 | MVP | ENGINEERING VERIFIED / 本轮未发现新缺陷 |
| EXP-003 | MVP | 原wheel+锁及原3Ref真实重放通过；完整旧安装器/宿主字节未验证 |
| EXP-004 | MVP | BLOCKED / WORK-P3-IMPL-002 |
| QA-004 | MVP | BLOCKED / WORK-P3-IMPL-001,WORK-P3-IMPL-003 |
| INT-001 | MVP | BLOCKED / WORK-P3-IMPL-001,WORK-P3-IMPL-003 |

DATA-012为真实PIT Parquet侧车，绑定parent/hash/证券/币种/行业版本、可选risk exposure和null，不给原八表静默加表。PriceVolume正确使用t−1价格回报和不含t的历史均量，0.06与当前量0的−0.1有冻结答案及实际实现测试；全bundle准入和旧Ref兼容实证保留。

五stage均有真实工件、计数、reason/fit_scope/hash/input_ref及明确SKIPPED；截面中性化为行业dummy+log市值OLS，秩亏/缺暴露不复制原值冒充。算子按完整session网格、不压缩缺失；条件是结构化白名单。Ledger保存全部候选×期限，含合成及失败槽；参数实验、cache origin原config/signals、重复/预算、审批拒绝和JSON/HTML报告已有真实工程路径。终态审批绑定仍受002阻断。

Train/Validation/Test、闭区间purge、embargo、保守跨fold保护及去重、Test禁止fit的代码与工程测试存在；001使主档晚修订标签可能错误提前入Train，相关需求不能视为全部通过。研究替换Momentum→Reversal、薄CLI与同一服务真实执行，未依赖后续回测。

受限HAC增长带宽/整数根、原始gamma/S/SE、非年化ICIR和多重校正实际算术已检查。正式p与工程p_approx分离，失败槽raw=null/reason、保守校正槽1，全部family而非赢家子集。G1批准的受限方法不等于某个实际IC生成过程已证明有界严格平稳固定m0-dependent、S>0，也不保证N252有限样本尾部校准。实际model/proof/protocol/独立Test仍未验证。

U-001四主体配置/权限验证入口及预算控制有代码和模拟负例；此处四主体为research/evaluator/auditor三个标准账户加可信owner，未扩张为新增部署授权。无真实SID/UID/ACL/服务/调度部署。不能以单用户mock、ordinary hosted CI或公开合成数据全项验收VALID-004；正式Test缺证据必须fail closed。U-002仅合成经济口径确认，真实市场规则、金融标准及StrategyApproved没有批准。

EXP-003有真实原wheel、原锁、原三Ref与原发布66文件/3原运行的重放正向路径，不是全Unsupported。原安装器/整个历史宿主字节及完整等同环境没有被核实，开发方也明确限制；本轮只认可实际原wheel+锁验证和声明投影重现，不把它包装为所有历史环境字节相同。上述未验证内容不能静默标完成。

**D · 本轮实际独立执行**

本机Windows11 build26300；独立CPython3.13.16 cbc944f/MSC1944、AMD64 x64、标准GIL。按原hash锁在审查专用新venv安装依赖，从固定Git archive构建并安装真实wheel；没有修改全局项目依赖、正式源码或部署账户。原0.2.0在另一个受管旧venv实际执行。

独立SDK运行ID：aqrp-0397504c-4079-4bd5-ad18-09c175371cff。environment.code_commit=5a5e093c2e9b39abe1332e49d1df40d20f9fd33f、dirty=false、complete=true。本轮新wheel SHA256=de061a4b0f520b5e66dc80595c6d582def64f4aa17eb107bc05185f18be58048；45模块集合和每字节、receipt均与固定源码相同。

| 执行 | 本轮实际结果 | 含义 |
|---|---|---|
| 干净SDK/Ruff/格式/pytest/coverage/真实smoke/参考/秘密扫描 | 564 passed，0失败/错误/跳过，所有门槛通过 | GPT Work独立执行开发方固定工具及测试；未将工具名称当独立数学方法 |
| 原P1外置回归6+10及P2原4 | 16+4=20 passed，原脚本字节保持 | 当前安装wheel真实回归；最初6+4子集10通过日志保留，不重复计数 |
| 审查方独立数学算法 | 91 passed | Fraction Toeplitz HAC、直接排序Holm/BY/BH、精确正常方程Gauss–Jordan、原始和式/ties相关和整数五次根，与安装实现比较 |
| 审查方新增产品回归 | 4 failed、0 errors | 对应上述1 High/2 Medium；不是辅助脚本错误 |
| 最终扫描例外控制 | 3通过（exit 0/1/1） | 精确旧事件允许，同digest异路径及原路径新增合成凭证仍检测 |

SDK coverage实际语句2761/2778=99.3880%，分支1135/1154=98.3536%。关键模块95%行/90%分支、其余90%/85%门槛逐文件独立核过；原始coverage包含其自身excluded_lines=3记录，未改该记录。门槛通过不能说明未覆盖的时点/证据语义正确。

独立数学expected来自审查方标准库有理数/高精度推导，不从AQRP或开发方参考生成。冻结Golden的实际实现测试亦在564项中执行；旧G1独立答案原件hash未变。不把旧349项重新报成本轮新跑，也不把当前91项或564项当金融批准。

SDK还实际完成原0.2.0锁环境、22个Windows依赖wheel保存、原三因子Ref与原发布三运行重放，原66文件核hash，完整研究合成/参数/替换/投影重现以及数据/因子smoke。新旧代码环境未混装；完整SDK日志与185文件selection逐项核验。

主要原始命令：
- git clone --shared --no-checkout --config core.longpaths=true <开发方仓库> <独立副本>；checkout --detach 5a5e093c2e9b39abe1332e49d1df40d20f9fd33f。
- C:/Users/11638/AppData/Local/AQRP/runtime/Python31316/python.exe -I <固定副本>/tools/ci.py；AQRP_RUN_ROOT指向审查目录/sdk，实际子命令全在SDK commands.log。
- <SDK>/venv/Scripts/python.exe -I -m pytest <审查目录>/original-probes/三份原脚本 -q --junitxml=<审查目录>/original20-regressions.xml，实际16+4通过。
- <SDK>/venv/Scripts/python.exe -I -m pytest <审查目录>/test_review_regressions.py -q --junitxml=<审查目录>/reviewer-regressions.xml，实际退出1、4失败。
- 独立解释器-I执行verify_scope.py、verify_ci.py、verify_sdk.py、verify_end.py；安装环境-I执行independent_implementation_math.py、adversarial_probes.py、late_master_causal.py、verify_fit_leak.py。
- 已锁gitleaks8.30.1 dir <控制目录> --config <固定副本>/.gitleaks.toml --redact=100 --no-banner。

实际绝对路径、cwd、参数、UTC/本地起止、退出码及原始stdout/stderr见各*.command.json与配套日志；源码/数据/wheel/snapshot/config/ledger原字节及hash在证据清单。verify_fit_leak的实际argv和stdout另记，未捏造当时未单独捕获的起始时间。

**E · 最终CI、失败历史与哈希**

[最终Actions run39683883359](https://github.com/wwooyy429/Alpha-Quant-Research-Platform-AQRP-/actions/runs/39683883359)：Windows/Ubuntu均success，各564项，0失败/错误/跳过。实际checkout为PR integration ab885d4f48053bad52c77c6e10a4949aec9765c8，整个tree bd0e3578f594008962b3809d88fdbe5193262642等于固定审查SHA；它不是main合并。

两份官方原ZIP本轮实际下载，按GitHub官方metadata校bytes/SHA256/CRC；核完整upload-selection及精确成员集合、environment提交/锁/完成状态、45模块wheel及receipt、研究终态manifest/hash链、95批engine原config字节/signals/content_hash（含cache引用）、依赖wheelhouse、旧66文件/三原运行重放记录。CI执行者为GitHub hosted runners，GPT Work独立核原始产物；本机SDK则由GPT Work实际新执行，身份区分保留。未在本机执行Ubuntu环境。

| 原始artifact | bytes | SHA256 | selected / 实际ZIP成员 |
|---|---:|---|---|
| Ubuntu 12385084521 | 136795968 | 79b0ad94ed0590b01db556af7a85c605253a94e6966cb29d7bfb295e575e3d09 | 184 / 185 |
| Windows 12385054743 | 95523501 | 9063a8f7bebfa3e441eaed9e1476da8536ca1244b05ed1a1f55891d0f7fbdea3 | 185 / 186 |

成员计数包含selection自身，不能错称少文件；Ubuntu原锁条件安装21个依赖wheel，Windows22个，两OS身份不混同。CI wheel SHA分别2f0e0b9468966fbaac58234715e049db7a19b297a4c44b0a487877a2f4d2b6b9、0538c54ffb9b5a7e0f090c32604ce4889104fd3e4977149b01d2f47b780b6c18；构建字节不同不等于源码不同，45模块和receipt已逐字节比对。

旧bc99dc671d7292a8cb9e77cea17d91e84193bc6d的run39682778261确实failure，已读API metadata并核其归档原始扫描失败证据，未计作成功。最终.gitleaks例外仅generic-api-key、精确历史路径AND精确提取digest。审查方独立从cache canonical key复算69266f2f…32c554，确认其为公开合成缓存hash，并实际跑三项对抗控制；不是只接受开发方说明。配置SHA256=73dbfe9e8ddd221da5ffd18a3cfa467ea8435dfa57b1ce4f28159eb6c5bab928。未宣称修改或重新解决未变的P1历史例外。

固定源码archive SHA256=800ae0a3469f9623aaf320bd9ab6f91bcdd6a6b21659b7424d7f63ec468c2c56。其余原始文件/脚本/命令/JUnit和本报告hash由REVIEW_EVIDENCE_MANIFEST及外置封存收据登记，不自指修改原文件。

审查辅助错误亦保留：首次scope将20个module类别误当16个ID组，scope失败脚本/日志保留，按ID前缀修正后通过；一次GitHub tree字段显示错误、两次不存在验证文件的只读探查，以及PowerShell coverage JSON显示错误均记reviewer-helper-errors.json。它们与四个真实产品回归失败分开，不隐藏或混算。

**F · 未验证、处置与结论**

NOT VERIFIED / NOT AUTHORIZED：真实Windows/Ubuntu独立四主体/SID/UID/token/ACL/受管入口、真实私有Test与反馈泄露/并发预算/崩溃恢复实证、实际IC过程证明及正式统计protocol/样本/阈值/金融标准、完整历史安装器/宿主字节、正式ResearchValidated/StrategyApproved、用户Phase3验收。无部署授权，本轮未操作账户/ACL/服务/调度器；不要求开发方越权部署来关闭代码缺陷。

请开发方先修复3项实现发现并纳入4个有效回归，保留旧失败/正确Golden/原测试。源码变化后重审全bundle/receipt、保留旧Ref/锁兼容，重跑干净SDK、原16/4、关键独立数学/冻结答案、双OS及扫描控制，保存真实完整证据。更新PR描述AQRP_FIXED_REVIEW_SHA为新的完整40位提交再复核，禁止用漂移HEAD或旧564成功外推。

本轮结论仅为固定SHA技术审查建议：**G2 REQUEST CHANGES / IMPLEMENTATION BLOCKED**。1 High和2 Medium未闭环，因此不能认定26项已全部验收。G1设计通过与U-001/U-002确认继续有效；代码修复和真实部署/正式金融/人工验收门禁分别处理。未合并、未打标签、未部署、未进入P4。
