#!/usr/bin/env python3
"""Turn the draft 5 prototype into the live GHL page. Every replacement must match exactly once."""
import re, sys
src, out = sys.argv[1], sys.argv[2]
h = open(src, encoding="utf-8").read()

def rep(old, new, count=1):
    global h
    n = h.count(old)
    if n != count:
        raise SystemExit(f"expected {count} match(es), got {n}: {old[:80]!r}")
    h = h.replace(old, new)

def rep_re(pat, new, flags=re.S):
    global h
    m = list(re.finditer(pat, h, flags))
    if len(m) != 1:
        raise SystemExit(f"regex expected 1 match, got {len(m)}: {pat[:80]!r}")
    h = h[:m[0].start()] + new + h[m[0].end():]

WEBHOOK = "https://businessgrowr.app.n8n.cloud/webhook/bg-scorecard-ghl"
CAL_BASE = "https://calendly.com/d/dvtq-vgz-stw/dfy-guarantee-demo-meeting-bg-aaf"

# ---------- head: prototype-only meta ----------
rep('<meta name="claude:viewport-fit-sides" content="cover">\n', '')

# ---------- CSS: live player + calendar ----------
rep('.vp-note{margin:8px 0 0;font-size:12px;line-height:1.45;color:var(--muted)}',
    '.vp-note{margin:8px 0 0;font-size:12px;line-height:1.45;color:var(--muted)}\n'
    '.vp-live{display:block;padding:0;border-left-width:1px;overflow:hidden}\n'
    '.vp-frame{position:relative;display:block;aspect-ratio:16/9;background:#000}\n'
    '.vp-frame iframe{position:absolute;inset:0;width:100%;height:100%;border:0}\n'
    '.cal-live{margin-top:14px;border:1px solid var(--line);border-radius:15px;overflow:hidden;background:#fff}\n'
    '.cal-live .calendly-inline-widget{width:100%;height:1020px}\n'
    '@media (min-width:700px){.cal-live .calendly-inline-widget{height:720px}}\n'
    '.consent a{color:inherit;text-decoration:underline}')

# ---------- HTML: remove setter view and review drawer ----------
rep('\n  <!-- SETTER (review only) -->\n  <section class="view setter" id="v-setter" data-view="setter" hidden></section>\n', '\n')
rep_re(r'<button class="rv-fab".*?</ol>\n</div>\n', '')

# ---------- JS: live video player ----------
rep_re(r"function videoPlayerHTML\(a, early\)\{.*?\n\}\n",
'''function videoPlayerHTML(a, early){
  var leak = leakOf(a), lever = num(a[leak.id]) >= 75, v = videoFor(a, early);
  if (!v) return "";
  var k = (lever ? "Picked for your next lever: " : "Picked for your biggest leak: ") + leak.label;
  var src = "https://www.youtube-nocookie.com/embed/" + v.id + "?rel=0&modestbranding=1&playsinline=1" + (v.t ? "&start=" + v.t : "");
  return '<div class="vid-card vp-live" data-video="' + v.id + '">' +
    '<span class="vp-frame"><iframe src="' + src + '" title="' + esc(v.title) + '" loading="lazy" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe></span>' +
    '<span class="vid-b vp-body"><span class="vid-k">' + esc(k) + '</span><span class="vid-t">' + esc(v.why) + '</span>' +
    '<span class="vid-src">From our YouTube: “' + esc(v.title) + '”</span></span></div>';
}
''')

# ---------- JS: consent line with links ----------
rep('''consent:"By tapping See my score, you agree that BusinessGrowR can call and text you at this number about your results and our services, including with automated tools. This isn’t a condition of buying anything. Message and data rates may apply. Reply STOP to opt out."}''',
    '''consent:"By tapping See my score, you agree that BusinessGrowR can call and text you at this number about your results and our services, including with automated tools. This isn’t a condition of buying anything. Message and data rates may apply. Reply STOP to opt out.", consentLinks:' See our <a href="https://businessgrowr.com/privacy" target="_blank" rel="noopener">Privacy Policy</a> and <a href="https://businessgrowr.com/terms" target="_blank" rel="noopener">Terms</a>.'}''')
rep('''var extra = c.consent ? '<p class="consent">' + esc(c.consent) + '</p>' : '';''',
    '''var extra = c.consent ? '<p class="consent">' + esc(c.consent) + (c.consentLinks || '') + '</p>' : '';''')

# ---------- JS: keep only the intro example ----------
rep_re(r"  nurture:\{name:\"Sam\".*?\n  early:\{name:\"Alex\".*?\n", '')

# ---------- JS: send the lead on the phone step ----------
rep('''    state.a.phone = v;
    /* Live build: partial submit here (answers, score, route) to the duplicate n8n flow. Draft: nothing is sent. */
    runAnalyzing();''',
'''    state.a.phone = v;
    sendLead();
    runAnalyzing();''')

TRACK = r'''
/* ---------- live: attribution + lead send ---------- */
var WEBHOOK = "__WEBHOOK__";
var CONSENT_VERSION = "scorecard-2026-11-08";
function qp(k){ try { return new URLSearchParams(location.search).get(k) || ""; } catch(e){ return ""; } }
function cleanV(v){ v = String(v || "").trim(); return (/\{\{|%7B%7B/i.test(v) || /^_+$/.test(v) || /^x{3,}$/i.test(v) || v === "null" || v === "undefined") ? "" : v; }
function ss(k, v){ try { if (v) sessionStorage.setItem(k, v); else v = sessionStorage.getItem(k) || ""; } catch(e){} return cleanV(v); }
function keep(k){ return ss("bg_sc_" + k, cleanV(qp(k))); }
function cookie(n){ var m = document.cookie.match(new RegExp("(?:^|; )" + n.replace(/[.$?*|{}()\[\]\\\/+^]/g, "\\$&") + "=([^;]*)")); return m ? decodeURIComponent(m[1]) : ""; }
function setCookie(n, v){ try { document.cookie = n + "=" + encodeURIComponent(v) + ";path=/;max-age=7776000;SameSite=Lax"; } catch(e){} }
var CLICK_KEYS = ["utm_source","utm_medium","utm_campaign","utm_content","utm_term","ad_id","adset_id","ad_group_id","campaign_id","gclid","gbraid","wbraid","ttclid","twclid","wacid","waid","wasid","bg_ch","utm_whop","callix_sid"];
var ATTR = {};
CLICK_KEYS.forEach(function(k){ ATTR[k] = keep(k); });
if (!ATTR.adset_id) ATTR.adset_id = ATTR.ad_group_id;
function fbclidFromFbc(f){ var p = String(f || "").split("."); return p.length >= 4 ? p.slice(3).join(".") : ""; }
function readFbclid(){
  var u = cleanV(qp("fbclid"));
  if (u) { try { sessionStorage.setItem("bg_fbclid", u); } catch(e){} setCookie("bg_fbclid", u); return u; }
  var s = ""; try { s = sessionStorage.getItem("bg_fbclid") || ""; } catch(e){}
  return cleanV(s) || cleanV(cookie("bg_fbclid")) || fbclidFromFbc(cookie("_fbc"));
}
function pickFbc(fbclid){
  var c = cookie("_fbc");
  if (c && (!fbclid || fbclidFromFbc(c) === fbclid)) return c;
  if (!fbclid) return c;
  var built = ""; try { built = sessionStorage.getItem("bg_fbc") || ""; } catch(e){}
  if (!built || fbclidFromFbc(built) !== fbclid) { built = "fb.1." + Date.now() + "." + fbclid; try { sessionStorage.setItem("bg_fbc", built); } catch(e){} }
  return built;
}
function ensureFbp(){
  var f = cookie("_fbp"); if (f) return f;
  var s = ""; try { s = sessionStorage.getItem("bg_fbp") || ""; } catch(e){}
  if (!s) { s = "fb.1." + Date.now() + "." + Math.floor(Math.random() * 1e10); try { sessionStorage.setItem("bg_fbp", s); } catch(e){} }
  setCookie("_fbp", s); return s;
}
var FBCLID = readFbclid();
var LEAD_ID = "";
function isTest(a){ return /@example\.com$/i.test(a.email || "") || qp("bgtest") === "1"; }
function leadPayload(){
  var a = state.a, r = routeOf(a), leak = leakOf(a), v = videoFor(a, r === "early");
  var parts = {}; PARTS.forEach(function(p){ parts[p.id] = num(a[p.id]); });
  var labels = {}; Q.forEach(function(q){ if (a[q.id] !== undefined && q.options) labels[q.id] = labelOf(q.id, a[q.id]); });
  if (!LEAD_ID) LEAD_ID = Date.now().toString(36) + Math.random().toString(36).slice(2, 8);
  return {
    lead_id: LEAD_ID, source: "Scorecard", test: isTest(a),
    name: a.name || "", email: a.email || "", phone: a.phone || "",
    answers: (function(){ var o = {}; Q.forEach(function(q){ if (a[q.id] !== undefined) o[q.id] = a[q.id]; }); return o; })(),
    answer_labels: labels,
    part_scores: parts, score: scoreOf(a), band: bandOf(scoreOf(a)).label,
    biggest_leak: leak.id, biggest_leak_label: leak.label, lever: num(a[leak.id]) >= 75,
    route: r,
    video_id: v ? v.id : "", video_start: v ? (v.t || 0) : 0, video_title: v ? v.title : "",
    page_url: location.href, referrer: document.referrer || "", ua: navigator.userAgent || "",
    fbclid: FBCLID, fbc: pickFbc(FBCLID), fbp: ensureFbp(),
    attribution: ATTR, consent_version: CONSENT_VERSION, submitted_at: new Date().toISOString()
  };
}
function sendLead(){
  var body;
  try { body = JSON.stringify(leadPayload()); } catch(e){ return; }
  try {
    fetch(WEBHOOK, {method:"POST", mode:"cors", keepalive:true, headers:{"Content-Type":"text/plain;charset=UTF-8"}, body:body}).catch(function(){});
  } catch(e) {
    try { navigator.sendBeacon && navigator.sendBeacon(WEBHOOK, body); } catch(e2){}
  }
  try { window.dispatchEvent(new CustomEvent("bg:scorecard-lead", {detail:{route:routeOf(state.a), lead_id:LEAD_ID, test:isTest(state.a)}})); } catch(e){}
}
function calendlyURL(a){
  var parts = ["hide_event_type_details=1", "hide_gdpr_banner=1"];
  var digits = String(a.phone || "").replace(/\D/g, "");
  if (digits.length === 10) digits = "1" + digits;
  if (a.name) parts.push("name=" + encodeURIComponent(a.name));
  if (/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(a.email || "")) parts.push("email=" + encodeURIComponent(a.email));
  if (digits.length >= 8 && digits.length <= 15) parts.push("a1=" + encodeURIComponent("+" + digits));
  ["utm_source","utm_medium","utm_campaign","utm_content","utm_term"].forEach(function(k){ if (ATTR[k]) parts.push(k + "=" + encodeURIComponent(ATTR[k])); });
  var su = (ATTR.ad_id || ATTR.adset_id || FBCLID) ? ["bg1", ATTR.ad_id, ATTR.adset_id, FBCLID].join(".") : "";
  if (su) parts.push("salesforce_uuid=" + encodeURIComponent(su));
  return "__CAL__?" + parts.join("&");
}
var calLoaded = false;
function mountCalendly(root){
  var box = $("#cal-live", root); if (!box) return;
  var el = document.createElement("div");
  el.className = "calendly-inline-widget";
  el.setAttribute("data-url", calendlyURL(state.a));
  box.appendChild(el);
  if (window.Calendly && window.Calendly.initInlineWidget) { window.Calendly.initInlineWidget({url:el.getAttribute("data-url"), parentElement:el}); el.setAttribute("data-processed", "true"); return; }
  if (calLoaded) return;
  calLoaded = true;
  var s = document.createElement("script");
  s.src = "https://assets.calendly.com/assets/external/widget.js"; s.async = true;
  document.body.appendChild(s);
}
window.addEventListener("message", function(e){
  if (String(e.origin || "").indexOf("calendly.com") === -1) return;
  var d = e.data; if (!d || d.event !== "calendly.event_scheduled") return;
  if (state.view === "result" && state.step && state.step.kind === "result") showBooked($("#v-result"));
});
'''
TRACK = TRACK.replace("__WEBHOOK__", WEBHOOK).replace("__CAL__", CAL_BASE)
rep("/* ---------- views ---------- */", TRACK + "\n/* ---------- views ---------- */")

# ---------- JS: live calendar ----------
rep_re(r"function calendarHTML\(a\)\{.*?\n\}\n",
'''function calendarHTML(a){
  return '<div class="cal-live" id="cal-live" aria-label="Pick a time for your call"></div>';
}
''')

# ---------- JS: Leak Finder hidden until it has a product link and price ----------
rep_re(r"  var lf = '<button type=\"button\" class=\"next-card\" data-toast=.*?</button>';\n", "  var lf = ''; /* Leak Finder card hidden until it has a product link and price */\n")
rep("""    (early ? '' : '<p class="note">The Leak Finder is charged at checkout only if you buy it.</p>') +\n""", "")

# ---------- JS: booked state (Calendly does not pass the time to the page) ----------
rep_re(r"function bookedHTML\(a, day, time\)\{.*?\n\}\nfunction showBooked\(root, day, time\)\{\n  var nx = \$\(\".next\", root\); if \(!nx\) return;\n  nx.innerHTML = bookedHTML\(state.a, day, time\);",
'''function bookedHTML(a){
  return '<div class="panel">' + eyebrowHTML("Your next step", "") +
    '<h2 id="booked-h" tabindex="-1">You’re booked' + (a.name ? ', ' + esc(a.name) : '') + '</h2>' +
    '<p class="lead">Accept the calendar invite when it lands, and check spam if you don’t see it.</p>' +
    (a.partners === "yes" ? '<p class="note">Add your partner to the invite so they can join the call.</p>' : '') +
    '<h3 class="vid-h">Before your call, watch this</h3>' + videoCardHTML(a, false) + '</div>';
}
function showBooked(root){
  var nx = $(".next", root); if (!nx) return;
  state.step = {kind:"booked"};
  nx.innerHTML = bookedHTML(state.a);''')

rep_re(r"function wireResult\(root\)\{.*?\n\}\n",
'''function wireResult(root){
  mountCalendly(root);
  var jb = $("#jump-book", root);
  if (jb) jb.addEventListener("click", function(){ var nx = $(".next", root); try { nx.scrollIntoView({behavior: reduce ? "auto" : "smooth", block:"start"}); } catch(e){ nx.scrollIntoView(); } var h = $(".next h2", root); if (h) { h.setAttribute("tabindex", "-1"); try { h.focus({preventScroll:true}); } catch(e){} } });
  $$("[data-toast]", root).forEach(function(b){ b.addEventListener("click", function(){ toast(b.getAttribute("data-toast")); }); });
}
''')

# ---------- JS: drop setter view, review drawer, hash jumps ----------
rep_re(r"function showSetter\(\)\{.*?\n\}\n\n/\* ---------- toast", "/* ---------- toast")
rep_re(r"/\* ---------- review drawer ---------- \*/.*?\n\}\n\n/\* ---------- global wiring", "/* ---------- global wiring")
rep('''  if (e.key === "Escape" && !rv.hidden) { setReview(false); fab.focus(); return; }\n''', '')
rep_re(r"function fromHash\(\)\{.*?fromHash\(\);\n", "")
rep("var state = {a:{name:\"\"}, step:null, showSTL:false, lock:false, view:\"start\"};",
    "var state = {a:{name:\"\"}, step:null, showSTL:false, lock:false, view:\"start\"};")

open(out, "w", encoding="utf-8").write(h)
# leftovers check
for bad in ["rv-fab", "showSetter", "Preview only", "vp-note\">", "data-jump", "Draft review", "setReview", "fromHash"]:
    if bad in h:
        print("LEFTOVER:", bad)
print("bytes", len(h.encode()))
