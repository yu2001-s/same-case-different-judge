/* Extra chart types for the combined report (same conventions as charts.js: thin marks, hairline grid,
   tooltip + keyboard focus, and a table twin). Depends on window.Viz from charts.js for shared helpers. */
(function () {
  const css = (name) => getComputedStyle(document.documentElement).getPropertyValue(name).trim();
  const tip = document.querySelector('.viz-tip');
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
  const hideTip = () => { tip.hidden = true; };
  function bindTip(sel, fn) {
    sel.attr('tabindex', 0).on('pointermove', (e, d) => showTip(e, fn(d))).on('pointerleave', hideTip)
      .on('focus', (e, d) => showTip(e, fn(d))).on('blur', hideTip);
  }
  function frame(el, height, margin) {
    el.replaceChildren();
    const width = Math.max(300, el.clientWidth || 640);
    const svg = d3.select(el).append('svg').attr('viewBox', `0 0 ${width} ${height}`).attr('width', '100%')
      .attr('role', 'img').attr('aria-label', el.dataset.label || '');
    const g = svg.append('g').attr('transform', `translate(${margin.l},${margin.t})`);
    return { svg, g, w: width - margin.l - margin.r, h: height - margin.t - margin.b, width };
  }
  function xgrid(g, x, h, ticks, fmt) {
    const ax = g.append('g').attr('class', 'axis').attr('transform', `translate(0,${h})`).call(d3.axisBottom(x).ticks(ticks).tickSize(-h).tickFormat(fmt));
    ax.select('.domain').remove(); ax.selectAll('line').attr('stroke', css('--grid')); ax.selectAll('text').attr('fill', css('--muted')).attr('dy', '1.1em');
  }
  function ygrid(g, y, w, ticks, fmt) {
    const ax = g.append('g').attr('class', 'axis').call(d3.axisLeft(y).ticks(ticks).tickSize(-w).tickFormat(fmt));
    ax.select('.domain').remove(); ax.selectAll('line').attr('stroke', css('--grid')); ax.selectAll('text').attr('fill', css('--muted')).attr('dx', '-0.4em');
  }
  function table(el, headers, rows) {
    const host = document.getElementById(el.dataset.table);
    if (!host) return;
    host.replaceChildren();
    const t = document.createElement('table'); const hr = t.createTHead().insertRow();
    headers.forEach(h => { const th = document.createElement('th'); th.textContent = h; hr.append(th); });
    const tb = t.createTBody();
    rows.forEach(r => { const tr = tb.insertRow(); r.forEach(c => { const td = tr.insertCell(); td.textContent = c; }); });
    host.append(t);
  }

  /* Time series on a numeric x, several series, optional vertical event markers, direct end labels. */
  function tlines(el, series, o) {
    const narrow = (el.clientWidth || 600) < 520;
    const margin = { t: 26, r: narrow ? 16 : 130, b: 40, l: 50 };
    const { g, w, h } = frame(el, o.height || 300, margin);
    const xs = series.flatMap(s => s.values.map(v => v.x));
    const x = d3.scaleLinear().domain(o.xdomain || d3.extent(xs)).range([0, w]);
    const ys = series.flatMap(s => s.values.map(v => v.y));
    const y = d3.scaleLinear().domain(o.ydomain || [Math.min(0, d3.min(ys)), d3.max(ys) * 1.12]).range([h, 0]).nice();
    ygrid(g, y, w, 5, o.yfmt);
    const xa = g.append('g').attr('transform', `translate(0,${h})`).call(d3.axisBottom(x).ticks(Math.min(xs.length, Math.floor(w / 60))).tickSize(0).tickFormat(o.xfmt || d3.format('d')));
    xa.select('.domain').attr('stroke', css('--axis')); xa.selectAll('text').attr('fill', css('--muted')).attr('dy', '1.3em');
    (o.events || []).forEach(ev => {
      g.append('line').attr('x1', x(ev.x)).attr('x2', x(ev.x)).attr('y1', -8).attr('y2', h).attr('stroke', css('--axis')).attr('stroke-dasharray', '3 3');
      g.append('text').attr('x', x(ev.x) + 4).attr('y', -12).attr('fill', css('--muted')).attr('class', 'small').text(ev.label);
    });
    if (o.zero) g.append('line').attr('x1', 0).attr('x2', w).attr('y1', y(0)).attr('y2', y(0)).attr('stroke', css('--axis'));
    series.forEach(s => {
      const col = css(s.color);
      g.append('path').datum(s.values).attr('fill', 'none').attr('stroke', col).attr('stroke-width', 2).attr('stroke-linejoin', 'round')
        .attr('stroke-dasharray', s.dash ? '5 4' : null).attr('d', d3.line().x(v => x(v.x)).y(v => y(v.y)));
      const pts = g.append('g').selectAll('circle').data(s.values).join('circle').attr('cx', v => x(v.x)).attr('cy', v => y(v.y))
        .attr('r', 4).attr('fill', col).attr('stroke', css('--surface')).attr('stroke-width', 2).attr('class', 'hit');
      bindTip(pts, v => [[o.yfmt(v.y), s.name], [(o.xfmt || String)(v.x), o.xlab || ''], ...(v.note ? [[v.note, '']] : [])]);
      const last = s.values[s.values.length - 1];
      if (!narrow) g.append('text').attr('x', x(last.x) + 10).attr('y', y(last.y) + (s.dy || 0)).attr('dy', '0.35em').attr('fill', css('--ink')).attr('class', 'lab').text(s.name);
    });
    if (narrow) {
      const lg = d3.select(el).append('div').attr('class', 'legend');
      series.forEach(s => { const it = lg.append('span'); it.append('i').style('background', css(s.color)); it.append('span').text(s.name); });
    }
    if (o.ylab) g.append('text').attr('x', -44).attr('y', -12).attr('fill', css('--muted')).attr('class', 'small').text(o.ylab);
    table(el, o.tableHead || ['Series', 'x', 'Value'], series.flatMap(s => s.values.map(v => [s.name, (o.xfmt || String)(v.x), o.yfmt(v.y)])));
  }

  /* Dumbbell: per row, value a (hollow) and value b (filled) on a shared axis. */
  function dumbbell(el, rows, o) {
    const margin = { t: 30, r: 24, b: 36, l: Math.min(o.left || 190, (el.clientWidth || 600) * 0.42) };
    const { g, w, h } = frame(el, rows.length * 32 + 66, margin);
    const all = rows.flatMap(r => [r.a, r.b].concat(r.alo !== undefined ? [r.alo, r.ahi] : []));
    const x = d3.scaleLinear().domain(o.domain || [Math.min(0, d3.min(all)), d3.max(all) * 1.08]).range([0, w]).nice();
    const y = d3.scaleBand().domain(rows.map(r => r.k)).range([0, h]).padding(0.3);
    xgrid(g, x, h, 5, o.fmt);
    const cy = r => y(r.k) + y.bandwidth() / 2;
    g.append('g').selectAll('text').data(rows).join('text').attr('x', -10).attr('y', cy).attr('dy', '0.35em').attr('text-anchor', 'end')
      .attr('fill', css('--ink')).attr('class', 'lab').text(r => r.k);
    g.append('g').selectAll('line').data(rows).join('line').attr('x1', r => x(Math.min(r.a, r.b))).attr('x2', r => x(Math.max(r.a, r.b)))
      .attr('y1', cy).attr('y2', cy).attr('stroke', css('--neutral-mark')).attr('stroke-width', 2);
    const ca = css(o.colorA || '--s2'), cb = css(o.colorB || '--s1');
    const pa = g.append('g').selectAll('circle').data(rows).join('circle').attr('cx', r => x(r.a)).attr('cy', cy).attr('r', 5.5)
      .attr('fill', css('--surface')).attr('stroke', ca).attr('stroke-width', 2.5).attr('class', 'hit');
    const pb = g.append('g').selectAll('circle.b').data(rows).join('circle').attr('cx', r => x(r.b)).attr('cy', cy).attr('r', 5.5)
      .attr('fill', cb).attr('stroke', css('--surface')).attr('stroke-width', 2).attr('class', 'hit');
    bindTip(pa, r => [[o.fmt(r.a), o.labA], [r.k, ''], ...(r.note ? [[r.note, '']] : [])]);
    bindTip(pb, r => [[o.fmt(r.b), o.labB], [r.k, ''], ...(r.note ? [[r.note, '']] : [])]);
    const lg = g.append('g').attr('transform', 'translate(0,-20)');
    lg.append('circle').attr('cx', 6).attr('cy', 0).attr('r', 5).attr('fill', css('--surface')).attr('stroke', ca).attr('stroke-width', 2.5);
    const ta = lg.append('text').attr('x', 16).attr('y', 0).attr('dy', '0.35em').attr('fill', css('--ink')).attr('class', 'small').text(o.labA);
    let tw = o.labA.length * 7; try { tw = ta.node().getComputedTextLength() || tw; } catch (e) {}
    const off = 16 + tw + 22;
    lg.append('circle').attr('cx', off + 6).attr('cy', 0).attr('r', 5).attr('fill', cb);
    lg.append('text').attr('x', off + 16).attr('y', 0).attr('dy', '0.35em').attr('fill', css('--ink')).attr('class', 'small').text(o.labB);
    table(el, ['', o.labA, o.labB, ''], rows.map(r => [r.k, o.fmt(r.a), o.fmt(r.b), r.note || '']));
  }

  /* Coefficient plot (estimate with 95% interval) grouped by a heading per block. */
  function coefs2(el, rows, o) {
    const margin = { t: 10, r: 24, b: 40, l: Math.min(o.left || 240, (el.clientWidth || 600) * 0.46) };
    const { g, w, h } = frame(el, rows.length * 30 + 56, margin);
    const lim = o.lim || d3.max(rows, r => Math.max(Math.abs(r.lo), Math.abs(r.hi))) * 1.1;
    const x = d3.scaleLinear().domain([-lim, lim]).range([0, w]).nice();
    const y = d3.scaleBand().domain(rows.map((r, i) => i)).range([0, h - 10]).padding(0.25);
    xgrid(g, x, h - 10, 6, o.fmt);
    g.append('line').attr('x1', x(0)).attr('x2', x(0)).attr('y1', 0).attr('y2', h - 10).attr('stroke', css('--axis')).attr('stroke-width', 1.5);
    const cy = (r, i) => y(i) + y.bandwidth() / 2;
    g.append('g').selectAll('text').data(rows).join('text').attr('x', -10).attr('y', cy).attr('dy', '0.35em').attr('text-anchor', 'end')
      .attr('fill', css('--ink')).attr('class', 'lab').text(r => r.term);
    g.append('g').selectAll('line').data(rows).join('line').attr('x1', r => x(Math.max(-lim, r.lo))).attr('x2', r => x(Math.min(lim, r.hi)))
      .attr('y1', cy).attr('y2', cy).attr('stroke', r => css(r.color || '--s1')).attr('stroke-width', 2).attr('stroke-linecap', 'round');
    const pts = g.append('g').selectAll('circle').data(rows).join('circle').attr('cx', r => x(r.coef)).attr('cy', cy)
      .attr('r', 5).attr('fill', r => css(r.color || '--s1')).attr('stroke', css('--surface')).attr('stroke-width', 2).attr('class', 'hit');
    bindTip(pts, r => [[o.fmt(r.coef), r.term], ['95% interval ' + o.fmt(r.lo) + ' to ' + o.fmt(r.hi), ''], ...(r.note ? [[r.note, '']] : [])]);
    table(el, o.tableHead || ['Comparison', 'Estimate', '95% interval', 'Note'], rows.map(r => [r.term, o.fmt(r.coef), o.fmt(r.lo) + ' to ' + o.fmt(r.hi), r.note || '']));
  }

  Object.assign(window.Viz, { tlines, dumbbell, coefs2, showTip, hideTip });
})();
