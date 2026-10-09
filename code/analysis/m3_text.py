"""Module 3 (judgment-text part): foreign nationality and (name-inferred) gender of the defendant, 2024–2026.

m3_text.py BULK_PARSED_DIR DATA_DIR NAME_GENDER_JSON OUT_JSON
Single-defendant first-instance judgments from frame.parquet are matched to the bulk judgment texts by JID.
Foreign national: the defendant's name is written in Latin script or the judgment states a foreign nationality
(mainland China, Hong Kong and Macau are reported separately). Gender is inferred from the given name with a model
trained on election candidates' recorded sex (held-out accuracy ~98% where it assigns a gender); defendants whose
names are masked or not confidently classified are kept as 'unknown'. Results are aggregate only.
"""
import sys, os, glob, json, math, re
import numpy as np, pandas as pd

BP, D_DIR, NG, OUT = sys.argv[1:5]
T = pd.concat([pd.read_parquet(p) for p in sorted(glob.glob(os.path.join(BP, '*.parquet')))], ignore_index=True)
T = T.drop_duplicates('jid')
NGm = json.load(open(NG, encoding='utf-8'))
llr = NGm['llr']
COMPOUND = {'歐陽', '司馬', '上官', '諸葛', '張簡', '范姜', '東方', '司徒', '夏侯', '皇甫', '公孫', '慕容', '長孫', '令狐', '端木', '尉遲'}

def gender(raw):
    if not raw or re.search(r'[○Ｏ〇◯＊*ＡＢＣ甲乙丙丁某]|[A-Za-z]', raw):
        return 'unknown'
    n = re.split(r'[（(，,\s]', raw.strip())[0]
    n = ''.join(ch for ch in n if '一' <= ch <= '鿿')
    if len(n) not in (2, 3, 4):
        return 'unknown'
    g = n[2:] if len(n) == 4 else n[1:]
    g = g[-2:].rjust(2, '_')
    s = sum(llr.get(f'{p}{ch}', 0.0) for p, ch in enumerate(g))
    return 'female' if s >= 2 else ('male' if s <= -2 else 'unknown')

MAIN = {'大陸地區', '中國大陸', '中華人民共和國', '香港', '澳門'}
T = T[T['n_def_hdr'] == 1].copy()
T['gender'] = T['def_names'].map(gender)
if 'sex_doc' in T:                     # sex written in the charging document, where the parser captured it, wins
    sd = T['sex_doc'].fillna('')
    T['gender_src'] = np.where(sd.isin(['男', '女']), 'recorded', 'name')
    T.loc[sd == '男', 'gender'] = 'male'; T.loc[sd == '女', 'gender'] = 'female'
else:
    T['gender_src'] = 'name'
T['origin'] = np.where(T['nat_kw'].isin(MAIN) | T['mainland'], 'mainland China / HK / Macau',
                       np.where(T['latin'] | (T['nat_kw'] != ''), 'foreign national', 'Taiwanese (presumed)'))

F = pd.read_parquet(os.path.join(D_DIR, 'frame.parquet'))
D = pd.read_parquet(os.path.join(D_DIR, 'defendants.parquet'), columns=['court', 'level', 'jyear', 'jcase', 'jno', 'def_idx'])
K = ['court', 'jyear', 'jcase', 'jno']
nd = D[D['level'] == 'district'].groupby(K)['def_idx'].nunique().rename('ndef').reset_index()
F = F.merge(nd, on=K)
F = F[(F['ndef'] == 1) & (F['date'] >= '2024-01-01')]
F = F.merge(T[['jid', 'gender', 'origin', 'interp', 'gender_src']], on='jid', how='inner')
F['log_days'] = np.where(F['sentence_days'] > 0, np.log(F['sentence_days'].clip(lower=1)), np.nan)
F['custodial_i'] = np.where(F['convicted'] == 1, F['custodial'].astype(float), np.nan)
F['female'] = (F['gender'] == 'female').astype(float)
F['g_unknown'] = (F['gender'] == 'unknown').astype(float)
F['foreign'] = (F['origin'] == 'foreign national').astype(float)
F['mainland'] = (F['origin'] == 'mainland China / HK / Macau').astype(float)
print('matched', len(F), F['origin'].value_counts().to_dict(), F['gender'].value_counts().to_dict(), flush=True)

CTRL = ['rec', 'attempt_i', 'acc_i', 'm_self', 'm_confess', 'm_59', 'm_mental', 'm_minor', 'a_any', 'a_rec', 'simplified', 'indigenous', 'dv_i']
def coefs(d, y, cols):
    X = d[CTRL + cols].astype(float)
    X = pd.concat([X, pd.get_dummies(d['counsel'], prefix='c', drop_first=True, dtype=float),
                   pd.get_dummies(d['art'].astype(str) + '-' + d['art_sub'].fillna(0).astype(int).astype(str) + '-' + d['para'].fillna(0).astype(int).astype(str),
                                  prefix='s', drop_first=True, dtype=float)], axis=1)
    Xd = X - X.groupby(d['pool']).transform('mean')
    keep = [c for c in Xd.columns if Xd[c].abs().sum() > 0]
    Xm = Xd[keep].to_numpy()
    yd = (d[y] - d.groupby('pool')[y].transform('mean')).to_numpy()
    XtXi = np.linalg.pinv(Xm.T @ Xm)
    b = XtXi @ Xm.T @ yd
    e = yd - Xm @ b
    S = pd.DataFrame(Xm * e[:, None]).groupby(d['judge_key'].to_numpy()).sum().to_numpy()
    V = XtXi @ (S.T @ S) @ XtXi
    return {c: {'b': float(b[keep.index(c)]), 'se': float(math.sqrt(V[keep.index(c), keep.index(c)]))} for c in cols if c in keep}

months = sorted(os.path.basename(p)[:6] for p in glob.glob(os.path.join(BP, '*.parquet')))
R = {'months': f'{months[0][:4]}-{months[0][4:]} to {months[-1][:4]}-{months[-1][4:]} ({len(months)} months)', 'n_matched': int(len(F)), 'origin': F['origin'].value_counts().to_dict(), 'gender': F['gender'].value_counts().to_dict(),
     'name_model': NGm['heldout'], 'gender_src': F['gender_src'].value_counts().to_dict(), 'by_offence': [], 'shares': []}
for off, g in F.groupby('offence'):
    R['shares'].append({'offence': off, 'n': int(len(g)), 'foreign': float(g['foreign'].mean()), 'mainland': float(g['mainland'].mean()),
                        'female_known': float((g['gender'] == 'female').sum() / max((g['gender'] != 'unknown').sum(), 1))})
for off in ['Impaired driving', 'Theft', 'Fraud', 'Drug use', 'Money-mule (aiding laundering)', 'Money-mule (aiding fraud)', 'Assault', 'Negligent injury']:
    base = F[F['offence'] == off]
    for y in ('log_days', 'prob', 'extra_fine', 'custodial_i', 'convicted'):
        d = base[base['decided']] if y == 'convicted' else base[base[y].notna()]
        d = d[d.groupby('pool')['judge_key'].transform('nunique') >= 2]
        if len(d) < 1000 or d[y].std() == 0:
            continue
        cols = [c for c in ('foreign', 'mainland', 'female', 'g_unknown') if d[c].sum() >= 30]
        co = coefs(d, y, cols)
        R['by_offence'].append({'offence': off, 'outcome': y, 'n': int(len(d)), 'mean': float(d[y].mean()), 'n_foreign': int(d['foreign'].sum()),
                                'n_female': int(d['female'].sum()), 'coef': co})
        print(off, y, len(d), {k: (round(v['b'], 3), round(v['se'], 3)) for k, v in co.items()}, flush=True)

# does the foreign gap depend on the judge? (impaired driving, prison length; judges with enough of both)
d = F[(F['offence'] == 'Impaired driving') & F['log_days'].notna()].copy()
d = d[d.groupby('pool')['judge_key'].transform('nunique') >= 2]
X = d[CTRL].astype(float)
Xd = X - X.groupby(d['pool']).transform('mean')
keep = [c for c in Xd.columns if Xd[c].abs().sum() > 0]
yd = d['log_days'] - d.groupby('pool')['log_days'].transform('mean')
b, *_ = np.linalg.lstsq(Xd[keep].to_numpy(), yd.to_numpy(), rcond=None)
d['e'] = yd.to_numpy() - Xd[keep].to_numpy() @ b
for var, lab in (('foreign', 'foreign'), ('female', 'female')):
    sub = d if var == 'foreign' else d[d['gender'] != 'unknown']
    gg = sub.groupby(['judge_key', var])['e'].agg(['mean', 'var', 'count']).unstack()
    gg = gg[(gg[('count', 1.0)] >= 8) & (gg[('count', 0.0)] >= 30)]
    if len(gg) >= 20:
        gap = gg[('mean', 1.0)] - gg[('mean', 0.0)]
        sv = gg[('var', 1.0)] / gg[('count', 1.0)] + gg[('var', 0.0)] / gg[('count', 0.0)]
        R[f'judge_gap_{lab}'] = {'judges': int(len(gg)), 'mean_gap_pct': float(100 * (math.exp(gap.mean()) - 1)),
                                 'sd_gap_pct': float(100 * math.sqrt(max(gap.var(ddof=1) - sv.mean(), 0)))}
        print('judge gap', lab, R[f'judge_gap_{lab}'], flush=True)
json.dump(R, open(OUT, 'w'), ensure_ascii=False)
print('wrote', OUT)
