// Render the report locally (wrapped like the artifact skeleton) and screenshot desktop/phone, light/dark.
const { chromium } = require(require('path').join(process.env.NODE_TOOLS, 'playwright'));
const fs = require('fs');
(async () => {
  const src = fs.readFileSync(process.argv[2], 'utf8');
  const page_html = `<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover"><style>:root{color-scheme:light}body{margin:0}img{max-width:100%}[hidden]{display:none!important}</style></head><body>${src}</body></html>`;
  const tmp = process.argv[3] + '/page.html'; fs.writeFileSync(tmp, page_html);
  const browser = await chromium.launch();
  for (const [name, vp, scheme] of [['desk-light', { width: 1280, height: 900 }, 'light'], ['desk-dark', { width: 1280, height: 900 }, 'dark'], ['phone-light', { width: 400, height: 860 }, 'light']]) {
    const ctx = await browser.newContext({ viewport: vp, colorScheme: scheme });
    const page = await ctx.newPage();
    const errs = [];
    page.on('console', m => { if (m.type() === 'error') errs.push(m.text()); });
    page.on('pageerror', e => errs.push(String(e)));
    await page.goto('file://' + tmp, { waitUntil: 'networkidle' });
    await page.waitForTimeout(1500);
    const overflow = await page.evaluate(() => document.documentElement.scrollWidth > window.innerWidth + 1);
    await page.screenshot({ path: `${process.argv[3]}/${name}.png`, fullPage: true });
    console.log(name, 'errors:', errs.length ? errs.join(' | ') : 'none', 'h-overflow:', overflow);
    await ctx.close();
  }
  await browser.close();
})();
