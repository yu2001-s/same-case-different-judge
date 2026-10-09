"""Write docs/bibliography.md from the verified reference file produced by build_refs.py.

build_bibliography.py REFS_JSON OUT_MD
"""
import json, sys, re, html

refs = json.load(open(sys.argv[1]))
TITLES = {
    'intl-extraneous': 'Extraneous factors (timing, mood, weather, anchoring, workload): international',
    'intl-judge-identity': 'Judge identity and inter-judge disparity: international',
    'taiwan-criminal': 'Taiwan: criminal sentencing and judges',
    'taiwan-civil-admin-const': 'Taiwan: civil, administrative and constitutional courts',
    'taiwan-litigant-trust': 'Taiwan: litigant identity, representation and public trust',
    'taiwan-data': 'Taiwan: data, law and infrastructure',
    'methods': 'Research design and methods',
    'gap-1': 'Gap search: detention and other high-discretion dispositions',
    'gap-2': 'Gap search: politically salient cases and case assignment',
    'gap-3': 'Gap search: judicial careers, evaluation and discipline',
    'gap-4': 'Gap search: marginalised litigants (Indigenous, foreign, disabled defendants)',
    'gap-5': 'Gap search: consistency institutions and East Asian comparisons',
}

def strip(s):
    return html.unescape(re.sub(r'<[^>]+>', '', s or '')).strip()

out = ['# Bibliography', '',
       'Every source below was found by the literature searches and then checked by an independent reviewer against the publisher, DOI or repository record.',
       '**Confirmed**: details and finding match. **Corrected**: the work exists but a detail was wrong; the fixed details are shown, or the reviewer\'s correction note is quoted.',
       'Sources the reviewers could not confirm are listed at the end and are not cited in the report.', '']
by = {}
for r in refs['refs']:
    by.setdefault(r.get('dim') or 'other', []).append(r)
for dim in list(TITLES) + [d for d in by if d not in TITLES]:
    if dim not in by:
        continue
    out += [f'## {TITLES.get(dim, dim)}', '']
    for r in sorted(by[dim], key=lambda x: (x['authors'] or '').lower()):
        url = r.get('url') or ''
        cite = f"{r['authors']} ({r['year']}). *{r['title']}*. {r['venue']}."
        if url.startswith('http'):
            cite += f' [link]({url})'
        status = 'Confirmed' if r['verdict'] == 'confirmed' else 'Corrected'
        out.append(f'- {cite} — **{status}**')
        if r.get('finding'):
            out.append(f'  - Finding: {strip(r["finding"])[:600]}')
        if r.get('corrections'):
            out.append(f'  - Reviewer correction: {strip(r["corrections"])[:600]}')
    out.append('')
dropped = [d for d in refs.get('dropped', []) if d['verdict'] in ('unverifiable', 'likely_fabricated')]
if dropped:
    out += ['## Not confirmed (not cited)', '']
    out += [f"- {d['title']} ({d['verdict']})" for d in dropped]
open(sys.argv[2], 'w', encoding='utf-8').write('\n'.join(out) + '\n')
print('wrote', sys.argv[2], len(refs['refs']), 'sources')
