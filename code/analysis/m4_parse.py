"""Module 4: link each election-offence judgment to the candidate it was meant to help, and that candidate's party.

m4_parse.py RAWDIR DATA_DIR CEC_DIR OUT_PARQUET
For each judgment text, every candidate of the matching election (from the microdata 選舉類別 field, else elections
in the three years before the judgment) in the court's counties whose full name occurs in the text is scored by how
often it appears near campaign words (候選人, 支持, 投票, 當選, 參選, 競選, 助選, 樁腳, 拉票). The top-scoring
candidate is taken as the beneficiary. Candidate names are used only for matching and are not written out.
"""
import sys, os, re, glob, html
import pandas as pd

RAW, D_DIR, CEC, OUT = sys.argv[1:5]
COUNTY = {'臺北': ['臺北市'], '士林': ['臺北市', '新北市'], '新北': ['新北市'], '桃園': ['桃園市', '桃園縣'], '新竹': ['新竹縣', '新竹市'],
          '苗栗': ['苗栗縣'], '臺中': ['臺中市'], '南投': ['南投縣'], '彰化': ['彰化縣'], '雲林': ['雲林縣'], '嘉義': ['嘉義縣', '嘉義市'],
          '臺南': ['臺南市'], '高雄': ['高雄市'], '橋頭': ['高雄市'], '屏東': ['屏東縣'], '臺東': ['臺東縣'], '花蓮': ['花蓮縣'],
          '宜蘭': ['宜蘭縣'], '基隆': ['基隆市', '新北市'], '澎湖': ['澎湖縣'], '金門': ['金門縣'], '連江': ['連江縣']}
ROC2CEC = {101: '20120114', 103: '2014', 105: '2016', 107: '2018', 109: '2020', 111: '2022', 113: '2024'}
PRE = re.compile(r'(候選人|支持|投票給|投票予|投給|圈選|助選|為使|使其|拉票)[^，。；]{0,6}$')
POST = re.compile(r'^[^，。；]{0,4}(當選|參選|競選|拉票|之候選人|服務處|順利)')
def office_set(e):
    if not e: return None
    if '村里' in e or '代表' in e: return {'village', 'township rep'}
    if '議員' in e: return {'councillor'}
    if '立委' in e: return {'legislator'}
    if '總統' in e or '市長' in e or '縣長' in e or '鄉鎮' in e: return {'mayor/president'}
    return None

C = pd.read_parquet(os.path.join(CEC, 'candidates.parquet'))
C = C[C['name_cjk'].str.len() >= 2]
C['party_g'] = C['party'].map(lambda p: 'KMT' if p == '中國國民黨' else ('DPP' if p == '民主進步黨' else ('Independent' if '無黨籍' in p else 'Other party')))
C['ekey'] = C['election'].str[:4].replace({'2012': '20120114'})
C['ekey'] = C['election'].map(lambda e: '20120114' if e.startswith('2012') else e[:4])
C['level'] = C['office'].map(lambda o: 'village' if ('村里' in o or o == 'V1') else ('township rep' if ('代表' in o or o in ('R1', 'R2', 'R3')) else
                                   ('legislator' if '立委' in o else ('councillor' if ('議員' in o or o in ('D1', 'D2', 'prv')) else ('mayor/president' if True else '')))))
D = pd.read_parquet(os.path.join(D_DIR, 'defendants.parquet'), columns=['court', 'level', 'jid', 'election_type', 'end_date'])
et = D[D['level'] == 'district'].drop_duplicates('jid').set_index('jid')['election_type'].to_dict()

def clean(t):
    t = re.sub(r'<[^>]+>', '', t)
    t = html.unescape(t)
    return re.sub(r'\s+', '', t)

rows = []
for f in glob.glob(os.path.join(RAW, '*.html')):
    raw = open(f, encoding='utf-8', errors='replace').read()
    jid = raw.split('\n', 1)[0].strip()
    t = clean(raw.split('\n', 1)[1] if '\n' in raw else raw)
    code = jid.split(',')[0]
    court_name = next((k for k in COUNTY if k in t[:40]), None)
    counties = COUNTY.get(court_name, [])
    e = (et.get(jid) or '').strip()
    m = re.match(r'(\d{2,3})', e)
    jy = int(jid.split(',')[4][:4]) if len(jid.split(',')) > 4 else 0
    if m and int(m.group(1)) in ROC2CEC:
        ekeys = [ROC2CEC[int(m.group(1))]]
    elif m:
        ekeys = []                      # election not covered by the candidate files (pre-2012 or by-election)
    else:
        ekeys = [k for k in ROC2CEC.values() if 0 <= jy - int(k[:4]) <= 3]
    cand = C[C['ekey'].isin(ekeys) & (C['county'].isin(counties) if counties else True)]
    os_ = office_set(e)
    if os_:
        cand = cand[cand['level'].isin(os_)]
    head = t[:t.find('上列')] if '上列' in t[:600] else t[:300]
    best, scores = None, []
    names = set(cand['name_cjk'])
    found = [n for n in names if len(n) >= 2 and n in t]
    for n in found:
        pos = [mm.start() for mm in re.finditer(re.escape(n), t)]
        near = sum(1 for p in pos if PRE.search(t[max(0, p - 12): p]) or POST.search(t[p + len(n): p + len(n) + 8]))
        if len(n) < 3 and near < 2:
            continue
        scores.append((near, len(pos), n))
    scores.sort(reverse=True)
    if scores and scores[0][0] > 0:
        n = scores[0][2]
        cr = cand[cand['name_cjk'] == n].sort_values('elected', ascending=False).iloc[0]
        best = {'party': cr['party_g'], 'party_raw': cr['party'], 'office_level': cr['level'], 'cand_elected': bool(cr['elected']),
                'cand_incumbent': bool(cr['incumbent']), 'cand_is_defendant': n in head, 'cand_election': cr['election'],
                'role': 'target' if re.search(re.escape(n) + r'[^。；]{0,12}不當選|不當選[^。；]{0,6}' + re.escape(n), t) else 'beneficiary',
                'match_score': scores[0][0], 'n_matched_names': len(scores), 'fallback_no_election_type': not bool(m),
                'ambiguous': len(scores) > 1 and scores[1][0] == scores[0][0] and cand[cand['name_cjk'] == scores[1][2]]['party_g'].iloc[0] != cr['party_g'], 'runner_up_gap': scores[0][0] - (scores[1][0] if len(scores) > 1 else 0)}
    rows.append(dict({'jid': jid, 'election_type': e, 'court_name': court_name, 'text_len': len(t),
                      'masked_candidate': bool(re.search(r'候選人[^，。]{0,4}[○Ｏ〇]', t)),
                      'vote_buying': bool(re.search(r'賄賂|賄選|不正利益|買票', t)), 'acquittal_text': '無罪' in t[:1500]}, **(best or {'party': None})))
R = pd.DataFrame(rows)
R.to_parquet(OUT, index=False)
print(len(R), R['party'].value_counts(dropna=False).to_dict(), R['masked_candidate'].mean())
