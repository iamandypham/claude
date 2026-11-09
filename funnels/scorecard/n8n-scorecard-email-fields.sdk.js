import { workflow, node, trigger, ifElse, expr } from '@n8n/workflow-sdk';

// BG — Scorecard email fields. Built 8 Nov 2026 on Andy's approval of the scorecard email text (9:16 PM ET).
// The GHL workflow "Scorecard email" calls this webhook when a contact gets the tag scorecard-optin.
// It reads the contact and writes the per-lead email text into the ten "Scorecard Email ..." fields.
// It never sends anything, never adds tags and fires no ad event. Test contacts (tag scorecard-test) get
// no Ready flag, so the GHL workflow skips them.

const GHL_CRED = { httpBearerAuth: { id: 'I9syQTyegPSmKR0a', name: 'GoHighLevel BG' } };
const GHL_HEADERS = { parameters: [
  { name: 'Version', value: '2021-07-28' },
  { name: 'Content-Type', value: 'application/json' },
  { name: 'Accept', value: 'application/json' },
] };

const hook = trigger({
  type: 'n8n-nodes-base.webhook',
  version: 2,
  config: { name: 'Scorecard Email Webhook', parameters: { httpMethod: 'POST', path: 'bg-scorecard-email-fields', responseMode: 'onReceived', options: {} } },
});

const idCode = `
const j = $input.first().json || {};
let b = j.body; if (typeof b === 'string') { try { b = JSON.parse(b); } catch (e) { b = {}; } }
b = b || {};
const id = String(b.contact_id || b.contactId || (b.contact && b.contact.id) || b.id || '').trim();
return [{ json: { contactId: id, ok: /^[A-Za-z0-9]{10,40}$/.test(id) } }];
`;
const getId = node({ type: 'n8n-nodes-base.code', version: 2, config: { name: 'Contact Id', parameters: { jsCode: idCode } } });

const okId = ifElse({ version: 2.2, config: { name: 'Has contact id?', parameters: { conditions: {
  options: { caseSensitive: true, leftValue: '', typeValidation: 'loose' },
  conditions: [{ leftValue: expr('{{ $json.ok }}'), rightValue: true, operator: { type: 'boolean', operation: 'true', singleValue: true } }],
  combinator: 'and' } } } });

const getContact = node({ type: 'n8n-nodes-base.httpRequest', version: 4.2, config: { name: 'GHL Get Contact', parameters: {
  method: 'GET', url: expr("{{ 'https://services.leadconnectorhq.com/contacts/' + $json.contactId }}"),
  authentication: 'genericCredentialType', genericAuthType: 'httpBearerAuth', sendHeaders: true, headerParameters: GHL_HEADERS, options: {} },
  credentials: GHL_CRED } });

const buildCode = `
const c = ($input.first().json || {}).contact || {};
const cf = {}; for (const f of (c.customFields || [])) cf[f.id] = f.value;
const tags = (c.tags || []).map((t) => String(t).toLowerCase());
const F = { score: 'pPBfRFgquz2479DswrUS', leak: 'LqKKlOUNLZf3c1DGGeb5', route: 'G9qBavyN1gq4Rxu4zuei', video: 'xnsOYUL151iUyfkkwAnD' };
const OUT = { heading: 'NzPFb9aRpwWTB9y5scQF', diagnosis: 'GmboRWuA7XuYv6zFrFK4', move: 'Zlvl4YathHiEA0qkqRjW', videoLine: 'QxgtAczRExCiHGTkS2Qs', videoUrl: 'RtRh2W7GezEnOlePrD7q', ending: 'ixfP2vh6EEQdJ7tLcctJ', linkLabel: 'bqel65y4cgo4Q41pLVHf', linkUrl: 'RNb03yfLygAuISzLDH0V', ready: 'yg1tekvyunGq8Cyutmy0', endingAfter: 'y3NVFN72lrUJJXcFi4Ed' };
const LABEL = { reach: 'Reach', capture: 'Capture', nurture: 'Nurture', sales: 'Sales', retention: 'Onboarding', backend: 'Backend' };
// Same diagnosis lines and first moves as the live page (funnels/scorecard/scorecard-live.html, LEAK).
const LEAK = {
  reach: ["In our experience, lifestyle content gets you views. Educational content gets you buyers who stay.", "At least about half of what you post should be educational and actually provide value. Put a CTA in every reel."],
  capture: ["In our experience, views are a weaker sign of revenue than the leads and emails you collect.", "Make a 1 page PDF on your model to give out in exchange for emails. Pick a keyword, and when people comment it, ManyChat sends them the link. Put a CTA in every reel."],
  nurture: ["In the funnels we build, we order the YouTube videos people watch in the email sequences and in the Discord. Those videos break their beliefs and pre-handle objections, while also selling them on the unique mechanism.", "When someone gives you their email, redirect them to your VSL page and tell them to check their email. Record the VSL horizontal, so they can just click the button all in one screen. Then they get pitched straight away."],
  sales: ["A lot of owners just sit on social media and hope that one day somebody clicks their Whop link and randomly pays.", "Trial to paid should be at least 20%. If it\\u2019s well below that, maybe try a three-day trial instead of seven."],
  retention: ["Generally, owners who aren\\u2019t making money haven\\u2019t thought once about what happens after someone joins.", "Record a Start Here video and put it at the top of your community. Start with 30 seconds of proof of your trading and student results. Then show the top three most valuable parts of your Discord, and screen share to teach them how to use each one."],
  backend: ["The $99 subscription isn\\u2019t the whole business. It keeps people around long enough to launch indicators, mid ticket and high ticket, and to earn on affiliates.", "Don\\u2019t pitch high ticket on day one. Pre-seed it inside the community, then sell it on calls a few months in."],
};
const leakTag = tags.find((t) => t.startsWith('scorecard-leak-'));
const key = leakTag ? leakTag.slice('scorecard-leak-'.length) : '';
const leakRaw = String(cf[F.leak] || '');
const lever = /next lever/i.test(leakRaw);
const label = LABEL[key] || leakRaw.replace(/\\s*\\(next lever\\)/i, '');
const routeTag = tags.find((t) => t.startsWith('scorecard-route-'));
const route = String(cf[F.route] || (routeTag ? routeTag.slice('scorecard-route-'.length) : '')).toLowerCase();
const test = tags.includes('scorecard-test') || /@example\\.com$/i.test(c.email || '');
const booked = tags.includes('scorecard-booked');
const L = LEAK[key];
const ok = !!(L && label && c.email && !test);

let videoLine = '', videoUrl = '';
const v = String(cf[F.video] || '');
const m = v.match(/^(.*)\\s\\|\\s(https:\\/\\/\\S+)$/);
if (m) {
  videoUrl = m[2];
  const t = Number((videoUrl.match(/[?&]t=(\\d+)/) || [])[1] || 0);
  const mmss = Math.floor(t / 60) + ':' + String(t % 60).padStart(2, '0');
  videoLine = 'Watch this part next: ' + m[1].trim() + (t ? ', from ' + mmss : '') + ':';
}
// Ending = text before the link, Link Label = the linked words, Ending After = text after the link (approved wording, 8 Nov).
let ending, linkLabel = '', linkUrl = '', endingAfter = '';
if (route === 'qualified' && booked) {
  ending = "You\\u2019re booked for your call. Check your inbox for the exact time.";
} else if (route === 'qualified') {
  ending = 'If you want us to look at it with you,';
  linkLabel = 'pick a time here';
  linkUrl = 'https://calendly.com/d/dvtq-vgz-stw/dfy-guarantee-demo-meeting-bg-aaf?name=' + encodeURIComponent(((c.firstName || '') + ' ' + (c.lastName || '')).trim()) + '&email=' + encodeURIComponent(c.email || '') + (c.phone ? '&a1=' + encodeURIComponent(c.phone) : '') + '&utm_source=scorecard-email&utm_medium=email';
  endingAfter = '. On the call we go through your scorecard and show you what fixing ' + label + ' would look like in your community.';
} else {
  ending = "Start with the video above. When your community is earning or your following is growing, take the scorecard again and see what\\u2019s changed:";
  linkLabel = 'businessgrowr.com/scorecard';
  linkUrl = 'https://businessgrowr.com/scorecard?utm_source=scorecard-email&utm_medium=email';
}
const vals = {
  heading: (lever ? 'Your next lever: ' : 'Your biggest leak: ') + label,
  diagnosis: lever ? 'Nothing is leaking badly. This is the part with the most room left.' : (L ? L[0] : ''),
  move: L ? L[1] : '', videoLine, videoUrl, ending, linkLabel, linkUrl, endingAfter, ready: ok ? 'yes' : '',
};
const customFields = Object.keys(OUT).map((k) => ({ id: OUT[k], field_value: vals[k] }));
return [{ json: { contactId: c.id, ok, test, route, key, lever, booked, vals, body: { customFields } } }];
`;
const build = node({ type: 'n8n-nodes-base.code', version: 2, config: { name: 'Build Email Fields', parameters: { jsCode: buildCode } } });

const put = node({ type: 'n8n-nodes-base.httpRequest', version: 4.2, config: { name: 'GHL Write Fields', parameters: {
  method: 'PUT', url: expr("{{ 'https://services.leadconnectorhq.com/contacts/' + $json.contactId }}"),
  authentication: 'genericCredentialType', genericAuthType: 'httpBearerAuth', sendHeaders: true, headerParameters: GHL_HEADERS,
  sendBody: true, specifyBody: 'json', jsonBody: expr('{{ JSON.stringify($json.body) }}'), options: {} },
  credentials: GHL_CRED } });

const stop = node({ type: 'n8n-nodes-base.noOp', version: 1, config: { name: 'No contact id' } });

export default workflow('bg-scorecard-email-fields', 'BG — Scorecard email fields')
  .add(hook)
  .to(getId)
  .to(okId.onTrue(getContact.to(build).to(put)).onFalse(stop));
