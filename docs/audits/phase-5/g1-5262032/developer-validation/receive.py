from pathlib import Path
from datetime import datetime, UTC
import hashlib, json, shutil, subprocess, zipfile

R=Path(r'C:\Users\11638\AppData\Local\AQRP\checkouts\phase1-57461d5d-5de2-4c78-9b4e-5fad2b5ccb29')
S=Path(r'C:\Users\11638\AppData\Local\AQRP\reviews\p5-g1-recheck-5262032-independent')
O=Path(__file__).parent
P=R/'docs/audits/phase-5'
D=P/'g1-5262032'
FIXED='5262032bee4f631f68763e57510e1878945f6b8c'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,x):
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
def write(p,s):
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(s.strip()+'\n',encoding='utf-8',newline='\n')
def git(*a): return subprocess.check_output(['git',*a],cwd=R).decode().strip()
assert git('rev-parse','HEAD')==FIXED and not git('status','--porcelain')
assert git('branch','--show-current')=='codex/phase-5-backtest-plan'
write(O/'BEFORE_REMOTE_REFS.txt',git('ls-remote','--heads','--tags','origin'))
receipt=json.loads((S/'RECEIPT.json').read_bytes())
assert receipt['fixed_sha']==FIXED and receipt['verdict']=='PLAN PASS WITH CONDITIONS'
zp=S/receipt['archive']
assert zp.stat().st_size==receipt['bytes'] and sha(zp)==receipt['sha256']
D.mkdir(exist_ok=False)
copied=[]
with zipfile.ZipFile(zp) as z:
    assert z.testzip() is None
    names=z.namelist()
    assert len(names)==len(set(names))==receipt['zip_members']
    raw=z.read('EVIDENCE_MANIFEST.json')
    assert hashlib.sha256(raw).hexdigest()==receipt['manifest_sha256']
    files=json.loads(raw)['files']
    assert len(files)==receipt['manifest_files']==188
    assert set(names)=={e['path'] for e in files}|{'EVIDENCE_MANIFEST.json'}
    for e in files:
        raw=z.read(e['path'])
        assert len(raw)==e['bytes'] and hashlib.sha256(raw).hexdigest()==e['sha256'],e['path']
    for p in sorted(S.iterdir()):
        if not p.is_file() or p.suffix not in ('.md','.json','.py','.txt','.log'): continue
        if p.name not in names and p.name!='RECEIPT.json':
            assert p.name.startswith('seal.'),p.name
            continue
        if p.name!='RECEIPT.json': assert p.read_bytes()==z.read(p.name),p.name
        dest=D/'received'/p.name
        dest.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(p,dest)
        copied.append({'path':p.name,'bytes':p.stat().st_size,'sha256':sha(p),'sealed_member':p.name in names})
findings=json.loads((D/'received/FINDINGS.json').read_bytes())
assert findings['fixed_sha']==FIXED
assert len(findings['findings'])==4 and all(e['status']=='CLOSED_DESIGN' for e in findings['findings'])
assert not findings['implementation_authorized']
dump(D/'RECEIVED.json',{
 'received_utc':datetime.now(UTC).isoformat(),'receiver':'Codex developer; receipt validation only, not independent re-execution',
 'reviewer_as_reported':'GPT Work supplemental reviewer','reviewed_sha':FIXED,
 'verdict':'PLAN PASS WITH CONDITIONS','scope':'G1 restricted engineering design; all four CLOSED_DESIGN, not G2 or human acceptance',
 'original_archive':str(zp),'bytes':receipt['bytes'],'sha256':receipt['sha256'],
 'manifest_sha256':receipt['manifest_sha256'],'manifest_files_verified':188,'zip_members_verified':189,
 'CRC_exact_members_all_hashes_verified':True,'git_copied_files':copied,
 'git_subset_not_full_archive':True,'full_original_archive_retained_externally':True,
 'receipt_is_external_seal_metadata_not_a_zip_member':True,
 'post_seal_command_logs_retained_externally_not_relabelled_as_sealed_members':True,
 'old_5c_BLOCKED_report_and_all_raw_failures_preserved':True,
 'new_SDK_product_real_crash_native_isolation_or_CI_ZIP_execution_this_receipt':False,
 'human_contract_and_profile_acceptance':'PENDING','implementation_authorized':False,
 'merge_tag_deploy_formal_Test_financial_approval_next_phase_authorized':False})
write(D/'.gitattributes','* whitespace=cr-at-eol')
write(D/'DEVELOPER_RESPONSE.md',f'''# Phase5 G1 有条件通过接收与处理

2026-10-23，开发 Codex按原字节接收GPT Work对固定 `{FIXED}` 的独立报告。结论 **PLAN PASS WITH CONDITIONS（受限工程设计）**；四项均由主审确认 **CLOSED_DESIGN — FIX VERIFIED AT G1**，没有新增阻断技术设计发现。以下接收检查由开发方执行，不能补记为独立重新运行。

| 发现 | 主审处置 | 仍需在真实产品实现后验证 |
|---|---|---|
| WORK-P5-G1-001 / High | CLOSED_DESIGN：外层事件总序、逐单原子子事务和重放 | 持久队列、最新状态门禁、幂等、崩溃前后原子恢复 |
| WORK-P5-G1-002 / High | CLOSED_DESIGN：互斥现金桶、交收及P4保守投影 | 原生P4适配、真实cashlot/交收/保证金/双风险账本 |
| WORK-P5-G1-003 / Medium | CLOSED_DESIGN：全部方向/类型价格域及累计费用上界 | tick、GTC、部分成交、取消、预算注入与最终落盘字节 |
| WORK-P5-G1-004 / Medium | CLOSED_DESIGN：FIFO闭合片段及历史成本归属 | 原始事件独立重建、历史池守恒及真实输出统计 |

## 未闭环的人工决定

1. **HUMAN-P5-CONTRACT：PENDING。** 用户须明确接受 `CONTRACT_CHANGE_IMPACT.md` 的C-P5-001事件总序/原子子事务/重放及取消语义补充。冻结P0原文件保持原字节；如实施还需正式修改P0或schema，另列版本/迁移批准。
2. **HUMAN-P5-PROFILE：PENDING。** 用户须接受 `PROFILE_AND_DECISIONS.md` 的P5-D01–D10，含C-P5-002互斥现金桶与仅预算保守量H、C-P5-003双边价格域/有利极端gap拒绝/固定费用预算、C-P5-004 CLOSED_FIFO_FRAGMENT统计，以及T+1、short/borrow与公司行动规则。技术可实现性不代替用户选择，也不等于金融批准。
3. **HUMAN-P5-IMPLEMENTATION：NOT AUTHORIZED。** 接受上述口径后仍需用户单独明确授权既定12项（10MVP/2CR）工程实现。本次仅转交报告，不能登记成接受或实施授权。如不同意某项，先修订设计、提交新固定SHA复核。

## 证据范围与版本

主审独立复算原25组/70项、补充25组/209项，另6组/2349个设计模型情景通过；全部是设计参考，不能称P5产品测试或真实恢复/隔离验证。主审本轮查到双OS既有P4 quality成功，但未重新核验该轮CI原始ZIP，不能写成P5 SDK/CI原始证据通过。

`received/`是原包顶层文本/原始日志的明确子集，完整168864680字节原ZIP保留在RECEIVED.json所列外部路径；开发方实测SHA256、CRC、精确189成员及188声明文件哈希一致，外层收据不是数字签名。原5c9721f BLOCKED报告及所有初次失败、旧锁/交审包保持原字节。

本轮只新增接收/状态记录，12份设计身份文件、131冻结输入、原答案及源码/测试/工具/CI/依赖锁不改。后续归档提交不同于已审设计SHA；以`DESIGN_CONTINUITY.json`证明字节一致，不能扩大独立报告的固定版本结论。审查状态中的旧OPEN只指原交审轮次，由本记录前瞻更新，不篡改原报告。

WI-R2-001/002与整体Windows真实隔离持续 **DEFERRED / NOT VERIFIED**，最终集成完整SHA的真实全生命周期验证另行授权。R3代码候选6207450未集成P4/P5。正式Test、金融批准和完整历史宿主复现延期/限定范围保留，正式入口继续失败关闭。本轮无实现、合并、标签、部署、真实账户/ACL操作、正式Test或后续阶段。
''')
dump(D/'HUMAN_DECISIONS.json',{'reviewed_design_sha':FIXED,'receipt_is_not_human_acceptance':True,'conditions':findings['conditions'],'implementation_authorized':False,'financial_approval':'NONE','main_merge_tag_deployment_authorized':False})
s=json.loads((P/'STATUS.json').read_bytes())
s.update({'current':'G1_PLAN_PASS_WITH_CONDITIONS_HUMAN_ACCEPTANCE_AND_IMPLEMENTATION_AUTHORIZATION_PENDING',
 'G1':'PLAN_PASS_WITH_CONDITIONS_AT_5262032','last_independent_reviewed_sha':FIXED,
 'previous_independent_reviewed_sha':'5c9721f96679f4d495b7b3b93af3e2e31e66ae62',
 'previous_review_final_head_not_covered':s.pop('last_review_final_head_not_covered'),
 'G1_findings':{e['id']:'CLOSED_DESIGN' for e in findings['findings']},
 'design_candidate_math':'GPT Work independently verified original25/70 and supplemental25/209; extra6/2349 MODEL scenarios; no P5 product tests',
 'review_record':'g1-5262032/DEVELOPER_RESPONSE.md','human_design_acceptance':'PENDING',
 'pending_human_decisions':findings['conditions'],
 'updated_profile':'P5-D01-D10 / C-P5-002-004 PENDING_EXPLICIT_USER_ACCEPTANCE',
 'receipt_scope':'Archive/status only; reviewed design files unchanged; report verdict limited to5262032',
 'independent_recheck_current_CI_raw_ZIP':'NOT_VERIFIED_THIS_ROUND_P4_QUALITY_METADATA_ONLY'})
dump(P/'STATUS.json',s)
banner=f'''2026-10-23 最新Phase5 G1：GPT Work对固定 `{FIXED}` 判 **PLAN PASS WITH CONDITIONS（受限工程设计）**，四项均 **CLOSED_DESIGN**，无新增阻断技术设计。原25/70、新25/209及6组2349设计模型独立通过，均不是P5产品测试。本轮仅接收归档/状态更新；用户仍须明确接受C-P5-001及P5-D01–D10（含C-P5-002–004）经济/统计口径，再单独授权P5实施，当前 **NOT AUTHORIZED / NOT STARTED**。原报告、失败及旧轮OPEN/BLOCKED保留历史；现状见 `docs/audits/phase-5/g1-5262032/DEVELOPER_RESPONSE.md`。12份已审设计身份文件不改，归档提交与已审526版本分别标识；main/标签保持P4基线，真实隔离WI-R2-001/002继续 **DEFERRED / NOT VERIFIED**，正式Test/金融批准/完整旧宿主边界不变，无部署/实盘/合并/标签/P6。

以下既有状态按原轮次保留，由上述新独立处置更新当前状态；不改写原审计结论。
'''
for rel in ('AGENTS.md','docs/PROGRESS.md','docs/ROADMAP.md','docs/DECISIONS.md','docs/TRACEABILITY.md','docs/CHANGELOG.md','docs/audits/phase-5/REVIEW_PACKAGE.md','docs/audits/phase-5/REVIEW_PACKAGE_CURRENT.md'):
    p=R/rel
    first,rest=p.read_bytes().split(b'\n',1)
    p.write_bytes(first+b'\n\n'+banner.encode('utf-8')+b'\n'+rest)
print(json.dumps({'verdict':receipt['verdict'],'reviewed_sha':FIXED,'verified_zip_members':189,'verified_declared_files':188,'copied_text_files':len(copied),'implementation':'NOT_AUTHORIZED_NOT_STARTED'}))
