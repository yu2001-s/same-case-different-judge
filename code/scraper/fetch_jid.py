"""Fetch FJUD judgments by JID (one per line in LISTFILE) into RAWDIR/<sha1>.html; resumable.

fetch_jid.py LISTFILE RAWDIR [DELAY]
"""
import sys, os, hashlib, urllib.parse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fj

lst, raw = sys.argv[1], sys.argv[2]
delay = float(sys.argv[3]) if len(sys.argv) > 3 else 0.8
os.makedirs(raw, exist_ok=True)
s = fj.Session(delay=delay)
jids = [l.strip() for l in open(lst, encoding='utf-8') if l.strip()]
done = 0
for i, jid in enumerate(jids):
    p = os.path.join(raw, hashlib.sha1(jid.encode()).hexdigest() + '.html')
    if os.path.exists(p):
        continue
    try:
        _, html = s.get(fj.BASE + 'data.aspx?ty=JD&id=' + urllib.parse.quote(jid, safe=''))
    except Exception as e:
        print('ERR', jid, str(e)[:120], flush=True)
        continue
    i0 = html.find('裁判字號'); i1 = html.find('歷審裁判')
    with open(p, 'w', encoding='utf-8') as f:
        f.write(jid + '\n' + (html[i0:i1] if i0 >= 0 else html))
    done += 1
    if done % 100 == 0:
        print('fetched', i + 1, '/', len(jids), flush=True)
print('done', done, flush=True)
