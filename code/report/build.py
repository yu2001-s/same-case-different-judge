"""Build the report page from analysis outputs.

build.py SIX_RESULTS NATIONAL_RESULTS AGREEMENT_JSON REFS_JSON OUT_HTML
Every number in the prose comes from the JSON inputs; {{key}} placeholders must all resolve.
"""
import json, re, sys, os, html

six_p, nat_p, agr_p, refs_p, out_p = sys.argv[1:6]
agr_dev_n = sys.argv[6] if len(sys.argv) > 6 else '60'
HERE = os.path.dirname(os.path.abspath(__file__))
S = json.load(open(six_p)); N = json.load(open(nat_p)); A = json.load(open(agr_p))
REFS = json.load(open(refs_p)) if os.path.exists(refs_p) else {'refs': [], 'order': []}

def f0(x): return f'{x:,.0f}'
def pct(x, d=0): return f'{x * 100:.{d}f}%'
def mo(days, d=1): return f'{days / 30:.{d}f}'
def sg(x, d=0):
    v = f'{abs(x):.{d}f}'
    return ('−' if x < 0 and float(v) != 0 else '+' if x > 0 and float(v) != 0 else '') + v
def pv(p): return '< 0.001' if p < 0.001 else f'{p:.3f}'

courts_order = ['Taipei', 'New Taipei', 'Taoyuan', 'Taichung', 'Tainan', 'Kaohsiung']
r2 = S['r2']; mx = S['mixed']
remaining = 1 - r2['pool_legal']
judge_share = mx['icc'] * remaining
decomp = [
    {'k': 'Case facts (alcohol level, record, crash, vehicle…)', 'v': r2['legal_only'], 'color': '--stack-legal', 'note': 'what the law says should matter'},
    {'k': 'Court and quarter (assignment pool)', 'v': max(0, r2['pool_legal'] - r2['legal_only']), 'color': '--stack-pool', 'light': True, 'note': 'regional and seasonal practice'},
    {'k': 'Which judge was assigned', 'v': judge_share, 'color': '--stack-judge', 'note': 'noise-corrected judge variance'},
    {'k': 'Unexplained', 'v': max(0, 1 - r2['pool_legal'] - judge_share), 'color': '--stack-rest', 'light': True, 'note': 'facts not captured, case-by-case judgment'},
]
timing_sig = sum(1 for t in S['timing'] if t['q_bh'] < 0.05)
fine_nat = N['addl_fine']
std_by_court = S['standard_case']['by_court']
nat_rng = N['lottery']
lot = S['lottery']
bal = S.get('balance', [])
bal_ok = all(b['p'] > 0.05 for b in bal)
ind = S.get('indigenous'); ind_n = N.get('indigenous')
cc = S.get('controls_compare', {})
CA = [c for c in N['court_adjusted'] if c['n'] >= 200]
mc = S.get('microdata_check', {})

V = {
    'report_date': '9 October 2026',
    'n_six_fmt': f0(S['n_sample']), 'n_nat_fmt': f0(N['n']), 'nat_courts': str(N['n_courts']),
    'n_six_judges': str(S['n_judges']), 'n_nat_judges': f0(N['n_judges']),
    'tile_icc': pct(mx['icc']), 'tile_gap': f'{lot["gap_p90_p10_days"]:.0f} days',
    'tile_fine': f'{pct(max(0, fine_nat["p10"]))} vs {pct(fine_nat["p90"])}', 'tile_timing': f'{timing_sig} of {len(S["timing"])}',
    'icc': pct(mx['icc']), 'judge_sd': f'{mx["judge_sd_days"]:.0f}', 'resid_sd': f'{mx["resid_sd_days"]:.0f}',
    'lr_p': pv(mx['lr_p']), 'f_judge': f'{r2["judge_F"]:.2f}', 'f_judge_p': pv(r2['judge_F_p']),
    'r2_legal': pct(r2['legal_only']), 'r2_pool_legal': pct(r2['pool_legal']), 'judge_share_total': pct(judge_share),
    'gap_days': f'{lot["gap_p90_p10_days"]:.0f}', 'p10_days': sg(lot['p10_blup']), 'p90_days': sg(lot['p90_blup']),
    'min_days': sg(lot['min_blup']), 'max_days': sg(lot['max_blup']),
    'n_big_judges': str(S['n_judges_big']), 'judge_min_n': str(S['judge_min_n']), 'n_cases_big': f0(S['n_cases_big']),
    'perm_ratio': f'{S["permutation"]["ratio"]:.1f}', 'perm_p': pv(S['permutation']['p_value']), 'n_perm': f0(S['permutation']['n_perm']),
    'split_r': f'{S["split_half"]["r_mean_200"]:.2f}', 'split_lo': f'{S["split_half"]["r_p05"]:.2f}', 'split_hi': f'{S["split_half"]["r_p95"]:.2f}',
    'mean_sentence_mo': mo(S['desc']['sentence_mean']), 'share_prior': pct(S['desc']['share_prior']),
    'share_prob': pct(S['desc']['share_probation'], 1), 'share_fine': pct(S['desc']['share_addl_fine']),
    'fine_p10': pct(max(0, S['addl_fine']['adj_p10'])), 'fine_p90': pct(S['addl_fine']['adj_p90']), 'fine_F': f'{S["addl_fine"]["F"]:.1f}',
    'prob_base': pct(S['probation']['base_rate'], 1), 'prob_p90': pct(S['probation']['adj_p90'], 1),
    'nat_icc': pct(N['mixed']['icc']), 'nat_sd': f'{N["mixed"]["judge_sd_days"]:.0f}', 'nat_gap': f'{nat_rng["gap"]:.0f}',
    'nat_big': str(nat_rng['n_judges_30']), 'nat_perm_ratio': f'{N["permutation"]["ratio"]:.1f}', 'nat_split': f'{N["split_half"]["r_mean"]:.2f}',
    'nat_mean_mo': mo(N['mean_days']), 'nat_fine_p10': pct(max(0, fine_nat['p10'])), 'nat_fine_p90': pct(fine_nat['p90']),
    'nat_prob_never': pct(N['probation']['share_judges_never']), 'nat_prob_base': pct(N['probation']['base'], 1),
    'nat_court_lo': CA[0]['court'], 'nat_court_lo_v': mo(CA[0]['pred_days'], 2),
    'nat_court_hi': CA[-1]['court'], 'nat_court_hi_v': mo(CA[-1]['pred_days'], 2),
    'timing_sig': str(timing_sig), 'timing_n': str(len(S['timing'])),
    'timing_sig_cap': ('None' if timing_sig == 0 else str(timing_sig)), 'timing_max': f"{max(abs(t['coef']) for t in S['timing']):.0f}",
    'mean_sentence_days': f"{S['desc']['sentence_mean']:.0f}",
    'mix_sd': f'{S["casemix"]["judge_sd_casemix_days"]:.0f}', 'mp_sd': f'{S["monthly_pools"]["judge_sd_days"]:.1f}', 'judge_sd1': f'{mx["judge_sd_days"]:.1f}',
    'bal_rows': ''.join(f'<tr><td>{html.escape(b["fact"])}</td><td>{b["F"]:.2f}</td><td>{pv(b["p"])}</td></tr>' for b in bal),
    'cc_full': f'{cc.get("judge_sd_full_controls", 0):.1f}', 'cc_min': f'{cc.get("judge_sd_minimal_controls", 0):.1f}',
    'ind_n': f0(ind['n']) if ind else '0', 'ind_coef': sg(ind['sentence'][0], 1) if ind else 'n/a',
    'ind_lo': sg(ind['sentence'][1], 1) if ind else '', 'ind_hi': sg(ind['sentence'][2], 1) if ind else '',
    'ind_prior': pct(ind['prior_share']) if ind else '', 'ind_prior_other': pct(ind['prior_share_other']) if ind else '',
    'ind_nat_n': f0(ind_n['n']), 'ind_nat_coef': sg(ind_n['coef'], 1), 'ind_nat_lo': sg(ind_n['lo'], 1), 'ind_nat_hi': sg(ind_n['hi'], 1),
    'agr_n': str(A['n']), 'agr_dev_n': agr_dev_n,
    'agr_rows': ''.join(f'<tr><td>{html.escape(k)}</td><td>{pct(v)}</td></tr>' for k, v in A['fields'].items()),
    'mc_n': f0(mc.get('n_matched', 0)), 'mc_prison': pct(mc.get('prison_months', 0), 1), 'mc_prob': pct(mc.get('probation', 0), 1),
    'mc_rec': pct(mc.get('recidivist', 0), 1), 'mc_fine': pct(mc.get('addl_fine', 0), 1), 'mc_judge': pct(mc.get('judge', 0), 1),
    'funnel_rows': ''.join(f'<tr><td>{html.escape(a)}</td><td>{f0(b)}</td></tr>' for a, b in S['funnel']),
    'nat_funnel_rows': ''.join(f'<tr><td>{html.escape(a)}</td><td>{f0(b)}</td></tr>' for a, b in N['funnel']),
    'std_desc': S['standard_case']['description'],
    'std_court_rows': ''.join(f'<tr><td>{c}</td><td>{mo(v, 2)}</td></tr>' for c, v in sorted(std_by_court.items(), key=lambda x: x[1])),
    'rob_rows': ''.join(f'<tr><td>{html.escape(k)}</td><td>{f0(v["n"])}</td><td>{v["judges"]}</td><td>{v["F"]:.2f}</td><td>{pv(v["p"])}</td></tr>' for k, v in S['robustness'].items()),
    'date_min': S['date_min'], 'date_max': S['date_max'],
}

# citations: {{cite:key1,key2}} -> numbered superscripts; unknown keys are an error
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

body = open(os.path.join(HERE, 'body.html'), encoding='utf-8').read()
findings = open(os.path.join(HERE, 'findings.html'), encoding='utf-8').read()
tpl = open(os.path.join(HERE, 'template.html'), encoding='utf-8').read()
tpl = tpl.replace('{{findings_html}}', findings).replace('{{body_html}}', body)
tpl = re.sub(r'\{\{cite:([^}]+)\}\}', cite, tpl)
refs_html = ''.join(
    f'<li id="ref-{i + 1}">{refmap[k]["html"]}</li>' for i, k in enumerate(order))
tpl = tpl.replace('{{refs_html}}', refs_html)
V['n_refs'] = str(len(order))
missing = sorted(set(re.findall(r'\{\{([a-z0-9_]+)\}\}', tpl)) - set(V))
if missing:
    raise SystemExit(f'unresolved placeholders: {missing}')
for k, v in V.items():
    tpl = tpl.replace('{{' + k + '}}', v)

data = {'six': S, 'nat': N, 'decomp': decomp, 'court_order': courts_order}
tpl = tpl.replace('/*DATA_JSON*/', json.dumps(data, ensure_ascii=False, separators=(',', ':')))
tpl = tpl.replace('/*CHARTS_JS*/', open(os.path.join(HERE, 'charts.js'), encoding='utf-8').read())
tpl = tpl.replace('/*RENDER_JS*/', open(os.path.join(HERE, 'render.js'), encoding='utf-8').read())
open(out_p, 'w', encoding='utf-8').write(tpl)
print('wrote', out_p, len(tpl) // 1024, 'KB;', len(order), 'references cited')
