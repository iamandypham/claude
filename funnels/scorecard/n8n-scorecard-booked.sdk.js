import { workflow, node, trigger, ifElse, expr } from '@n8n/workflow-sdk';

// BG — Scorecard booked → GHL tag. Built 8 Nov 2026 on Andy's ask ("have the quiz info save into contact so when they book we know it's from quiz funnel").
// The scorecard page posts here when Calendly reports a booking made on the quiz page.
// It only ADDS the tag scorecard-booked to a contact that already carries scorecard-optin. It never creates a contact,
// never sends a message and fires no ad event. scorecard-booked matches no published GHL tag trigger (checked 8 Nov).

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
    name: 'Scorecard Booked Webhook',
    parameters: {
      httpMethod: 'POST',
      path: 'bg-scorecard-booked',
      responseMode: 'onReceived',
      options: { allowedOrigins: 'https://businessgrowr.com,https://www.businessgrowr.com' },
    },
  },
});

const mapCode = `
const j = $input.first().json || {};
let b = j.body;
if (typeof b === 'string') { try { b = JSON.parse(b); } catch (e) { b = {}; } }
if (!b || typeof b !== 'object') b = {};
if (!b.email && Object.keys(b).length === 1) { try { b = JSON.parse(Object.keys(b)[0]); } catch (e) {} }
const email = String(b.email || '').trim().toLowerCase();
const okEmail = /^[^\\s@]+@[^\\s@]+\\.[^\\s@]{2,}$/.test(email);
return [{ json: { email, okEmail, lead_id: String(b.lead_id || ''), route: String(b.route || ''), page_url: String(b.page_url || '') } }];
`;
const mapNode = node({ type: 'n8n-nodes-base.code', version: 2, config: { name: 'Map Booked', parameters: { jsCode: mapCode } } });

const okEmail = ifElse({
  version: 2.2,
  config: {
    name: 'Valid email?',
    parameters: {
      conditions: {
        options: { caseSensitive: true, leftValue: '', typeValidation: 'loose' },
        conditions: [{ leftValue: expr('{{ $json.okEmail }}'), rightValue: true, operator: { type: 'boolean', operation: 'true', singleValue: true } }],
        combinator: 'and',
      },
    },
  },
});

const search = node({
  type: 'n8n-nodes-base.httpRequest',
  version: 4.2,
  config: {
    name: 'GHL Search',
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

const pickCode = `
// Only a contact with this exact email that already has the scorecard-optin tag. Anything else stops here.
const m = $('Map Booked').first().json;
const raw = $input.first().json || {};
const list = Array.isArray(raw.contacts) ? raw.contacts : [];
const c = list.find((x) => String(x.email || '').toLowerCase() === m.email && ((x.tags || []).map((t) => String(t).toLowerCase())).includes('scorecard-optin'));
if (!c) return [];
return [{ json: { contactId: c.id, email: m.email } }];
`;
const pick = node({ type: 'n8n-nodes-base.code', version: 2, config: { name: 'Scorecard contact?', parameters: { jsCode: pickCode } } });

const addTag = node({
  type: 'n8n-nodes-base.httpRequest',
  version: 4.2,
  config: {
    name: 'GHL Tag scorecard-booked',
    parameters: {
      method: 'POST',
      url: expr("{{ 'https://services.leadconnectorhq.com/contacts/' + $json.contactId + '/tags' }}"),
      authentication: 'genericCredentialType',
      genericAuthType: 'httpBearerAuth',
      sendHeaders: true,
      headerParameters: GHL_HEADERS,
      sendBody: true,
      specifyBody: 'json',
      jsonBody: expr("{{ JSON.stringify({ tags: ['scorecard-booked'] }) }}"),
      options: {},
    },
    credentials: GHL_CRED,
  },
});

// Added 9 Nov 2026 (scorecard email, approved by Andy 8 Nov 9:16 PM ET): a booked lead's scorecard email says
// "You're booked" instead of the calendar link, so nobody books twice. Writes contact fields only.
const bookedEnding = node({
  type: 'n8n-nodes-base.httpRequest',
  version: 4.2,
  config: {
    name: 'GHL Booked Email Ending',
    parameters: {
      method: 'PUT',
      url: expr("{{ 'https://services.leadconnectorhq.com/contacts/' + $('Scorecard contact?').first().json.contactId }}"),
      authentication: 'genericCredentialType',
      genericAuthType: 'httpBearerAuth',
      sendHeaders: true,
      headerParameters: GHL_HEADERS,
      sendBody: true,
      specifyBody: 'json',
      jsonBody: expr("{{ JSON.stringify({ customFields: [ { id: 'ixfP2vh6EEQdJ7tLcctJ', field_value: 'You\u2019re booked for your call. Check your inbox for the exact time.' }, { id: 'bqel65y4cgo4Q41pLVHf', field_value: '' }, { id: 'RNb03yfLygAuISzLDH0V', field_value: '' }, { id: 'y3NVFN72lrUJJXcFi4Ed', field_value: '' } ] }) }}"),
      options: {},
    },
    credentials: GHL_CRED,
  },
});

const stop = node({ type: 'n8n-nodes-base.noOp', version: 1, config: { name: 'No valid email' } });

export default workflow('bg-scorecard-booked', 'BG — Scorecard booked → GHL tag')
  .add(hook)
  .to(mapNode)
  .to(okEmail
    .onTrue(search.to(pick).to(addTag).to(bookedEnding))
    .onFalse(stop));
