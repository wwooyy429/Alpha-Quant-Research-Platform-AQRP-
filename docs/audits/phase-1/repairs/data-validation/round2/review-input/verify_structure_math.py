import csv,json,re,hashlib,subprocess,sys
from collections import Counter
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
from decimal import Decimal,localcontext
R=Path(__file__).resolve().parent
repo=Path(r'C:\Users\11638\AppData\Local\AQRP\reviews\p1-18d51fb')
records=[]
def git(name,args):
    p=subprocess.run(['git',*args],cwd=repo,capture_output=True)
    (R/(name+'.stdout.log')).write_bytes(p.stdout);(R/(name+'.stderr.log')).write_bytes(p.stderr)
    records.append(dict(name=name,argv=['git',*args],cwd=str(repo),exit_code=p.returncode))
    return p.stdout.decode(errors='replace').strip()
for name,sha in [('p0-merge','8c37e952be61054c6c72b5aaf573026c0355647b'),('p0-head','228190a0c46595cf2927125fdc7d4f1c51b39ccf'),('p0-baseline','7de1d0e81385ae97f98ea673fe05dd726f0b577b'),('p1-merge','9b843b17ccf362cf5b7a5351269559a627c55b32')]:
    git(name,['show','-s','--format=%H%n%P%n%T',sha])
git('p0-release-diff',['diff','--stat','228190a0c46595cf2927125fdc7d4f1c51b39ccf','7de1d0e81385ae97f98ea673fe05dd726f0b577b'])
git('p1-pr-release-code-diff',['diff','--stat','18d51fbecc4a1526f2ab75d34874a0b25d00f6c1','f579b2c99e762085772de6e70ba1fa98792a7add','--','src','tests','tools','.github','requirements.lock','pyproject.toml','.gitleaks.toml'])
git('remote-refs',['ls-remote','https://github.com/wwooyy429/Alpha-Quant-Research-Platform-AQRP-.git','refs/heads/main','refs/pull/1/head','refs/pull/2/head','refs/tags/phase0-baseline','refs/tags/phase0-baseline^{}','refs/tags/phase1-baseline','refs/tags/phase1-baseline^{}'])
summary={'audit':'GPT Work 补充审核','time':datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(),'commands':records,'phases':{}}
for phase,sha,mname in [('phase0','7de1d0e81385ae97f98ea673fe05dd726f0b577b','docs/audits/phase-0/MANIFEST.json'),('phase1','f579b2c99e762085772de6e70ba1fa98792a7add','docs/audits/phase-1/publication/MANIFEST.json')]:
    source=R/phase
    rows=list(csv.DictReader((source/'docs/requirements.csv').open(encoding='utf-8',newline='')))
    ids={r['id'] for r in rows}; graph={r['id']:[x for x in r['dependencies'].split(';') if x!='NONE'] for r in rows}
    missing=[(k,x) for k,ds in graph.items() for x in ds if x not in ids]
    future=[(k,x) for k,ds in graph.items() for x in ds if (99 if next(r['phase'] for r in rows if r['id']==x)=='POST7' else int(next(r['phase'] for r in rows if r['id']==x)))>(99 if next(r['phase'] for r in rows if r['id']==k)=='POST7' else int(next(r['phase'] for r in rows if r['id']==k)))]
    visited=set();active=set();cycles=[]
    def visit(k):
        if k in active:cycles.append(k);return
        if k in visited:return
        active.add(k)
        for d in graph[k]:visit(d)
        active.remove(k);visited.add(k)
    for k in graph:visit(k)
    req=(source/'docs/REQUIREMENTS.md').read_text(encoding='utf-8');trace=(source/'docs/TRACEABILITY.md').read_text(encoding='utf-8')
    absent=[i for i in ids if f'## {i} ·' not in req or f'| {i} |' not in trace]
    invalid_design=[r['id'] for r in rows if not (source/'docs'/r['design']).is_file()]
    empty=[(r['id'],k) for r in rows for k,v in r.items() if not v.strip()]
    manifest=json.loads((source/mname).read_bytes());checks=[]
    for f in manifest['files']:
        p=source/f['path'];actual=hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else None
        checks.append(dict(path=f['path'],expected=f['sha256'],actual=actual,match=actual==f['sha256']))
    (R/(phase+'-manifest-check.json')).write_text(json.dumps(checks,ensure_ascii=False,indent=2),encoding='utf-8')
    summary['phases'][phase]={'sha':sha,'requirement_total':len(rows),'unique_ids':len(ids),'groups':dict(Counter(r['id'].split('-')[0] for r in rows)),'missing_dependencies':missing,'future_dependencies':future,'cycles':cycles,'untraced':absent,'missing_design':invalid_design,'empty_fields':empty,'manifest_total':len(checks),'manifest_matched':sum(x['match'] for x in checks),'src_files':len(list((source/'src').rglob('*.py'))) if (source/'src').exists() else 0,'business_test_files':len(list((source/'tests').rglob('*.py')))}
    assert len(rows)==len(ids)==106 and len(summary['phases'][phase]['groups'])==16 and not any([missing,future,cycles,absent,invalid_design,empty])
    print(phase,'106/16 trace/dependencies PASS; manifest',sum(x['match'] for x in checks),'/',len(checks))
# Independently recompute every numerical candidate with stdlib only.
from fractions import Fraction as F
with localcontext() as ctx:
    ctx.prec=70
    d=Decimal
    x=list(map(d,['-2','-1','0','1','2']));y=list(map(d,['-.04','.01','-.01','.02','.05']))
    mx=sum(x)/5;my=sum(y)/5
    sx=sum((v-mx)**2 for v in x);sy=sum((v-my)**2 for v in y);sxy=sum((a-mx)*(b-my) for a,b in zip(x,y))
    pearson=sxy/(sx*sy).sqrt();assert abs(pearson-d('.893684825'))<d('1e-8')
    means=[d('1.5'),d('1.5'),d(3)]; yy=[d(1),d(2),d(3)]
    xm=sum(means)/3;ym=sum(yy)/3
    tie=sum((a-xm)*(b-ym) for a,b in zip(means,yy))/(sum((a-xm)**2 for a in means)*sum((b-ym)**2 for b in yy)).sqrt()
    assert abs(tie-d(3).sqrt()/2)<d('1e-65')
    math={'G-RET':str(F(110,100)-1),'G-MOM':str(F(121,100)-1),'G-VOL':str(F(30,15)-1),'G-IC':str(pearson),'G-RANK':str(1-F(6*2,5*(25-1))),'G-TIE':str(tie),'G-Z-sample-variance':'2.5','G-ICIR':str(d('.2')/d('.01').sqrt()),'G-W':[str(F(1,3))]*3,'G-CASH':[1000-2*100-1,2*105,1000-2*100-1+2*105],'G-SELL':[799+110-1,1,908+110],'G-PART':[1000-100-1-102-1,2,796+2*103],'G-SPLIT':[2*2,200,4*50],'G-DIV':[799+2*104+2,801+2*104],'G-DD':str(F(120-90,120))}
    summary['phase0_candidate_arithmetic']=math
# Check every archived P0 report hash against receive indexes.
report_checks=[]
for p in (R/'phase1/docs/audits/phase-0/gemini').glob('*INDEX.json'):
    v=json.loads(p.read_bytes())
    if isinstance(v,dict) and 'report_path' in v and 'report_sha256' in v:
        target=R/'phase1'/v['report_path'];actual=hashlib.sha256(target.read_bytes()).hexdigest()
        report_checks.append(dict(index=p.name,report=v['report_path'],expected=v['report_sha256'],actual=actual,match=actual==v['report_sha256']))
        assert actual==v['report_sha256']
summary['phase0_report_checks']=report_checks
summary['phase0_core_unchanged']={}
for n in ['ARCHITECTURE','INTERFACES','REQUIREMENTS','DATA_CONTRACT','BACKTEST_CONTRACT','RESEARCH_PROTOCOL','GOLDEN_DATASET','TESTING']:
    a=(R/f'phase0/docs/{n}.md').read_bytes();b=(R/f'phase1/docs/{n}.md').read_bytes()
    summary['phase0_core_unchanged'][n]=a==b
    assert a==b
(R/'structure-and-math.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
print('P0 candidate arithmetic',json.dumps(math,ensure_ascii=False));print('P0 reports',len(report_checks),'hashes MATCH; eight core contract/doc bytes unchanged')
