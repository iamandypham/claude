// Checks routeOf() in a page file against Andy's booking rule (8 Nov 2026), over every answer combination.
// Rule: qualified = community income OR a following OR $10K+/month trading. No cash requirement. "Still learning" keeps its own route.
// Usage: node test_rule.js <page.html>
const fs = require('fs'), vm = require('vm');
const html = fs.readFileSync(process.argv[2], 'utf8');
const src = html.match(/function routeOf\(a\)\{[\s\S]*?\n\}/)[0];
const ctx = {}; vm.createContext(ctx); vm.runInContext(src + '; this.routeOf = routeOf;', ctx);
const opt = (id) => { const m = html.match(new RegExp('\\{id:"' + id + '"[\\s\\S]*?options:\\[([\\s\\S]*?)\\]\\}')); return [...m[1].matchAll(/v:"([^"]+)"/g)].map(x => x[1]); };
const who = opt('who'), revenue = opt('revenue'), trading = opt('trading'), audience = opt('audience'), liquid = opt('liquid');
let n = 0, bad = [];
for (const w of who) for (const r of revenue) for (const t of [undefined, ...trading]) for (const au of audience) for (const l of [undefined, ...liquid]) {
  const tradingAsked = r === 'none' || r === 'u5';
  if (!tradingAsked && t !== undefined) continue;          // the page only asks trading when revenue is none or under $5K
  const a = { who: w, revenue: r, trading: t, audience: au, liquid: l };
  const want = w === 'early' ? 'early' : ((r !== 'none') || w === 'creator' || au !== 'none' || ['10to30', '30p'].includes(t)) ? 'qualified' : 'nurture';
  const got = ctx.routeOf(a); n++;
  if (got !== want) bad.push(JSON.stringify(a) + ' got ' + got + ' want ' + want);
}
console.log('audience options:', audience.join(', '));
console.log('combinations checked:', n, '| mismatches:', bad.length);
bad.slice(0, 10).forEach(x => console.log('  ' + x));
// Cash has no effect: same answers with every funds answer route the same.
let cashFx = 0;
for (const w of who) for (const r of revenue) for (const au of audience) { const s = new Set(liquid.map(l => ctx.routeOf({ who: w, revenue: r, audience: au, liquid: l }))); if (s.size > 1) cashFx++; }
console.log('answer sets where the funds answer changes the route:', cashFx);
process.exit(bad.length || cashFx ? 1 : 0);
