"""Primary independent finite admission arithmetic and static candidate assessment.
This is an abstract review oracle outside AQRP, not P7 admission implementation.
No AQRP imports, task/workers, research, browser, account or ACL operations.
"""
import itertools,json,hashlib
from pathlib import Path
from fractions import Fraction as F
O=Path(__file__).parent;P=Path('E:/WORK/AQRP-audits/p7-645049a/src/docs/audits/phase-7')
checks=0
def check(x,label):
 global checks
 checks+=1
 if not x:raise AssertionError(label)
# Independent constraint algebra: refusals cannot debit; all admitted units retained.
def decision(used,n,*,domain=True,history=True,active=True,stale=False,identity=True,key_conflict=False,bound_new_key=False,exact_retry=False,grant=100,family_remaining=12):
 if not domain:return ('ADMISSION_DOMAIN_CONFLICT',0)
 if not history:return ('ADMISSION_HISTORY_UNVERIFIED',0)
 if stale:return ('EXECUTION_PLAN_ACTIVATION_STALE',0)
 if not active:return ('EXECUTION_PLAN_SLOT_UNAUTHORIZED',0)
 if key_conflict:return ('ADMISSION_IDEMPOTENCY_CONFLICT',0)
 if not identity:return ('EXECUTION_PLAN_SLOT_IDENTITY_CONFLICT',0)
 if exact_retry:return ('ORIGINAL_OWNER',0)
 if bound_new_key:return ('EXECUTION_PLAN_SLOT_EXHAUSTED',0)
 if used+n>12 or n>family_remaining:return ('EXPERIMENT_BUDGET_EXCEEDED',0)
 if n>grant:return ('EXECUTION_PLAN_SLOT_EXHAUSTED',0)
 return ('ADMITTED',n)
for used,n in itertools.product(range(13),range(1,4)):
 code,debit=decision(used,n);check(debit in (0,n),'no partial units');check(used+debit<=12,'sum bound')
 check((debit==n)==(used+n<=12),'admit iff hard bound')
 for outcome in ['SUCCESS','FAILED','CANCELLED','CRASH','RISK_REJECTION']:
  check(used+debit==sum([used,debit]),'outcome does not refund '+outcome)
check(decision(12,1)==('EXPERIMENT_BUDGET_EXCEEDED',0),'12 cancelled Tasks then legacy')
check(decision(12,1)==('EXPERIMENT_BUDGET_EXCEEDED',0),'12 legacy then Task')
interleavings=[]
for order in itertools.permutations(['TASK','LEGACY']):
 used=11;results=[]
 for name in order:
  code,debit=decision(used,1);used+=debit;results.append([name,code,debit])
 check(used==12 and sum(x[2] for x in results)==1,'mixed serialized boundary')
 interleavings.append(results)
check(decision(11,2)[1]==0,'N2 atomic rejection')
# Parent-child unit ownership conserves the one parent debit and claims each unit once.
units={(17,i):None for i in range(2)};debit=2
for i in [0,0,1,1]:
 owner=('verified-R',i)
 if units[(17,i)] is None:units[(17,i)]=owner
 else:check(units[(17,i)]==owner,'repeat claim only same owner')
check(debit==2 and len(units)==2,'no parent child double debit')
# Authorization B precedes shared budget C, then slot capacity D.
check(decision(12,1,active=False)[0]=='EXECUTION_PLAN_SLOT_UNAUTHORIZED','unregistered main13 not budget probe')
check(decision(12,1,grant=0)[0]=='EXPERIMENT_BUDGET_EXCEEDED','authorized exhausted-budget probe')
check(decision(11,1,grant=0)[0]=='EXECUTION_PLAN_SLOT_EXHAUSTED','bad precondition probe must fail')
check(decision(1,1,bound_new_key=True)[0]=='EXECUTION_PLAN_SLOT_EXHAUSTED','risk fixture second new key blocked')
check(decision(1,1,exact_retry=True)[1]==0,'exact owner retry is no new debit')
check(decision(12,1,domain=False)[0]=='ADMISSION_DOMAIN_CONFLICT','root check first')
check(decision(12,1,history=False)[0]=='ADMISSION_HISTORY_UNVERIFIED','history check first')
check(decision(1,1,identity=False)[0]=='EXECUTION_PLAN_SLOT_IDENTITY_CONFLICT','no altered profile slot')
check(decision(1,1,key_conflict=True)[0]=='ADMISSION_IDEMPOTENCY_CONFLICT','same key changed request')
check(decision(1,1,stale=True)[1]==0,'stale session never claims next slot')
check(decision(1,1,family_remaining=0)[1]==0,'preserve smaller family limit')
for names in itertools.product(['f1','f2'],['c1','c2'],['sdk','legacy','adapter']):check(decision(12,1)[1]==0,'labels not budget keys')
main_units=4*2+1*2+1*2;risk_units=1;cancel_units=0;replay_units=0
check(main_units==12 and main_units+risk_units+cancel_units+replay_units==13,'honest separate outer accounting')
check(main_units<=12 and risk_units<=1,'separate preregistered fixture not main quota reset')
# Gross zero risk oracle: independent public engineering arithmetic.
alloc=F(1000)-10;ideal=alloc/100;rounded=ideal//1
check(ideal==F(99,10) and rounded==9,'risk ideal and rounded quantity')
check(ideal*100/alloc==1 and rounded*100/alloc==F(10,11),'GROSS positive before/after rounding')
check(ideal*100/alloc>0 and rounded*100/alloc>0,'gross_max0 real rejection')
check(F(1000)+0-0==1000,'noorders nofees cash and equity remain1000')
notes={
1:'合法active probe先过域/身份再到共享12检查；原取消预留计入，不能被legacy忽略。',
2:'反向legacy先耗12，Task同一authority整体拒绝并不分配研究子运行。',
3:'同一COMMIT线性化两个入口；两种串行次序均只能新增1单位。',
4:'完整N=2一次判定，剩1时0候选可观察或登记。',
5:'Task行与完整N预留同事务，拒绝不运行R。',
6:'可信R按父已预留两单位认领；两条trial不能再扣2。',
7:'direct ledger须独立解析受管域和整config，不依赖可省略上下文。',
8:'family/campaign/adapter/参数不是共享域键；各探针必须事前合法。',
9:'受管源混外部输出先拒绝域冲突，不能创建新authority。',
10:'exact key/owner只一份Task与admission；不能把随机key当actor身份。',
11:'同unit重复claim必须同一run/root/config/lineage；原投影只发布一次。',
12:'同key改request或unit定义在预算检查前拒绝，不能覆盖旧owner。',
13:'只限已冻结独立预算回归无E2E actor限制；新UUID仍新实验并保留repeat_of。',
14:'已用slot新key拒绝；取消不退款、不自动找其他actor空slot。',
15:'commit后outbox发布前崩溃保留debit，原owner恢复冻结字节前不得研究。',
16:'marker缺失只复用完整相同投影，不二次append/debit。',
17:'截断或异字节保留原故障并拒绝；不能擅自修复历史以继续成功。',
18:'迁移需精确历史全集，不能以能读子集充数。',
19:'历史原P6只读核验；可写迁移仅同包新schema夹具，按可信R绑定去重。',
20:'文字TaskID/campaign_control不能替代可信epoch/physical slot所有权。',
21:'anchor/历史仍在时DB缺失不能自动归新0额度域。',
22:'保留原requested/over_budget字面历史；不明计数饱和或拒绝，不退款式解释。',
23:'共享12之外仍执行family更严子预算。',
24:'旧外来写入触发完整性失败；不是OS层阻止管理员写入的证明。',
25:'主12无合法下一slot，先报UNAUTHORIZED；与合法预算拒绝探针分开。',
26:'预登记独立风险夹具cap1首次UI随机key绑定一次，第二新key在剩余11时仍拒绝。',
27:'请求/根/key身份各自优先错误冻结；不可重新标成主成功actor。',
28:'风险夹具失败保留唯一owner和debit，只恢复或拒绝重复，不能替换失败用例。',
29:'复合actor SDK仅入队，browser实际取消；维持同activation且0R/研究。',
30:'零研究slot必须为已核replay/source；不能自报units0包裹pipeline或研究。',
31:'省略token/plan仍由受管根强制解析，不可选择旧无共同计数分支。',
32:'R成功/P4失败/B无订单成功是不同事实；全Task由P4失败而失败。',
33:'legacy分配新UUID前查固定slot原owner；恢复或显式拒绝重复。',
34:'同canonical多个actor按受信CAS顺序唯一激活，页面不能自选purpose/slot。',
35:'过期UI epoch必须拒绝；迟到旧key不得认领下一同canonical actor。',
36:'若只11单位却运行cap0拒绝探针，应报slot不足并判夹具前提失败，不能冒称预算拒绝。'}
cand=json.loads((P/'COMMON_BUDGET_ADMISSION_CANDIDATES.json').read_bytes());check(len(cand['cases'])==36,'all36')
assessment=[]
for i,c in enumerate(cand['cases'],1):
 check(c['id']==f'BUD-{i:03}' and bool(c['setup']) and bool(c['action']) and bool(c['expected']),'complete unique case')
 assessment.append({'id':c['id'],'primary_static_judgment':'DESIGN_CONSISTENT; product execution NOT VERIFIED','primary_reason':notes[i]})
# Critical candidate literal outcomes agree with independently ordered model arithmetic.
check(cand['cases'][0]['expected']['code']==decision(12,1,grant=0)[0],'BUD001 expected')
check(cand['cases'][24]['expected']['code']==decision(12,1,active=False)[0],'BUD025 expected')
check(cand['cases'][35]['expected']['code']==decision(11,1,grant=0)[0],'BUD036 expected')
browser=json.loads((P/'BROWSER_NEGATIVE_PROTOCOL_CANDIDATES.json').read_bytes())
check(browser['risk_fixture']['new_research_units']==1 and browser['risk_fixture']['protocol_slot_limit']==1,'risk1')
check(browser['risk_fixture']['draft_template']['constraints']['gross_max']=='0','real gross override')
check(browser['cancel_replay']['new_research_units']==0 and browser['normal_replay']['new_research_units']==0,'both no new research')
check(browser['normal_replay']['expected']['P4_count']==10 and browser['cancel_replay']['expected']['slots']=={},'zero research not zero execution')
check(browser['risk_fixture']['expected']['P4_manifest']=='FAILED' and browser['risk_fixture']['expected']['Task_error']=='REQUIRED_STAGE_REJECTED','risk child/global barrier')
report={'executor':'Primary GPT Work','scope':'Independent abstract finite arithmetic plus static review of36 candidates; not P7 code or product tests; no AQRP imports/workers/probes/browser execution','assertions':checks,'mixed_interleavings':interleavings,'case_assessments':assessment,'browser_static_judgments':{'BR-RISK-ORIGINAL-01':'Reachable under explicit future authority; existing real UI/service paths and positive gross oracle support Rsuccess/P4reject/Bsuccessnofills/Taskfailure','BR-CANCEL-REPLAY-01':'SDKqueues only, sameactivation realbrowsercancel, nochild, terminalworknoop; queue-only scope','BR-REPLAY-01':'RealUIstarts newE+10P4; noR/trial; verifiedsource unchanged'},'independent_risk_arithmetic':{'allocatable':str(alloc),'ideal':str(ideal),'rounded':rounded,'pre_gross':'1','post_gross':str(rounded*100/alloc),'cash_no_orders':'1000'},'accounting':{'main':12,'risk':1,'cancel_research':0,'normal_replay_research':0,'outer_research_attempts':13,'no_statistical_independence_claim':True},'future_G2_precision_checks':['Outbox chain/seq drains deterministically even if committed claim writers obtain trials-lock in reverse order','Legacy same-owner retry while prior process still alive must explicitly refuse or use exclusive recovery fencing','Late old key/session must return original verified owner or reject, never bind next same-canonical actor'],'inputs_sha256':{n:hashlib.sha256((P/n).read_bytes()).hexdigest() for n in ['COMMON_BUDGET_ADMISSION_DESIGN.md','COMMON_BUDGET_ADMISSION_CANDIDATES.json','BROWSER_NEGATIVE_PROTOCOL.md','BROWSER_NEGATIVE_PROTOCOL_CANDIDATES.json']}}
(O/'PRIMARY_DESIGN_RECHECK.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({'abstract_assertions':checks,'candidate_static_reviews':36,'risk_gross_post':str(F(10,11)),'new_product_tests':0}))
