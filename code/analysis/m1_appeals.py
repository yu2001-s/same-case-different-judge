"""Module 1 appeals: do appeals correct outlier first-instance judges?

m1_appeals.py DATA_DIR OUT_JSON
Links each first-instance case in frame.parquet (single defendant) to its appeal (district appellate division for
summary cases, High Court otherwise) through the appeal's 原審 fields. For each case we know whether it was appealed,
by whom, how the appeal ended and the final sentence. A judge's stringency is the leave-one-out average of
her/his other cases' residual sentence (within assignment pools, after legal controls). We then ask how the appeal
rate, the appeal outcome and the final sentence move with the first-instance judge's stringency.
"""
import sys, os, json, math
import numpy as np, pandas as pd

D_DIR, OUT = sys.argv[1], sys.argv[2]
F = pd.read_parquet(os.path.join(D_DIR, 'frame.parquet'))
D = pd.read_parquet(os.path.join(D_DIR, 'defendants.parquet'),
                    columns=['court', 'level', 'jyear', 'jcase', 'jno', 'def_idx', 'case_outcome', 'hc_outcome', 'appellants',
                             'orig_court', 'orig_year', 'orig_case', 'orig_no', 'end_date', 'n_charges'])
C = pd.read_parquet(os.path.join(D_DIR, 'charges.parquet'),
                    columns=['court', 'jyear', 'jcase', 'jno', 'def_idx', 'charge_idx', 'result', 'prison_months', 'detention_days'])
DA = pd.read_parquet(os.path.join(D_DIR, 'dist_appellants.parquet'))
K = ['court', 'jyear', 'jcase', 'jno']
CTRL = ['rec', 'attempt_i', 'acc_i', 'm_self', 'm_confess', 'm_59', 'm_mental', 'm_minor', 'a_any', 'a_rec', 'simplified', 'indigenous', 'dv_i']

# first-instance cases with a single defendant, decided by end-2024 so that appeals have had time to finish
ndef = D[D['level'] == 'district'].groupby(K)['def_idx'].nunique().rename('ndef').reset_index()
F = F.merge(ndef, on=K, how='left')
F = F[(F['ndef'] == 1) & (F['date'] <= '2024-12-31') & F['custodial']].copy()

# appeals: district appellate division + High Court, single-defendant appeal judgments
A = D[((D['level'] == 'district') & D['jcase'].str.contains('上') & ~D['jcase'].str.contains('抗')) | (D['level'] == 'high')].copy()
A = A.merge(DA[K + ['def_idx', 'appellants']].rename(columns={'appellants': 'app_d'}), on=K + ['def_idx'], how='left')
A['appellants'] = np.where(A['level'] == 'high', A['appellants'], A['app_d'].fillna(''))
A['outcome'] = np.where(A['level'] == 'high', A['hc_outcome'], A['case_outcome'])
na = A.groupby(K)['def_idx'].transform('nunique')
A = A[(na == 1) & A['orig_no'].notna()]
ch = C[(C['charge_idx'] == 0) & (C['def_idx'] == 0)]
A = A.merge(ch, on=K + ['def_idx'], how='left')
A = A.sort_values('end_date').drop_duplicates(['orig_court', 'orig_year', 'orig_case', 'orig_no'], keep='last')
A = A.rename(columns={'orig_court': 'court_o', 'orig_year': 'jyear_o', 'orig_case': 'jcase_o', 'orig_no': 'jno_o'})
A['jyear_o'] = A['jyear_o'].astype(int); A['jno_o'] = A['jno_o'].astype(int)
A['a_days'] = np.where(A['result'].isin(['有期徒刑', '拘役']), A['prison_months'].fillna(0) * 30 + A['detention_days'].fillna(0),
                       np.where(A['result'].isin(['罰金', '無罪', '免除其刑']), 0.0, np.nan))
A = A[['court_o', 'jyear_o', 'jcase_o', 'jno_o', 'level', 'appellants', 'outcome', 'a_days', 'result']]
F = F.merge(A, left_on=K, right_on=['court_o', 'jyear_o', 'jcase_o', 'jno_o'], how='left')
F['appealed'] = F['outcome'].notna() & ~F['outcome'].fillna('').isin(['撤回上訴', ''])
F['app_def'] = F['appealed'] & F['appellants'].fillna('').str.contains('被告')
F['app_pros'] = F['appealed'] & F['appellants'].fillna('').str.contains('檢察官')
F['changed'] = F['appealed'] & F['outcome'].fillna('').str.contains('撤銷')
F['remand'] = F['outcome'].fillna('').str.contains('發回')
keep_first = ~F['changed'] | F['a_days'].isna()
F['final_days'] = np.where(keep_first, F['sentence_days'], F['a_days'])
F.loc[F['remand'], 'final_days'] = np.nan
F = F[F['final_days'].notna()]
print('cases', len(F), 'appeal rate', round(F['appealed'].mean(), 4), 'by def', round(F['app_def'].mean(), 4), 'by pros', round(F['app_pros'].mean(), 4),
      'changed', round(F['changed'].mean(), 4), flush=True)

def design(d):
    X = d[CTRL].astype(float).copy()
    return pd.concat([X, pd.get_dummies(d['counsel'], prefix='c', drop_first=True, dtype=float),
                      pd.get_dummies(d['art'].astype(str) + '-' + d['art_sub'].fillna(0).astype(int).astype(str) + '-' + d['para'].fillna(0).astype(int).astype(str),
                                     prefix='s', drop_first=True, dtype=float)], axis=1)

def resid(d, ycols):
    X = design(d)
    Xd = (X - X.groupby(d['pool']).transform('mean'))
    keep = Xd.columns[Xd.abs().sum() > 0]
    Xm = Xd[keep].to_numpy()
    out = {}
    for y in ycols:
        yd = d[y].astype(float) - d.groupby('pool')[y].transform('mean').astype(float)
        b, *_ = np.linalg.lstsq(Xm, yd.to_numpy(), rcond=None)
        out[y] = yd.to_numpy() - Xm @ b
    return out

def tau2(j, e):
    st = pd.DataFrame({'j': j, 'e': e}).groupby('j')['e'].agg(['mean', 'count', 'var'])
    st = st[st['count'] >= 2]
    N, J = st['count'].sum(), len(st)
    s2 = ((st['count'] - 1) * st['var']).sum() / (N - J)
    mbar = np.average(st['mean'], weights=st['count'])
    n0 = (N - (st['count'] ** 2).sum() / N) / (J - 1)
    return max((((st['count'] * (st['mean'] - mbar) ** 2).sum()) / (J - 1) - s2) / n0, 0.0)

parts, summ = [], []
for off, d in F.groupby('offence'):
    d = d[d.groupby('pool')['judge_key'].transform('nunique') >= 2].copy()
    if len(d) < 2000:
        continue
    for v in ('appealed', 'app_def', 'app_pros', 'changed'):
        d[v] = d[v].astype(float)
    d['delta'] = d['final_days'] - d['sentence_days']
    r = resid(d, ['sentence_days', 'final_days', 'appealed', 'app_def', 'app_pros', 'changed', 'delta'])
    for k, v in r.items():
        d['r_' + k] = v
    g = d.groupby('judge_key')['r_sentence_days']
    n = g.transform('count')
    d['z'] = (g.transform('sum') - d['r_sentence_days']) / (n - 1)          # leave-one-out stringency (days)
    d = d[n >= 30]
    t_first, t_final = tau2(d['judge_key'].to_numpy(), d['r_sentence_days'].to_numpy()), tau2(d['judge_key'].to_numpy(), d['r_final_days'].to_numpy())
    sl = {}
    for v in ('sentence_days', 'final_days', 'appealed', 'app_def', 'app_pros', 'changed', 'delta'):
        x = d['z'].to_numpy(); y = d['r_' + v].to_numpy()
        b = np.cov(x, y)[0, 1] / np.var(x, ddof=1)
        # judge-clustered SE
        e = y - y.mean() - b * (x - x.mean())
        sc = pd.Series((x - x.mean()) * e).groupby(d['judge_key'].to_numpy()).sum()
        se = math.sqrt((sc ** 2).sum()) / ((x - x.mean()) ** 2).sum()
        sl[v] = (float(b), float(se))
    corr = 1 - sl['final_days'][0] / sl['sentence_days'][0] if sl['sentence_days'][0] else None
    summ.append({'offence': off, 'n': int(len(d)), 'judges': int(d['judge_key'].nunique()), 'appeal_rate': float(d['appealed'].mean()),
                 'app_def_rate': float(d['app_def'].mean()), 'app_pros_rate': float(d['app_pros'].mean()), 'changed_rate': float(d['changed'].mean()),
                 'tau_first': math.sqrt(t_first), 'tau_final': math.sqrt(t_final), 'var_removed': 1 - t_final / t_first if t_first else None,
                 'slopes': sl, 'correction_share': corr})
    print(off, len(d), 'appeal %.3f' % d['appealed'].mean(), 'tau %.1f -> %.1f' % (math.sqrt(t_first), math.sqrt(t_final)),
          'slope app_def per 10d %.4f' % (10 * sl['app_def'][0]), 'app_pros %.4f' % (10 * sl['app_pros'][0]), 'corr %.3f' % corr, flush=True)
    d['zbin'] = pd.qcut(d['z'], 10, labels=False, duplicates='drop')
    b = d.groupby('zbin').agg(z=('z', 'mean'), appealed=('appealed', 'mean'), app_def=('app_def', 'mean'), app_pros=('app_pros', 'mean'),
                              changed=('changed', 'mean'), delta=('delta', 'mean'), n=('z', 'size')).reset_index()
    b['offence'] = off
    parts.append(b)
bins = pd.concat(parts)
json.dump({'summary': summ, 'bins': bins.to_dict('records')}, open(OUT, 'w'), ensure_ascii=False)
print('wrote', OUT)
