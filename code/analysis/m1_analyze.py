"""Module 1: how much do outcomes depend on the assigned judge, by offence and year (2013–2026)?

m1_analyze.py DATA_DIR OUT_JSON
Method: within assignment pools (court x case type x quarter) residualise each outcome on the legally relevant
controls carried by the microdata; estimate the noise-corrected between-judge variance (ANOVA estimator), the
judge share, the expected gap between two randomly drawn judges, split-half reliability and shrunken (empirical
Bayes) judge effects with intervals and rank ranges.
"""
import sys, os, json, math
import numpy as np, pandas as pd

D_DIR, OUT = sys.argv[1], sys.argv[2]
F = pd.read_parquet(os.path.join(D_DIR, 'frame.parquet'))
rng = np.random.default_rng(20261009)
CTRL = ['rec', 'attempt_i', 'acc_i', 'm_self', 'm_confess', 'm_59', 'm_mental', 'm_minor', 'a_any', 'a_rec', 'simplified', 'indigenous', 'dv_i']
OFFENCES = ['Impaired driving', 'Theft', 'Drug use', 'Negligent injury', 'Fraud', 'Assault', 'Money-mule (aiding laundering)',
            'Money-mule (aiding fraud)', 'Drug possession', 'Defamation / insult', 'Criminal damage', 'Money laundering']
OUTCOMES = {'sentence_days': 'Prison/detention length (days)', 'prob': 'Probation granted', 'extra_fine': 'Extra fine with prison',
            'convicted': 'Convicted (vs acquitted)'}
# offences covered by the Judicial Yuan sentencing-trend guidance (2018-12-21) and the AI sentencing system (2023-02-06)
GUIDED = {'Impaired driving', 'Theft', 'Drug use', 'Drug possession', 'Fraud', 'Assault'}

def design(d):
    X = d[CTRL].astype(float).copy()
    X = pd.concat([X, pd.get_dummies(d['counsel'], prefix='c', drop_first=True, dtype=float),
                   pd.get_dummies(d['art'].astype(str) + '-' + d['art_sub'].fillna(0).astype(int).astype(str) + '-' + d['para'].fillna(0).astype(int).astype(str),
                                  prefix='s', drop_first=True, dtype=float)], axis=1)
    return X

def residualise(d, y, drop=()):
    """Within-pool demeaning (pool fixed effects) + OLS on controls; returns residuals."""
    X = design(d).drop(columns=list(drop), errors='ignore')
    g = d['pool']
    yd = d[y] - d.groupby('pool')[y].transform('mean')
    Xd = X - X.groupby(g).transform('mean')
    keep = Xd.columns[Xd.abs().sum() > 0]
    beta, *_ = np.linalg.lstsq(Xd[keep].to_numpy(), yd.to_numpy(), rcond=None)
    return yd - Xd[keep].to_numpy() @ beta

def components(d, resid):
    """Noise-corrected between-judge variance (ANOVA estimator) on residuals."""
    g = pd.DataFrame({'j': d['judge_key'].to_numpy(), 'e': resid.to_numpy()})
    st = g.groupby('j')['e'].agg(['mean', 'count', 'var'])
    st = st[st['count'] >= 2]
    N = st['count'].sum(); J = len(st)
    if J < 5:
        return None
    sigma2 = float(((st['count'] - 1) * st['var']).sum() / (N - J))
    mbar = np.average(st['mean'], weights=st['count'])
    ssb = float((st['count'] * (st['mean'] - mbar) ** 2).sum())
    n0 = (N - (st['count'] ** 2).sum() / N) / (J - 1)
    tau2 = max((ssb / (J - 1) - sigma2) / n0, 0.0)
    shrink = tau2 / (tau2 + sigma2 / st['count']) if tau2 > 0 else st['count'] * 0
    st['eb'] = (st['mean'] - mbar) * shrink
    st['post_sd'] = np.sqrt(1 / (1 / tau2 + st['count'] / sigma2)) if tau2 > 0 else np.sqrt(sigma2 / st['count'])
    return {'tau': math.sqrt(tau2), 'sigma': math.sqrt(sigma2), 'icc': tau2 / (tau2 + sigma2) if tau2 + sigma2 > 0 else 0,
            'J': J, 'N': int(N), 'st': st}

def split_half(d, resid, min_n=40, reps=20):
    g = pd.DataFrame({'j': d['judge_key'].to_numpy(), 'e': resid.to_numpy()})
    big = g['j'].map(g['j'].value_counts()) >= min_n
    g = g[big]
    if g['j'].nunique() < 10:
        return None
    rs = []
    for k in range(reps):
        h = rng.integers(0, 2, len(g))
        m = g.assign(h=h).groupby(['j', 'h'])['e'].mean().unstack().dropna()
        rs.append(np.corrcoef(m[0], m[1])[0, 1])
    return float(np.mean(rs))

def keep_multi_judge_pools(d):
    pj = d.groupby('pool')['judge_key'].transform('nunique')
    return d[pj >= 2]

R = {'offences': {}, 'yearly': [], 'judges': {}}
for off in OFFENCES:
    base = F[F['offence'] == off]
    R['offences'][off] = {'n_all': int(len(base)), 'judges_all': int(base['judge_key'].nunique()), 'guided': off in GUIDED, 'outcomes': {}}
    for y, label in OUTCOMES.items():
        if y == 'convicted':
            d = base[base['decided']]
        else:
            d = base[base[y].notna()]
        d = keep_multi_judge_pools(d)
        if len(d) < 500 or d[y].std() == 0:
            continue
        resid = residualise(d, y)
        c = components(d, resid)
        if c is None:
            continue
        sh = split_half(d, resid)
        st = c['st']
        big = st[st['count'] >= 50]
        scale = 1.0 if y == 'sentence_days' else 100.0     # binary outcomes in percentage points
        out = {'label': label, 'n': c['N'], 'judges': c['J'], 'mean': float(d[y].mean()) * scale,
               'tau': c['tau'] * scale, 'icc': c['icc'], 'two_judge_gap': 2 * c['tau'] / math.sqrt(math.pi) * scale,
               'p10': float(big['eb'].quantile(.1)) * scale if len(big) >= 10 else None,
               'p90': float(big['eb'].quantile(.9)) * scale if len(big) >= 10 else None,
               'split_half': sh, 'n_judges_50': int(len(big))}
        if y == 'sentence_days':      # robustness: drop controls that are themselves judge decisions
            c2 = components(d, residualise(d, y, drop=('m_59', 'simplified', 'm_minor')))
            out['tau_nodisc'] = c2['tau'] if c2 else None; out['icc_nodisc'] = c2['icc'] if c2 else None
        R['offences'][off]['outcomes'][y] = out
        print(off, '|', y, '| n', c['N'], 'J', c['J'], '| tau', round(out['tau'], 2), 'icc', round(c['icc'], 3), 'split', None if sh is None else round(sh, 2), flush=True)
        # judge-level table (named), for prison length and probation only
        if y in ('sentence_days', 'prob') and c['tau'] > 0:
            t = st[st['count'] >= (100 if y == 'sentence_days' else 100)].copy()
            t['court'] = [k.split(':')[0] for k in t.index]
            t['judge'] = [k.split(':', 1)[1] for k in t.index]
            # rank range within court via posterior draws
            rows = []
            for court, tc in t.groupby('court'):
                if len(tc) < 3:
                    continue
                draws = rng.normal(tc['eb'].to_numpy()[:, None], tc['post_sd'].to_numpy()[:, None], size=(len(tc), 1000))
                ranks = (draws.argsort(axis=0).argsort(axis=0) + 1) / len(tc)          # 1/len = most lenient
                for i, (k, r) in enumerate(tc.iterrows()):
                    lo, hi = np.quantile(ranks[i], [.05, .95])
                    rows.append({'court': court, 'judge': r['judge'], 'n': int(r['count']), 'effect': float(r['eb']) * scale,
                                 'lo': float(r['eb'] - 1.96 * r['post_sd']) * scale, 'hi': float(r['eb'] + 1.96 * r['post_sd']) * scale,
                                 'pct_lo': float(lo), 'pct_hi': float(hi), 'judges_in_court': int(len(tc))})
            R['judges'].setdefault(off, {})[y] = rows
    # yearly series (prison length and probation)
    for yr, dy in base.groupby('year'):
        for y in ('sentence_days', 'prob'):
            d = keep_multi_judge_pools(dy[dy[y].notna()])
            if len(d) < 300:
                continue
            resid = residualise(d, y)
            c = components(d, resid)
            if c is None:
                continue
            scale = 1.0 if y == 'sentence_days' else 100.0
            R['yearly'].append({'offence': off, 'year': int(yr), 'outcome': y, 'n': c['N'], 'judges': c['J'], 'tau': c['tau'] * scale,
                                'icc': c['icc'], 'mean': float(d[y].mean()) * scale, 'guided': off in GUIDED})

def clean(o):
    if isinstance(o, dict): return {str(k): clean(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)): return [clean(v) for v in o]
    if isinstance(o, (np.integer,)): return int(o)
    if isinstance(o, (np.floating, float)): return None if math.isnan(o) or math.isinf(o) else float(o)
    if isinstance(o, (np.bool_,)): return bool(o)
    return o
json.dump(clean(R), open(OUT, 'w'), ensure_ascii=False)
print('wrote', OUT)
