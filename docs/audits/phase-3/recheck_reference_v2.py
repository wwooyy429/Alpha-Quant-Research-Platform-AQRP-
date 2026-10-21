"""Developer stdlib reference for v2 design inputs, never AQRP business tests.

All case times/expected answers live in JSON. Missing inputs are errors, not
hidden timestamp fallbacks. Public engineering evidence; no OS/formal run.
"""
import hashlib
import itertools
import json
import platform
import sys
import uuid
from datetime import datetime, timezone
from fractions import Fraction as F
from pathlib import Path


def utc(s):
    return datetime.fromisoformat(s.replace('Z','+00:00'))


def fifth_root(n):
    lo,hi=0,n+1
    while hi-lo>1:
        mid=(lo+hi)//2
        if mid**5<=n:lo=mid
        else:hi=mid
    return lo


def main():
    root=Path(__file__).parent
    label_path=root/'label_visibility_v2.json';hac_path=root/'hac_growth_cases.json'
    labels=json.loads(label_path.read_bytes());hac=json.loads(hac_path.read_bytes());checks=[]
    def eq(case,field,a,e):
        assert a==e,(case,field,a,e)
        checks.append({'case':case,'field':field,'actual':str(a),'expected':str(e),'pass':True,'comparison':'exact'})
    for c in labels['cases']:
        ident=c['id'];cutoff=utc(c['evaluation_cutoff']);entry=utc(c['entry_at']);exit=utc(c['exit_at']);expected=c['expected']
        for a in c['actions']:
            for key in ['action_id','revision_id','announcement_at','event_time','available_at','effective_at','unit_anchor_close','ex_date','record_date','pay_date','dividend_basis','type']:assert key in a,(ident,key)
            assert a['event_time']==a['announcement_at'] and utc(a['available_at'])>=utc(a['event_time'])
            assert a['effective_at'][:10]==a['ex_date'] and a['dividend_basis']=='PER_OLD_SHARE'
        for cv in c['coverage_versions']:
            for key in ['coverage_id','revision_id','source_version','event_time','available_at','actions_complete_through','signature_status']:assert key in cv,(ident,key)
            assert utc(cv['available_at'])>=utc(cv['event_time'])
        eq(ident,'explicit_fixture_no_formal_signature',all(v['signature_status']=='PROPOSED_UNSIGNED' for v in c['coverage_versions']),True)
        visible_cov=[v for v in c['coverage_versions'] if utc(v['event_time'])<=cutoff and utc(v['available_at'])<=cutoff]
        bars=c['bars'];anchors=c['anchor_rows'];calendar=c['calendar']
        all_visible=all(utc(v['event_time'])<=cutoff and utc(v['available_at'])<=cutoff for v in bars+anchors+[calendar])
        if not visible_cov or not all_visible:
            for field in ['shares','credit','return','label_available_at']:eq(ident,field,None,expected[field])
            eq(ident,'status','NOT_YET_AVAILABLE',expected['status'])
            continue
        cov=max(visible_cov,key=lambda v:utc(v['available_at']));assert utc(cov['actions_complete_through'])>=exit
        visible_actions={}
        for a in c['actions']:
            if utc(a['event_time'])<=cutoff and utc(a['available_at'])<=cutoff:
                key=a['action_id']
                if key not in visible_actions or utc(a['available_at'])>utc(visible_actions[key]['available_at']):visible_actions[key]=a
        actions=list(visible_actions.values());events=[(entry,2,'entry',None),(exit,3,'exit',None)]
        for a in actions:
            if utc(a['effective_at'])<=exit:events.append((utc(a['effective_at']),0 if a['type']=='SPLIT' else 1,a['action_id'],a))
        n=F(0);credit=F(0);held_at_exit=None
        for instant,priority,key,a in sorted(events,key=lambda t:(t[0],t[1],t[2])):
            if key=='entry':n+=1
            elif key=='exit':held_at_exit=n
            elif a['type']=='SPLIT':n*=F(a['split_ratio'])
            elif entry<instant<=exit:
                ratio=F(1)
                for split in actions:
                    if split['type']=='SPLIT' and utc(a['unit_anchor_close'])<utc(split['effective_at'])<=instant:ratio*=F(split['split_ratio'])
                credit+=n*F(a['cash_per_share'])/ratio
        bykey={v['key']:v for v in bars}
        ret=(held_at_exit*F(bykey['exit']['open'])+credit)/F(bykey['entry']['open'])-1
        deps=bars+anchors+[calendar,cov]+[a for a in actions if utc(a['effective_at'])<=exit]
        available=max(utc(v[k]) for v in deps for k in ['event_time','available_at'])
        for key,value in [('shares',held_at_exit),('credit',credit),('return',ret)]:eq(ident,key,value,F(expected[key]))
        eq(ident,'label_available_at',available,utc(expected['label_available_at']))
    # Independent population covariance enumeration, not running reviewer helper.
    rows=[[(F(s[k])+s[k+1])/2 for k in range(3)] for s in itertools.product((-1,1),repeat=4)]
    gamma=[sum(x[2]*x[2-k] for x in rows)/len(rows) for k in range(3)]
    eq('MA1','gamma',gamma,[F(1,2),F(1,4),F(0)]);eq('MA1','true_S',gamma[0]+2*gamma[1],F(1))
    for c in hac['fixed_population_targets']:
        S=gamma[0]+2*(1-F(1,c['q']+1))*gamma[1]
        eq('FIXED-'+str(c['q']),'S',S,F(c['S']));eq('FIXED-'+str(c['q']),'bias',1-S,F(c['bias']))
    for c in hac['integer_root_boundaries']:
        r=fifth_root(c['N']);eq('ROOT-'+str(c['N']),'r',r,c['r']);assert r**5<=c['N']<(r+1)**5
    for c in hac['growing_ma1_population']:
        q=max(c['h']-1,c['m0'],fifth_root(c['N']));S=gamma[0]+2*(1-F(1,q+1))*gamma[1]
        eq('GROW-'+str(c['N']),'q',q,c['q']);eq('GROW-'+str(c['N']),'S_population',S,F(c['S_population']));eq('GROW-'+str(c['N']),'bias_population',1-S,F(c['bias_population']))
    for c in hac['profile_cases']:
        q=max(c['h']-1,c['m0'],fifth_root(c['N']));ident='SCREEN-'+str(c['N'])+'-'+str(c['h'])+'-'+str(c['m0'])
        eq(ident,'q',q,c['q']);eq(ident,'numeric_screen',c['N']>=max(252,20*(q+1)),c['numeric_screen'])
    finite=hac['ma1_exact_finite_quantities'];n=finite['N'];q=finite['q']
    eq('FINITE-MA1','known_mean_weighted_covariance_expectation',F(1,2)+(1-F(1,q+1))*(1-F(1,n))/2,F(finite['known_mean_covariance_weighted_expectation']))
    eq('FINITE-MA1','exact_sample_mean_variance',(F(n)-F(1,2))/n**2,F(finite['exact_variance_sample_mean']))
    for c in hac['formal_rejections']:
        # Specified gate predicate only, not a production approval API test.
        reasons=[]
        if c['n_actual']!=c['N']:reasons.append('PLANNED_SAMPLE_MISMATCH')
        if not c['bounded_stationary_mdep_proved']:reasons.append('DEPENDENCE_MODEL_UNVERIFIED')
        if not c['profile_reviewed']:reasons.append('METHOD_REVIEW_REQUIRED')
        if not c['user_protocol_approved']:reasons.append('FORMAL_PROTOCOL_UNAPPROVED')
        eq('FORMAL-REJECTION-'+c['reason'],'reason',reasons,[c['reason']])
    print(json.dumps({'run_id':'p3-v2-reference-'+str(uuid.uuid4()),'actual_executor':'Codex developer reference; not GPT Work independent execution','python':sys.version,'platform':platform.platform(),'timestamp_utc':datetime.now(timezone.utc).isoformat(),'inputs':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [label_path,hac_path]},'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'label_cases':len(labels['cases']),'assertions':len(checks),'passed':len(checks),'failed':0,'scope':'P3 design arithmetic, complete time fixtures and predicates only; not business or finite-sample coverage/OS/formal tests','checks':checks},ensure_ascii=False,indent=2))


if __name__=='__main__':main()
