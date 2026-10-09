"""Pilot analysis: does the assigned judge change the sentence for the same drunk-driving offence?

Input : directory of raw judgment pages (from scraper/collect.py)
Output: out/parsed_all.csv        every parsed judgment (no defendant names, judges pseudonymised)
        out/sample.csv            analysis sample
        out/results.json          all numbers + chart data used by the report
        out/judge_key_PRIVATE.csv pseudonym -> judge name (never committed)
"""
import os, sys, json, re, hashlib, math
import numpy as np, pandas as pd
import statsmodels.formula.api as smf
import statsmodels.api as sm
from scipy import stats

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import parse as P

RAW, OUT = sys.argv[1], sys.argv[2]
N_PERM = int(os.environ.get('N_PERM', '1000'))
os.makedirs(OUT, exist_ok=True)
rng = np.random.default_rng(20261009)

COURT = {'臺灣臺北地方法院': 'Taipei', '臺灣新北地方法院': 'New Taipei', '臺灣桃園地方法院': 'Taoyuan',
         '臺灣臺中地方法院': 'Taichung', '臺灣臺南地方法院': 'Tainan', '臺灣高雄地方法院': 'Kaohsiung'}

# ---------------------------------------------------------------- parse
rows = []
for fn in sorted(os.listdir(RAW)):
    try:
        r = P.parse(open(os.path.join(RAW, fn), encoding='utf-8').read())
    except Exception as e:  # keep going; count failures
        r = None
    if r:
        r.pop('main', None)
        r['judges'] = '|'.join(r['judges'])
        r['file'] = fn
        rows.append(r)
df = pd.DataFrame(rows)
df['court'] = df['court_name'].map(COURT).fillna(df['court_name'])

# pseudonymise judges: stable code per court, ordered by caseload
key = []
df['judge_id'] = None
for court, g in df[df['judge'].notna()].groupby('court'):
    order = g['judge'].value_counts().index.tolist()
    abbrev = {'Taipei': 'TPE', 'New Taipei': 'NTP', 'Taoyuan': 'TYN', 'Taichung': 'TXG', 'Tainan': 'TNN', 'Kaohsiung': 'KHH'}.get(court, court[:3].upper())
    for i, name in enumerate(order):
        code = f'{abbrev}-{i + 1:02d}'
        df.loc[(df['court'] == court) & (df['judge'] == name), 'judge_id'] = code
        key.append((code, court, name))
pd.DataFrame(key, columns=['judge_id', 'court', 'judge']).to_csv(os.path.join(OUT, 'judge_key_PRIVATE.csv'), index=False)
pub = df.drop(columns=['judge', 'judges', 'prosecutor'])
pub.to_csv(os.path.join(OUT, 'parsed_all.csv'), index=False)

# ---------------------------------------------------------------- sample
funnel = [('All 公共危險 decisions downloaded', len(df))]
s = df[df['is_judgment']]; funnel.append(('Judgments (not rulings/裁定)', len(s)))
s = s[~s['appeal']]; funnel.append(('First instance (no appeals)', len(s)))
s = s[s['simple'] & ~s['plea_bargain']]; funnel.append(('Simple-procedure judgments (簡易判決, one judge)', len(s)))
alcohol = (s['art_185_3_1_1'] | s['bac'].notna()) & ~s['drugs'] & ~s['art_185_4'] & ~s['art_185_3_2'] & ~s['art_185_3_3']
s = s[alcohol]; funnel.append(('Alcohol offence only (刑法185-3 I(1)), no injury/death count', len(s)))
s = s[~s['multi'] & ~s['acquit'] & ~s['dismiss']]; funnel.append(('Single count, convicted', len(s)))
s = s[s['prison_months'].notna() | s['detention_days'].notna()]; funnel.append(('Custodial sentence parsed', len(s)))
s = s[s['bac'].notna()]; funnel.append(('Breath-alcohol level parsed', len(s)))
s = s[s['judge_id'].notna()]; funnel.append(('Single judge identified', len(s)))
s = s.copy()
for a, b in funnel:
    print(f'{b:7d}  {a}')

s['sentence_days'] = s['prison_months'].fillna(0) * 30 + s['detention_days'].fillna(0)
s['date'] = pd.to_datetime(s['date'])
s['quarter'] = s['date'].dt.quarter
s['division'] = s['division'].fillna('unknown')
# assignment pool: cases with the same court, case-type prefix (字別, which also encodes the 簡易庭 location)
# and quarter are distributed among the same set of judges by the court's random-assignment rules
s['pool'] = s['court'] + '|' + s['jcase'] + '|Q' + s['quarter'].astype(str)
s['bac_bin'] = pd.cut(s['bac'], [0, 0.40, 0.55, 0.80, 1.00, 9], right=False,
                      labels=['0.25-0.39', '0.40-0.54', '0.55-0.79', '0.80-0.99', '1.00+'])
s['n_prior'] = s['n_prior_dui'].fillna(pd.Series(np.where(s['prior_dui'], 1, 0), index=s.index)).clip(upper=3)
s.loc[s['recidivist'] & (s['n_prior'] < 1), 'n_prior'] = 1
s['vehicle'] = s['vehicle'].fillna('unknown')
s['econ_c'] = s['econ'].fillna(0).astype(int).astype(str)
s['edu_c'] = s['edu'].fillna(0).astype(int).astype(str)
s['addl_fine'] = (s['addl_fine_ntd'] > 0).astype(int)
s['indigenous'] = s['jcase'].str.contains('原').astype(int)  # 原-prefixed case types go to Indigenous-affairs divisions
s['prob'] = s['probation'].astype(int)
# keep pools with >=2 judges and judges with >=10 cases for judge-level work
jn = s['judge_id'].value_counts()
s['judge_n'] = s['judge_id'].map(jn)
s.to_csv(os.path.join(OUT, 'sample.csv'), index=False)

R = {'funnel': funnel, 'n_sample': int(len(s)), 'n_judges': int(s['judge_id'].nunique()),
     'n_courts': int(s['court'].nunique()), 'date_min': str(s['date'].min().date()), 'date_max': str(s['date'].max().date())}

LEGAL = ('C(bac_bin) + bac + C(n_prior) + recidivist + accident + injury + C(vehicle) + self_report + art59 '
         '+ C(econ_c) + C(edu_c)')

def fit(formula, data):
    return smf.ols(formula, data=data).fit(cov_type='cluster', cov_kwds={'groups': data['judge_id']})

# ---------------------------------------------------------------- descriptives
R['desc'] = {
    'sentence_mean': float(s['sentence_days'].mean()), 'sentence_median': float(s['sentence_days'].median()),
    'sentence_dist': s['prison_months'].value_counts().sort_index().to_dict(),
    'bac_mean': float(s['bac'].mean()), 'share_prior': float((s['n_prior'] > 0).mean()),
    'share_accident': float(s['accident'].mean()), 'share_probation': float(s['prob'].mean()),
    'share_addl_fine': float(s['addl_fine'].mean()), 'conv_rate': s['conv_rate'].value_counts().to_dict(),
    'by_court': s.groupby('court').agg(n=('sentence_days', 'size'), judges=('judge_id', 'nunique'),
                                       mean_days=('sentence_days', 'mean'), prob=('prob', 'mean'),
                                       prior=('n_prior', lambda x: float((x > 0).mean()))).reset_index().to_dict('records'),
}
R['bac_curve'] = (s.groupby('bac_bin', observed=True)['sentence_days']
                  .agg(['mean', 'count', lambda x: x.quantile(.1), lambda x: x.quantile(.9)])
                  .reset_index().rename(columns={'<lambda_0>': 'p10', '<lambda_1>': 'p90'}).astype({'bac_bin': str}).to_dict('records'))
R['bac_prior_curve'] = (s.assign(prior=np.where(s['n_prior'] > 0, 'prior', 'first'))
                        .groupby(['bac_bin', 'prior'], observed=True)['sentence_days'].agg(['mean', 'count']).reset_index()
                        .astype({'bac_bin': str}).to_dict('records'))

# ---------------------------------------------------------------- variance decomposition
m_pool = fit('sentence_days ~ C(pool)', s)
m_legal = fit('sentence_days ~ C(pool) + ' + LEGAL, s)
m_judge = smf.ols('sentence_days ~ C(pool) + ' + LEGAL + ' + C(judge_id)', data=s).fit()
m_legal_plain = smf.ols('sentence_days ~ C(pool) + ' + LEGAL, data=s).fit()
ftest = m_judge.compare_f_test(m_legal_plain)
r2_legal_only = smf.ols('sentence_days ~ ' + LEGAL, data=s).fit().rsquared
R['r2'] = {'pool_only': m_pool.rsquared, 'legal_only': r2_legal_only, 'pool_legal': m_legal.rsquared,
           'pool_legal_judge': m_judge.rsquared, 'judge_increment': m_judge.rsquared - m_legal.rsquared,
           'judge_F': float(ftest[0]), 'judge_F_p': float(ftest[1]), 'judge_F_df': int(ftest[2]),
           'adj_r2_legal': m_legal_plain.rsquared_adj, 'adj_r2_judge': m_judge.rsquared_adj}
R['legal_coefs'] = {k: [float(m_legal.params[k]), float(m_legal.bse[k])] for k in m_legal.params.index if not k.startswith('C(pool)')}

# mixed model: judge random intercept, pool + legal fixed effects
s['resid_legal'] = m_legal_plain.resid
# two-step random-intercept model: residualise on pool + legal factors (OLS handles rank deficiency),
# then estimate the judge variance component on the residuals (REML) and test it with a likelihood ratio.
s['one'] = 1.0
mm = smf.mixedlm('resid_legal ~ 1', s, groups=s['judge_id']).fit(reml=True)
judge_sd = float(np.sqrt(mm.cov_re.iloc[0, 0])); resid_sd = float(np.sqrt(mm.scale))
mm_ml = smf.mixedlm('resid_legal ~ 1', s, groups=s['judge_id']).fit(reml=False)
mm0_llf = smf.ols('resid_legal ~ 1', data=s).fit().llf
lr = 2 * (mm_ml.llf - mm0_llf)
R['mixed'] = {'judge_sd_days': judge_sd, 'resid_sd_days': resid_sd, 'icc': judge_sd ** 2 / (judge_sd ** 2 + resid_sd ** 2),
              'lr_stat': float(lr), 'lr_p': float(0.5 * stats.chi2.sf(lr, 1)) if lr > 0 else 1.0}
ranef = mm.random_effects
blup = pd.Series({k: float(v.iloc[0]) for k, v in ranef.items()})

# judge effects (fixed-effect version) relative to pool-weighted average, with SEs, for judges with >= 30 cases
MINN = 20
jparams = {k[len('C(judge_id)[T.'):-1]: (m_judge.params[k], m_judge.bse[k]) for k in m_judge.params.index if k.startswith('C(judge_id)[T.')}
base = sorted(set(s['judge_id']) - set(jparams))[0]
jparams[base] = (0.0, np.nan)
jdf = pd.DataFrame([(j, v[0], v[1]) for j, v in jparams.items()], columns=['judge_id', 'fe', 'se'])
jdf['n'] = jdf['judge_id'].map(jn)
jdf['court'] = jdf['judge_id'].map(s.drop_duplicates('judge_id').set_index('judge_id')['court'])
# centre within court (weighted by caseload) so each judge is compared with colleagues in the same court
jdf['effect'] = jdf['fe'] - jdf.groupby('court')['fe'].transform(lambda x: np.average(x, weights=jdf.loc[x.index, 'n']))
jdf['blup'] = jdf['judge_id'].map(blup)
mean_resid = s.groupby('judge_id')['resid_legal'].agg(['mean', 'sem', 'size'])
jdf = jdf.merge(mean_resid.rename(columns={'mean': 'mean_resid', 'sem': 'resid_se', 'size': 'nn'}), left_on='judge_id', right_index=True)
big = jdf[jdf['n'] >= MINN].copy()
# CI from residual means (simple, transparent): mean residual +/- 1.96 * SE
big['lo'] = big['mean_resid'] - 1.96 * big['resid_se']
big['hi'] = big['mean_resid'] + 1.96 * big['resid_se']
R['judges'] = big.sort_values('mean_resid')[['judge_id', 'court', 'n', 'mean_resid', 'lo', 'hi', 'blup']].to_dict('records')
R['judge_min_n'] = MINN
R['n_judges_big'] = int(len(big)); R['n_cases_big'] = int(big['n'].sum())
q = big['blup'].quantile([.1, .9])
R['lottery'] = {'p10_blup': float(q.iloc[0]), 'p90_blup': float(q.iloc[1]), 'gap_p90_p10_days': float(q.iloc[1] - q.iloc[0]),
                'min_blup': float(big['blup'].min()), 'max_blup': float(big['blup'].max()),
                'share_sig': float(((big['lo'] > 0) | (big['hi'] < 0)).mean())}

# predicted sentence for a "standard case" by judge (BLUP + model prediction for typical first offence)
std = s.iloc[[0]].copy()
std['bac_bin'] = pd.Categorical(['0.40-0.54'], categories=s['bac_bin'].cat.categories); std['bac'] = 0.47
std['n_prior'] = 0; std['recidivist'] = False; std['accident'] = False; std['injury'] = False
std['vehicle'] = 'car/truck'; std['self_report'] = False; std['art59'] = False; std['econ_c'] = '0'; std['edu_c'] = '0'
std_preds = {}
for court in s['court'].unique():
    pools = s[(s['court'] == court) & (s['indigenous'] == 0)]['pool'].value_counts()
    std['pool'] = pools.index[0]
    std_preds[court] = float(m_legal_plain.predict(std).iloc[0])
R['standard_case'] = {'description': 'first offence, breath alcohol 0.47 mg/L, car, no accident, no other aggravating or mitigating factors',
                      'by_court': std_preds}
std_rows = []
for _, j in big.iterrows():
    std_rows.append({'judge_id': j['judge_id'], 'court': j['court'], 'pred_days': std_preds[j['court']] + j['blup']})
R['standard_case']['by_judge'] = std_rows

# ---------------------------------------------------------------- randomisation check: are case facts balanced across judges?
bal = []
for col, lab in [('bac', 'Breath-alcohol level'), ('n_prior', 'Number of prior drunk-driving cases'), ('accident', 'Crash in this incident'),
                 ('recidivist', 'Repeat offender (累犯)'), ('motorcycle_i', 'Riding a motorcycle')]:
    if col == 'motorcycle_i':
        s['motorcycle_i'] = (s['vehicle'] == 'motorcycle').astype(int)
    y = s[col].astype(float)
    b0 = smf.ols(f'{col} ~ C(pool)', data=s.assign(**{col: y})).fit(); b1 = smf.ols(f'{col} ~ C(pool) + C(judge_id)', data=s.assign(**{col: y})).fit()
    ff = b1.compare_f_test(b0)
    bal.append({'fact': lab, 'F': float(ff[0]), 'p': float(ff[1])})
R['balance'] = bal

# case-mix index: the sentence predicted from case facts alone. If judges' case mix differed a lot, judges would differ
# in this index; compare its noise-corrected judge SD with the judge SD in actual sentencing (net of facts).
m_facts = smf.ols('sentence_days ~ ' + LEGAL, data=s).fit()
s['pred_facts'] = m_facts.fittedvalues
s['pred_facts_r'] = smf.ols('pred_facts ~ C(pool)', data=s).fit().resid
mm_mix = smf.mixedlm('pred_facts_r ~ 1', s, groups=s['judge_id']).fit(reml=True)
b0 = smf.ols('pred_facts ~ C(pool)', data=s).fit(); b1 = smf.ols('pred_facts ~ C(pool) + C(judge_id)', data=s).fit()
ff = b1.compare_f_test(b0)
R['casemix'] = {'judge_sd_casemix_days': float(np.sqrt(max(mm_mix.cov_re.iloc[0, 0], 0))), 'judge_sd_sentencing_days': judge_sd,
                'F': float(ff[0]), 'p': float(ff[1])}

# finer assignment pools (court x case type x month) as a robustness check
s['pool_m'] = s['court'] + '|' + s['jcase'] + '|M' + s['date'].dt.month.astype(str)
a_ = smf.ols('sentence_days ~ C(pool_m) + ' + LEGAL, data=s).fit(); b_ = smf.ols('sentence_days ~ C(pool_m) + ' + LEGAL + ' + C(judge_id)', data=s).fit()
f_ = b_.compare_f_test(a_)
s['resid_m'] = a_.resid
mm_m = smf.mixedlm('resid_m ~ 1', s, groups=s['judge_id']).fit(reml=True)
R['monthly_pools'] = {'F': float(f_[0]), 'p': float(f_[1]), 'judge_sd_days': float(np.sqrt(mm_m.cov_re.iloc[0, 0])),
                      'icc': float(mm_m.cov_re.iloc[0, 0] / (mm_m.cov_re.iloc[0, 0] + mm_m.scale))}

# how much do the case-fact controls change the judge estimate? (the national microdata lack most of them)
s['resid_min'] = smf.ols('sentence_days ~ C(pool) + recidivist + self_report + art59', data=s).fit().resid
mm_min = smf.mixedlm('resid_min ~ 1', s, groups=s['judge_id']).fit(reml=True)
R['controls_compare'] = {'judge_sd_full_controls': judge_sd, 'judge_sd_minimal_controls': float(np.sqrt(mm_min.cov_re.iloc[0, 0])),
                         'resid_sd_full': resid_sd, 'resid_sd_minimal': float(np.sqrt(mm_min.scale))}

# ---------------------------------------------------------------- permutation test (shuffle judges within pool)
def between_var(d):
    g = d.groupby('judge_id')['resid_legal']
    m = g.mean(); n = g.size()
    return float(np.average((m - np.average(m, weights=n)) ** 2, weights=n))

obs = between_var(s)
perm = []
grp = s.groupby('pool').indices
judges = s['judge_id'].to_numpy()
tmp = s[['resid_legal']].copy()
for b in range(N_PERM):
    jj = judges.copy()
    for idx in grp.values():
        jj[idx] = rng.permutation(jj[idx])
    tmp['judge_id'] = jj
    perm.append(between_var(tmp))
perm = np.array(perm)
R['permutation'] = {'observed': obs, 'null_mean': float(perm.mean()), 'null_p99': float(np.quantile(perm, .99)),
                    'p_value': float((1 + (perm >= obs).sum()) / (1 + len(perm))), 'n_perm': N_PERM,
                    'hist': np.histogram(perm, bins=30)[0].tolist(), 'edges': np.histogram(perm, bins=30)[1].tolist(),
                    'ratio': float(obs / perm.mean())}

# ---------------------------------------------------------------- split-half reliability
def split_half(seed):
    r = np.random.default_rng(seed)
    a = s.assign(half=r.integers(0, 2, len(s)))
    m = a[a['judge_n'] >= MINN].groupby(['judge_id', 'half'])['resid_legal'].mean().unstack()
    m = m.dropna()
    return m, float(np.corrcoef(m[0], m[1])[0, 1])

m_half, r_half = split_half(1)
rs = [split_half(k)[1] for k in range(2, 202)]
R['split_half'] = {'r': r_half, 'r_mean_200': float(np.mean(rs)), 'r_p05': float(np.quantile(rs, .05)), 'r_p95': float(np.quantile(rs, .95)),
                   'points': [{'judge_id': j, 'a': float(v[0]), 'b': float(v[1]), 'court': s.loc[s['judge_id'] == j, 'court'].iloc[0]} for j, v in m_half.iterrows()],
                   'spearman_brown': float(2 * np.mean(rs) / (1 + np.mean(rs)))}

# ---------------------------------------------------------------- secondary outcomes: probation, additional fine
def judge_spread_binary(col):
    m0 = smf.ols(f'{col} ~ C(pool) + ' + LEGAL, data=s).fit()
    m1 = smf.ols(f'{col} ~ C(pool) + ' + LEGAL + ' + C(judge_id)', data=s).fit()
    f = m1.compare_f_test(m0)
    rr = s.assign(r=m0.resid).groupby('judge_id').agg(rate=(col, 'mean'), adj=('r', 'mean'), n=(col, 'size'), court=('court', 'first'))
    rr = rr[rr['n'] >= MINN]
    base_rate = float(s[col].mean())
    return {'base_rate': base_rate, 'F': float(f[0]), 'p': float(f[1]),
            'judges': [{'judge_id': j, 'court': v['court'], 'n': int(v['n']), 'raw': float(v['rate']), 'adj': float(base_rate + v['adj'])}
                       for j, v in rr.sort_values('adj').iterrows()],
            'adj_p10': float(base_rate + rr['adj'].quantile(.1)), 'adj_p90': float(base_rate + rr['adj'].quantile(.9))}

R['probation'] = judge_spread_binary('prob')
R['addl_fine'] = judge_spread_binary('addl_fine')

# ---------------------------------------------------------------- extraneous timing factors (within judge)
s['dow'] = s['date'].dt.dayofweek  # 0=Mon
bd = pd.bdate_range('2025-01-01', '2025-12-31')
last3 = set()
for (y, mth), g in pd.Series(bd).groupby([bd.year, bd.month]):
    last3.update(g.sort_values().iloc[-3:].dt.date)
s['month_end'] = s['date'].dt.date.isin(last3).astype(int)
# working days before the Lunar New Year break (2025-01-25 .. 2025-02-02) and before the Dragon Boat / Mid-Autumn long weekends
pre_holiday_days = set(pd.to_datetime(['2025-01-20', '2025-01-21', '2025-01-22', '2025-01-23', '2025-01-24',
                                       '2025-05-29', '2025-05-30', '2025-10-03', '2025-10-08', '2025-10-09']).date)
s['pre_holiday'] = s['date'].dt.date.isin(pre_holiday_days).astype(int)
s['day_load'] = s.groupby(['judge_id', 'date'])['sentence_days'].transform('size')
s['heavy_day'] = (s['day_load'] >= 5).astype(int)
s['dec'] = (s['date'].dt.month == 12).astype(int)
# Frisch-Waugh: partial pool, case facts and judge fixed effects out of the outcome and of each timing variable,
# then regress residual on residuals (avoids the rank problems of pool and judge dummies in one clustered model)
for k in range(1, 5):
    s[f'dow{k}'] = (s['dow'] == k).astype(int)
TV = ['dow1', 'dow2', 'dow3', 'dow4', 'month_end', 'pre_holiday', 'heavy_day', 'dec']
TV = [v for v in TV if s[v].sum() > 0]
X_abs = 'C(pool) + C(judge_id) + ' + LEGAL
rt = pd.DataFrame({'y': smf.ols('sentence_days ~ ' + X_abs, data=s).fit().resid})
for v in TV:
    rt[v] = smf.ols(f'{v} ~ ' + X_abs, data=s).fit().resid
rt['judge_id'] = s['judge_id'].values
tim = smf.ols('y ~ ' + ' + '.join(TV) + ' - 1', data=rt).fit(cov_type='cluster', cov_kwds={'groups': rt['judge_id']})
labels = {'dow1': 'Tuesday (vs Monday)', 'dow2': 'Wednesday (vs Monday)', 'dow3': 'Thursday (vs Monday)',
          'dow4': 'Friday (vs Monday)', 'month_end': 'Last 3 working days of month', 'pre_holiday': 'Working days just before a long holiday',
          'heavy_day': 'Judge signs 5+ of these judgments that day', 'dec': 'December (year-end clearance)'}
tests = []
for k, lab in labels.items():
    if k in tim.params:
        ci = tim.conf_int().loc[k]
        tests.append({'term': lab, 'coef': float(tim.params[k]), 'se': float(tim.bse[k]), 'p': float(tim.pvalues[k]),
                      'lo': float(ci[0]), 'hi': float(ci[1]), 'n_exposed': int(s[k].sum())})
tests = [t for t in tests if t['n_exposed'] > 0 and not math.isnan(t['p'])]
ps = np.array([t['p'] for t in tests])
order = np.argsort(ps); bh = np.empty(len(ps)); m_ = len(ps)
prev = 1.0
for rank, i in reversed(list(enumerate(order, 1))):
    prev = min(prev, ps[i] * m_ / rank); bh[i] = prev
for t, q_ in zip(tests, bh):
    t['q_bh'] = float(q_)
R['timing'] = tests

# ---------------------------------------------------------------- litigant characteristics where visible
sx = s[s['def_sex'].notna()]
if len(sx) > 200 and sx['def_sex'].nunique() == 2:
    msx = smf.ols('sentence_days ~ C(def_sex) + C(pool) + C(judge_id) + ' + LEGAL, data=sx).fit(cov_type='cluster', cov_kwds={'groups': sx['judge_id']})
    k = [x for x in msx.params.index if x.startswith('C(def_sex)')][0]
    R['def_sex'] = {'n': int(len(sx)), 'share_female': float((sx['def_sex'] == '女').mean()), 'term': k,
                    'coef': float(msx.params[k]), 'lo': float(msx.conf_int().loc[k, 0]), 'hi': float(msx.conf_int().loc[k, 1]), 'p': float(msx.pvalues[k])}

# Indigenous-defendant cases (原-prefixed case types) vs others, same court and quarter, same legal factors
s['cq'] = s['court'] + '|Q' + s['quarter'].astype(str)
if s['indigenous'].sum() > 30:
    mi = smf.ols('sentence_days ~ indigenous + C(cq) + ' + LEGAL, data=s).fit(cov_type='cluster', cov_kwds={'groups': s['judge_id']})
    mp = smf.ols('prob ~ indigenous + C(cq) + ' + LEGAL, data=s).fit(cov_type='cluster', cov_kwds={'groups': s['judge_id']})
    mf = smf.ols('addl_fine ~ indigenous + C(cq) + ' + LEGAL, data=s).fit(cov_type='cluster', cov_kwds={'groups': s['judge_id']})
    R['indigenous'] = {'n': int(s['indigenous'].sum()), 'share': float(s['indigenous'].mean()),
                       'raw_mean': float(s.loc[s['indigenous'] == 1, 'sentence_days'].mean()), 'raw_mean_other': float(s.loc[s['indigenous'] == 0, 'sentence_days'].mean()),
                       'prior_share': float((s.loc[s['indigenous'] == 1, 'n_prior'] > 0).mean()), 'prior_share_other': float((s.loc[s['indigenous'] == 0, 'n_prior'] > 0).mean()),
                       'sentence': [float(mi.params['indigenous']), float(mi.conf_int().loc['indigenous', 0]), float(mi.conf_int().loc['indigenous', 1]), float(mi.pvalues['indigenous'])],
                       'probation': [float(mp.params['indigenous']), float(mp.conf_int().loc['indigenous', 0]), float(mp.conf_int().loc['indigenous', 1]), float(mp.pvalues['indigenous'])],
                       'addl_fine': [float(mf.params['indigenous']), float(mf.conf_int().loc['indigenous', 0]), float(mf.conf_int().loc['indigenous', 1]), float(mf.pvalues['indigenous'])]}

# court-level differences for the standard case
R['court_std'] = [{'court': c, 'pred_days': v, 'n': int((s['court'] == c).sum())} for c, v in sorted(std_preds.items(), key=lambda x: x[1])]

# robustness: log outcome, judges >= 50, drop accident cases
rob = {}
for name, d, y in [('log sentence', s, 'np.log(sentence_days)'), ('judges with 50+ cases', s[s['judge_n'] >= 50], 'sentence_days'),
                   ('no accident', s[~s['accident']], 'sentence_days'), ('first offenders only', s[s['n_prior'] == 0], 'sentence_days')]:
    a = smf.ols(f'{y} ~ C(pool) + ' + LEGAL, data=d).fit(); b = smf.ols(f'{y} ~ C(pool) + ' + LEGAL + ' + C(judge_id)', data=d).fit()
    f = b.compare_f_test(a)
    rob[name] = {'n': int(len(d)), 'judges': int(d['judge_id'].nunique()), 'F': float(f[0]), 'p': float(f[1]), 'r2_gain': float(b.rsquared - a.rsquared)}
R['robustness'] = rob

# ---------------------------------------------------------------- external check against the official microdata
micro_path = os.environ.get('MICRO')
if micro_path and os.path.exists(micro_path):
    mic = pd.read_csv(micro_path)
    mic = mic[mic['file'].notna() & (mic['n_charges'] == 1)].drop_duplicates('file').set_index('file')
    j = s.set_index('file').join(mic[['prison_months', 'detention_days', 'probation', 'recidivist', 'fine_ntd', 'judge1']], rsuffix='_jy', how='inner')
    key = pd.read_csv(os.path.join(OUT, 'judge_key_PRIVATE.csv')).set_index('judge_id')['judge']
    def same(a, b):
        a = 0 if pd.isna(a) else float(a); b = 0 if pd.isna(b) else float(b)
        return a == b
    R['microdata_check'] = {
        'n_matched': int(len(j)), 'n_sample': int(len(s)),
        'prison_months': float(np.mean([same(a, b) for a, b in zip(j['prison_months'], j['prison_months_jy'])])),
        'probation': float(np.mean([bool(a) == bool(b) for a, b in zip(j['probation'], j['probation_jy'].fillna(0))])),
        'recidivist': float(np.mean([bool(a) == bool(b) for a, b in zip(j['recidivist'], j['recidivist_jy'].fillna(0))])),
        'addl_fine': float(np.mean([same(a, b) for a, b in zip(j['addl_fine_ntd'], j['fine_ntd'].fillna(0))])),
        'judge': float(np.mean([key.get(a) == b for a, b in zip(j['judge_id'], j['judge1'])])),
    }

def clean_json(o):
    if isinstance(o, dict):
        return {str(k): clean_json(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [clean_json(v) for v in o]
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.floating, float)):
        return None if (o is None or math.isnan(o) or math.isinf(o)) else float(o)
    if isinstance(o, (np.bool_,)):
        return bool(o)
    return o

json.dump(clean_json(R), open(os.path.join(OUT, 'results.json'), 'w'), ensure_ascii=False, indent=1)
print(json.dumps(clean_json({k: R[k] for k in ['funnel', 'n_sample', 'n_judges', 'r2', 'mixed', 'lottery', 'permutation', 'split_half']}), ensure_ascii=False, indent=1)[:6000])
