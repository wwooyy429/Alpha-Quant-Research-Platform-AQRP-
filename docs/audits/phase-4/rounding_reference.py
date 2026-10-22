"""Independent Fraction design candidates only; NOT AQRP implementation tests."""
from fractions import Fraction as F
import json

checks=[]

def record(case,actual,expected):
    assert actual==expected,(case,actual,expected)
    checks.append({'case':case,'actual':repr(actual),'expected':repr(expected),'status':'PASS'})

# Separate fixed expected table. This is mathematical divisibility truth-table verification,
# not a new executable portfolio service, permission approval, or order algorithm.
quantity_cases=[
    ('R01',F(15),F(10),True,('DELTA_LOT_MISMATCH',F(-5))),
    ('R02',F(15),F(20),True,('DELTA_LOT_MISMATCH',F(5))),
    ('R03',F(15),F(15),False,('UNCHANGED_HOLDING',F(0))),
    ('R04',F(15),F(0),True,('FULL_CLOSE_LOT_EXCEPTION',F(-15))),
    ('R05',F(15),F(0),False,('DELTA_LOT_MISMATCH',F(-15))),
    ('R06',F(-15),F(0),True,('FULL_CLOSE_LOT_EXCEPTION',F(15))),
    ('R07',F(-15),F(0),False,('DELTA_LOT_MISMATCH',F(15))),
    ('R08',F(15),F(-10),True,('DELTA_LOT_MISMATCH',F(-25))),
    ('R09',F(-15),F(10),True,('DELTA_LOT_MISMATCH',F(25))),
    ('R10',F(10),F(20),False,('ALIGNED_QUANTITIES_ONLY',F(10))),
    ('R11',F(-15),F(-10),True,('DELTA_LOT_MISMATCH',F(5))),
    ('R12',F(-15),F(-20),True,('DELTA_LOT_MISMATCH',F(-5))),
    ('R13',F(-15),F(-15),False,('UNCHANGED_HOLDING',F(0))),
    ('R17',F(10),F(15),True,('TARGET_LOT_MISMATCH',F(5))),
]
for case,current,target,full_close,expected in quantity_cases:
    delta=target-current
    if delta==0:status='UNCHANGED_HOLDING'
    elif target!=0 and (target/F(10)).denominator!=1:status='TARGET_LOT_MISMATCH'
    elif (delta/F(10)).denominator==1:status='ALIGNED_QUANTITIES_ONLY'
    elif target==0 and current!=0 and delta==-current and full_close:status='FULL_CLOSE_LOT_EXCEPTION'
    else:status='DELTA_LOT_MISMATCH'
    if case=='R01':
        targets=[F(10),F(90)];original=[F(15),F(0)];px=F(10);equity=F(1000)
        weights=[q*px/equity for q in targets]
        record(case,{'quantity_gate':(status,delta),'target_B_delta':targets[1]-original[1],
                     'weights':weights,'net':sum(weights),'gross':sum(abs(v) for v in weights),
                     'beta_and_sector_net':sum(weights),
                     'turnover':sum(abs(q-c)*px for q,c in zip(targets,original))/equity,
                     'cash':equity-sum(q*px for q in targets)},
                    {'quantity_gate':('DELTA_LOT_MISMATCH',F(-5)),'target_B_delta':F(90),
                     'weights':[F(1,10),F(9,10)],'net':F(1),'gross':F(1),'beta_and_sector_net':F(1),
                     'turnover':F(19,20),'cash':F(0)})
    else:
        record(case,(status,delta),expected)

E=F(1000);prices=[F(60),F(50)];lots=[F(10),F(10)]
ideal=[E*F(1,2)/prices[0],-E*F(1,2)/prices[1]]
rounded=[(1 if q>=0 else -1)*(abs(q)//lot)*lot for q,lot in zip(ideal,lots)]
w=[q*p/E for q,p in zip(rounded,prices)]
net=sum(w);gross=sum(abs(x) for x in w);short=sum(max(-q*p,0) for q,p in zip(rounded,prices))
cash=E-sum(q*p for q,p in zip(rounded,prices));free=cash-2*short
record('R14',{'ideal':ideal,'target':rounded,'weights':w,'gross':gross,'beta':net,'sector_net':net,
              'beta_abs':abs(net),'sector_net_abs':abs(net),'pre_interval_pass':-F(1,10)<=0<=F(1,10),
              'post_interval_pass':-F(1,10)<=net<=F(1,10),'cash':cash,'free_cash':free},
             {'ideal':[F(25,3),F(-10)],'target':[F(0),F(-10)],'weights':[F(0),-F(1,2)],'gross':F(1,2),
              'beta':-F(1,2),'sector_net':-F(1,2),'beta_abs':F(1,2),'sector_net_abs':F(1,2),
              'pre_interval_pass':True,'post_interval_pass':False,'cash':F(1500),'free_cash':F(500)})

current=[F(10),F(0)];ideal_long=[E*F(1,2)/p for p in prices]
rounded_long=[(q//lot)*lot for q,lot in zip(ideal_long,lots)]
pre=sum(abs((q-c)*p) for q,c,p in zip(ideal_long,current,prices))/E
post=sum(abs((q-c)*p) for q,c,p in zip(rounded_long,current,prices))/E
record('R15',{'current_cash':E-sum(c*p for c,p in zip(current,prices)),'ideal':ideal_long,'target':rounded_long,
              'pre_turnover':pre,'post_turnover':post,'pre_half':pre/2,'post_half':post/2,
              'pre_cap_pass':pre<=F(4,5),'post_cap_pass':post<=F(4,5)},
             {'current_cash':F(400),'ideal':[F(25,3),F(10)],'target':[F(0),F(10)],
              'pre_turnover':F(3,5),'post_turnover':F(11,10),'pre_half':F(3,10),'post_half':F(11,20),
              'pre_cap_pass':True,'post_cap_pass':False})

abs_qty=[abs(a)<=abs(b) for a,b in zip(rounded,ideal)]
abs_notional=[abs(a*p)<=abs(b*p) for a,b,p in zip(rounded,ideal,prices)]
pre_gross=sum(abs(q*p/E) for q,p in zip(ideal,prices))
funds=[]
for long,short in [(F(500),F(500)),(F(700),F(500))]:
    by_cash=E-long+short-short-short
    by_gross=E*(1-(long+short)/E)
    funds.append((by_cash,by_gross))
record('R16',{'absolute_qty_nonincrease':abs_qty,'absolute_notional_nonincrease':abs_notional,
              'gross_nonincrease':gross<=pre_gross,'same_sector_gross_nonincrease':gross<=pre_gross,'funding_identities':funds},
             {'absolute_qty_nonincrease':[True,True],'absolute_notional_nonincrease':[True,True],
              'gross_nonincrease':True,'same_sector_gross_nonincrease':True,'funding_identities':[(F(0),F(0)),(F(-200),F(-200))]})
assert len(checks)==17
print(json.dumps({'actual_executor':'Codex developer','scope':'Independent design arithmetic and divisibility candidates, no AQRP imports or P4 runtime verdict',
                  'groups_passed':len(checks),'cases':checks},indent=2))
