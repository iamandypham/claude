/* BusinessGrower.io draft. The page reads fine without this file; it adds the route map, the replay board and motion. */
(function () {
  document.documentElement.classList.add('js');
  var reduce = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* draft markers: on by default in the preview, remembered per browser */
  var body = document.body, stored = null;
  try { stored = localStorage.getItem('bgio-review'); } catch (e) {}
  if (stored !== 'off') body.classList.add('review');
  var tbtn = document.querySelector('[data-review-toggle]');
  var sync = function () { if (tbtn) tbtn.textContent = body.classList.contains('review') ? 'Hide draft markers' : 'Show draft markers'; };
  if (tbtn) tbtn.addEventListener('click', function () {
    body.classList.toggle('review');
    try { localStorage.setItem('bgio-review', body.classList.contains('review') ? 'on' : 'off'); } catch (e) {}
    sync();
  });
  sync();

  /* entrances */
  document.querySelectorAll('[data-stagger]').forEach(function (g) {
    g.querySelectorAll('.rise').forEach(function (el, i) { el.style.setProperty('--i', Math.min(i, 6)); });
  });
  var risers = document.querySelectorAll('.rise');
  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add('is-in'); io.unobserve(e.target); } });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.05 });
    risers.forEach(function (r) { io.observe(r); });
  } else { risers.forEach(function (r) { r.classList.add('is-in'); }); }

  /* channel switch in the automation panel */
  document.querySelectorAll('[data-channel]').forEach(function (box) {
    var msg = box.querySelector('.msg'), when = box.querySelector('[data-when]'), title = box.querySelector('[data-title]');
    var modes = {
      email: { title: 'Day 2 email', msg: 'Subject: Watch this before your next trade', when: 'Day 2 of the sequence' },
      sms: { title: 'Call reminder', msg: 'Reminder: your call is tomorrow at 2pm. Reply here to move it, or STOP to opt out.', when: '1 day before the call' }
    };
    box.querySelectorAll('.seg button').forEach(function (b) {
      b.addEventListener('click', function () {
        var m = modes[b.getAttribute('data-mode')];
        box.querySelectorAll('.seg button').forEach(function (o) { o.setAttribute('aria-pressed', o === b ? 'true' : 'false'); });
        msg.style.opacity = 0;
        setTimeout(function () { msg.textContent = m.msg; title.textContent = m.title; when.textContent = m.when; msg.style.opacity = 1; }, reduce ? 0 : 180);
      });
    });
  });

  /* the route map */
  var svg = document.getElementById('map');
  if (!svg) return;
  var NS = 'http://www.w3.org/2000/svg';
  var el = function (tag, attrs, parent) {
    var n = document.createElementNS(NS, tag);
    for (var k in attrs) n.setAttribute(k, attrs[k]);
    (parent || svg).appendChild(n);
    return n;
  };

  // grey network: the separate tools a setup gets stitched from (illustrative)
  var lines = [
    'M40 60 H300 L420 180 H760',
    'M560 40 V300 L640 380 V660',
    'M40 300 H200 L300 400 H520',
    'M120 660 H420 L520 560 H760',
    'M700 120 V480 H760',
    'M200 140 V300'
  ];
  var tools = [
    ['page tool', 120, 60, 0, -16, 'middle'], ['form app', 220, 60, 0, -16, 'middle'], ['link-in-bio', 480, 180, 0, -16, 'middle'],
    ['email app', 640, 180, 0, -16, 'middle', 1], ['newsletter', 760, 180, -4, 26, 'end'],
    ['texting app', 560, 100, 12, 5, 'start'], ['phone line', 560, 260, 12, 5, 'start'], ['spreadsheet', 640, 500, 12, 5, 'start'], ['CRM', 640, 620, 12, 5, 'start'],
    ['scheduler', 80, 300, 0, -15, 'middle'], ['calendar', 200, 300, -12, 5, 'end', 1], ['connector', 380, 400, 0, -15, 'middle'], ['invoices', 520, 400, 12, 5, 'start'],
    ['reminders', 200, 660, 0, 24, 'middle'], ['chat inbox', 320, 660, 0, 24, 'middle'], ['reports', 640, 560, 0, -15, 'middle', 1], ['surveys', 760, 560, -4, -15, 'end'],
    ['autoresponder', 700, 300, -12, 5, 'end'], ['web forms', 200, 220, -12, 5, 'end']
  ];
  var stops = [
    { name: 'Lead magnet', tool: 'Web page builder', what: 'They trade their email for a checklist, a short PDF or a free Discord invite. Now you own the contact.', t: '0:00', x: 80, y: 180, lx: 80, ly: 145, a: 'middle' },
    { name: 'E-mail', tool: 'E-mail automation builder', what: 'A sequence sends them through your YouTube videos in order, each one breaking a belief before the offer.', t: '+2 min', x: 300, y: 180, lx: 300, ly: 145, a: 'middle' },
    { name: 'SMS', tool: 'SMS automation builder', what: 'Texts follow up alongside your emails and remind them about their booked call.', t: '+1 day', x: 420, y: 300, lx: 444, ly: 296, a: 'start' },
    { name: 'Book a call', tool: 'Calendar', what: 'Leads who fit your high ticket offer book a call from the same funnel.', t: '+2 days', x: 420, y: 480, lx: 396, ly: 486, a: 'end' },
    { name: 'Pipeline', tool: 'Visual pipeline', what: 'Opted in, booked, showed, paid. You see where leads drop off.', t: '+3 days', x: 600, y: 480, lx: 600, ly: 520, a: 'middle' }
  ];
  var routeD = 'M80 180 H300 L420 300 V480 H600';

  var gNet = el('g', { fill: 'none', stroke: '#A3ABBA', 'stroke-width': 6, 'stroke-linejoin': 'round', 'stroke-linecap': 'round' });
  lines.forEach(function (d) { el('path', { d: d }, gNet); });
  el('path', { d: routeD, fill: 'none', stroke: '#0E182C', 'stroke-width': 18, 'stroke-linejoin': 'round', 'stroke-linecap': 'round' });
  var route = el('path', { d: routeD, fill: 'none', stroke: '#3D725F', 'stroke-width': 10, 'stroke-linejoin': 'round', 'stroke-linecap': 'round' });

  var gTools = el('g', {});
  tools.forEach(function (s) {
    el('circle', { cx: s[1], cy: s[2], r: s[6] ? 7 : 5, fill: '#fff', stroke: s[6] ? '#56627C' : '#A3ABBA', 'stroke-width': s[6] ? 3 : 2.5 }, gTools);
    var t = el('text', { x: s[1] + s[3], y: s[2] + s[4], 'text-anchor': s[5], class: 'lbl' }, gTools);
    t.textContent = s[0];
  });

  var rows = Array.prototype.slice.call(document.querySelectorAll('[data-route] tbody tr'));
  var nodes = stops.map(function (s, i) {
    var g = el('g', { class: 'stop', tabindex: 0, role: 'button', 'aria-label': s.name + ': ' + s.what });
    el('circle', { class: 'pulse', cx: s.x, cy: s.y, r: 14 }, g);
    el('circle', { class: 'ring', cx: s.x, cy: s.y, r: 13, fill: '#fff', stroke: '#0E182C', 'stroke-width': 5 }, g);
    var lbl = el('text', { x: s.lx, y: s.ly, 'text-anchor': s.a, class: 'stop-lbl' }, g);
    lbl.textContent = s.name;
    var tag = el('g', { class: 'tag' }, g);
    var w = s.t.length * 7.5 + 14;
    var tx = s.a === 'start' ? s.lx : (s.a === 'end' ? s.lx - w : s.lx - w / 2);
    el('rect', { x: tx, y: s.ly + 7, width: w, height: 20, rx: 3 }, tag);
    var tt = el('text', { x: tx + w / 2, y: s.ly + 21, 'text-anchor': 'middle' }, tag);
    tt.textContent = s.t;
    g.addEventListener('click', function () { stopPlay(); go(i); });
    g.addEventListener('keydown', function (e) { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); stopPlay(); go(i); } });
    return g;
  });

  // draw the route in once the map is on screen
  var len = route.getTotalLength();
  if (!reduce) {
    route.style.strokeDasharray = len;
    route.style.strokeDashoffset = len;
    route.getBoundingClientRect();
    route.style.transition = 'stroke-dashoffset 1.8s cubic-bezier(0.22, 1, 0.36, 1)';
  }

  // replay board
  var board = document.querySelector('[data-board]');
  var bStop = board && board.querySelector('.board-stop');
  var bTime = board && board.querySelector('.board-time');
  var bWhat = board && board.querySelector('.board-what');
  var bBars = board ? board.querySelectorAll('.board-stops i') : [];
  var bBtn = board && board.querySelector('button');
  var cur = -1, timer = null;

  function go(i) {
    cur = i;
    nodes.forEach(function (n, k) { n.classList.toggle('active', k === i); });
    rows.forEach(function (r, k) { r.classList.toggle('active', k === i); });
    Array.prototype.forEach.call(bBars, function (b, k) { b.className = k < i ? 'past' : (k === i ? 'on' : ''); });
    if (bStop) { bStop.textContent = stops[i].name; bTime.textContent = stops[i].t; bWhat.textContent = stops[i].what; }
  }
  function play() {
    if (timer) return;
    if (bBtn) bBtn.textContent = 'Pause';
    timer = setInterval(function () { go((cur + 1) % stops.length); }, 1800);
  }
  function stopPlay() {
    clearInterval(timer); timer = null;
    if (bBtn) bBtn.textContent = 'Replay';
  }
  if (bBtn) bBtn.addEventListener('click', function () { if (timer) stopPlay(); else { go((cur + 1) % stops.length); play(); } });
  rows.forEach(function (r, i) {
    r.addEventListener('mouseenter', function () { stopPlay(); go(i); });
    r.addEventListener('click', function () { stopPlay(); go(i); });
    r.tabIndex = 0;
    r.addEventListener('keydown', function (e) { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); stopPlay(); go(i); } });
  });

  var started = false;
  function start() {
    if (started) return; started = true;
    if (!reduce) route.style.strokeDashoffset = 0;
    setTimeout(function () { go(0); if (!reduce) play(); }, reduce ? 0 : 1200);
  }
  if ('IntersectionObserver' in window) {
    var mo = new IntersectionObserver(function (es) { if (es[0].isIntersecting) { start(); mo.disconnect(); } }, { threshold: 0.25 });
    mo.observe(svg);
  } else start();
  document.addEventListener('visibilitychange', function () { if (document.hidden) stopPlay(); });
})();
