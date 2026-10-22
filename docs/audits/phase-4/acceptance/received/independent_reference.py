"""GPT Work independent exact-rational reference, derived from approved G1 rules.
No AQRP import, no generated expected values from product code.
"""
from fractions import Fraction as Q
Z=Q(0);RT=Q(1,10**12);CT=Q(1,10**8)
def reference(x):
 data=x['inputs'];p=x['policy'];lim=x['constraints'];profile=x['profile'];a=data['account']['data'];E=Q(a['equity'])
 maps={k:{r['security_id']:r for r in data[k]['data']} for k in ['securities','prices','status','exposures','permissions']};ids=sorted(maps['securities']);old={s:Z for s in ids};old.update({r['security_id']:Q(r['quantity']) for r in a['positions']});price={s:Q(maps['prices'][s]['price']) for s in ids};lots={s:Q(maps['prices'][s]['lot']) for s in ids}
 scoremaps={e['data']['factor_key']:{r['security_id']:r for r in e['data']['rows']} for e in data['scores']};coef={k:Q(v) for k,v in p['factor_weights'].items()};den=sum(map(abs,coef.values()));scores={}
 for s in ids:
  if maps['status'][s]['tradable'] and maps['status'][s]['in_universe'] and all(s in rows and rows[s]['valid'] for rows in scoremaps.values()):scores[s]=sum(coef[k]*Q(str(scoremaps[k][s]['score'])) for k in coef)/den
 rank=sorted(scores,key=lambda s:(-scores[s],s));w={s:Z for s in ids}
 if p['mode']=='LONG_ONLY':
  selected=rank[:p['top_k']];parts={s:Q(1) if p['weighting']=='equal' else max(scores[s],Z) for s in selected};total=sum(parts.values())
  if total:w.update({s:v/total for s,v in parts.items()})
 else:
  L=(Q(p['gross'])+Q(p['net']))/2;H=(Q(p['gross'])-Q(p['net']))/2
  if not rank:
   if L or H:return {'status':'INFEASIBLE','reason':'INFEASIBLE_EMPTY_LEG'}
  elif p['weighting']=='equal':
   longs=rank[:p['long_k']] if L else [];shorts=rank[-p['short_k']:][::-1] if H else []
   if set(longs)&set(shorts) or (L and H and p['long_k']+p['short_k']>len(rank)):return {'status':'INFEASIBLE','reason':'INFEASIBLE_OVERLAPPING_LEGS'}
   if (L and not longs) or (H and not shorts):return {'status':'INFEASIBLE','reason':'INFEASIBLE_EMPTY_LEG'}
   for group,budget in [(longs,L),(shorts,-H)]:
    for s in group:w[s]=budget/len(group)
  else:
   m=sum(scores.values())/len(rank);center={s:scores[s]-m for s in rank};longs=[s for s in rank if center[s]>0][:p['long_k']] if L else [];shorts=[s for s in rank[::-1] if center[s]<0][:p['short_k']] if H else []
   if (L and not longs) or (H and not shorts):return {'status':'INFEASIBLE','reason':'INFEASIBLE_EMPTY_LEG'}
   for group,budget in [(longs,L),(shorts,-H)]:
    total=sum(abs(center[s]) for s in group)
    for s in group:w[s]=budget*abs(center[s])/total
 ideal={s:w[s]*E/price[s] for s in ids};rounded={s:ideal[s] if ideal[s]==old[s] else (1 if ideal[s]>=0 else -1)*int(abs(ideal[s])/lots[s])*lots[s] for s in ids}
 def assess(q,post):
  v={s:q[s]*price[s]/E for s in ids};dq={s:q[s]-old[s] for s in ids};gross=sum(map(abs,v.values()));net=sum(v.values());short=sum(max(-q[s]*price[s],Z) for s in ids);cash=E*(1-net);restr=short+Q(a['nonshort_restriction']);reserve=Q(profile['fee_reserve']);free=cash-restr-short-reserve;turn=sum(abs(dq[s])*price[s] for s in ids)/E;beta=sum(v[s]*Q(maps['exposures'][s]['beta']) for s in ids);industries={};bad=set()
  def bound(code,val,lo=None,hi=None,tol=RT):
   if (lo is not None and val<lo-tol) or (hi is not None and val>hi+tol):bad.add(code)
  for s in ids:bound('ASSET_WEIGHT',abs(v[s]),hi=Q(lim['per_asset'][s]))
  for code,key,val in [('GROSS','gross_max',gross),('LEVERAGE','leverage_max',gross),('TURNOVER','turnover_max',turn)]:bound(code,val,hi=Q(lim[key]))
  bound('NET',net,Q(lim['net_min']),Q(lim['net_max']));bound('BETA',beta,Q(lim['beta_min']),Q(lim['beta_max']));bound('FREE_CASH',free,lo=Z,tol=CT)
  if not lim['allow_cash_only'] and gross<RT:bad.add('CASH_ONLY_FORBIDDEN')
  for s in ids:
   sector=maps['exposures'][s]['industry'];cell=industries.setdefault(sector,{'net':Z,'gross':Z});cell['net']+=v[s];cell['gross']+=abs(v[s]);permission=maps['permissions'][s]
   if post and dq[s]:
    if (q[s]/lots[s]).denominator!=1:bad.add('TARGET_LOT_MISMATCH')
    if (dq[s]/lots[s]).denominator!=1 and not(q[s]==0 and old[s]!=0 and profile['allow_full_close_odd_lot']):bad.add('DELTA_LOT_MISMATCH')
   if dq[s]:
    if not maps['status'][s]['tradable']:bad.add('NOT_TRADABLE')
    if min(max(-dq[s],Z),max(old[s],Z))>Q(permission['sellable_qty']):bad.add('SELLABLE')
   if q[s]<0:
    if not permission['short_permission']:bad.add('SHORT_PERMISSION')
    if -q[s]>Q(permission['borrow_limit_total']):bad.add('BORROW_TOTAL')
  for sector,cell in industries.items():
   cfg=lim['industries'][sector];bound('INDUSTRY_NET',cell['net'],Q(cfg['net_min']),Q(cfg['net_max']));bound('INDUSTRY_GROSS',cell['gross'],hi=Q(cfg['gross_max']))
  return {'metrics':{'weights':v,'quantities':q,'deltas':dq,'cash':cash,'restricted_cash':restr,'margin_requirement':short,'fee_reserve':reserve,'free_cash':free,'gross':gross,'net':net,'cash_weight':1-net,'leverage':gross,'turnover':turn,'half_turnover':turn/2,'beta':beta,'industries':industries},'failures':sorted(bad)}
 pre=assess(ideal,False);post=assess(rounded,True);return {'status':'REJECTED' if pre['failures'] or post['failures'] else 'SUCCEEDED','ideal':ideal,'rounded':rounded,'ranked':rank,'scores':scores,'pre':pre,'post':post}
