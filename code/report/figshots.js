// Screenshot every chart in a built report page, light and dark, at 2x.  node figshots.js PAGE.html OUTDIR
const { chromium } = require('/opt/node-tools/node_modules/playwright');
const fs = require('fs');
(async () => {
  const src = fs.readFileSync(process.argv[2], 'utf8'); const out = process.argv[3];
  fs.mkdirSync(out, { recursive: true });
  const tmp = out + '/_page.html';
  fs.writeFileSync(tmp, `<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><style>body{margin:0}[hidden]{display:none!important}</style></head><body>${src}</body></html>`);
  const b = await chromium.launch();
  for (const scheme of ['light', 'dark']) {
    const ctx = await b.newContext({ viewport: { width: 1000, height: 900 }, deviceScaleFactor: 2, colorScheme: scheme });
    const p = await ctx.newPage();
    await p.goto('file://' + tmp, { waitUntil: 'networkidle' }); await p.waitForTimeout(1500);
    const ids = await p.$$eval('.chart[id]', els => els.map(e => e.id));
    for (const id of ids) {
      const box = await p.$eval('#' + id, e => { const c = e.getBoundingClientRect(), f = e.closest('figure').getBoundingClientRect();
        return { x: f.left + 4, y: c.top + window.scrollY - 6, width: f.width - 8, height: c.height + 12 }; });
      await p.screenshot({ path: `${out}/${id}-${scheme}.png`, clip: box, fullPage: true });
    }
    console.log(scheme, ids.join(','));
    await ctx.close();
  }
  fs.unlinkSync(tmp); await b.close();
})();
