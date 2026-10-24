# 独立于产品导入的开发方设计参考

本参考仅计算公开输入公式下19个截面的分位清洗、样本zscore、中性化OLS、next-open标签、IC/Rank IC与分层。使用80位Decimal与3×3正规方程Gauss-Jordan，区别于产品NumPy lstsq；高精度减少正规方程条件数损失。它是开发方参考，**不是GPT Work独立审核或P7产品执行**；实际数据/时序/线性代数适用条件/真实血缘仍须独立核对。

初次编写参考的corr函数发生局部变量遮蔽，报TypeError，未生成候选输出；修正见本版本，错误作为REFERENCE_FAILED_ATTEMPT.json记载，不称原始stderr文件或产品测试。候选只来自这里显式公式，未导入AQRP或读取其运算输出。

```python
from pathlib import Path
from fractions import Fraction as F
from decimal import Decimal as D, localcontext
from datetime import date, timedelta
import json

out = Path(__file__).parent
checks = 0
with localcontext() as ctx:
    ctx.prec = 80

    def dec(v):
        return D(v.numerator) / D(v.denominator)

    def dstr(v):
        return format(v, '.40g')

    def mean(v):
        return sum(v) / D(len(v))

    def quant(v, p):
        v = sorted(v)
        q = D(len(v) - 1) * p
        lo, w = int(q), q - int(q)
        return v[lo] if lo == len(v) - 1 else v[lo] + w * (v[lo + 1] - v[lo])

    def zscore(v):
        m = mean(v)
        s = (sum((a - m) ** 2 for a in v) / D(len(v) - 1)).sqrt()
        return [(a - m) / s for a in v]

    def ranks(v):
        return [D(1 + sum(a < x for a in v)) + D(sum(a == x for a in v) - 1) / 2 for x in v]

    def corr(a, b):
        am, bm = mean(a), mean(b)
        ac, bc = [x - am for x in a], [x - bm for x in b]
        return sum(x * y for x, y in zip(ac, bc)) / (sum(x * x for x in ac) * sum(y * y for y in bc)).sqrt()

    def solve(A, b):
        n = len(b)
        M = [list(row) + [v] for row, v in zip(A, b)]
        for i in range(n):
            pivot = max(range(i, n), key=lambda j: abs(M[j][i]))
            M[i], M[pivot] = M[pivot], M[i]
            scale = M[i][i]
            assert scale
            M[i] = [v / scale for v in M[i]]
            for j in range(n):
                if j != i:
                    factor = M[j][i]
                    M[j] = [x - factor * y for x, y in zip(M[j], M[i])]
        return [row[-1] for row in M]

    def fit(y, X):
        k = len(X[0])
        A = [[sum(row[i] * row[j] for row in X) for j in range(k)] for i in range(k)]
        b = [sum(row[i] * v for row, v in zip(X, y)) for i in range(k)]
        beta = solve(A, b)
        residual = [v - sum(x * b for x, b in zip(row, beta)) for v, row in zip(y, X)]
        return beta, residual

    def price(a, i):
        return 100 + 3 * a + ((i * i + 7 * a * i) % (5 * a + 17))

    caps = [1000 + a * a * 113 for a in range(1, 7)]
    X = [[D(1), D(a % 2 == 0), D(cap).ln()] for a, cap in zip(range(1, 7), caps)]
    sections = []
    series = {f: {k: [] for k in ('pearson', 'spearman')} for f in ('momentum', 'reversal')}
    for i in range(2, 21):
        raw = [F(price(a, i), price(a, i - 2)) - 1 for a in range(1, 7)]
        labels = [F(price(a, i + 2), price(a, i + 1)) - 1 for a in range(1, 7)]
        values, lab = [dec(v) for v in raw], [dec(v) for v in labels]
        low, high = quant(values, D('0.05')), quant(values, D('0.95'))
        clean = [min(high, max(low, v)) for v in values]
        z = zscore(clean)
        beta, residual = fit(z, X)
        for j in range(3):
            assert abs(sum(row[j] * v for row, v in zip(X, residual))) < D('1e-60')
            checks += 1
        _, reversal = fit([-v for v in z], X)
        for a, b in zip(residual, reversal):
            assert abs(a + b) < D('1e-60')
            checks += 1
        record = {
            'decision_index': i,
            'session': str(date(2024, 1, 2) + timedelta(days=i)),
            'raw_momentum': [str(v) for v in raw],
            'label_entry_index': i + 1,
            'label_exit_index': i + 2,
            'raw_next_open_label': [str(v) for v in labels],
            'clean_bounds': [dstr(low), dstr(high)],
            'momentum_clean': [dstr(v) for v in clean],
            'momentum_standardized': [dstr(v) for v in z],
            'OLS_design_columns': ['intercept', 'industry_B', 'ln(market_cap)'],
            'OLS_beta': [dstr(v) for v in beta],
            'momentum_final': [dstr(v) for v in residual],
            'reversal_final': [dstr(v) for v in reversal],
            'expected_top1': {
                'momentum': f'SYN_A:{max(range(1, 7), key=lambda a: residual[a - 1]):03d}',
                'reversal': f'SYN_A:{max(range(1, 7), key=lambda a: reversal[a - 1]):03d}',
            },
            'statistics': {},
        }
        for factor, scores in (('momentum', residual), ('reversal', reversal)):
            ic, rank_ic = corr(scores, lab), corr(ranks(scores), ranks(lab))
            series[factor]['pearson'].append(ic)
            series[factor]['spearman'].append(rank_ic)
            r = ranks(scores)
            bins = [min(2, int((v - 1) * D(3) / 6)) for v in r]
            groups = [mean([v for v, b in zip(lab, bins) if b == g]) for g in range(3)]
            record['statistics'][factor] = {
                'pearson_ic': dstr(ic),
                'spearman_rank_ic': dstr(rank_ic),
                'group_counts': [bins.count(g) for g in range(3)],
                'group_mean_returns': [dstr(v) for v in groups],
                'top_minus_bottom': dstr(groups[2] - groups[0]),
                'n': 6,
            }
        sections.append(record)
    summaries = {}
    for factor, stats in series.items():
        summaries[factor] = {}
        for name, values in stats.items():
            m = mean(values)
            sd = (sum((v - m) ** 2 for v in values) / D(len(values) - 1)).sqrt()
            summaries[factor][name] = {
                'n': len(values), 'mean': dstr(m), 'sample_std_ddof1': dstr(sd),
                'unannualized_icir': dstr(m / sd),
                'positive_fraction': dstr(D(sum(v > 0 for v in values)) / len(values)),
            }
    doc = {
        'scope': 'DEVELOPER DESIGN REFERENCE ONLY; no AQRP imports, independent audit or P7 product execution claim',
        'method': 'Public integer input formula -> Fraction returns/labels -> Decimal80 linear quantiles/sample-z -> Gauss-Jordan OLS [1,industry_B,ln(cap)] -> IC/rank/group formulas',
        'precision': 80,
        'tolerance': {'abs': 1e-12, 'rel': 1e-10, 'note': 'Stricter old Golden applies; do not compare singular values from different solvers'},
        'inputs': {'assets': [f'SYN_A:{a:03d}' for a in range(1, 7)], 'market_caps': caps, 'industry': ['A', 'B', 'A', 'B', 'A', 'B'], 'lookback': 2, 'direction': 1, 'horizon': 1, 'neutralize': True, 'quantiles': ['0.05', '0.95'], 'sessions': 24, 'decision_indices': [2, 20]},
        'section_count': len(sections),
        'developer_reference_checks': checks,
        'sections': sections,
        'IC_summaries': summaries,
        'not_verified': 'Actual input bytes/lineage, OOS/purge/HAC/multiplicity behavior, financial run, product tests, independent audit and real isolation are NOT verified by this reference',
    }
    destination = out / 'MAIN_PIPELINE_CANDIDATES.json'
    assert not destination.exists(), 'Preserve previous output; do not overwrite reference evidence'
    destination.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps({'sections': len(sections), 'reference_checks': checks, 'Jan6_top1': sections[2]['expected_top1'], 'IC_means': {f: v['pearson']['mean'] for f, v in summaries.items()}}, ensure_ascii=False))
```
