import { workflow, node, trigger, ifElse, expr } from '@n8n/workflow-sdk';

const GHL_CRED = { httpBearerAuth: { id: 'I9syQTyegPSmKR0a', name: 'GoHighLevel BG' } };
const GHL_HEADERS = { parameters: [
  { name: 'Version', value: '2021-07-28' },
  { name: 'Content-Type', value: 'application/json' },
  { name: 'Accept', value: 'application/json' },
] };

const hook = trigger({
  type: 'n8n-nodes-base.webhook',
  version: 2,
  config: {
    name: 'Scorecard Webhook',
    parameters: {
      httpMethod: 'POST',
      path: 'bg-scorecard-ghl',
      responseMode: 'onReceived',
      options: { allowedOrigins: 'https://businessgrowr.com,https://www.businessgrowr.com' },
    },
  },
});

const mapCode = `
// BG Scorecard -> GHL. Built 2026-11-08 side by side with y7Lksw9o5jJbetf9 (never edits it).
// LIVE = false: real (non-test) leads are only logged in this execution and NOT sent to GHL, Discord, the setter notify, Meta or Whop.
// Flip LIVE to true only on Andy's or Louis's typed go (the GHL upsert fires the opt-in first text to the lead).
const LIVE = false;
const j = $input.first().json || {};
let b = j.body;
if (typeof b === 'string') { try { b = JSON.parse(b); } catch (e) { b = {}; } }
if (!b || typeof b !== 'object') b = {};
if (!b.email && Object.keys(b).length === 1) { try { b = JSON.parse(Object.keys(b)[0]); } catch (e) {} }
const real = (v) => { const s = String(v == null ? '' : v).trim(); return (!s || /^x{3,}$/i.test(s) || /^_+$/.test(s) || s === 'null' || s === 'undefined' || /\\{\\{|%7B%7B/i.test(s)) ? '' : s; };
const email = real(b.email).toLowerCase();
const okEmail = /^[^\\s@]+@[^\\s@]+\\.[^\\s@]{2,}$/.test(email);
let digits = String(b.phone || '').replace(/\\D/g, '');
if (digits.length === 10) digits = '1' + digits;
const phone = digits.length >= 8 && digits.length <= 15 ? '+' + digits : '';
const test = b.test === true || /@example\\.com$/i.test(email) || /^zz/i.test(email) || /[?&]bgtest=1/.test(String(b.page_url || ''));
const route = ['qualified', 'nurture', 'early'].includes(b.route) ? b.route : 'nurture';
const ans = b.answers || {}, lab = b.answer_labels || {}, at = b.attribution || {}, ps = b.part_scores || {};
const hdr = j.headers || {};
const ip = real(String(hdr['x-forwarded-for'] || hdr['x-real-ip'] || '').split(',')[0]);
const ua = real(b.ua || hdr['user-agent']);
const day = new Intl.DateTimeFormat('en-CA', { timeZone: 'America/New_York', year: 'numeric', month: '2-digit', day: '2-digit' }).format(new Date());

const CF = {
  score: 'pPBfRFgquz2479DswrUS', leak: 'LqKKlOUNLZf3c1DGGeb5', route: 'G9qBavyN1gq4Rxu4zuei', parts: 'W2t3k6kkwkV6J1jy7lLU', video: 'xnsOYUL151iUyfkkwAnD', answers: '9VzV8XVJ7iTgvhuykqoP',
  situation: '5dhNyrTJbLKr2UenOZqN', liquid: 'qAxPDhVMTAMt2KlrxrAr', partners: 'EuPxciFU9NlsTMpc4wXe', selfReport: 'G0mmULOi3WTioex3NOPt', bizType: 's9gPHPtPs6WdoQZtooxX', startTiming: 'l5732eOGO42X7zUb5Zzg',
  fbclid: 'JWTR0vAJRxMvAG6OlBif', fbp: 'RzbVjmM23gs65mEuKI19', fbc: 'c4AMd3QYRikJyNblx0eu', ua: 'pcY63eAnyn4Dv8UetO3O', ip: '9qj5KAwFui5fJpkh9YB5',
  ad_id: 'yyh23HPJJDb8YloY6gQB', adset_id: 'VqoSmEtBb0zHWBWqBpuN', campaign_id: 'kPnkh0heKr2HJrce6Dno',
  utm_source: 'smaUfk1Iu079oHCFMPaG', utm_medium: 'gi6McGlx1H9dqlPNuk7e', utm_campaign: 'G3SdU90aQCbDlO98C9IP', utm_term: 'Y4MP5aM8PPgmKZ8IcdmH', utm_content: 'PMfPo0K4d3v3DLf1Ncrn',
  callix_sid: 'rYIQSt8mCpDfUm7nAmz3', twclid: 'wcrMskguF8sQpa8GzJ3v', gclid: 'dFWxciDXevZFl3wQGZ4x', gbraid: 'BNdULDDRLVCqPLXWjSvh', wbraid: 'uHGp2HNZSp1Us2TsimLo', ttclid: 'iR15diTaGWmvmzVm1cbj',
  wacid: 'Jm9bu4gqQA3MLE0tGG1W', bg_ch: 'V1oWhETUK1VzmlnGc8MW', utm_whop: 'AEQjZ3icG55f52M20ldF', waid: 'BEbIIPNTeUdTOUS8wGXC', wasid: 'wawCZoAlYEWVVehqCIa7',
};
// Quiz answers mapped onto the live application fields only where the meaning is the same.
const SITUATION = { owner: "I run a trading community that's already generating revenue", creator: 'I have a social media following I want to monetize as a trading educator' };
let situation = '';
if (ans.who === 'owner' && ans.revenue && ans.revenue !== 'none') situation = SITUATION.owner;
else if (ans.who === 'creator') situation = SITUATION.creator;
else if (['trader', 'signals', 'owner'].includes(ans.who) && ['10to30', '30p'].includes(ans.trading)) situation = "I'm a profitable trader making $10k+/month and I want to build a trading community";
const LIQ = ['Less Than $5k', '$5,000 to $10,000', '$10,000 to $20,000', '$20,000 to $50,000', '$50,000+'];
const liquid = LIQ.includes(lab.liquid) ? lab.liquid : '';
const partners = ans.partners === 'yes' ? 'Yes, adding them as guests below and they will show up to the call' : ans.partners === 'no' ? 'No, I make all of the decisions in my business.' : '';
const PART_LABEL = { reach: 'Reach', capture: 'Capture', nurture: 'Nurture', sales: 'Sales', retention: 'Onboarding', backend: 'Backend' };
const partsText = Object.keys(PART_LABEL).map((k) => PART_LABEL[k] + ' ' + (Number(ps[k]) || 0)).join(', ');
const ORDER = ['who', 'revenue', 'trading', 'audience', 'goal', 'reach', 'capture', 'nurture', 'sales', 'retention', 'backend', 'liquid', 'timing', 'partners', 'source', 'tiedown'];
const answersText = ORDER.filter((k) => ans[k] !== undefined).map((k) => k + ': ' + (lab[k] || ans[k])).join('\\n');
const videoText = b.video_id ? (b.video_title || '') + ' | https://youtu.be/' + b.video_id + (b.video_start ? '?t=' + b.video_start : '') : '';
const leakLabel = real(b.biggest_leak_label) || PART_LABEL[b.biggest_leak] || '';

const customFields = [];
const put = (id, v) => { v = real(v); if (v !== '') customFields.push({ id, field_value: v }); };
put(CF.score, b.score); put(CF.leak, leakLabel + (b.lever ? ' (next lever)' : '')); put(CF.route, route); put(CF.parts, partsText); put(CF.video, videoText); put(CF.answers, answersText);
put(CF.situation, situation); put(CF.liquid, liquid); put(CF.partners, partners); put(CF.selfReport, 'Scorecard: ' + (lab.source || '')); put(CF.bizType, lab.who); put(CF.startTiming, lab.timing);
put(CF.fbclid, b.fbclid); put(CF.fbp, b.fbp); put(CF.fbc, b.fbc); put(CF.ua, ua); put(CF.ip, ip);
for (const k of ['ad_id', 'adset_id', 'campaign_id', 'utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content', 'callix_sid', 'twclid', 'gclid', 'gbraid', 'wbraid', 'ttclid', 'wacid', 'bg_ch', 'utm_whop', 'waid', 'wasid']) put(CF[k], at[k]);

const tags = ['scorecard-optin', 'scorecard-route-' + route, 'scorecard-leak-' + (b.biggest_leak || 'unknown')];
if (test) tags.push('scorecard-test', 'dialer-off');
const first = real(b.name).split(' ')[0] || '';
const upsertBody = { locationId: 'F8y82aHd3V0Y4Y2ccET6', firstName: first, email, source: 'Scorecard', customFields };
// Test contacts never get a phone in GHL, so no text or call can reach a real number.
if (phone && !test) upsertBody.phone = phone;

return [{ json: {
  LIVE, test, proceed: okEmail && (test || LIVE), okEmail, email, phone, firstName: first, route, score: Number(b.score) || 0, band: real(b.band), leak: b.biggest_leak || '', leakLabel, lever: !!b.lever,
  lead_id: real(b.lead_id), video: videoText, answersText, partsText, labels: lab, tags, stlDayTag: 'optin-stl-et-' + day, dayET: day,
  fbclid: real(b.fbclid), fbc: real(b.fbc), fbp: real(b.fbp), ip, ua, attribution: at, upsertBody, page_url: real(b.page_url), raw: b,
} }];
`;

const mapNode = node({ type: 'n8n-nodes-base.code', version: 2, config: { name: 'Map Scorecard', parameters: { jsCode: mapCode } } });

const proceed = ifElse({
  version: 2.2,
  config: {
    name: 'Proceed? (test, or LIVE)',
    parameters: {
      conditions: {
        options: { caseSensitive: true, leftValue: '', typeValidation: 'loose' },
        conditions: [{ leftValue: expr('{{ $json.proceed }}'), rightValue: true, operator: { type: 'boolean', operation: 'true', singleValue: true } }],
        combinator: 'and',
      },
    },
  },
});

const held = node({ type: 'n8n-nodes-base.noOp', version: 1, config: { name: 'Held: not live yet' } });

const search = node({
  type: 'n8n-nodes-base.httpRequest',
  version: 4.2,
  config: {
    name: 'GHL Search',
    onError: 'continueRegularOutput',
    parameters: {
      method: 'GET',
      url: expr("{{ 'https://services.leadconnectorhq.com/contacts/?locationId=F8y82aHd3V0Y4Y2ccET6&limit=5&query=' + encodeURIComponent($json.email) }}"),
      authentication: 'genericCredentialType',
      genericAuthType: 'httpBearerAuth',
      sendHeaders: true,
      headerParameters: GHL_HEADERS,
      options: {},
    },
    credentials: GHL_CRED,
  },
});

const dedupeCode = `
// Same-day ET dedupe, same rule as the live intake: if this person already opted in today (tag optin-stl-et-<day>), do not upsert again
// (an upsert would re-fire the GHL opt-in first text). Stamp the scorecard fields on the existing contact instead.
const m = $('Map Scorecard').first().json;
const raw = $input.first().json || {};
const list = Array.isArray(raw.contacts) ? raw.contacts : [];
let contact = list.find((c) => String(c.email || '').toLowerCase() === m.email) || null;
const tags = ((contact && contact.tags) || []).map((t) => String(t).toLowerCase());
const sd = $getWorkflowStaticData('global'); sd.stlDay = sd.stlDay || {};
for (const k of Object.keys(sd.stlDay)) if (sd.stlDay[k] !== m.dayET) delete sd.stlDay[k];
const hit = tags.includes(m.stlDayTag) || sd.stlDay[m.email] === m.dayET;
if (!hit) sd.stlDay[m.email] = m.dayET;
return [{ json: { stampOnly: !!(hit && contact), contactId: contact ? contact.id : '', existingTags: tags } }];
`;
const dedupe = node({ type: 'n8n-nodes-base.code', version: 2, config: { name: 'Same-day Dedupe', parameters: { jsCode: dedupeCode } } });

const stampOnly = ifElse({
  version: 2.2,
  config: {
    name: 'Stamp Only?',
    parameters: {
      conditions: {
        options: { caseSensitive: true, leftValue: '', typeValidation: 'loose' },
        conditions: [{ leftValue: expr('{{ $json.stampOnly }}'), rightValue: true, operator: { type: 'boolean', operation: 'true', singleValue: true } }],
        combinator: 'and',
      },
    },
  },
});

const stamp = node({
  type: 'n8n-nodes-base.httpRequest',
  version: 4.2,
  config: {
    name: 'GHL Stamp Fields',
    parameters: {
      method: 'PUT',
      url: expr("{{ 'https://services.leadconnectorhq.com/contacts/' + $json.contactId }}"),
      authentication: 'genericCredentialType',
      genericAuthType: 'httpBearerAuth',
      sendHeaders: true,
      headerParameters: GHL_HEADERS,
      sendBody: true,
      specifyBody: 'json',
      jsonBody: expr("{{ JSON.stringify({ customFields: $('Map Scorecard').first().json.upsertBody.customFields }) }}"),
      options: {},
    },
    credentials: GHL_CRED,
  },
});

const upsert = node({
  type: 'n8n-nodes-base.httpRequest',
  version: 4.2,
  config: {
    name: 'GHL Upsert',
    parameters: {
      method: 'POST',
      url: 'https://services.leadconnectorhq.com/contacts/upsert',
      authentication: 'genericCredentialType',
      genericAuthType: 'httpBearerAuth',
      sendHeaders: true,
      headerParameters: GHL_HEADERS,
      sendBody: true,
      specifyBody: 'json',
      jsonBody: expr("{{ JSON.stringify($('Map Scorecard').first().json.upsertBody) }}"),
      options: {},
    },
    credentials: GHL_CRED,
  },
});

const pickCode = `
const m = $('Map Scorecard').first().json;
const d = $('Same-day Dedupe').first().json;
const r = $input.first().json || {};
const c = r.contact || {};
const contactId = String(c.id || d.contactId || '');
if (!contactId) throw new Error('No GHL contact id for ' + m.email);
const tags = m.tags.slice();
if (!d.stampOnly) tags.push(m.stlDayTag);
return [{ json: { contactId, contact: c, tags, stampOnly: d.stampOnly, test: m.test, route: m.route } }];
`;
const pick = node({ type: 'n8n-nodes-base.code', version: 2, config: { name: 'Pick Contact', parameters: { jsCode: pickCode } } });

const addTags = node({
  type: 'n8n-nodes-base.httpRequest',
  version: 4.2,
  config: {
    name: 'GHL Add Tags',
    parameters: {
      method: 'POST',
      url: expr("{{ 'https://services.leadconnectorhq.com/contacts/' + $json.contactId + '/tags' }}"),
      authentication: 'genericCredentialType',
      genericAuthType: 'httpBearerAuth',
      sendHeaders: true,
      headerParameters: GHL_HEADERS,
      sendBody: true,
      specifyBody: 'json',
      jsonBody: expr('{{ JSON.stringify({ tags: $json.tags }) }}'),
      options: {},
    },
    credentials: GHL_CRED,
  },
});

const realLead = ifElse({
  version: 2.2,
  config: {
    name: 'Real lead? (not a test)',
    parameters: {
      conditions: {
        options: { caseSensitive: true, leftValue: '', typeValidation: 'loose' },
        conditions: [{ leftValue: expr("{{ $('Pick Contact').first().json.test }}"), rightValue: false, operator: { type: 'boolean', operation: 'false', singleValue: true } }],
        combinator: 'and',
      },
    },
  },
});

const formatCode = `
// Card in "new opt-ins" (same channel and bot name as the live intake), labelled Scorecard. One card per person per ET day.
// Roles are pinged for qualified leads only (setters text and call qualified leads only).
const SALES_ROLE = '1305679491011711016';
const SETTERS_ROLE = '1389056437753221180';
const NEW_OPTINS_HOOK = '__DISCORD_HOOK__';
const m = $('Map Scorecard').first().json;
const p = $('Pick Contact').first().json;
if (!/^https:\\/\\/discord(app)?\\.com\\/api\\/webhooks\\//.test(NEW_OPTINS_HOOK)) return [];
const sd = $getWorkflowStaticData('global'); sd.card = sd.card || {};
for (const k of Object.keys(sd.card)) if (sd.card[k] !== m.dayET) delete sd.card[k];
if (sd.card[m.email] === m.dayET) return [];
const L = m.labels || {};
const routeLabel = { qualified: 'Qualified', nurture: 'Not yet qualified', early: 'Still learning' }[m.route] || m.route;
const lines = [
  '**Scorecard · ' + routeLabel + '**', '',
  '**' + (m.firstName || 'unknown') + '**',
  'Score: ' + m.score + '/100' + (m.band ? ' (' + m.band + ')' : '') + ' · ' + (m.lever ? 'Next lever: ' : 'Biggest leak: ') + m.leakLabel,
  'Parts: ' + m.partsText,
];
const add = (k, v) => { if (v) lines.push(k + ': ' + v); };
add('Who', L.who); add('Revenue a month', L.revenue); add('Own trading a month', L.trading); add('Followers', L.audience); add('Goal', L.goal);
add('Cash on hand', L.liquid); add('Timing', L.timing); add('Partners', L.partners); add('Heard about us', L.source); add('Tie-down', L.tiedown);
add('Video on results page', m.video);
add('Phone', m.phone); add('Email', m.email);
if (m.route === 'qualified') { lines.push('', 'Calendar shown on the page. Not booked within 5 minutes: call.', '<@&' + SALES_ROLE + '> <@&' + SETTERS_ROLE + '>'); }
else lines.push('', 'No setter action. Scorecard lead only.');
return [{ json: { content: lines.join('\\n'), username: 'BG Leads', allowed_mentions: { roles: m.route === 'qualified' ? [SALES_ROLE, SETTERS_ROLE] : [] }, _hook: NEW_OPTINS_HOOK, contactId: p.contactId, email: m.email } }];
`;
const formatDiscord = node({ type: 'n8n-nodes-base.code', version: 2, config: { name: 'Format Scorecard Card', parameters: { jsCode: formatCode } } });

const postDiscord = node({
  type: 'n8n-nodes-base.httpRequest',
  version: 4.2,
  config: {
    name: 'Post Discord Card',
    onError: 'continueRegularOutput',
    parameters: {
      method: 'POST',
      url: expr("{{ $json._hook + '?wait=true' }}"),
      sendHeaders: true,
      headerParameters: { parameters: [{ name: 'Content-Type', value: 'application/json' }, { name: 'User-Agent', value: 'DiscordBot (https://businessgrowr.com, 1.0)' }] },
      sendBody: true,
      specifyBody: 'json',
      jsonBody: expr('{{ JSON.stringify({ content: $json.content, allowed_mentions: $json.allowed_mentions, username: $json.username }) }}'),
      options: {},
    },
  },
});

const saveCardCode = `
const m = $('Map Scorecard').first().json;
const sd = $getWorkflowStaticData('global'); sd.card = sd.card || {};
const r = $input.first().json || {};
if (r.id) sd.card[m.email] = m.dayET;
return [{ json: { discordOk: !!r.id, messageId: r.id || '', contactId: $('Pick Contact').first().json.contactId } }];
`;
const saveCard = node({ type: 'n8n-nodes-base.code', version: 2, config: { name: 'Save Card', parameters: { jsCode: saveCardCode } } });

const tagPinged = node({
  type: 'n8n-nodes-base.httpRequest',
  version: 4.2,
  config: {
    name: 'Tag scorecard-pinged',
    onError: 'continueRegularOutput',
    parameters: {
      method: 'POST',
      url: expr("{{ 'https://services.leadconnectorhq.com/contacts/' + $json.contactId + '/tags' }}"),
      authentication: 'genericCredentialType',
      genericAuthType: 'httpBearerAuth',
      sendHeaders: true,
      headerParameters: GHL_HEADERS,
      sendBody: true,
      specifyBody: 'json',
      jsonBody: expr("{{ JSON.stringify({ tags: ['scorecard-pinged'] }) }}"),
      options: {},
    },
    credentials: GHL_CRED,
  },
});

const isQualified = ifElse({
  version: 2.2,
  config: {
    name: 'Qualified?',
    parameters: {
      conditions: {
        options: { caseSensitive: true, leftValue: '', typeValidation: 'loose' },
        conditions: [{ leftValue: expr("{{ $('Map Scorecard').first().json.route }}"), rightValue: 'qualified', operator: { type: 'string', operation: 'equals' } }],
        combinator: 'and',
      },
    },
  },
});

const notify = node({
  type: 'n8n-nodes-base.httpRequest',
  version: 4.2,
  config: {
    name: 'Fire GHL Optin Notify',
    onError: 'continueRegularOutput',
    parameters: {
      method: 'POST',
      url: '__GHL_NOTIFY_HOOK__',
      sendHeaders: true,
      headerParameters: { parameters: [{ name: 'Content-Type', value: 'application/json' }, { name: 'Accept', value: 'application/json' }, { name: 'User-Agent', value: 'n8n' }] },
      sendBody: true,
      specifyBody: 'json',
      jsonBody: expr("{{ JSON.stringify({ contact_id: $('Pick Contact').first().json.contactId, email: $('Map Scorecard').first().json.email, phone: $('Map Scorecard').first().json.phone, first_name: $('Map Scorecard').first().json.firstName, last_name: '', full_name: $('Map Scorecard').first().json.firstName, source: 'Scorecard', is_partial: false, is_dq: false, location_id: 'F8y82aHd3V0Y4Y2ccET6', event: 'scorecard_optin_card_posted' }) }}"),
      options: { timeout: 10000, response: { response: { neverError: true, fullResponse: true } } },
    },
  },
});

const capi = node({
  type: 'n8n-nodes-base.httpRequest',
  version: 4.2,
  config: {
    name: 'Fire Lead CAPI',
    onError: 'continueRegularOutput',
    parameters: {
      method: 'POST',
      url: 'https://businessgrowr.app.n8n.cloud/webhook/bg-lead-capi',
      sendHeaders: true,
      headerParameters: { parameters: [{ name: 'Content-Type', value: 'application/json' }, { name: 'User-Agent', value: 'n8n' }] },
      sendBody: true,
      specifyBody: 'json',
      jsonBody: expr("{{ JSON.stringify({ email: $('Map Scorecard').first().json.email, phone: $('Map Scorecard').first().json.phone, contact_id: $('Pick Contact').first().json.contactId, firstName: $('Map Scorecard').first().json.firstName, lastName: '', name: $('Map Scorecard').first().json.firstName, url: 'https://businessgrowr.com/scorecard', event_id: 'sc_lead_' + ($('Map Scorecard').first().json.lead_id || $('Pick Contact').first().json.contactId), fbp: $('Map Scorecard').first().json.fbp, fbc: $('Map Scorecard').first().json.fbc, first_fbclid: $('Map Scorecard').first().json.fbclid, ip: $('Map Scorecard').first().json.ip, ua: $('Map Scorecard').first().json.ua, contact: $('Pick Contact').first().json.contact || {} }) }}"),
      options: { timeout: 10000, response: { response: { neverError: true, fullResponse: true } } },
    },
  },
});

const saBuildCode = `
// SubmitApplication for a qualified scorecard finish, same events as the live SA branch (Meta dataset 3039470253072337 + Whop submit_application), event_id app_sc_<lead_id>.
const crypto = require('crypto');
const sha = (v) => { const s = String(v == null ? '' : v).trim().toLowerCase(); return s ? crypto.createHash('sha256').update(s).digest('hex') : null; };
const m = $('Map Scorecard').first().json;
const p = $('Pick Contact').first().json;
const tags = ((p.contact && p.contact.tags) || []).map((t) => String(t).toLowerCase());
if (tags.includes('capi-block') || /zztest|example\\.com/i.test(m.email)) return [];
const sd = $getWorkflowStaticData('global'); sd.saSent = sd.saSent || {};
if (sd.saSent['em_' + m.email]) return [];
const eventId = 'app_sc_' + (m.lead_id || p.contactId);
let digits = String(m.phone || '').replace(/\\D/g, ''); if (digits.length < 11) digits = '';
const ud = {};
const put = (k, v) => { const h = sha(v); if (h) ud[k] = [h]; };
put('em', m.email); put('ph', digits); put('fn', (m.firstName || '').toLowerCase().replace(/[^\\p{L}]/gu, '')); put('external_id', p.contactId);
if (/^fb\\.\\d\\.\\d+\\./.test(m.fbp)) ud.fbp = m.fbp;
if (/^fb\\.\\d\\.\\d+\\./.test(m.fbc)) ud.fbc = m.fbc;
if (m.ip) ud.client_ip_address = m.ip;
if (m.ua && m.ua.length > 10) ud.client_user_agent = m.ua;
const at = m.attribution || {};
const url = 'https://businessgrowr.com/scorecard';
const et = Math.floor(Date.now() / 1000);
const drop = (o) => { const r = {}; for (const [k, v] of Object.entries(o)) { if (v === null || v === undefined || v === '') continue; if (typeof v === 'object' && !Array.isArray(v)) { const x = drop(v); if (Object.keys(x).length) r[k] = x; } else r[k] = v; } return r; };
const meta = drop({ event_name: 'SubmitApplication', event_time: et, event_id: eventId, action_source: 'website', event_source_url: url, user_data: ud, custom_data: { qualified: true, form: 'scorecard', ad_id: at.ad_id, adset_id: at.adset_id, campaign_id: at.campaign_id } });
const whop = drop({ account_id: 'biz_0PFOl9w41XrCmJ', event_name: 'submit_application', action_source: 'website', event_id: eventId, event_time: new Date(et * 1000).toISOString(), url,
  user: { email: m.email, phone: digits ? '+' + digits : null, first_name: m.firstName, external_id: p.contactId },
  context: { fbp: ud.fbp, fbc: ud.fbc, ip_address: ud.client_ip_address, user_agent: ud.client_user_agent, fbclid: m.fbclid, utm_source: at.utm_source, utm_medium: at.utm_medium, utm_campaign: at.utm_campaign, utm_content: at.utm_content, utm_term: at.utm_term } });
return [{ json: { event_id: eventId, email: m.email, meta_body: { data: [meta] }, whop_body: whop } }];
`;
const saBuild = node({ type: 'n8n-nodes-base.code', version: 2, config: { name: 'SA — build', parameters: { jsCode: saBuildCode } } });

const saMeta = node({
  type: 'n8n-nodes-base.httpRequest',
  version: 4.2,
  config: {
    name: 'SA — Meta SubmitApplication (3039470253072337)',
    onError: 'continueRegularOutput',
    parameters: {
      method: 'POST',
      url: 'https://graph.facebook.com/v25.0/3039470253072337/events',
      authentication: 'predefinedCredentialType',
      nodeCredentialType: 'facebookGraphApi',
      sendBody: true,
      specifyBody: 'json',
      jsonBody: expr('{{ JSON.stringify($json.meta_body) }}'),
      options: { response: { response: { neverError: true, fullResponse: true } } },
    },
    credentials: { facebookGraphApi: { id: 'MxgLlb5kDOK9ej1N', name: 'Whackamole FB User Token' } },
  },
});

const saWhop = node({
  type: 'n8n-nodes-base.httpRequest',
  version: 4.2,
  config: {
    name: 'SA — Whop submit_application',
    onError: 'continueRegularOutput',
    parameters: {
      method: 'POST',
      url: 'https://api.whop.com/api/v1/events',
      authentication: 'genericCredentialType',
      genericAuthType: 'httpBearerAuth',
      sendHeaders: true,
      headerParameters: { parameters: [{ name: 'Api-Version-Date', value: '2026-08-25' }, { name: 'Accept', value: 'application/json' }, { name: 'Content-Type', value: 'application/json' }] },
      sendBody: true,
      specifyBody: 'json',
      jsonBody: expr("{{ JSON.stringify($('SA — build').first().json.whop_body) }}"),
      options: { response: { response: { fullResponse: true, neverError: true } } },
    },
    credentials: { httpBearerAuth: { id: 'MaBhfdkRQCc6Eji7', name: 'Whop Events API (Andy BG)' } },
  },
});

const saRecordCode = `
const sd = $getWorkflowStaticData('global'); sd.saSent = sd.saSent || {};
const b = $('SA — build').first().json;
const r = $input.first().json || {};
const mm = $('SA — Meta SubmitApplication (3039470253072337)').first().json || {};
const whopOk = Number(r.statusCode) >= 200 && Number(r.statusCode) < 300;
const metaOk = !!(mm.body && mm.body.events_received);
if (whopOk || metaOk) { const t = new Date().toISOString(); sd.saSent[b.event_id] = t; if (b.email) sd.saSent['em_' + b.email] = t; }
return [{ json: { event_id: b.event_id, meta_ok: metaOk, whop_ok: whopOk, whop_status: r.statusCode || null } }];
`;
const saRecord = node({ type: 'n8n-nodes-base.code', version: 2, config: { name: 'SA — record', parameters: { jsCode: saRecordCode } } });

export default workflow('bg-scorecard-ghl', 'BG — Scorecard → GHL Contact')
  .add(hook)
  .to(mapNode)
  .to(proceed
    .onTrue(search.to(dedupe).to(stampOnly
      .onTrue(stamp.to(pick))
      .onFalse(upsert.to(pick))))
    .onFalse(held))
  .add(pick)
  .to(addTags)
  .to(realLead.onTrue(capi.to(formatDiscord).to(postDiscord).to(saveCard).to(tagPinged).to(isQualified.onTrue(notify.to(saBuild).to(saMeta).to(saWhop).to(saRecord)))));
