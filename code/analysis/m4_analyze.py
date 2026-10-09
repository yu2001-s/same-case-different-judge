"""Module 4: party of the candidate in election-offence trials, before and after the 2016 change of government.

m4_analyze.py CASES_PARQUET DATA_DIR CEC_DIR OUT_JSON
Unit: defendant in a district first-instance election-offence judgment (2013–2026), linked to the candidate the
offence was meant to help. Questions:
 (1) prosecution intensity: is each party's share of prosecuted cases in line with its share of candidates, and did
     that change when the executive (which runs the prosecution service) changed hands in May 2016?
 (2) trial outcomes: conviction, prison length and probation by party, with court and office-level fixed effects;
 (3) appeals: how often the High Court overturns the first-instance judgment, by party.
Elections held before May 2016 were investigated under a KMT government; later ones under a DPP government.
"""
import sys, os, json, math
import numpy as np, pandas as pd
import statsmodels.formula.api as smf

CASES, D_DIR, CEC, OUT = sys.argv[1:5]
K = ['court', 'jyear', 'jcase', 'jno']
R = pd.read_parquet(CASES)
D = pd.read_parquet(os.path.join(D_DIR, 'defendants.parquet'))
CH = pd.read_parquet(os.path.join(D_DIR, 'charges.parquet'), columns=K + ['def_idx', 'charge_idx', 'law', 'art', 'result', 'prison_months', 'detention_days'])
cand = pd.read_parquet(os.path.join(CEC, 'candidates.parquet'))

R['elec_year'] = R['cand_election'].str[:4].astype(float)
R.loc[R['cand_election'].fillna('').str.startswith('2012'), 'elec_year'] = 2012
R['govt'] = np.where(R['elec_year'] <= 2016, 'KMT government (elections 2012–2016)', 'DPP government (elections 2018–2024)')
R = R[R['party'].notna() & (R['role'] == 'beneficiary') & ~R['ambiguous'].fillna(False).astype(bool)]

dd = D[(D['level'] == 'district') & D['jid'].isin(R['jid'])].copy()
el = CH[CH['law'].isin(['公職人員選舉罷免法', '總統副總統選舉罷免法']) | ((CH['law'] == '刑法') & CH['art'].isin([143, 144, 145, 146, 147, 148]))]
conv = {'有期徒刑', '拘役', '罰金', '免除其刑'}
g = el.groupby(K + ['def_idx']).agg(any_conv=('result', lambda s: s.isin(conv).any()), any_acq=('result', lambda s: (s == '無罪').any()),
                                    max_prison=('prison_months', 'max'), n_el=('result', 'size')).reset_index()
dd = dd.merge(g, on=K + ['def_idx'], how='inner')
dd = dd[dd['any_conv'] | dd['any_acq']]
dd['convicted'] = dd['any_conv'].astype(float)
dd['prison_m'] = np.where(dd['any_conv'], dd['max_prison'], np.nan)          # longest prison sentence on an election count (months)
dd['probation_i'] = np.where(dd['any_conv'], (dd['probation'] == 1).astype(float), np.nan)
dd = dd.merge(R[['jid', 'party', 'office_level', 'cand_is_defendant', 'cand_elected', 'govt', 'elec_year', 'match_score', 'fallback_no_election_type']], on='jid')
dd['n_def'] = dd.groupby('jid')['def_idx'].transform('nunique')
dd['dpp_govt'] = (dd['elec_year'] >= 2018).astype(int)
for p_, c_ in (('KMT', 'kmt_post'), ('DPP', 'dpp_post'), ('Other party', 'oth_post')):
    dd[c_] = ((dd['party'] == p_) & (dd['dpp_govt'] == 1)).astype(float)
# opposition = linked to the party that did NOT control the executive (and so the prosecution service) when the case was investigated
dd['opposition'] = (((dd['party'] == 'KMT') & (dd['dpp_govt'] == 1)) | ((dd['party'] == 'DPP') & (dd['dpp_govt'] == 0))).astype(float)
dd['ruling'] = (((dd['party'] == 'KMT') & (dd['dpp_govt'] == 0)) | ((dd['party'] == 'DPP') & (dd['dpp_govt'] == 1))).astype(float)
print('defendants', len(dd), 'cases', dd['jid'].nunique())
print(dd.groupby(['govt', 'party']).agg(n=('jid', 'size'), cases=('jid', 'nunique'), conv=('convicted', 'mean'), prison=('prison_m', 'mean'),
                                        prob=('probation_i', 'mean')).round(3).to_string())

out = {'share_fallback': float(R['fallback_no_election_type'].fillna(False).astype(bool).mean()), 'n_ambiguous_dropped': None, 'n_def': int(len(dd)), 'n_cases': int(dd['jid'].nunique()), 'match_rate': None}

# (1) prosecution intensity: case share vs candidate share, by office level and election
cand['party_g'] = cand['party'].map(lambda p: 'KMT' if p == '中國國民黨' else ('DPP' if p == '民主進步黨' else ('Independent' if '無黨籍' in p else 'Other party')))
cand['elec_year'] = cand['election'].map(lambda e: 2012 if e.startswith('2012') else int(e[:4]))
cand['level'] = cand['office'].map(lambda o: 'village' if ('村里' in o or o == 'V1') else ('township rep' if ('代表' in o or o in ('R1', 'R2', 'R3')) else
                                   ('legislator' if '立委' in o else ('councillor' if ('議員' in o or o in ('D1', 'D2', 'prv')) else 'mayor/president'))))
cases = R.drop_duplicates('jid')
inten = []
partisan = ['councillor', 'mayor/president', 'legislator', 'township rep']
for gov, yrs in (('KMT government (elections 2012–2016)', (2012, 2016)), ('DPP government (elections 2018–2024)', (2018, 2024))):
    cs = cases[cases['elec_year'].between(*yrs) & cases['office_level'].isin(partisan)]
    ca = cand[cand['elec_year'].between(*yrs) & cand['level'].isin(partisan)]
    # weight candidate shares by the office mix of prosecuted cases, so a party is compared with its share of
    # candidates in the kinds of races that generate cases
    w = cs['office_level'].value_counts(normalize=True)
    for p in ('KMT', 'DPP', 'Independent', 'Other party'):
        case_share = float((cs['party'] == p).mean()) if len(cs) else None
        cand_share = float(sum(w.get(l, 0) * (ca[ca['level'] == l]['party_g'] == p).mean() for l in w.index))
        elected_share = float(sum(w.get(l, 0) * (ca[(ca['level'] == l) & ca['elected']]['party_g'] == p).mean() for l in w.index))
        k = int((cs['party'] == p).sum()); n = len(cs)
        se = math.sqrt(case_share * (1 - case_share) / n) if n else None
        inten.append({'govt': gov, 'party': p, 'cases': k, 'n_cases': n, 'case_share': case_share, 'case_share_se': se,
                      'cand_share': cand_share, 'elected_share': elected_share,
                      'ratio_cand': case_share / cand_share if cand_share else None, 'ratio_elected': case_share / elected_share if elected_share else None})
out['intensity'] = inten
for r in inten:
    print('intensity', r['govt'][:3], r['party'], r['cases'], '/', r['n_cases'], 'case %.2f cand %.2f elected %.2f' % (r['case_share'], r['cand_share'], r['elected_share']))

# (2) trial outcomes by party, KMT vs DPP vs independent, with court and office fixed effects; interaction with government
models = {}
for y, d in (('convicted', dd), ('prison_m', dd[dd['prison_m'].notna()]), ('probation_i', dd[dd['probation_i'].notna()])):
    d = d.copy()
    d['party'] = pd.Categorical(d['party'], categories=['Independent', 'KMT', 'DPP', 'Other party'])
    f = f'{y} ~ C(party) + C(office_level) + C(court) + C(elec_year) + n_charges + cand_is_defendant + n_def'
    m = smf.ols(f, data=d).fit(cov_type='cluster', cov_kwds={'groups': pd.factorize(d['jid'])[0]})
    f2 = f'{y} ~ C(party) + kmt_post + dpp_post + oth_post + C(office_level) + C(court) + C(elec_year) + n_charges + cand_is_defendant + n_def'
    m2 = smf.ols(f2, data=d).fit(cov_type='cluster', cov_kwds={'groups': pd.factorize(d['jid'])[0]})
    pick = lambda mm, k: {'b': float(mm.params.get(k, np.nan)), 'se': float(mm.bse.get(k, np.nan)), 'p': float(mm.pvalues.get(k, np.nan))}
    # KMT minus DPP difference
    def diff(mm, a, b):
        try:
            t = mm.t_test(f'{a} - {b} = 0')
            return {'b': float(t.effect[0]), 'se': float(t.sd[0][0]), 'p': float(t.pvalue)}
        except Exception:
            return None
    models[y] = {'n': int(m.nobs), 'mean': float(d[y].mean()),
                 'KMT_vs_ind': pick(m, 'C(party)[T.KMT]'), 'DPP_vs_ind': pick(m, 'C(party)[T.DPP]'),
                 'KMT_vs_DPP': diff(m, 'C(party)[T.KMT]', 'C(party)[T.DPP]'),
                 'KMT_x_dppgovt': pick(m2, 'kmt_post'), 'DPP_x_dppgovt': pick(m2, 'dpp_post'),
                 'KMTxgov_minus_DPPxgov': diff(m2, 'kmt_post', 'dpp_post')}
    # opposition vs ruling-party-linked, among KMT/DPP-linked defendants only
    dp = d[d['party'].isin(['KMT', 'DPP'])].copy()
    f3 = f'{y} ~ opposition + C(party) + C(office_level) + C(court) + C(elec_year) + n_charges + cand_is_defendant + n_def'
    m3 = smf.ols(f3, data=dp).fit(cov_type='cluster', cov_kwds={'groups': pd.factorize(dp['jid'])[0]})
    models[y]['opposition'] = dict(pick(m3, 'opposition'), n=int(m3.nobs), cases=int(dp['jid'].nunique()))
    dq = dp[dp['match_score'] >= 2]
    m4 = smf.ols(f3, data=dq).fit(cov_type='cluster', cov_kwds={'groups': pd.factorize(dq['jid'])[0]})
    models[y]['opposition_strict_match'] = dict(pick(m4, 'opposition'), n=int(m4.nobs))
    dr = dp[~dp['fallback_no_election_type'].fillna(False).astype(bool)]
    m5 = smf.ols(f3, data=dr).fit(cov_type='cluster', cov_kwds={'groups': pd.factorize(dr['jid'])[0]})
    models[y]['opposition_known_election'] = dict(pick(m5, 'opposition'), n=int(m5.nobs))
    # KMT-DPP gap separately by government period
    for gv in (0, 1):
        dg = d[d['dpp_govt'] == gv]
        mg = smf.ols(f'{y} ~ C(party) + C(office_level) + C(court) + C(elec_year) + n_charges + cand_is_defendant + n_def', data=dg).fit(cov_type='cluster', cov_kwds={'groups': pd.factorize(dg['jid'])[0]})
        models[y][f'KMT_vs_DPP_govt{gv}'] = diff(mg, 'C(party)[T.KMT]', 'C(party)[T.DPP]')
    print(y, json.dumps(models[y], ensure_ascii=False)[:600])
out['models'] = models
out['cells'] = dd.groupby(['govt', 'party']).agg(n=('jid', 'size'), cases=('jid', 'nunique'), conv=('convicted', 'mean'), prison=('prison_m', 'mean'),
                                                 prob=('probation_i', 'mean')).reset_index().to_dict('records')

# (3) appeals: High Court judgments on these cases
H = D[(D['level'] == 'high') & D['orig_no'].notna()].copy()
H['orig_year'] = H['orig_year'].astype(int); H['orig_no'] = H['orig_no'].astype(int)
hk = H.groupby(['orig_court', 'orig_year', 'orig_case', 'orig_no']).agg(
    hc_rev=('hc_outcome', lambda s: s.fillna('').str.contains('撤銷').any()),
    hc_pros=('appellants', lambda s: s.fillna('').str.contains('檢察官').any()),
    hc_def=('appellants', lambda s: s.fillna('').str.contains('被告').any())).reset_index()
cs = dd.drop_duplicates('jid')[K + ['jid', 'party', 'govt']]
cs = cs.merge(hk, left_on=K, right_on=['orig_court', 'orig_year', 'orig_case', 'orig_no'], how='left')
cs['appealed'] = cs['hc_rev'].notna()
cs['hc_rev'] = cs['hc_rev'].fillna(False).astype(bool)
ap = cs.groupby(['party']).agg(cases=('jid', 'size'), appealed=('appealed', 'mean'),
                               reversed_if_appealed=('hc_rev', lambda s: s[cs.loc[s.index, 'appealed']].mean()),
                               pros_appeal=('hc_pros', lambda s: s.fillna(False).astype(bool).mean())).reset_index()
out['appeals'] = ap.to_dict('records')
print(ap.round(3).to_string())

def clean(o):
    if isinstance(o, dict): return {str(k): clean(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)): return [clean(v) for v in o]
    if isinstance(o, (np.integer,)): return int(o)
    if isinstance(o, (np.floating, float)): return None if math.isnan(o) or math.isinf(o) else float(o)
    if isinstance(o, (np.bool_,)): return bool(o)
    return o
json.dump(clean(out), open(OUT, 'w'), ensure_ascii=False)
print('wrote', OUT)
