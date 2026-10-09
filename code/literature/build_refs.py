"""Build refs.json (key -> formatted citation) from the research workflow's sweep and verification results.

build_refs.py SWEEPS_OR_WORKFLOW_RESULT OUT_JSON [--all] [--overrides overrides.json]
Default: keep only sources whose verdict is 'confirmed' or 'corrected'. Corrected sources must have an entry in the
overrides file (field fixes applied by hand after reading the verifier's note); otherwise they are dropped and listed.
"""
import json, sys, html

src, out = sys.argv[1], sys.argv[2]
keep_all = '--all' in sys.argv
ov = {}
if '--overrides' in sys.argv:
    ov = json.load(open(sys.argv[sys.argv.index('--overrides') + 1]))

data = json.load(open(src))
if 'sources' in data and isinstance(data['sources'], list):      # workflow return value
    sources = data['sources']
else:                                                              # raw sweeps.json {dim: {sources: [...]}}
    sources = [dict(s, dim=d, verdict='unchecked') for d, v in data.items() for s in v['sources']]

def fmt(s):
    a = html.escape(s.get('authors', '').strip().rstrip('.'))
    t = html.escape(s.get('title', '').strip().rstrip('.'))
    v = html.escape(s.get('venue', '').strip().rstrip('.'))
    y = html.escape(str(s.get('year', '')).strip())
    url = s.get('evidence_url') or s.get('url') or ''
    link = f' <a href="{html.escape(url)}" target="_blank" rel="noopener">link</a>' if url.startswith('http') else ''
    return f'{a} ({y}). {t}. <i>{v}</i>.{link}'

refs, dropped, needs_fix = {}, [], []
for s in sources:
    k = s['id']
    if k in ov:
        s = dict(s, **ov[k])
    verdict = s.get('verdict', 'unchecked')
    ok = keep_all or verdict in ('confirmed', 'corrected')
    if verdict == 'corrected' and k not in ov and not keep_all:
        needs_fix.append({'key': k, 'dim': s.get('dim'), 'title': s.get('title'), 'corrections': s.get('corrections'), 'note': s.get('verify_note')})
    if not ok:
        dropped.append({'key': k, 'verdict': verdict, 'title': s.get('title')})
        continue
    if k in refs and (refs[k]['verdict'] == 'confirmed' or (refs[k]['ok_for_report'] and verdict != 'confirmed')):
        continue
    refs[k] = {'key': k, 'html': fmt(s), 'verdict': verdict, 'ok_for_report': keep_all or verdict == 'confirmed' or k in ov,
               'corrections': s.get('corrections', '') if k not in ov else '', 'dim': s.get('dim'), 'year': str(s.get('year', '')),
               'authors': s.get('authors', ''), 'title': s.get('title', ''), 'venue': s.get('venue', ''),
               'url': s.get('evidence_url') or s.get('url') or '', 'finding': s.get('finding', ''), 'jurisdiction': s.get('jurisdiction', ''),
               'factor': s.get('factor', ''), 'status': s.get('status', '')}
json.dump({'refs': list(refs.values()), 'dropped': dropped, 'needs_fix': needs_fix}, open(out, 'w'), ensure_ascii=False, indent=1)
print(f'kept {len(refs)}, dropped {len(dropped)}, corrected-without-override {len(needs_fix)}')
