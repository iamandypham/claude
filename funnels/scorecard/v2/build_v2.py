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
  '    field:{id:"f-email", label:"Email", type:"email", autocomplete:"email", placeholder:"you@example.com", inputmode:"email"}, cta:"Send my score"},\n  ')
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

# 7. intro screen first (Jeremy spec), quiz starts on the CTA
rep('''function showStart(){ if (state.view === "quiz" && state.step && state.step.kind === "q" && state.step.id === Q[0].id) return; goQ(Q[0].id, -1); }''',
    '''function showStart(){ state.step = null; show("start"); } /* V2-INTRO 2026-11-13 (Jeremy spec): intro sells the score before question 1 */''')
rep('''try { state.example = null; try { track("quiz_start", {}); } catch(e){} goQ(Q[0].id, 1); } catch(e){ try { show("start"); } catch(e2){} }''',
    '''try { state.example = null; showStart(); } catch(e){ try { show("start"); } catch(e2){} }''')
rep('''<h1 class="h-hero">Where is your trading business <em>leaking money?</em></h1>''', '''<h1 class="h-hero">Find where your trading business is <em>leaking money.</em></h1>''')
rep('''<p class="lede">Score the six parts of your funnel across traffic, conversion and monetisation. See your biggest leak and the first move to fix it.</p>''',
    '''<p class="lede">Answer a few quick questions about your trading community. You get your Leak Score out of 100, the one part to fix first, and your move this week.</p>''')
rep('''data-action="begin">Find my biggest leak''', '''data-action="begin">Get my Leak Score''')
rep('''<ul class="meta-row"><li>About 3 minutes</li><li>Free</li><li>Your score shows the moment you finish</li></ul>''',
    '''<ul class="meta-row"><li>Free</li><li>About 3 minutes</li><li>Your score on screen</li></ul>''')
rep('''<p class="proof-line">From the team that’s helped trading education businesses do <strong>$20M+</strong> in revenue.</p>''',
    '''<p class="proof-line">We’ve helped trading education businesses do <strong>$20M+</strong> in revenue.</p>''')


# 9. mobile banner: section name only, no counts or percentages (Jeremy spec)
rep('''    $("#bgx-b-count").textContent = ($("#q-count").textContent || "") + " · " + pct + "%";''',
    '''    $("#bgx-b-count").textContent = (function(){ try { var sg = s.kind === "q" ? byId[s.id].seg : "next"; return ({you:"About you", traffic:"Traffic", conversion:"Conversion", monetisation:"Monetisation", next:"Next step"})[sg] || ""; } catch(e){ return ""; } })(); /* V2-NOCOUNT */''')

# 10. send finished leads to the side-by-side n8n copy KUBSAOeLdXH8lcGx (under-$5K: tag lt5k, no SubmitApplication); live 4WaO untouched
rep('''var WEBHOOK = "https://businessgrowr.app.n8n.cloud/webhook/bg-scorecard-ghl";''', '''var WEBHOOK = "https://businessgrowr.app.n8n.cloud/webhook/bg-scorecard-v2-ghl"; /* V2-WEBHOOK */''')

# 11. reviewer fixes (review-v2.md, 13 Nov)
# 11a. Back button visible on Q1 now that the intro exists
rep("""  try { var bk = $("#v-quiz [data-action=back]"); if (bk) bk.style.visibility = id === Q[0].id ? "hidden" : ""; } catch(e){} /* QUIZSTEP v3.1pq: no Back on question 1 */""",
    """  try { var bk = $("#v-quiz [data-action=back]"); if (bk) bk.style.visibility = ""; } catch(e){} /* V2: Back on Q1 returns to the intro */""")
# 11b. timing/partner questions only for people who will see the calendar
rep("""function calAsk(a){ return (a.tiedown === "yes" || a.tiedown === "maybe") && a.who !== "prop" && a.who !== "vendor"; } /* V2-NOGATE */""",
    """function calAsk(a){ return routeOf(a) === "qualified" && (a.tiedown === "yes" || a.tiedown === "maybe"); } /* V2-NOGATE: calendar questions only for people who get the calendar */""")
# 11c. no expanded banner on Q1 (intro already sold it) and no "5 minutes"
rep("""<li>About 5 minutes. Your score shows the moment you finish</li>""", """<li>About 3 minutes. Your score shows the moment you finish</li>""")
rep("""    b.classList.toggle("is-full", q1);""", """    b.classList.toggle("is-full", false); /* V2: intro replaces the Q1 hero banner */""")
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
rep("""    title:function(){ return "Your score is almost ready."; },""", """    title:function(){ return "What’s your best email?"; },""")
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

# 8. mark the build
s = s.replace('<title>Revenue Leak Scorecard</title>', '<title>Revenue Leak Scorecard</title>\n<!-- SCORECARD V2 2026-11-13: intro, 12 questions, early email, no cash gate, no counter. Built from live element; Jeremy conv a31b5255. -->', 1)
open('scorecard-v2-element.html', 'w').write(s)
print('ok', len(src), '->', len(s))
