"""Convert a built report page (final.html / zh.html) into GitHub-flavoured Markdown.

html2md.py PAGE.html FIGDIR_REL OUT.md [HEAD_MD] [TAIL_MD]
Charts become <picture> elements with light/dark PNGs exported by figshots.js (FIGDIR_REL/<chart-id>-light.png).
The interactive named-judge table is replaced by a pointer to data/named_judges.csv.
"""
import sys, re
from bs4 import BeautifulSoup, NavigableString, Tag

page, figdir, out = sys.argv[1:4]
head = open(sys.argv[4], encoding='utf-8').read() if len(sys.argv) > 4 else ''
tail = open(sys.argv[5], encoding='utf-8').read() if len(sys.argv) > 5 else ''
soup = BeautifulSoup(open(page, encoding='utf-8').read(), 'html.parser')
wrap = soup.select_one('div.wrap')
ZH = bool(re.search(r'[一-鿿]', wrap.find('h1').get_text()))

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

def figure_md(f):
    t = f.select_one('figcaption .t'); s = f.select_one('figcaption .s')
    title = clean(inline(t)) if t else ''
    cap = clean(inline(s)) if s else ''
    if f.select_one('#nm-table'):
        if ZH:
            body = '完整的具名法官表在 [`data/named_judges.csv`](data/named_judges.csv)，GitHub 會把它顯示成可以搜尋的表格。'
        else:
            body = ('The full table is in [`data/named_judges.csv`](data/named_judges.csv); GitHub shows it as a searchable table. '
                    'Columns: decision, offence, court, judge, cases, difference from the court average with its 95% interval, '
                    '90% rank range among the court\'s listed judges, and the flag (clearly higher / clearly lower).')
        return f'<b>{title}</b>\n\n{cap}\n\n{body}'
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
md = head + '\n\n'.join(p for p in parts if p.strip()) + '\n' + tail
md = md.replace('https://claude.ai/artifact/GezyRfdw7n6jJooaNFn44j', 'README.md')
for pat in (r'；?滑鼠移到長條上可看平均刑期。?', r' ?Hover for [^.<]*\.', r' ?Click a column heading to sort\.'):
    md = re.sub(pat, '', md)
md = md.replace('括號內是差距佔該罪名平均刑期的百分比</sub>', '括號內是差距佔該罪名平均刑期的百分比。</sub>')
open(out, 'w', encoding='utf-8').write(md)
print('wrote', out, len(md), 'chars')
