const { chromium } = require('playwright'); const path = require('path');
(async () => {
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 390, height: 900 } }); const errs = [];
  p.on('pageerror', e => errs.push(String(e)));
  await p.route('**/*', r => {
    const u = r.request().url();
    if (u.startsWith('file:')) return r.continue();
    if (u === 'https://calendly.com/fake-sender') return r.fulfill({ status: 200, contentType: 'text/html', body: '<script>parent.postMessage({event:"calendly.event_scheduled",payload:{}},"*")</script>' });
    return r.fulfill({ status: 204, body: '' });
  });
  await p.goto('file://' + path.resolve(process.argv[2] || 'live.html'));
  await p.click('[data-action="begin"]'); await p.fill('#f-name', 'Zed'); await p.press('#f-name', 'Enter');
  const picks = [0, 2, 2, 1, 1, 3, 2, 2, 1, 3, 2, 0, 0, 0, 0];
  for (const k of picks) { await p.waitForTimeout(350); const o = await p.$$('#q-card .opt'); await o[k].click(); }
  await p.waitForTimeout(400); await p.fill('#f-email', 'zz@example.com'); await p.press('#f-email', 'Enter');
  await p.waitForTimeout(300); await p.fill('#f-phone', '+15550100000'); await p.press('#f-phone', 'Enter');
  await p.waitForSelector('#cal-live', { timeout: 8000 });
  await p.evaluate(() => { const f = document.createElement('iframe'); f.src = 'https://calendly.com/fake-sender'; document.body.appendChild(f); });
  await p.waitForTimeout(1500);
  const t = await p.$eval('#booked-h', e => e.textContent).catch(() => '');
  console.log('booked heading:', t, '| video card:', !!await p.$('.next .vid-card'), '| errors:', errs.length);
  await p.screenshot({ path: 'shot-booked.png', fullPage: true }); await b.close();
})();
