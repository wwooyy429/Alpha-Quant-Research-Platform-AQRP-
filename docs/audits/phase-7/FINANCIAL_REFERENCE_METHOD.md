# 主层金融可行性的开发方纯stdlib设计模型

下面仅把已审工程规则写成独立有限状态参考，不导入AQRP、不执行产品或真实账户。模型使用Fraction精确计算、公开设计候选的选股顺序；记录每条顺序的实际数学状态、资金桶、预留和P4/P5约束，不能称为原始产品账本或P7测试通过。模型不能证明真实服务的来源/权限/hash/Task实现，后者仍须实施后的真实SDK/CI/浏览器及GPT Work G2。

```python
from pathlib import Path
from fractions import Fraction as F
from itertools import product
from copy import deepcopy
import json

OUT = Path(__file__).parent
REF = json.loads((OUT / 'MAIN_PIPELINE_CANDIDATES.json').read_bytes())
SIDS = [f'SYN_A:{a:03d}' for a in range(1, 7)]
CHECKS = 0

def dump(value):
    if isinstance(value, F):
        return str(value)
    if isinstance(value, dict):
        return {str(k): dump(v) for k, v in value.items()}
    if isinstance(value, (tuple, list)):
        return [dump(v) for v in value]
    return value

def cash(state):
    u = sum((v['amount'] for v in state['cashlots']), F(0))
    on = sum((o['quantity'] * 105 for o in state['orders'] if o['side'] == 'BUY'), F(0))
    of = sum((o['quantity'] for o in state['orders']), F(0))
    marked = sum(state['positions'].values()) * 100
    unused = state['budget'] - state['paid'] - of if state['has_budget'] else F(0)
    alloc = state['cash_set'] - on - of - unused
    return {
        'cash_set': state['cash_set'], 'U_free': u, 'U_short': F(0), 'S_set': F(0),
        'cash_total': state['cash_set'] + u, 'marked_value': marked,
        'O_N': on, 'O_F': of, 'F_unused': unused,
        'short_value': F(0), 'P_res': F(0), 'Z': F(0),
        'available': state['cash_set'] - on - of,
        'cash_alloc': alloc, 'equity_alloc': alloc + marked,
        'equity': state['cash_set'] + u + marked,
    }

def saleable(state, sid, day):
    return sum((v['quantity'] for v in state['lots'] if v['sid'] == sid and v['due'] <= day), F(0))

def p4_metrics(state, prior_positions, quantities):
    c = cash(state)
    e = c['equity_alloc']
    if e <= 0:
        return {'passed': False, 'errors': ['P4_POSITIVE_ALLOCATION'], 'equity_alloc': e}
    marked = sum(quantities.values()) * 100
    weights = {sid: q * 100 / e for sid, q in quantities.items()}
    turnover = sum(abs(quantities[sid] - prior_positions[sid]) * 100 for sid in SIDS) / e
    errors = []
    if max(abs(w) for w in weights.values()) > 1:
        errors.append('P4_ASSET_WEIGHT')
    if sum(abs(w) for w in weights.values()) > 2:
        errors.append('P4_GROSS_LEVERAGE_INDUSTRY')
    if not -2 <= sum(weights.values()) <= 2:
        errors.append('P4_NET_INDUSTRY')
    if not -3 <= sum(weights.values()) <= 3:
        errors.append('P4_BETA')
    if turnover > 4:
        errors.append('P4_TURNOVER')
    if e - marked < 0:
        errors.append('P4_FREE_CASH')
    return {'passed': not errors, 'errors': errors, 'equity_alloc': e,
            'free_cash': e - marked, 'max_asset_weight': max(abs(w) for w in weights.values()),
            'gross': sum(abs(w) for w in weights.values()), 'turnover': turnover}

def p5_metrics(state):
    c = cash(state)
    e = c['equity']
    errors = []
    if e <= 0: errors.append('ACTUAL_NONPOSITIVE_EQUITY')
    if c['available'] < 0: errors.append('ACTUAL_FREE_CASH')
    if c['F_unused'] < 0: errors.append('COMMISSION_BUDGET')
    if min(state['positions'].values()) < 0: errors.append('UNEXPECTED_SHORT')
    if e > 0:
        weights = [q * 100 / e for q in state['positions'].values()]
        if max(abs(w) for w in weights) > 1: errors.append('ACTUAL_ASSET')
        if sum(abs(w) for w in weights) > 2: errors.append('ACTUAL_GROSS_LEVERAGE')
        if not -2 <= sum(weights) <= 2: errors.append('ACTUAL_NET_INDUSTRY')
        if not -3 <= sum(weights) <= 3: errors.append('ACTUAL_BETA')
        if state['decision_turnover'] / state['decision_equity'] > 4: errors.append('ACTUAL_TURNOVER')
    return {'passed': not errors, 'errors': errors, 'account': c,
            'decision_turnover': state['decision_turnover'], 'decision_equity': state['decision_equity']}

def run(sequence, days, choices, *, fee_budget):
    global CHECKS
    state = {'cash_set': F(1000), 'cashlots': [], 'lots': [],
             'positions': dict.fromkeys(SIDS, F(0)), 'orders': [],
             'budget': F(fee_budget), 'has_budget': False, 'paid': F(0), 'fees': F(0), 'slippage': F(0),
             'decision_turnover': F(0), 'decision_equity': F(1000)}
    logs, p4_records, fills = [], [], []
    pending = None
    switch_index = 0

    def record(day, stage, extra=None):
        logs.append({'day_index': day, 'stage': stage, 'account': cash(state),
                     'positions': deepcopy(state['positions']), 'cashlots': deepcopy(state['cashlots']),
                     'live_orders': deepcopy(state['orders']), 'budget': state['budget'] if state['has_budget'] else None,
                     'paid_this_decision': state['paid'], 'cumulative_fees': state['fees'],
                     'cumulative_slippage': state['slippage'], 'detail': extra})

    def fail(day, stage, errors, detail):
        record(day, stage, detail)
        return {'model_status': 'EXPECTED_DESIGN_REJECTION', 'day_index': day,
                'stage': stage, 'errors': errors, 'trace': logs, 'P4': p4_records, 'fills': fills}

    for day in range(1, 23):
        for lot in list(state['cashlots']):
            if lot['due'] <= day:
                state['cash_set'] += lot['amount']
                state['cashlots'].remove(lot)
        record(day, 'SETTLEMENT_OPEN')
        if pending is not None and pending['eligible'] == day:
            orders = state['orders']
            if len(orders) == 2:
                buy_first = choices[switch_index] == 'BUY_FIRST'
                switch_index += 1
                orders = sorted(orders, key=lambda o: (o['side'] != ('BUY' if buy_first else 'SELL')))
            else:
                orders = list(orders)
            for order in orders:
                before = deepcopy(state)
                sid, q, side = order['sid'], order['quantity'], order['side']
                px = F('100.1') if side == 'BUY' else F('99.9')
                fee = max(F(1), q * px / 1000)
                assert fee == 1 and 0 < q <= 10
                CHECKS += 2
                state['orders'].remove(order)
                if side == 'BUY':
                    state['cash_set'] -= q * px + fee
                    state['positions'][sid] += q
                    state['lots'].append({'sid': sid, 'quantity': q, 'due': day + 1})
                else:
                    if saleable(before, sid, day) < q:
                        return fail(day, 'MATCH', ['SELLABLE'], {'order': order})
                    state['cash_set'] -= fee
                    state['cashlots'].append({'amount': q * px, 'due': day + 1})
                    state['positions'][sid] -= q
                    remain = q
                    for lot in state['lots']:
                        if lot['sid'] == sid and lot['quantity']:
                            n = min(remain, lot['quantity'])
                            lot['quantity'] -= n
                            remain -= n
                    assert remain == 0
                    CHECKS += 1
                state['paid'] += fee
                state['fees'] += fee
                state['slippage'] += q * F('0.1')
                state['decision_turnover'] += q * px
                p4 = p4_metrics(state, before['positions'], state['positions'])
                p5 = p5_metrics(state)
                CHECKS += 2
                fill = {'day_index': day, 'sid': sid, 'side': side, 'quantity': q, 'actual_price': px,
                        'fee': fee, 'sell_tax': F(0), 'slippage': q * F('0.1'),
                        'P4_post': p4, 'P5_post': p5}
                record(day, 'CANDIDATE_FILL', fill)
                if not p4['passed'] or not p5['passed']:
                    return fail(day, 'ATOMIC_FILL_WOULD_CANCEL', p4['errors'] + p5['errors'],
                                {'candidate': fill, 'note': 'Model candidate rejected before atomic commit; not a product transaction'})
                fills.append(fill)
            assert not state['orders']
            CHECKS += 1
            pending = None
        record(day, 'CLOSE_VALUATION')
        if day in days:
            index = days.index(day)
            selected = sequence[index]
            assert not state['orders']
            CHECKS += 1
            state['budget'], state['paid'], state['decision_turnover'] = F(fee_budget), F(0), F(0)
            state['has_budget'] = True
            state['decision_equity'] = cash(state)['equity']
            target = dict.fromkeys(SIDS, F(0))
            ideal = dict.fromkeys(SIDS, F(0))
            ideal[selected] = cash(state)['equity_alloc'] / 200
            target[selected] = F(ideal[selected].numerator // ideal[selected].denominator)
            pre, post = p4_metrics(state, state['positions'], ideal), p4_metrics(state, state['positions'], target)
            selling = {sid: state['positions'][sid] - target[sid]
                       for sid in SIDS if state['positions'][sid] > target[sid]}
            unavailable = {sid: q for sid, q in selling.items() if saleable(state, sid, day) < q}
            detail = {'decision': index, 'selected': selected, 'ideal': ideal, 'target': target,
                      'P4_pre': pre, 'P4_post_rounding': post, 'unavailable_long_sales': unavailable}
            p4_records.append(detail)
            CHECKS += 2
            if unavailable or not pre['passed'] or not post['passed']:
                return fail(day, 'P4_REQUIRED_DECISION', ['SELLABLE'] if unavailable else pre['errors'] + post['errors'], detail)
            assert target[selected] == 4
            CHECKS += 1
            orders = []
            for sid in SIDS:
                delta = target[sid] - state['positions'][sid]
                if delta:
                    orders.append({'sid': sid, 'side': 'BUY' if delta > 0 else 'SELL', 'quantity': abs(delta)})
            bare = cash(state)
            new_n = sum((o['quantity'] * 105 for o in orders if o['side'] == 'BUY'), F(0))
            new_f = sum((o['quantity'] for o in orders), F(0))
            accepted = bare['available'] >= new_n + new_f and bare['F_unused'] >= new_f
            CHECKS += 1
            if not accepted:
                return fail(day, 'SUBMISSION', ['BASKET_CASH_OR_FEE_BOUND'], {'new_N': new_n, 'new_F': new_f, 'account': bare})
            state['orders'] = orders
            if orders:
                pending = {'eligible': day + 1}
            record(day, 'ORDERS_ACCEPTED', {'decision': index, 'new_N': new_n, 'new_F': new_f})
    c = cash(state)
    assert not pending and not state['orders'] and not state['cashlots']
    assert len(p4_records) == len(days) and sum(state['positions'].values()) == 4
    assert c['equity'] == 1000 - state['fees'] - state['slippage']
    CHECKS += 3
    return {'model_status': 'DESIGN_FINANCIALLY_FEASIBLE', 'required_P4': len(p4_records),
            'fills': fills, 'P4': p4_records, 'trace': logs, 'final': c,
            'cumulative_fees': state['fees'], 'cumulative_slippage': state['slippage'],
            'positions': state['positions'], 'fee_budget_per_decision': fee_budget,
            'choices_used': switch_index}

all_paths, summaries = [], []
actual_days = list(range(2, 21, 2))
sequences = {
    factor: [row['expected_top1'][factor] for row in REF['sections'][::2]]
    for factor in ('momentum', 'reversal')
}
sequences['adversarial_nine_switches'] = [SIDS[i % 2] for i in range(10)]
for name, sequence in sequences.items():
    switches = sum(a != b for a, b in zip(sequence, sequence[1:]))
    results = []
    for choices in product(('BUY_FIRST', 'SELL_FIRST'), repeat=switches):
        value = run(sequence, actual_days, choices, fee_budget=50)
        assert value['model_status'] == 'DESIGN_FINANCIALLY_FEASIBLE', dump(value)
        CHECKS += 1
        case = {'sequence': name, 'choices': choices, 'result': value}
        all_paths.append(case)
        results.append(value)
    finals = {json.dumps(dump({k: v for k, v in r.items() if k in ('final','positions','cumulative_fees','cumulative_slippage')}), sort_keys=True) for r in results}
    assert len(finals) == 1
    CHECKS += 1
    summaries.append({'name': name, 'selected_sequence': sequence, 'switches': switches,
                      'permutations': len(results), 'required_P4_each': 10,
                      'fills_each': len(results[0]['fills']), 'final': results[0]['final'],
                      'cumulative_fees': results[0]['cumulative_fees'],
                      'cumulative_slippage': results[0]['cumulative_slippage'],
                      'final_positions': results[0]['positions']})

daily_sequence = [r['expected_top1']['momentum'] for r in REF['sections']]
daily = run(daily_sequence, list(range(2, 21)), ['BUY_FIRST'] * 18, fee_budget=100)
assert daily['model_status'] == 'EXPECTED_DESIGN_REJECTION' and 'SELLABLE' in daily['errors']
old100 = run(sequences['momentum'], actual_days, ['SELL_FIRST'] * 7, fee_budget=100)
assert old100['model_status'] == 'EXPECTED_DESIGN_REJECTION' and 'P4_TURNOVER' in old100['errors']
CHECKS += 2
for filename, body in (
    ('FINANCIAL_MODEL_ALL_PATHS.json', {'scope': 'Developer independent finite design model; not actual AQRP/P7 tests or original transactions', 'paths': all_paths}),
    ('SUPERSEDED_FINANCIAL_COUNTEREXAMPLES.json', {'scope': 'Original unreviewed design counterexamples preserved; not product bug or execution', 'daily19_Tplus1': daily, 'sparse10_fee100_SELL_FIRST': old100}),
    ('FINANCIAL_FEASIBILITY_CANDIDATES.json', {'scope': 'Developer design math only; no product execution or independent GPT Work verdict', 'candidate': {'research_decisions': 19, 'execution_days': actual_days, 'initial_cash': '1000', 'fee_budget_per_decision': '50', 'gross': '0.5', 'net': '0.5', 'long_budget': '0.5', 'short_budget': '0', 'lot': '1', 'target_quantity': '4', 'Tplus1': 'Original execution-session+1', 'sell_tax': 'No separate sell-tax term in existing engineering profile; zero in this fixture, no real-market claim'}, 'summaries': summaries, 'paths': len(all_paths), 'developer_model_checks': CHECKS, 'not_verified': 'Actual Task/lineage/hash/OS/financial approval/formal Test/P7 product execution'}),
):
    p = OUT / filename
    assert not p.exists(), 'Preserve old evidence; choose explicit new revision if rerunning'
    p.write_text(json.dumps(dump(body), ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
print(json.dumps(dump({'paths': len(all_paths), 'developer_model_checks': CHECKS, 'summaries': summaries, 'retained_counterexamples': [daily['errors'], old100['errors']]}), ensure_ascii=False))
```
