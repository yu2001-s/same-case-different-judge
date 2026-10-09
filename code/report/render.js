function renderAll() {
  const V = window.Viz, S = DATA.six, N = DATA.nat;
  const mo = (d) => (d / 30).toFixed(1) + ' mo';
  const days = (d) => (d > 0 ? '+' : d < 0 ? '−' : '') + Math.abs(Math.round(d)) + ' d';
  const el = (id) => document.getElementById(id);

  // 1. Sentence rises with breath alcohol and with a prior drunk-driving record
  const bins = [...new Set(S.bac_prior_curve.map(r => r.bac_bin))];
  const mk = (p, name, color) => ({ name, color, values: S.bac_prior_curve.filter(r => r.prior === p).map(r => ({ x: r.bac_bin, y: r.mean / 30, n: r.count })) });
  V.lines(el('c-bac'), [mk('first', 'First offence', '--s1'), mk('prior', 'Prior drunk driving', '--s2')], {
    x: bins, yfmt: (d) => d.toFixed(1) + ' mo',
    tableHead: ['Breath alcohol (mg/L)', 'Group', 'Mean sentence (months)', 'Cases'],
    tableRows: (series) => series.flatMap(s => s.values.map(v => [v.x, s.name, v.y.toFixed(2), String(v.n)])),
  });

  // 2. Same typical case, different judge
  const courts = DATA.court_order;
  const std = S.standard_case.by_judge;
  const courtMean = {}; courts.forEach(c => { const v = std.filter(r => r.court === c).map(r => r.pred_days); if (v.length) courtMean[c] = d3.mean(v); });
  const nByJudge = Object.fromEntries(S.judges.map(j => [j.judge_id, j.n]));
  V.strip(el('c-judges'), std, {
    group: 'court', value: 'pred_days', groups: courts.filter(c => std.some(r => r.court === c)), mark: courtMean,
    fmt: (d) => (d / 30).toFixed(1),
    tip: (r) => [[(r.pred_days / 30).toFixed(2) + ' months', 'predicted for the typical case'], [r.judge_id, r.court + ' · ' + (nByJudge[r.judge_id] || '?') + ' cases']],
    tableHead: ['Judge (anonymous)', 'Court', 'Cases decided', 'Predicted sentence, typical case (months)'],
    tableRows: (rows) => rows.slice().sort((a, b) => a.court.localeCompare(b.court) || a.pred_days - b.pred_days).map(r => [r.judge_id, r.court, String(nByJudge[r.judge_id] || ''), (r.pred_days / 30).toFixed(2)]),
  });

  // 3. Split-half reliability
  V.scatter(el('c-split'), S.split_half.points, {
    fmt: (d) => Math.round(d), xlab: 'Judge effect, random half A (days)', ylab: 'Judge effect, half B (days)',
    tip: (p) => [[days(p.a) + ' / ' + days(p.b), 'half A / half B'], [p.judge_id, p.court]],
    tableHead: ['Judge', 'Court', 'Half A (days)', 'Half B (days)'],
    tableRows: (pts) => pts.map(p => [p.judge_id, p.court, p.a.toFixed(1), p.b.toFixed(1)]),
  });

  // 4. Permutation test
  V.nullHist(el('c-perm'), S.permutation.hist, S.permutation.edges, S.permutation.observed, {
    fmt: (d) => Math.round(d), obsLabel: 'Real data: ' + S.permutation.ratio.toFixed(1) + '× chance',
  });

  // 5. Variance decomposition
  V.stack(el('c-var'), DATA.decomp, {});

  // 6. Extra fine on top of prison, by judge
  const fj = S.addl_fine.judges;
  const fm = {}; courts.forEach(c => { const v = fj.filter(r => r.court === c).map(r => r.adj); if (v.length) fm[c] = d3.mean(v); });
  V.strip(el('c-fine'), fj.map(r => ({ ...r, adjc: Math.max(0, Math.min(1, r.adj)) })), {
    group: 'court', value: 'adjc', groups: courts.filter(c => fj.some(r => r.court === c)), mark: fm, domain: [0, 1],
    fmt: (d) => Math.round(d * 100) + '%',
    tip: (r) => [[Math.round(r.adjc * 100) + '%', 'adjusted share with an extra fine'], [Math.round(r.raw * 100) + '% raw', r.judge_id + ' · ' + r.court + ' · ' + r.n + ' cases']],
    tableHead: ['Judge', 'Court', 'Cases', 'Raw share with extra fine', 'Adjusted share'],
    tableRows: (rows) => rows.map(r => [r.judge_id, r.court, String(r.n), Math.round(r.raw * 100) + '%', Math.round(r.adjc * 100) + '%']),
  });

  // 7. National: spread of judge effects within each court
  V.ranges(el('c-nat-range'), N.courts.filter(c => c.judges >= 3).sort((a, b) => (a.max - a.min) - (b.max - b.min)), { fmt: (d) => (d > 0 ? '+' : d < 0 ? '−' : '') + Math.abs(Math.round(d)) });

  // 8. National: where you are tried
  V.hbars(el('c-nat-court'), N.court_adjusted.filter(r => r.n >= 200).map(r => ({ k: r.court, v: r.pred_days / 30, note: r.n + ' cases' })), {
    fmt: (v) => v.toFixed(2) + ' mo',
    tableHead: ['Court', 'Adjusted mean sentence', 'Cases'],
  });

  // 9. Timing effects (within judge)
  V.coefs(el('c-timing'), S.timing.map(t => ({ term: t.term, coef: t.coef, lo: t.lo, hi: t.hi, p: t.p, q: t.q_bh })), {
    fmt: (d) => (d > 0 ? '+' : d < 0 ? '−' : '') + Math.abs(d).toFixed(1) + ' d', tableHead: ['Factor', 'Effect (days)', '95% CI', 'p', 'q (BH)'],
  });
}
let raf = null;
function rerender() { cancelAnimationFrame(raf); raf = requestAnimationFrame(renderAll); }
if (window.d3) renderAll();
window.addEventListener('resize', rerender);
matchMedia('(prefers-color-scheme: dark)').addEventListener('change', rerender);
new MutationObserver(rerender).observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] });
