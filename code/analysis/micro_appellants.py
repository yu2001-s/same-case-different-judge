"""Second pass over district criminal files: appellants and defendant outcome for district appellate cases (簡上 etc.).

micro_appellants.py MICRO_ROOT OUT_PARQUET
District defendant rows end with 被告終結情形, 上訴人別(1), 上訴人別(2) (fields 70-72; one later in 2023+ files).
"""
import os, re, sys, glob
from multiprocessing import Pool
import pandas as pd

ROOT, OUT = sys.argv[1], sys.argv[2]

def dec(b):
    try:
        return b.decode('utf-8')
    except UnicodeDecodeError:
        return b.decode('cp950', errors='replace')

def ival(v):
    try:
        return int(float((v or '').strip()))
    except ValueError:
        return None

def parse(path):
    code = re.search(r'\.([A-Z]{3})M\.刑事訴訟\.txt$', path)
    if not code or not (code.group(1).endswith('D') or code.group(1).endswith('E')):
        return []
    rows = []
    for rec in dec(open(path, 'rb').read()).split('#'):
        lines = [l.rstrip('\r') for l in rec.strip().split('\n') if l.strip()]
        if not lines or not lines[0].startswith('0!'):
            continue
        c = lines[0].split('!')
        if len(c) < 17 or '上' not in c[3] or '抗' in c[3]:
            continue
        di = -1
        for l in lines[1:]:
            f = l.split('!')
            if f[0] != '1':
                continue
            di += 1
            f = [v.strip() for v in f]
            while f and f[-1] == '':
                f.pop()
            tail = [v for v in f[66:] if v]
            apps = '|'.join(v for v in tail if v in ('檢察官', '被告', '自訴人', '輔佐人', '代理人', '告訴人'))
            outc = next((v for v in tail if v not in ('檢察官', '被告', '自訴人', '輔佐人', '代理人', '告訴人', '0', '1')), '')
            rows.append({'court': c[1], 'jyear': ival(c[2]), 'jcase': c[3], 'jno': ival(c[4]), 'def_idx': di,
                         'appellants': apps, 'def_outcome': outc, 'tag': os.path.basename(path).split('.')[0]})
    return rows

if __name__ == '__main__':
    files = sorted(glob.glob(os.path.join(ROOT, 'dl_*', '**', '*M.刑事訴訟.txt'), recursive=True))
    out = []
    with Pool(4) as p:
        for r in p.imap_unordered(parse, files, chunksize=20):
            out += r
    df = pd.DataFrame(out).sort_values('tag').drop_duplicates(['court', 'jyear', 'jcase', 'jno', 'def_idx'], keep='last')
    df.to_parquet(OUT, index=False)
    print(len(df), df['appellants'].value_counts().head(8).to_dict(), df['def_outcome'].value_counts().head(8).to_dict())
