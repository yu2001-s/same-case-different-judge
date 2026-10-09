function renderAll() {
  const V = window.Viz, D = DATA, Z = D.zh;
  const el = (id) => document.getElementById(id);
  const sgn = (v, d = 0) => (v > 0 ? '+' : v < 0 ? '−' : '') + Math.abs(v).toFixed(d);
  const off = D.off.filter(r => r.n >= 5000).slice().sort((a, b) => b.gap - a.gap);
  V.hbars(el('z-gap'), off.map(r => ({ k: Z[r.offence] || r.label, v: r.gap, hl: r.offence === 'Fraud', label: `${r.gap.toFixed(1)} 天（${Math.round(r.gap_pct)}%）`,
    note: `平均刑期 ${Math.round(r.mean_days)} 天 · ${r.n.toLocaleString()} 件` })), {
    fmt: (v) => v.toFixed(1) + ' 天', left: 170, right: 104, tableHead: ['罪名', '兩位法官平均差距（佔平均刑期）', '說明'],
  });
  V.scatter(el('z-movers'), D.movers, {
    fmt: (v) => v.toFixed(1), xlab: '在舊法院的寬嚴（標準化）', ylab: '在新法院的寬嚴',
    tip: (p) => [[p.a.toFixed(2) + ' → ' + p.b.toFixed(2), '調動前 → 調動後'], ['一位法官', '']],
    tableHead: ['法官（匿名）', '調動前', '調動後'], tableRows: (pts) => pts.map((p, i) => ['法官 ' + (i + 1), p.a.toFixed(2), p.b.toFixed(2)]),
  });
  V.tlines(el('z-trend'), D.trend.map((s, i) => ({ ...s, name: i === 0 ? '有涵蓋的罪名' : '未涵蓋的罪名', dy: i === 0 ? 9 : -9 })), {
    yfmt: (v) => v.toFixed(1) + '%', xlab: '年', ydomain: [0, 20],
    events: [{ x: 2018.97, label: '2018 量刑趨勢建議' }, { x: 2023.1, label: '2023 AI 量刑' }],
    tableHead: ['組別', '年', '法官差距（%）'],
  });
  V.coefs2(el('z-identity'), D.idrows_zh, { fmt: (v) => sgn(v, 0) + '%', lim: 40, left: 220,
    tableHead: ['比較', '刑期差距', '95% 信賴區間', ''] });
  V.dumbbell(el('z-party'), D.party_zh, { fmt: (v) => v.toFixed(0) + '%', labA: '候選人中的比例', labB: '被起訴案件中的比例', left: 200, domain: [0, 80] });
}
let raf = null;
function rerender() { cancelAnimationFrame(raf); raf = requestAnimationFrame(renderAll); }
if (window.d3) renderAll();
window.addEventListener('resize', rerender);
matchMedia('(prefers-color-scheme: dark)').addEventListener('change', rerender);
new MutationObserver(rerender).observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] });
