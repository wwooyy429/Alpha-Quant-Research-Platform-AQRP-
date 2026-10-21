from decimal import Decimal as D,localcontext
from fractions import Fraction as F
from pathlib import Path
import json
R=Path(__file__).resolve().parent
out={}
with localcontext() as ctx:
    ctx.prec=80
    x=list(map(D,['-2','-1','0','1','2']));y=list(map(D,['-.04','.01','-.01','.02','.05']))
    mx=sum(x)/len(x);my=sum(y)/len(y)
    sxx=sum((v-mx)**2 for v in x);syy=sum((v-my)**2 for v in y);sxy=sum((a-mx)*(b-my) for a,b in zip(x,y))
    ic=sxy/(sxx*syy).sqrt();assert abs(ic-D('.893684825'))<D('1e-8')
    out['G-IC']={'x':x,'y':y,'sxx':sxx,'syy':syy,'sxy':sxy,'actual':ic,'approx_tolerance':'1e-8'}
    def rank(v):return [sum(i+1 for i,z in enumerate(sorted(v)) if z==a)/sum(z==a for z in v) for a in v]
    def corr(a,b):
        a=list(map(lambda z:D(str(z)),a));b=list(map(lambda z:D(str(z)),b));am=sum(a)/len(a);bm=sum(b)/len(b)
        return sum((v-am)*(w-bm) for v,w in zip(a,b))/(sum((v-am)**2 for v in a)*sum((w-bm)**2 for w in b)).sqrt()
    rank_ic=corr(rank(x),rank(y));assert rank_ic==D('.9');out['G-RANK']=rank_ic
    tie=corr(rank([1,1,3]),rank([1,2,3]));assert abs(tie-D(3).sqrt()/2)<D('1e-70');out['G-TIE']=tie
    std=(sxx/(len(x)-1)).sqrt();zs=[(v-mx)/std for v in x]
    assert abs(sum(zs))<D('1e-70') and abs(sum(z*z for z in zs)/(len(zs)-1)-1)<D('1e-70')
    out['G-Z']={'sample_variance':sxx/(len(x)-1),'standardized':zs}
    ics=list(map(D,['.1','.2','.3']));m=sum(ics)/len(ics);sd=(sum((z-m)**2 for z in ics)/(len(ics)-1)).sqrt();assert m/sd==2
    out['G-ICIR']={'mean':m,'sample_std':sd,'actual':m/sd}
    for key,actual,expected in [('G-RET',F(110,100)-1,F(1,10)),('G-MOM',F(121,100)-1,F(21,100)),('G-VOL',F(30,(10+20)//2)-1,F(1))]:
        assert actual==expected;out[key]=str(actual)
    weights=[F(1,3)]*3;assert sum(weights)==1;out['G-W']=[str(z) for z in weights]
    cash=1000-2*100-1;qty=2;mv=qty*105;assert (cash,qty,mv,cash+mv)==(799,2,210,1009);out['G-CASH']=[cash,qty,mv,cash+mv]
    after=cash+110-1;remaining=qty-1;assert (after,remaining,after+remaining*110)==(908,1,1018);out['G-SELL']=[after,remaining,after+remaining*110]
    partcash=1000-sum([100+1,102+1]);partqty=1+1;assert (partcash,partqty,partcash+partqty*103)==(796,2,1002);out['G-PART']=[partcash,partqty,partcash+partqty*103]
    oldqty=2;oldprice=100;ratio=2;newqty=oldqty*ratio;newprice=F(oldprice,ratio);assert newqty*newprice==oldqty*oldprice==200;out['G-SPLIT']=[newqty,str(newprice),str(newqty*newprice)]
    receivable=qty*1;ex=cash+qty*104+receivable;paycash=cash+receivable;paid=paycash+qty*104;assert (receivable,paycash,ex,paid)==(2,801,1009,1009);out['G-DIV']=[receivable,paycash,ex,paid]
    equity=[100,120,90,108];peaks=[];peak=equity[0]
    for e in equity:peak=max(peak,e);peaks.append(peak)
    dd=max(1-F(e,p) for e,p in zip(equity,peaks));assert dd==F(1,4);out['G-DD']={'equity':equity,'peaks':peaks,'actual':str(dd)}
(R/'independent-golden-math.json').write_text(json.dumps(out,indent=2,default=str),encoding='utf-8')
print('15 Phase0 candidate cases independently computed and asserted; no AQRP import')
