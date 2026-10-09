"""Pilot check (6 courts, 2025 drunk driving, with blood-alcohol and prior-DUI controls): (a) accuracy of the given-name
gender model against the sex recorded in the charging document; (b) the foreign-national and gender sentencing gaps
with and without the controls that the national microdata lack.

pilot_identity.py SAMPLE_CSV RAWDIR NAME_GENDER_JSON OUT_JSON
"""
import sys, os, re, json, math, html
import numpy as np, pandas as pd
import statsmodels.formula.api as smf

S = pd.read_csv(sys.argv[1]); RAW = sys.argv[2]; NG = json.load(open(sys.argv[3], encoding='utf-8')); OUT = sys.argv[4]
llr = NG['llr']
def name_of(f):
    t = html.unescape(re.sub(r'<[^>]+>', '', open(os.path.join(RAW, f), encoding='utf-8', errors='replace').read()))
    m = re.search(r'被[\s　]*告[\s　]+(.+?)(?:上列|指定辯護人|選任辯護人|輔佐人|公設辯護人|被[\s　]*告)', t[:3000])
    return m.group(1).strip() if m else ''
S['name_raw'] = [name_of(f) for f in S['file']]
S['latin'] = S['name_raw'].str.contains(r'[A-Za-z]{3,}', regex=True)
S['nat'] = [bool(re.search(r'(越南|印尼|泰國|菲律賓|馬來西亞|緬甸)(?:國)?籍', open(os.path.join(RAW, f), encoding='utf-8', errors='replace').read()[:20000])) for f in S['file']]
S['foreign'] = (S['latin'] | S['nat']).astype(float)
def gscore(raw):
    if re.search(r'[○Ｏ〇◯＊*ＡＢＣ甲乙丙丁某]|[A-Za-z]', raw or ''):
        return np.nan
    n = ''.join(ch for ch in re.split(r'[（(，,\s]', raw.strip())[0] if '一' <= ch <= '鿿') if raw else ''
    if len(n) not in (2, 3, 4):
        return np.nan
    g = (n[2:] if len(n) == 4 else n[1:])[-2:].rjust(2, '_')
    return sum(llr.get(f'{p}{ch}', 0.0) for p, ch in enumerate(g))
S['gs'] = S['name_raw'].map(gscore)
v = S[S['def_sex'].isin(['男', '女']) & S['gs'].notna()]
acc = {}
for thr in (1, 2, 3):
    w = v[v['gs'].abs() >= thr]
    acc[str(thr)] = {'coverage': len(w) / len(v), 'accuracy': float(((w['gs'] > 0) == (w['def_sex'] == '女')).mean()),
                     'female_recall': float((w[w['def_sex'] == '女']['gs'] > 0).mean()), 'male_recall': float((w[w['def_sex'] == '男']['gs'] < 0).mean())}
print('name-model vs recorded sex', len(v), acc)
d = S[(S['sentence_days'] > 0) & (S['is_judgment'] == 1) if 'is_judgment' in S else (S['sentence_days'] > 0)].copy()
d['ly'] = np.log(d['sentence_days'])
d['female'] = (d['def_sex'] == '女').astype(float)
d['sex_known'] = d['def_sex'].isin(['男', '女']).astype(float)
res = {'name_model_validation': acc, 'n_validation': int(len(v)), 'foreign_n': int(d['foreign'].sum()), 'n': int(len(d))}
for lab, f in (('no BAC/prior controls', 'ly ~ foreign + female + sex_known + C(pool) + recidivist + self_report + art59 + accident'),
               ('with BAC band and prior-DUI count', 'ly ~ foreign + female + sex_known + C(pool) + recidivist + self_report + art59 + accident + C(bac_bin) + C(n_prior)'),
               ('plus vehicle, injury, education, economic status', 'ly ~ foreign + female + sex_known + C(pool) + recidivist + self_report + art59 + accident + C(bac_bin) + C(n_prior) + C(vehicle) + injury + C(edu_c) + C(econ_c)')):
    m = smf.ols(f, data=d).fit(cov_type='cluster', cov_kwds={'groups': pd.factorize(d['judge_id'])[0]})
    res[lab] = {k: {'pct': 100 * (math.exp(m.params[k]) - 1), 'se_log': float(m.bse[k])} for k in ('foreign', 'female')}
    print(lab, res[lab], 'n', int(m.nobs))
print('foreign share prior DUI', d.groupby('foreign')['n_prior'].mean().to_dict(), 'bac', d.groupby('foreign')['bac'].mean().to_dict())
json.dump(res, open(OUT, 'w'), ensure_ascii=False)
