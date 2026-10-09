"""Candidate table from the Central Election Commission vote data (kiang/db.cec.gov.tw mirror) and a given-name
gender model trained on candidates' recorded sex.

cec_build.py VOTEDATA_DIR OUT_DIR
Writes OUT_DIR/candidates.parquet and OUT_DIR/name_gender.json (character log-likelihood ratios + held-out accuracy).
"""
import sys, os, glob, csv, re, json, math, random
from collections import Counter, defaultdict
import pandas as pd

VD, OUTD = sys.argv[1], sys.argv[2]
os.makedirs(OUTD, exist_ok=True)

def read(p):
    with open(p, encoding='utf-8-sig', errors='replace') as f:
        return [[v.strip().lstrip("'") for v in r] for r in csv.reader(f)]

rows = []
for cand in glob.glob(os.path.join(VD, '**', 'elcand.csv'), recursive=True):
    d = os.path.dirname(cand)
    rel = os.path.relpath(d, VD)
    m = re.match(r'(\d{4})', rel)
    if not m:
        continue
    year = int(m.group(1))
    party = {r[0]: r[1] for r in read(os.path.join(d, 'elpaty.csv')) if len(r) >= 2}
    base = {}
    for r in read(os.path.join(d, 'elbase.csv')):
        if len(r) >= 6:
            base[tuple(r[:5])] = r[5]
    for r in read(cand):
        if len(r) < 15:
            continue
        county = base.get((r[0], r[1], '00', '000', '0000')) or base.get((r[0], '000', '00', '000', '0000')) or ''
        town = base.get((r[0], r[1], '00', r[3], '0000'), '') if r[3] not in ('000', '') else ''
        rows.append({'election': rel.split(os.sep)[0], 'office': rel.split(os.sep)[-1], 'year': year, 'county': county, 'town': town,
                     'district': r[2], 'name': r[6], 'party': party.get(r[7], r[7]), 'sex': r[8], 'birth': r[9],
                     'elected': r[14] in ('*', '!'), 'incumbent': r[13] == 'Y'})
C = pd.DataFrame(rows)
C['name_cjk'] = C['name'].map(lambda s: ''.join(ch for ch in s if '一' <= ch <= '鿿'))
C.to_parquet(os.path.join(OUTD, 'candidates.parquet'), index=False)
print(len(C), C['election'].nunique(), C['party'].value_counts().head(8).to_dict(), C['sex'].value_counts().to_dict())

# ---- given-name gender model
COMPOUND = {'歐陽', '司馬', '上官', '諸葛', '張簡', '范姜', '東方', '司徒', '夏侯', '皇甫', '公孫', '慕容', '長孫', '令狐', '端木', '尉遲'}
def given(n):
    n = ''.join(ch for ch in n if '一' <= ch <= '鿿')
    if len(n) == 4 and n[:2] in COMPOUND:
        return n[2:]
    if len(n) == 4:            # 冠夫姓 (husband's surname + own surname + given name) is the common 4-character case
        return n[2:]
    if len(n) in (2, 3):
        return n[1:]
    return None
P = C[C['sex'].isin(['1', '2'])].drop_duplicates(['name_cjk', 'birth'])
P = P.assign(g=P['name_cjk'].map(given)).dropna(subset=['g'])
P['fem'] = (P['sex'] == '2').astype(int)
random.seed(1)
idx = list(range(len(P))); random.shuffle(idx)
cut = int(0.8 * len(P))
tr, te = P.iloc[idx[:cut]], P.iloc[idx[cut:]]

def fit(df):
    cnt = {0: defaultdict(Counter), 1: defaultdict(Counter)}
    tot = Counter(df['fem'])
    for g, f in zip(df['g'], df['fem']):
        for pos, ch in enumerate(g[-2:].rjust(2, '_')):
            cnt[f][pos][ch] += 1
    llr = {}
    for pos in (0, 1):
        chars = set(cnt[0][pos]) | set(cnt[1][pos])
        for ch in chars:
            a, b = cnt[1][pos][ch] + 0.5, cnt[0][pos][ch] + 0.5
            llr[f'{pos}{ch}'] = math.log(a / (tot[1] + 0.5 * len(chars))) - math.log(b / (tot[0] + 0.5 * len(chars)))
    return llr

def score(llr, g):
    g = g[-2:].rjust(2, '_')
    return sum(llr.get(f'{pos}{ch}', 0.0) for pos, ch in enumerate(g))   # balanced prior (log odds 0)

llr = fit(tr)
te = te.assign(s=[score(llr, g) for g in te['g']])
res = {}
for thr in (1.0, 2.0, 3.0):
    sel = te[te['s'].abs() >= thr]
    acc = ((sel['s'] > 0).astype(int) == sel['fem']).mean()
    acc_f = ((sel[sel['fem'] == 1]['s'] > 0)).mean(); acc_m = ((sel[sel['fem'] == 0]['s'] < 0)).mean()
    res[str(thr)] = {'coverage': float(len(sel) / len(te)), 'accuracy': float(acc), 'recall_f': float(acc_f), 'recall_m': float(acc_m)}
print('held-out', res, 'train n', len(tr), 'female share', round(P['fem'].mean(), 3))
json.dump({'llr': fit(P), 'heldout': res, 'n_train': int(len(P)), 'female_share': float(P['fem'].mean())},
          open(os.path.join(OUTD, 'name_gender.json'), 'w'), ensure_ascii=False)
