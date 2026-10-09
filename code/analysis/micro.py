"""Read the Judicial Yuan's open terminated-case microdata (終結案件資料, '!'-delimited, '#'-separated records)
and extract first-instance drunk-driving convictions (刑法185-3 I(1)) from every district court.

Usage: micro.py MICRO_ROOT OUT_CSV
"""
import os, sys, re, glob, hashlib
import pandas as pd

root, out = sys.argv[1], sys.argv[2]

def yymm_to_months(v):
    v = (v or '').strip()
    if not v or not v.isdigit():
        return None
    v = v.zfill(4)
    return int(v[:2]) * 12 + int(v[2:])

def to_int(v):
    v = (v or '').strip()
    return int(float(v)) if re.fullmatch(r'-?\d+(\.\d+)?', v) else None

rows = []
files = [f for f in glob.glob(os.path.join(root, '**', '*.刑事訴訟.txt'), recursive=True) if re.search(r'\.[A-Z]{3}M\.', f)]
for f in files:
    code = re.search(r'\.([A-Z]{3})M\.', f).group(1)
    if not code.endswith('D'):  # district courts only (xxD); skips high courts, Supreme Court etc.
        continue
    text = open(f, encoding='utf-8', errors='replace').read()
    for rec in text.split('#'):
        lines = [l.rstrip('\r') for l in rec.strip().split('\n') if l.strip()]
        if not lines or not lines[0].startswith('0!'):
            continue
        c = lines[0].split('!')
        case = {'court_code': code, 'court': c[1], 'jyear': to_int(c[2]), 'jcase': c[3], 'jno': to_int(c[4]), 'cause': c[5],
                'judge1': c[6], 'judge2': c[7], 'judge3': c[8], 'date': f'{to_int(c[13]) + 1911:04d}-{to_int(c[14]):02d}-{to_int(c[15]):02d}' if to_int(c[13]) else None,
                'outcome': c[16], 'jid': c[27] if len(c) > 27 else ''}
        defs = [l.split('!') for l in lines if l.startswith('1!')]
        charges = [l.split('!') for l in lines if l.startswith('1.1!')]
        aggr = [l.split('!')[1] for l in lines if l.startswith('1.1.1!') or l.startswith('1.1.3!')]
        mitig = [l.split('!')[1] for l in lines if l.startswith('1.1.2!') or l.startswith('1.1.4!')]
        case['n_defendants'] = len(defs)
        case['n_charges'] = len(charges)
        if defs:
            d = defs[0]
            case['defense'] = d[4]
            case['procedure'] = d[14]
            case['probation'] = to_int(d[30])
            case['recidivist'] = to_int(d[67]) if len(d) > 67 else None
        if charges:
            ch = charges[0]
            case.update({'law': ch[1], 'art': to_int(ch[2]), 'art_sub': to_int(ch[3]), 'para': to_int(ch[5]), 'item': to_int(ch[7]),
                         'charge_result': ch[9], 'prison_months': yymm_to_months(ch[10]), 'detention_days': to_int(ch[11]),
                         'fine_ntd': to_int(ch[12]), 'convertible': to_int(ch[13])})
        case['aggravating'] = '|'.join(aggr)
        case['mitigating'] = '|'.join(mitig)
        case['file'] = hashlib.sha1(case['jid'].encode()).hexdigest() + '.html' if case['jid'] else ''
        rows.append(case)

df = pd.DataFrame(rows)
df.to_csv(out.replace('.csv', '_all_district.csv'), index=False)
# the microdata leave 款 blank for 185-3, so this is 185-3 I (alcohol or drug impaired driving) as a whole
dui = df[(df['law'] == '刑法') & (df['art'] == 185) & (df['art_sub'] == 3) & (df['para'] == 1)]
dui.to_csv(out, index=False)
print('district criminal records', len(df), 'courts', df['court_code'].nunique())
print('185-3 I records', len(dui))
print(dui['charge_result'].value_counts().head(8).to_string())
print(dui['jcase'].value_counts().head(15).to_string())
