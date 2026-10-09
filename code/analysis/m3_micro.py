"""Module 3 (microdata part): who the defendant is — counsel type and Indigenous-division cases; plus trial-stage
detention: how much the chance of release on bail depends on the judge.

m3_micro.py MICRO_ROOT DATA_DIR OUT_JSON
"""
import os, re, sys, glob, json, math
from multiprocessing import Pool
import numpy as np, pandas as pd

ROOT, D_DIR, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
CTRL = ['rec', 'attempt_i', 'acc_i', 'm_self', 'm_confess', 'm_59', 'm_mental', 'm_minor', 'a_any', 'a_rec', 'simplified', 'dv_i']

def dec(b):
    try:
        return b.decode('utf-8')
    except UnicodeDecodeError:
        return b.decode('cp950', errors='replace')

GRANT = re.compile(r'准許|具保|責付|限制住居|停止羈押|撤銷羈押')
def parse_bail(path):
    code = re.search(r'\.([A-Z]{3})M\.刑事其他\.txt$', path)
    if not code or not code.group(1).endswith('D'):
        return []
    rows = []
    for rec in dec(open(path, 'rb').read()).split('#'):
        rec = rec.strip()
        if not rec.startswith('0!'):
            continue
        c = rec.split('\n', 1)[0].split('!')
        if len(c) < 17 or '停止羈押' not in c[5] or '偵' in c[3]:
            continue
        out = c[16]
        if '撤回' in out or out in ('', '其他'):
            continue
        g = 1 if ('部分准許' in out or (GRANT.search(out) and '駁回' not in out)) else 0
        rows.append({'court': c[1], 'jyear': c[2], 'jcase': c[3], 'jno': c[4], 'cause': c[5], 'judge1': c[6].strip(), 'judge2': c[7].strip(),
                     'y': c[13], 'm': c[14], 'outcome': out, 'grant': g, 'tag': os.path.basename(path).split('.')[0]})
    return rows

def design(d, extra=()):
    X = d[CTRL + list(extra)].astype(float).copy()
    return pd.concat([X, pd.get_dummies(d['art'].astype(str) + '-' + d['art_sub'].fillna(0).astype(int).astype(str) + '-' + d['para'].fillna(0).astype(int).astype(str),
                                        prefix='s', drop_first=True, dtype=float)], axis=1)

def within_coef(d, y, cols, pool):
    """Coefficients on `cols` with pool fixed effects and legal controls; judge-clustered SEs."""
    X = design(d, cols)
    Xd = X - X.groupby(d[pool]).transform('mean')
    keep = [c for c in Xd.columns if Xd[c].abs().sum() > 0]
    Xm = Xd[keep].to_numpy()
    yd = (d[y] - d.groupby(pool)[y].transform('mean')).to_numpy()
    XtX_inv = np.linalg.pinv(Xm.T @ Xm)
    b = XtX_inv @ Xm.T @ yd
    e = yd - Xm @ b
    S = pd.DataFrame(Xm * e[:, None]).groupby(d['judge_key'].to_numpy()).sum().to_numpy()
    V = XtX_inv @ (S.T @ S) @ XtX_inv
    return {c: (float(b[keep.index(c)]), float(math.sqrt(V[keep.index(c), keep.index(c)]))) for c in cols if c in keep}

if __name__ == '__main__':
    R = {}
    F = pd.read_parquet(os.path.join(D_DIR, 'frame.parquet'))
    F['log_days'] = np.where(F['sentence_days'] > 0, np.log(F['sentence_days'].clip(lower=1)), np.nan)
    for c in ('legal aid', 'public defender', 'retained', 'appointed'):
        F['cn_' + c] = (F['counsel'] == c).astype(float)
    F['pool2'] = F['court'] + '|' + F['jcase'].str.replace('原', '', regex=False) + '|' + F['year'].astype(str)
    F['ind'] = F['indigenous'].astype(float)
    R['counsel'], R['indigenous'] = [], []
    for off in ['Impaired driving', 'Theft', 'Drug use', 'Fraud', 'Assault', 'Negligent injury', 'Money-mule (aiding laundering)', 'Money-mule (aiding fraud)']:
        base = F[F['offence'] == off]
        for y in ('log_days', 'prob', 'convicted'):
            d = base[base['decided']] if y == 'convicted' else base[base[y].notna()]
            if len(d) < 2000:
                continue
            co = within_coef(d, y, ['cn_legal aid', 'cn_public defender', 'cn_retained', 'cn_appointed'], 'pool')
            share = d['counsel'].value_counts(normalize=True).to_dict()
            R['counsel'].append({'offence': off, 'outcome': y, 'n': int(len(d)), 'share': share,
                                 'coef': {k[3:]: v for k, v in co.items()}})
            ci = within_coef(d, y, ['ind'], 'pool2')
            if 'ind' in ci and d['ind'].sum() >= 200:
                R['indigenous'].append({'offence': off, 'outcome': y, 'n': int(len(d)), 'n_ind': int(d['ind'].sum()), 'coef': ci['ind']})
        print(off, [r for r in R['counsel'] if r['offence'] == off][:1], [r for r in R['indigenous'] if r['offence'] == off], flush=True)

    # judge-dependence of the Indigenous gap (impaired driving, prison length): judges deciding both kinds of case
    d = F[(F['offence'] == 'Impaired driving') & F['log_days'].notna()].copy()
    X = design(d)
    Xd = X - X.groupby(d['pool2']).transform('mean')
    keep = Xd.columns[Xd.abs().sum() > 0]
    yd = d['log_days'] - d.groupby('pool2')['log_days'].transform('mean')
    b, *_ = np.linalg.lstsq(Xd[keep].to_numpy(), yd.to_numpy(), rcond=None)
    d['e'] = yd.to_numpy() - Xd[keep].to_numpy() @ b
    g = d.groupby(['judge_key', 'ind'])['e'].agg(['mean', 'var', 'count']).unstack()
    g = g[(g[('count', 0.0)] >= 20) & (g[('count', 1.0)] >= 20)]
    gap = g[('mean', 1.0)] - g[('mean', 0.0)]
    sv = g[('var', 1.0)] / g[('count', 1.0)] + g[('var', 0.0)] / g[('count', 0.0)]
    tau2 = max(gap.var(ddof=1) - sv.mean(), 0)
    R['indigenous_judge'] = {'judges': int(len(g)), 'mean_gap_pct': float(100 * (math.exp(gap.mean()) - 1)), 'sd_gap_pct': float(100 * math.sqrt(tau2)),
                             'gaps': [{'gap': float(100 * (math.exp(v) - 1)), 'se': float(100 * math.sqrt(s))} for v, s in zip(gap, sv)]}
    print('indigenous judge gap', {k: v for k, v in R['indigenous_judge'].items() if k != 'gaps'}, flush=True)

    # bail-release motions during trial
    files = sorted(glob.glob(os.path.join(ROOT, 'dl_*', '**', '*M.刑事其他.txt'), recursive=True))
    rows = []
    with Pool(4) as p:
        for r in p.imap_unordered(parse_bail, files, chunksize=20):
            rows += r
    B = pd.DataFrame(rows).sort_values('tag').drop_duplicates(['court', 'jyear', 'jcase', 'jno'], keep='last')
    B['year'] = pd.to_numeric(B['y'], errors='coerce') + 1911
    B = B[B['year'].between(2013, 2026) & B['judge1'].str.len().between(2, 4)]
    B['single'] = B['judge2'] == ''
    _fx = os.path.join(D_DIR, 'name_fix.json')
    if os.path.exists(_fx):
        _m = {k: v for k, v in json.load(open(_fx, encoding='utf-8')).items() if v}
        B['judge1'] = (B['court'] + '|' + B['judge1']).map(_m).fillna(B['judge1'])
    B['judge_key'] = B['court'] + ':' + B['judge1']
    B['pool'] = B['court'] + '|' + B['year'].astype(int).astype(str)
    R['bail'] = {'n': int(len(B)), 'grant_rate': float(B['grant'].mean()), 'by_year': B.groupby('year')['grant'].agg(['mean', 'size']).reset_index().to_dict('records'),
                 'outcomes': B['outcome'].value_counts().head(12).to_dict()}
    for lab, d in (('all', B), ('single', B[B['single']])):
        d = d[d.groupby('pool')['judge_key'].transform('nunique') >= 2]
        e = d['grant'] - d.groupby('pool')['grant'].transform('mean')
        st = pd.DataFrame({'j': d['judge_key'], 'e': e}).groupby('j')['e'].agg(['mean', 'count', 'var'])
        st = st[st['count'] >= 2]
        N, J = st['count'].sum(), len(st)
        s2 = ((st['count'] - 1) * st['var']).sum() / (N - J)
        mbar = np.average(st['mean'], weights=st['count'])
        n0 = (N - (st['count'] ** 2).sum() / N) / (J - 1)
        t2 = max((((st['count'] * (st['mean'] - mbar) ** 2).sum()) / (J - 1) - s2) / n0, 0.0)
        # permutation within pool
        perm = []
        rng = np.random.default_rng(3)
        for k in range(200):
            jp = d.groupby('pool')['judge_key'].transform(lambda s: s.sample(frac=1, random_state=int(rng.integers(1e9))).to_numpy())
            sp = pd.DataFrame({'j': jp.to_numpy(), 'e': e.to_numpy()}).groupby('j')['e'].agg(['mean', 'count'])
            sp = sp[sp['count'] >= 2]
            perm.append(float((sp['count'] * (sp['mean'] - mbar) ** 2).sum()))
        obs = float((st['count'] * (st['mean'] - mbar) ** 2).sum())
        st['eb'] = (st['mean'] - mbar) * (t2 / (t2 + s2 / st['count']) if t2 > 0 else 0)
        big = st[st['count'] >= 30]
        R['bail'][lab] = {'n': int(N), 'judges': int(J), 'tau_pp': 100 * math.sqrt(t2), 'icc': t2 / (t2 + s2),
                          'perm_ratio': obs / np.mean(perm), 'perm_p': float(np.mean([v >= obs for v in perm])),
                          'p10': float(100 * (big['eb'].quantile(.1))), 'p90': float(100 * (big['eb'].quantile(.9))),
                          'p10_raw': float(100 * (big['mean'].quantile(.1))), 'p90_raw': float(100 * (big['mean'].quantile(.9))), 'judges_30': int(len(big)),
                          'share_panel': float((d['judge2'] != '').mean())}
        print('bail', lab, R['bail'][lab], flush=True)
    json.dump(R, open(OUT, 'w'), ensure_ascii=False, default=float)
    print('wrote', OUT)
