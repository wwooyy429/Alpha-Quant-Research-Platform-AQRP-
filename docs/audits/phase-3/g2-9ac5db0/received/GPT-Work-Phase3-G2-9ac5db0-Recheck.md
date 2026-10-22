# AQRP Phase3 G2 固定SHA修复复核

固定完整SHA：**9ac5db069287a6e4a095e25ae8c3cc8fa229cded**。

**三项实现发现均 CLOSED；本轮结论为 G2 TECHNICAL PASS WITH CONDITIONS（实现修复技术复核通过，保留既定验收限制）。** 本轮范围内无新增阻断代码发现。G1 PLAN PASS保持；不再要求重复批准P3启动。此结论不等于26项正式全项验收、不授予ResearchValidated金融批准，也不等于Phase3 ACCEPTED/RELEASED。

本轮由GPT Work主审实际执行，针对上一固定5a5e093的完整26项实现审查做增量关闭与全套回归。仅向审查专用目录写公开输入、脚本、报告与证据；未改正式源码/测试/Golden/旧报告，没有提交、推送、合并、标签、部署或进入P4。

## 固定范围与证据连续性

从[PR #5描述](https://github.com/wwooyy429/Alpha-Quant-Research-Platform-AQRP-/pull/5)读取并保存AQRP_FIXED_REVIEW_SHA，初始/收尾描述和PR head均等于完整9ac5db0；独立clone detach检出同一提交。审查副本和开发方原副本均干净。main与phase2-baseline/v0.2.0剥离标签后仍同点f26255fc40a3080bfa883ad64938f60036a14759，PR open/未合并。原G1固定3861ef1637bc2b4c28725d7afc5f2e1f02242e80及U-001/U-002决定未被改写。

canonical仍106项/16个ID前缀组、Phase3 26项=23 MVP+3 Competition Ready；原CSV SHA256=20dd4e6be7188d3121f3cb361faf8901bc91815a6e9752beb14054a12183f0c1。独立核验1957项冻结资产、557项P3清单；G1原15/28/17组、growth输入与参考脚本/独立答案字节未变。本轮不把旧349项答案核验重新宣称为新执行。

源修复集中labels/approvals/pipeline，另更新全bundle准入receipt、集成原四回归与十个参数化边界，原阶段fixture仅补显式时钟、未改正确数值expected。45模块bundle=3cec8a9da49a49a93010d7fa6a2012dded25185e2cdca49144cf4d719d56876e。最终src/tests/tools/CI/pyproject/锁字节与修复业务1b4be236e888805f5c4e45357b158fcdb6058df0一致；Python3.13.16、requirements.lock SHA256=86c7bf65c9a9690036006360062c8cd10a91279705b4070af7033d7699abffeb保持。与旧5a相比tools/CI/锁/扫描例外未变，没有引入未锁依赖、DAG/任意外部插件或P4/P5/P6业务范围。

上一封存原ZIP 296718793 bytes、SHA256=54f559f9360cafcdc4d4fc9ab7af7a3eb6c13af846b6ab19524208e2cf336ca0，本轮实际重读CRC/完整成员及319文件hash通过。仓库received的147文件与未入Git172文件恰好分割原319，147个原字节一致；原报告、四项真实失败及辅助错误完整保留，不倒写旧结论。详见archive-verification.json。

## 三项发现的关闭

**WORK-P3-IMPL-001 · High · CLOSED**

位置：[src/aqrp/validation/labels.py:188](https://github.com/wwooyy429/Alpha-Quant-Research-Platform-AQRP-/blob/9ac5db069287a6e4a095e25ae8c3cc8fa229cded/src/aqrp/validation/labels.py#L188)、[src/aqrp/validation/labels.py:237](https://github.com/wwooyy429/Alpha-Quant-Research-Platform-AQRP-/blob/9ac5db069287a6e4a095e25ae8c3cc8fa229cded/src/aqrp/validation/labels.py#L237)。需求：VALID-001, VALID-002, VALID-003, QA-004, INT-001。

依据：原反例：晚到证券主档修订让标签由无效变有效，却未进入标签最早可用时间及依赖hash；实际purged_train错误接受。

修复：选中security_master加入deps，available/information_interval/dependency_hash包含该行；security_master_ref绑定发布后行hash/修订与时钟。

本轮实际结果：原用例通过。独立有效P1快照：修订Jan5 00可见，标签0.1的available恰为Jan5 00，Jan4 12:10和Jan5前1us均拒绝，Jan5相等及后1us接受。578套件亦覆盖晚到上市/退市。 原始证据：original-four.xml, after-causal-independent.json, sdk-verification.json。

**WORK-P3-IMPL-002 · Medium · CLOSED**

位置：[src/aqrp/validation/approvals.py:126](https://github.com/wwooyy429/Alpha-Quant-Research-Platform-AQRP-/blob/9ac5db069287a6e4a095e25ae8c3cc8fa229cded/src/aqrp/validation/approvals.py#L126)。需求：FACTOR-009, VALID-008, EXP-001, EXP-004。

依据：原反例：终态manifest外后补approvals.json可被record_decision接受。

修复：verify返回清单中唯一approvals条目为前提；同一次read_bytes进行SHA256验证和JSON解析，拒绝symlink/非dict/不匹配proposal。

本轮实际结果：原缺文件及后补文件负例通过；新增list/mismatch/verify后更改原字节负例均拒绝，既有合法manifest绑定人工决策工程正例仍通过。仅公开测试key；不宣称突破或验证真实OS/人工签名。 原始证据：original-four.xml, sdk-verification.json。

**WORK-P3-IMPL-003 · Medium · CLOSED**

位置：[src/aqrp/research/pipeline.py:16](https://github.com/wwooyy429/Alpha-Quant-Research-Platform-AQRP-/blob/9ac5db069287a6e4a095e25ae8c3cc8fa229cded/src/aqrp/research/pipeline.py#L16)、[src/aqrp/research/pipeline.py:215](https://github.com/wwooyy429/Alpha-Quant-Research-Platform-AQRP-/blob/9ac5db069287a6e4a095e25ae8c3cc8fa229cded/src/aqrp/research/pipeline.py#L215)。需求：RESEARCH-007, QA-004, INT-001。

依据：原反例：公开compose入口接受未来available或混合decision_time；未夸大为正常统一服务已泄漏。

修复：pipeline/compose共用必需、UTC感知、按session共同decision时点和available<=decision检查；输出时钟/输入hash/lineage，拒绝重复键。

本轮实际结果：原两负例和正常组合控制通过；新增缺/null时钟、UTC同瞬间、lineage/hash/input不变、多session/重复键工程边界通过。 原始证据：original-four.xml, sdk-verification.json。

## 26项需求、接口与阶段依赖

下表是工程实现覆盖与本轮判断；逐项原来源/定义/依赖/接口/验收/实际代码及测试映射见canonical-phase3-implementation-coverage.csv和requirement-coverage.json。旧规划字段作为来源保留并明确命名，不用Planned/Unsupported删掉应实现能力。

| ID | 级别 | 工程判断及保留限制 |
|---|---|---|
| DATA-012 | Competition Ready | ENGINEERING VERIFIED / 本轮未发现新缺陷 |
| FACTOR-007 | Competition Ready | ENGINEERING VERIFIED / 本轮未发现新缺陷 |
| FACTOR-009 | MVP | ENGINEERING VERIFIED / 原实现发现已关闭：WORK-P3-IMPL-002 |
| RESEARCH-001 | MVP | ENGINEERING VERIFIED / 本轮未发现新缺陷 |
| RESEARCH-002 | MVP | ENGINEERING VERIFIED / 本轮未发现新缺陷 |
| RESEARCH-003 | Competition Ready | ENGINEERING VERIFIED / 本轮未发现新缺陷 |
| RESEARCH-004 | MVP | ENGINEERING VERIFIED / 本轮未发现新缺陷 |
| RESEARCH-005 | MVP | ENGINEERING VERIFIED / 本轮未发现新缺陷 |
| RESEARCH-006 | MVP | ENGINEERING VERIFIED / 本轮未发现新缺陷 |
| RESEARCH-007 | MVP | ENGINEERING VERIFIED / 原实现发现已关闭：WORK-P3-IMPL-003 |
| RESEARCH-008 | MVP | ENGINEERING VERIFIED / 本轮未发现新缺陷 |
| RESEARCH-009 | MVP | ENGINEERING VERIFIED / 本轮未发现新缺陷 |
| VALID-001 | MVP | ENGINEERING VERIFIED / 原实现发现已关闭：WORK-P3-IMPL-001 |
| VALID-002 | MVP | ENGINEERING VERIFIED / 原实现发现已关闭：WORK-P3-IMPL-001 |
| VALID-003 | MVP | ENGINEERING VERIFIED / 原实现发现已关闭：WORK-P3-IMPL-001 |
| VALID-004 | MVP | 代码及模拟控制已实现；实际隔离NOT VERIFIED，不全项验收 |
| VALID-005 | MVP | 实际算术/拒绝分支已验证；正式过程证明/Test仍未验证 |
| VALID-006 | MVP | ENGINEERING VERIFIED / 本轮未发现新缺陷 |
| VALID-007 | MVP | ENGINEERING VERIFIED / 本轮未发现新缺陷 |
| VALID-008 | MVP | ENGINEERING VERIFIED / 原实现发现已关闭：WORK-P3-IMPL-002 |
| EXP-001 | MVP | ENGINEERING VERIFIED / 原实现发现已关闭：WORK-P3-IMPL-002 |
| EXP-002 | MVP | ENGINEERING VERIFIED / 本轮未发现新缺陷 |
| EXP-003 | MVP | 原wheel+锁及原3Ref真实重放通过；完整旧安装器/宿主字节未验证 |
| EXP-004 | MVP | ENGINEERING VERIFIED / 原实现发现已关闭：WORK-P3-IMPL-002 |
| QA-004 | MVP | ENGINEERING VERIFIED / 原实现发现已关闭：WORK-P3-IMPL-001,WORK-P3-IMPL-003 |
| INT-001 | MVP | ENGINEERING VERIFIED / 原实现发现已关闭：WORK-P3-IMPL-001,WORK-P3-IMPL-003 |

DATA-012的PIT侧车/null、FACTOR-007的t−1价量公式与原P2加法兼容、FACTOR-009工程审查/研究审批隔离、QA-004独立算术及INT-001同服务研究替换均保留真实路径。45模块新bundle逐字节准入，旧0.2.0 wheel/锁/三精确Ref实际独立环境重放，原发布66文件/3运行核对；不把旧receipt绑定新代码。

raw/clean/standardized/neutralized/final五stage、明确SKIPPED与reason/count/hash/input_ref、完整session网格、行业dummy+log市值OLS/秩亏处理、全部候选×期限ledger、失败槽、原config/signals的cache来源、参数预算/污染、OOS/跨fold保护/去重、JSON/HTML报告与投影复现仍由当前578套件及真实smoke覆盖。001修复使主档晚修订不会提前进入fit，002修复终态proposal血缘，003让公开合成入口也执行时钟契约；后续组合持仓、撮合回测和UI未提前实现。

HAC原gamma/S/SE尺度、受限增长带宽、小样本拒绝、Pearson/Spearman ties、OLS残差、Holm/BY/BH全family及失败槽1规则的独立91项仍通过。Formal p与工程p_approx分离；有界严格平稳固定m0-dependent、S>0等实际模型假设和有限样本尾部校准不由算术通过证明。min_hac_n/lag或库锁不是本轮新增缺陷；真实模型证明、协议和金融标准门禁保持。

## 实际执行、原始命令与环境

本机Windows11 build26300，CPython3.13.16 cbc944f/MSC1944 AMD64标准GIL；按原锁新建独立venv、从固定Git archive构建并安装wheel，原0.2.0使用另一受管环境。全SDK于本地13:32:55开始、13:39:42结束（UTC+08），exit0。run_id=aqrp-b95750e5-e167-4173-94b6-20568b25fab4，environment.code_commit=完整9ac、dirty=false、complete=true。

| 实际核验 | 结果 | 执行身份和范围 |
|---|---|---|
| 新干净SDK、Ruff/格式/覆盖/参考/真实smoke/秘密扫描 | 578 passed，0失败/错误/跳过 | GPT Work本机实际运行固定工具与安装wheel |
| 原审查方四个失败用例，字节未改 | 4 passed | 包含两个合成负例的正常控制；不是开发方新expected |
| 原P1六+十、P2原四外置用例 | 16+4=20 passed | 原脚本字节一致，当前安装wheel |
| 独立数学算法与安装实现比较 | 91 passed | 审查方标准库Fraction/高精度算法；不从AQRP生成expected |
| 晚到主档→标签→实际purged_train因果链 | 全通过，前两cutoff train0、等于/后一微秒train1 | 独立真实P1 publish_snapshot，无绕过校验mock |
| 窄扫描例外控制 | 三项通过，exit0/1/1 | 固定gitleaks8.30.1；精确事件允许，同digest异路径及原路径新合成凭证仍检测 |
| 当前Windows/Ubuntu官方CI | 各578通过 | hosted runners执行，GPT Work独立下载并核原ZIP；没有冒称本机执行Ubuntu |

这些是不同层次/存在重复覆盖的检查，不能相加声称独立测试总数。SDK语句2784/2801=99.3931%，分支1145/1164=98.3677%；逐文件95/90关键与90/85普通门槛已核，原coverage excluded_lines=3照实保留。45个wheel模块精确集合/字节及receipt与固定源码一致，独立wheel SHA256=41237f475ff2ff7983b40272cfaaafb57acc5426eb1de587d9dbb89a08efae3c。185个SDK选择文件逐项核hash，Windows锁依赖22个，旧66文件/3运行实际重放记录保持。

主要真实命令及参数：
- git clone --shared --no-checkout --config core.longpaths=true <开发方副本> <独立副本>；git checkout --detach 9ac5db069287a6e4a095e25ae8c3cc8fa229cded。
- C:/Users/11638/AppData/Local/AQRP/runtime/Python31316/python.exe -I C:/Users/11638/AppData/Local/AQRP/reviews/p3-recheck-9ac5db0/tools/ci.py；AQRP_RUN_ROOT指向审查专用sdk。全部实际子命令和stdout/stderr见SDK commands.log及clean-sdk.command.json。
- <本轮SDK>/venv/Scripts/python.exe -I -m pytest <审查目录>/test_review_regressions.py ... --junitxml=<审查目录>/original-four.xml。
- 同一安装解释器-I -m pytest <original-probes三原文件> ... --junitxml=original20.xml。
- 安装解释器-I执行independent_implementation_math.py、after_causal_independent.py、verify_scanner_controls.py <固定副本>。
- 标准库解释器-I执行verify_archive.py、verify_scope.py、verify_ci.py、verify_sdk.py、verify_end.py。
- git status --porcelain=v1 --untracked-files=all、rev-parse HEAD、ls-remote main与稳定标签核收尾状态。

完整绝对argv/cwd/时间/退出码、原stdout/stderr、脚本hash、输入及JUnit在各.command.json及配套日志；这些是原始证据，不用此处省略参数的展示替代。原数学/扫描/四回归脚本含旧5a SHA或旧身份字面量，为保持原字节未改；本轮实际执行9ac身份由extra-verification.json、installed-identity及命令记录绑定，不把字面量当当前目标或另一次Gemini执行。

审查辅助首次扫描调用早于SDK下载gitleaks.exe，FileNotFoundError/exit1是本轮调度错误，扫描器当时没有执行。run_extras-attempt1.py、extra-verification-attempt1.json、extras及scanner-controls-attempt1原日志保留。SDK完成后仅重跑扫描三控制并通过，4/20/91不重复计数；没有删失败、未作为产品缺陷。最终extra-verification.completed=true。历史开发方失败尝试也按原轮次保留，不替换为成功。

## 两份最终CI原ZIP与hash

[Actions run39726898890](https://github.com/wwooyy429/Alpha-Quant-Research-Platform-AQRP-/actions/runs/39726898890)两job成功，实际PR集成checkout=d3d9b262d4866e8768670dc1d2392ef32bbd7889，whole tree=2d2790365e5f202796d5089c93abbb1c037093fa，与固定9ac整tree相等。这是CI集成提交，不是main已合并。

| 官方artifact | bytes | SHA256 | selected/ZIP成员 |
|---|---:|---|---|
| Windows 12404165070 | 95545850 | f26ba7566ad44a3c3e415fca5dbcaf46574b2ff8325eaf86c52c86e4d5b6b456 | 185/186 |
| Ubuntu 12403373418 | 136817989 | 3b7c4534a48d4f10a94228077af6e7acac7ea6671faf3230e2acc09739728589 | 184/185 |

原ZIP bytes/SHA与GitHub metadata一致，CRC/精确成员/selection全部hash、环境完成/锁、JUnit578、45模块与receipt、终态manifest/hash链、95批engine原config/signals/content_hash含cache引用、依赖wheel及旧66文件/3运行均独立核。selection自身额外一成员，不算漏清单。Ubuntu条件依赖21个，Windows22个。CI wheels分别Ubuntu0a0491008550c695b78fdf54f179ace693c10a08e66d1b44004a800b5d36be9a、Windowsdbb836053efadf76c897d6c6ac847326466f4d0ef97c8e1b0b54994ed853a276；构建wheel hash不同，已用源码逐字节身份而非假设二进制相等。

固定源码archive SHA256=9694d32db7f5240966a4124a1c1ffedcbd0a3dd08af7e0cd8e42680b7da04fc4。原ZIP、固定源码、所有本轮命令/脚本/报告/选择证据将在REVIEW_EVIDENCE_MANIFEST.json登记，外置Seal收据登记整个封存ZIP hash，避免自指。

## 保留条件、未验证与用户决定

1. U-001仅批准四主体隔离设计/责任，未授权部署。本轮未改SID/UID/ACL/token/账户/服务/调度器，真实隔离、私有sealed Test、反馈/并发预算/崩溃恢复部署实证仍NOT VERIFIED；role/API或单OS用户/公开fixture/普通CI不能替代。VALID-004不得全项标完成，正式Test缺证据继续fail closed。
2. U-002仅确认合成经济口径。实际研究过程的依赖/平稳性证明、正式统计protocol与样本/阈值、用户金融标准/真实私有Test/人工金融签封仍NOT VERIFIED；正IC或统计显著不代表金融批准，未授ResearchValidated/StrategyApproved。
3. EXP-003认可实际原wheel+锁+三精确Ref/66文件/三运行的重放和声明投影复现；完整历史安装器与宿主全字节等同仍NOT VERIFIED，不静默删掉或声称全部完成。
4. Phase3用户验收尚未发生；需用户就本轮技术通过及明确保留限制作阶段决定。若后续要真实部署/正式Test，须另行授权和提供相应批准标准/证据；本轮不要求开发方越权部署来关闭代码缺陷。
5. 不合并、不打标签、不部署、不进入P4。代码再变须新完整固定SHA及适用回归/全bundle复核；仅归档本报告也需如实区分审查SHA与后续文档提交，不把新HEAD自动视为已审。

**最终：WORK-P3-IMPL-001/002/003均CLOSED；G2 TECHNICAL PASS WITH CONDITIONS。** 原G1及用户设计决定有效，正式Test/金融/实际隔离/完整历史宿主限制与人工验收继续独立保留。
