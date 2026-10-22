"""Developer stdlib design reference only; no AQRP service/implementation imports.

Fixtures contain independent hand-specified expected answers. This script checks
arithmetic definitions and candidate states; it is not a production evaluator,
PIT label implementation, OS isolation test, or independent Gemini approval.
"""

import hashlib
import json
import math
import platform
import sys
import uuid
from datetime import datetime, timezone
from decimal import Decimal, localcontext
from fractions import Fraction as F
from pathlib import Path


def time(s):
    return datetime.fromisoformat(s.replace('Z', '+00:00'))


def erfc_decimal(x):
    # Direct erf power series in 80-digit Decimal; math.erfc uses a separate path.
    with localcontext() as c:
        c.prec = 80
        pi = Decimal('3.141592653589793238462643383279502884197169399375105820974944592307816406286208998628')
        term, total, k = x, x, 0
        while True:
            k += 1
            term *= -x*x/Decimal(k)
            addition = term/Decimal(2*k+1)
            total += addition
            if abs(addition) < Decimal('1e-75'):
                break
            assert k < 1000
        return +(1-2*total/pi.sqrt())


def zscore(v):
    m=sum(v)/len(v)
    sd=math.sqrt(float(sum((x-m)**2 for x in v)/(len(v)-1)))
    return [float(x-m)/sd for x in v]


def main():
    started=datetime.now(timezone.utc).isoformat()
    p=Path(__file__).with_name('supplemental_cases.json')
    d=json.loads(p.read_bytes())
    checks=[]
    def eq(case, field, a, e):
        assert a == e, (case,field,a,e)
        checks.append({'case':case,'field':field,'actual':str(a),'expected':str(e),'comparison':'exact','pass':True})
    def close(case, field, a, e):
        assert math.isfinite(float(a)) and math.isfinite(float(e))
        assert abs(float(a)-float(e))<=max(1e-12,1e-10*abs(float(e))), (case,field,a,e)
        checks.append({'case':case,'field':field,'actual':str(a),'expected':str(e),'comparison':'abs1e-12/rel1e-10','pass':True})
    default=d['label_defaults']
    entry,exit=time(default['entry_at']),time(default['exit_at'])
    for v in d['label_cases']:
        ident=v['id']; e=v['expected']
        cutoff=time(v.get('evaluation_cutoff',default['evaluation_cutoff']))
        available=max(time(default['entry_bar_available_at']),time(default['exit_bar_available_at']),time(v.get('action_available_at',default['entry_bar_available_at'])),time(v.get('coverage_available_at',default['coverage_available_at'])))
        div=F(v.get('dividend_per_old_share','0'))
        if 'revision_available_at' in v and time(v['revision_available_at'])<=cutoff:
            div=F(v['revised_dividend_per_old_share'])
            available=max(available,time(v['revision_available_at']))
        if available>cutoff:
            eq(ident,'label_available_at',None,e['label_available_at'])
            eq(ident,'status','NOT_YET_AVAILABLE',e['status'])
            for field in ['shares','credit','return']:
                eq(ident,field,None,e[field])
            continue
        eq(ident,'label_available_at',available,time(e['label_available_at']))
        held = v['action_at'] is not None and entry<time(v['action_at'])<=exit
        split=F(v.get('split','1'))
        shares=split if held else F(1)
        # All one-event fixtures use that session's pre-split OLD_SHARE anchor.
        credit=shares*div/split if held else F(0)
        ret=(shares*F(v['exit_price'])+credit)/F(v['entry_price'])-1
        for field,a in [('shares',shares),('credit',credit),('return',ret)]:
            eq(ident,field,a,F(e[field]))
    other={v['id']:v for v in d['other_cases']}
    e=other['LABEL-ANCHOR-RESET']['expected']
    eq('LABEL-ANCHOR-RESET','ratio_anchor_to_dividend',F(1),F(e['ratio_anchor_to_dividend']))
    eq('LABEL-ANCHOR-RESET','shares',F(2),F(e['shares']))
    eq('LABEL-ANCHOR-RESET','credit',F(2)*F(1),F(e['credit']))
    eq('LABEL-ANCHOR-RESET','return',(F(2)*51+2)/100-1,F(e['return']))
    v=other['LABEL-BAR-CLOSE-AND-FIT']; i=v['input']; e=v['expected']; label=time(i['exit_bar_available_at'])
    eq(v['id'],'visible_at_exit_open',label<=time(i['exit_open_at']),e['visible_at_exit_open'])
    for tag in ['before','equal','after']:
        eq(v['id'],'fit_'+tag,label<=time(i['fit_cutoff_'+tag]),e['fit_'+tag])
    v=other['LABEL-LATE-TRAIN-FIT']; i=v['input']
    eq(v['id'],'fit_allowed',time(i['label_available_at'])<=time(i['fit_cutoff']),v['expected']['fit_allowed'])
    v=other['PURGE-INFORMATION-CONTACT']; i=v['input']
    a,b=map(time,i['train_information_interval']); c,end=map(time,i['heldout_protected_interval'])
    eq(v['id'],'purge',max(a,c)<=min(b,end),v['expected']['purge'])
    for ident in ['COMPOSITE-SIGNED-SCALE','COMPOSITE-POSITIVE-DIRECTION','COMPOSITE-MISSING-INTERSECTION']:
        v=other[ident]; i=v['input']; e=v['expected']
        keep=[k for k in range(len(i['A'])) if i['A'][k] is not None and i['B'][k] is not None]
        a=zscore([F(i['A'][k]) for k in keep]); b=zscore([F(i['B'][k]) for k in keep]); w=list(map(F,i['weights'])); directions=i['directions']
        actual=[(float(w[0])*directions[0]*x+float(w[1])*directions[1]*y)/float(sum(w)) for x,y in zip(a,b)]
        expected=[float(F(x)) for x in e['composite']] if 'composite' in e else [-1/math.sqrt(2),1/math.sqrt(2)]
        for k,(x,y) in enumerate(zip(actual,expected)): close(ident,'score_'+str(k),x,y)
        if 'kept_indices' in e: eq(ident,'kept_indices',keep,e['kept_indices'])
        if ident=='COMPOSITE-SIGNED-SCALE':
            rho=sum(x*y for x,y in zip(a,b))/(len(a)-1)
            close(ident,'raw_correlation',rho,F(e['raw_correlation']))
            close(ident,'signed_correlation',rho*directions[0]*directions[1],F(e['signed_correlation']))
            scaled=zscore([F(i['B'][k])*7 for k in keep])
            for k,(x,y) in enumerate(zip(b,scaled)):close(ident,'scale_invariance_'+str(k),x,y)
    v=other['COMPOSITE-REJECTIONS']; i=v['input']; e=v['expected']
    eq(v['id'],'all_zero',not any(map(F,i['weights_zero'])),e['all_zero']=='INVALID_WEIGHTS')
    eq(v['id'],'one_positive',sum(F(x)>0 for x in i['weights_one_positive'])<2,e['one_positive']=='INSUFFICIENT_COMPONENTS')
    eq(v['id'],'empty',i['missing_all'],e['empty']=='INSUFFICIENT_INTERSECTION')
    eq(v['id'],'missing_thresholds',i['thresholds'] is None,e['missing_thresholds']=='UNCLASSIFIED')
    v=other['REDUNDANCY-PREDECLARED']; i=v['input']; e=v['expected']
    flag=(abs(F(i['absolute_rho']))>=F(i['tau']) and i['pair_n']>=i['min_pair_n'] and i['eligible_days']>=i['min_days'] and F(i['hit_fraction'])>=F(i['min_fraction']))
    eq(v['id'],'flag',flag,e['flag'])
    for ident in ['HAC-NONZERO-Q1','HAC-NONZERO-Q2']:
        v=other[ident]; i=v['input']; e=v['expected']; x=list(map(F,i['IC'])); n=len(x); q=i['q']; m=sum(x)/n; u=[t-m for t in x]
        gamma=[sum(u[t]*u[t-k] for t in range(k,n))/n for k in range(q+1)]
        S=gamma[0]+2*sum((1-F(k,q+1))*gamma[k] for k in range(1,q+1)); variance=S/n
        eq(ident,'mean',m,F(e['mean']))
        for k,g in enumerate(gamma):eq(ident,'gamma_'+str(k),g,F(e['gamma'][k]))
        eq(ident,'S',S,F(e['S'])); eq(ident,'variance',variance,F(e['variance']))
        with localcontext() as ctx:
            ctx.prec=80
            var_d=Decimal(variance.numerator)/Decimal(variance.denominator); mean_d=Decimal(m.numerator)/Decimal(m.denominator)
            se=var_d.sqrt(); z=mean_d/se; p_d=erfc_decimal(z/Decimal(2).sqrt())
        close(ident,'SE',se,1/16 if q==1 else 1/(8*math.sqrt(3)))
        close(ident,'z',z,4 if q==1 else 2*math.sqrt(3))
        close(ident,'high_precision_p_vs_hand_constant',p_d,Decimal(e['p_approx']))
        close(ident,'libm_p_vs_decimal_series',math.erfc(float(z)/math.sqrt(2)),p_d)
        eq(ident,'sample_not_formal',n>=252,e['formal_eligible'])
    v=other['HAC-PROFILE-BOUNDARIES']; e=v['expected']; qs=[max(h-1,5) for h in v['input']['horizons']]
    mins=[max(252,20*(q+1)) for q in qs]
    eq(v['id'],'lags',qs,e['lags']); eq(v['id'],'minimum_ns',mins,e['minimum_ns'])
    for key,n,req in [('h1_n251',251,mins[0]),('h1_n252',252,mins[0]),('h20_n399',399,mins[3]),('h20_n400',400,mins[3])]:eq(v['id'],key,n>=req,e[key])
    v=other['HAC-REJECTION-CONTRACT']; i=v['input']; e=v['expected']
    for k,a in [('short_lag',i['q_overlap_too_short']<i['h']-1),('lag_equal_n',not 0<=i['q_equal_n']<i['n']),('missing_session',i['contains_missing_session']),('no_assumptions',i['dependence_assessment_ref'] is None),('no_approval',not i['user_formal_protocol_approved'])]:
        eq(v['id'],k,a,True)
        # State-code names are specified contracts, not executed future API behavior.
        checks[-1]['specified_future_reason']=e[k]
    v=other['MULTI-FAILED-FAMILY']; ps=list(map(F,v['input']['conservative_adjustment_p'])); m=len(ps); order=sorted(range(m),key=lambda k:ps[k]); sortedp=[ps[k] for k in order]
    h=[];current=F(0)
    for k,pv in enumerate(sortedp):current=max(current,min(F(1),(m-k)*pv));h.append(current)
    harmonic=sum(F(1,k) for k in range(1,m+1)); bh=[F(1)]*m;by=[F(1)]*m
    for k in range(m-1,-1,-1):
        bh[k]=min(F(1),F(m,k+1)*sortedp[k],bh[k+1] if k+1<m else F(1))
        by[k]=min(F(1),harmonic*F(m,k+1)*sortedp[k],by[k+1] if k+1<m else F(1))
    for method,sorted_vals in [('Holm',h),('BY',by),('BH',bh)]:
        vals=[F(0)]*m
        for k,idx in enumerate(order):vals[idx]=sorted_vals[k]
        eq(v['id'],method,vals,list(map(F,v['expected'][method])))
    eq(v['id'],'formal_family_approvable',all(pv is not None for pv in v['input']['raw_p']),v['expected']['formal_family_approvable'])
    report={'run_id':'p3-design-reference-'+str(uuid.uuid4()),'actual_executor':'Codex developer, not independent reviewer/Gemini','started_at_utc':started,'finished_at_utc':datetime.now(timezone.utc).isoformat(),'argv':sys.argv,'python':sys.version,'platform':platform.platform(),'source_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'reference_script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'fixture_groups':len(d['label_cases'])+len(d['other_cases']),'assertions':len(checks),'passed':len(checks),'failed':0,'scope':'Developer arithmetic and candidate-state predicates only. No P3 business, OS isolation or formal finance execution.','checks':checks}
    print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':
    main()
