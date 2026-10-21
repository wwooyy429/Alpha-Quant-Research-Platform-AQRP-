import hashlib, json, re, zipfile
from pathlib import Path
from datetime import datetime

ROOT=Path(__file__).resolve().parent
data=json.loads((ROOT/'execution-verification.json').read_bytes())
assert data['status']=='PASS'
assert (ROOT/'verification.exit.txt').read_text().strip()=='0'
assert (ROOT/'sdk.exit.txt').read_text().strip()=='0'
checks=data['checks']; local=checks['new_local_sdk']; env=local['environment']
RUN=ROOT/'runs'/env['run_id']; repo=ROOT.parent/'p1-31a548b'
TARGET=data['target_sha']; now=datetime.now().astimezone().isoformat()
link=lambda p:Path(p).as_posix()
sha=lambda b:hashlib.sha256(b).hexdigest()
with zipfile.ZipFile(ROOT/'fixed-source.zip') as z:
    for n in z.namelist():
        if not n.endswith('/'): assert z.read(n)==(RUN/'source'/n).read_bytes(),n
    core=json.loads(z.read('docs/audits/phase-1/implementation/CORE_PRESERVATION.json'))
    for i in core['files']: assert sha(z.read(i['path']))==i['sha256'],i['path']
    prefix='docs/audits/phase-1/repairs/data-validation/'
    evidence=json.loads(z.read(prefix+'EVIDENCE_MANIFEST.json'))
    for i in evidence['files']:
        raw=z.read(prefix+i['path']);assert sha(raw)==i['sha256'] and len(raw)==i['bytes']
snapshot_rows='\n'.join(f'| {k} | {v} |' for k,v in local['snapshot_replay']['rows'].items())
ci_rows='\n'.join(f"| {i['name']} | {i['artifact_id']} | {i['bytes']} | {i['sha256']} |" for i in checks['current_raw_ci_zip'])
ci_wheels='\n'.join(f"- artifact{i['artifact_id']}：wheel SHA256 `{i['wheel_hash']}`；运行目录 `{i['environment']['run_id']}`；原始环境 OS `{i['environment']['os']}`。" for i in checks['current_raw_ci_zip'])
report=f'''# GPT Work 补充审核 — 用户指定代执行报告

**固定目标：{TARGET}。本次代执行核验 PASS。**

用户本轮原话为“请代替Gemini执行证据”。据此，本次由 **GPT Work（Codex）作为用户指定替代执行者**，实际完成此前 WORK-P1-004 缺少的固定版本 SDK、当前双平台原始 ZIP、Git 拓扑、数据/查询及跨平台核验。本报告中的新运行不是上轮结果的复述，也不登记为 Gemini 执行。

**WORK-P1-004 本次固定目标的执行缺口已补齐，建议处置为 USER-AUTHORIZED SUBSTITUTE EXECUTION PASS。** 原“Gemini本人未执行”的历史不改写；本次不表示用户接受其他未验证限制，也不代签修复交付验收、合并或发布。

## A. 对象、权限、方法及实际执行

| 项目 | 事实 |
|---|---|
| 仓库 / PR | [AQRP PR #4](https://github.com/wwooyy429/Alpha-Quant-Research-Platform-AQRP-/pull/4)，Draft/Open，未合并 |
| 固定目标 | {TARGET}，开始时PR head/本地detached HEAD一致，结束远端仍一致 |
| base/main | f579b2c99e762085772de6e70ba1fa98792a7add |
| 独立只读副本 | `{link(repo)}`，SDK前后clean |
| 新实际 run_id | {env['run_id']} |
| 解释器 | 标准CPython3.13.16/x64/GIL；安装来源/路径与运行探针见原件 |
| 本轮起止 | 2026-10-21 23:08:16+08:00启动；验证完成{data['finished_at']}；报告{now}，Asia/Shanghai |
| 来源与工具 | 固定 Git 对象、GitHub只读连接器、原始Actions ZIP、PowerShell、隔离venv；输出/缓存/快照均位于非同步审核目录 |

已重新审阅原版 tools/ci.py、REPRODUCE、扫描器及原外置测试。SDK按原入口新建venv、按原锁使用require-hashes/only-binary安装、pip check、固定源码Git archive构建/安装真实wheel，随后执行静态检查、测试、逐模块覆盖率门槛、独立数学参考、八表快照查询和秘密扫描正负控制。未升级/重算依赖或改答案。额外证据核验从本轮新venv导入实际site-packages包，未用PYTHONPATH换入工作树源码。

## B. 授权及阶段边界

- 本次用户授权替代执行者。证据包的 EXECUTION_AUTHORIZATION.json 保存原话、目标、执行者和限制；该授权优先于既有“等待Gemini执行”分工，执行来源必须保留真实身份。
- 正式源码、测试、Golden、锁、项目状态、Gemini原件和PR均未修改；未建审计分支、提交、推送、合并、打标签、发布或向其他聊天/人员发送消息。
- main仍为f579b2c99e762085772de6e70ba1fa98792a7add；phase0-baseline目标仍为7de1d0e81385ae97f98ea673fe05dd726f0b577b；phase1-baseline仍为f579；Phase2分支仍为947467b9d094905cab0af37ec5cc53f1d187e755。
- 原Phase1验收/发布记录与当前修复交付分别判断。本报告没有登记新的ACCEPTED/RELEASED，也没有启动或验证Phase2–7。

## C. 问题处置与本次结论

| ID | 本次核实 | 处置建议 |
|---|---|---|
| WORK-P1-004 / Medium证据缺口 | 在目标{TARGET}真实新跑完整SDK；下载并核对该目标的两份原始CI ZIP；核对实际checkout拓扑并执行八表/查询/跨OS重放 | **本次用户指定替代执行PASS，执行内容缺口已补齐；不称Gemini已执行** |
| WORK-P1-001–003、006–009 | 本轮新SDK234/0/0/0、原始未改16反例与正向控制16/0/0/0；包17模块与固定源码一致 | 七项修复经GPT Work实际执行再次通过，未发现新阻断问题 |
| WORK-P1-005 / Medium证据缺口 | 当前run原ZIP均含真实wheel/.coverage；各23项选择文件及12项上传根清单hash匹配，2工具字节明确省略 | 新上传策略证据通过；原历史未上传字节保持NOT VERIFIED |

004关联QA-002、ENV-001、ENV-002。原定位为固定副本recheck-3ab93b3/RECONCILIATION.md第20行和round2/EXECUTION_EVIDENCE.md第28行。预期是有实际固定版本命令、环境、退出码、SDK/ZIP/数据执行，而非静态PASS文字。本次新原件已提供这些内容；原来要求Gemini执行的分工由用户本轮明确改为代执行，未假称来自Gemini。

本轮无已确认的新实现缺陷。SDK、原始16回归、ZIP核验均无失败；不存在靠改项目答案、删失败用例或降低覆盖率门槛得到PASS。历史失败原件保持原处。

## D. 需求→实现/测试→实际证据→状态

| 需求 | 本轮实际证据 | 状态 |
|---|---|---|
| DATA-001、DATA-011 | schemas/quality/units/query；单位、股数、Decimal及跨市场用例，原001回归 | PASS |
| DATA-002、DATA-003 | time/pit/quality；双时间、IANA/DST、精度、未知可得性及原006/007/009回归 | PASS |
| DATA-004 | actions/ex-session；拆股/分红/时序与原002回归、独立参考 | PASS |
| DATA-005 | universe/status/alias、历史区间及PIT入口测试 | PASS |
| DATA-006 | OHLC缺失组合、整数位宽、计数守恒；原003/008回归 | PASS |
| DATA-007、DATA-008 | 三套真实快照（本轮本地/Windows CI/Ubuntu CI），各八表文件与manifest独立hash、验证读取、SDK查询重放 | PASS |
| DATA-009 | mutation与有效正向控制、晚到/未来修订泄漏防御 | PASS |
| ENV-001 | 新venv、22活动锁包版本、真实安装来源、17模块hash、精确解释器和真实wheel | PASS |
| ENV-002 | 当前run两端原件、attempt1、checkout真实父/树、完整上传清单 | PASS |
| SEC-002 | 固定扫描器hash下载、正负控制和实际源码扫描通过 | PASS |
| QA-002 | 本轮234+原始16测试、逐模块行/分支门槛、参考计算/集成 | PASS；004由本次用户指定替代执行补齐 |

Phase0本轮只重新核对50项冻结文件及稳定标签，并核对336项修复证据；未宣称新做Phase0全面设计审查或将设计算例当作后续实现。

## E. 原始执行结果、Git/ZIP核验与边界

| 本轮实际运行 | 结果 |
|---|---|
| 完整SDK | **234 passed，0失败/0错误/0跳过，exit0，complete=true，dirty=false** |
| 原始外置回归 | **16 passed，0失败/0错误/0跳过，exit0**；原两份脚本hash与既有原件一致，输入Golden也与当前固定源码一致 |
| 安装与wheel | 22活动锁包版本符合锁；17安装模块及wheel模块与固定源码逐字节一致 |
| 本地wheel SHA256 | `{env['wheel_sha256']}`；这是本次构建原字节，与CI wheel分别记录 |
| ruff / 覆盖率 / 参考 / 数据 / 扫描 | 静态与格式、逐模块行/分支门槛、Fraction/Decimal参考、快照查询、扫描正负控制均通过 |
| 固定资产 | 50/50冻结文件和336/336修复证据hash重新匹配；Git archive与本次SDK构建源逐文件一致 |

实际核对当前[run39620574953](https://github.com/wwooyy429/Alpha-Quant-Research-Platform-AQRP-/actions/runs/39620574953)，不是以旧业务run代替本次新原件：

| 原件 | artifact ID | ZIP字节 | SHA256（与GitHub官方digest一致） |
|---|---|---|---|
{ci_rows}

每端原件环境均complete=true、dirty=false、Python3.13.16，GitHub run_id=39620574953、attempt=1、code_commit/GITHUB_SHA为 **fa1d53620be60d683538b428a2a9cd29035b0127**。本轮实际获取并检查该Git对象，父为main f579和固定目标31a；tree **995849f2c7b2d73fbcacb38de84d1cc143d0b2f8** 与目标tree相同。这是CI临时合并，main没有被合并。

每份ZIP安全检查无路径越界/符号链接/重复名，恰有24文件：23项选择文件与排除自身的upload-selection；各12项上传根文件逐hash匹配。真实wheel hash与environment一致，17模块匹配目标；.coverage为真实SQLite；JUnit各234/0/0/0，覆盖率门槛重新执行通过，扫描报告为空。两个工具字节（扫描器、pip引导wheel）按上传策略显式省略，不假称已从CI原件重新得到其原字节。

{ci_wheels}

三套实际快照均有八表，表文件hash与各自manifest匹配；逻辑manifest digest使用外置标准库独立重算。使用本次新安装SDK分别加载本地及两端CI快照，查询结果字节与各自原smoke-result及其hash一致。三套八表逻辑数据、查询行与配置一致；唯一比较排除为表行snapshot_id及配置snapshot_id/manifest_hash（各自原始manifest/分片仍完整核对，不改写原件）。这证明重现一致性；金融正确性还由独立参考与Golden测试支持，不把“同一SDK得到相同答案”单独当作正确性证明。

| 表 | 本地快照行数（两端逻辑数据一致） |
|---|---|
{snapshot_rows}

**证据入口：** [全部核验结果]({link(ROOT/'execution-verification.json')})、[SDK完整命令/输出]({link(RUN/'commands.log')})、[SDK环境]({link(RUN/'environment.json')})、[16项日志]({link(ROOT/'original16.stdout.log')})、[额外核验命令/退出码]({link(ROOT/'verification-commands.jsonl')})、[原始证据总清单]({link(ROOT/'EXECUTION_EVIDENCE_MANIFEST.json')})。两份原ZIP直接保存在本报告同目录。

**保留边界：** 本次没有启动新的Linux本地安装，Linux部分是当前Ubuntu CI原件的实际核验及在本次Windows SDK中的重放；不声称Gemini本人执行。旧历史CI未上传字节仍NOT VERIFIED，本次授权不等于用户接受所有旧限制。先前jobs包装API的Windows作业顶层状态不一致记录保持原件，本次完整ZIP的环境、JUnit、attempt和hash已直接核验，不依赖其顶层状态文字作结论。真实供应商、账户/订单/凭证、修复验收/发布及Phase2集成均不在本轮执行范围。

## F. 给Codex的接收与复核任务

1. 按本轮用户原话接收该报告及原件，记录“{TARGET}：WORK-P1-004 用户指定GPT Work替代执行PASS”。同时保留“原Gemini本人未执行”的来源历史，不改写旧报告。
2. 关联新run {env['run_id']} 的234通过、原外置16通过、当前run39620574953两份原ZIP、Git拓扑和三套数据/查询一致结果；不要再将本轮写为“仅hash、未运行SDK/ZIP”。
3. 001–003、006–009保持补充复核通过；005只登记当前新策略/可得原件通过，旧缺字节继续NOT VERIFIED。不需要本轮新增业务修复，不改Golden/容差/锁。
4. 本报告未改正式状态；后续由开发方在正常接收流程更新记录。用户验收、合并/标签/发布及Phase2受控纳入分别遵守实际授权；如业务/测试/工具/锁变化，提供新完整SHA及相应验证。

**结论：用户指定替代执行的技术证据关卡通过；WORK-P1-004本次固定目标的实际执行缺口已补齐。执行者为GPT Work，未冒充Gemini，未登记修复交付验收或发布。**
'''
(ROOT/'GPT-Work-User-Designated-Execution-31a548b.md').write_text(report,encoding='utf-8')
checklist=f'''# 给Codex的代执行接收单

用户原话：“请代替Gemini执行证据”。固定目标：{TARGET}。

- WORK-P1-004：USER-AUTHORIZED SUBSTITUTE EXECUTION PASS；实际执行者GPT Work，不是Gemini。原Gemini未执行历史不改写。
- 新SDK run {env['run_id']}：234通过；原始未改外置16通过；coverage/参考/扫描正负控制均通过。
- 当前CI run39620574953/attempt1，两份原ZIP已实际下载/校验/解包；每端234通过、23选择文件/12上传根文件、wheel/.coverage/八表/SDK查询通过。
- 实际CI checkout fa1d53620be60d683538b428a2a9cd29035b0127 的父和tree已实际Git核对；三套逻辑数据/结果一致。
- 001–003、006–009补充通过保持；005新策略通过，历史缺字节NOT VERIFIED。本轮无新增代码修复要求。
- 接收报告及EXECUTION_EVIDENCE_MANIFEST.json并记录真实来源；本次不是用户验收、合并/标签/发布或Phase2集成授权。
'''
(ROOT/'Codex-Delegated-Execution-Receipt-Checklist.md').write_text(checklist,encoding='utf-8')
receipt={'executor':data['executor'],'target_sha':TARGET,'user_instruction':'请代替Gemini执行证据',
 'finding':'WORK-P1-004','disposition':'USER-AUTHORIZED SUBSTITUTE EXECUTION PASS',
 'actual_gemini_execution':False,'historical_gemini_non_execution_unchanged':True,
 'formal_repository_status_modified':False,'acceptance_merge_release_authorized_by_this_report':False,
 'report_generated_at':now,'sdk_run':env['run_id'],'sdk_pass':234,'original16_pass':16,
 'raw_zip_ids':[i['artifact_id'] for i in checks['current_raw_ci_zip']],
 'preserved_core_files':len(core['files']),'repair_evidence_hashes':len(evidence['files'])}
(ROOT/'EXECUTION_DISPOSITION.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')

for md in ROOT.glob('*.md'):
    for p in re.findall(r'\]\(([^)]+)\)',md.read_text(encoding='utf-8')):
        if p.startswith('C:/') and not p.endswith('/EXECUTION_EVIDENCE_MANIFEST.json'):
            assert Path(re.sub(r':\d+$','',p)).exists(),p
selected={p for p in ROOT.iterdir() if p.is_file() and p.name!='EXECUTION_EVIDENCE_MANIFEST.json'}
selected.update(p for p in RUN.iterdir() if p.is_file())
for folder in (RUN/'wheel',RUN/'dataset',ROOT/'zip-replay'):
    selected.update(p for p in folder.rglob('*') if p.is_file())
entries=[]
for p in sorted(selected):
    raw=p.read_bytes();entries.append({'path':p.relative_to(ROOT).as_posix(),'bytes':len(raw),'sha256':sha(raw)})
manifest={'executor':data['executor'],'target_sha':TARGET,'generated_at':now,
 'scope':'Report/scripts/commands/raw outputs/original ZIPs, actual new SDK root and wheel/dataset, extracted original CI evidence; excludes self, venv/caches/build source. Full fixed source ZIP is included.','files':entries}
(ROOT/'EXECUTION_EVIDENCE_MANIFEST.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'report':str(ROOT/'GPT-Work-User-Designated-Execution-31a548b.md'),'files':len(entries),
 'status':'PASS','sdk':234,'original16':16,'raw_zip_verifications':2,'disposition':receipt['disposition']},ensure_ascii=False))
