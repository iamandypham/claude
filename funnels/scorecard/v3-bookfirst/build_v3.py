"""Scorecard v3 'book first' result page (Andy 14 Nov 12:24 PM ET; Jeremy copy). Built from ../v2/scorecard-v2-element.html. Usage: python3 build_v3.py"""
import sys
s = open('../v2/scorecard-v2-element.html').read()
def rep(old, new, count=1):
    global s
    n = s.count(old)
    if n != count: sys.exit(f'expected {count} of {old[:90]!r}, found {n}')
    s = s.replace(old, new)

# 1. booking panel: Jeremy copy. Headline names the fix, video optional and never gates the calendar, callback right above the calendar.
rep('''function bookingHTML(a){
  return '<div class="panel">' + eyebrowHTML("Your next step", "") +
    '<h2>Book your Scaling Roadmap Call</h2>' +
    '<p class="lead">We’ll go through your scorecard with you and map out how to ' + (num(a[leakOf(a).id]) >= 75 ? 'pull your next lever' : 'fix your biggest leak first') + '. If it’s a fit, we’ll show you how we’d build it for you.</p>' +
    (a.tiedown === "yes" ? '<p class="callback">You said you’d want help putting the fix in place. That’s exactly what this call is for.</p>'
      : a.tiedown === "maybe" ? '<p class="callback">You said you’d like to see the plan first. That’s what this call is for.</p>' : '') +
    videoStepsHTML(a) + calendarHTML(a) +''',
'''function bookingHTML(a, s, b){ /* V3-BOOKFIRST 2026-11-14: booking panel is the top of the result page (Jeremy copy) */
  var leak = leakOf(a), lever = num(a[leak.id]) >= 75, vh = videoPlayerHTML(a, false);
  return '<div class="panel book-first" id="book-first">' +
    '<p class="bf-chip"><span class="pill tone-' + b.tone + '">Score ' + s + '/100</span><span>' + (lever ? 'Next lever' : 'Biggest leak') + ': <b>' + esc(leak.label) + '</b></span></p>' +
    '<h1 class="bf-h" id="res-title" tabindex="-1">' + (a.name ? esc(a.name) + ', your' : 'Your') + ' fix starts with ' + esc(leak.label) + '.</h1>' +
    '<p class="lead">Grab a time that works, then watch the short breakdown on your leak before the call.</p>' +
    (a.tiedown === "yes" ? '<p class="callback">You said you’d want help putting the fix in place. That’s exactly what this call is for.</p>'
      : a.tiedown === "maybe" ? '<p class="callback">You said you’d like to see the plan first. That’s what this call is.</p>' : '') +
    '<h2 class="step-h bf-ask"><span aria-hidden="true">1</span>Get your fix plan built on a call</h2>' +
    calendarHTML(a) +''')

rep('''    (a.partners === "yes" ? '<p class="note">Add your partner as a guest when you book, so they can join the call.</p>' : '') +
    '</div>';
}''', '''    (a.partners === "yes" ? '<p class="note">Add your partner as a guest when you book, so they can join the call.</p>' : '') +
    (vh ? '<h3 class="step-h bf-vid"><span aria-hidden="true">2</span><i class="sh-t">Before your call: the short breakdown on your leak</i></h3>' + vh : '') +
    '</div>';
}''')
# 1b. qualified: scoring animation ~1s (Jeremy audit 15 Nov)
rep('''      setTimeout(function(){ r.classList.add("done"); }, reduce ? 0 : 520);
    }, reduce ? 0 : 180 + i * 300);
  });
  setTimeout(showResult, reduce ? 700 : 2700);''', '''      setTimeout(function(){ r.classList.add("done"); }, reduce || fastAn ? 0 : 520);
    }, reduce ? 0 : (fastAn ? 60 + i * 120 : 180 + i * 300));
  });
  setTimeout(showResult, reduce ? 700 : (fastAn ? 1000 : 2700)); /* V3-BOOKFIRST: qualified gets ~1s */''')
rep('''  state.step = {kind:"analyzing"};''', '''  state.step = {kind:"analyzing"}; var fastAn = routeOf(a) === "qualified";''')

# 2. result page: qualified -> booking panel first, full report below, no second next-step aside, no jump button
rep('''  var html =
    '<div class="wrap res-head">' + eyebrowHTML("Revenue Leak Scorecard", date) +
      '<h1 class="h-res" id="res-title" tabindex="-1">' + (a.name ? esc(a.name) + ", " + hl : hl.charAt(0).toUpperCase() + hl.slice(1)) + '</h1></div>' +
    '<div class="res-stage"><div class="band-res" aria-hidden="true"></div><div class="wrap res-grid">' +''',
'''  var bf = r === "qualified"; /* V3-BOOKFIRST */
  var html =
    (bf ? '<div class="wrap bf-wrap"><div class="next bf-next">' + bookingHTML(a, s, b) + '</div><p class="bf-more">Your full scorecard is below.</p></div>'
        : '<div class="wrap res-head">' + eyebrowHTML("Revenue Leak Scorecard", date) +
      '<h1 class="h-res" id="res-title" tabindex="-1">' + (a.name ? esc(a.name) + ", " + hl : hl.charAt(0).toUpperCase() + hl.slice(1)) + '</h1></div>') +
    '<div class="res-stage' + (bf ? ' bf-stage' : '') + '"><div class="band-res" aria-hidden="true"></div><div class="wrap res-grid' + (bf ? ' no-next' : '') + '">' +''')
rep('''        (r === "qualified" ? '<button type="button" class="jump-book" id="jump-book">''', '''        (false ? '<button type="button" class="jump-book" id="jump-book">''')
rep('''      '<aside class="next" aria-label="Your next step">' + (r === "qualified" ? bookingHTML(a) : nurtureHTML(a, r === "early")) + '</aside>' +''',
    '''      (bf ? '' : '<aside class="next" aria-label="Your next step">' + nurtureHTML(a, r === "early") + '</aside>') +''')
rep('''track("quiz_score_view", {step_id:"result", answer:r + "|" + s + "|" + leak.id});''',
    '''track("quiz_score_view", {step_id:"result", answer:r + "|" + s + "|" + leak.id + (bf ? "|bookfirst" : "")});''')

# 3. styles
rep('''</style>''', '''/* V3-BOOKFIRST */
.bf-wrap{padding-top:18px;position:relative;z-index:2}
.book-first .bf-chip{display:flex;flex-wrap:wrap;align-items:center;gap:8px 10px;margin:0;font-size:14px;color:var(--muted)}
.book-first .bf-chip b{color:var(--navy)}
.book-first .bf-h{margin-top:12px;font:700 clamp(26px, 1.4vw + 20px, 36px)/1.1 var(--f-display);letter-spacing:-.03em;color:var(--navy)}
.book-first .bf-ask{font-size:18px;margin-top:22px}
.book-first .bf-vid{margin-top:28px}
.book-first .bf-opt{font-style:normal;font-weight:500;color:var(--muted)}
.book-first .vp-body .vid-t,.book-first .vp-body .vid-src{display:none}
.book-first .sh-t{font-style:normal}
.bf-more{margin:14px 4px 0;font-size:14px;color:var(--muted);text-align:center}
.bf-stage{margin-top:8px}
@media (min-width:1024px){.bf-wrap{max-width:860px}.res-grid.no-next{grid-template-columns:minmax(0,1fr);grid-template-areas:"report" "parts";max-width:860px}}
</style>''')
s = s.replace('<title>Revenue Leak Scorecard</title>', '<title>Revenue Leak Scorecard</title>\n<!-- SCORECARD V3 BOOK-FIRST 2026-11-14: v2 + qualified result page opens on the booking panel (Jeremy copy). -->', 1)
open('scorecard-v3-element.html', 'w').write(s)
print('ok', len(s))
