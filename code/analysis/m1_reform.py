"""Module 1 reforms: did judge-to-judge disparity fall where the Judicial Yuan introduced sentencing tools?

m1_reform.py DATA_DIR OUT_JSON
Reform 1 (2018-12-21, sentencing-trend guidance): covers impaired driving, fraud, theft (also sexual offences,
robbery, homicide, guns, which are too rare for single-judge analysis here).
Reform 2 (2023-02-06, AI sentencing information system): impaired driving, fraud, theft, assault (fact mode) and
drug offences (evaluation mode).
Disparity = noise-corrected between-judge SD of log prison length (so it reads as a proportional gap and is not
mechanically driven by rising average sentences), and of the probation rate, per offence x year, estimated within
assignment pools exactly as in m1_analyze.py. The difference-in-differences compares covered vs uncovered offences
before vs after each reform, with offence and year fixed effects, weighted by cases; inference by randomisation over
which offences are labelled 'covered' (exact enumeration).
"""
import sys, os, json, math, itertools
import numpy as np, pandas as pd

D_DIR, OUT = sys.argv[1], sys.argv[2]
F = pd.read_parquet(os.path.join(D_DIR, 'frame.parquet'))
F['log_days'] = np.where(F['sentence_days'] > 0, np.log(F['sentence_days'].clip(lower=1)), np.nan)
CTRL = ['rec', 'attempt_i', 'acc_i', 'm_self', 'm_confess', 'm_59', 'm_mental', 'm_minor', 'a_any', 'a_rec', 'simplified', 'indigenous', 'dv_i']
OFFS = ['Impaired driving', 'Theft', 'Fraud', 'Assault', 'Drug use', 'Drug possession', 'Negligent injury', 'Criminal damage',
        'Defamation / insult', 'Money laundering', 'Money-mule (aiding laundering)', 'Money-mule (aiding fraud)']
R1 = {'Impaired driving', 'Fraud', 'Theft'}
R2 = {'Impaired driving', 'Fraud', 'Theft', 'Assault', 'Drug use', 'Drug possession'}

def design(d):
    X = d[CTRL].astype(float).copy()
    X = pd.concat([X, pd.get_dummies(d['counsel'], prefix='c', drop_first=True, dtype=float),
                   pd.get_dummies(d['art'].astype(str) + '-' + d['art_sub'].fillna(0).astype(int).astype(str) + '-' + d['para'].fillna(0).astype(int).astype(str),
                                  prefix='s', drop_first=True, dtype=float)], axis=1)
    return X

def tau(d, y):
    d = d[d.groupby('pool')['judge_key'].transform('nunique') >= 2]
    if len(d) < 300:
        return None
    X = design(d)
    yd = d[y] - d.groupby('pool')[y].transform('mean')
    Xd = X - X.groupby(d['pool']).transform('mean')
    keep = Xd.columns[Xd.abs().sum() > 0]
    beta, *_ = np.linalg.lstsq(Xd[keep].to_numpy(), yd.to_numpy(), rcond=None)
    e = yd - Xd[keep].to_numpy() @ beta
    st = pd.DataFrame({'j': d['judge_key'].to_numpy(), 'e': e.to_numpy()}).groupby('j')['e'].agg(['mean', 'count', 'var'])
    st = st[st['count'] >= 2]
    N, J = st['count'].sum(), len(st)
    if J < 5:
        return None
    s2 = ((st['count'] - 1) * st['var']).sum() / (N - J)
    mbar = np.average(st['mean'], weights=st['count'])
    n0 = (N - (st['count'] ** 2).sum() / N) / (J - 1)
    t2 = max((((st['count'] * (st['mean'] - mbar) ** 2).sum()) / (J - 1) - s2) / n0, 0.0)
    return {'tau': math.sqrt(t2), 'icc': t2 / (t2 + s2), 'n': int(N), 'J': int(J)}

rows = []
for off in OFFS:
    for yr, dy in F[F['offence'] == off].groupby('year'):
        for y, scale in (('log_days', 100.0), ('prob', 100.0)):
            r = tau(dy[dy[y].notna()], y)
            if r:
                rows.append({'offence': off, 'year': int(yr), 'outcome': y, 'tau': r['tau'] * scale, 'icc': r['icc'], 'n': r['n'], 'J': r['J']})
T = pd.DataFrame(rows)
T = T[T['year'] <= 2025]          # 2026 is a partial year

def did(T, y, covered, pre, post, offs):
    d = T[(T['outcome'] == y) & T['offence'].isin(offs) & T['year'].between(pre[0], post[1])].copy()
    d = d[~d['year'].between(pre[1] + 1, post[0] - 1)]
    d['post'] = (d['year'] >= post[0]).astype(float)
    def est(cov):
        g = d['offence'].isin(cov).astype(float)
        X = pd.concat([pd.get_dummies(d['offence'], dtype=float), pd.get_dummies(d['year'], prefix='y', drop_first=True, dtype=float)], axis=1)
        X['tp'] = g * d['post']
        w = np.sqrt(d['n'].to_numpy())
        b, *_ = np.linalg.lstsq(X.to_numpy() * w[:, None], np.log(d['tau'].clip(lower=0.5)).to_numpy() * w, rcond=None)
        return float(b[-1])
    b = est(covered)
    k = len(covered & set(offs))
    perms = [est(set(c)) for c in itertools.combinations(sorted(set(offs)), k)]
    p = float(np.mean([abs(v) >= abs(b) - 1e-12 for v in perms]))
    pre_c = d[(d['post'] == 0) & d['offence'].isin(covered)]
    post_c = d[(d['post'] == 1) & d['offence'].isin(covered)]
    pre_u = d[(d['post'] == 0) & ~d['offence'].isin(covered)]
    post_u = d[(d['post'] == 1) & ~d['offence'].isin(covered)]
    wm = lambda x: float(np.average(x['tau'], weights=x['n'])) if len(x) else None
    return {'outcome': y, 'pre': pre, 'post': post, 'covered': sorted(covered & set(offs)), 'uncovered': sorted(set(offs) - covered),
            'did_log': b, 'did_pct': (math.exp(b) - 1) * 100, 'p_perm': p, 'n_perm': len(perms),
            'covered_pre': wm(pre_c), 'covered_post': wm(post_c), 'uncovered_pre': wm(pre_u), 'uncovered_post': wm(post_u)}

offs1 = [o for o in OFFS if o != 'Money-mule (aiding fraud)']           # fraud-adjacent: ambiguous coverage, dropped
res = {'series': T.to_dict('records'), 'did': []}
for y in ('log_days', 'prob'):
    res['did'].append(dict(did(T, y, R1, (2015, 2018), (2019, 2022), offs1), reform='2018 sentencing-trend guidance'))
    res['did'].append(dict(did(T, y, R2, (2019, 2022), (2023, 2025), offs1), reform='2023 AI sentencing information system'))
for r in res['did']:
    print(r['reform'], r['outcome'], 'DiD %+.1f%%' % r['did_pct'], 'p=%.2f' % r['p_perm'], 'cov %.1f->%.1f unc %.1f->%.1f' % (
        r['covered_pre'], r['covered_post'], r['uncovered_pre'], r['uncovered_post']))
piv = T[T['outcome'] == 'log_days'].pivot(index='year', columns='offence', values='tau').round(1)
print(piv.to_string())
json.dump(res, open(OUT, 'w'), ensure_ascii=False)

# robustness: drop one covered offence at a time (each has its own concurrent law changes)
res['loo'] = []
for name, cov, pre, post in (('2018 sentencing-trend guidance', R1, (2015, 2018), (2019, 2022)),
                             ('2023 AI sentencing information system', R2, (2019, 2022), (2023, 2025))):
    for drop in sorted(cov):
        offs = [o for o in offs1 if o != drop]
        r = did(T, 'log_days', cov - {drop}, pre, post, offs)
        res['loo'].append({'reform': name, 'dropped': drop, 'did_pct': r['did_pct'], 'p_perm': r['p_perm']})
        print(name, 'drop', drop, 'DiD %+.1f%%' % r['did_pct'], 'p=%.2f' % r['p_perm'])
json.dump(res, open(OUT, 'w'), ensure_ascii=False)
