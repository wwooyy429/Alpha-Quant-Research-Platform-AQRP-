"""Developer-authored independent arithmetic candidates; no AQRP imports or implementation claim."""
from fractions import Fraction as F
import json
checks=[]
def check(name,actual,expected):
    assert actual == expected,(name,actual,expected)
    checks.append({'case':name,'actual':str(actual),'expected':str(expected),'status':'PASS'})
single=[F(3),F(1)]
check('G01',[v/sum(single) for v in single],[F(3,4),F(1,4)])
s=[(3*2+4)/F(4),(3*4+2)/F(4)]
check('G02',[v/sum(s) for v in s],[F(5,12),F(7,12)])
check('G03',sorted(['C','B','A'])[:2],['A','B'])
check('G04',sum(max(F(v),0) for v in [-1,-2]),0)
check('G05',F(1,len([-1,-2])),F(1,2))
check('G06',sorted(set('AB') & set('BC')),['B'])
check('G07',[(F(1)+0)/2,-(F(1)-0)/2],[F(1,2),-F(1,2)])
check('G08',[(F(6,5)+F(1,5))/2,-(F(6,5)-F(1,5))/2],[F(7,10),-F(1,2)])
check('G09',[F(1,2)*F(3,4),F(1,2)*F(1,4),-F(1,2)*F(1,4),-F(1,2)*F(3,4)],[F(3,8),F(1,8),-F(1,8),-F(3,8)])
q=[(F(500,p)//10)*10 for p in [30,40]]
check('G10',(q,1000-q[0]*30-q[1]*40),([10,10],300))
check('G11',(F(300-400,1000),F(300+400,1000),1000-300+400-400-400),(-F(1,10),F(7,10),300))
check('G12',F(3,4)-F(7,10),F(1,20))
check('G13',abs(F(3,4)-F(1,2))+abs(F(1,4)-F(1,2)),F(1,2))
check('G14',F(300-400,1000)<0,True)
check('G15',(F(3,4)-F(1,4),F(3,4)+F(1,4)),(F(1,2),1))
check('G16',F(3,4)*F(6,5)+F(1,4)*F(4,5),F(11,10))
check('G17',(min(15,10),max(5,0)),(10,5))
check('G18',(6-4,6>5),(2,True))
check('G19',(1000-500+500-500-500,1000-700+500-500-500),(0,-200))
tol=F(1,10**12);cap=F(3,4)
check('G20',[(v<=cap+tol) for v in (cap,cap+tol/2,cap+tol*2)],[True,True,False])
print(json.dumps({'actual_executor':'Codex developer','scope':'20 arithmetic design candidates only; NOT independent review and NOT implementation tests','cases_passed':len(checks),'checks':checks},indent=2))
