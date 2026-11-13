// Scorecard v2 email screen -> GHL (built 13 Nov 2026). Email-only partial. No phone, so no texts or calls.
const j = $input.first().json || {};
let b = j.body;
if (typeof b === 'string') { try { b = JSON.parse(b); } catch (e) { b = {}; } }
if (!b || typeof b !== 'object') b = {};
if (!b.email && Object.keys(b).length === 1) { try { b = JSON.parse(Object.keys(b)[0]); } catch (e) {} }
const email = String(b.email || '').trim().toLowerCase();
const ok = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(email);
const test = b.test === true || /@example\.com$/i.test(email) || /^zz/i.test(email) || /[?&]bgtest=1/.test(String(b.page_url || ''));
const hdr = j.headers || {};
const ip = String(hdr['x-forwarded-for'] || hdr['x-real-ip'] || '').split(',')[0].trim();
const at = b.attribution || {};
const CF = { fbclid: 'JWTR0vAJRxMvAG6OlBif', fbp: 'RzbVjmM23gs65mEuKI19', fbc: 'c4AMd3QYRikJyNblx0eu', ua: 'pcY63eAnyn4Dv8UetO3O', ip: '9qj5KAwFui5fJpkh9YB5', ad_id: 'yyh23HPJJDb8YloY6gQB', adset_id: 'VqoSmEtBb0zHWBWqBpuN', campaign_id: 'kPnkh0heKr2HJrce6Dno', utm_source: 'smaUfk1Iu079oHCFMPaG', utm_campaign: 'G3SdU90aQCbDlO98C9IP', utm_content: 'PMfPo0K4d3v3DLf1Ncrn', callix_sid: 'rYIQSt8mCpDfUm7nAmz3' };
const customFields = [];
const put = (id, v) => { v = String(v == null ? '' : v).trim(); if (v && !/\{\{|%7B%7B/i.test(v)) customFields.push({ id, field_value: v }); };
put(CF.fbclid, b.fbclid); put(CF.fbp, b.fbp); put(CF.fbc, b.fbc); put(CF.ua, b.ua); put(CF.ip, ip);
for (const k of ['ad_id', 'adset_id', 'campaign_id', 'utm_source', 'utm_campaign', 'utm_content', 'callix_sid']) put(CF[k], at[k]);
const tags = ['scorecard-v2', 'scorecard-partial'];
if (test) tags.push('scorecard-test', 'dialer-off');
return [{ json: { ok, test, email, lead_id: String(b.lead_id || ''), page_url: String(b.page_url || 'https://businessgrowr.com/scorecard').split('?')[0], fbp: String(b.fbp || ''), fbc: String(b.fbc || ''), fbclid: String(b.fbclid || ''), ip, ua: String(b.ua || ''), tags,
  upsertBody: { locationId: 'F8y82aHd3V0Y4Y2ccET6', email, source: 'Scorecard v2 partial', customFields } } }];
