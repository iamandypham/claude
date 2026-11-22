// Local test of the live page. All outside requests are intercepted: nothing reaches n8n, YouTube, Calendly or any pixel.
const { chromium } = require('playwright');
const path = require('path');
const file = 'file://' + path.resolve(process.argv[2] || 'live.html');
const results = []; const ok = (name, cond, info) => results.push({ name, pass: !!cond, info });

const PATHS = {
  qualified: { who: 0, revenue: 2, audience: 2, goal: 1, reach: 1, capture: 3, nurture: 2, sales: 2, retention: 1, backend: 3, liquid: 2, timing: 0, partners: 1, source: 0, tiedown: 0 },
  nurture: { who: 2, revenue: 0, trading: 2, audience: 0, goal: 4, reach: 3, capture: 4, nurture: 3, sales: 4, retention: 4, backend: 4, liquid: 0, timing: 3, partners: 1, source: 1, tiedown: 1 },
  early: { who: 5, revenue: 0, trading: 0, audience: 0, goal: 0, reach: 3, capture: 4, nurture: 4, sales: 4, retention: 4, backend: 4, liquid: 0, timing: 3, partners: 1, source: 2, tiedown: 1 },
};

async function run(route, width) {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width, height: 900 } });
  const errors = []; const outside = []; const posts = [];
  page.on('pageerror', e => errors.push(String(e)));
  page.on('console', m => { if (m.type() === 'error') errors.push(m.text()); });
  await page.route('**/*', async r => {
    const u = r.request().url();
    if (u.startsWith('file:')) return r.continue();
    outside.push(u);
    if (u.includes('n8n.cloud/webhook/bg-scorecard-ghl')) { posts.push(r.request().postData()); return r.fulfill({ status: 200, body: '{}', headers: { 'access-control-allow-origin': '*' } }); }
    return r.fulfill({ status: 204, body: '' });
  });
  await page.goto(file + '?utm_source=fb&ad_id=111&adset_id=222&fbclid=ABC&campaign_id=333');
  await page.click('[data-action="begin"]');
  await page.fill('#f-name', 'Zed Test');
  await page.press('#f-name', 'Enter');
  const p = PATHS[route];
  for (let i = 0; i < 20; i++) {
    await page.waitForTimeout(350);
    const st = await page.evaluate(() => { const t = document.querySelector('#q-title'); return t ? t.textContent : ''; });
    if (await page.$('#f-email')) break;
    const ids = ['who','revenue','trading','audience','goal','reach','capture','nurture','sales','retention','backend','liquid','timing','partners','source','tiedown'];
    // find which question by matching option count is unreliable; use the internal step via title keywords
    const map = [['describes you','who'],['bring in a month','revenue'],['own trading','trading'],['follow you','audience'],['main thing','goal'],['find you','reach'],['happens next','capture'],['what do they get','nurture'],['become paying','sales'],['first week','retention'],['Besides the monthly','backend'],['liquid','liquid'],['get started','timing'],['decision-making','partners'],['come across','source'],['Last one','tiedown']];
    const hit = map.find(m => st.includes(m[0]));
    if (!hit) throw new Error('unknown question: ' + st);
    const opts = await page.$$('#q-card .opt');
    await opts[p[hit[1]]].click();
  }
  await page.fill('#f-email', 'zz.scorecard.test@example.com');
  await page.press('#f-email', 'Enter');
  await page.waitForTimeout(400);
  const consent = await page.$eval('.consent', e => e.innerHTML);
  ok(`${route}@${width} consent links`, consent.includes('businessgrowr.com/privacy') && consent.includes('businessgrowr.com/terms'));
  await page.fill('#f-phone', '+1 555 010 9999');
  await page.press('#f-phone', 'Enter');
  await page.waitForSelector('#res-title', { timeout: 8000 });
  await page.waitForTimeout(800);
  ok(`${route}@${width} one lead POST`, posts.length === 1, posts.length);
  const body = JSON.parse(posts[0] || '{}');
  ok(`${route}@${width} payload route`, body.route === route, body.route);
  ok(`${route}@${width} payload test flag`, body.test === true);
  ok(`${route}@${width} payload attribution`, body.attribution && body.attribution.ad_id === '111' && body.attribution.adset_id === '222' && body.fbclid === 'ABC' && /^fb\.1\.\d+\.ABC$/.test(body.fbc), JSON.stringify(body.attribution));
  ok(`${route}@${width} payload scores`, typeof body.score === 'number' && Object.keys(body.part_scores).length === 6 && body.biggest_leak);
  ok(`${route}@${width} payload contact`, body.name === 'Zed' && body.email === 'zz.scorecard.test@example.com' && body.phone);
  const iframe = await page.$eval('#v-result', el => { const f = el.querySelector('.vp-frame iframe'); return f ? f.getAttribute('src') : ''; });
  const cal = await page.$eval('#v-result', el => { const c = el.querySelector('.calendly-inline-widget'); return c ? c.getAttribute('data-url') : ''; });
  const lf = await page.$eval('#v-result', el => el.textContent.includes('Leak Finder'));
  ok(`${route}@${width} no Leak Finder`, !lf);
  if (route === 'qualified') {
    ok(`${route}@${width} player nocookie at start`, /youtube-nocookie\.com\/embed\/\w+\?rel=0.*&start=\d+/.test(iframe), iframe);
    ok(`${route}@${width} calendly prefilled`, cal.startsWith('https://calendly.com/d/dvtq-vgz-stw/dfy-guarantee-demo-meeting-bg-aaf?') && cal.includes('name=Zed') && cal.includes('email=zz.scorecard.test%40example.com') && cal.includes('a1=%2B15550109999') && cal.includes('utm_source=fb') && cal.includes('salesforce_uuid=bg1.111.222.ABC'), cal);
    const order = await page.$eval('#v-result', el => { const f = el.querySelector('.vp-frame'), c = el.querySelector('#cal-live'); return !!(f && c && (f.compareDocumentPosition(c) & Node.DOCUMENT_POSITION_FOLLOWING)); });
    ok(`${route}@${width} player above calendar`, order);
    await page.evaluate(() => window.postMessage({ event: 'calendly.event_scheduled', payload: {} }, '*'));
    await page.waitForTimeout(300);
    const booked0 = await page.$('#booked-h');
    ok(`${route}@${width} same-origin message ignored`, !booked0);
  } else if (route === 'nurture') {
    ok(`${route}@${width} player shown`, /youtube-nocookie/.test(iframe), iframe);
    ok(`${route}@${width} no calendar`, !cal);
  } else {
    ok(`${route}@${width} no player, no calendar`, !iframe && !cal);
    ok(`${route}@${width} channel card`, await page.$eval('#v-result', el => !!el.querySelector('a[href="https://www.youtube.com/@BusinessGrowR"]')));
  }
  const sw = await page.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
  ok(`${route}@${width} no sideways scroll`, sw <= 0, sw);
  ok(`${route}@${width} no console errors`, errors.length === 0, errors.join(' | '));
  const bad = outside.filter(u => /facebook|whop|hyros|googletagmanager|google-analytics|callix/.test(u));
  ok(`${route}@${width} no pixel calls`, bad.length === 0, bad.join(','));
  await page.screenshot({ path: `shot-${route}-${width}.png`, fullPage: true });
  await browser.close();
}

(async () => {
  for (const r of ['qualified', 'nurture', 'early']) for (const w of [360, 1280]) await run(r, w);
  // vendor exit
  const browser = await chromium.launch(); const page = await browser.newPage({ viewport: { width: 390, height: 800 } });
  const posts = []; await page.route('**/*', r => { const u = r.request().url(); if (u.startsWith('file:')) return r.continue(); if (u.includes('webhook')) posts.push(u); return r.fulfill({ status: 204, body: '' }); });
  await page.goto(file); await page.click('[data-action="begin"]'); await page.fill('#f-name', 'Vee'); await page.press('#f-name', 'Enter'); await page.waitForTimeout(400);
  await (await page.$$('#q-card .opt'))[4].click(); await page.waitForTimeout(500);
  ok('vendor exit shown, nothing sent', await page.isVisible('#v-vendor') && posts.length === 0);
  await browser.close();
  const fails = results.filter(r => !r.pass);
  results.forEach(r => console.log((r.pass ? 'PASS ' : 'FAIL ') + r.name + (r.pass ? '' : '  ' + (r.info || ''))));
  console.log(`${results.length - fails.length}/${results.length} pass`);
})();
