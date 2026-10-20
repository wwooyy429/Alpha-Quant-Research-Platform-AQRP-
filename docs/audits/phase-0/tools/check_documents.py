"""仅对Phase0文档作可复现结构自查，绝不执行AQRP业务/插件。"""
import argparse
import csv
import hashlib
import json
import platform
import re
import subprocess
import sys
from datetime import datetime, timezone
from decimal import Decimal, localcontext
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
AUDIT = ROOT / 'docs/audits/phase-0'

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source-v30', type=Path)
    parser.add_argument('--source-v32', type=Path)
    args = parser.parse_args()
    started = datetime.now(timezone.utc).isoformat()
    checks, errors = [], []
    def check(name, ok, detail):
        checks.append({'name': name, 'result': 'PASS' if ok else 'FAIL', 'detail': detail})
        if not ok:
            errors.append(name)
    with (ROOT/'docs/requirements.csv').open(encoding='utf-8', newline='') as f:
        rows = list(csv.DictReader(f))
    ids = {r['id'] for r in rows}
    check('unique_requirement_ids', len(ids) == len(rows), {'rows': len(rows), 'unique': len(ids)})
    empty = [(r['id'], k) for r in rows for k,v in r.items() if not v.strip()]
    check('all_required_fields_present', not empty, empty)
    tiers = {'MVP', 'Competition Ready', 'Advanced Research', 'Production Extensions'}
    invalid = [(r['id'], r['tier'], r['phase'], r['capability_status']) for r in rows
               if r['tier'] not in tiers or r['phase'] not in {'0','1','2','3','4','5','6','7','POST7'}
               or r['capability_status'] not in {'Planned','Deferred','Unsupported'}]
    check('tier_phase_unimplemented_status', not invalid, invalid)
    by_id = {r['id']: r for r in rows}
    graph = {r['id']: [d for d in r['dependencies'].split(';') if d != 'NONE'] for r in rows}
    missing = [(i,d) for i,ds in graph.items() for d in ds if d not in ids]
    check('dependency_ids_exist', not missing, missing)
    future = []
    for i, ds in graph.items():
        p = 99 if by_id[i]['phase'] == 'POST7' else int(by_id[i]['phase'])
        for d in ds:
            if d in by_id:
                dp = 99 if by_id[d]['phase'] == 'POST7' else int(by_id[d]['phase'])
                if dp > p:
                    future.append((i, by_id[i]['phase'], d, by_id[d]['phase']))
    check('no_future_phase_prerequisite', not future, future)
    visited, active, cycles = set(), set(), []
    def visit(n):
        if n in active:
            cycles.append(n)
            return
        if n in visited:
            return
        active.add(n)
        for d in graph.get(n, []):
            visit(d)
        active.remove(n)
        visited.add(n)
    for i in graph:
        visit(i)
    check('dependency_graph_acyclic', not cycles, cycles)
    bad_design = [(r['id'], r['design']) for r in rows if not (ROOT/'docs'/r['design']).is_file()]
    check('requirement_design_files_exist', not bad_design, bad_design)
    req = (ROOT/'docs/REQUIREMENTS.md').read_text(encoding='utf-8')
    trace = (ROOT/'docs/TRACEABILITY.md').read_text(encoding='utf-8')
    absent = [i for i in sorted(ids) if f'## {i} ·' not in req or f'| {i} |' not in trace]
    check('all_requirements_rendered_and_traced', not absent, absent)
    source_tokens = {s for r in rows for s in r['source'].split(';')}
    uncovered = []
    source_stats = {}
    for version in ['3.0', '3.1', '3.2']:
        content = (ROOT/f'docs/sources/AQRP_V{version}.md').read_text(encoding='utf-8-sig')
        pattern = r'^##\s+(\d+\.\d+)\b' if version == '3.0' else r'^#{1,2}\s+(\d+)\.\s'
        sections = re.findall(pattern, content, re.M)
        for section in sections:
            token = f'V{version}§{section}'
            if not any(s == token or s.startswith(token + '.') for s in source_tokens):
                uncovered.append(token)
        source_stats[version] = len(sections)
    gate = (ROOT/'docs/sources/AQRP_V3.2_BASELINE_GATE.md').read_text(encoding='utf-8')
    gate_sections = re.findall(r'^##\s+(\d+)\.\s', gate, re.M)
    for section in gate_sections:
        if f'V3.2-Baseline§{section}' not in source_tokens:
            uncovered.append(f'V3.2-Baseline§{section}')
    source_stats['3.2-Baseline'] = len(gate_sections)
    check('numbered_source_sections_mapped_structurally', not uncovered, {'counts': source_stats, 'unmapped': uncovered,
          'limitation': '节存在映射不证明逐句语义完整，需Gemini审查。'})
    required = ['AGENTS.md','README.md'] + ['docs/'+n+'.md' for n in [
        'PROJECT_CHARTER','REQUIREMENTS','ARCHITECTURE','INTERFACES','ACCEPTANCE','TRACEABILITY',
        'ROADMAP','DECISIONS','PROGRESS','TESTING','CHANGELOG','DATA_CONTRACT','BACKTEST_CONTRACT',
        'RESEARCH_PROTOCOL','GOLDEN_DATASET','ENVIRONMENT_AND_SECURITY','BASELINE']]
    required += ['docs/audits/templates/'+n+'.md' for n in ['DUAL_AI_AUDIT_REPORT','REVIEW_PACKAGE','PHASE_ACCEPTANCE_REPORT']]
    required += ['tests/'+n+'/README.md' for n in ['golden','integration','e2e']]
    check('required_deliverables_exist', all((ROOT/p).is_file() for p in required), required)
    links = []
    for path in ROOT.rglob('*.md'):
        if '.git' in path.parts:
            continue
        content = path.read_text(encoding='utf-8-sig')
        for target in re.findall(r'\[[^\]]*\]\(([^)]+)\)', content):
            if '://' in target or target.startswith('#'):
                continue
            target = target.split('#')[0].strip('<>')
            if target and not (path.parent/target).exists():
                links.append([str(path.relative_to(ROOT)), target])
    check('local_markdown_links_resolve', not links, links)
    business = [p.as_posix() for p in (ROOT/'src').rglob('*')] if (ROOT/'src').exists() else []
    tests = [str(p.relative_to(ROOT)) for p in (ROOT/'tests').rglob('*.py')]
    check('no_future_business_implementation', not business and not tests, {'src_files': business, 'business_tests': tests})
    milestones = {'FACTOR-011':'2','RESEARCH-009':'3','BT-010':'5','UI-007':'6','INT-005':'7'}
    check('replacement_test_stage_assignment', all(by_id[i]['phase'] == p for i,p in milestones.items()), milestones)
    copied = {}
    for version, original in [('3.0', args.source_v30), ('3.2', args.source_v32)]:
        archive = ROOT/f'docs/sources/AQRP_V{version}.md'
        if original:
            ok = original.is_file() and sha(original) == sha(archive)
            copied[version] = {'equal': ok, 'archived_sha256': sha(archive)}
            check('source_attachment_byte_copy_'+version, ok, copied[version])
        else:
            copied[version] = {'result': 'NOT VERIFIED', 'reason': '未提供原附件参数'}
    with localcontext() as ctx:
        ctx.prec = 50
        x = list(map(Decimal, ['-2','-1','0','1','2']))
        y = list(map(Decimal, ['-.04','.01','-.01','.02','.05']))
        mx, my = sum(x)/5, sum(y)/5
        sxx = sum((v-mx)**2 for v in x)
        syy = sum((v-my)**2 for v in y)
        sxy = sum((a-mx)*(b-my) for a,b in zip(x,y))
        ic = sxy/(sxx*syy).sqrt()
        check('golden_candidate_ic_arithmetic_only', sxx==10 and syy==Decimal('.00452') and sxy==Decimal('.19')
              and abs(ic-Decimal('.893684825')) < Decimal('1e-8'),
              {'sxx':str(sxx),'syy':str(syy),'sxy':str(sxy),'pearson':str(ic),
               'limitation':'开发方标准库算式自查；无待测业务函数，不是Gemini核验或业务Golden测试。'})
        cash=Decimal(1000)-Decimal(2)*100-1
        mv=Decimal(2)*105
        check('golden_candidate_ledger_arithmetic_only', (cash,mv,cash+mv)==(799,210,1009),
              {'cash':str(cash),'market_value':str(mv),'equity':str(cash+mv)})
    commands = []
    for command in [['git','status','--short','--branch'], ['git','remote','-v'], ['git','--version']]:
        result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, encoding='utf-8', errors='replace')
        commands.append({'argv':command,'exit_code':result.returncode,'stdout':result.stdout,'stderr':result.stderr})
    review_evidence = AUDIT/'gemini/GATE_EVIDENCE_INDEX.json'
    if not review_evidence.is_file():
        review_evidence = AUDIT/'gemini/FINAL_EVIDENCE_INDEX.json'
    if not review_evidence.is_file():
        review_evidence = AUDIT/'gemini/REV2_EVIDENCE_INDEX.json'
    if not review_evidence.is_file():
        review_evidence = AUDIT/'gemini/INCREMENTAL_EVIDENCE_INDEX.json'
    if not review_evidence.is_file():
        review_evidence = AUDIT/'gemini/EVIDENCE_INDEX.json'
    gemini_status = 'NOT VERIFIED'
    if review_evidence.is_file():
        supplied_review = json.loads(review_evidence.read_text(encoding='utf-8'))
        gemini_status = {'status':'Original report received; verdict applies only to reviewed_commit',
                        'verdict':supplied_review['overall_verdict'],
                        'reviewed_commit':supplied_review['reviewed_commit'],
                        'report_path':supplied_review['report_path'],
                        'report_sha256':supplied_review['report_sha256'],
                        'execution_scope':supplied_review['execution_evidence_scope'],
                        'developer_closure':supplied_review.get('developer_closure','See developer response; no automatic finding closure')}
    approval_path = AUDIT/'publication/APPROVAL.json'
    human_approval = 'NOT VERIFIED'
    if approval_path.is_file():
        recorded_approval = json.loads(approval_path.read_text(encoding='utf-8'))
        human_approval = {'status':'Human approval record present; this tool does not grant authorization',
                          'path':approval_path.relative_to(ROOT).as_posix(),
                          'phase0_accepted':recorded_approval.get('user_phase0_accepted',False),
                          'approved_pr_head':recorded_approval.get('approved_pr_head'),
                          'phase1_authorized':recorded_approval.get('phase1_authorized',False)}
    summary = {'scope':'Phase0文档结构与候选算式开发方自查；不是业务测试、CI或Gemini审计',
       'started_at_utc': started, 'finished_at_utc':datetime.now(timezone.utc).isoformat(),
       'python':sys.version,'platform':platform.platform(),'requirements':len(rows),
       'checks_passed':len(checks)-len(errors),'checks_failed':len(errors),'checks':checks,
       'business_tests':'NOT RUN / Planned','gemini_review':gemini_status,'human_approval':human_approval,
       'ci':'NOT ESTABLISHED; Phase1 planned','attachment_copy':copied,'git_commands':commands}
    (AUDIT/'SELF_CHECK.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    log = ['PHASE0 DOCUMENT SELF-CHECK — RAW CAPTURE',f'Start UTC: {started}',
           'Actual argv: '+subprocess.list2cmdline([sys.executable]+sys.argv),f'CWD: {ROOT}',
           f'Python: {sys.version}',f'Platform: {platform.platform()}',
           'NOTE: 仅文档自查，不是业务测试或独立审查。']
    for c in checks:
        log.append(c['result']+' '+c['name']+' '+json.dumps(c['detail'],ensure_ascii=False))
    for c in commands:
        log += ['COMMAND '+subprocess.list2cmdline(c['argv']), 'EXIT '+str(c['exit_code']),
                'STDOUT\n'+c['stdout'], 'STDERR\n'+c['stderr']]
    log += [f'Check exit code: {1 if errors else 0}',f'End UTC: {summary["finished_at_utc"]}']
    (AUDIT/'COMMAND_LOG.txt').write_text('\n'.join(log)+'\n',encoding='utf-8',newline='\n')
    files=[]
    inventory = subprocess.check_output(['git','ls-files','--cached','--others','--exclude-standard','-z'],cwd=ROOT)
    inventory_paths = sorted(set(inventory.decode('utf-8').split('\0')) - {''})
    for relative in inventory_paths:
        p = ROOT / relative
        if not p.is_file() or '.git' in p.parts or '__pycache__' in p.parts or '.baiduyun.' in p.name or p == AUDIT/'MANIFEST.json':
            continue
        files.append({'path':p.relative_to(ROOT).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)})
    canonical = json.dumps(files, ensure_ascii=False,sort_keys=True,separators=(',',':')).encode('utf-8')
    manifest={'scope':'Git跟踪或未忽略的交付文件，排除.git/__pycache__/同步临时元数据与已确认同义副本/本manifest自身；非Git SHA替代品',
              'generated_at_utc':datetime.now(timezone.utc).isoformat(),
              'entries_sha256':hashlib.sha256(canonical).hexdigest(),'files':files}
    (AUDIT/'MANIFEST.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({'requirements':len(rows),'checks_passed':len(checks)-len(errors),
                      'checks_failed':len(errors),'failed_names':errors,'manifest_files':len(files)},ensure_ascii=False))
    return 1 if errors else 0

if __name__ == '__main__':
    raise SystemExit(main())
