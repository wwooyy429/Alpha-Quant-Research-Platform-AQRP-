# Phase2 修订数学原件与增量复核报告接收

用户连续提供修订数学.py/.log及aqrp_phase2_math_and_errata_incremental_recheck_report.md。本轮同时归档三原件，接收锚点0b5107fa611af9d3a858440261b5321c83ca9fa4；业务8183b3762b56c466b989d9062a720b5f0d31172a不改。Gemini报告结论PASS / READY、十二项AGREE/CLOSED、两项Low继续CLOSED按原文登记，非用户验收/接受限制或发布授权。

| 原件 | bytes | 实际SHA256 |
|---|---:|---|
| aqrp_phase2_math_verification_revised.py | 9527 | a4d6ab561cf81040411a9980adc4d72dbd69b79661cebaaf395da2312baae92c |
| aqrp_phase2_math_verification_revised.log | 5702 | b211a417759654981eff08309415bcf9f0fd8b682bc9a91711d3750e2b23ffee |
| aqrp_phase2_math_and_errata_incremental_recheck_report.md | 20041 | 3df97ed8a3902463a8c7139cc406789b32d08ac9ec554ca38aa560d57c0868d0 |

三原件位于gemini/revised-math/；来源、接收时间和完整hash见gemini/MATH_INCREMENTAL_INDEX.json。旧报告、旧有缺陷脚本及旧日志不覆盖，旧索引/manifest按各自历史接收时点解释。本轮开发方记录在revised-math/，不改写为Gemini执行。

## 已解决的核心数学问题

- MATH-SUP-001：修订脚本分别算旧输入均量3000、当期1800的raw ratio=3/5与formal factor=-2/5；正式Golden输入[100,150,200]的200/125-1=3/5。原参考遗漏-1已明确纠正，两套输入不再混用。开发方独立Fraction复算一致，数学缺陷CLOSED。
- MATH-SUP-002：证券B从价格[200,180,160]和量[40,60,50]计算momentum=-1/5、reversal=1/5、volume=0；明确为三个因子结果。原常量自比较问题CLOSED。
- MATH-SUP-003：修订脚本用Fraction(float)取得binary64的精确有理数表示，实际计算绝对及非零参考值的相对误差并断言；±0.21误差约7.77e-18、0.6及-0.4约2.22e-17，与开发方独立计算一致。零误差误述核心问题RESOLVED，容差不变。
- 范围：修订脚本明确只验证数学，不能替代SDK、安全、CI。新的修订数学原件及提供日志现在已收到，不能继续笼统称“修订数学执行原件缺失”。

完整阅读后确认仅标准库算术/print/assert，无网络/文件访问/动态执行。开发方在仓库外以CPython3.13.16 -I -S复跑原字节，退出0、stderr空。所供日志显示3.11.2；只规范化换行/末尾换行、以及唯一Python版本banner后，其余内容完全一致。没有把完整日志称为逐字节相等，没有隐去版本差异。真实命令、输出/hash、run_id及独立Fraction结果见revised-math/checks.json。

提供的Gemini数学源/日志可支持其有限数学验证记录；开发方复跑不认证历史运行时点/环境，也不补记Gemini完整SDK执行。脚本header/log标明审查SHA，但没有程序性校验Git checkout，仍是对冻结算式输入的标准库验证。

## 非阻断性展示及字节说明

1. 报告写脚本9528 bytes、hash前缀4d71b9db4c2362e3；实收9527 bytes、hash为a4d6...。只在开发方内存诊断中追加一个末尾LF，候选变体为9528 bytes、完整hash 4d71b9db4c2362e399b7edcd08a2a875c1a7240ec331078b79e7ef66336933be，与报告提供前缀及大小相符。可解释为一个末尾换行差异；未给报告中的完整hash，不能把候选变体冒充实收原件。**原始文件不补换行，实际完整hash为归档依据**。日志实收大小/hash前缀与报告一致。
2. 参考值0时，代码跳过relative断言是正确的绝对容差处理，但打印rel_err=0和“rel<=...”不应读成相对误差已定义或已验证；报告已说明数学上N/A。开发方记录明确N/A，不改原件。
3. 源码assert用严格<，打印文字用<=；本次结果严格位于两门槛内，没有改变业务容差，也没有实际误判。保留为展示差异。
4. “ALL6”是沿用汇总标签，不能当作测试覆盖计数或全部Golden。代码有8次check_tolerances调用及公司行动算术，本轮只确认实际执行和已核算的算式。脚本内“business code100%correct”不能由未导入业务的数学脚本证明。

## 十二项裁定：记录原意见，同时核对说明是否真实对齐

| ID | Gemini标签 | 开发方接收结论 |
|---|---|---|
| ERR-P2-IMPL-001 | AGREE/CLOSED | PARTIAL：仍把PR标题写为旧plan/pre-review标题，并称修改BASELINE.md。实际标题feat: Phase 2 Factor Registry and reviewed builtin signals；79c91e4→0b5107f未改docs/BASELINE.md，状态改动还含AGENTS/README/DECISIONS/ROADMAP等。代码冻结结论成立，报告元数据需更正。 |
| ERR-P2-IMPL-002 | AGREE/CLOSED | PARTIAL：无完整DAG义务获认可，但解释仍把FACTOR-011写成依赖声明/拓扑检查。canonical实际为P2注册替换/API版本兼容；Volatility为FACTOR-008/POST7/Deferred，不为后续阶段新增DAG义务。 |
| ERR-P2-IMPL-003 | AGREE/CLOSED | ACCEPTED：compute(view,context)、输入血缘不需虚构input_data_hash等方向一致。具体字段在Signal rows与context/config中，以源码为准。 |
| ERR-P2-IMPL-004 | AGREE/CLOSED | NOT FACTUALLY ALIGNED：解释再次声称src/aqrp/core/security.py与protocols.py，均不存在。实际core/security/__init__.py与factors/contracts.py；原coverage默认排除坐标contracts.py289–291（Protocol相关），非protocols.py。不造文件迎合文字。 |
| ERR-P2-IMPL-005 | AGREE/CLOSED | PARTIAL：无mypy/pyright独立执行已认可，但TEST_ONLY仍被混称准入状态；ENGINEERING_APPROVED是state，TEST_ONLY是environment/用途，financial_approval=NONE。两项Low限定关闭保留。 |
| ERR-P2-IMPL-006 | AGREE/CLOSED | VERIFIED/CLOSED：原输入正式-0.4与Golden输入正式0.6都被正确独立推导，修订源/日志支持。 |
| ERR-P2-IMPL-007 | AGREE/CLOSED | VERIFIED CORE RESOLVED：非零浮点绝对/相对误差实际计算；零参考值和打印比较符的展示差异见上，不否定本次算式结果。 |
| ERR-P2-IMPL-008 | AGREE/CLOSED | PARTIAL：依赖available<=decision已认可，但解释仍把信号available_at泛称盘后安全点。正式合成实现available_at=冻结decision_time，logical_compute_delay=0，不能推定真实市场盘后时刻。 |
| ERR-P2-IMPL-009 | AGREE/CLOSED | ACCEPTED：AST/只读对象不是OS沙箱、不覆盖全部漏洞、外部不可信插件Unsupported的边界已明确。 |
| ERR-P2-IMPL-010 | AGREE/CLOSED | PARTIAL SCOPE CLARIFIED：旧预审与新数学修订原件现均收到；不能据此称原实现报告另述的综合AST/数学/hash工具已提供。该综合工具仍无源/日志原件，现报告对其功能的描述按自述保留，不制造原件。 |
| ERR-P2-IMPL-011 | AGREE/CLOSED | ACCEPTED SCOPE DISCLOSURE：ZIP本轮为Evidence Reviewed Only，完整SDK为NOT VERIFIED已明确，不再猜测本次独立下载/运行；开发方/CI证据与Gemini独立数学分开。未附的SDK尝试原始命令输出不补造。 |
| ERR-P2-IMPL-012 | AGREE/CLOSED | ACCEPTED：用户批准/合并/标签/下一阶段权限分开。报告“法定”按项目治理理解；RELEASED后仍须Phase3独立授权。 |

因此可以登记“Gemini十二项均标AGREE/CLOSED”，但不能把上述仍重复错误的说明写成“双方全部事实已对齐”。尤其001/002/004需改正，005/008/010需限定表述/证据范围；这不是发现新的金融业务缺陷，不据此改变正确源码、需求或Golden。报告CI链接的Google搜索包装不作证据源，使用GitHub直接run链接。

## 更新后的剩余条件

- 数学实质缺陷已解决、修订原件/日志已收到，不再沿用“Volume漏-1/证券B常量比较仍未修”的当前状态；旧版本仅保留历史。
- 原报告PASS/本增量PASS及READY均为审查建议；仍须报告说明对齐上述事实，不能只凭AGREE标签宣告全部争议闭环。源码/目录/元数据的更正无需新增业务能力。
- 修订数学脚本只做数学，不含hash/ZIP/SDK执行。Gemini明确本轮ZIP是Evidence Reviewed Only，完整CPython3.13.16 SDK独立执行仍NOT VERIFIED；相关独立执行未完成，用户是否接受限制尚未决定。开发方与双OS CI254项证据继续保留，不能补记为Gemini执行。
- 原实现报告称综合AST/math/hash工具的实际原件/执行仍未收到；若不提供，保留NOT VERIFIED及范围澄清，不能用本数学脚本代替。
- 用户Phase2人工验收、是否接受限制、合并/标签授权、main获批范围/适用检查/基线发布核验均未完成。Phase3独立启动尚未授权，保持BLOCKED。

本轮只更新原件、核对证据及状态，main/稳定标签不动；不合并、不打标签、不进入Phase3。
