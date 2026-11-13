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

# 8. mark the build
s = s.replace('<title>Revenue Leak Scorecard</title>', '<title>Revenue Leak Scorecard</title>\n<!-- SCORECARD V2 2026-11-13: intro, 12 questions, early email, no cash gate, no counter. Built from live element; Jeremy conv a31b5255. -->', 1)
open('scorecard-v2-element.html', 'w').write(s)
print('ok', len(src), '->', len(s))
