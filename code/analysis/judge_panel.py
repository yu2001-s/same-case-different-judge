"""Judge career panel: every (judge name, court, year, division) appearance in all microdata files 2013–2026.

judge_panel.py MICRO_ROOT OUT_PARQUET
Reads only case rows (control code 0) of every court file (civil, family, criminal, administrative, petty offences),
so that 'first appearance' measures time on the bench, not only time in criminal divisions.
"""
import os, re, sys, glob
from multiprocessing import Pool
from collections import Counter
import pandas as pd

ROOT, OUT = sys.argv[1], sys.argv[2]

def dec(b):
    try:
        return b.decode('utf-8')
    except UnicodeDecodeError:
        return b.decode('cp950', errors='replace')

def parse(path):
    m = re.search(r'(\d{5})\.([A-Z]{3})([A-Z])\.(.+)\.txt$', os.path.basename(path))
    if not m:
        return Counter()
    ym, code, sysc, kind = m.groups()
    year = int(ym[:3]) + 1911
    cnt = Counter()
    for rec in dec(open(path, 'rb').read()).split('#'):
        rec = rec.strip()
        if not rec.startswith('0!'):
            continue
        c = rec.split('\n', 1)[0].split('!')
        if len(c) < 9:
            continue
        court = c[1]
        ndg = sum(1 for v in c[6:9] if v.strip())
        for pos, v in enumerate(c[6:9]):
            v = v.strip().replace('　', '').replace(' ', '')
            if 2 <= len(v) <= 4:
                cnt[(v, court, code, year, kind, 'single' if ndg == 1 else 'panel', pos)] += 1
    return cnt

if __name__ == '__main__':
    files = sorted(glob.glob(os.path.join(ROOT, 'dl_*', '**', '*.txt'), recursive=True))
    tot = Counter()
    with Pool(4) as p:
        for c in p.imap_unordered(parse, files, chunksize=50):
            tot.update(c)
    df = pd.DataFrame([dict(judge=k[0], court=k[1], code=k[2], year=k[3], kind=k[4], bench=k[5], pos=k[6], n=v) for k, v in tot.items()])
    df.to_parquet(OUT, index=False)
    print(len(df), df['judge'].nunique(), df.groupby('kind')['n'].sum().to_dict())
