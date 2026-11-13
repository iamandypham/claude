// Local E2E of scorecard v2: network to n8n/Calendly/Meta is intercepted (nothing leaves). Usage: node test_v2.js <element.html> <outdir> <liquidIndex>
const { chromium, devices } = require('playwright'); const fs = require('fs');
const [,, file, out, liqIdx] = process.argv;
(async () => {
  const el = fs.readFileSync(file, 'utf8');
  const html = '<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head><body>' + el + '</body></html>';
  const b = await chromium.launch(); const c = await b.newContext({ ...devices['iPhone 13'] }); const p = await c.newPage();
  const posts = []; const errors = [];
  p.on('pageerror', e => errors.push(String(e)));
  await p.route('**/*', async r => {
    const u = r.request().url();
    if (u.startsWith('https://scorecard.test/')) return r.fulfill({ status: 200, contentType: 'text/html', body: html });
    if (/n8n\.cloud\/webhook/.test(u)) { posts.push({ url: u.split('/webhook/')[1], body: r.request().postData() }); return r.fulfill({ status: 200, body: '{}' }); }
    if (/fonts\.(googleapis|gstatic)\.com/.test(u)) return r.continue();
    return r.fulfill({ status: 204, body: '' });
  });
  await p.goto('https://scorecard.test/scorecard?bgtest=1&utm_source=facebook&utm_campaign=SC01-test'); await p.waitForTimeout(800);
  await p.screenshot({ path: out + '/01-intro.png' });
  const vis = async () => (await p.evaluate(() => [...document.querySelectorAll('.view')].filter(v => !v.hidden).map(v => v.dataset.view).join(',')));
  const log = [];
  log.push('view on load: ' + await vis());
  await p.click('[data-action=begin]'); await p.waitForTimeout(500);
  const choose = (t) => /paid trading community/.test('') ? 0 : 0;
  const want = (t) => {
    if (/describes you/i.test(t)) return 'paid trading community';
    if (/bring in a month/i.test(t)) return 'Under $5K';
    if (/follow you/i.test(t)) return process.env.MODE === 'nurture' ? 'No following' : '1,000 to 50,000';
    if (/liquid/i.test(t)) return Number(liqIdx);
    return 0;
  };
  let lastT = '', same = 0;
  for (let guard = 0; guard < 60; guard++) {
    const view = await vis(); if (view !== 'quiz') { log.push('left quiz -> ' + view); break; }
    const t = (await p.textContent('#q-title').catch(()=>'')).trim();
    if (t === lastT) same++; else { same = 0; lastT = t; }
    if (same > 4) { log.push('STUCK at ' + t); break; }
    const cnt = (await p.textContent('#q-count').catch(()=>'')).trim();
    if (await p.locator('#q-card input').count()) {
      const val = /email/i.test(t) || /send it/i.test(await p.textContent('#q-card')) ? 'zztest.v2@example.com' : /name/i.test(t) ? 'Zztest' : '+1 555 010 0199';
      log.push('FIELD: ' + t + ' = ' + val + ' | counter="' + cnt + '"');
      if (/score is almost ready/i.test(t)) await p.screenshot({ path: out + '/02-email.png' });
      await p.fill('#q-card input', val); await p.press('#q-card input', 'Enter'); await p.waitForTimeout(600); continue;
    }
    const opts = p.locator('#q-card .opt'); const n = await opts.count();
    if (n && same === 0) {
      const w = want(t); let idx = 0;
      if (typeof w === 'number') idx = w; else for (let k = 0; k < n; k++) if ((await opts.nth(k).textContent()).includes(w)) { idx = k; break; }
      log.push('Q: ' + t + ' -> ' + (await opts.nth(idx).textContent()).replace(/\s+/g,' ').trim().slice(0, 50) + ' | counter="' + cnt + '"');
      await opts.nth(idx).click(); await p.waitForTimeout(500); continue;
    }
    const btns = p.locator('#q-card button:not(.opt):not([disabled])');
    if (await btns.count()) { log.push('BTN on: ' + t.slice(0,60) + ' -> ' + (await btns.first().textContent()).trim().slice(0,30)); await btns.first().click(); await p.waitForTimeout(500); continue; }
    await p.waitForTimeout(400);
  }
  await p.waitForTimeout(4500);
  log.push('final view: ' + await vis());
  log.push('calendar present: ' + (await p.locator('#cal-live').count()));
  await p.screenshot({ path: out + '/03-result.png', fullPage: true });
  const lead = posts.find(x => /bg-scorecard-ghl/.test(x.url));
  log.push('posts: ' + posts.map(x => x.url).join(', '));
  if (lead) { const j = JSON.parse(lead.body); log.push('lead route=' + j.route + ' test=' + j.test + ' liquid=' + JSON.stringify((j.answers||{}).liquid || j.liquid) ); fs.writeFileSync(out + '/lead-payload.json', JSON.stringify(j, null, 2)); }
  const partialEmail = posts.filter(x => /partial/.test(x.url)).map(x => JSON.parse(x.body)).find(x => x.q === 'email');
  log.push('partial email post: ' + (partialEmail ? 'yes, test=' + partialEmail.test : 'no'));
  log.push('page errors: ' + JSON.stringify(errors));
  fs.writeFileSync(out + '/log.txt', log.join('\n')); console.log(log.join('\n'));
  await b.close();
})();
