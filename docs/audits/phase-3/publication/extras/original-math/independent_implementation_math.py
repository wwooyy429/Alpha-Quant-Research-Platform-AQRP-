"""Independent exact-Fraction / matrix / ordered-p expectations against installed wheel."""
import hashlib,json,math,sys
from decimal import Decimal,localcontext
from fractions import Fraction as F
from pathlib import Path
from aqrp.research.numerics import correlation,ols
from aqrp.validation.inference import hac,adjust_pvalues,bandwidth
out=Path(__file__).resolve().parent;checks=[]
def check(name,a,b):
 if a is None or b is None: ok=a is b
 else:ok=abs(float(a)-float(b))<=max(1e-12,1e-10*abs(float(b)))
 checks.append(dict(name=name,actual=a,expected=str(b),pass_=ok));assert ok,checks[-1]
for i,xs in enumerate(([1,-1,1,-1],[1,2,4,-2,3],[F(1,10),F(2,10),F(-3,10),F(4,10),F(-1,10)])):
 xs=list(map(F,xs));n=len(xs);u=[x-sum(xs)/n for x in xs]
 for q in range(min(n,4)):
  r=hac([float(x) for x in xs],q)
  # Independent Bartlett Toeplitz quadratic form, including both off-diagonals.
  S=sum(u[a]*u[b]*max(F(0),1-F(abs(a-b),q+1)) for a in range(n) for b in range(n))/n
  check(f"HAC-{i}-{q}-mean",r["mean"],sum(xs)/n);check(f"HAC-{i}-{q}-S",r["S"],S);check(f"HAC-{i}-{q}-variance",r["variance"],S/n)
  assert r["p"] is None
for ps in ([F(4,100),F(1,100),F(3,100)],[F(1,100),None,F(4,100),F(1,100)],[F(1),F(0),F(1,2),F(1,3)]):
 p=[F(1) if v is None else v for v in ps];m=len(p);order=sorted(range(m),key=p.__getitem__);ranked=[p[j] for j in order];harm=sum(F(1,j) for j in range(1,m+1))
 for method in ("holm","by","bh"):
  r=adjust_pvalues([None if p is None else float(p) for p in ps],method,bh_evidence="UNIT_ARITHMETIC_ONLY")
  expected=[]
  for k in range(m):
   if method=="holm":v=min(F(1),max((m-j)*ranked[j] for j in range(k+1)))
   else:v=min(F(1),min(F(m,j+1)*ranked[j]*(harm if method=="by" else 1) for j in range(k,m)))
   expected.append(v)
  restored=[None]*m
  for j,v in zip(order,expected):restored[j]=v
  for j,v in enumerate(restored):check(f"{method}-{ps}-{j}",r["adjusted"][j],v)
def solve(A,b):
 a=[[F(v) for v in row]+[F(rhs)] for row,rhs in zip(A,b)];n=len(a)
 for j in range(n):
  k=next(i for i in range(j,n) if a[i][j]);a[j],a[k]=a[k],a[j];s=a[j][j];a[j]=[v/s for v in a[j]]
  for k in range(n):
   if k!=j:s=a[k][j];a[k]=[v-s*w for v,w in zip(a[k],a[j])]
 return [a[i][-1] for i in range(n)]
X=[[1,i,i%2] for i in range(6)];y=[1,1,2,4,8,3];p=3
A=[[sum(F(row[i])*row[j] for row in X) for j in range(p)] for i in range(p)]
b=[sum(F(row[i])*v for row,v in zip(X,y)) for i in range(p)]
beta=solve(A,b);res=[F(v)-sum(F(a)*b for a,b in zip(row,beta)) for row,v in zip(X,y)]
r=ols(y,X)
for i,v in enumerate(beta):check(f"OLS-beta-{i}",r["beta"][i],v)
for i,v in enumerate(res):check(f"OLS-residual-{i}",r["residual"][i],v)
for j in range(p):check(f"OLS-orthogonal-{j}",sum(row[j]*a for row,a in zip(X,r["residual"])),0)
def ranks(xs):
 sort=sorted(xs)
 return [F(sort.index(v)+1+len(sort)-list(reversed(sort)).index(v),2) for v in xs]
for rank in (False,True):
 xs=list(map(F,[3,1,2,2,5]));ys=list(map(F,[0,2,1,1,4]));a,b=(ranks(xs),ranks(ys)) if rank else (xs,ys);n=len(a)
 cross=n*sum(x*y for x,y in zip(a,b))-sum(a)*sum(b)
 den=(n*sum(x*x for x in a)-sum(a)**2)*(n*sum(y*y for y in b)-sum(b)**2)
 with localcontext() as ctx:
  ctx.prec=80
  d=lambda q:Decimal(q.numerator)/Decimal(q.denominator)
  expected=d(cross)/d(den).sqrt()
 check("CORRELATION-rank="+str(rank),correlation(xs,ys,rank=rank)["value"],expected)
for n in (31,32,242,243,1023,1024,3124,3125):
 r=0
 while (r+1)**5<=n:r+=1
 check("FIFTHROOT-"+str(n),bandwidth(n,1,0),r)
result=dict(executor="GPT Work independent installed-wheel mathematics",reviewed_sha="5a5e093c2e9b39abe1332e49d1df40d20f9fd33f",script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),checks=checks,passed=len(checks),failed=0,finite_sample_inference_approved=False)
(out/"independent-implementation-math.json").write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps({k:v for k,v in result.items() if k!="checks"},indent=2))

