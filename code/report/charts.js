/* Charts for the "Same Case, Different Judge" report. Plain SVG via d3 (scales/axes only).
   Every chart: thin marks, hairline grid, hover tooltip (textContent only), keyboard focus, and a table twin. */
(function () {
  const css = (name) => getComputedStyle(document.documentElement).getPropertyValue(name).trim();
  const tip = document.createElement('div');
  tip.className = 'viz-tip'; tip.setAttribute('role', 'status'); tip.hidden = true;
  document.body.appendChild(tip);

  function showTip(evt, lines) {
    tip.replaceChildren();
    lines.forEach(([value, label], i) => {
      const row = document.createElement('div'); row.className = i === 0 ? 'tip-row tip-main' : 'tip-row';
      const v = document.createElement('strong'); v.textContent = value;
      const l = document.createElement('span'); l.textContent = label;
      row.append(v, l); tip.append(row);
    });
    tip.hidden = false;
    const r = tip.getBoundingClientRect();
    let x, y;
    if (evt.clientX !== undefined && evt.type.startsWith('pointer')) { x = evt.clientX + 14; y = evt.clientY + 14; }
    else { const b = evt.target.getBoundingClientRect(); x = b.right + 8; y = b.top; }
    if (x + r.width > window.innerWidth - 8) x = Math.max(8, x - r.width - 28);
    if (y + r.height > window.innerHeight - 8) y = Math.max(8, y - r.height - 28);
    tip.style.left = x + 'px'; tip.style.top = y + 'px';
  }
  function hideTip() { tip.hidden = true; }
  function bindTip(sel, linesFn) {
    sel.attr('tabindex', 0)
      .on('pointermove', (e, d) => showTip(e, linesFn(d)))
      .on('pointerleave', hideTip)
      .on('focus', (e, d) => showTip(e, linesFn(d)))
      .on('blur', hideTip);
  }

  function frame(el, height, margin) {
    el.replaceChildren();
    const width = Math.max(300, el.clientWidth || 640);
    const svg = d3.select(el).append('svg').attr('viewBox', `0 0 ${width} ${height}`).attr('width', '100%')
      .attr('role', 'img').attr('aria-label', el.dataset.label || '');
    const g = svg.append('g').attr('transform', `translate(${margin.l},${margin.t})`);
    return { svg, g, w: width - margin.l - margin.r, h: height - margin.t - margin.b, width };
  }
  function grid(g, x, h, ticks, fmt) {
    const ax = g.append('g').attr('class', 'axis').attr('transform', `translate(0,${h})`)
      .call(d3.axisBottom(x).ticks(ticks).tickSize(-h).tickFormat(fmt));
    ax.select('.domain').remove();
    ax.selectAll('line').attr('stroke', css('--grid'));
    ax.selectAll('text').attr('fill', css('--muted')).attr('dy', '1.1em');
    return ax;
  }
  function ygrid(g, y, w, ticks, fmt) {
    const ax = g.append('g').attr('class', 'axis').call(d3.axisLeft(y).ticks(ticks).tickSize(-w).tickFormat(fmt));
    ax.select('.domain').remove();
    ax.selectAll('line').attr('stroke', css('--grid'));
    ax.selectAll('text').attr('fill', css('--muted')).attr('dx', '-0.4em');
    return ax;
  }
  function table(el, headers, rows) {
    const host = document.getElementById(el.dataset.table);
    if (!host) return;
    host.replaceChildren();
    const t = document.createElement('table'); const thead = t.createTHead(); const hr = thead.insertRow();
    headers.forEach(h => { const th = document.createElement('th'); th.textContent = h; hr.append(th); });
    const tb = t.createTBody();
    rows.forEach(r => { const tr = tb.insertRow(); r.forEach(c => { const td = tr.insertCell(); td.textContent = c; }); });
    host.append(t);
  }
  const m1 = (d) => (d / 30).toFixed(2);
  const pct = (v) => (v * 100).toFixed(0) + '%';

  /* Strip plot: one row per group (court), one dot per judge. */
  function strip(el, rows, o) {
    const groups = o.groups || [...new Set(rows.map(r => r[o.group]))];
    const rowH = 46, margin = { t: 8, r: 24, b: 34, l: Math.min(118, (el.clientWidth || 600) * 0.28) };
    const { g, w, h } = frame(el, groups.length * rowH + margin.t + margin.b, margin);
    const ext = d3.extent(rows, r => r[o.value]);
    const pad = (ext[1] - ext[0]) * 0.06 || 1;
    const x = d3.scaleLinear().domain(o.domain || [ext[0] - pad, ext[1] + pad]).range([0, w]).nice();
    const y = d3.scaleBand().domain(groups).range([0, h]).padding(0.2);
    grid(g, x, h, Math.max(3, Math.floor(w / 90)), o.fmt);
    g.append('g').selectAll('text').data(groups).join('text')
      .attr('x', -10).attr('y', d => y(d) + y.bandwidth() / 2).attr('dy', '0.35em').attr('text-anchor', 'end')
      .attr('fill', css('--ink')).attr('class', 'lab').text(d => d);
    g.append('g').selectAll('line').data(groups).join('line')
      .attr('x1', 0).attr('x2', w).attr('y1', d => y(d) + y.bandwidth() / 2).attr('y2', d => y(d) + y.bandwidth() / 2)
      .attr('stroke', css('--grid'));
    if (o.mark) {
      g.append('g').selectAll('line').data(groups.filter(gr => o.mark[gr] !== undefined)).join('line')
        .attr('x1', d => x(o.mark[d])).attr('x2', d => x(o.mark[d])).attr('y1', d => y(d) + 2).attr('y2', d => y(d) + y.bandwidth() - 2)
        .attr('stroke', css('--ink')).attr('stroke-width', 2);
    }
    const jitter = (i) => ((i * 7919) % 11 - 5) / 5 * (y.bandwidth() * 0.22);
    const dots = g.append('g').selectAll('circle').data(rows).join('circle')
      .attr('cx', r => x(r[o.value])).attr('cy', (r, i) => y(r[o.group]) + y.bandwidth() / 2 + jitter(i))
      .attr('r', 5).attr('fill', css('--s1')).attr('fill-opacity', 0.85).attr('stroke', css('--surface')).attr('stroke-width', 2)
      .attr('class', 'hit');
    bindTip(dots, o.tip);
    table(el, o.tableHead, o.tableRows(rows));
  }

  /* Multi-series line over an ordinal x (with markers). */
  function lines(el, series, o) {
    const margin = { t: 16, r: 110, b: 40, l: 48 };
    const { g, w, h } = frame(el, 300, margin);
    const x = d3.scalePoint().domain(o.x).range([0, w]).padding(0.3);
    const all = series.flatMap(s => s.values.map(v => v.y));
    const y = d3.scaleLinear().domain([0, d3.max(all) * 1.12]).range([h, 0]).nice();
    ygrid(g, y, w, 5, o.yfmt);
    const xa = g.append('g').attr('transform', `translate(0,${h})`).call(d3.axisBottom(x).tickSize(0).tickFormat(t => w < 460 ? String(t).split('-')[0].replace('+', '') + '+' : t));
    xa.select('.domain').attr('stroke', css('--axis'));
    xa.selectAll('text').attr('fill', css('--muted')).attr('dy', '1.3em');
    series.forEach((s, si) => {
      const col = css(s.color);
      g.append('path').datum(s.values).attr('fill', 'none').attr('stroke', col).attr('stroke-width', 2)
        .attr('stroke-linejoin', 'round').attr('stroke-linecap', 'round')
        .attr('d', d3.line().x(v => x(v.x)).y(v => y(v.y)));
      const pts = g.append('g').selectAll('circle').data(s.values).join('circle')
        .attr('cx', v => x(v.x)).attr('cy', v => y(v.y)).attr('r', 4.5).attr('fill', col)
        .attr('stroke', css('--surface')).attr('stroke-width', 2).attr('class', 'hit');
      bindTip(pts, v => [[o.yfmt(v.y), s.name], [v.x + ' mg/L', 'breath alcohol'], [v.n + ' cases', '']]);
      const last = s.values[s.values.length - 1];
      g.append('text').attr('x', x(last.x) + 10).attr('y', y(last.y)).attr('dy', '0.35em').attr('fill', css('--ink'))
        .attr('class', 'lab').text(s.name);
    });
    table(el, o.tableHead, o.tableRows(series));
  }

  /* Scatter with a 45-degree reference line. */
  function scatter(el, pts, o) {
    const margin = { t: 12, r: 16, b: 46, l: 54 };
    const size = Math.min(el.clientWidth || 480, 520);
    const { g, w, h } = frame(el, size, margin);
    const ext = d3.extent(pts.flatMap(p => [p.a, p.b])); const pad = (ext[1] - ext[0]) * 0.08;
    const x = d3.scaleLinear().domain([ext[0] - pad, ext[1] + pad]).range([0, w]).nice();
    const y = d3.scaleLinear().domain(x.domain()).range([h, 0]);
    grid(g, x, h, 5, o.fmt); ygrid(g, y, w, 5, o.fmt);
    g.append('line').attr('x1', x(x.domain()[0])).attr('y1', y(x.domain()[0])).attr('x2', x(x.domain()[1])).attr('y2', y(x.domain()[1]))
      .attr('stroke', css('--axis')).attr('stroke-width', 1.5);
    g.append('text').attr('x', w - 4).attr('y', h + 38).attr('text-anchor', 'end').attr('fill', css('--muted')).attr('class', 'small').text(o.xlab);
    g.append('text').attr('transform', 'rotate(-90)').attr('x', 0).attr('y', -42).attr('text-anchor', 'end').attr('fill', css('--muted')).attr('class', 'small').text(o.ylab);
    const dots = g.append('g').selectAll('circle').data(pts).join('circle')
      .attr('cx', p => x(p.a)).attr('cy', p => y(p.b)).attr('r', 4.5).attr('fill', css('--s1')).attr('fill-opacity', 0.8)
      .attr('stroke', css('--surface')).attr('stroke-width', 2).attr('class', 'hit');
    bindTip(dots, o.tip);
    table(el, o.tableHead, o.tableRows(pts));
  }

  /* Histogram of a null distribution with the observed value marked. */
  function nullHist(el, hist, edges, observed, o) {
    const margin = { t: 28, r: 20, b: 40, l: 44 };
    const { g, w, h } = frame(el, 240, margin);
    const bins = hist.map((c, i) => ({ c, x0: edges[i], x1: edges[i + 1] }));
    const x = d3.scaleLinear().domain([0, Math.max(observed * 1.08, edges[edges.length - 1])]).range([0, w]).nice();
    const y = d3.scaleLinear().domain([0, d3.max(hist)]).range([h, 0]).nice();
    grid(g, x, h, 5, o.fmt);
    const bars = g.append('g').selectAll('rect').data(bins).join('rect')
      .attr('x', b => x(b.x0) + 1).attr('width', b => Math.max(1, x(b.x1) - x(b.x0) - 2))
      .attr('y', b => y(b.c)).attr('height', b => h - y(b.c)).attr('fill', css('--neutral-mark')).attr('rx', 2).attr('class', 'hit');
    bindTip(bars, b => [[b.c + ' shuffles', ''], [o.fmt(b.x0) + '–' + o.fmt(b.x1), 'between-judge variance']]);
    g.append('line').attr('x1', x(observed)).attr('x2', x(observed)).attr('y1', -6).attr('y2', h).attr('stroke', css('--s2')).attr('stroke-width', 2);
    g.append('circle').attr('cx', x(observed)).attr('cy', -6).attr('r', 5).attr('fill', css('--s2')).attr('stroke', css('--surface')).attr('stroke-width', 2);
    g.append('text').attr('x', x(observed) - 8).attr('y', -12).attr('text-anchor', 'end').attr('fill', css('--ink')).attr('class', 'lab').text(o.obsLabel);
    table(el, ['Shuffled-data variance (bin)', 'Count of shuffles'], bins.map(b => [o.fmt(b.x0) + '–' + o.fmt(b.x1), String(b.c)]).concat([['Observed', o.fmt(observed)]]));
  }

  /* Coefficient plot around zero. */
  function coefs(el, rows, o) {
    const margin = { t: 10, r: 24, b: 40, l: Math.min(250, (el.clientWidth || 600) * 0.42) };
    const { g, w, h } = frame(el, rows.length * 38 + 50, margin);
    const lim = d3.max(rows, r => Math.max(Math.abs(r.lo), Math.abs(r.hi))) * 1.1;
    const x = d3.scaleLinear().domain([-lim, lim]).range([0, w]).nice();
    const y = d3.scaleBand().domain(rows.map(r => r.term)).range([0, h - 10]).padding(0.3);
    grid(g, x, h - 10, 5, o.fmt);
    g.append('line').attr('x1', x(0)).attr('x2', x(0)).attr('y1', 0).attr('y2', h - 10).attr('stroke', css('--axis')).attr('stroke-width', 1.5);
    g.append('g').selectAll('text').data(rows).join('text').attr('x', -10).attr('y', r => y(r.term) + y.bandwidth() / 2)
      .attr('dy', '0.35em').attr('text-anchor', 'end').attr('fill', css('--ink')).attr('class', 'lab').text(r => r.term);
    g.append('g').selectAll('line').data(rows).join('line').attr('x1', r => x(r.lo)).attr('x2', r => x(r.hi))
      .attr('y1', r => y(r.term) + y.bandwidth() / 2).attr('y2', r => y(r.term) + y.bandwidth() / 2)
      .attr('stroke', css('--s1')).attr('stroke-width', 2).attr('stroke-linecap', 'round');
    const pts = g.append('g').selectAll('circle').data(rows).join('circle').attr('cx', r => x(r.coef)).attr('cy', r => y(r.term) + y.bandwidth() / 2)
      .attr('r', 5).attr('fill', css('--s1')).attr('stroke', css('--surface')).attr('stroke-width', 2).attr('class', 'hit');
    bindTip(pts, r => [[o.fmt(r.coef), r.term], ['95% CI ' + o.fmt(r.lo) + ' to ' + o.fmt(r.hi), ''], ['q = ' + r.q.toFixed(2), 'after multiple-testing correction']]);
    table(el, o.tableHead, rows.map(r => [r.term, o.fmt(r.coef), o.fmt(r.lo) + ' to ' + o.fmt(r.hi), r.p.toFixed(3), r.q.toFixed(2)]));
  }

  /* Range plot: per court, min-max whisker, IQR bar, median tick. */
  function ranges(el, rows, o) {
    const margin = { t: 8, r: 24, b: 40, l: Math.min(118, (el.clientWidth || 600) * 0.28) };
    const { g, w, h } = frame(el, rows.length * 30 + 52, margin);
    const lim = d3.max(rows, r => Math.max(Math.abs(r.min), Math.abs(r.max))) * 1.05;
    const x = d3.scaleLinear().domain([-lim, lim]).range([0, w]).nice();
    const y = d3.scaleBand().domain(rows.map(r => r.court)).range([0, h - 12]).padding(0.35);
    grid(g, x, h - 12, 6, o.fmt);
    g.append('line').attr('x1', x(0)).attr('x2', x(0)).attr('y1', 0).attr('y2', h - 12).attr('stroke', css('--axis'));
    g.append('g').selectAll('text').data(rows).join('text').attr('x', -10).attr('y', r => y(r.court) + y.bandwidth() / 2)
      .attr('dy', '0.35em').attr('text-anchor', 'end').attr('fill', css('--ink')).attr('class', 'lab').text(r => r.court);
    const cy = r => y(r.court) + y.bandwidth() / 2;
    g.append('g').selectAll('line').data(rows).join('line').attr('x1', r => x(r.min)).attr('x2', r => x(r.max)).attr('y1', cy).attr('y2', cy)
      .attr('stroke', css('--neutral-mark')).attr('stroke-width', 2);
    const bars = g.append('g').selectAll('rect').data(rows).join('rect').attr('x', r => x(r.p25)).attr('width', r => Math.max(2, x(r.p75) - x(r.p25)))
      .attr('y', r => cy(r) - 6).attr('height', 12).attr('rx', 4).attr('fill', css('--s1')).attr('class', 'hit');
    g.append('g').selectAll('line.med').data(rows).join('line').attr('x1', r => x(r.median)).attr('x2', r => x(r.median))
      .attr('y1', r => cy(r) - 8).attr('y2', r => cy(r) + 8).attr('stroke', css('--surface')).attr('stroke-width', 2);
    bindTip(bars, r => [[o.fmt(r.min) + ' to ' + o.fmt(r.max), r.court + ': range of judge effects'], ['middle half ' + o.fmt(r.p25) + ' to ' + o.fmt(r.p75), ''], [r.judges + ' judges · ' + r.cases + ' cases', '']]);
    table(el, ['Court', 'Judges (30+ cases)', 'Cases', 'Most lenient', '25th pct', 'Median', '75th pct', 'Harshest'],
      rows.map(r => [r.court, r.judges, r.cases, o.fmt(r.min), o.fmt(r.p25), o.fmt(r.median), o.fmt(r.p75), o.fmt(r.max)]));
  }

  /* Horizontal bars (one series), value at the tip. */
  function hbars(el, rows, o) {
    const margin = { t: 6, r: o.right || 64, b: 30, l: Math.min(o.left || 118, (el.clientWidth || 600) * 0.4) };
    const { g, w, h } = frame(el, rows.length * 28 + 40, margin);
    const x = d3.scaleLinear().domain(o.domain || [0, d3.max(rows, r => r.v) * 1.05]).range([0, w]).nice();
    const y = d3.scaleBand().domain(rows.map(r => r.k)).range([0, h]).padding(0.3);
    grid(g, x, h, 5, o.fmt);
    g.append('g').selectAll('text').data(rows).join('text').attr('x', -10).attr('y', r => y(r.k) + y.bandwidth() / 2)
      .attr('dy', '0.35em').attr('text-anchor', 'end').attr('fill', css('--ink')).attr('class', 'lab').text(r => r.k);
    const x0 = x(o.domain ? o.domain[0] : 0);
    const bars = g.append('g').selectAll('path').data(rows).join('path')
      .attr('d', r => { const bw = Math.min(y.bandwidth(), 24), yy = y(r.k) + (y.bandwidth() - bw) / 2, xe = x(r.v), rr = Math.min(4, (xe - x0) / 2);
        return `M${x0},${yy}H${xe - rr}Q${xe},${yy} ${xe},${yy + rr}V${yy + bw - rr}Q${xe},${yy + bw} ${xe - rr},${yy + bw}H${x0}Z`; })
      .attr('fill', r => r.hl ? css('--s2') : css('--s1')).attr('class', 'hit');
    g.append('g').selectAll('text.v').data(rows).join('text').attr('x', r => x(r.v) + 6).attr('y', r => y(r.k) + y.bandwidth() / 2)
      .attr('dy', '0.35em').attr('fill', css('--muted')).attr('class', 'small num').text(r => r.label || o.fmt(r.v));
    bindTip(bars, r => [[r.label || o.fmt(r.v), r.k], [r.note || '', '']]);
    table(el, o.tableHead, rows.map(r => [r.k, r.label || o.fmt(r.v), r.note || '']));
  }

  /* Stacked 100% bar (variance decomposition). */
  function stack(el, parts, o) {
    const margin = { t: 6, r: 8, b: 6, l: 8 };
    const { g, w } = frame(el, 64, margin);
    let acc = 0;
    const x = d3.scaleLinear().domain([0, 1]).range([0, w]);
    const segs = parts.map(p => { const s = { ...p, x0: acc, x1: acc + p.v }; acc += p.v; return s; });
    const rects = g.selectAll('rect').data(segs).join('rect').attr('x', s => x(s.x0) + (s.x0 > 0 ? 1 : 0)).attr('width', s => Math.max(1, x(s.x1) - x(s.x0) - (s.x0 > 0 ? 2 : 0)))
      .attr('y', 4).attr('height', 40).attr('rx', 4).attr('fill', s => css(s.color)).attr('class', 'hit');
    bindTip(rects, s => [[pct(s.v), s.k], [s.note || '', '']]);
    g.selectAll('text').data(segs.filter(s => x(s.x1) - x(s.x0) > 70)).join('text').attr('x', s => x(s.x0) + 10).attr('y', 29)
      .attr('fill', s => s.light ? css('--ink') : '#ffffff').attr('class', 'lab').text(s => pct(s.v));
    table(el, ['Component', 'Share of sentence variation'], segs.map(s => [s.k, pct(s.v)]));
  }

  window.Viz = { strip, lines, scatter, nullHist, coefs, ranges, hbars, stack, m1, pct };
})();
