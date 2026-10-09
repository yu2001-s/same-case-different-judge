"""Parse FJUD judgment pages (drunk-driving pilot) into one row per judgment.

Defendant names are never written out. Judges are kept by name here only so that
they can be pseudonymised in the analysis step.
"""
import re, os, sys, html as htmlmod, json

CN = {'零': 0, '〇': 0, '一': 1, '壹': 1, '二': 2, '貳': 2, '兩': 2, '三': 3, '參': 3, '叁': 3, '四': 4, '肆': 4,
      '五': 5, '伍': 5, '六': 6, '陸': 6, '七': 7, '柒': 7, '八': 8, '捌': 8, '九': 9, '玖': 9}
UNIT = {'十': 10, '拾': 10, '百': 100, '佰': 100, '千': 1000, '仟': 1000}
BIG = {'萬': 10000}

def cn2int(s):
    """Convert Chinese numerals (incl. financial forms, 萬) or arabic digits to int."""
    s = s.replace(',', '').replace('，', '')
    if re.fullmatch(r'\d+', s):
        return int(s)
    total, section, num = 0, 0, 0
    for ch in s:
        if ch in CN:
            num = CN[ch]
        elif ch in UNIT:
            section += (num or 1) * UNIT[ch]; num = 0
        elif ch in BIG:
            total += (section + num) * BIG[ch]; section = 0; num = 0
        elif ch.isdigit():
            num = num * 10 + int(ch)
        else:
            return None
    return total + section + num

NUM = r'[0-9零〇一壹二貳兩三參叁四肆五伍六陸七柒八捌九玖十拾百佰千仟萬,]+'

def clean(raw):
    t = re.sub(r'<br\s*/?>', '\n', raw)
    t = re.sub(r'<[^>]+>', '', t)
    t = htmlmod.unescape(t).replace('　', ' ').replace('\xa0', ' ')
    t = re.sub(r'[ \t]+', ' ', t)
    t = re.sub(r'\n\s*', '\n', t)
    return t

def flat(t):
    return re.sub(r'\s+', '', t)

def months(y, m):
    return (cn2int(y) if y else 0) * 12 + (cn2int(m) if m else 0)

def parse(raw):
    t = clean(raw)
    f = flat(t)
    r = {}
    m = re.search(r'裁判字號：(.+?)(\d+)年度(.+?)字第(\d+)號(.+?)(判決|裁定)', f)
    if not m:
        return None
    r['court_name'], r['jyear'], r['jcase'], r['jno'], r['jkind'] = m.group(1), int(m.group(2)), m.group(3), int(m.group(4)), m.group(5) + m.group(6)
    m = re.search(r'裁判日期：民國(\d+)年(\d+)月(\d+)日', f)
    r['date'] = f'{int(m.group(1)) + 1911:04d}-{int(m.group(2)):02d}-{int(m.group(3)):02d}' if m else None
    m = re.search(r'裁判案由：(.+?)(?:臺灣|福建)', f)
    r['cause'] = m.group(1) if m else None
    r['is_judgment'] = r['jkind'].endswith('判決')
    head = f[:600]
    r['simple'] = '簡易判決' in head
    r['appeal'] = '上' in r['jcase']
    r['plea_bargain'] = '協商判決' in head

    # split: judgment proper | signature | statute appendix (附錄) | prosecutor's application (附件)
    # signature block ends where the clerk's certification starts: 以上正本證明 / 上列正本證明 / 上正本證明 (varies by court)
    msig = re.search(r'(?:以上|上列|上)正本證明', f)
    sig_at = msig.start() if msig else -1
    judgment = f[:sig_at] if sig_at > 0 else f
    rest = f[sig_at:] if sig_at > 0 else ''
    k = rest.find('附錄')
    appendix_free = rest
    if k >= 0:
        k2 = rest.find('附件', k)
        appendix_free = rest[:k] + (rest[k2:] if k2 >= 0 else '')
    facts = judgment + appendix_free  # everything except the quoted statute text

    i = judgment.find('主文')
    j = len(judgment)
    for stop in ['犯罪事實及證據', '犯罪事實', '事實及理由', '事實及證據', '理由', '事實']:
        kk = judgment.find(stop, i + 2)
        if kk > 0:
            j = min(j, kk)
    main = judgment[i:j] if i >= 0 else ''
    r['main'] = main[:600]

    r['art_185_3_1_1'] = bool(re.search(r'第185條之3第1項第1款', facts))
    r['art_185_3_1_2'] = bool(re.search(r'第185條之3第1項第2款', facts))
    r['art_185_3_1_3'] = bool(re.search(r'第185條之3第1項第[34]款', facts))
    r['art_185_3_2'] = bool(re.search(r'第185條之3第2項', facts))
    r['art_185_3_3'] = bool(re.search(r'第185條之3第3項', facts))
    r['art_185_4'] = bool(re.search(r'第185條之4', facts))
    r['drugs'] = r['art_185_3_1_3']  # statutory subsection only; '毒品' also appears in prior-record text

    bac = None
    for mm in re.finditer(r'每公升(\d+(?:\.\d+)?)毫克(以上)?', facts):
        if mm.group(2):
            continue
        v = float(mm.group(1))
        if 0.0 < v < 3.0:
            bac = v; break
    if bac is None:
        mm = re.search(r'血液中?(?:所含)?酒精濃度(?:達|為)?(?:百分之)?(\d+(?:\.\d+)?)(%|％)?', facts)
        if mm:
            v = float(mm.group(1))
            if 0 < v < 1:
                bac = round(v * 5, 3)  # 0.05% blood ~ 0.25 mg/L breath (statutory equivalence)
    r['bac'] = bac

    r['acquit'] = '無罪' in main
    r['dismiss'] = bool(re.search(r'免訴|不受理', main))
    r['multi'] = bool(re.search(r'應執行|各處|附表', main)) or len(re.findall(r'處有期徒刑|處拘役|處罰金', main)) > 1
    pm = None
    mm = re.search(r'處有期徒刑(?:(' + NUM + r')年)?(?:(' + NUM + r')月)?', main)
    if mm and (mm.group(1) or mm.group(2)):
        pm = months(mm.group(1), mm.group(2))
    r['prison_months'] = pm
    mm = re.search(r'處拘役(' + NUM + r')日', main)
    r['detention_days'] = cn2int(mm.group(1)) if mm else None
    mm = re.search(r'併科罰金新臺幣(' + NUM + r')元', main)
    r['addl_fine_ntd'] = cn2int(mm.group(1)) if mm else 0
    mm = re.search(r'處罰金新臺幣(' + NUM + r')元', main)
    r['fine_only_ntd'] = cn2int(mm.group(1)) if mm else None
    mm = re.search(r'易科罰金[^。]{0,40}?以新臺幣(' + NUM + r')元折算(?:壹|一|1)日', main)
    r['conv_rate'] = cn2int(mm.group(1)) if mm else None
    mm = re.search(r'緩刑(' + NUM + r')年', main)
    r['probation_years'] = cn2int(mm.group(1)) if mm else 0
    r['probation'] = r['probation_years'] > 0

    reasons = judgment[j:] + appendix_free
    # courts that find 累犯 state it in the operative part (主文); reasons often mention it only to reject it
    enh = False
    for mm in re.finditer(r'依刑法第47條第1項(?:之)?(?:規定)?[，,]?(?:加重其?刑|加重最低本刑)', reasons):
        pre = reasons[max(0, mm.start() - 15):mm.start()]
        if not re.search(r'無庸|毋庸|不予|無從|不依|亦無|不再|未依|無須|不必', pre):
            enh = True; break
    r['recidivist'] = ('累犯' in main) or enh
    pri = re.search(r'(?:前因|曾因|前於|曾於|前已|曾有|前有|已有)[^。；]{0,40}?(?:酒後駕|酒駕|酒醉駕|公共危險|不能安全駕駛)[^。；]{0,40}?(?:前科|前案|紀錄|判處|判決|處刑|緩起訴|確定)', reasons)
    many = re.search(r'(?:多次|數次|屢次|多項|二次以上|兩次以上)[^。；]{0,10}(?:酒後駕|酒駕|酒醉駕|公共危險|不能安全駕駛)', reasons)
    r['prior_dui'] = bool(pri) or bool(many) or r['recidivist']
    n = None
    mm = re.search(r'([0-9一二兩三四五六七八九十])次(?:之)?(?:酒後駕車|酒駕|酒醉駕車|公共危險|不能安全駕駛)', reasons)
    if mm:
        n = cn2int(mm.group(1).replace('兩', '二'))
    mm2 = re.search(r'第([0-9二三四五六七八九十])次(?:酒後駕車|酒駕|酒醉駕車|犯)', reasons)
    if mm2:
        n2 = cn2int(mm2.group(1)) - 1
        n = max(n or 0, n2)
    r['n_prior_dui'] = n
    r['clean_record'] = bool(re.search(r'無(?:任何)?(?:犯罪)?前科|素行(?:尚)?(?:良好|端正|尚可)|未曾有.{0,10}(?:犯罪|前科)|初犯', reasons))
    r['self_report'] = bool(re.search(r'自首', reasons))
    r['art59'] = bool(re.search(r'刑法第59條', reasons))
    acc = False
    for mm in re.finditer(r'肇事|車禍|交通事故|擦撞|追撞|撞擊|碰撞|自撞|撞及|撞上|撞到|自摔|摔倒|倒地', facts):
        pre = facts[max(0, mm.start() - 6):mm.start()]
        post = facts[mm.end():mm.end() + 12]
        if re.search(r'未|無|非|沒有|免於|避免|易|可能|恐|若|預防|防止', pre):
            continue
        if re.match(r'(?:當事人|駕駛人)?(?:酒精|測得|呼氣)|危險|率|風險|之虞|可能|機率|發生率', post):
            continue  # police form names ('交通事故當事人酒精測定紀錄表') and generic risk language
        acc = True; break
    r['accident'] = acc
    r['injury'] = bool(re.search(r'致.{0,15}(?:受傷|傷害)|受有.{0,30}傷', facts)) or r['art_185_3_2']
    mm = re.search(r'(?:駕駛|騎乘).{0,25}?(機車|小客車|小貨車|貨車|自小客|自用小|營業|大客車|聯結車|曳引車|微型電動|電動自行車|腳踏車|自行車)', facts)
    r['vehicle'] = ({'機車': 'motorcycle', '微型電動': 'e-bike', '電動自行車': 'e-bike', '腳踏車': 'bicycle', '自行車': 'bicycle'}.get(mm.group(1), 'car/truck') if mm else None)
    edu = None
    for kw, v in [('國小', 1), ('國中', 2), ('初中', 2), ('高中', 3), ('高職', 3), ('專科', 4), ('五專', 4), ('大學', 5), ('碩士', 6), ('博士', 7)]:
        if re.search(kw + r'(?:畢業|肄業|就讀|在學|學歷|之教育|教育程度|之智識|之學歷)', reasons):
            edu = v if (edu is None or v > edu) else edu
    r['edu'] = edu
    eco = None
    for kw, v in [('貧寒', 1), ('貧困', 1), ('清寒', 1), ('勉持', 2), ('小康', 3), ('中產', 4), ('富裕', 5)]:
        if kw in reasons:
            eco = v; break
    r['econ'] = eco
    mm = re.search(r'(男|女)(?:性)?[，,]?(?:\d{1,3}歲)?[（(]?民國', f[:1500] + appendix_free[:3000])
    r['def_sex'] = mm.group(1) if mm else None
    mm = re.search(r'(?:男|女)(\d{1,3})歲', f[:1500] + appendix_free[:3000])
    r['def_age'] = int(mm.group(1)) if mm else None

    region = judgment[-180:]
    names = re.findall(r'法官([一-鿿]{2,4}?)(?=審判長|法官|$)', region)
    r['judges'] = names
    r['judge'] = names[-1] if len(names) == 1 else None
    r['panel'] = len(names) > 1 or '審判長' in region
    mm = re.search(r'日([一-鿿]{2,12}?庭)(?:審判長)?法官', region)
    r['division'] = mm.group(1) if mm else None
    mm = re.search(r'(?:本案|本件)經檢察官([一-鿿]{2,4}?)(?:聲請|提起|到庭|起訴|偵查|追加|移送)', f)
    r['prosecutor'] = mm.group(1) if mm else None
    r['text_len'] = len(judgment)
    return r

if __name__ == '__main__':
    rawdir = sys.argv[1]
    files = sorted(os.listdir(rawdir))[: int(sys.argv[2]) if len(sys.argv) > 2 else None]
    for fn in files:
        r = parse(open(os.path.join(rawdir, fn), encoding='utf-8').read())
        if r:
            r.pop('main', None)
            print(json.dumps(r, ensure_ascii=False))
