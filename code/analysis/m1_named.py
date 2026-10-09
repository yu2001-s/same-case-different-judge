"""Named judge table (recent cases): how each judge's outcomes compare with other judges of the same court deciding
comparable cases in the same assignment pools.

m1_named.py DATA_DIR OUT_JSON [START_DATE] [MIN_CASES]
Safeguards: only judges with at least MIN_CASES cases in the window; effects are empirical-Bayes (shrunk toward the
court average, so small samples cannot produce extreme values); every effect has a 95% interval and a 90% interval
for the judge's rank among the court's judges; a judge is flagged only when the whole 95% interval lies on one side
of zero AND the rank interval lies entirely in the top or bottom fifth of the court.
"""
import sys, os, json, math
import numpy as np, pandas as pd

D_DIR, OUT = sys.argv[1], sys.argv[2]
START = sys.argv[3] if len(sys.argv) > 3 else '2022-01-01'
MIN_N = int(sys.argv[4]) if len(sys.argv) > 4 else 100
rng = np.random.default_rng(2026)
F = pd.read_parquet(os.path.join(D_DIR, 'frame.parquet'))
F = F[F['date'] >= START]
CTRL = ['rec', 'attempt_i', 'acc_i', 'm_self', 'm_confess', 'm_59', 'm_mental', 'm_minor', 'a_any', 'a_rec', 'simplified', 'indigenous', 'dv_i']
JOBS = [('Impaired driving', 'sentence_days'), ('Impaired driving', 'prob'), ('Impaired driving', 'extra_fine'),
        ('Theft', 'sentence_days'), ('Drug use', 'sentence_days'), ('Fraud', 'sentence_days'), ('Fraud', 'extra_fine'),
        ('Money-mule (aiding laundering)', 'sentence_days'), ('Money-mule (aiding laundering)', 'prob'), ('Negligent injury', 'sentence_days')]

def design(d):
    X = d[CTRL].astype(float).copy()
    return pd.concat([X, pd.get_dummies(d['counsel'], prefix='c', drop_first=True, dtype=float),
                      pd.get_dummies(d['art'].astype(str) + '-' + d['art_sub'].fillna(0).astype(int).astype(str) + '-' + d['para'].fillna(0).astype(int).astype(str),
                                     prefix='s', drop_first=True, dtype=float)], axis=1)

rows, meta = [], []
for off, y in JOBS:
    d = F[(F['offence'] == off) & F[y].notna()]
    d = d[d.groupby('pool')['judge_key'].transform('nunique') >= 2]
    X = design(d)
    Xd = X - X.groupby(d['pool']).transform('mean')
    keep = Xd.columns[Xd.abs().sum() > 0]
    yd = d[y] - d.groupby('pool')[y].transform('mean')
    b, *_ = np.linalg.lstsq(Xd[keep].to_numpy(), yd.to_numpy(), rcond=None)
    e = yd.to_numpy() - Xd[keep].to_numpy() @ b
    st = pd.DataFrame({'j': d['judge_key'].to_numpy(), 'e': e}).groupby('j')['e'].agg(['mean', 'count', 'var'])
    st = st[st['count'] >= 2]
    N, J = st['count'].sum(), len(st)
    s2 = ((st['count'] - 1) * st['var']).sum() / (N - J)
    mbar = np.average(st['mean'], weights=st['count'])
    n0 = (N - (st['count'] ** 2).sum() / N) / (J - 1)
    t2 = max((((st['count'] * (st['mean'] - mbar) ** 2).sum()) / (J - 1) - s2) / n0, 1e-12)
    st['eb'] = (st['mean'] - mbar) * t2 / (t2 + s2 / st['count'])
    st['psd'] = np.sqrt(1 / (1 / t2 + st['count'] / s2))
    scale = 1.0 if y == 'sentence_days' else 100.0
    base = float(d[y].mean()) * scale
    t = st[st['count'] >= MIN_N].copy()
    t['court'] = [k.split(':')[0] for k in t.index]; t['judge'] = [k.split(':', 1)[1] for k in t.index]
    t = t[[all('\u4e00' <= ch <= '\u9fff' or ord(ch) >= 0x20000 for ch in n) and 2 <= len(n) <= 4 for n in t['judge']]]     # drop the few names still unreadable
    for court, tc in t.groupby('court'):
        if len(tc) < 3:
            continue
        draws = rng.normal(tc['eb'].to_numpy()[:, None], tc['psd'].to_numpy()[:, None], size=(len(tc), 2000))
        pr = (draws.argsort(axis=0).argsort(axis=0) + 0.5) / len(tc)      # 0 = lowest outcome in court
        for i, (k, r) in enumerate(tc.iterrows()):
            lo, hi = np.quantile(pr[i], [.05, .95])
            elo, ehi = r['eb'] - 1.96 * r['psd'], r['eb'] + 1.96 * r['psd']
            flag = 'higher' if (elo > 0 and lo >= 0.8) else ('lower' if (ehi < 0 and hi <= 0.2) else '')
            if len(tc) < 5:              # with fewer than five listed judges a top/bottom-fifth rank is not meaningful
                flag = ''
            rows.append({'offence': off, 'outcome': y, 'court': court, 'judge': r['judge'], 'n': int(r['count']),
                         'effect': round(float(r['eb']) * scale, 2), 'lo': round(float(elo) * scale, 2), 'hi': round(float(ehi) * scale, 2),
                         'rank_lo': round(float(lo), 3), 'rank_hi': round(float(hi), 3), 'judges_in_court': int(len(tc)), 'flag': flag})
    sub = [r for r in rows if r['offence'] == off and r['outcome'] == y]
    meta.append({'offence': off, 'outcome': y, 'mean': base, 'tau': math.sqrt(t2) * scale, 'judges_listed': len(sub),
                 'flag_higher': sum(r['flag'] == 'higher' for r in sub), 'flag_lower': sum(r['flag'] == 'lower' for r in sub), 'cases': int(N)})
    print(meta[-1], flush=True)
json.dump({'window_start': START, 'min_cases': MIN_N, 'meta': meta, 'rows': rows}, open(OUT, 'w'), ensure_ascii=False, separators=(',', ':'))
print('rows', len(rows))
