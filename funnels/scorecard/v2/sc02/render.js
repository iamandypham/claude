// Render SC02 N2-style plain cards at 1080x1350 (Jeremy 13 Nov: bigger type, 4:5, no example card). Usage: node render.js
const { chromium } = require('playwright'); const fs = require('fs');
const ads = JSON.parse(fs.readFileSync(__dirname + '/ads.json', 'utf8'));
const esc = s => s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/'/g,'’');
(async () => {
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1080, height: 1350 }, deviceScaleFactor: 1 });
  for (const a of ads) {
    const [call, ...rest] = a.card.split(': ');
    const html = `<!doctype html><html><head><meta charset="utf-8"><link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap" rel="stylesheet"><style>
      html,body{margin:0;width:1080px;height:1350px;background:${a.bg};display:flex;align-items:center;justify-content:center}
      p{font-family:Inter,sans-serif;color:#fff;font-size:66px;line-height:1.28;font-weight:400;text-align:center;max-width:860px;margin:0;letter-spacing:-.01em;text-wrap:balance}
      b{font-weight:600}</style></head><body><p><b>${esc(call)}:</b> ${esc(rest.join(': '))}</p></body></html>`;
    await p.setContent(html, { waitUntil: 'networkidle' }); await p.evaluate(() => document.fonts.ready);
    await p.screenshot({ path: `${__dirname}/SC02-${a.id}.png` });
  }
  await b.close(); console.log('ok', ads.length);
})();
