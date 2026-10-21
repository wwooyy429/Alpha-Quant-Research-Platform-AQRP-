# Phase 2 实现审计接收与开发方核对

最新增量：修订数学源/日志与增量报告已收到，Volume/证券B/非零误差核心问题核对通过；本文件以下旧版缺陷或“未收到”表述按历史时点解释，不代表当前仍未修。Gemini十二项均标AGREE/CLOSED，但部分解释仍与真实标题/需求职责/路径冲突，最新事实及执行限制见MATH_INCREMENTAL_RECONCILIATION.md和gemini/MATH_INCREMENTAL_INDEX.json；尚未人工验收/发布。

当前补充：用户已提供旧预审命名的数学脚本/日志，原件已按本轮时间补收；复跑相符但存在错误公式和验证范围不足。此前“未收到”的文字按历史接收时点解释，完整当前核对见MATH_SUPPLEMENT_RECONCILIATION.md。实现报告所称新数学/hash执行证据仍未匹配，不能以旧文件名或相同最终数字补齐。

Gemini审查固定2a70dc6251ce2e7d014d76f3c1bd26cdddb3aac1，业务8183b3762b56c466b989d9062a720b5f0d31172a。报告原件按字节归档于gemini/aqrp_phase2_implementation_audit_report.md，SHA256为395eadf04145e5a23b624687c3576def8a9b23260cb75a53037c7218e30a3d0f，17062 bytes。来源/用户授权边界见gemini/IMPLEMENTATION_AUDIT_INDEX.json。

当前：**AUDIT PASS AS REPORTED / REPORT ERRATA AND EXECUTION EVIDENCE OPEN**。Gemini给出PASS、建议READY；八项ERR-P2-001..008均AGREE/CLOSED，F-P2-PRE-001/002均获Gemini正式CLOSED，限受审内置工程测试。没有新Critical/High发现或可复现业务缺陷。以上审查意见已经接收；不将原件的事实误述和未附执行文件一并当成已验证，不把转交报告登记成用户验收或限制豁免。

## 已确认处理与开发方复核

- 既定106条/16组、10项P2范围与源码/实际测试映射正确；不新增Volatility/DAG、研究/组合/回测/UI。工程准入仍ENGINEERING_APPROVED / TEST_ONLY / financial_approval=NONE；金融批准和OS沙箱未实现。两项Low的审查方关闭原话保留，以下报告勘误不擅自改写其结论。
- 本轮重新核验2a70原636项文件manifest、50项保护资产及448份旧审计文件；业务代码/测试/工具/CI/包配置/锁与8183一致。以固定Git tree及原始字节核对，不运行会覆盖旧清单的Phase0自查工具。
- 本轮实际读取两份原始ZIP，重新计算SHA/size、CRC/路径、上传完整集合/每文件hash和JUnit（两端各254/0/0/0），并用新取得的GitHub API元数据交叉核对。与旧开发方验证结论一致；这是Codex开发方本轮执行，不能补记为Gemini执行。
- 原完整CPython3.13.16 wheel SDK及双OS CI通过的记录保留；本轮不改业务，不另造“Gemini独立SDK通过”。报告明确其Python3.11.2沙箱未运行指定SDK，Gemini完整独立执行仍NOT VERIFIED。
- 重新以标准库Fraction独立核算固定答案及精确binary64误差，不调用待验证因子函数；容差未变，开发方新证据见implementation-audit/developer-math-recheck.json。并非Gemini所述新脚本/日志的替代品。

## 本报告新增事实勘误（待Gemini确认）

| 编号 | 原报告表述 | 开发方核对及处理 |
|---|---|---|
| ERR-P2-IMPL-001 | PR标题仍为plan/pre-review，2a70相对8183只在audits目录“新增” | 当前PR标题为feat: Phase 2 Factor Registry and reviewed builtin signals；该提交还修改AGENTS、README、CHANGELOG、DECISIONS、PROGRESS、ROADMAP及预审处理状态文档。业务/测试/工具/CI/锁冻结结论成立，但不能缩写成只新增audits文件。 |
| ERR-P2-IMPL-002 | Volatility与DAG属于Phase3/5职责 | canonical FACTOR-008将波动率等扩展列Advanced Research / POST7 / Deferred；没有已批准DAG引擎需求或P3/P5交付义务。不在P2实现的结论正确，但不据报告给后续阶段新增需求。 |
| ERR-P2-IMPL-003 | 因子字段含input_data_hash等，签名带view:DataView | 实际协议在factors/contracts.py的Factor.compute(self,view,context:FactorContext)->SignalBatch，view参数没有字面类型注解；语义为经host验证的DataView。Signal有snapshot_id/params_hash/implementation_hash等；manifest_hash/query_hash在context/config_snapshot；不存在input_data_hash字段。不得为迎合误写新增字段或破坏契约。 |
| ERR-P2-IMPL-004 | core/security.py；factors/protocols.py | 实际是src/aqrp/core/security/__init__.py与src/aqrp/factors/contracts.py。原始coverage三行排除实际为contracts.py 289–291的Protocol声明；没有protocols.py，不为报告造文件。 |
| ERR-P2-IMPL-005 | AST扫描、类型检查即准入；ENGINEERING_APPROVED与TEST_ONLY均为状态 | 需完整源码bundle/锁身份、受信receipt、环境与固定ID、API/元数据等联合核验。ENGINEERING_APPROVED是状态，TEST_ONLY是环境/用途，NONE是金融批准标记。现有流水线有ruff与运行时契约/类型负例，没有mypy/pyright静态类型检查执行证据，不声称已有该步骤。AST实现检查Name/Import/Attribute等，不能描述为仅遍历Call。 |
| ERR-P2-IMPL-006 | Volume基准1800/3000=3/5为成交量与历史均量的比值 | 冻结G-P2-A输入V=[100,150,200]，均量125，200/125-1=3/5。未减1的原始比值是8/5；3/5是超出历史均量的相对变化。1800/3000不来自该固定案例，不能拿相同最终数字代替公式/输入校验。 |
| ERR-P2-IMPL-007 | 数学绝对误差0.00e+00，完全位对齐 | 同float比较可为0，但相对精确有理数的binary64误差：±0.21为7.771561172376097e-18，0.6为2.2204460492503132e-17，均非零且满足既定容差。既有MATH_PRECISION_RECHECK.json及本轮Fraction核对支持，不改答案或放宽容差。 |
| ERR-P2-IMPL-008 | decision/依赖/available_at均严格按“盘后安全发布时点对齐” | decision_time是冻结请求cutoff，依赖event/available必须<=cutoff，输出available_at保守=decision_time（合成logical_compute_delay=0）。依赖时间不必相等；通用契约不能推定真实市场盘后时刻。坏目标/未来目标输出invalid，不能把无效占位的signal_time当可执行信号。 |
| ERR-P2-IMPL-009 | “不存在越权执行漏洞” | 能确认受审内置准入与既有负例；无法由静态语义/有限测试证明不存在全部漏洞。同权限恶意维护者、反射/原生扩展等不由本阶段Python/AST隔离；外部插件/OS沙箱Unsupported的限制继续保留，报告绝对措辞待澄清。 |
| ERR-P2-IMPL-010 | 本次新.py/.log已生成，原数学证据缺口已闭环 | 后续已收到aqrp_phase2_math_verification.py/.log，文件自述Plan Pre-Review，不含hash/SDK/ZIP校验且Volume公式错误；两原件已归档、开发方复跑相符。旧预审同名缺件当前补齐，但不是实现报告指定的新implementation_math_and_hash_audit文件身份/范围证明，不能登记新数学/hash证据匹配或全部闭环。详见MATH_SUPPLEMENT_RECONCILIATION.md，不追溯改写旧接收事实。 |
| ERR-P2-IMPL-011 | CI Verified/归档MATCH即可视为独立SDK/远端验证闭环 | 报告明确未运行3.13.16 SDK；CI与开发方日志审阅不等于Gemini独立SDK。ZIP实际执行清单/哈希脚本与新远端API响应未随报告提供，审查方的MATCH按报告自述保留，开发方新API核对不得替其补证。沙箱无网与外部只读工具可分开说明，不据此猜测审查者做过哪些操作。 |
| ERR-P2-IMPL-012 | “法定”四条件；main gate后解除Phase3启动阻断 | 属项目治理条件，不是法律结论。报告提出phase2-baseline/主干复核不构成本轮合并/标签授权。用户阶段验收与限制决定、另行合并/标签授权、获批范围合并后核验/基线发布仍未完成；即使RELEASED，Phase3还需用户独立明确启动授权，不能自动解除并开发。 |

以上仅修正审计记录，不改变业务实现、金融公式、独立答案、安全能力或批准流程。开发方不改Gemini原报告；新增勘误与执行证据范围仍须Gemini澄清/复核。

## 当前未闭环条件

1. 本表12项报告事实更正与执行范围澄清尚未获Gemini确认；不能将八项旧勘误AGREE推广为对新增勘误已AGREE。
2. 旧预审数学两原件现已收到，开发方复跑相符，原始文件接收缺件当前关闭；但Volume错式、证券B常量比较、浮点口径等仍需新修订证据。实现报告所称新数学/hash文件身份与执行范围尚未匹配，补证需绑定固定SHA/正确输入/实际命令/输出/hash，不追溯改写旧历史。
3. Gemini在CPython3.13.16的完整独立SDK执行仍NOT VERIFIED。可以补充真实执行；如无法执行，由用户在人工验收时明确决定是否接受该限制，当前用户没有作此决定。不能把用户本次“请归档处理报告”当作接受限制。
4. 原始ZIP开发方校验及远端API校验已通过；Gemini独立执行/原始记录范围与证据缺口需澄清，不能以另一执行者的证据补记。
5. 新归档SHA仅审查记录增量，业务与已审2a70/8183相同；Gemini对新增记录/勘误复核后，后续若发现金融/安全阻断缺陷须修复、新SHA、适用测试再复核。
6. 用户Phase2人工验收、P2合并授权、标签授权、main范围/检查/基线核验及发布均未完成。Phase3独立启动未授权，保持BLOCKED。

Gemini称技术局限非阻断/建议READY是审查建议，已忠实保留；开发方只登记AUDIT PASS AS REPORTED，不宣告所有证据闭环、ACCEPTED或RELEASED。不合并、不打标签、不进入Phase3。
