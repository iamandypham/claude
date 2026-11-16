// One-off: copy live 4WaO into this workflow with V2 edits, then this builder is overwritten. 13 Nov 2026.
const crypto = require('crypto');
const w = $input.first().json;
const R = [
 ['Map Scorecard','jsCode',"// BG Scorecard -> GHL. Built 2026-11-08","// SCORECARD V2 copy 2026-11-13 (side by side; live 4WaO3TM95EeZePXd untouched). No cash gate: under-$5K qualified get tag lt5k and NO SubmitApplication (same as y7Lk); 33Dn sends ScheduleUnder5k from the liquid field.\n// BG Scorecard -> GHL. Built 2026-11-08"],
 ['Map Scorecard','jsCode',"const tags = ['scorecard-optin',","const tags = ['scorecard-v2', 'scorecard-optin',"],
 ['Map Scorecard','jsCode',"if (test) tags.push('scorecard-test', 'dialer-off');","if (liquid === 'Less Than $5k') tags.push('lt5k'); // V2: same tag as the main funnel under-$5K route\nif (test) tags.push('scorecard-test', 'dialer-off');"],
 ['Map Scorecard','jsCode',"tags, stlDayTag:","tags, lt5k: liquid === 'Less Than $5k', stlDayTag:"],
 ['SA — build','jsCode',"if (tags.includes('capi-block')","if (m.lt5k) return []; // V2: no SubmitApplication for under-$5K (main funnel rule, 11 Nov)\nif (tags.includes('capi-block')"],
 ['SA — build','jsCode',"const url = 'https://businessgrowr.com/scorecard';","const url = (m.page_url || 'https://businessgrowr.com/scorecard').split('?')[0];"],
 ['SA — build','jsCode',"form: 'scorecard',","form: 'scorecard-v2',"],
 ['Fire Lead CAPI','jsonBody',"url: 'https://businessgrowr.com/scorecard',","url: ($('Map Scorecard').first().json.page_url || 'https://businessgrowr.com/scorecard').split('?')[0],"],
 ['Fire Lead CAPI','jsonBody',"event_id: 'sc_lead_'","event_id: 'sc2_lead_'"],
 ['Format Scorecard Card','jsCode',"'**Scorecard · ' + routeLabel","'**Scorecard v2 · ' + routeLabel + (m.lt5k ? ' · under $5K cash' : '')"],
 ['Fire GHL Optin Notify','jsonBody',"source: 'Scorecard',","source: 'Scorecard v2',"],
];
const nodes = JSON.parse(JSON.stringify(w.nodes));
const by = {}; for (const n of nodes) by[n.name] = n;
for (const [name, key, a, b] of R) {
  const p = by[name].parameters; const c = p[key].split(a).length - 1;
  if (c !== 1) throw new Error('anchor ' + c + 'x in ' + name + ': ' + a.slice(0, 40));
  p[key] = p[key].replace(a, () => b);
}
by['Scorecard Webhook'].parameters.path = 'bg-scorecard-v2-ghl';
for (const n of nodes) { n.id = crypto.randomUUID(); if (n.webhookId) n.webhookId = crypto.randomUUID(); }
const hash = (s) => crypto.createHash('sha256').update(s).digest('hex').slice(0, 16);
const report = {}; for (const n of nodes) report[n.name] = hash(JSON.stringify(n.parameters));
return [{ json: { body: { name: 'BG — Scorecard v2 → GHL Contact', nodes, connections: w.connections, settings: { executionOrder: 'v1' } }, srcVersion: w.versionId, report } }];
