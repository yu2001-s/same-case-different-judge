"""Module 1 analysis frame: first-instance, single-judge, single-charge criminal judgments 2013–2026.

m1_prep.py DATA_DIR   (reads defendants.parquet, charges.parquet; writes frame.parquet)
"""
import sys, os, json
import numpy as np, pandas as pd

D_DIR = sys.argv[1]
D = pd.read_parquet(os.path.join(D_DIR, 'defendants.parquet'))
C = pd.read_parquet(os.path.join(D_DIR, 'charges.parquet'))
key = ['court', 'jyear', 'jcase', 'jno', 'def_idx']

def offence(r):
    law, art, sub, para = r['law'], r['art'], r['art_sub'], r['para']
    acc = r['accomplice'] == 1
    if law == '刑法':
        if art == 185 and sub == 3:
            return 'Impaired driving'
        if art == 339 or (art == 339 and sub):
            return 'Money-mule (aiding fraud)' if acc else 'Fraud'
        if art in (320, 321):
            return 'Theft'
        if art == 277:
            return 'Assault'
        if art == 284:
            return 'Negligent injury'
        if art == 354:
            return 'Criminal damage'
        if art in (143, 144, 145, 146, 147, 148):
            return 'Election offences (Criminal Code)'
        if art in (309, 310):
            return 'Defamation / insult'
    if law == '洗錢防制法':
        return 'Money-mule (aiding laundering)' if acc else 'Money laundering'
    if law == '毒品危害防制條例':
        if art == 10:
            return 'Drug use'
        if art == 11:
            return 'Drug possession'
        if art in (4, 5):
            return 'Drug dealing'
    if law in ('公職人員選舉罷免法', '總統副總統選舉罷免法'):
        return 'Election offences'
    if law == '貪污治罪條例':
        return 'Corruption'
    return None

first = C[C['charge_idx'] == 0].copy()
first['offence'] = first.apply(offence, axis=1)
F = D[(D['level'] == 'district')].merge(first.drop(columns=['file_code']), on=key, how='inner')
F = F[(F['n_charges'] == 1) & F['offence'].notna()]
F = F[F['judge1'].fillna('').str.len().between(2, 4) & (F['judge2'].fillna('') == '')]          # single named judge
F = F[F['procedure'].fillna('') != '認罪協商']                                                     # plea bargains decided by agreement
F = F[F['juvenile'].fillna(0) != 1]
F = F[~F['jcase'].str.contains('上|抗|再|聲|協|國審', regex=True)]                                  # first instance only

conv_results = {'有期徒刑', '拘役', '罰金', '免除其刑'}
F['decided'] = F['result'].isin(conv_results | {'無罪'})
F['convicted'] = F['result'].isin(conv_results).astype(int)
F['custodial'] = F['result'].isin({'有期徒刑', '拘役'})
F['sentence_days'] = np.where(F['custodial'], F['prison_months'].fillna(0) * 30 + F['detention_days'].fillna(0), np.nan)
F['extra_fine'] = np.where(F['custodial'], (F['fine'].fillna(0) > 0).astype(float), np.nan)
# the microdata only record fine amounts from 2024; before that the field is blank for every case
F['extra_fine'] = np.where(pd.to_datetime(F['end_date'], errors='coerce').dt.year >= 2024, F['extra_fine'], np.nan)
F['prob'] = np.where(F['custodial'], (F['probation'] == 1).astype(float), np.nan)
F['convertible_pct'] = np.where(F['custodial'] & (F['sentence_days'] <= 180), (F['convertible'] == 1).astype(float), np.nan)

F['date'] = pd.to_datetime(F['end_date'], errors='coerce')
F = F[F['date'].between('2013-01-01', '2026-07-31')]
F['year'] = F['date'].dt.year
F['half'] = F['year'].astype(str) + 'H' + np.where(F['date'].dt.month <= 6, '1', '2')
F['quarter'] = F['date'].dt.quarter
F['pool'] = F['court'] + '|' + F['jcase'] + '|' + F['year'].astype(str) + 'Q' + F['quarter'].astype(str)
F['judge'] = F['judge1'].astype(str).map(lambda v: ''.join(v.split()).replace('\u3000', ''))
# names with characters the Big5 files could not encode, repaired from judgment signatures (fix_names.py)
fx = os.path.join(D_DIR, 'name_fix.json')
if os.path.exists(fx):
    fixmap = {k: v for k, v in json.load(open(fx, encoding='utf-8')).items() if v}
    key = F['court'] + '|' + F['judge']
    F['judge'] = key.map(fixmap).fillna(F['judge'])
F['judge_key'] = F['court'] + ':' + F['judge']

# legally relevant controls available in the microdata
F['rec'] = F['recidivist'].fillna(0).astype(int)
F['attempt_i'] = F['attempt'].fillna(0).astype(int)
F['acc_i'] = F['accomplice'].fillna(0).astype(int)
m = F['mitig'].fillna('')
for k, pat in [('m_self', '自首'), ('m_confess', '自白'), ('m_59', '酌減'), ('m_mental', '精神|心智'), ('m_minor', '輕微|免除')]:
    F[k] = m.str.contains(pat).astype(int)
F['a_any'] = F['aggr'].fillna('').str.len().gt(0).astype(int)
F['a_rec'] = F['aggr'].fillna('').str.contains('累犯').astype(int)
F['counsel'] = F['defense'].fillna('').replace({'': 'none'}).map(lambda v: 'legal aid' if '法律扶助' in v else ('public defender' if '公設' in v else ('retained' if '選任' in v else ('appointed' if '義務' in v else 'none'))))
F['simplified'] = F['procedure'].fillna('').str.contains('簡式').astype(int)
F['indigenous'] = F['jcase'].str.contains('原').astype(int)
F['dv_i'] = F['dv'].fillna(0).astype(int)
keep = ['court', 'jyear', 'jcase', 'jno', 'def_idx', 'jid', 'judge', 'judge_key', 'offence', 'law', 'art', 'art_sub', 'para', 'result',
        'decided', 'convicted', 'custodial', 'sentence_days', 'extra_fine', 'prob', 'convertible_pct', 'fine', 'date', 'year', 'half',
        'quarter', 'pool', 'rec', 'attempt_i', 'acc_i', 'm_self', 'm_confess', 'm_59', 'm_mental', 'm_minor', 'a_any', 'a_rec',
        'counsel', 'simplified', 'indigenous', 'dv_i', 'defense', 'procedure', 'mitig', 'aggr']
F[keep].to_parquet(os.path.join(D_DIR, 'frame.parquet'), index=False)
print(len(F))
print(F.groupby('offence').agg(n=('judge', 'size'), judges=('judge_key', 'nunique'), custodial=('custodial', 'sum'),
                               mean_days=('sentence_days', 'mean'), conv=('convicted', 'mean')).sort_values('n', ascending=False).to_string())
