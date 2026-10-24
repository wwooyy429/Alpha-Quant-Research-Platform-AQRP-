"""Write final conclusions only after every required independent verification completes."""
from pathlib import Path
import json,datetime,hashlib
O=Path(__file__).parent;C=Path('E:/WORK/AQRP-audits/p6-3017a09/src')
FIX='3017a097b49ecdae68228ca9a417fcd03c313200'
get=lambda n:json.loads((O/n).read_text(encoding='utf-8-sig'))
sdk=get('INDEPENDENT_SDK_VERIFICATION.json');assert sdk['SDK_exit']==0 and sdk['pytest_tests']==1567
assert get('COVERAGE_VERIFICATION.json')['result']=='PASS'
assert get('INDEPENDENT_CAMPAIGN_RECHECK.json')['result']=='PASS'
assert len(get('INDEPENDENT_CANCELLATION_RECHECK.json')['records'])==8
assert get('INDEPENDENT_UNIVERSE_RECHECK.json')['result']=='PASS'
assert get('INDEPENDENT_FILL_LITERAL_CHECK.json')['result']=='PASS'
assert get('DEVELOPER_SOURCE_AND_DEFAULTS_READBACK.json')['result']=='PASS'
assert get('INDEPENDENT_WAL_RECHECK.json')['result']=='PASS'
assert get('HISTORY_AND_DEVELOPER_BROWSER_VERIFICATION.json')['result']=='PASS'
assert get('CRASH_LIFECYCLE_AND_IDENTITY_CONTROLS.json')['result']=='PASS'
assert get('BROWSER_STOP.json')['remaining']==0
assert get('DEVELOPER_ARCHIVE_VERIFICATION.json')['result']=='PASS'
env=get('ENVIRONMENT.json');obs=get('BROWSER_ACTIONS.json')
findings=[
 dict(id='WORK-P6-G2-001',severity='High',status='CLOSED — FIX VERIFIED',location=['src/aqrp/services/task_campaigns.py:76','src/aqrp/services/task_campaigns.py:188','src/aqrp/services/task_state.py:181','src/aqrp/experiments/ledger.py:275','src/aqrp/services/research.py:519'],basis='P3统计契约禁止事后换family绕过预算/多重检验；G1同根试验历史与预算要求',evidence='INDEPENDENT_CAMPAIGN_RECHECK.json',disposition='Immutable campaign declarations and common Holm definitions; atomic same-data quota, cross-family contamination and nonrefund independently verified.'),
 dict(id='WORK-P6-G2-002',severity='Medium / blocking',status='CLOSED — FIX VERIFIED',location=['src/aqrp/services/tasks.py:468','src/aqrp/services/tasks.py:509','src/aqrp/services/tasks.py:723'],basis='P6取消/完整完成屏障与P5未知财务状态必须失败关闭',evidence='INDEPENDENT_CANCELLATION_RECHECK.json',disposition='Re-read actual journal, anchor, file set and complete financial projection, including completed replay and source. Unknown cancellation becomes FAILED/COMMITTED_STATE_UNVERIFIED.'),
 dict(id='WORK-P6-G2-003',severity='Medium / blocking',status='CLOSED — FIX VERIFIED',location=['src/aqrp/ui/app.py:285','src/aqrp/services/task_requests.py:264','src/aqrp/services/task_inputs.py:67'],basis='UI-003 canonical股票池选择及P1时点成员契约；G1研究/回测两入口范围',evidence='INDEPENDENT_UNIVERSE_RECHECK.json',disposition='Actual CUA TAIL4/Core4, immutable P1 memberships, P3 rows and P5 sidecar verified; all three pool IDs have CLI/SDK canonical parity.'),
 dict(id='DEV-P6-004',severity='Medium / required concurrency verification',status='CLOSED — FIX VERIFIED within restricted engineering scope',location=['src/aqrp/services/task_state.py:53','tests/ui/test_task_state_setup.py:1'],basis='Observed actual C5 SDK native WAL lock failure and required multiprocess task admission',evidence='INDEPENDENT_WAL_RECHECK.json',disposition='Before-BEGIN retry only for primary BUSY/LOCKED with finite deadline, confirmed WAL; no body/commit replay. New fixed SDK and40 additional real processes verified. Historical native crash cause remains unproved.'),
 dict(id='DEV-P6-002',severity='Developer lifecycle finding',status='CLOSED — FIX VERIFIED (connection lifetime)',location=['src/aqrp/services/task_campaigns.py:38'],basis='Read-only sqlite connections need explicit closure on success/error',evidence='Fixed SDK tests/ui/test_g2_campaigns.py lifecycle controls',disposition='contextlib.closing and both actual connection lifecycle controls verified.'),
 dict(id='DEV-P6-003',severity='Developer abrupt-death harness finding',status='CLOSED — engineering harness FIX VERIFIED; original native cause NOT VERIFIED',location=['tests/ui/crash_support.py:1'],basis='Original C3/C4 strict exit failures; six deliberate process-death boundaries must remain strict',evidence='Fixed SDK raw crash markers and six recovery controls; prior failure originals retained',disposition='Actual strict self-TerminateProcess/os._exit records and same-run recovery verified; no claim exact old native cause proved.'),
 dict(id='DEV-P6-001',severity='Original developer browser defect',status='CLOSED — FIX VERIFIED (prior independent disposition maintained)',location=['src/aqrp/ui/app.py'],basis='Prior independent two-session CAS/default history [3,2,4,3]',evidence='prior-independent-inputs/REPORT.md + HISTORY_AND_DEVELOPER_BROWSER_VERIFICATION.json',disposition='Relevant editor behavior unchanged; current SDK regressions and developer raw browser sequence preserve fix. Current reviewer browser work covers pool selection, not a falsely claimed repetition of all earlier browser cases.')]
# Verify actual editor path instead of guessing its module name.
findings[-1]['location']=['src/aqrp/ui/app.py (unchanged defaults-editor logic)']
(O/'FINDINGS.json').write_text(json.dumps(dict(fixed_sha=FIX,verdict='G2 PASS — restricted engineering scope',new_open_findings=[],findings=findings),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
report=f"""**Phase6 固定版本 G2 独立复核：PASS（八项受限工程范围）。**

固定 SHA：`{FIX}`。PR：[#9](https://github.com/wwooyy429/Alpha-Quant-Research-Platform-AQRP-/pull/9)。执行者为 GPT Work 主审；未使用子代理或改写为 Gemini 执行。日期为2026-10-24。

WORK-P6-G2-001、002、003 均 **CLOSED — FIX VERIFIED**；DEV-P6-004 的并发准入修复在本工程范围确认通过；DEV-P6-001 维持此前独立关闭。当前未发现新的阻断问题。本结论仅覆盖以上完整SHA，不外推到漂移HEAD、后续归档提交或最终集成宿主。旧eae807f的BLOCKED报告及失败反例继续作为真实历史保留。

**固定身份、范围与依赖**

已从PR描述实际读取 `AQRP_FIXED_REVIEW_SHA: {FIX}`，确认PR未合并，独立clone后detached checkout该提交。未创建开发分支、编辑候选源码或测试。独立目录：`{C}`。Git commit对象自身SHA1、整树、工作区干净状态与最终远端引用均核验。

原106项目录不变；Phase6是UI-001–008，共5 MVP /3 Competition Ready，八项全部属于适用验收范围。G1合同及原32＋95组答案保持原字节。归档起点0242db37b4c822e7c73ef6c17faf104bcea54892的5016个受保护文件逐一匹配Git blob及SHA256；5108个固定Git文件与开发实际SDK源码归档匹配。原22个显式适配项未静默扩展到冻结文件。

core锁及G1已审UI锁不变；Windows22/Linux21个core wheel、每平台29个UI wheel均按锁中hash核对。候选为0.6.0.dev5、83源码模块，bundle `28c3cc049efcce8fc3e55b4056e8e116f98deca39eeb1d2c8822799c8e98855b`。新增模块是受限campaign管理；未加入通用DAG、任意外部插件、真实行情/账户接入或P7业务。

main、phase5-baseline、v0.5.0保持 `59246f9fd391c1713b6bed65dd22280f4d248493`；旧标签未移动。证据见SCOPE_IDENTITY_VERIFICATION.json、FINAL_LOCAL_IDENTITY.json及REMOTE_REFS_START/FINAL。

| 需求 | 等级 | 适用能力及本次证据 | 结论 |
|---|---|---|---|
| UI-001 | MVP | Dashboard状态/真实任务与完整性错误；完整SDK及开发六页原始观察 | PASS |
| UI-002 | CR | 固定Ref、参数/选择/权重及配置版本；SDK两因子链、旧Ref、数值对照、默认编辑回归 | PASS |
| UI-003 | MVP | P1历史股票池实际驱动P3、五阶段、IC/Rank IC/ICIR、分层/衰减/OOS和缺失原因；本轮真实浏览器与原始行 | PASS |
| UI-004 | MVP | 真实P5内部P4、现金桶/应收应付/订单成交持仓/净值回撤；98.1/998.1/9股及损坏取消反例 | PASS |
| UI-005 | CR | 固定配置/版本比较、声明投影重放、原工件下载及源只读；原66文件/三旧run与SDK、开发浏览器原件 | PASS |
| UI-006 | CR | 追加默认配置/CAS/回滚、旧请求不变、日志和依赖；旧独立DEV001结论与本轮回归/开发原始[3,2,4,3] | PASS |
| UI-007 | MVP | SDK、旧CLI、任务CLI、AppTest真实两因子研究和精确金融一致；本轮三股票池CLI/SDK canonical一致 | PASS |
| UI-008 | MVP | SQLite幂等/唯一claim/固定槽位、全任务完成、取消/恢复、错误不提成功；完整SDK及独立并发/损坏控制 | PASS |

这里的PASS沿用已批准受限工程边界，不将正式Test、金融批准、真实OS隔离或完整历史宿主认证标为已实现通过。Competition Ready等级没有被删去。

**三项原发现的独立处置**

1. **WORK-P6-G2-001，High，CLOSED — FIX VERIFIED。**
位置：task_campaigns.py:76/188、task_state.py:181、ledger.py:275、research.py:519。旧问题是参数改变自动获得新family及一份干净额度。本版在不可变campaign中提前固定完整候选及共同Holm定义；Task提交与同数据额度预留在SQLite中原子执行。

实际installed wheel反例：未经登记的原14个lookback变体仅初始值获准，后13个均UNREGISTERED_CAMPAIGN_VARIANT，campaign/试验文件及Task无新增副作用；显式登记14个变体后同一family及14项固定Holm分母，前12个真实P3成功、13/14失败并保留预留记录。另起名称的计划仍被预算拒绝。两个真实跨计划研究保留历史并标污染，原拥有Task的P3 trial不双重计数。并发提交两个因子×两个期限（无composite）的4单位Task，累计预留0/4/8/12，三项排队、一项预算失败；取消三项后新计划仍见16单位历史并失败，幂等不重复扣额。见INDEPENDENT_CAMPAIGN_RECHECK.json及两轮原始helper日志。

边界是同工程workspace及数据身份；这不能防止人为复制/删除整个工作区，不能代表独立Test样本或跨宿主安全隔离。默认first-use有限候选仅工程便利，正式预注册/金融批准仍未获得。

2. **WORK-P6-G2-002，Medium blocking，CLOSED — FIX VERIFIED。**
位置：tasks.py:468/509/723。旧问题是已完成P5在取消收尾仅信任旧已知状态。现在重读物理事务目录、初始锚、完整链、实际文件集合及完整财务projection；重放同时核验子运行和源。

主审实际执行8组：有效取消、原末笔commit追加空格、删除initial锚、添加未声明文件、重放子运行损坏、重放源损坏、成功后读到损坏、有效重放取消。损坏取消均FAILED / COMMITTED_STATE_UNVERIFIED，保留取消意图及核验错误，不返回成功结果；有效前缀仍CANCELLED。非取消的成功后损坏公开为INTEGRITY_ERROR/usable=false而数据库原SUCCEEDED保留。另验证已CANCELLED后损坏公开为INTEGRITY_ERROR，原CANCELLED历史不改写。见INDEPENDENT_CANCELLATION_RECHECK.json；原始被篡改前字节及新损坏副本均封存。未观测到新版本用未知账本认证98.1的错误行为。

3. **WORK-P6-G2-003，Medium blocking，CLOSED — FIX VERIFIED。**
位置：ui/app.py:285、task_requests.py:264、task_inputs.py:67。两网页表单、CLI/SDK均可选SYN_U、SYN_CORE4、SYN_TAIL4；请求绑定P1快照和历史成员身份，未知池明确拒绝。

主审真实CUA提交TAIL4研究与CORE4工程流水线并核对SQLite/冻结请求/原始产物：TAIL4的P3实际成员003–006，CORE4为001–004。CORE4的48行P5侧车按各event_time与同P1成员契约逐行对照；排除池外标的，金融结果现金98.1、权益998.1，原9股成交答案不变。三池CLI/SDK请求canonical相等且池间hash不同，未知池拒绝不增加Task。见INDEPENDENT_UNIVERSE_RECHECK.json、17份主审浏览器观察、4张原JPEG。这是实际计算选择，不只是下拉框截图。

**SQLite新增修复及历史失败**

task_state.py:53只在BEGIN之前，对主错误码BUSY/LOCKED执行单调时钟限定的WAL准入等待；显式确认返回wal，设置synchronous FULL，并将剩余时间交给busy_timeout/BEGIN。正文、commit不重放，非锁错误、无法确认WAL、超时均传播并关闭连接。这与[SQLite对busy handler不保证被调用的说明](https://www.sqlite.org/c3ref/busy_handler.html)及[主错误码低8位定义](https://www.sqlite.org/rescode.html)一致；这些说明不能证明旧原生崩溃的精确原因。

DEV-P6-002只读连接生命周期修复（task_campaigns.py:38的closing及正常/异常两项实际连接控制）确认关闭。DEV-P6-003六断点强制结束控制在本工程验证范围关闭；旧原生原因NOT VERIFIED单列保留，不把测试机制修复当原生原因证明。

主审新增固定安装包40个真实进程（4个新目录×10），每目录唯一workspace及Task，40/40 exit0；真实rollback-journal reader持锁释放后成功、有限期限耗尽不建workspace、正文BUSY只执行一次并回滚均通过。完整SDK还执行新增7项确定性控制及原十进程用例。DEV-P6-004据此在本范围关闭。见INDEPENDENT_WAL_RECHECK.json及所有子进程原始日志。

C3/C4 Windows原生退出失败、C5本机WAL真实缺陷和Windows首轮环境拒绝原始ZIP/日志保留并核CRC/hash；后来的成功不抵消历史失败。无原生栈，精确DLL/指令原因仍未证实。Windows崩溃控制现用self-TerminateProcess、Unix用os._exit，仍在实际断点强制结束，严格核73/74/75、原run恢复、试验不重复和源字节不变；没有将0xC0000005当成功。测试机制足以验证本轮声明的进程终止/恢复契约，不把它描述为证明所有原生崩溃原因已消失。

开发120进程仅提交前editable/dirty预检，不算本固定SHA clean SDK；旧负控第一轮无效、修订native timeout0负控与原default30竞争不是完全相同的复演；包装器exit1误判与原输出也保留。具体处置见开发指令、HISTORY_AND_DEVELOPER_BROWSER_VERIFICATION.json及封存原件。

**实际执行与证据等级**

主审环境：{env['python']}；{env['os']}、x64、标准GIL。基础解释器：`{env['executable']}`，SHA256 `{env['interpreter_sha256']}`。SDK创建独立新venv并从hash锁安装，复用的是已留存wheel字节，未复用旧已安装环境，也不宣称全程离线。

主审独立完整SDK：**1567 passed /0 failed /0 errors /0 skipped**，clean固定源码、wheel/安装/source83模块一致，全部模块覆盖门槛、原阶段烟测、扫描控制、两个因子的SDK/旧CLI/任务CLI/AppTest研究与精确金融、原66发布文件及三旧run重放通过。保留同进程runpy入口测试的两条RuntimeWarning，不声称零警告。原20＋4回归、独立数学91项通过；先前Fraction独立答案对本轮installed numbers执行852输入×6种Decimal精度/陷阱，共5112次通过，expected未用AQRP实现生成。

SDK实际启动与结束：{get('SDK_START.json')['started_utc']} → {get('SDK_COMPLETION.json')['ended_utc']}。执行父目录与完整argv见SDK_START/COMPLETION.json，内部逐条命令/退出码/UTC见独立SDK压缩包commands.jsonl、commands.log、junit.xml、coverage.json、environment.json与upload-selection。主审脚本及运行器命令也在本目录 *.command.json / *.stdout.log / *.stderr.log，保留失败原件。

原始命令核心如下（所有路径和完整参数见收据，不以本摘录代替原日志）：

```text
git clone --no-local --no-checkout E:/WORK/AQRP-audits/p6-eae807f/src E:/WORK/AQRP-audits/p6-3017a09/src
git fetch --no-tags origin {FIX} 59246f9fd391c1713b6bed65dd22280f4d248493 446f0f995f0fabefb1e952e05b8e911f751286e0
git checkout --detach {FIX}
Python31316/python.exe -X utf8 E:/WORK/AQRP-audits/p6-3017a09/src/tools/ci.py
<new SDK venv>/python.exe -I probe_campaign_repairs.py
<new SDK venv>/python.exe -I probe_cancel_repairs.py
<new SDK venv>/python.exe -I probe_wal_repairs.py
<new SDK venv>/python.exe -I verify_own_universes.py
<new SDK venv>/python.exe -I run_original_extras.py
<new SDK venv>/python.exe -I verify_installed_numbers.py
```

双系统是主审核验收到的官方原包及实时GitHub API摘要，不冒充主审亲自操作远端runner或重新下载。固定[run40079197702](https://github.com/wwooyy429/Alpha-Quant-Research-Platform-AQRP-/actions/runs/40079197702)双job success、各1567/0失败错误跳过，head/source环境/wheel/锁/全部声明成员一致：

- Windows原ZIP198336918 bytes，SHA256 `1a286a16bf55d9b76dc018efc793aa1f77838a26bf109dfb441638b5078572b8`。
- Ubuntu原ZIP239459656 bytes，SHA256 `e8392f5dd2adb7953fd6e0e51cd2e28effc4da61a14feca8759ece504408242f`。
- 各265组current展开副本（7278文件）逐整子树反向成员集与原字节核对；这只证明字节一致，不证明原ACL或符号链接身份。
- 5108文件源码原ZIP88435541 bytes，SHA256 `416501153449e423005274870e2ce3397d1108ce292319a381eb123450d6c4d9`；官方CI ZIP没有源码整包，不把本地源码包冒充CI上传成员。

开发真实浏览器主观察57份/主截图27张，另有控制观察，六页、两个因子、五入口投影一致、原42文件只读、12旧请求不变、原下载、默认CAS/回滚及实际取消/风险失败证据已核。主审本轮只把自己的两次真实股票池提交称为亲自浏览器执行；其余开发观察与独立SDK覆盖分别标注。临时主审UI全部停止，端口拒绝，见BROWSER_STOP.json。

开发外层原ZIP1893714422 bytes，SHA256 `c2b0ad0b7403734ad178dfcb2f4c588c2ef18097dad10f9428af5514acfefcb8`；3328声明文件＋manifest共3329成员核CRC/大小/每成员hash。旧主审902364045-byte证据ZIP SHA256 `086c0a1d7128c241bff30cfed32f9d5178940c9decf3942cd462021f30983b3c`也重核304声明文件＋manifest，复制原字节保存在prior-independent-inputs/。本轮主审SDK包见INDEPENDENT_SDK_VERIFICATION.json，整个本轮证据包最终大小/hash/成员数见RECEIPT.json（外置、自身排除，不作循环hash或数字签名）。

**主审辅助执行更正**

旧archive核验器首次把嵌套BROWSER_FILES_SHA256.json后缀误认作根清单；改为精确根名后又因Git ZIP含目录成员触发“全成员等于文件集”的辅助断言。现明确5108文件/580目录，全部文件集与字节对照通过，没有放宽遗漏/重复成员或hash检查，原两轮辅助失败脚本/日志保留。

主审多因子预算辅助脚本初次误假设默认P3存在composite，因预期7项而实际5项声明停止；发生在该并发控制提交之前，未修改候选或正确金融答案。修订为实际配置“两个单因子×两个期限=4单位，加另一单期限变体共5项”，在全新目录重跑所有控制通过。第一轮已产生的原始工作区也封存，未伪称首次即通过。浏览器初始连接早于服务器就绪失败后，已就绪的新标签成功；未绕过任何安全屏障。上述辅助失败与产品历史失败分列。

最终六断点收据核验脚本首次读UI源码时遗漏UTF-8编码，Windows默认GBK产生UnicodeDecodeError；原脚本/日志保留，显式UTF-8重读后同一固定字节通过。SDK自身与候选代码不变。

**未验证、延期及用户决定**

- WI-R2-001/002和真实Windows三主体隔离继续 **DEFERRED / NOT VERIFIED**；本轮不启用账户、不修改真实ACL，不用角色/API或同OS用户冒充独立权限隔离。
- 正式Test **NOT RUN**；无部署能力的正式入口继续失败关闭。金融批准 **NONE**，统计显著或正IC不替代金融批准。
- 完整历史宿主复现仍 **NOT VERIFIED**；已验证的是接受的软件包/锁、旧Ref及声明结果投影，不能外推原OS、原CPU、原完整宿主或真实权限。
- 未来最终集成40位SHA的延期验证及真实权限执行需另行方案/授权，本次工程G2不能自动关闭它们。
- Phase6用户阶段验收及合并/建立基线/标签许可尚未授予；不得登记ACCEPTED/RELEASED，不进入P7。

本轮未合并、打标签、部署、实盘、运行正式Test、授予金融批准或进入P7。**技术审核G2 PASS不等于用户阶段验收或发布授权。**

实际截图（主审自己的合成工程任务）：

![CORE4工程回测成功，金融批准NONE]({O.as_posix()}/browser-observations/017-core4-success.jpg)
"""
(O/'REPORT.md').write_text(report,encoding='utf-8')
handoff=f"""GPT Work已对PR #9固定SHA {FIX} 完成Phase6八项受限工程范围G2独立复核，结论G2 PASS。WORK-P6-G2-001（High，共享预算/污染）、002（Medium blocking，账本损坏取消失败关闭）、003（Medium blocking，实际股票池）均CLOSED — FIX VERIFIED；DEV-P6-004并发准入修复在本工程范围通过，DEV-P6-001维持此前独立关闭。主审干净SDK1567项、双系统官方原包各1567项、原20+4/91数学、5112数值对照及新独立反例通过，原失败/反例/日志和精确原因未证实部分保留。详本轮REPORT.md、FINDINGS.json及RECEIPT.json。请将报告与完整原证据按原字节归档，清楚区分已审固定SHA与后续归档SHA；不要把后续漂移HEAD自动视为通过。此结论不代替用户Phase6验收或合并发布授权；当前不合并、不打标签、不部署、不实盘、不进入P7。WI-R2-001/002及真实Windows隔离继续DEFERRED / NOT VERIFIED，正式Test未运行、金融批准NONE，完整历史宿主边界保持，不启用账户或修改真实ACL。"""
(O/'DEVELOPER_HANDOFF.txt').write_text(handoff+'\n',encoding='utf-8')
print('Report and findings written after required independent checks PASS')
