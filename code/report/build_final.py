"""Build the combined public report from the analysis outputs.

build_final.py RESULTS_DIR PILOT_SIX PILOT_NATIONAL PILOT_IDENTITY REFS_JSON OUT_HTML
Every number in the prose is a {{placeholder}} filled from the JSON inputs; unresolved placeholders are an error.
"""
import json, re, sys, os, html, math

RD, six_p, nat_p, pid_p, refs_p, out_p = sys.argv[1:7]
HERE = os.path.dirname(os.path.abspath(__file__))
L = lambda n: json.load(open(os.path.join(RD, n), encoding='utf-8'))
M1, RF, AP, NM, M2, M3, M3T, M4 = (L('m1_results.json'), L('m1_reform.json'), L('m1_appeals.json'), L('m1_named.json'),
                                   L('m2_results.json'), L('m3_micro.json'), L('m3_text.json'), L('m4_results.json'))
S = json.load(open(six_p)); N = json.load(open(nat_p)); PID = json.load(open(pid_p))
NGJ = L('name_gender.json')
REFS = json.load(open(refs_p, encoding='utf-8'))

def f0(x): return f'{x:,.0f}'
def f1(x): return f'{x:,.1f}'
def pc(x, d=0): return f'{x * 100:.{d}f}%'
def sg(x, d=0, unit=''):
    v = f'{abs(x):.{d}f}'
    return ('−' if x < 0 and float(v) != 0 else '+' if x > 0 and float(v) != 0 else '') + v + unit
def pv(p): return '&lt; 0.001' if p < 0.001 else f'{p:.3f}' if p < 0.1 else f'{p:.2f}'
def lpct(b): return 100 * (math.exp(b) - 1)

ZH = {'Impaired driving': '不能安全駕駛 (drunk/drugged driving)', 'Theft': '竊盜 (theft)', 'Drug use': '施用毒品 (drug use)', 'Fraud': '詐欺 (fraud)',
      'Assault': '傷害 (assault)', 'Negligent injury': '過失傷害 (negligent injury)', 'Drug possession': '持有毒品 (drug possession)',
      'Money-mule (aiding laundering)': '幫助洗錢 (money mule)', 'Money-mule (aiding fraud)': '幫助詐欺 (money mule)',
      'Defamation / insult': '妨害名譽 (defamation)', 'Criminal damage': '毀損 (criminal damage)', 'Money laundering': '洗錢 (money laundering)'}
SHORT = {'Impaired driving': 'Drunk/drugged driving', 'Money-mule (aiding laundering)': 'Money mule (laundering)',
         'Money-mule (aiding fraud)': 'Money mule (fraud)', 'Defamation / insult': 'Defamation', 'Negligent injury': 'Negligent injury'}
sh = lambda o: SHORT.get(o, o)
COURT_EN = {'臺北': 'Taipei', '士林': 'Shilin', '新北': 'New Taipei', '桃園': 'Taoyuan', '新竹': 'Hsinchu', '苗栗': 'Miaoli', '臺中': 'Taichung',
            '南投': 'Nantou', '彰化': 'Changhua', '雲林': 'Yunlin', '嘉義': 'Chiayi', '臺南': 'Tainan', '高雄': 'Kaohsiung', '橋頭': 'Ciaotou',
            '屏東': 'Pingtung', '臺東': 'Taitung', '花蓮': 'Hualien', '宜蘭': 'Yilan', '基隆': 'Keelung', '澎湖': 'Penghu', '金門': 'Kinmen', '連江': 'Lienchiang'}
cen = lambda c: COURT_EN.get(c[:2], c)

# ---------------- Module 1: judge lottery by offence
MAIN = ['Impaired driving', 'Theft', 'Drug use', 'Fraud', 'Assault', 'Negligent injury', 'Drug possession',
        'Money-mule (aiding laundering)', 'Money-mule (aiding fraud)', 'Money laundering', 'Criminal damage', 'Defamation / insult']
off_rows = []
for o in MAIN:
    oc = M1['offences'][o]['outcomes']
    s = oc.get('sentence_days')
    if not s:
        continue
    off_rows.append({'offence': o, 'label': sh(o), 'zh': ZH.get(o, ''), 'n': s['n'], 'judges': s['judges'], 'mean_days': s['mean'],
                     'tau': s['tau'], 'gap': s['two_judge_gap'], 'gap_pct': 100 * s['two_judge_gap'] / s['mean'], 'icc': s['icc'],
                     'split': s['split_half'], 'p10': s['p10'], 'p90': s['p90'],
                     'prob_icc': oc.get('prob', {}).get('icc'), 'prob_tau': oc.get('prob', {}).get('tau'), 'prob_mean': oc.get('prob', {}).get('mean'),
                     'fine_icc': oc.get('extra_fine', {}).get('icc'), 'fine_tau': oc.get('extra_fine', {}).get('tau'), 'fine_mean': oc.get('extra_fine', {}).get('mean'),
                     'conv_icc': oc.get('convicted', {}).get('icc'), 'conv_tau': oc.get('convicted', {}).get('tau'), 'conv_mean': oc.get('convicted', {}).get('mean')})
big = [r for r in off_rows if r['n'] >= 20000]
n_total = sum(M1['offences'][o]['n_all'] for o in M1['offences'])
judges_total = len({j for o in M1['judges'] for y in M1['judges'][o] for j in [r['court'] + r['judge'] for r in M1['judges'][o][y]]})
dui = M1['offences']['Impaired driving']['outcomes']; fr = M1['offences']['Fraud']['outcomes']; th = M1['offences']['Theft']['outcomes']

# reform series: case-weighted average of proportional judge SD for covered vs uncovered offences (2018 definition and 2023 definition)
ser = [r for r in RF['series'] if r['outcome'] == 'log_days']
def avg(group, yr):
    v = [r for r in ser if r['year'] == yr and r['offence'] in group]
    return sum(r['tau'] * r['n'] for r in v) / sum(r['n'] for r in v) if v else None
R2C = {'Impaired driving', 'Fraud', 'Theft', 'Assault', 'Drug use', 'Drug possession'}
UNC = {'Negligent injury', 'Criminal damage', 'Defamation / insult', 'Money laundering', 'Money-mule (aiding laundering)'}
yrs = sorted({r['year'] for r in ser})
tau_all = {(r['outcome'], r['offence'], r['year']): r for r in RF['series']}
def fixed_avg(group, years, outcome='log_days'):
    """Average spread over offences present in every one of `years`, weighted by their total cases (fixed weights)."""
    tau_of = {(o, y): r for (oc, o, y), r in tau_all.items() if oc == outcome}
    offs = [o for o in group if all((o, y) in tau_of for y in years)]
    w = {o: sum(tau_of[(o, y)]['n'] for y in years) for o in offs}
    return offs, (lambda y: sum(tau_of[(o, y)]['tau'] * w[o] for o in offs) / sum(w.values()))
c_offs, c_f = fixed_avg(R2C, yrs); u_offs, u_f = fixed_avg(UNC, yrs)
trend = [{'name': 'Covered (2023 tool)', 'color': '--s1', 'values': [{'x': y, 'y': c_f(y)} for y in yrs]},
         {'name': 'Not covered', 'color': '--s2', 'values': [{'x': y, 'y': u_f(y)} for y in yrs]}]
def prepost(d):
    pre = list(range(d['pre'][0], d['pre'][1] + 1)); post = list(range(d['post'][0], d['post'][1] + 1))
    tau_of = {(o, y): r for (oc, o, y), r in tau_all.items() if oc == d['outcome']}
    out = {}
    for lab, grp in (('cov', set(d['covered'])), ('unc', set(d['uncovered']))):
        offs, f = fixed_avg(grp, pre + post, d['outcome'])
        w = {o: sum(tau_of[(o, y)]['n'] for y in pre + post) for o in offs}
        m = lambda ys: sum(sum(tau_of[(o, y)]['tau'] for y in ys) / len(ys) * w[o] for o in offs) / sum(w.values())
        out[lab] = (m(pre), m(post), offs)
    return out
per_off = {o: [{'x': r['year'], 'y': r['tau']} for r in ser if r['offence'] == o] for o in ['Impaired driving', 'Theft', 'Fraud', 'Drug use']}
did = {(d['reform'][:4], d['outcome']): d for d in RF['did']}
d18, d23 = did[('2018', 'log_days')], did[('2023', 'log_days')]
loo23 = [r['did_pct'] for r in RF['loo'] if r['reform'].startswith('2023')]
loo18 = [r['did_pct'] for r in RF['loo'] if r['reform'].startswith('2018')]
loo23_dui = next(r for r in RF['loo'] if r['reform'].startswith('2023') and r['dropped'] == 'Impaired driving')
pp18, pp23 = prepost(d18), prepost(d23)

# appeals
aps = sorted([a for a in AP['summary'] if a['n'] >= 5000], key=lambda a: a['var_removed'])
ap_rows = [{'k': sh(a['offence']), 'v': 100 * max(a['var_removed'], 0), 'note': f"appeal rate {pc(a['appeal_rate'])}; judge SD {a['tau_first']:.1f} → {a['tau_final']:.1f} days"} for a in aps]
apd = {a['offence']: a for a in AP['summary']}
bins_ni = [b for b in AP['bins'] if b['offence'] == 'Negligent injury']
bins_th = [b for b in AP['bins'] if b['offence'] == 'Fraud']
tot_app = AP['summary']
max_removed = max(a['var_removed'] for a in aps); min_removed = min(a['var_removed'] for a in aps)

# named judges
nm_meta = {(m['offence'], m['outcome']): m for m in NM['meta']}
nd = nm_meta[('Impaired driving', 'sentence_days')]

# ---------------- Module 2
exp = M2['experience']
expd = {e['offence']: e for e in exp}
pers = M2['persistence']; cross = M2['cross_offence']; mov = M2['movers']
p4 = [p for p in pers if p['early'] != '2013–2016' or p['late'] != '2021–2024']
p8 = [p for p in pers if p['early'] == '2013–2016' and p['late'] == '2021–2024']
lvl = [abs(e['level_gap_pct']) for e in exp if e['level_gap_pct'] is not None]
sig_lvl = [e for e in exp if e['level_gap_pct'] is not None and abs(e['level_gap_pct']) > 1.96 * e['level_gap_se_pct']]

# ---------------- Module 3
bail = M3['bail']
yrb = {int(r['year']): r for r in bail['by_year']}
ind = {(r['offence'], r['outcome']): r for r in M3['indigenous']}
cou = {(r['offence'], r['outcome']): r for r in M3['counsel']}
tx = {(r['offence'], r['outcome']): r for r in M3T['by_offence']}
def tcoef(off, y, var):
    r = tx.get((off, y)); c = r and r['coef'].get(var)
    return None if not c else c
idrows = []
for off in ['Impaired driving', 'Theft', 'Fraud', 'Money-mule (aiding laundering)', 'Money-mule (aiding fraud)', 'Assault', 'Negligent injury', 'Drug use']:
    for var, lab, col in (('foreign', 'foreign national', '--s2'), ('female', 'woman', '--s1')):
        c = tcoef(off, 'log_days', var)
        nn = tx.get((off, 'log_days'), {}).get('n_foreign' if var == 'foreign' else 'n_female', 0)
        if c and nn >= 50 and c['se'] < 0.2:
            idrows.append({'term': f'{sh(off)} · {lab}', 'coef': lpct(c['b']), 'lo': lpct(c['b'] - 1.96 * c['se']), 'hi': lpct(c['b'] + 1.96 * c['se']),
                           'color': col, 'note': f'{nn:,} {"foreign" if var == "foreign" else "women"} defendants'})
for off in ['Impaired driving', 'Theft', 'Drug use', 'Fraud', 'Assault', 'Money-mule (aiding laundering)']:
    r = ind.get((off, 'log_days'))
    if r:
        b, se = r['coef']
        idrows.append({'term': f'{sh(off)} · Indigenous division', 'coef': lpct(b), 'lo': lpct(b - 1.96 * se), 'hi': lpct(b + 1.96 * se), 'color': '--s3',
                       'note': f"{r['n_ind']:,} cases in Indigenous divisions"})
fd = tcoef('Impaired driving', 'log_days', 'foreign'); fw = tcoef('Impaired driving', 'log_days', 'female')
fdp = tcoef('Impaired driving', 'prob', 'foreign'); fdf = tcoef('Impaired driving', 'extra_fine', 'foreign')
mm = tcoef('Money-mule (aiding laundering)', 'log_days', 'foreign')
thw = tcoef('Theft', 'log_days', 'female'); thwp = tcoef('Theft', 'custodial_i', 'female')
pid_full = PID['plus vehicle, injury, education, economic status']; pid_raw = PID['no BAC/prior controls']; pid_bac = PID['with BAC band and prior-DUI count']
la_th = cou[('Theft', 'log_days')]['coef']; la_mm = cou[('Money-mule (aiding laundering)', 'log_days')]['coef']

# ---------------- Module 4
inten = M4['intensity']
def it(gov, p): return next(r for r in inten if r['govt'].startswith(gov) and r['party'] == p)
party_rows = []
for gov, lab in (('KMT', 'KMT gov’t (elections 2012–16)'), ('DPP', 'DPP gov’t (elections 2018–24)')):
    for p in ('KMT', 'DPP', 'Independent'):
        r = it(gov, p)
        party_rows.append({'k': f'{p} · {lab}', 'a': 100 * r['cand_share'], 'b': 100 * r['case_share'],
                           'note': f"{r['cases']} of {r['n_cases']} cases; share of winners {pc(r['elected_share'])}"})
mods = M4['models']
opp = {y: mods[y]['opposition'] for y in mods}
oppS = {y: mods[y]['opposition_strict_match'] for y in mods}
kd = {y: mods[y]['KMT_vs_DPP'] for y in mods}
cells = M4['cells']
apm = {a['party']: a for a in M4['appeals']}

# ---------------- pilot (drunk driving deep dive)
mx = S['mixed']; lot = S['lottery']; timing_sig = sum(1 for t in S['timing'] if t['q_bh'] < 0.05)

V = {
    'report_date': '9 October 2026',
    'n_total': f0(n_total), 'n_def_rows': '2,993,332', 'years': '2013–2026',
    'n_offences': str(len(off_rows)), 'judges_total': f0(judges_total),
    'icc_lo': pc(min(r['icc'] for r in big)), 'icc_hi': pc(max(r['icc'] for r in big)),
    'dui_n': f0(dui['sentence_days']['n']), 'dui_mean': f0(dui['sentence_days']['mean']), 'dui_gap': f1(dui['sentence_days']['two_judge_gap']),
    'dui_icc': pc(dui['sentence_days']['icc']), 'dui_split': f"{dui['sentence_days']['split_half']:.2f}",
    'dui_p10': sg(dui['sentence_days']['p10'], 0), 'dui_p90': sg(dui['sentence_days']['p90'], 0),
    'dui_prob_icc': pc(dui['prob']['icc']), 'dui_prob_mean': f1(dui['prob']['mean']) + '%', 'dui_prob_tau': f1(dui['prob']['tau']),
    'dui_fine_icc': pc(dui['extra_fine']['icc']), 'fr_fine_icc': pc(fr['extra_fine']['icc']), 'fr_fine_split': f"{fr['extra_fine']['split_half']:.2f}",
    'fr_mean': f0(fr['sentence_days']['mean']), 'fr_gap': f0(fr['sentence_days']['two_judge_gap']), 'fr_icc': pc(fr['sentence_days']['icc']),
    'th_gap': f1(th['sentence_days']['two_judge_gap']), 'th_mean': f0(th['sentence_days']['mean']),
    'trend_cov': ', '.join(sh(o).lower() for o in sorted(c_offs)), 'trend_unc': ', '.join(sh(o).lower() for o in sorted(u_offs)),
    'nodisc_max': f"{max(abs(o['outcomes']['sentence_days'].get('icc_nodisc', o['outcomes']['sentence_days']['icc']) - o['outcomes']['sentence_days']['icc']) for o in M1['offences'].values() if 'sentence_days' in o['outcomes']) * 100:.1f}",
    'conv_sd_hi': f1(max(r['conv_tau'] for r in big if r.get('conv_tau') is not None)),
    'dui_fine_mean': f"{dui['extra_fine']['mean']:.0f}%", 'fr_fine_mean': f"{fr['extra_fine']['mean']:.1f}%",
    'conv_icc_lo': pc(min(r['conv_icc'] for r in big if r['conv_icc'] is not None), 1), 'conv_icc_hi': pc(max(r['conv_icc'] for r in big if r['conv_icc'] is not None), 1),
    'mule_icc': pc(M1['offences']['Money-mule (aiding fraud)']['outcomes']['sentence_days']['icc']),
    'gap_pct_lo': f0(min(r['gap_pct'] for r in big)), 'gap_pct_hi': f0(max(r['gap_pct'] for r in big)),
    'd18': sg(d18['did_pct'], 0, '%'), 'd18_p': pv(d18['p_perm']), 'd23': sg(d23['did_pct'], 0, '%'), 'd23_p': pv(d23['p_perm']),
    'd23_loo_lo': sg(min(loo23), 0, '%'), 'd23_loo_hi': sg(max(loo23), 0, '%'), 'd18_loo_lo': sg(min(loo18), 0, '%'), 'd18_loo_hi': sg(max(loo18), 0, '%'),
    'd23_cov_pre': f1(pp23['cov'][0]), 'd23_cov_post': f1(pp23['cov'][1]), 'd23_unc_pre': f1(pp23['unc'][0]), 'd23_unc_post': f1(pp23['unc'][1]),
    'd18_cov_pre': f1(pp18['cov'][0]), 'd18_cov_post': f1(pp18['cov'][1]), 'd18_unc_pre': f1(pp18['unc'][0]), 'd18_unc_post': f1(pp18['unc'][1]),
    'd18_abs': f"{abs(d18['did_pct']):.0f}%", 'd23_loo_dui_p': pv(loo23_dui['p_perm']),
    'n_perm18': str(d18['n_perm']), 'n_perm23': str(d23['n_perm']),
    'dui_tau_2013': f1(next(r['tau'] for r in M1['yearly'] if r['offence'] == 'Impaired driving' and r['year'] == 2013 and r['outcome'] == 'sentence_days')),
    'dui_tau_2025': f1(next(r['tau'] for r in M1['yearly'] if r['offence'] == 'Impaired driving' and r['year'] == 2025 and r['outcome'] == 'sentence_days')),
    'fr_mean_2013': f0(next(r['mean'] for r in M1['yearly'] if r['offence'] == 'Fraud' and r['year'] == 2013 and r['outcome'] == 'sentence_days')),
    'fr_mean_2025': f0(next(r['mean'] for r in M1['yearly'] if r['offence'] == 'Fraud' and r['year'] == 2025 and r['outcome'] == 'sentence_days')),
    'app_n': f0(sum(a['n'] for a in tot_app)), 'app_rate': pc(sum(a['appeal_rate'] * a['n'] for a in tot_app) / sum(a['n'] for a in tot_app), 1),
    'app_surv_sd_lo': pc(math.sqrt(1 - max_removed)), 'app_surv_sd_hi': pc(math.sqrt(1 - max(min_removed, 0))),
    'app_drug_removed': pc(max(apd['Drug use']['var_removed'], 0), 1), 'app_th_removed': pc(max(apd['Theft']['var_removed'], 0), 1),
    'app_surv_lo': pc(1 - max_removed), 'app_surv_hi': pc(1 - max(min_removed, 0)),
    'pid_full_abs': f"{abs(pid_full['foreign']['pct']):.0f}%",
    'app_removed_lo': pc(max(min_removed, 0)), 'app_removed_hi': pc(max_removed),
    'app_dui_removed': pc(max(apd['Impaired driving']['var_removed'], 0), 1), 'app_dui_rate': pc(apd['Impaired driving']['appeal_rate'], 1),
    'app_ni_rate': pc(apd['Negligent injury']['appeal_rate']), 'app_ni_def10': f1(100 * 10 * apd['Negligent injury']['slopes']['app_def'][0]),
    'app_ni_pros10': f1(100 * 10 * abs(apd['Negligent injury']['slopes']['app_pros'][0])),
    'app_fr_removed': pc(apd['Fraud']['var_removed']), 'app_mule_removed': pc(apd['Money-mule (aiding laundering)']['var_removed']),
    'nm_start': NM['window_start'][:4], 'nm_min': str(NM['min_cases']), 'nm_dui_judges': str(nd['judges_listed']),
    'nm_dui_hi': str(nd['flag_higher']), 'nm_dui_lo': str(nd['flag_lower']), 'nm_rows': f0(len(NM['rows'])),
    'nm_judges': f0(len({(r['court'], r['judge']) for r in NM['rows']})),
    'exp_dui_nov': f1(expd['Impaired driving']['tau_novice_pct']), 'exp_dui_exp': f1(expd['Impaired driving']['tau_exp_pct']),
    'exp_lvl_max': f1(max(lvl)), 'exp_sig_n': str(len(sig_lvl)), 'exp_n_off': str(len(exp)),
    'exp_sig_list': ', '.join(f"{sh(e['offence']).lower()} {sg(e['level_gap_pct'], 1, '%')}" for e in sig_lvl) or 'none',
    'exp_fr_nov': f1(expd['Fraud']['tau_novice_pct']), 'exp_fr_exp': f1(expd['Fraud']['tau_exp_pct']),
    'exp_ni': sg(expd['Negligent injury']['level_gap_pct'], 1, '%'),
    'p4_lo': f'{min(p["r_true"] for p in p4):.2f}', 'p4_hi': f'{max(p["r_true"] for p in p4):.2f}',
    'p8_lo': f'{min(p["r_true"] for p in p8):.2f}', 'p8_hi': f'{max(p["r_true"] for p in p8):.2f}',
    'cross_lo': f'{min(v["r_true"] for v in cross.values()):.2f}', 'cross_hi': f'{max(v["r_true"] for v in cross.values()):.2f}',
    'mov_n': str(mov['judges']), 'mov_r': f'{mov["r_true"]:.2f}', 'mov_raw': f'{mov["r_raw"]:.2f}',
    'bail_n': f0(bail['n']), 'bail_rate': pc(bail['grant_rate']), 'bail_tau': f0(bail['all']['tau_pp']), 'bail_icc': pc(bail['all']['icc']),
    'bail_perm': f1(bail['all']['perm_ratio']), 'bail_p10': sg(bail['all']['p10'], 0), 'bail_p90': sg(bail['all']['p90'], 0), 'bail_j30': str(bail['all']['judges_30']),
    'bail_panel': pc(bail['all'].get('share_panel', 0)),
    'bail_2013': pc(yrb[2013]['mean']), 'bail_2025': pc(yrb[2025]['mean']),
    'tx_n': f0(M3T['n_matched']), 'tx_foreign': f0(M3T['origin'].get('foreign national', 0)), 'tx_main': f0(M3T['origin'].get('mainland China / HK / Macau', 0)),
    'tx_months': (lambda m: f"{['January','February','March','April','May','June','July','August','September','October','November','December'][int(m[5:7]) - 1]} {m[:4]} – {['January','February','March','April','May','June','July','August','September','October','November','December'][int(m[16:18]) - 1]} {m[11:15]}")(M3T['months']),
    'kd_prison_abs': f"{abs(kd['prison_m']['b']):.1f}", 'opp_prob_abs': f"{abs(100 * opp['probation_i']['b']):.0f}",
    'tx_rec_share': pc(M3T.get('gender_src', {}).get('recorded', 0) / max(sum(M3T.get('gender_src', {}).values()), 1)),
    'ng_train': f0(NGJ['n_train']),
    'pid_full_lo': sg(100 * (math.exp(math.log(1 + pid_full['foreign']['pct'] / 100) - 1.96 * pid_full['foreign']['se_log']) - 1), 0, '%'),
    'pid_full_hi': sg(100 * (math.exp(math.log(1 + pid_full['foreign']['pct'] / 100) + 1.96 * pid_full['foreign']['se_log']) - 1), 0, '%'),
    'pid_expl': f"{100 * (1 - pid_full['foreign']['pct'] / pid_raw['foreign']['pct']):.0f}%",
    'fd': sg(lpct(fd['b']), 0, '%'), 'fd_lo': sg(lpct(fd['b'] - 1.96 * fd['se']), 0, '%'), 'fd_hi': sg(lpct(fd['b'] + 1.96 * fd['se']), 0, '%'),
    'fdp': sg(100 * fdp['b'], 1), 'fdf': sg(100 * fdf['b'], 1), 'mm_f': sg(lpct(mm['b']), 0, '%'),
    'fw': sg(lpct(fw['b']), 0, '%'), 'thw': sg(lpct(thw['b']), 0, '%'), 'thwp': sg(100 * thwp['b'], 0),
    'pid_raw': sg(pid_raw['foreign']['pct'], 0, '%'), 'pid_bac': sg(pid_bac['foreign']['pct'], 0, '%'), 'pid_full': sg(pid_full['foreign']['pct'], 0, '%'),
    'pid_w_full': sg(pid_full['female']['pct'], 0, '%'), 'pid_foreign_n': f0(PID['foreign_n']),
    'ng_acc': pc(PID['name_model_validation']['2']['accuracy'], 1), 'ng_cov': pc(PID['name_model_validation']['2']['coverage']),
    'ng_n': f0(PID['n_validation']), 'ng_cand_acc': pc(M3T['name_model']['2.0']['accuracy'], 1),
    'jg_f': (sg(M3T['judge_gap_foreign']['sd_gap_pct'], 0, '%').lstrip('+') if 'judge_gap_foreign' in M3T else 'n/a'),
    'jg_f_n': str(M3T.get('judge_gap_foreign', {}).get('judges', 0)),
    'ind_dui': sg(lpct(ind[('Impaired driving', 'log_days')]['coef'][0]), 1, '%'), 'ind_drug': sg(lpct(ind[('Drug use', 'log_days')]['coef'][0]), 1, '%'),
    'ind_assault': sg(lpct(ind[('Assault', 'log_days')]['coef'][0]), 0, '%'),
    'ind_jsd': f1(M3['indigenous_judge']['sd_gap_pct']), 'ind_jn': str(M3['indigenous_judge']['judges']),
    'la_th': sg(lpct(la_th['legal aid'][0]), 0, '%'), 'pd_th': sg(lpct(la_th['public defender'][0]), 0, '%'), 'rt_th': sg(lpct(la_th['retained'][0]), 0, '%'),
    'la_mm': sg(lpct(la_mm['legal aid'][0]), 0, '%'),
    'pol_n': f0(M4['n_def']), 'pol_cases': f0(M4['n_cases']), 'pol_all': '2,283',
    'kmt_case_k': pc(it('KMT', 'KMT')['case_share']), 'kmt_cand_k': pc(it('KMT', 'KMT')['cand_share']),
    'kmt_case_d': pc(it('DPP', 'KMT')['case_share']), 'kmt_cand_d': pc(it('DPP', 'KMT')['cand_share']),
    'dpp_case_k': pc(it('KMT', 'DPP')['case_share']), 'dpp_cand_k': pc(it('KMT', 'DPP')['cand_share']),
    'dpp_case_d': pc(it('DPP', 'DPP')['case_share']), 'dpp_cand_d': pc(it('DPP', 'DPP')['cand_share']),
    'kmt_elec_k': pc(it('KMT', 'KMT')['elected_share']), 'kmt_elec_d': pc(it('DPP', 'KMT')['elected_share']),
    'dpp_elec_k': pc(it('KMT', 'DPP')['elected_share']), 'dpp_elec_d': pc(it('DPP', 'DPP')['elected_share']),
    'pol_n_k': str(it('KMT', 'KMT')['n_cases']), 'pol_n_d': str(it('DPP', 'KMT')['n_cases']),
    'kd_conv': sg(100 * kd['convicted']['b'], 1), 'kd_conv_se': f1(100 * kd['convicted']['se']),
    'kd_conv_lo': sg(100 * (kd['convicted']['b'] - 1.96 * kd['convicted']['se']), 0), 'kd_conv_hi': sg(100 * (kd['convicted']['b'] + 1.96 * kd['convicted']['se']), 0),
    'kd_prison_g0': sg(mods['prison_m']['KMT_vs_DPP_govt0']['b'], 1), 'kd_prison_g1': sg(mods['prison_m']['KMT_vs_DPP_govt1']['b'], 1),
    'kd_prison_int_p': pv(mods['prison_m']['KMTxgov_minus_DPPxgov']['p']),
    'opp_prob_k': sg(100 * mods['probation_i']['opposition_known_election']['b'], 0), 'opp_prob_k_p': pv(mods['probation_i']['opposition_known_election']['p']),
    'pol_fallback': pc(M4['share_fallback']),
    'opp_prob_adj': pv(min(1, 3 * opp['probation_i']['p'])), 'opp_prob_s_adj': pv(min(1, 3 * oppS['probation_i']['p'])),
    'opp_prob_k_adj': pv(min(1, 3 * mods['probation_i']['opposition_known_election']['p'])),
    'kmt_post_prob': sg(100 * mods['probation_i']['KMT_x_dppgovt']['b'], 0), 'kmt_post_prob_p': pv(mods['probation_i']['KMT_x_dppgovt']['p']),
    'prob_rule_k': pc(next(c['prob'] for c in cells if c['govt'].startswith('KMT') and c['party'] == 'KMT')), 'prob_opp_k': pc(next(c['prob'] for c in cells if c['govt'].startswith('KMT') and c['party'] == 'DPP')),
    'prob_rule_d': pc(next(c['prob'] for c in cells if c['govt'].startswith('DPP') and c['party'] == 'DPP')), 'prob_opp_d': pc(next(c['prob'] for c in cells if c['govt'].startswith('DPP') and c['party'] == 'KMT')),
    'kd_prison': sg(kd['prison_m']['b'], 1), 'kd_prison_p': pv(kd['prison_m']['p']),
    'dpp_ind_prison': sg(mods['prison_m']['DPP_vs_ind']['b'], 1), 'dpp_ind_p': pv(mods['prison_m']['DPP_vs_ind']['p']),
    'opp_conv': sg(100 * opp['convicted']['b'], 0), 'opp_conv_p': pv(opp['convicted']['p']),
    'opp_prison': sg(opp['prison_m']['b'], 1), 'opp_prison_p': pv(opp['prison_m']['p']),
    'opp_prob': sg(100 * opp['probation_i']['b'], 0), 'opp_prob_p': pv(opp['probation_i']['p']),
    'opp_prob_s': sg(100 * oppS['probation_i']['b'], 0), 'opp_prob_s_p': pv(oppS['probation_i']['p']), 'opp_cases': str(opp['convicted']['cases']),
    'ap_kmt': pc(apm['KMT']['reversed_if_appealed']), 'ap_dpp': pc(apm['DPP']['reversed_if_appealed']), 'ap_ind': pc(apm['Independent']['reversed_if_appealed']),
    'pil_n': f0(S['n_sample']), 'pil_icc': pc(mx['icc']), 'pil_gap': f0(lot['gap_p90_p10_days']), 'pil_timing': f'{timing_sig} of {len(S["timing"])}',
    'pil_sd': f0(mx['judge_sd_days']), 'pil_mix': f0(S['casemix']['judge_sd_casemix_days']),
    'pil_perm': f1(S['permutation']['ratio']), 'pil_split': f"{S['split_half']['r_mean_200']:.2f}",
    'nat_icc': pc(N['mixed']['icc']), 'nat_n': f0(N['n']),
}

# offence table html
V['off_table'] = ''.join(
    f"<tr><td>{html.escape(r['label'])}<br><span class='zh-s'>{html.escape(r['zh'].split(' ')[0])}</span></td><td>{f0(r['n'])}</td><td>{f0(r['mean_days'])}</td>"
    f"<td>{f1(r['gap'])} <span class='muted'>({f0(r['gap_pct'])}%)</span></td><td>{pc(r['icc'], 1)}</td><td>{'' if r['split'] is None else format(r['split'], '.2f')}</td>"
    f"<td>{'' if r['prob_icc'] is None else pc(r['prob_icc'], 1)}</td><td>{'' if r['fine_icc'] is None or r['fine_mean'] < 1 else pc(r['fine_icc'], 1)}</td>"
    f"<td>{'' if r['conv_icc'] is None else pc(r['conv_icc'], 1)}</td></tr>" for r in off_rows)
V['did_table'] = ''.join(
    f"<tr><td>{html.escape(d['reform'])}</td><td>{'Prison length' if d['outcome'] == 'log_days' else 'Probation'}</td><td>{', '.join(sh(c) for c in d['covered'])}</td>"
    f"<td>{f1(prepost(d)['cov'][0])} → {f1(prepost(d)['cov'][1])}</td><td>{f1(prepost(d)['unc'][0])} → {f1(prepost(d)['unc'][1])}</td><td>{sg(d['did_pct'], 0, '%')}</td><td>{pv(d['p_perm'])}</td></tr>"
    for d in RF['did'] if d['outcome'] == 'log_days' or True)
V['pol_table'] = ''.join(
    f"<tr><td>{html.escape(c['govt'].split(' (')[0])}</td><td>{c['party']}</td><td>{c['n']}</td><td>{c['cases']}</td><td>{pc(c['conv'])}</td>"
    f"<td>{'' if c['prison'] is None else f1(c['prison'])}</td><td>{'' if c['prob'] is None else pc(c['prob'])}</td></tr>"
    for c in sorted(cells, key=lambda c: (c['govt'][:3] != 'KMT', ['KMT', 'DPP', 'Independent', 'Other party'].index(c['party']))))
V['cou_table'] = ''.join(
    f"<tr><td>{sh(o)}</td>" + ''.join(f"<td>{sg(lpct(cou[(o, 'log_days')]['coef'][k][0]), 0, '%')}</td>" for k in ('public defender', 'legal aid', 'retained')) +
    f"<td>{pc(1 - cou[(o, 'log_days')]['share'].get('none', 0))}</td></tr>"
    for o in ['Impaired driving', 'Theft', 'Drug use', 'Fraud', 'Money-mule (aiding laundering)', 'Negligent injury'])

# citations
order = []
refmap = {r['key']: r for r in REFS['refs']}
def cite(m):
    keys = [k.strip() for k in m.group(1).split(',')]
    nums = []
    for k in keys:
        if k not in refmap or not refmap[k].get('ok_for_report', True):
            raise SystemExit(f'unknown, unverified or uncorrected citation key: {k}')
        if k not in order:
            order.append(k)
        nums.append(order.index(k) + 1)
    return '<sup class="c">' + ','.join(f'<a href="#ref-{n}">{n}</a>' for n in sorted(set(nums))) + '</sup>'

tpl = open(os.path.join(HERE, 'final_template.html'), encoding='utf-8').read()
tpl = tpl.replace('{{body_html}}', open(os.path.join(HERE, 'final_body.html'), encoding='utf-8').read())
tpl = re.sub(r'\{\{cite:([^}]+)\}\}', cite, tpl)
tpl = tpl.replace('{{refs_html}}', ''.join(f'<li id="ref-{i + 1}">{refmap[k]["html"]}</li>' for i, k in enumerate(order)))
V['n_refs'] = str(len(order))
missing = sorted(set(re.findall(r'\{\{([a-z0-9_]+)\}\}', tpl)) - set(V))
if missing:
    raise SystemExit(f'unresolved placeholders: {missing}')
for k, v in V.items():
    tpl = tpl.replace('{{' + k + '}}', v)
tpl = tpl.replace('p = &lt; ', 'p &lt; ')

named = [dict(r, court_en=cen(r['court'])) for r in NM['rows']]
DATA = {'off': off_rows, 'trend': trend, 'per_off': per_off, 'ap_rows': ap_rows, 'bins_ni': bins_ni, 'bins_fr': bins_th,
        'named': named, 'named_meta': NM['meta'], 'exp': exp, 'pers': pers, 'cross': cross, 'movers': M2.get('movers_points', []),
        'idrows': idrows, 'party_rows': party_rows, 'bail_year': bail['by_year'], 'tenure': M2['tenure_curve'],
        'labels': {o: sh(o) for o in ZH}}
tpl = tpl.replace('/*DATA_JSON*/', json.dumps(DATA, ensure_ascii=False, separators=(',', ':')))
tpl = tpl.replace('/*CHARTS_JS*/', open(os.path.join(HERE, 'charts.js'), encoding='utf-8').read() + '\n' +
                  open(os.path.join(HERE, 'charts_extra.js'), encoding='utf-8').read())
tpl = tpl.replace('/*RENDER_JS*/', open(os.path.join(HERE, 'final_render.js'), encoding='utf-8').read())
open(out_p, 'w', encoding='utf-8').write(tpl)
print('wrote', out_p, len(tpl) // 1024, 'KB;', len(order), 'references cited')
