"""Download one month of Judicial Yuan bulk judgments, keep only district/summary criminal judgments, and extract
defendant-level markers from the header (name string, Latin-script name, stated nationality, interpreter use).

bulk_text.py YYYYMM FILESET_ID WORKDIR OUTDIR
The auth header is read from /root/.jy_auth_header (never printed). Names are written to OUTDIR (private, local only).
"""
import sys, os, re, json, glob, shutil, subprocess
import pandas as pd

ym, fid, work, outd = sys.argv[1:5]
os.makedirs(outd, exist_ok=True)
out = os.path.join(outd, f'{ym}.parquet')
if os.path.exists(out):
    sys.exit(0)
wd = os.path.join(work, ym)
os.makedirs(wd, exist_ok=True)
rar = os.path.join(wd, f'{ym}.rar')
for k in range(4):
    p = subprocess.run(['curl', '-sS', '-L', '--max-time', '3000', '-H', '@/root/.jy_auth_header',
                        f'https://opendata.judicial.gov.tw/api/FilesetLists/{fid}/file', '-o', rar, '-w', '%{http_code}'],
                       capture_output=True, text=True)
    if p.returncode == 0 and p.stdout.strip() == '200' and os.path.getsize(rar) > 10_000_000:
        break
else:
    print(ym, 'download failed', p.stdout, p.stderr[:200], flush=True)
    sys.exit(1)
x = os.path.join(wd, 'x')
subprocess.run(['unar', '-q', '-f', '-o', x, rar, '*/*地方法院刑事/*', '*/*簡易庭刑事/*'], capture_output=True)
os.remove(rar)

NAT = r'(越南|印尼|印度尼西亞|泰國|菲律賓|馬來西亞|緬甸|柬埔寨|日本|韓國|美國|加拿大|英國|法國|德國|澳洲|香港|澳門|大陸地區|中國大陸|中華人民共和國|新加坡|印度|巴基斯坦|蒙古|斯里蘭卡|尼泊爾|孟加拉)'
ROLE = re.compile(r'^\s*(?:(?:上\s*訴\s*人|聲\s*請\s*人|抗\s*告\s*人|再\s*審\s*聲\s*請\s*人)\s*)?(?:即\s*)?被\s*告\s*(?:兼[^\s]*\s*)?(.*)$')
OTHER = re.compile(r'^\s*(公\s*訴\s*人|聲\s*請\s*人|自\s*訴\s*人|選\s*任|指\s*定|辯\s*護\s*人|代\s*理\s*人|輔\s*佐\s*人|法\s*定\s*代\s*理|告\s*訴\s*人|被\s*害\s*人|參\s*與\s*人|上\s*列|上\s*訴\s*人)')
rows = []
for f in glob.glob(os.path.join(x, '**', '*.json'), recursive=True):
    try:
        d = json.load(open(f, encoding='utf-8'))
    except Exception:
        continue
    full = d.get('JFULL') or ''
    lines = full.replace('\r\n', '\n').split('\n')
    defs = []
    cur = None
    for ln in lines[2:60]:
        if re.search(r'上列|主\s*文', ln):
            break
        m = ROLE.match(ln)
        if m and m.group(1).strip():
            cur = [m.group(1).strip()]
            defs.append(cur)
        elif OTHER.match(ln):
            cur = None
        elif cur is not None and ln.strip():
            cur.append(ln.strip())
    head = full[:4000]
    nat_m = re.search(r'被告[^，。；\n]{0,15}?' + NAT + r'(?:國)?籍|' + NAT + r'(?:國)?籍[^，。；\n]{0,8}被告', full)
    nat = (nat_m.group(1) or nat_m.group(2)) if nat_m else ''
    sx = re.findall(r'被[\s\u3000]*告[\s\u3000]*[^\s\u3000，。]{1,14}[\s\u3000]+(男|女)[\s\u3000]*(?:[（(]?[\s\u3000]*(\d{1,3})[\s\u3000]*歲)?', full)
    rows.append({'sex_doc': '|'.join(sorted(set(a for a, b in sx))), 'age_doc': next((int(b) for a, b in sx if b), None),
                 'jid': d.get('JID', ''), 'jtitle': d.get('JTITLE', ''), 'jdate': d.get('JDATE', ''), 'n_def_hdr': len(defs),
                 'def_names': '|'.join(' '.join(v) for v in defs),
                 'latin': any(re.search(r'[A-Za-z]{3,}', ' '.join(v)) for v in defs),
                 'nat_kw': nat, 'interp': '通譯' in full, 'mainland': bool(re.search(r'大陸地區人民', head)),
                 'len': len(full)})
shutil.rmtree(wd, ignore_errors=True)
pd.DataFrame(rows).to_parquet(out, index=False)
print(ym, len(rows), flush=True)
