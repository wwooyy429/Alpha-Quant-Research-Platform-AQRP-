import hashlib, json, re
from pathlib import Path
from datetime import datetime

ROOT=Path(__file__).resolve().parent
data=json.loads((ROOT/'evidence-verification.json').read_bytes()); checks=data['checks']
assert data['status']=='EVIDENCE VERIFIED; PROJECT REVIEW BLOCKING'
assert (ROOT/'verification.exit.txt').read_text().strip()=='0'
assert (ROOT/'query-identity.exit.txt').read_text().strip()=='0'
TARGET=data['target_sha']; repo=ROOT.parent/'p2-c70727c'
env=checks['new_local_sdk']['environment']; run=ROOT/'runs'/env['run_id']; source=run/'source'
link=lambda p:Path(p).as_posix()
sha=lambda b:hashlib.sha256(b).hexdigest()
now=datetime.now().astimezone().isoformat()
bundle={'factor_api':'1.0.0','data_contract':'contracts/1.0.0','dependency_lock_sha256':sha((source/'requirements.lock').read_bytes()),
        'files':[{'path':p.relative_to(source/'src/aqrp').as_posix(),'sha256':sha(p.read_bytes())} for p in sorted((source/'src/aqrp').rglob('*.py'))]}
assert bundle==json.loads((source/'docs/audits/phase-2/CODE_BUNDLE.json').read_bytes())
assert sha(json.dumps(bundle,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode())==checks['runtime']['policy']['bundle_sha256']
badroot=next((ROOT/'new-probe-tmp').glob('test_work_p2_reformatted_valid*/roundtrip-runs/*'))
badmanifest=json.loads((badroot/'manifest.json').read_bytes())
declared=next(i['sha256'] for i in badmanifest['artifacts'] if i['path']=='config.json')
actual=sha((badroot/'config.json').read_bytes()); assert declared!=actual
ci_rows='\n'.join(f"| {i['name']} | {i['artifact_id']} | {i['zip_bytes']} | {i['zip_sha256']} | {i['selected_hashes']} / {i['root_hashes']} |" for i in checks['raw_current_ci_zip'])
findings=[
 {'id':'WORK-P2-001','original_severity':'High','target_sha':TARGET,'status':'SUPPLEMENTAL RECHECK PASS','blocking':False,
  'evidence':'Shared source equals released main and reviewed business8902ba0; original16 all pass; original UNKNOWN-calendar-to-factor probe now passes; actual bundle and merge topology verified.','formal_repository_status_modified':False},
 {'id':'WORK-P2-002','severity':'Medium','target_sha':TARGET,'status':'OPEN','blocking':True,
  'file':str(repo/'src/aqrp/factors/engine.py'),'line':136,
  'requirements':['FACTOR-002','FACTOR-010','QA-002','ENV-002'],
  'expected':'Reject or consistently normalize noncanonical config; manifest SHA256 matches exact persisted bytes.',
  'actual':'Same semantic JSON with indentation is accepted; write_run persists original bytes, hashes canonical projection, and records SUCCEEDED.',
  'declared_config_sha256':declared,'actual_config_sha256':actual,'repro_root':str(badroot)},
 {'id':'WORK-P2-003','severity':'Medium','target_sha':TARGET,'status':'OPEN','blocking':True,
  'file':str(repo/'src/aqrp/factors/contracts.py'),'line':257,
  'requirements':['FACTOR-001','FACTOR-002','FACTOR-010','QA-002'],
  'expected':'Recompute parameter hash from validated config.params and verify it against config and Signal rows.',
  'actual':'Changing canonical config lookback2 to1 while retaining hash/rows is accepted with result0.21; real lookback1 gives0.1 and a different hash.'}
]
(ROOT/'findings.json').write_text(json.dumps({'audit':'GPT Work 补充审核','target_sha':TARGET,'findings':findings},ensure_ascii=False,indent=2),encoding='utf-8')
report=f'''# GPT Work 补充审核 — Phase2 集成版本复核

**固定目标：{TARGET}。结论：发现阻断问题。**

**Phase1受控集成及上轮WORK-P2-001通过补充复核；WORK-P2-002、003仍OPEN，均为Medium阻断。** 本轮没有将旧的11项失败沿用到新版：真实新SDK为392通过，未改原16项回归全部通过，未改原四项P2探针为2失败/2通过。两项失败恰为上轮配置哈希及参数血缘问题，原未知日历到因子的失败已消失。

## A. 审核对象、权限、方法与覆盖范围

| 项目 | 本轮核实 |
|---|---|
| 仓库 / PR | [AQRP PR #3](https://github.com/wwooyy429/Alpha-Quant-Research-Platform-AQRP-/pull/3)，Draft/Open，未合并 |
| 固定目标 | **{TARGET}**，开始及结束与PR/远端Phase2分支/开发副本HEAD一致 |
| base / 集成发布版 | fb1ba4fd51202a303115e4449ee49db09ccc071c，main / v0.1.1 |
| 上轮Phase2目标 | 947467b9d094905cab0af37ec5cc53f1d187e755 |
| 集成业务提交 | 566f0ece4175fddb2703daab3b5b26ff0e4e245f，双父为上轮P2和上述发布main |
| 独立只读副本 | `{link(repo)}`，detached/clean；Git longpaths仅作用于审核副本 |
| 原开发副本 | C:/Users/11638/AppData/Local/AQRP/checkouts/phase1-57461d5d-5de2-4c78-9b4e-5fad2b5ccb29，开始/结束status clean，未修改 |
| 本轮新SDK | {env['run_id']}，标准CPython3.13.16/x64/GIL，新venv、实际安装0.2.0 wheel |
| 时间 | 2026-10-22 00:17:34+08:00开始；证据验证完成{data['finished_at']}；报告{now}；Asia/Shanghai |
| 权限/工具 | Git/原件只读、GitHub PR/Actions读取、PowerShell与精确Python隔离执行；输出/缓存/数据均位于非同步审核目录 |

本轮重新核对AGENTS最新状态、集成授权/双父历史、三处共享源码、active CODE_BUNDLE与工程准入回执、六项新增集成用例、执行/ZIP/校验器更正记录及上轮三个问题。既有治理/契约/需求和未改P2实现/测试沿用此前已读材料，并以实际差异、冻结文件hash及完整SDK重新验证，不声称重新全面审核所有Phase0设计或后续能力。

执行原版tools/ci.py完整新安装与验证、两份未编辑原16回归、原样保留的四项P2探针、当前最终头双平台原始ZIP下载/解包/内部hash/数据与因子重放、原查询身份重算及保护资产检查。项目源码、正式测试、Golden、锁、原报告/状态和PR未修改；未提交/推送/合并/打标签/发布或向其他聊天/人员发消息。全部失败保留在新审核目录。

## B. 授权、版本与阶段边界

- 用户本轮明确授权审核这个完整固定SHA。仓库集成授权记录原话“请集成到phase 2，然后更新完发给我我去审核”，不包含Phase2验收、main合并、发布或Phase3启动。
- 新main是已登记的P1修复发布版，不把主干由f579前进到fb1误报为本次擅自合并P2。publication-v0.1.1/APPROVAL.json与BASELINE.md保留其批准/发布来源，外部转交聊天身份认证不在本轮工具能力范围。
- 远端v0.1.1附注对象6611ca42e213c78be5155cba702ae789d48aab24，目标fb1ba4fd51202a303115e4449ee49db09ccc071c；Phase0原标签对象/7de1d0e目标、Phase1原标签对象/f579目标均不变。
- 仍限定FACTOR-001–006、010–012与SEC-001共10项。ENGINEERING_APPROVED / TEST_ONLY / financial_approval=NONE不等于金融批准；外部不可信插件/OS沙箱和P3–7能力保持原范围。
- 本轮实际执行者是GPT Work。此前用户指定的P1代执行不扩写为Gemini本人已执行P2或P2独立审查豁免；本轮技术阻断有明确反例，不以执行者名称差异代替代码判断。

## C. 旧问题逐项处置与阻断依据

### WORK-P2-001 — 原High — 集成补充复核通过

目标：{TARGET}。关联原WORK-P1-001–003、006–009及DATA/FACTOR依赖。

实际Git与源码字节核验：core/time.py、data/pit.py、data/quality.py精确等于已发布main及此前实际审过的业务8902ba00a818150bf00af8d051a3837bc79e6bfc；相对旧P2全部源码变化仅为这三处和reviewed_code.json。因子Python逻辑保持原字节。集成业务提交的双父正确，业务提交到最终审查头的src/tests/tools/workflow/构建/锁无差异。

完整26模块bundle独立重建，与active CODE_BUNDLE.json、随库准入回执均一致：**fc1b50110c02efbe4a53168c43d7fe4972e5ebab3edc3091aeaf58ac72a11fc7**。核验代码及准入绑定，不仅核对文档中的“相同”标记；本结论不覆盖002/003的正确性。

本轮原16项全部通过，原UNKNOWN日历正式发布→因子反例通过，新六项host时间精度/探索快照/共享代码漂移回归也在392全套中实际通过。因此不再把旧P1七项缺陷列为本固定版本未修。此处是GPT Work补充复核通过，不直接修改正式问题库/用户批准状态。

### WORK-P2-002 — Medium / 产物完整性代码缺陷 / OPEN，阻断

目标：{TARGET}。关联FACTOR-002、FACTOR-010、QA-002、ENV-002。

**定位：** [engine.write_run第136行]({link(repo/'src/aqrp/factors/engine.py')}:136)，及[SignalBatch第251行]({link(repo/'src/aqrp/factors/contracts.py')}:251)。这两处与上轮代码相同。

**最小复现：** 正常momentum batch的config经json.loads，再json.dumps(indent=2).encode重新编码，语义完全不变；构造SignalBatch并调用write_run。**预期**明确拒绝非canonical配置，或统一规范化并使持久化字节、manifest和batch内容hash一致。**实际**接受并写SUCCEEDED，保存含缩进的原配置字节，却用digest(json.loads(data))计算canonical投影的hash：

- 清单声明：`{declared}`。
- 实际文件：`{actual}`。
- 本轮[实际错误成功产物]({link(badroot/'manifest.json')})及[未改探针日志]({link(ROOT/'new-probe.stdout.log')})均保存。

**影响及阻断理由：** 普通JSON往返即可生成无法按清单核对的成功产物，损害审计/归档/重放完整性。正常canonical配置的写盘hash正向控制通过，故不是全局环境故障。本轮CI只走正常canonical路径，其绿色结果不能关闭此反例。

**最小修复/复核：** 在入口拒绝非canonical配置，或一致规范化并保持config/content_hash/manifest对应；文件hash应依据实际写出的字节。保留原canonical成功、空白/键顺序往返和精确hash验证，不通过降级核对或改正确输入答案消除失败。

### WORK-P2-003 — Medium / 参数血缘代码缺陷 / OPEN，阻断

目标：{TARGET}。关联FACTOR-001、FACTOR-002、FACTOR-010、QA-002。

**定位：** [SignalBatch第251–257行]({link(repo/'src/aqrp/factors/contracts.py')}:251)。构造器依然将config自报params_hash直接与Signal比对，没有从config.params按schema重新冻结并计算hash；本轮未改该实现。

**最小复现：** 以close100/110/121、lookback2得到0.21，只把配置中的params改为lookback1，保留旧params_hash及Signal，使用canonical(config)构造SignalBatch。**预期**参数与hash矛盾应抛ContractError。**实际**仍被接受，结果保留0.21；相同输入真正用lookback1运行是0.1，并有不同params_hash，正向控制已真实运行。

**影响及阻断理由：** 被接受的配置与实际计算参数不一致，按配置复现得到不同结果，参数冻结与完整血缘验收不成立。这个输入本身是canonical，修002的格式检查不能自动修003。

**最小修复/复核：** 按既有参数schema验证和冻结config.params，重算hash，与配置及每条Signal一致核对；保留真实lookback1/2数值变化正控、非法类型/未知键/重复参数及合法往返。不将旧结果hash改成新参数hash来掩盖错误。

没有新增问题编号。001在本轮已通过，002/003保持原编号并以新包实际重现；不因本轮主要工作是P1集成而忽略仍存在的P2阻断。

## D. 需求→实现/测试→证据→本轮状态

| 需求 | 实际核验 | 状态 |
|---|---|---|
| DATA-001–009、011适用修复 | 发布版共享源码等价、132项数据修复回归、原16与UNKNOWN日历到因子反例 | 集成已测范围通过，001通过 |
| FACTOR-001 | Spec/Context、元数据/参数schema；完整SDK/原探针 | 正常路径通过；003仍阻断参数血缘 |
| FACTOR-002 | SignalBatch/唯一键/血缘/持久化 | 002、003阻断 |
| FACTOR-003 | 精确Ref、幂等/停用/旧pin/紧急停用/rollback/兼容 | 已测限定范围通过 |
| FACTOR-004/005/006 | Momentum/Reversal/Volume独立答案、逐证券窗口/零量/行动、三端真实回放 | 公式及正常数值路径通过；输出配置问题另列002/003 |
| FACTOR-010 | 参数冻结、版本pin、权重仅元数据、旧运行行为 | 正常路径通过；002/003破坏配置可追溯性 |
| FACTOR-011 | 只改精确FactorRef的替换与API版本兼容 | 已测P2范围通过，未追加DAG/研究/回测义务 |
| FACTOR-012 | 每decision取数、可见窗口、mutation/正控；新增host秒/offset精度与辅助表拒绝 | 原继承可得性问题已解决，已测范围通过 |
| SEC-001 | 26模块bundle/回执、新旧hash及共享代码漂移拒绝 | 准入绑定核验通过，仍限定工程测试，整体bundle仍含002/003 |
| ENV-001/002、SEC-002 | 精确运行时、22锁包、新venv/真实wheel、当前双OS原件、扫描正负控制 | 原件及已执行内容通过 |
| QA-002 | 新392全部通过、原16通过、原四探针2失败 | 测试覆盖仍缺002/003边界，当前整体不能正常技术通过 |

正式目录仍106项、Phase2仍10项，50项P0冻结文件hash不变。没有新功能或后续阶段要求。

## E. 实际执行、失败保留及证据边界

| 本轮实际执行 | 结果 |
|---|---|
| 完整新SDK | **392/0失败/0错误/0跳过，exit0**；{env['run_id']}，目标固定、dirty=false、complete=true |
| 新安装 | 标准CPython3.13.16/x64/GIL，新venv，原锁require-hashes/only-binary安装；22活动锁包版本正确，26安装模块/真实wheel与固定源码一致 |
| 本地真实wheel | `{env['wheel_sha256']}`，候选0.2.0；与各CI原wheel分别核对 |
| 两份原16回归 | **16通过，exit0**；未改原脚本/期望/hash |
| 原四项P2探针 | **2失败/2通过，exit1**；文件与上轮原字节相同；canonical写盘与实际lookback1/2正控通过，未知日历反例转通过 |
| 覆盖/静态/数学/数据/扫描 | ruff/格式、逐模块行/分支门槛、参考、两套数据/因子smoke、固定扫描器正负控制和源码扫描实际通过 |
| 文件保护 | 本轮集成证据清单{checks['preservation']['latest_manifest_files']}项及50项冻结文件hash匹配；Golden与实现前答案同字节；历史清单按原快照范围保留 |

实际下载并核验**最终目标的新CI** [run39632670690/attempt1](https://github.com/wwooyy429/Alpha-Quant-Research-Platform-AQRP-/actions/runs/39632670690)，没有借用仓库中566f0ec业务轮ZIP冒充新头：

| 原件 | artifact | ZIP字节 | 与官方digest一致的SHA256 | 选择文件 / 上传根文件 |
|---|---|---|---|---|
{ci_rows}

两端原件环境均complete=true、dirty=false、Python3.13.16、GitHub run39632670690/attempt1，JUnit各392通过。实际CI checkout **adcf22b877e731e2b8de98aa556cf90b6ff2725a** 的Git父为main fb1和目标c707，tree **{checks['ci_topology']['tree']}** 与目标完全一致；这是CI临时合并，没有将P2合并main。

每份原ZIP安全路径/CRC/无重复名/无符号链接、46选择文件hash及14上传根清单、实际wheel/准入JSON/.coverage/JUnit/覆盖门槛/空扫描报告通过，2工具字节的省略按原策略明确保留。分别验证data和factor-data两套各八表快照的文件hash与独立manifest digest；实际读取/查询、三因子重放及完整Signal行原字节一致。两端与本轮本地的两套逻辑数据、data查询/配置及三因子结果一致。

比较投影仅排除表行snapshot_id和data config的snapshot_id/manifest_hash；保留原UUID重放Signal，未为比较改写原始血缘。额外按原记录Windows/Linux/本地存储root重算**12项原query_hash全部匹配**，并单独验证迁移后结果。原查询身份按契约包含存储root，不要求迁移后hash相同。因此开发方关于首次校验器路径假设错误的更正有实际代码/独立重算支持；旧失败脚本/日志原件完整保留，未据此修改产品、答案或容差。

原始证据入口：[汇总]({link(ROOT/'evidence-verification.json')})、[SDK完整命令/输出]({link(run/'commands.log')})、[SDK环境]({link(run/'environment.json')})、[原16通过日志]({link(ROOT/'original16.stdout.log')})、[原四探针失败日志]({link(ROOT/'new-probe.stdout.log')})、[原query身份重算]({link(ROOT/'original-query-identity.json')})、[问题状态索引]({link(ROOT/'findings.json')})、[总证据清单]({link(ROOT/'REVIEW_EVIDENCE_MANIFEST.json')})。

**NOT VERIFIED：** 本轮新的Linux本地安装（使用当前Ubuntu CI原件，在新Windows SDK回放）；Gemini本人新的全量SDK执行；旧P1历史未上传字节；原外部转交聊天身份认证；修复002/003后的新SHA；用户Phase2验收/合并/标签/发布及Phase3授权。旧报告标题/职责/源码路径等说明冲突及旧综合工具缺原件的历史不改写，本轮依据真实代码/执行作补充判断。

## F. 给Codex的最小任务及复核清单

1. 接收本轮001的集成补充通过证据，保留新旧SHA、实际merge、共享源码与bundle绑定，按真实来源登记GPT Work复核；不把本报告写成整版通过或用户验收。
2. **WORK-P2-002：** 修配置原字节、batch内容hash、实际写盘及manifest hash的一致性；明确拒绝或一致规范化非canonical输入。将本次原反例加入正式回归并保留原始失败。
3. **WORK-P2-003：** 按schema重算配置参数hash并与配置/Signal核对；保留真实lookback1/2正控，拒绝不一致参数，而非为旧结果重贴hash。
4. 保留已通过P1集成行为、原Golden/容差/锁和全部历史审计原件。上述P2源码改变后，对完整26模块bundle实际重审并更新CODE_BUNDLE/准入回执，不仅机械改hash。
5. 修复后提交**新完整40位SHA**及影响差异；按原锁运行全套（含新回归）、未编辑原16和原四探针、覆盖/参考/扫描及双OS原件核对。验收、合并/发布、Phase3分别遵守实际授权，本轮不代签。

**最终结论：Phase1集成及WORK-P2-001补充复核通过；WORK-P2-002、003仍为已复现的Medium阻断，当前Phase2整体不能给予正常技术通过。仅为GPT Work补充审核。**
'''
(ROOT/'GPT-Work-Phase2-c70727c-Recheck.md').write_text(report,encoding='utf-8')
tasks=f'''# 给Codex的Phase2固定集成版复核任务

目标：{TARGET}；GPT Work补充审核；整体仍BLOCKING。

- WORK-P2-001：补充复核通过。三处共享源码等于发布main及已审8902ba0，新bundle及双父集成正确；原16全部通过、原UNKNOWN日历到因子反例已通过。
- WORK-P2-002：OPEN / Medium阻断。格式化但语义相同的JSON被接受，write_run保存原字节却hash canonical投影。统一config/batch/实际文件/manifest，或明确拒绝非canonical输入；保留原正负控制。
- WORK-P2-003：OPEN / Medium阻断。config.params由lookback2改1而旧hash/0.21结果仍被接受，真实1是0.1。按schema重算并交叉核对参数hash；不为旧结果改贴标签。
- 本轮新SDK392通过、原16通过、原四探针2失败/2通过；当前最终头双OS原ZIP已真实核验。不要用392/CI绿代替修上述两项。
- 保留Golden/容差/锁、P1修复与历史原件。修改P2源码后实际重审并更新全bundle/准入回执，提交新40位SHA及差异，运行完整适用验证及未改原16/四探针。
- 只登记真实GPT Work证据；本报告未改正式状态，不代表用户验收、合并/标签/发布或Phase3授权。
'''
(ROOT/'Codex-Phase2-c70727c-Repair-Tasks.md').write_text(tasks,encoding='utf-8')
commands={'target_sha':TARGET,'sdk':{'argv':['C:/Users/11638/AppData/Local/AQRP/runtime/Python31316/python.exe','-u',str(repo/'tools/ci.py')],'AQRP_RUN_ROOT':str(ROOT/'runs'),'exit':0,'stdout':'sdk.stdout.log','stderr':'sdk.stderr.log'},'external_tests':[]}
for name,tests,expected in [('original16',[i['path'] for i in checks['original16_scripts_unchanged']],0),('new-probe',[str(ROOT/'test_work_p2_regressions.py')],1)]:
    prefix='original' if name=='original16' else 'new-probe'
    commands['external_tests'].append({'argv':[checks['runtime']['executable'],'-m','pytest','-q','--showlocals','-o',f'cache_dir={ROOT/(prefix+"-pytest-cache")}','--basetemp',str(ROOT/(prefix+'-tmp')),f'--junitxml={ROOT/(name+"-junit.xml")}',*tests],'cwd':str(ROOT),'exit':expected,'stdout':name+'.stdout.log','stderr':name+'.stderr.log'})
(ROOT/'execution-command-index.json').write_text(json.dumps(commands,ensure_ascii=False,indent=2),encoding='utf-8')
for md in ROOT.glob('*.md'):
    for p in re.findall(r'\]\(([^)]+)\)',md.read_text(encoding='utf-8')):
        if p.startswith('C:/') and not p.endswith('/REVIEW_EVIDENCE_MANIFEST.json'):
            assert Path(re.sub(r':\d+$','',p)).exists(),p
selected={p for p in ROOT.iterdir() if p.is_file() and p.name!='REVIEW_EVIDENCE_MANIFEST.json'}
selected.update(p for p in run.iterdir() if p.is_file())
for folder in (run/'wheel',run/'dataset',run/'factor-dataset',run/'factor-runs',ROOT/'zip-replay'):
    selected.update(p for p in folder.rglob('*') if p.is_file())
selected.update(p for p in badroot.iterdir() if p.is_file())
entries=[]
for p in sorted(selected):
    b=p.read_bytes();entries.append({'path':p.relative_to(ROOT).as_posix(),'bytes':len(b),'sha256':sha(b)})
(ROOT/'REVIEW_EVIDENCE_MANIFEST.json').write_text(json.dumps({'audit':'GPT Work 补充审核','target_sha':TARGET,'generated_at':now,'conclusion':'001 supplemental PASS; 002/003 OPEN BLOCKING','scope':'Review reports/scripts/commands/raw failures/original ZIPs, new SDK root/wheel/two datasets/factor runs, extracted CI originals, invalid emitted receipt; excludes self, venv/cache/build source and routine pytest temporary snapshots. Full fixed source ZIP included.','files':entries},ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'status':'BLOCKING: WORK-P2-002/003','001':'SUPPLEMENTAL PASS','sdk':392,'original16':16,'original4':checks['new-probe']['junit'],'review_evidence_files':len(entries),'integration_manifest_files':checks['preservation']['latest_manifest_files'],'report':str(ROOT/'GPT-Work-Phase2-c70727c-Recheck.md')},ensure_ascii=False))
