"""Pilot collector: drunk-driving simple judgments (交簡, 公共危險) from the public FJUD search.

Usage:
  collect.py count  DB COURTS YEAR M1 M2      # one search per court-month, store counts + query hash
  collect.py list   DB [COURTS]                # page through result lists, store judgment ids
  collect.py fetch  DB RAWDIR [COURTS]         # download judgment pages (raw text kept outside the repo)
"""
import sys, os, re, sqlite3, calendar, json, hashlib, urllib.parse, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fj

def db(path):
    c = sqlite3.connect(path, timeout=120)
    c.execute('create table if not exists q (court text, y int, m int, part int, d1 int, d2 int, n int, qhash text, listed int default 0, primary key(court,y,m,part))')
    c.execute('create table if not exists doc (jid text primary key, court text, y int, m int, href text, fetched int default 0)')
    return c

def run_search(s, court, y, m, d1, d2):
    url, html, _ = fj.search(s, court, case='', title='公共危險', y1=str(y), m1=str(m), d1=str(d1), y2=str(y), m2=str(m), d2=str(d2))
    mm = re.search(r'qryresultlst\.aspx\?ty=JUDBOOK&(?:amp;)?q=([0-9a-f]+)"[^>]*>.*?<span class="badge">(\d+)</span>', html, re.S)
    if not mm:
        if '查無資料' in html or 'badge' not in html:
            return 0, None
        raise RuntimeError('cannot parse result count')
    return int(mm.group(2)), mm.group(1)

def cmd_count(path, courts, y, m1, m2):
    c = db(path); s = fj.Session(delay=1.0)
    for court in courts.split(','):
        for m in range(int(m1), int(m2) + 1):
            if c.execute('select 1 from q where court=? and y=? and m=?', (court, y, m)).fetchone():
                continue
            last = calendar.monthrange(int(y) + 1911, m)[1]
            n, h = run_search(s, court, y, m, 1, last)
            parts = [(0, 1, last, n, h)]
            if n > 480:  # result lists cap at 500; split into thirds of the month
                parts = []
                for k, (a, b) in enumerate([(1, 10), (11, 20), (21, last)]):
                    nn, hh = run_search(s, court, y, m, a, b)
                    parts.append((k + 1, a, b, nn, hh))
            for part, a, b, nn, hh in parts:
                c.execute('insert or replace into q values (?,?,?,?,?,?,?,?,0)', (court, y, m, part, a, b, nn, hh))
            c.commit()
            print(court, y, m, [p[3] for p in parts], flush=True)

def cmd_list(path, courts=None):
    c = db(path); s = fj.Session(delay=1.0)
    rows = c.execute('select court,y,m,part,d1,d2,n,qhash from q where listed=0 and n>0' + (" and court in (%s)" % ','.join('?' * len(courts.split(','))) if courts else ''), tuple(courts.split(',')) if courts else ()).fetchall()
    for court, y, m, part, d1, d2, n, h in rows:
        # query hashes are session-bound: re-run the search in this session
        n2, h = run_search(s, court, y, m, d1, d2)
        pages = (n2 + 19) // 20
        got = 0
        for p in range(1, pages + 1):
            _, lst = s.get(fj.BASE + f'qryresultlst.aspx?ty=JUDBOOK&q={h}&page={p}')
            for href in re.findall(r'href="(data\.aspx\?ty=JD&(?:amp;)?id=[^"]+)"', lst):
                href = href.replace('&amp;', '&')
                jid = urllib.parse.unquote(re.search(r'id=([^&]+)', href).group(1))
                c.execute('insert or ignore into doc (jid,court,y,m,href) values (?,?,?,?,?)', (jid, court, y, m, href))
                got += 1
        c.execute('update q set listed=1 where court=? and y=? and m=? and part=?', (court, y, m, part))
        c.commit()
        print('listed', court, y, m, part, n2, got, flush=True)

def cmd_fetch(path, rawdir, courts=None):
    c = db(path); s = fj.Session(delay=0.5)
    os.makedirs(rawdir, exist_ok=True)
    q = 'select jid, href from doc where fetched=0' + (" and court in (%s)" % ','.join('?' * len(courts.split(','))) if courts else '')
    rows = c.execute(q, tuple(courts.split(',')) if courts else ()).fetchall()
    for i, (jid, href) in enumerate(rows):
        try:
            _, html = s.get(fj.BASE + href)
        except Exception as e:
            print('ERR', jid, e, flush=True); continue
        i0 = html.find('裁判字號'); i1 = html.find('歷審裁判')
        body = html[i0:i1] if i0 >= 0 else html
        fn = hashlib.sha1(jid.encode()).hexdigest() + '.html'
        with open(os.path.join(rawdir, fn), 'w', encoding='utf-8') as f:
            f.write(body)
        for k in range(20):  # commit per document so parallel workers never hold the write lock for long
            try:
                c.execute('update doc set fetched=1 where jid=?', (jid,)); c.commit(); break
            except sqlite3.OperationalError:
                time.sleep(1 + k)
        if i % 25 == 0:
            print('fetched', i + 1, '/', len(rows), jid, flush=True)

if __name__ == '__main__':
    cmd = sys.argv[1]
    {'count': lambda a: cmd_count(*a), 'list': lambda a: cmd_list(*a), 'fetch': lambda a: cmd_fetch(*a)}[cmd](sys.argv[2:])
