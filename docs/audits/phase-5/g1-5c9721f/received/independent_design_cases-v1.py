"""Concrete design countermodels and boundary references; no AQRP implementation imports."""
import json,pathlib,hashlib
from fractions import Fraction as Q
from datetime import datetime,timezone,timedelta
O=pathlib.Path(__file__).parent;C=O.parent/'p5-g1-review-5c9721f';records=[]
def record(case,inputs,answers,interpretation):records.append({'case':case,'inputs':inputs,'independent_answers':answers,'interpretation':interpretation,'level':'Design reference / not an implementation failure'})
def s(x):return str(x)
# A strict global priority sort cannot also emit each Match/Fill/Account group contiguously.
events=[{'id':'A.Match','priority':70,'seq':1},{'id':'B.Match','priority':70,'seq':2},{'id':'A.Fill','priority':80,'seq':3},{'id':'A.Account','priority':90,'seq':4},{'id':'B.Fill','priority':80,'seq':5},{'id':'B.Account','priority':90,'seq':6}]
total=[e['id'] for e in sorted(events,key=lambda e:(e['priority'],e['seq']))];atomic=['A.Match','A.Fill','A.Account','B.Match','B.Fill','B.Account'];assert total!=atomic
record('C01_ATOMIC_TOTAL_ORDER',{'same_logical_time':True,'events':events},{'strict_tuple':total,'atomic_transaction_order':atomic},'Specify parent transaction vs child events and one deterministic log/replay key. This does not claim actual P5 code exists.')
# Post-fill risk must see preceding committed state, even if initial cash reservations fit.
E=Q(1000);fee=Q(1);p=Q(100);limit=Q(15,100);one=p/(E-fee);two=(2*p)/(E-2*fee);assert one<limit<two
record('C01_RISK_STATE_REFERENCE',{'equity':'1000','two_accepted_buy_fragments':'1 share each','price':'100','fee':'1 each','current_asset_limit':'0.15'},{'individual_candidate_weight':s(one),'after_both_weight':s(two),'cash_pre_reservation_sufficient':True},'Abstract accepted-order state: second Fill must re-evaluate on the first committed state; does not assert complete current P4 request feasibility.')
# The same short-sale proceeds belong to unsettled and restricted until settlement.
C=Q(1100);U=Q(100);S=Q(100);V=Q(100);literal0=C-U-S-V;literal1=C-S-V;union_reserve=max(U,S)+V;available_disjoint=C-union_reserve
assert literal0==800 and literal1==available_disjoint==900
record('C02_SHORT_SETTLEMENT_OVERLAP',{'initial_cash':'1000','short_open':'1 @100','fees':'0, isolated bucket proof','cash_after':'1100','U_short':'100','S_all_unclosed_proceeds':'100','V_margin':'100'},{'literal_before_settlement':s(literal0),'literal_after_settlement':s(literal1),'cash_minus_union_of_declared_restrictions':s(available_disjoint),'economic_equity_both':'1000'},'Either partition settled/unsettled restricted short proceeds or explicitly propose/approve an additional temporary funding reserve. Existing disjoint-reserve statement does not define that reserve.')
# Fees included do not remove the overlap.
assert Q(1099)-U-S-V==799 and Q(1099)-max(U,S)-V==899
record('C02_WITH_PROFILE_MIN_FEE',{'actual_cash_after_short_fill':'1099','unsettled_notional':'100','short_proceeds':'100','margin':'100','commission':'1'},{'literal_available':'799','disjoint_available':'899','equity':'999'},'A minimum commission changes both answers by1, not the100 overlap.')
# Sell-limit lower protection does not cap commission on favorable price gaps.
decision=Q(100);sell_floor=Q(95);actual=Q('200200');commission=actual/1000;budget=Q(10)
assert actual>sell_floor and commission>budget
record('C03_SELL_FEE_UPPER',{'decision_raw_price':'100','quantity':'1','sell_min_price':'95','next_raw_open':'200400.40','slippage_bps':'10','actual_sell_tick_price':'200200.00','fee_rate':'0.001','F':'10'},{'actual_commission':'200.20','fee_upper_if_assumed_105_price':'1.00','passes_sell_lower_bound':True},'Sell-only lower bound and symmetric +/-5% wording differ. Define which executions qualify and cap cumulative actual fees before commit. Positive gap rejection is a valid explicit synthetic choice.')
# Independent FIFO fragments vs whole original entry: identical total account P&L, different trade stats.
entry_fee=Q(1);first=(Q(104)-100)-entry_fee/2-1;second=(Q(97)-100)-entry_fee/2-1;net=first+second;assert (first,second,net)==(Q('2.5'),Q('-4.5'),-2)
record('C04_FIFO_COMPLETION_UNIT',{'entry':'BUY2 @100, fee1','exit1':'SELL1 @104, fee1','exit2':'SELL1 @97, fee1','FIFO':'same original entry lot'},{'fragment_net':[s(first),s(second)],'fragment_win_rate':'1/2','fragment_profit_loss_ratio':'5/9','whole_entry_net':s(net),'whole_entry_win_rate':'0/1','whole_entry_ratio':'UNDEFINED_NO_WINNER'},'Freeze whether completed trade means each closed FIFO fragment or an entire entry lot/flat-to-flat episode. FIFO and fee allocation alone do not state grouping.')
# A time/lot accrual policy is needed separately from aggregate position cost.
gross=Q('2.07');entry_exit=Q(2);holding_time_cost=Q('.04')+Q('.04');pooled_cost=Q('.12')/2;assert gross-entry_exit-holding_time_cost<0<gross-entry_exit-pooled_cost
record('C04_BORROW_LOT_ATTRIBUTION',{'short_lot_A':'1@1000 session1, entry fee1','short_lot_B':'1@1000 session2, entry fee1','day1_total_borrow':'0.04','day2_total_borrow':'0.08','cover_A':'1@997.93 next open, exit fee1'},{'per-lot-time_accrual_A':'0.08','pooled-position_cost_A':'0.06','net_if_time':'-0.01','net_if_pooled':'+0.01'},'Both derive from the same0.12 position cost; choose/accrue a specific allocation before FIFO profitability is deterministic. Total ledger P&L remains identical.')
# A zero-width open allows a timely previous submission and forbids retroactive fills.
open_=datetime(2024,1,5,9,tzinfo=timezone.utc);cases=[('before',open_-timedelta(microseconds=1),open_,True),('same',open_,open_,False),('after',open_+timedelta(microseconds=1),open_,False),('late_slice',open_-timedelta(microseconds=1),open_+timedelta(microseconds=1),False)]
for name,submitted,available,want in cases:
 eligible=submitted<open_ and available<=open_;assert eligible==want
 record('T01_'+name,{'submitted':submitted.isoformat(),'slice_available':available.isoformat(),'logical_open':open_.isoformat()},{'may_fill_this_open':eligible},'Strict future-open and zero-width availability design reference, not a product test.')
# Capacity including complete odd-lot close boundary.
cap=10;requests=[6,6];fills=[]
for qty in requests:fill=(min(qty,cap)//3)*3;fills.append(fill);cap-=fill
assert fills==[6,3] and cap==1
record('T03_CAPACITY',{'capacity':10,'orders':[6,6],'lot':3},{'fills':fills,'remaining_capacity':cap},'Shared capacity cannot reset per order; complete odd-lot-close exception needs separate final-fill test.')
record('T03_ODD_CLOSE',{'old_position':5,'target':0,'lot':3,'first_fill':-3},{'remaining_position':2,'last_full_close':-2,'partial_of_1':'NOT_A_LOT_AND_NOT_FULL_CLOSE'},'Final complete close may use explicit full-close exception; arbitrary nonlot fragments do not gain an exception.')
output={'fixed_sha':'5c9721f96679f4d495b7b3b93af3e2e31e66ae62','reviewer':'GPT Work supplemental reviewer','scope':'Independent plan countermodels, not P5 implementation outcomes','records':records,'cases':len(records),'formal_Test':False}
(O/'INDEPENDENT_DESIGN_CASES.json').write_text(json.dumps(output,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({'concrete_design_cases':len(records),'countermodels':'C01-C04','timing_capacity_boundaries':'PASS as reference arithmetic'}))
