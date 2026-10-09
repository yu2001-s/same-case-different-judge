"""Parse every Judicial Yuan terminated-case microdata archive (2013–2026) into analysis tables.

micro_all.py MICRO_ROOT OUT_DIR
Writes OUT_DIR/defendants.parquet (one row per case x defendant, criminal litigation, district + summary + High
courts) and OUT_DIR/charges.parquet (one row per charge). Handles UTF-8 (2021+) and CP950/Big5 (2013–2020) files,
and the extra defendant field added in 2023 (73 vs 72 fields).
"""
import os, re, sys, glob
from multiprocessing import Pool
import pandas as pd

ROOT, OUT = sys.argv[1], sys.argv[2]
os.makedirs(OUT, exist_ok=True)
HIGH = {'TPH', 'TCH', 'TNH', 'KSH', 'HLH', 'KMH'}

def dec(b):
    try:
        return b.decode('utf-8')
    except UnicodeDecodeError:
        return b.decode('cp950', errors='replace')

def ival(v):
    v = (v or '').strip()
    try:
        return int(float(v))
    except ValueError:
        return None

def yymm(v):
    v = (v or '').strip()
    if not v.isdigit():
        return None
    v = v.zfill(4)
    return int(v[:2]) * 12 + int(v[2:])

def date3(y, m, d):
    y, m, d = ival(y), ival(m), ival(d)
    if not y or not m or not d:
        return None
    return f'{y + 1911:04d}-{m:02d}-{d:02d}'

def parse_file(path):
    code = re.search(r'\.([A-Z]{3})M\.刑事訴訟\.txt$', path)
    if not code:
        return [], []
    code = code.group(1)
    level = 'high' if code in HIGH else ('district' if code.endswith('D') or code.endswith('E') else 'other')
    if level == 'other':
        return [], []
    month_tag = os.path.basename(path).split('.')[0]
    text = dec(open(path, 'rb').read())
    drows, crows = [], []
    for rec in text.split('#'):
        lines = [l.rstrip('\r') for l in rec.strip().split('\n') if l.strip()]
        if not lines or not lines[0].startswith('0!'):
            continue
        c = lines[0].split('!')
        if len(c) < 27:
            continue
        case = {'file_code': code, 'level': level, 'tag': month_tag, 'court': c[1], 'jyear': ival(c[2]), 'jcase': c[3],
                'jno': ival(c[4]), 'cause': c[5], 'judge1': c[6], 'judge2': c[7], 'judge3': c[8],
                'orig_court': c[9], 'orig_year': ival(c[10]), 'orig_case': c[11], 'orig_no': ival(c[12]),
                'end_date': date3(c[13], c[14], c[15]), 'case_outcome': c[16], 'election_type': c[26] if len(c) > 26 else '',
                'jid': c[27] if len(c) > 27 else ''}
        di = -1; cur = None; ch = None
        for l in lines[1:]:
            f = l.split('!')
            k = f[0]
            if k == '1':
                di += 1
                hc_out, appellants = '', ''
                if level == 'high':                       # High Court rows insert the appeal outcome at index 4
                    hc_out = f.pop(4)
                    appellants = '|'.join(v for v in f[60:] if v in ('檢察官', '被告', '自訴人', '輔佐人', '代理人', '告訴人'))
                off = 0 if len(f) >= 73 else -1          # 2023+ files carry one extra field before index 54
                g = lambda i: f[i + off] if 0 <= i + off < len(f) else ''
                cur = dict(case, def_idx=di, def_date=date3(f[1], f[2], f[3]), defense=f[4], procedure=f[14],
                           probation=ival(f[30]), prob_victim_pay=ival(f[33]), prob_treasury=ival(f[35]), prob_service=ival(f[37]),
                           prob_treatment=ival(f[38]),
                           agg_prison=yymm(g(60)) or yymm(g(61)) or yymm(g(62)) or yymm(g(59)), agg_detention=ival(g(63)), agg_fine=ival(g(65)),
                           recidivist=ival(g(67)), hc_outcome=hc_out, appellants=appellants, n_charges=0)
                drows.append(cur)
            elif k == '1.1' and cur is not None:
                ch = {'court': case['court'], 'file_code': code, 'jyear': case['jyear'], 'jcase': case['jcase'], 'jno': case['jno'],
                      'def_idx': di, 'charge_idx': cur['n_charges'], 'law': f[1], 'art': ival(f[2]), 'art_sub': ival(f[3]),
                      'para': ival(f[5]), 'item': ival(f[7]), 'law_rev': f[8], 'result': f[9], 'prison_months': yymm(f[10]),
                      'detention_days': ival(f[11]), 'fine': ival(f[12]), 'convertible': ival(f[13]), 'juvenile': ival(f[15]),
                      'accomplice': ival(f[16]), 'attempt': ival(f[17]), 'dv': ival(f[18]), 'aggr': '', 'mitig': ''}
                crows.append(ch)
                cur['n_charges'] += 1
            elif k in ('1.1.1', '1.1.3') and ch is not None:
                ch['aggr'] += ('|' if ch['aggr'] else '') + f[1]
            elif k in ('1.1.2', '1.1.4') and ch is not None:
                ch['mitig'] += ('|' if ch['mitig'] else '') + f[1]
    return drows, crows

def run(arch):
    files = [p for p in glob.glob(os.path.join(arch, '**', '*M.刑事訴訟.txt'), recursive=True)]
    D, C = [], []
    for p in files:
        d, c = parse_file(p)
        D += d; C += c
    name = os.path.basename(arch)
    if D:
        pd.DataFrame(D).to_parquet(os.path.join(OUT, f'def_{name}.parquet'), index=False)
        pd.DataFrame(C).to_parquet(os.path.join(OUT, f'chg_{name}.parquet'), index=False)
    return name, len(files), len(D), len(C)

if __name__ == '__main__':
    archs = sorted(d for d in glob.glob(os.path.join(ROOT, 'dl_*')) if os.path.isdir(d))
    with Pool(4) as pool:
        for name, nf, nd, nc in pool.imap_unordered(run, archs):
            print(name, nf, nd, nc, flush=True)
