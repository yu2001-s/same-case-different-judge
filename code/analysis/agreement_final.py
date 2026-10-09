"""Score the final parser against blind independent coding (re-parses each file with the current parser).

agreement_final.py WORKFLOW_OUTPUT VALIDATION_DIR RAW_DIR OUT_JSON
"""
import json, sys, re, os
import pandas as pd, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import parse as P
wf, vdir, raw, out = sys.argv[1:5]
A = pd.DataFrame(json.load(open(wf))['result']).set_index('doc')
files = pd.read_csv(os.path.join(vdir, 'parser_values.csv')).set_index('doc')['file']
def eq(x, y, tol=0):
    xn = x is None or (isinstance(x, float) and np.isnan(x)) or x == 0
    yn = y is None or (isinstance(y, float) and np.isnan(y)) or y == 0
    if xn and yn: return True
    if xn or yn: return False
    return abs(float(x) - float(y)) <= tol
rows = []
for doc, fn in files.items():
    if doc not in A.index: continue
    r = P.parse(open(os.path.join(raw, fn), encoding='utf-8').read()); a = A.loc[doc]
    prior = bool(r['prior_dui'] or (r['n_prior_dui'] or 0) > 0 or r['recidivist'])
    rows.append({
        'Breath-alcohol level': eq(r['bac'], a['bac_mg_per_l'], 0.005),
        'Prison term (months)': eq(r['prison_months'], a['prison_months']),
        'Detention (days)': eq(r['detention_days'], a['detention_days']),
        'Additional fine (NT$)': eq(r['addl_fine_ntd'], a['addl_fine_ntd']),
        'Fine-conversion rate': eq(r['conv_rate'], a['conversion_ntd_per_day']),
        'Probation (years)': eq(r['probation_years'], a['probation_years']),
        'Prior drunk-driving case': prior == bool(a['prior_dui']),
        'Repeat offender (累犯)': bool(r['recidivist']) == bool(a['recidivist']),
        'Crash in this incident': bool(r['accident']) == bool(a['accident']),
        'Vehicle type': (r['vehicle'] or 'unknown') == a['vehicle'] or (r['vehicle'] in ('e-bike',) and a['vehicle'] == 'motorcycle'),
        'Judge': (r['judge'] or '') == re.sub(r'\s', '', a['judge_name'] or ''),
        '_doc': doc, '_court': r['court_name'],
    })
D = pd.DataFrame(rows)
fields = [c for c in D.columns if not c.startswith('_')]
res = {'n': int(len(D)), 'fields': {f: float(D[f].mean()) for f in fields}, 'by_court_n': D['_court'].value_counts().to_dict(),
       'misses': {f: D.loc[~D[f], '_doc'].tolist() for f in fields if (~D[f]).any()}}
json.dump(res, open(out, 'w'), ensure_ascii=False, indent=1)
for f in fields: print(f'{f:28s} {D[f].mean():.3f}  misses: {D.loc[~D[f], "_doc"].tolist()}')
print('n', len(D), res['by_court_n'])
