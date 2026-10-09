"""Module 2: who the judge is — experience, stability of a judge's style, and whether it travels between courts.

m2_judges.py DATA_DIR OUT_JSON
Uses frame.parquet (single-judge first-instance cases) and judge_panel.parquet (all appearances in all case types).
Each case's outcome is residualised within its assignment pool on legal controls (as in m1_analyze.py); for
cross-offence comparisons residuals of log prison length are standardised by each offence's residual SD.
"""
import sys, os, json, math
import numpy as np, pandas as pd

D_DIR, OUT = sys.argv[1], sys.argv[2]
F = pd.read_parquet(os.path.join(D_DIR, 'frame.parquet'))
P = pd.read_parquet(os.path.join(D_DIR, 'judge_panel.parquet'))
_fx = os.path.join(D_DIR, 'name_fix.json')
if os.path.exists(_fx):
    _m = {k: v for k, v in json.load(open(_fx, encoding='utf-8')).items() if v}
    P['judge'] = (P['court'] + '|' + P['judge']).map(_m).fillna(P['judge'])
rng = np.random.default_rng(7)
CTRL = ['rec', 'attempt_i', 'acc_i', 'm_self', 'm_confess', 'm_59', 'm_mental', 'm_minor', 'a_any', 'a_rec', 'simplified', 'indigenous', 'dv_i']
OFFS = ['Impaired driving', 'Theft', 'Drug use', 'Fraud', 'Assault', 'Negligent injury', 'Drug possession',
        'Money-mule (aiding fraud)', 'Money-mule (aiding laundering)']

# ---- experience: first year a name decides cases (litigation dockets only, any court)
JUDGING = {'民事訴訟', '刑事訴訟', '家事訴訟', '行政訴訟', '社會秩序維護法'}
first = P[P['kind'].isin(JUDGING) & (P['n'] >= 5)].groupby('judge')['year'].min().rename('first_year')
F['judge'] = F['judge'].astype(str)
F = F.merge(first, left_on='judge', right_index=True, how='left')
F['tenure'] = F['year'] - F['first_year']
F['novice'] = (F['first_year'] >= 2015) & (F['tenure'] <= 2)
F['log_days'] = np.where(F['sentence_days'] > 0, np.log(F['sentence_days'].clip(lower=1)), np.nan)

def design(d):
    X = d[CTRL].astype(float).copy()
    return pd.concat([X, pd.get_dummies(d['counsel'], prefix='c', drop_first=True, dtype=float),
                      pd.get_dummies(d['art'].astype(str) + '-' + d['art_sub'].fillna(0).astype(int).astype(str) + '-' + d['para'].fillna(0).astype(int).astype(str),
                                     prefix='s', drop_first=True, dtype=float)], axis=1)

def residualise(d, y):
    X = design(d)
    yd = d[y] - d.groupby('pool')[y].transform('mean')
    Xd = X - X.groupby(d['pool']).transform('mean')
    keep = Xd.columns[Xd.abs().sum() > 0]
    b, *_ = np.linalg.lstsq(Xd[keep].to_numpy(), yd.to_numpy(), rcond=None)
    return pd.Series(yd.to_numpy() - Xd[keep].to_numpy() @ b, index=d.index)

def tau(j, e):
    st = pd.DataFrame({'j': j, 'e': e}).groupby('j')['e'].agg(['mean', 'count', 'var'])
    st = st[st['count'] >= 2]
    N, J = st['count'].sum(), len(st)
    if J < 5:
        return None
    s2 = ((st['count'] - 1) * st['var']).sum() / (N - J)
    mbar = np.average(st['mean'], weights=st['count'])
    n0 = (N - (st['count'] ** 2).sum() / N) / (J - 1)
    return math.sqrt(max((((st['count'] * (st['mean'] - mbar) ** 2).sum()) / (J - 1) - s2) / n0, 0.0))

R = {'experience': [], 'tenure_curve': [], 'persistence': [], 'cross_offence': {}, 'movers': {}}
resid = []
for off in OFFS:
    d = F[(F['offence'] == off) & F['log_days'].notna()]
    d = d[d.groupby('pool')['judge_key'].transform('nunique') >= 2]
    e = residualise(d, 'log_days')
    sd = e.std()
    dd = d[['judge', 'judge_key', 'court', 'year', 'tenure', 'first_year', 'novice', 'pool']].copy()
    dd['e'] = e; dd['z'] = e / sd; dd['offence'] = off
    resid.append(dd)
    # experience: dispersion and level for novice vs experienced judges (pools holding both)
    known = dd[dd['first_year'].notna()]
    nov = known[known['novice']]
    exp = known[(known['tenure'] >= 5)]
    tn, te = tau(nov['judge_key'], nov['e']), tau(exp['judge_key'], exp['e'])
    cmp_ = known[known['novice'] | (known['tenure'] >= 5)]          # novices vs judges with 5+ years only
    both = cmp_[cmp_.groupby('pool')['novice'].transform(lambda s: s.any() and (~s).any())]
    gap = both.groupby('novice')['e'].mean()
    # judge-clustered SE of the level gap
    jm = both.groupby(['judge_key', 'novice'])['e'].agg(['mean', 'count']).reset_index()
    se = math.sqrt(sum(g['mean'].var(ddof=1) / len(g) for _, g in jm.groupby('novice'))) if jm['novice'].nunique() == 2 else None
    R['experience'].append({'offence': off, 'tau_novice_pct': None if tn is None else 100 * tn, 'tau_exp_pct': None if te is None else 100 * te,
                            'n_novice': int(len(nov)), 'n_exp': int(len(exp)), 'judges_novice': int(nov['judge_key'].nunique()),
                            'judges_exp': int(exp['judge_key'].nunique()),
                            'level_gap_pct': 100 * (math.exp(gap.get(True, np.nan) - gap.get(False, np.nan)) - 1) if len(gap) == 2 else None,
                            'level_gap_se_pct': None if se is None else 100 * se})
    print(off, R['experience'][-1], flush=True)
Z = pd.concat(resid)

# tenure curve (pooled over offences, standardised units): mean residual and dispersion by years on the bench
for t, g in Z[(Z['first_year'] >= 2015) & Z['tenure'].between(0, 9)].groupby('tenure'):
    R['tenure_curve'].append({'tenure': int(t), 'mean_z': float(g['z'].mean()), 'se': float(g.groupby('judge_key')['z'].mean().std() / math.sqrt(g['judge_key'].nunique())),
                              'tau_z': tau(g['judge_key'].astype(str) + g['offence'], g['z']), 'n': int(len(g)), 'judges': int(g['judge_key'].nunique())})

def disattenuated_corr(a, b, min_n=30):
    """Correlation of judge means between two samples, corrected for sampling noise via split-half reliabilities."""
    ma = a.groupby('judge_key')['z'].agg(['mean', 'count', 'var'])
    mb = b.groupby('judge_key')['z'].agg(['mean', 'count', 'var'])
    m = ma.join(mb, lsuffix='_a', rsuffix='_b', how='inner')
    m = m[(m['count_a'] >= min_n) & (m['count_b'] >= min_n)]
    if len(m) < 15:
        return None
    r = np.corrcoef(m['mean_a'], m['mean_b'])[0, 1]
    rel = lambda mean, var, cnt: max(1 - (var / cnt).mean() / mean.var(ddof=1), 0.05)
    ra = rel(m['mean_a'], m['var_a'], m['count_a']); rb = rel(m['mean_b'], m['var_b'], m['count_b'])
    return {'r_raw': float(r), 'r_true': float(min(r / math.sqrt(ra * rb), 1.0)), 'rel_a': float(ra), 'rel_b': float(rb), 'judges': int(len(m))}

# persistence: same judge, same court, earlier vs later years
for off in ['Impaired driving', 'Theft', 'Drug use']:
    z = Z[Z['offence'] == off]
    for (p1, p2) in (((2013, 2016), (2017, 2020)), ((2017, 2020), (2021, 2024)), ((2013, 2016), (2021, 2024))):
        r = disattenuated_corr(z[z['year'].between(*p1)], z[z['year'].between(*p2)])
        if r:
            R['persistence'].append(dict(r, offence=off, early=f'{p1[0]}–{p1[1]}', late=f'{p2[0]}–{p2[1]}'))
            print('persist', off, p1, p2, r, flush=True)

# cross-offence: is a judge who is harsh in one offence harsh in another? (same judge, same court)
for a, b in (('Impaired driving', 'Theft'), ('Impaired driving', 'Drug use'), ('Theft', 'Drug use'), ('Theft', 'Fraud'), ('Impaired driving', 'Fraud')):
    r = disattenuated_corr(Z[Z['offence'] == a], Z[Z['offence'] == b])
    if r:
        R['cross_offence'][f'{a} | {b}'] = r
        print('cross', a, b, r, flush=True)

# movers: judges seen in two different courts; is their harshness in court A (relative to A's pools) mirrored in court B?
Z['spell'] = Z['court'] + ':' + Z['judge']
sp = Z.groupby(['judge', 'court'])['year'].agg(['min', 'max', 'count']).reset_index()
pairs = []
for j, g in sp[sp['count'] >= 30].groupby('judge'):
    g = g.sort_values('min')
    for i in range(len(g) - 1):
        a, b = g.iloc[i], g.iloc[i + 1]
        if a['court'] != b['court'] and a['max'] <= b['min'] + 1:
            pairs.append((j, a['court'], b['court']))
pairs = pd.DataFrame(pairs, columns=['judge', 'court_a', 'court_b']).drop_duplicates('judge')
A = Z.merge(pairs, left_on=['judge', 'court'], right_on=['judge', 'court_a'])
B = Z.merge(pairs, left_on=['judge', 'court'], right_on=['judge', 'court_b'])
A['judge_key'] = A['judge']; B['judge_key'] = B['judge']
r = disattenuated_corr(A, B)
R['movers'] = dict(r or {}, pairs=int(len(pairs)))
print('movers', R['movers'], flush=True)
ma = A.groupby('judge')['z'].agg(['mean', 'count']); mb = B.groupby('judge')['z'].agg(['mean', 'count'])
m = ma.join(mb, lsuffix='_a', rsuffix='_b', how='inner')
m = m[(m['count_a'] >= 30) & (m['count_b'] >= 30)]
R['movers_points'] = [{'a': float(x), 'b': float(y)} for x, y in zip(m['mean_a'], m['mean_b'])]

def clean(o):
    if isinstance(o, dict): return {str(k): clean(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)): return [clean(v) for v in o]
    if isinstance(o, (np.integer,)): return int(o)
    if isinstance(o, (np.floating, float)): return None if math.isnan(o) or math.isinf(o) else float(o)
    if isinstance(o, (np.bool_,)): return bool(o)
    return o
json.dump(clean(R), open(OUT, 'w'), ensure_ascii=False)
print('wrote', OUT)
