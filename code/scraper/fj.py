"""Minimal client for the public FJUD judgment search, using curl for HTTPS."""
import re, subprocess, urllib.parse, time, os, tempfile

BASE = 'https://judgment.judicial.gov.tw/FJUD/'
UA = 'Mozilla/5.0 (academic research pilot; low-rate)'

class Session:
    def __init__(self, delay=1.0):
        fd, self.jar = tempfile.mkstemp(prefix='fjcj_'); os.close(fd)
        self.delay = delay
        self.last = 0.0

    def _wait(self):
        dt = time.time() - self.last
        if dt < self.delay:
            time.sleep(self.delay - dt)
        self.last = time.time()

    def get(self, url, data=None, tries=4):
        for k in range(tries):
            self._wait()
            cmd = ['curl', '-sS', '-L', '--max-time', '60', '-A', UA, '-c', self.jar, '-b', self.jar,
                   '-w', '\n__EFFURL__%{url_effective}__CODE__%{http_code}']
            if data is not None:
                cmd += ['--data-binary', urllib.parse.urlencode(data, doseq=True)]
            cmd.append(url)
            p = subprocess.run(cmd, capture_output=True)
            out = p.stdout.decode('utf-8', 'replace')
            m = re.search(r'\n__EFFURL__(.*)__CODE__(\d+)$', out)
            if p.returncode == 0 and m and m.group(2) == '200':
                return m.group(1), out[:m.start()]
            time.sleep(2 ** (k + 1))
        raise RuntimeError(f'failed {url}: rc={p.returncode} {p.stderr[:200]!r} {out[-200:]!r}')

def hidden_fields(html):
    return dict(re.findall(r'<input type="hidden" name="(__[A-Z]+)" id="[^"]*" value="([^"]*)"', html))

def search(sess, court, sys_='M', case='', title='', kw='', jmain='', y1='', m1='', d1='', y2='', m2='', d2=''):
    """Run an advanced search; return the qryresult URL (first page) or None."""
    _, html = sess.get(BASE + 'Default_AD.aspx')
    data = hidden_fields(html)
    data.update({'jud_court': court, 'jud_sys': sys_, 'jud_year': '', 'sel_judword': '', 'jud_case': case,
                 'jud_no': '', 'jud_no_end': '', 'dy1': y1, 'dm1': m1, 'dd1': d1, 'dy2': y2, 'dm2': m2, 'dd2': d2,
                 'jud_title': title, 'jud_jmain': jmain, 'jud_kw': kw, 'KbStart': '', 'KbEnd': '',
                 'judtype': 'JUDBOOK', 'whosub': '0', 'ctl00$cp_content$btnQry': '送出查詢'})
    url, html = sess.get(BASE + 'Default_AD.aspx', data)
    m = re.search(r'qryresult\.aspx\?[^"\'<> ]+', html)
    return (url, html, m.group(0).replace('&amp;', '&') if m else None)
