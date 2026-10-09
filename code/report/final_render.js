function renderAll() {
  const V = window.Viz, D = DATA;
  const el = (id) => document.getElementById(id);
  const sgn = (v, d = 0) => (v > 0 ? '+' : v < 0 ? '−' : '') + Math.abs(v).toFixed(d);

  // 1. Two-judge gap by offence
  const off = D.off.filter(r => r.n >= 5000).slice().sort((a, b) => b.gap - a.gap);
  V.hbars(el('c-gap'), off.map(r => ({ k: r.label, v: r.gap, hl: r.label === 'Fraud', label: `${r.gap.toFixed(1)} d (${Math.round(r.gap_pct)}%)`,
    note: `average sentence ${Math.round(r.mean_days)} days · judge share ${(r.icc * 100).toFixed(1)}% · split-half ${r.split == null ? 'n/a' : r.split.toFixed(2)} · ${r.n.toLocaleString()} cases` })), {
    fmt: (v) => v.toFixed(1) + ' d', left: 150, right: 96, tableHead: ['Offence', 'Two-judge gap (days, % of average sentence)', 'Details'],
  });

  // 2. Spread over time with reform markers
  V.tlines(el('c-trend'), D.trend.map((s, i) => ({ ...s, dy: i === 0 ? 9 : -9 })), {
    yfmt: (v) => v.toFixed(1) + '%', xlab: 'year', ydomain: [0, 20],
    events: [{ x: 2018.97, label: '2018 guidance' }, { x: 2023.1, label: '2023 AI system' }],
    tableHead: ['Group', 'Year', 'Judge spread (%)'],
  });

  // 3. Appeals: variance removed
  V.hbars(el('c-appeal'), D.ap_rows.slice().sort((a, b) => b.v - a.v), {
    fmt: (v) => v.toFixed(1) + '%', domain: [0, Math.max(30, d3.max(D.ap_rows, r => r.v) * 1.1)],
    tableHead: ['Offence', 'Judge variance removed by appeals', 'Details'],
  });

  // 4. Who appeals vs first-judge harshness
  const b = D.bins_ni;
  V.tlines(el('c-appeal-bins'), [
    { name: 'Defendant appeals', color: '--s2', values: b.map(r => ({ x: r.z, y: r.app_def * 100, note: r.n.toLocaleString() + ' cases' })) },
    { name: 'Prosecutor appeals', color: '--s1', values: b.map(r => ({ x: r.z, y: r.app_pros * 100, note: r.n.toLocaleString() + ' cases' })) },
  ], { yfmt: (v) => v.toFixed(0) + '%', xfmt: (v) => sgn(v) + ' d', xlab: 'first judge vs court average', height: 260,
       tableHead: ['Who appeals', 'Judge harshness (days)', 'Appeal rate'] });

  // 5. Movers scatter
  V.scatter(el('c-movers'), D.movers, {
    fmt: (v) => v.toFixed(1), xlab: 'Harshness in first court (SD units)', ylab: 'Harshness in second court',
    tip: (p) => [[p.a.toFixed(2) + ' → ' + p.b.toFixed(2), 'before → after moving'], ['one judge', '']],
    tableHead: ['Judge (anonymous)', 'Before', 'After'], tableRows: (pts) => pts.map((p, i) => ['Judge ' + (i + 1), p.a.toFixed(2), p.b.toFixed(2)]),
  });

  // 6. Novice vs experienced spread
  V.dumbbell(el('c-exp'), D.exp.filter(e => e.tau_novice_pct != null && e.tau_exp_pct != null).map(e => ({
    k: D.labels[e.offence] || e.offence, a: e.tau_exp_pct, b: e.tau_novice_pct,
    note: `${e.judges_novice} novice, ${e.judges_exp} experienced judges` })), {
    fmt: (v) => v.toFixed(1) + '%', labA: 'Experienced (5+ yrs)', labB: 'First 3 years', left: 170, domain: [0, 25],
  });

  // 7. Defendant identity gaps
  V.coefs2(el('c-identity'), D.idrows, { fmt: (v) => sgn(v, 0) + '%', lim: 40, left: 260,
    tableHead: ['Comparison', 'Difference in prison length', '95% interval', 'Sample'] });

  // 8. Party: case share vs candidate share
  V.dumbbell(el('c-party'), D.party_rows, { fmt: (v) => v.toFixed(0) + '%', labA: 'Share of candidates', labB: 'Share of prosecuted cases', left: 230, domain: [0, 80] });

  renderNamed();
}

/* ---------- Named judge table ---------- */
const NM = { job: null, court: '', q: '', flag: false, sort: 'effect', dir: 1 };
const JOB_LABEL = { sentence_days: 'prison length (days)', prob: 'probation rate (points)', extra_fine: 'extra-fine rate (points)' };
function initNamed() {
  const jobs = DATA.named_meta.map(m => m.offence + '|' + m.outcome);
  const sel = document.getElementById('nm-job');
  jobs.forEach(j => { const [o, y] = j.split('|'); const op = document.createElement('option'); op.value = j; op.textContent = (DATA.labels[o] || o) + ' — ' + JOB_LABEL[y]; sel.append(op); });
  NM.job = jobs[0];
  const csel = document.getElementById('nm-court');
  const courts = [...new Set(DATA.named.map(r => r.court))].sort((a, b) => a.localeCompare(b, 'zh-Hant'));
  const all = document.createElement('option'); all.value = ''; all.textContent = 'All courts'; csel.append(all);
  courts.forEach(c => { const op = document.createElement('option'); op.value = c; op.textContent = c + ' (' + (DATA.named.find(r => r.court === c).court_en) + ')'; csel.append(op); });
  sel.addEventListener('change', () => { NM.job = sel.value; renderNamed(); });
  csel.addEventListener('change', () => { NM.court = csel.value; renderNamed(); });
  document.getElementById('nm-q').addEventListener('input', (e) => { NM.q = e.target.value.trim(); renderNamed(); });
  document.getElementById('nm-flag').addEventListener('change', (e) => { NM.flag = e.target.checked; renderNamed(); });
}
function renderNamed() {
  const host = document.getElementById('nm-table');
  if (!NM.job) initNamed();
  const [o, y] = NM.job.split('|');
  let rows = DATA.named.filter(r => r.offence === o && r.outcome === y);
  const lim = (d3.quantile(rows.map(r => Math.max(Math.abs(r.lo), Math.abs(r.hi))).sort(d3.ascending), 0.97) || 1) * 1.05;
  if (NM.court) rows = rows.filter(r => r.court === NM.court);
  if (NM.q) rows = rows.filter(r => r.judge.includes(NM.q));
  if (NM.flag) rows = rows.filter(r => r.flag);
  const key = NM.sort;
  rows = rows.slice().sort((a, b) => (typeof a[key] === 'string' ? a[key].localeCompare(b[key], 'zh-Hant') : a[key] - b[key]) * NM.dir);
  const unit = y === 'sentence_days' ? ' d' : ' pts';
  const fmt = (v) => (v > 0 ? '+' : v < 0 ? '−' : '') + Math.abs(v).toFixed(y === 'sentence_days' ? 1 : 1) + unit;
  const rank = (r) => { const lo = Math.round(r.rank_lo * 100), hi = Math.round(r.rank_hi * 100); return lo === hi ? `${lo}th pct` : `${lo}–${hi}th pct`; };
  const t = document.createElement('table');
  const head = [['court', 'Court'], ['judge', 'Judge'], ['n', 'Cases'], ['effect', 'Vs court average'], ['bar', 'Estimate and 95% interval'], ['rank_lo', 'Rank in court (90% range)'], ['flag', '']];
  const hr = t.createTHead().insertRow();
  head.forEach(([k, lab]) => { const th = document.createElement('th'); th.textContent = lab + (NM.sort === k ? (NM.dir > 0 ? ' ▲' : ' ▼') : ''); th.scope = 'col';
    if (k !== 'bar') { th.tabIndex = 0; const go = () => { NM.dir = NM.sort === k ? -NM.dir : 1; NM.sort = k; renderNamed(); }; th.addEventListener('click', go); th.addEventListener('keydown', (e) => { if (e.key === 'Enter') go(); }); }
    hr.append(th); });
  const tb = t.createTBody();
  const pos = (v) => (50 + 50 * Math.max(-1, Math.min(1, v / lim))).toFixed(2) + '%';
  rows.forEach(r => {
    const tr = tb.insertRow(); tr.className = r.flag === 'higher' ? 'hi' : r.flag === 'lower' ? 'lo' : '';
    const c = (txt) => { const td = tr.insertCell(); td.textContent = txt; return td; };
    c(r.court.replace('地方法院', '') + ' ' + r.court_en).className = 'court'; c(r.judge); c(r.n.toLocaleString()); c(fmt(r.effect));
    const td = tr.insertCell(); td.className = 'bar';
    const box = document.createElement('div'); box.className = 'eff';
    const ax = document.createElement('span'); ax.className = 'axis0'; ax.style.left = '50%';
    const ci = document.createElement('span'); ci.className = 'ci'; ci.style.left = pos(r.lo); ci.style.width = `calc(${pos(r.hi)} - ${pos(r.lo)})`;
    const pt = document.createElement('span'); pt.className = 'pt'; pt.style.left = pos(r.effect);
    box.append(ax, ci, pt); td.append(box);
    td.setAttribute('aria-label', `${fmt(r.effect)}, 95% interval ${fmt(r.lo)} to ${fmt(r.hi)}`);
    c(rank(r) + ' of ' + r.judges_in_court);
    const ft = tr.insertCell(); if (r.flag) { const b = document.createElement('span'); b.className = 'badge ' + (r.flag === 'higher' ? 'hi' : 'lo'); b.textContent = r.flag === 'higher' ? 'clearly higher' : 'clearly lower'; ft.append(b); }
  });
  host.replaceChildren(t);
  const m = DATA.named_meta.find(m => m.offence === o && m.outcome === y);
  document.getElementById('nm-count').textContent = `${rows.length} judges shown · ${m.judges_listed} listed for this decision (${m.flag_higher} clearly higher, ${m.flag_lower} clearly lower) · court-wide average ${y === 'sentence_days' ? Math.round(m.mean) + ' days' : m.mean.toFixed(1) + '%'}`;
}

let raf = null;
function rerender() { cancelAnimationFrame(raf); raf = requestAnimationFrame(renderAll); }
if (window.d3) renderAll();
window.addEventListener('resize', rerender);
matchMedia('(prefers-color-scheme: dark)').addEventListener('change', rerender);
new MutationObserver(rerender).observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] });
