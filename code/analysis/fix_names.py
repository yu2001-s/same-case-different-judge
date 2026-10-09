"""Repair judge names that the Big5 microdata files could not encode (rare characters became '�').

fix_names.py DATA_DIR OUT_JSON
For each (court, garbled name) in frame.parquet, fetch one of that judge's single-judge judgments from the public
FJUD site, read the signing judge's name, and keep it only if it agrees with every readable character of the
garbled name. Writes a {court|garbled: correct} map.
"""
import sys, os, re, json, html, urllib.parse
import pandas as pd
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scraper'))
import fj

D_DIR, OUT = sys.argv[1], sys.argv[2]
F = pd.read_parquet(os.path.join(D_DIR, 'frame.parquet'), columns=['judge', 'court', 'jid', 'date'])
bad = F[~F['judge'].str.fullmatch(r'[一-鿿]{2,4}')]
s = fj.Session(delay=1.0)
fixmap = json.load(open(OUT)) if os.path.exists(OUT) else {}
for (court, name), g in bad.groupby(['court', 'judge']):
    key = f'{court}|{name}'
    if fixmap.get(key):
        continue
    got, seen = None, []
    for jid in g.sort_values('date', ascending=False)['jid'].head(4):
        try:
            _, page = s.get(fj.BASE + 'data.aspx?ty=JD&id=' + urllib.parse.quote(jid, safe=''))
        except Exception as e:
            print('ERR', jid, e); continue
        t = html.unescape(re.sub(r'<[^>]+>', '', page))
        cands = re.findall(r'法[\s　]*官[\s　]+([一-鿿\U00020000-\U0002ffff]{2,8})', t)
        cands = [re.split(r'以上|上列|如不|中華|本件|附錄|正本', c)[0] for c in cands]
        cands = [c for c in cands if 2 <= len(c) <= 4]
        if len(set(cands)) == 1:          # single-judge judgment: the one signing judge is the assigned judge
            seen.append(cands[0])
        if len(seen) >= 2:
            got = seen[0] if seen[0] == seen[1] else None
            break
    fixmap[key] = got
    print(court, name, '->', got, flush=True)
    json.dump(fixmap, open(OUT, 'w'), ensure_ascii=False, indent=0)
