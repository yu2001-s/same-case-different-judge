"""National extension: judge variation in 2025 impaired-driving (刑法185-3 I) sentences across all district courts,
from the Judicial Yuan's open terminated-case microdata. No breath-alcohol data here, so only the controls the
microdata carry are used (repeat-offender status and the coded aggravating/mitigating reasons); with random
assignment within pools the omitted case facts add noise, not bias, to judge comparisons.

Usage: micro_analyze.py DUI_CSV OUT_JSON
"""
import sys, json, math
import numpy as np, pandas as pd
import statsmodels.formula.api as smf
from scipy import stats

src, out = sys.argv[1], sys.argv[2]
rng = np.random.default_rng(20261009)
N_PERM = 1000
d = pd.read_csv(src)

COURT_EN = {'TPD': 'Taipei', 'PCD': 'New Taipei', 'SLD': 'Shilin', 'TYD': 'Taoyuan', 'SCD': 'Hsinchu', 'MLD': 'Miaoli', 'TCD': 'Taichung',
            'CHD': 'Changhua', 'NTD': 'Nantou', 'ULD': 'Yunlin', 'CYD': 'Chiayi', 'TND': 'Tainan', 'KSD': 'Kaohsiung', 'CTD': 'Ciaotou',
            'PTD': 'Pingtung', 'TTD': 'Taitung', 'HLD': 'Hualien', 'ILD': 'Yilan', 'KLD': 'Keelung', 'PHD': 'Penghu', 'KMD': 'Kinmen', 'LCD': 'Lienchiang'}
R = {}
funnel = [('185-3 I records, 22 district courts, 2025', len(d))]
s = d[(d['n_defendants'] == 1) & (d['n_charges'] == 1)]; funnel.append(('One defendant, one charge', len(s)))
s = s[~s['jcase'].str.contains('上|抗|再|聲|協|國審', regex=True)]; funnel.append(('First-instance judgment', len(s)))
s = s[s['procedure'].fillna('') != '認罪協商']; funnel.append(('Not a plea bargain', len(s)))
s = s[s['charge_result'] == '有期徒刑']; funnel.append(('Prison sentence imposed', len(s)))
s = s[s['judge1'].notna() & s['judge2'].isna()]; funnel.append(('Decided by a single judge', len(s)))
s = s.copy()
s['court_en'] = s['court_code'].map(COURT_EN)
s['sentence_days'] = s['prison_months'].fillna(0) * 30 + s['detention_days'].fillna(0)
s['date'] = pd.to_datetime(s['date'])
s['quarter'] = s['date'].dt.quarter
s['pool'] = s['court_code'] + '|' + s['jcase'] + '|Q' + s['quarter'].astype(str)
s['judge_id'] = s['court_code'] + ':' + s['judge1']
s['addl_fine'] = (s['fine_ntd'].fillna(0) > 0).astype(int)
s['prob'] = s['probation'].fillna(0).astype(int)
s['rec'] = s['recidivist'].fillna(0).astype(int)
for k, pat in [('m_selfreport', '自首'), ('m_art59', '59'), ('m_attempt', '未遂'), ('m_other', '.')]:
    s[k] = s['mitigating'].fillna('').str.contains(pat).astype(int)
s['a_any'] = s['aggravating'].fillna('').str.len().gt(0).astype(int)
s['indigenous'] = s['jcase'].str.contains('原').astype(int)
# keep pools with at least two judges so that within-pool comparisons exist
pj = s.groupby('pool')['judge_id'].nunique()
s = s[s['pool'].map(pj) >= 2]; funnel.append(('In an assignment pool with 2+ judges', len(s)))
R['funnel'] = funnel
R['n'] = int(len(s)); R['n_judges'] = int(s['judge_id'].nunique()); R['n_courts'] = int(s['court_code'].nunique())
R['mean_days'] = float(s['sentence_days'].mean()); R['share_prob'] = float(s['prob'].mean()); R['share_fine'] = float(s['addl_fine'].mean())
R['share_rec'] = float(s['rec'].mean())

CTRL = 'rec + m_selfreport + m_art59 + m_other + a_any'
base = smf.ols('sentence_days ~ C(pool) + ' + CTRL, data=s).fit()
withj = smf.ols('sentence_days ~ C(pool) + ' + CTRL + ' + C(judge_id)', data=s).fit()
f = withj.compare_f_test(base)
R['r2'] = {'controls_pool': base.rsquared, 'plus_judge': withj.rsquared, 'F': float(f[0]), 'p': float(f[1]), 'df': int(f[2])}
s['resid'] = base.resid
mm = smf.mixedlm('resid ~ 1', s, groups=s['judge_id']).fit(reml=True)
mm_ml = smf.mixedlm('resid ~ 1', s, groups=s['judge_id']).fit(reml=False)
ll0 = smf.ols('resid ~ 1', data=s).fit().llf
jsd = float(np.sqrt(mm.cov_re.iloc[0, 0])); rsd = float(np.sqrt(mm.scale)); lr = 2 * (mm_ml.llf - ll0)
R['mixed'] = {'judge_sd_days': jsd, 'resid_sd_days': rsd, 'icc': jsd ** 2 / (jsd ** 2 + rsd ** 2), 'lr': float(lr), 'p': float(0.5 * stats.chi2.sf(lr, 1))}
blup = pd.Series({k: float(v.iloc[0]) for k, v in mm.random_effects.items()})
jn = s['judge_id'].value_counts()
big = blup[jn.reindex(blup.index) >= 30]
R['lottery'] = {'n_judges_30': int(len(big)), 'p10': float(big.quantile(.1)), 'p90': float(big.quantile(.9)), 'gap': float(big.quantile(.9) - big.quantile(.1))}

def between_var(df):
    g = df.groupby('judge_id')['resid']; m = g.mean(); n = g.size()
    return float(np.average((m - np.average(m, weights=n)) ** 2, weights=n))
obs = between_var(s); perm = []
idx = list(s.groupby('pool').indices.values()); jj0 = s['judge_id'].to_numpy(); tmp = s[['resid']].copy()
for b in range(N_PERM):
    jj = jj0.copy()
    for ix in idx:
        jj[ix] = rng.permutation(jj[ix])
    tmp['judge_id'] = jj; perm.append(between_var(tmp))
perm = np.array(perm)
R['permutation'] = {'observed': obs, 'null_mean': float(perm.mean()), 'ratio': float(obs / perm.mean()), 'p': float((1 + (perm >= obs).sum()) / (1 + N_PERM)), 'n_perm': N_PERM}

rs = []
for k in range(200):
    r_ = np.random.default_rng(k)
    a = s.assign(h=r_.integers(0, 2, len(s)))
    m = a[a['judge_id'].map(jn) >= 30].groupby(['judge_id', 'h'])['resid'].mean().unstack().dropna()
    rs.append(np.corrcoef(m[0], m[1])[0, 1])
R['split_half'] = {'r_mean': float(np.mean(rs)), 'p05': float(np.quantile(rs, .05)), 'p95': float(np.quantile(rs, .95))}

# per-court picture: spread of judge effects within each court (judges with 30+ cases)
courts = []
bj = pd.DataFrame({'blup': blup, 'n': jn.reindex(blup.index)})
bj['court'] = [i.split(':')[0] for i in bj.index]
for c, g in bj[bj['n'] >= 30].groupby('court'):
    courts.append({'court': COURT_EN.get(c, c), 'code': c, 'judges': int(len(g)), 'cases': int(s[s['court_code'] == c].shape[0]),
                   'min': float(g['blup'].min()), 'p25': float(g['blup'].quantile(.25)), 'median': float(g['blup'].median()),
                   'p75': float(g['blup'].quantile(.75)), 'max': float(g['blup'].max()),
                   'mean_days': float(s.loc[s['court_code'] == c, 'sentence_days'].mean())})
R['courts'] = sorted(courts, key=lambda x: x['mean_days'])

# court-level means adjusted for the available controls (where you are tried)
mc = smf.ols('sentence_days ~ C(court_code) + C(quarter) + ' + CTRL + ' + indigenous', data=s).fit()
pred = []
for c in sorted(s['court_code'].unique()):
    x = pd.DataFrame({'court_code': [c], 'quarter': [2], 'rec': [0], 'm_selfreport': [0], 'm_art59': [0], 'm_other': [0], 'a_any': [0], 'indigenous': [0]})
    pred.append({'court': COURT_EN.get(c, c), 'pred_days': float(mc.predict(x).iloc[0]), 'n': int((s['court_code'] == c).sum())})
R['court_adjusted'] = sorted(pred, key=lambda x: x['pred_days'])

def binary(col):
    b0 = smf.ols(f'{col} ~ C(pool) + ' + CTRL, data=s).fit(); b1 = smf.ols(f'{col} ~ C(pool) + ' + CTRL + ' + C(judge_id)', data=s).fit()
    ff = b1.compare_f_test(b0)
    rr = s.assign(r=b0.resid).groupby('judge_id').agg(adj=('r', 'mean'), n=(col, 'size'))
    rr = rr[rr['n'] >= 30]; br = float(s[col].mean())
    return {'base': br, 'F': float(ff[0]), 'p': float(ff[1]), 'p10': float(br + rr['adj'].quantile(.1)), 'p90': float(br + rr['adj'].quantile(.9)),
            'share_judges_never': float((s[s['judge_id'].map(jn) >= 30].groupby('judge_id')[col].max() == 0).mean())}
R['probation'] = binary('prob'); R['addl_fine'] = binary('addl_fine')

mi = smf.ols('sentence_days ~ indigenous + C(court_code) + C(quarter) + ' + CTRL, data=s).fit(cov_type='cluster', cov_kwds={'groups': s['judge_id']})
R['indigenous'] = {'n': int(s['indigenous'].sum()), 'coef': float(mi.params['indigenous']), 'lo': float(mi.conf_int().loc['indigenous', 0]),
                   'hi': float(mi.conf_int().loc['indigenous', 1]), 'p': float(mi.pvalues['indigenous'])}

def clean(o):
    if isinstance(o, dict): return {str(k): clean(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)): return [clean(v) for v in o]
    if isinstance(o, (np.integer,)): return int(o)
    if isinstance(o, (np.floating, float)): return None if math.isnan(o) or math.isinf(o) else float(o)
    return o
json.dump(clean(R), open(out, 'w'), ensure_ascii=False, indent=1)
print(json.dumps(clean({k: R[k] for k in ['funnel', 'n', 'n_judges', 'r2', 'mixed', 'lottery', 'permutation', 'split_half', 'probation', 'addl_fine', 'indigenous']}), ensure_ascii=False, indent=1))
