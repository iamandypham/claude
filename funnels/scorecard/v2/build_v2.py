"""Build scorecard v2 (Jeremy spec 13 Nov 2026, Andy picks) from the live element. Usage: python3 build_v2.py"""
import re, sys
src = open('live-element-2026-11-13.html').read()
s = src
def rep(old, new, count=1):
    global s
    n = s.count(old)
    if n != count: sys.exit(f'expected {count} of {old[:80]!r}, found {n}')
    s = s.replace(old, new)

def cut_q(qid):
    global s
    i = s.find('{id:"%s"' % qid); assert i > 0, qid
    j = s.find('\n  {id:"', i + 5); k = s.find('\n  /*', i + 5)
    ends = [x for x in (j, k) if x > 0]
    # also handle end of array
    e = min(ends)
    s = s[:i] + s[e+3:] if s[e+1:e+3] == '  ' else s[:i] + s[e:]

# 1. cut 4 questions (Jeremy: path12, work_model, content_time, source)
for q in ['path12', 'work_model', 'content_time', 'source']:
    cut_q(q)

# 2. email-only screen after trading (Q list), as a text question
i = s.find('{id:"audience"'); assert i > 0
email_q = ('{id:"email", seg:"you", type:"text", eyebrow:"Your score", eyebrowDim:"Almost ready",\n'
  '    title:function(){ return "Your score is almost ready."; },\n'
  '    sub:"Where should we send it? Your full scorecard, your biggest leak and your first fix go to this email. Free.",\n'
  '    field:{id:"f-email", label:"Business email", type:"email", autocomplete:"email", placeholder:"you@yourbusiness.com", inputmode:"email"}, cta:"Send my score"},\n  ')
s = s[:i] + email_q + s[i:]

# 3. text wiring handles email as well as name
rep('''  if (q.type === "text") wireField(q.field, function(val){
    var v = val.trim().replace(/\\s+/g, " ");''', '''  if (q.type === "text") wireField(q.field, function(val){
    if (q.id === "email") { /* V2-EMAIL-EARLY 2026-11-13 (Jeremy spec): email-only capture after the first questions -> partial lead */
      var ev = val.trim();
      if (!/^[^\\s@]+@[^\\s@]+\\.[^\\s@]{2,}$/.test(ev)) return "Enter an email like name@example.com.";
      state.a.email = ev; postPartial("answer", {q:"email", v:ev});
      try { track("quiz_answer", {step_number:visibleQs().indexOf(q) + 1, step_id:"email", question:qText(q), answer:""}); } catch(e){}
      return advanceFrom(q);
    }
    var v = val.trim().replace(/\\s+/g, " ");''')
# text field button label + prefill for email
rep('''    html += fieldHTML(q.field, state.a.name, "Continue");''', '''    html += fieldHTML(q.field, q.id === "email" ? state.a.email : state.a.name, q.cta || "Continue");''')

# 4. contact part = name + phone (Andy 10 Nov: name stays in the contact part)
i = s.find('var CONTACT'); j = s.find('{id:"email", title:function(a)', i); k = s.find('{id:"phone"', j)
assert 0 < i < j < k
s = s[:j] + s[k:]

# 5. no question counter (section rail only)
rep('''  $("#q-count").textContent = q.cal ? "Before your call · " + q.cal + " of 2" : q.when ? "Follow-up to question " + n : "Question " + n + " of " + base.length;''',
    '''  $("#q-count").textContent = ""; /* V2-NOCOUNT 2026-11-13: section rail only */''')
rep('''  $("#q-count").textContent = "Last step · " + (i + 1) + " of " + CONTACT.length;''', '''  $("#q-count").textContent = "";''')
rep('''  var html = eyebrowHTML("Your scorecard is ready", "Step " + (i + 1) + " of " + CONTACT.length) +''', '''  var html = eyebrowHTML("Your scorecard is ready", "Last step") +''')

# 6. no cash gate: liquid is data only (Andy 13 Nov). Under-$5K still writes the liquid CF -> 33Dn sends ScheduleUnder5k.
rep('''  return ((revenue || following || trader) && liquid) ? "qualified" : "nurture";''', '''  return (revenue || following || trader) ? "qualified" : "nurture"; /* V2-NOGATE 2026-11-13 (Andy): no cash gate; liquid = data only */''')
rep('''function calAsk(a){ return (a.tiedown === "yes" || a.tiedown === "maybe") && !!a.liquid && a.liquid !== "lt5" && a.who !== "prop" && a.who !== "vendor"; }''',
    '''function calAsk(a){ return (a.tiedown === "yes" || a.tiedown === "maybe") && a.who !== "prop" && a.who !== "vendor"; } /* V2-NOGATE */''')

# 7. NO start screen (Andy 13 Nov: "this is the screen we were running before and nobody was clicking"; Jeremy agrees). Open on Q1; the hero banner above Q1 carries the promise.
rep('''<p class="bgx-b-get">You get your Leak Score out of 100, the part of your funnel to fix first, and your move this week.</p>''',
    '''<p class="bgx-b-get">Free scorecard for trading educators. About 3 minutes.</p>''')
rep('''<ul class="bgx-b-list"><li>About 5 minutes. Your score shows the moment you finish</li><li>Free. Just tap your answers</li></ul>''',
    '''<ul class="bgx-b-list"><li>Your Leak Score out of 100 and the part to fix first</li><li>Free. Just tap your answers</li></ul>''')

# 9. mobile banner: section name only, no counts or percentages (Jeremy spec)
rep('''    $("#bgx-b-count").textContent = ($("#q-count").textContent || "") + " · " + pct + "%";''',
    '''    $("#bgx-b-count").textContent = (function(){ try { var sg = s.kind === "q" ? byId[s.id].seg : "next"; return ({you:"About you", traffic:"Traffic", conversion:"Conversion", monetisation:"Monetisation", next:"Next step"})[sg] || ""; } catch(e){ return ""; } })(); /* V2-NOCOUNT */''')

# 10. send finished leads to the side-by-side n8n copy KUBSAOeLdXH8lcGx (under-$5K: tag lt5k, no SubmitApplication); live 4WaO untouched
rep('''var WEBHOOK = "https://businessgrowr.app.n8n.cloud/webhook/bg-scorecard-ghl";''', '''var WEBHOOK = "https://businessgrowr.app.n8n.cloud/webhook/bg-scorecard-v2-ghl"; /* V2-WEBHOOK */''')

# 11. reviewer fixes (review-v2.md, 13 Nov)
# 11b. timing/partner questions only for people who will see the calendar
rep("""function calAsk(a){ return (a.tiedown === "yes" || a.tiedown === "maybe") && a.who !== "prop" && a.who !== "vendor"; } /* V2-NOGATE */""",
    """function calAsk(a){ return routeOf(a) === "qualified" && (a.tiedown === "yes" || a.tiedown === "maybe"); } /* V2-NOGATE: calendar questions only for people who get the calendar */""")
# 11d. no counts anywhere
rep("""    $("#bgx-b-fill").style.width = pct + "%";
    $("#bgx-b-bar").setAttribute("aria-valuenow", String(pct));""",
    """    $("#bgx-b-fill").style.width = "0%"; $("#bgx-b-bar").style.display = "none"; /* V2-NOCOUNT: no percentage bar */""")
rep("""var sg = s.kind === "q" ? byId[s.id].seg : "next";""", """var sg = (s.kind === "q" || s.kind === "presell") && byId[s.id] ? byId[s.id].seg : "next";""")
rep("""  var eb = q.eyebrow ? eyebrowHTML(q.eyebrow, q.eyebrowDim) : st.part ? eyebrowHTML(st.part, st.label) : eyebrowHTML(st.label, "");""",
    """  var eb = q.eyebrow ? eyebrowHTML(q.eyebrow, q.eyebrowDim) : eyebrowHTML(st.label, ""); /* V2-NOCOUNT: section name only */""")
rep("""<p class="build-n"><span id="build-n">0</span> of 6 parts scored</p>""", """<p class="build-n"><span id="build-n">0</span> parts scored</p>""")
rep("""  var html = eyebrowHTML("Your scorecard is ready", "Last step") +""",
    """  var html = eyebrowHTML("Your scorecard is ready", (state.step && state.step.i) ? "Last step" : "Almost done") +""")
# 11e. email screen copy that is true where it sits
rep("""    title:function(){ return "Your score is almost ready."; },""", """    title:function(){ return "What’s your business email?"; },""")
rep("""    sub:"Where should we send it? Your full scorecard, your biggest leak and your first fix go to this email. Free.",""",
    """    sub:"We’ll save your progress. Your Leak Score is about 2 minutes away. Free.",""")
rep("""inputmode:"email"}, cta:"Send my score"},""", """inputmode:"email"}, cta:"Continue"},""")
rep("""eyebrow:"Your score", eyebrowDim:"Almost ready",""", """eyebrow:"Your score", eyebrowDim:"Saved as you go",""")
# 11f. quiz_start once per session
rep("""  if (act === "begin") { state.example = null; try { track("quiz_start", {}); } catch(e){} goQ(Q[0].id, 1); }""",
    """  if (act === "begin") { state.example = null; try { if (!state.started) { state.started = true; track("quiz_start", {}); } } catch(e){} goQ(Q[0].id, 1); }""")

# 12. email screen -> n8n enYxj1N5YZUaZfQC (email-only partial into GHL, tags scorecard-v2 + scorecard-partial; its Lead CAPI node is OFF until Andy's go)
rep('''  var PARTIAL_URL = "https://businessgrowr.app.n8n.cloud/webhook/bg-scorecard-partial";''',
'''  var PARTIAL_URL = "https://businessgrowr.app.n8n.cloud/webhook/bg-scorecard-partial";
  var V2_EMAIL_URL = "https://businessgrowr.app.n8n.cloud/webhook/bg-scorecard-v2-email"; /* V2-EMAIL-CAPTURE */
  function postEmailCapture(ev){
    try {
      ensureSession();
      var a = state.a || {};
      var body = { email: ev, lead_id: LEAD_ID || SESSION_ID, session_id: SESSION_ID, page_url: location.href, ua: navigator.userAgent || "",
        fbclid: (typeof FBCLID !== "undefined" ? FBCLID : ""), fbc: (typeof pickFbc === "function" ? pickFbc(FBCLID) : ""), fbp: (typeof ensureFbp === "function" ? ensureFbp() : ""),
        attribution: (typeof ATTR !== "undefined" ? ATTR : {}),
        test: (typeof isTest === "function" ? isTest(a) : false) || /\\?.*bgtest=1|example\\.com/i.test(location.href + " " + ev) };
      var txt = JSON.stringify(body);
      if (navigator.sendBeacon) { try { if (navigator.sendBeacon(V2_EMAIL_URL, new Blob([txt], {type: "text/plain;charset=UTF-8"}))) return; } catch(e){} }
      fetch(V2_EMAIL_URL, {method:"POST", body: txt, headers:{"Content-Type":"text/plain;charset=UTF-8"}, keepalive:true, mode:"cors", credentials:"omit"}).catch(function(){});
    } catch(e){}
  }''')
rep('''      state.a.email = ev; postPartial("answer", {q:"email", v:ev});''',
    '''      state.a.email = ev; postPartial("answer", {q:"email", v:ev}); postEmailCapture(ev);''')

# 13. no consent line on the phone screen (Andy 13 Nov 7:10 PM ET: "We don't need phone consent remove that"). consent_version blank so records don't claim consent.
i = s.find(',\n    consent:"By tapping See my score'); j = s.find("Terms</a>.'}", i)
assert 0 < i < j
s = s[:i] + '}' + s[j + len("Terms</a>.'}"):]
rep('''var CONSENT_VERSION = "scorecard-2026-11-08";''', '''var CONSENT_VERSION = ""; /* V2: no consent line (Andy 13 Nov) */''')

# 14. phone + business email on one screen at Q3 (Jeremy 13 Nov 7:11 PM ET pick (b); Andy asked phone first). Contact part at the end = first name only.
rep('''    title:function(){ return "What’s your business email?"; },''', '''    title:function(){ return "Where should we send your Leak Score?"; },''')
rep('''    html += fieldHTML(q.field, q.id === "email" ? state.a.email : state.a.name, q.cta || "Continue");''',
    '''    html += fieldHTML(q.field, q.id === "email" ? state.a.email : state.a.name, q.cta || "Continue", q.id === "email" ? ('<label class="field-label" for="f-phone2" style="margin-top:14px">Mobile number</label><input class="field" id="f-phone2" name="f-phone2" type="tel" inputmode="tel" autocomplete="tel" placeholder="+1 555 123 4567" value="' + esc(state.a.phone || "") + '">') : ""); /* V2-PHONE-EARLY */''')
rep('''      if (!/^[^\\s@]+@[^\\s@]+\\.[^\\s@]{2,}$/.test(ev)) return "Enter an email like name@example.com.";
      state.a.email = ev; postPartial("answer", {q:"email", v:ev}); postEmailCapture(ev);''',
    '''      if (!/^[^\\s@]+@[^\\s@]+\\.[^\\s@]{2,}$/.test(ev)) return "Enter an email like name@example.com.";
      var pv = (($("#f-phone2") || {}).value || "").trim(), pd = pv.replace(/\\D/g, "");
      if (pd.length < 7 || pd.length > 15) return "Enter your mobile number, with the country code if you’re outside the US.";
      state.a.email = ev; state.a.phone = pv; postPartial("answer", {q:"email", v:ev}); postPartial("contact", {q:"phone", v:pv}); postEmailCapture(ev);''')
rep('''attribution: (typeof ATTR !== "undefined" ? ATTR : {}),
        test:''', '''attribution: (typeof ATTR !== "undefined" ? ATTR : {}), phone: a.phone || "",
        test:''')
# drop the phone screen from CONTACT; name becomes the last step and finishes the lead
i = s.find('var CONTACT'); j = s.find(',\n  {id:"phone"', i); k = s.find('\n];', j)
assert 0 < i < j < k
s = s[:j] + s[k:]
rep('''      try { track("quiz_answer", {step_number:visibleQs().length + i + 1, step_id:"name", answer:""}); } catch(e){}
      return goContact(i + 1, 1);''',
    '''      try { track("quiz_answer", {step_number:visibleQs().length + i + 1, step_id:"name", answer:""}); } catch(e){}
      if (i + 1 < CONTACT.length) return goContact(i + 1, 1);
      sendLead(); /* V2-PHONE-EARLY: phone came at Q3, name finishes */
      try { track("quiz_complete", {step_number:visibleQs().length + CONTACT.length, step_id:"name"}); } catch(e){}
      return runAnalyzing();''')

# 14b. first name is now the last screen
rep('''    sub:"We’ll put it on your scorecard.",
    field:{id:"f-name", label:"First name", type:"text", autocomplete:"given-name", placeholder:"First name", inputmode:"text"}, cta:"Continue"}''',
    '''    sub:"We’ll put it on your scorecard. Your score shows on the next screen.",
    field:{id:"f-name", label:"First name", type:"text", autocomplete:"given-name", placeholder:"First name", inputmode:"text"}, cta:"See my score"}''')

# 15. Q1 message match (Jeremy 13 Nov ~7:15 PM ET, Andy "work with him to fix Q1 drop off"):
#     hero = the ad's own words (N2 default; per-ad by utm_content), thin white hero on Q1 (no dark card), Q1 = "First, what do you run?"
rep('''<p class="bgx-b-line">Find where your trading business is leaking money.</p>''',
    '''<p class="bgx-b-line" id="bgx-hook">Trading Discord owners: find your biggest funnel leak in about 3 minutes. Free.</p>''')
rep('''<p class="bgx-b-get">Free scorecard for trading educators. About 3 minutes.</p>''', '''<p class="bgx-b-get" id="bgx-hook-sub">Free scorecard for trading educators.</p>''')
rep('''    title:function(){ return "What best describes you?"; },''', '''    title:function(){ return "First, what do you run?"; },''')
rep('''</style>''', '''/* V2-Q1MATCH: on Q1 the hero is a plain white headline, so Q1 + 4 options sit above the fold on a phone */
#v-quiz.bgx-q1 .bgx-banner{background:none;box-shadow:none;padding:0;margin:0 0 12px;border-radius:0;color:var(--navy)}
#v-quiz.bgx-q1 .bgx-b-head,#v-quiz.bgx-q1 .bgx-b-bar,#v-quiz.bgx-q1 .bgx-b-count,#v-quiz.bgx-q1 .bgx-b-list{display:none}
#v-quiz.bgx-q1 .bgx-b-more{display:block;margin:0}
#v-quiz.bgx-q1 .bgx-b-line{color:var(--navy);font:700 21px/1.25 var(--f-display);letter-spacing:-.015em}
#v-quiz.bgx-q1 .bgx-b-get{color:var(--muted);margin-top:4px;font-size:14px}
#v-quiz.bgx-q1 .h-q{font-size:22px;line-height:1.2;margin-top:6px}
@media (max-width:599px){#v-quiz.bgx-q1 .opts{margin-top:12px}#v-quiz.bgx-q1 .opt{padding-top:10px;padding-bottom:10px}}
@media (min-width:720px){#v-quiz.bgx-q1 .bgx-b-line{font-size:28px}}
</style>''', )
rep('''var ATTR = {};''', '''var ATTR = {};
/* V2-Q1MATCH: each ad lands on its own hook, word for word (Jeremy). Default = N2, the ad that drove 64 of 110 sessions. */
var HOOKS = [
  {m:/N1|journal/i, h:"You journal every trade. Who’s journaling your business?", sub:"Find your biggest funnel leak in about 3 minutes. Free."}
];
function applyHook(){ try { var c = ATTR.utm_content || ""; for (var i = 0; i < HOOKS.length; i++) if (HOOKS[i].m.test(c)) { $("#bgx-hook").textContent = HOOKS[i].h; $("#bgx-hook-sub").textContent = HOOKS[i].sub; return; } } catch(e){} }''')
rep('''CLICK_KEYS.forEach(function(k){ ATTR[k] = keep(k); });''', '''CLICK_KEYS.forEach(function(k){ ATTR[k] = keep(k); });
if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", applyHook); else applyHook();''')

# 16. SC02 statics (Jeremy 13 Nov): each card's text is its page hero word for word, keyed by utm_content SC02-V1..V8
rep('''var HOOKS = [\n''', '''var HOOKS = [\n  {m:/SC02-V1\\b/i, h:"Trading Discord owners: one of your six funnel parts is leaking. Find it in about 3 minutes. Free.", sub:"Free scorecard for trading educators."},\n  {m:/SC02-V2\\b/i, h:"Whop community owners: find your biggest funnel leak in about 3 minutes. Free.", sub:"Free scorecard for trading educators."},\n  {m:/SC02-V3\\b/i, h:"Trading educators: find your biggest funnel leak in about 3 minutes. Free.", sub:"Free scorecard for trading educators."},\n  {m:/SC02-V4\\b/i, h:"Signal group owners: find your biggest funnel leak in about 3 minutes. Free.", sub:"Free scorecard for trading educators."},\n  {m:/SC02-V5\\b/i, h:"Trading Discord owners: if members keep cancelling, that’s a leak. Find your biggest one in about 3 minutes. Free.", sub:"Free scorecard for trading educators."},\n  {m:/SC02-V6\\b/i, h:"Whop community owners: if trials don’t convert, that’s a leak. Find your biggest one in about 3 minutes. Free.", sub:"Free scorecard for trading educators."},\n  {m:/SC02-V7\\b/i, h:"Trading educators: members leaving might be your biggest leak. Find out in about 3 minutes. Free.", sub:"Free scorecard for trading educators."},\n  {m:/SC02-V8\\b/i, h:"Trading Discord owners: score your funnel out of 100. See your biggest leak in about 3 minutes. Free.", sub:"Free scorecard for trading educators."},\n''')

# 8. mark the build
s = s.replace('<title>Revenue Leak Scorecard</title>', '<title>Revenue Leak Scorecard</title>\n<!-- SCORECARD V2 2026-11-13 (rev 2): opens on Q1, 12 questions, early email, no cash gate, no counter. Built from live element; Jeremy conv a31b5255. -->', 1)
open('scorecard-v2-element.html', 'w').write(s)
print('ok', len(src), '->', len(s))
