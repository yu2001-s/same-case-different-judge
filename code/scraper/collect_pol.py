"""Collector for election-crime judgments (vote buying etc.) from the public FJUD search, all district courts.

  collect_pol.py count DB Y1 Y2            # one search per court x 案由 x year (ROC years), split by month if > 480 hits
  collect_pol.py list  DB [COURTS]
  collect_pol.py fetch DB RAWDIR [COURTS]
"""
import sys, os, re, sqlite3, calendar, hashlib, urllib.parse, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fj

COURTS = ['TPD', 'SLD', 'PCD', 'ILD', 'KLD', 'TYD', 'SCD', 'MLD', 'TCD', 'CHD', 'NTD', 'ULD', 'CYD', 'TND', 'KSD', 'CTD',
          'HLD', 'TTD', 'PTD', 'PHD', 'KMD', 'LCD']
TITLES = ['公職人員選舉罷免法', '妨害投票', '總統副總統選舉罷免法']

def db(path):
    c = sqlite3.connect(path, timeout=120)
    c.execute('create table if not exists q (court text, title text, y int, m1 int, m2 int, n int, listed int default 0, primary key(court,title,y,m1))')
    c.execute('create table if not exists doc (jid text primary key, court text, title text, y int, href text, fetched int default 0)')
    return c

def run_search(s, court, title, y, m1, m2):
    last = calendar.monthrange(y + 1911, m2)[1]
    url, html, _ = fj.search(s, court, case='', title=title, y1=str(y), m1=str(m1), d1='1', y2=str(y), m2=str(m2), d2=str(last))
    mm = re.search(r'qryresultlst\.aspx\?ty=JUDBOOK&(?:amp;)?q=([0-9a-f]+)"[^>]*>.*?<span class="badge">(\d+)</span>', html, re.S)
    if not mm:
        return 0, None
    return int(mm.group(2)), mm.group(1)

def cmd_count(path, y1, y2, courts=None):
    c = db(path); s = fj.Session(delay=0.8)
    for court in (courts.split(',') if courts else COURTS):
        for title in TITLES:
            for y in range(int(y1), int(y2) + 1):
                if c.execute('select 1 from q where court=? and title=? and y=?', (court, title, y)).fetchone():
                    continue
                n, _ = run_search(s, court, title, y, 1, 12)
                parts = [(1, 12, n)]
                if n > 480:
                    parts = []
                    for m in range(1, 13):
                        nn, _ = run_search(s, court, title, y, m, m)
                        parts.append((m, m, nn))
                for m1, m2, nn in parts:
                    c.execute('insert or replace into q values (?,?,?,?,?,?,0)', (court, title, y, m1, m2, nn))
                c.commit()
                print(court, title, y, [p[2] for p in parts], flush=True)

def cmd_list(path, courts=None):
    c = db(path); s = fj.Session(delay=0.8)
    cl = courts.split(',') if courts else COURTS
    rows = c.execute('select court,title,y,m1,m2,n from q where listed=0 and n>0').fetchall()
    for court, title, y, m1, m2, n in rows:
        if court not in cl:
            continue
        n2, h = run_search(s, court, title, y, m1, m2)
        for p in range(1, (n2 + 19) // 20 + 1):
            _, lst = s.get(fj.BASE + f'qryresultlst.aspx?ty=JUDBOOK&q={h}&page={p}')
            for href in re.findall(r'href="(data\.aspx\?ty=JD&(?:amp;)?id=[^"]+)"', lst):
                href = href.replace('&amp;', '&')
                jid = urllib.parse.unquote(re.search(r'id=([^&]+)', href).group(1))
                c.execute('insert or ignore into doc (jid,court,title,y,href) values (?,?,?,?,?)', (jid, court, title, y, href))
        c.execute('update q set listed=1 where court=? and title=? and y=? and m1=?', (court, title, y, m1))
        c.commit()
        print('listed', court, title, y, m1, n2, flush=True)

def cmd_fetch(path, rawdir, courts=None):
    c = db(path); s = fj.Session(delay=0.5)
    os.makedirs(rawdir, exist_ok=True)
    cl = courts.split(',') if courts else COURTS
    rows = [r for r in c.execute('select jid, href, court from doc where fetched=0').fetchall() if r[2] in cl]
    for i, (jid, href, _) in enumerate(rows):
        try:
            _, html = s.get(fj.BASE + href)
        except Exception as e:
            print('ERR', jid, e, flush=True); continue
        i0 = html.find('裁判字號'); i1 = html.find('歷審裁判')
        with open(os.path.join(rawdir, hashlib.sha1(jid.encode()).hexdigest() + '.html'), 'w', encoding='utf-8') as f:
            f.write(html[i0:i1] if i0 >= 0 else html)
        for k in range(20):
            try:
                c.execute('update doc set fetched=1 where jid=?', (jid,)); c.commit(); break
            except sqlite3.OperationalError:
                time.sleep(1 + k)
        if i % 50 == 0:
            print('fetched', i + 1, '/', len(rows), jid, flush=True)

if __name__ == '__main__':
    {'count': cmd_count, 'list': cmd_list, 'fetch': cmd_fetch}[sys.argv[1]](*sys.argv[2:])
