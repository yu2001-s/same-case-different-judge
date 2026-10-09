"""Build the plain-language Traditional Chinese report, reusing the numbers computed by build_final.py.

build_zh.py RESULTS_DIR PILOT_SIX PILOT_NATIONAL PILOT_IDENTITY REFS_JSON OUT_HTML
"""
import sys, os, re, json, runpy, tempfile, math
HERE = os.path.dirname(os.path.abspath(__file__))
out = sys.argv[6]
tmp = os.path.join(tempfile.mkdtemp(), 'en.html')
sys.argv = [os.path.join(HERE, 'build_final.py')] + sys.argv[1:6] + [tmp]
G = runpy.run_path(os.path.join(HERE, 'build_final.py'), run_name='__main__')
V, DATA = dict(G['V']), dict(G['DATA'])
lp = G['lpct']; fd = G['fd']; thw = G['thw']; bail = G['bail']
V['fd_abs'] = f"{abs(lp(fd['b'])):.0f}%"; V['thw_abs'] = f"{abs(lp(thw['b'])):.0f}%"
V['bail_p10_abs'] = f"{abs(bail['all']['p10']):.0f}"; V['bail_p90_abs'] = f"{abs(bail['all']['p90']):.0f}"
mo = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12']
m = G['M3T']['months']; V['tx_months'] = f"{m[:4]} 年 {int(m[5:7])} 月至 {m[11:15]} 年 {int(m[16:18])} 月"
ZH = {'Impaired driving': '酒駕／毒駕', 'Theft': '竊盜', 'Drug use': '施用毒品', 'Fraud': '詐欺', 'Assault': '傷害', 'Negligent injury': '過失傷害',
      'Drug possession': '持有毒品', 'Money-mule (aiding laundering)': '人頭帳戶（幫助洗錢）', 'Money-mule (aiding fraud)': '人頭帳戶（幫助詐欺）',
      'Money laundering': '洗錢', 'Criminal damage': '毀損', 'Defamation / insult': '妨害名譽'}
EN2ZH = {G['sh'](k): v for k, v in ZH.items()}
DATA['zh'] = ZH
# translate identity rows and party rows
idz = []
for r in DATA['idrows']:
    off, lab = r['term'].split(' · ')
    lab = {'foreign national': '外籍', 'woman': '女性', 'Indigenous division': '原住民族專庭'}[lab]
    idz.append(dict(r, term=f"{EN2ZH.get(off, off)} · {lab}", note=''))
DATA['idrows_zh'] = idz
pz = []
for r in DATA['party_rows']:
    p, g = r['k'].split(' · ')
    p = {'KMT': '國民黨', 'DPP': '民進黨', 'Independent': '無黨籍'}[p]
    g = '國民黨政府時期' if g.startswith('KMT') else '民進黨政府時期'
    pz.append(dict(r, k=f'{p} · {g}', note=''))
DATA['party_zh'] = pz
for k in ('named', 'named_meta'):
    DATA.pop(k, None)
tpl = open(os.path.join(HERE, 'final_template.html'), encoding='utf-8').read()
tpl = re.sub(r'<title>.*?</title>', '<title>同案不同法官</title>', tpl, count=1, flags=re.S)
tpl = re.sub(r'<meta name="description" content="[^"]*">', '<meta name="description" content="白話版：台灣刑事判決有多少取決於法官、被告與政治。">', tpl, count=1)
tpl = tpl.replace('{{body_html}}', open(os.path.join(HERE, 'zh_body.html'), encoding='utf-8').read())
missing = sorted(set(re.findall(r'\{\{([a-z0-9_]+)\}\}', tpl)) - set(V))
if missing:
    raise SystemExit(f'unresolved placeholders: {missing}')
for k, v in V.items():
    tpl = tpl.replace('{{' + k + '}}', v)
tpl = tpl.replace('p = &lt; ', 'p &lt; ')
tpl = tpl.replace('/*DATA_JSON*/', json.dumps(DATA, ensure_ascii=False, separators=(',', ':')))
tpl = tpl.replace('/*CHARTS_JS*/', open(os.path.join(HERE, 'charts.js'), encoding='utf-8').read() + '\n' + open(os.path.join(HERE, 'charts_extra.js'), encoding='utf-8').read())
tpl = tpl.replace('/*RENDER_JS*/', open(os.path.join(HERE, 'zh_render.js'), encoding='utf-8').read())
open(out, 'w', encoding='utf-8').write(tpl)
print('wrote', out, len(tpl) // 1024, 'KB')
