"""Convert a built report page (final.html / zh.html) into GitHub-flavoured Markdown.

html2md.py PAGE.html FIGDIR_REL OUT.md [HEAD_MD] [TAIL_MD]
Charts become <picture> elements with light/dark PNGs exported by figshots.js (FIGDIR_REL/<chart-id>-light.png).
The interactive named-judge table becomes collapsible tables of the flagged judges, read from data/named_judges.csv
(English: in place of the #nm-table figure; Chinese: after the paragraph headed 具名法官表).
"""
import sys, re, os, csv
from bs4 import BeautifulSoup, NavigableString, Tag

page, figdir, out = sys.argv[1:4]
head = open(sys.argv[4], encoding='utf-8').read() if len(sys.argv) > 4 else ''
tail = open(sys.argv[5], encoding='utf-8').read() if len(sys.argv) > 5 else ''
soup = BeautifulSoup(open(page, encoding='utf-8').read(), 'html.parser')
wrap = soup.select_one('div.wrap')
ZH = bool(re.search(r'[一-鿿]', wrap.find('h1').get_text()))
NAMED_CSV = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'data', 'named_judges.csv')
named_done = []

def inline(node):
    if isinstance(node, NavigableString):
        return re.sub(r'\s+', ' ', str(node))
    if not isinstance(node, Tag):
        return ''
    if node.name in ('script', 'style', 'details'):
        return ''
    inner = ''.join(inline(c) for c in node.children)
    if node.name in ('b', 'strong'):
        s = inner.strip()
        return (f'<b>{s}</b>' if ZH else f'**{s}**') if s else ''
    if node.name in ('i', 'em'):
        s = inner.strip()
        return f'*{s}*' if s else ''
    if node.name == 'a':
        if 'c' in (node.parent.get('class') or []):
            return inner
        return f"[{inner.strip()}]({node.get('href', '')})"
    if node.name == 'sup':
        return f'<sup>{inner.strip()}</sup>'
    if node.name == 'br':
        return ' '
    if node.name == 'span' and 'zh-s' in (node.get('class') or []):
        return f' ({inner.strip()})'
    return inner

def clean(s):
    s = re.sub(r'[ \t]+', ' ', s).strip()
    s = re.sub(r' ([，。、；：）])', r'\1', s)
    return s

def table_md(t):
    rows = []
    for tr in t.find_all('tr'):
        cells = [clean(inline(c)).replace('|', '\\|') for c in tr.find_all(['th', 'td'])]
        rows.append(cells)
    if not rows:
        return ''
    n = max(len(r) for r in rows)
    rows = [r + [''] * (n - len(r)) for r in rows]
    lines = ['| ' + ' | '.join(rows[0]) + ' |', '|' + '---|' * n]
    lines += ['| ' + ' | '.join(r) + ' |' for r in rows[1:]]
    return '\n'.join(lines)

def named_md():
    """Judges flagged clearly higher / lower in data/named_judges.csv: one collapsible table per offence and decision."""
    named_done.append(True)
    rows = list(csv.DictReader(open(NAMED_CSV, encoding='utf-8')))
    # decision prefix -> (English label, English unit, Chinese label, Chinese unit)
    DEC = {'prison': ('prison length', 'days', '刑期', '天'), 'probation': ('probation rate', 'points', '緩刑率', '百分點'),
           'extra-fine': ('extra-fine rate (2024–2026)', 'points', '併科罰金率（2024–2026 年）', '百分點')}
    OFF_EN = {'Impaired driving': 'Drunk/drugged driving', 'Money-mule (aiding laundering)': 'Money mule (laundering)'}
    groups = {}
    for r in rows:
        groups.setdefault((r['offence'], r['decision'].split(' ')[0]), []).append(r)
    size = {}
    for (o, d), g in groups.items():
        size[o] = max(size.get(o, 0), len(g))
    order = sorted(groups, key=lambda k: (-size[k[0]], k[0], list(DEC).index(k[1])))

    def sg(x):
        v = f'{abs(x):.1f}'
        return ('−' if x < 0 and float(v) != 0 else '+' if x > 0 and float(v) != 0 else '') + v
    def ordn(n):
        return f"{n}{'th' if 10 <= n % 100 <= 20 else {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')}"
    def rank(r):
        lo, hi = map(int, re.findall(r'\d+', r['rank_range_90pct'])[:2]); n = r['judges_listed_in_court']
        if ZH:
            return f"第 {lo} 百分位（共 {n} 位）" if lo == hi else f"第 {lo}–{hi} 百分位（共 {n} 位）"
        return f"{ordn(lo)} pct of {n}" if lo == hi else f"{ordn(lo)}–{ordn(hi)} pct of {n}"

    if ZH:
        parts = ['下面依罪名和判決項目分組，只列出「明顯較高」或「明顯較低」的法官，點一下標題就能展開。「較高」是指該項結果比較多：'
                 '刑期較長、較常給緩刑，或較常併科罰金。數字是和同一法院其他法官處理類似案件相比的差距，附 95% 信賴區間；'
                 '排名是這位法官在同院列入比較的法官中的百分位（90% 範圍，數字越大越高）。'
                 f'全部 {len(rows):,} 筆估計（包括沒有被標記的法官）在 [`data/named_judges.csv`](data/named_judges.csv)，GitHub 會把它顯示成可以搜尋的表格。']
    else:
        parts = ['Below are only the judges flagged *clearly higher* or *clearly lower*, grouped by offence and decision; click a line '
                 'to open its table. *Higher* means more of that outcome: longer prison terms, more probation or more extra fines. '
                 f'All {len(rows):,} estimates, including judges who are not flagged, are in '
                 '[`data/named_judges.csv`](data/named_judges.csv); GitHub shows it as a searchable table.']
    for o, d in order:
        g = groups[(o, d)]
        hi = sorted((r for r in g if r['flag'] == 'clearly higher'), key=lambda r: -float(r['difference_vs_court_avg']))
        lo = sorted((r for r in g if r['flag'] == 'clearly lower'), key=lambda r: float(r['difference_vs_court_avg']))
        dec_en, unit_en, dec_zh, unit_zh = DEC[d]
        if ZH:
            summary = f"<b>{g[0]['罪名']}・{dec_zh}</b>：{len(g)} 位法官中，{len(hi)} 位明顯較高、{len(lo)} 位明顯較低"
            lines = [f'| 法院 | 法官 | 件數 | 與同院平均相比（{unit_zh}） | 95% 信賴區間 | 院內排名（90% 範圍） | 標記 |']
        else:
            summary = f"<b>{OFF_EN.get(o, o)} · {dec_en}</b>: {len(hi)} clearly higher, {len(lo)} clearly lower, of {len(g)} judges"
            lines = [f'| Court | Judge | Cases | Vs court average ({unit_en}) | 95% interval | Rank in court (90% range) | Flag |']
        lines.append('|---|---|---|---|---|---|---|')
        for r in hi + lo:
            court = r['court'].replace('地方法院', '') + ('' if ZH else ' ' + r['court_en'])
            ci = f"{sg(float(r['ci95_low']))} {'至' if ZH else 'to'} {sg(float(r['ci95_high']))}"
            flag = {'clearly higher': '明顯較高', 'clearly lower': '明顯較低'}[r['flag']] if ZH else r['flag']
            lines.append(f"| {court} | {r['judge']} | {int(r['cases']):,} | {sg(float(r['difference_vs_court_avg']))} | {ci} | {rank(r)} | {flag} |")
        parts.append(f'<details>\n<summary>{summary}</summary>\n\n' + '\n'.join(lines) + '\n\n</details>')
    return '\n\n'.join(parts)

def figure_md(f):
    t = f.select_one('figcaption .t'); s = f.select_one('figcaption .s')
    title = clean(inline(t)) if t else ''
    cap = clean(inline(s)) if s else ''
    if f.select_one('#nm-table'):
        cap = cap.replace('Dot = estimate, line = 95% interval; rank = ', 'Rank = ')
        return f'<b>{title}</b>\n\n{cap}\n\n{named_md()}'
    parts = [(f'<b>{title}</b>' if ZH else f'**{title}**')] if title else []
    for ch in f.select('.chart[id]'):
        cid = ch['id']
        parts.append(f'<picture>\n  <source media="(prefers-color-scheme: dark)" srcset="{figdir}/{cid}-dark.png">\n'
                     f'  <img alt="{title}" src="{figdir}/{cid}-light.png">\n</picture>')
    if cap:
        parts.append(f'<sub>{cap}</sub>')
    return '\n\n'.join(parts)

def block(node, out):
    if isinstance(node, NavigableString) or not isinstance(node, Tag):
        return
    cls = node.get('class') or []
    if node.name in ('script', 'style', 'nav', 'details') or 'eyebrow' in cls or 'controls' in cls:
        return
    if node.name == 'h1':
        out.append('# ' + clean(inline(node)))
    elif node.name == 'h2':
        out.append('## ' + clean(inline(node)))
    elif node.name == 'h3':
        out.append('### ' + clean(inline(node)))
    elif node.name == 'p':
        txt = clean(inline(node))
        if txt:
            out.append(('> ' + txt) if 'note' in cls else txt)
        if ZH and txt.startswith('<b>具名法官表。</b>'):
            out.append(named_md())
    elif 'meta' in cls:
        out.append('\n'.join(f'<sub>{clean(inline(s))}</sub><br>' for s in node.find_all('span', recursive=False)))
    elif 'holding' in cls:
        hdr = '| 數字 | 意思 |' if ZH else '| Number | What it means |'
        rows = [hdr, '|---|---|'] + [f"| <b>{clean(inline(t.select_one('.v')))}</b> | {clean(inline(t.select_one('.l')))} |" for t in node.select('.tile')]
        out.append('\n'.join(rows))
    elif node.name == 'ol' and 'findings' in cls:
        out.append('\n'.join(f'{i + 1}. {clean(inline(li))}' for i, li in enumerate(node.find_all('li', recursive=False))))
    elif node.name == 'ol' and 'refs' in cls:
        out.append('\n'.join(f'{i + 1}. {clean(inline(li))}' for i, li in enumerate(node.find_all('li', recursive=False))))
    elif node.name == 'figure':
        out.append(figure_md(node))
    elif 'tablewrap' in cls and node.find('table'):
        out.append(table_md(node.find('table')))
    elif node.name == 'table':
        out.append(table_md(node))
    else:
        for c in node.children:
            block(c, out)

parts = []
for c in wrap.children:
    block(c, parts)
if not named_done:
    raise SystemExit('named-judge tables not placed: no #nm-table figure or 具名法官表 paragraph in ' + page)
md = head + '\n\n'.join(p for p in parts if p.strip()) + '\n' + tail
md = md.replace('https://claude.ai/artifact/GezyRfdw7n6jJooaNFn44j', 'README.md')
for pat in (r'；?滑鼠移到長條上可看平均刑期。?', r' ?Hover for [^.<]*\.', r' ?Click a column heading to sort\.'):
    md = re.sub(pat, '', md)
md = md.replace('括號內是差距佔該罪名平均刑期的百分比</sub>', '括號內是差距佔該罪名平均刑期的百分比。</sub>')
open(out, 'w', encoding='utf-8').write(md)
print('wrote', out, len(md), 'chars')
