/* ============================================================
   ClearGrade v3 — Cinematic Landing Page JS
   ============================================================ */
(function () {
  'use strict';

  /* --- Audit Data --- */
  var DATA = {
    resurgent: {
      name: 'Resurgent Sports Rehab',
      desc: 'Sports physical therapy clinic in Northern Virginia',
      score: 61, grade: 'C+',
      link: 'https://davidkimmel.github.io/resurgent/',
      dims: [
        { l: 'Content & Messaging', s: 64 },
        { l: 'Conversion', s: 47 },
        { l: 'SEO & Discovery', s: 62 },
        { l: 'Competitive', s: 67 },
        { l: 'Brand & Trust', s: 72 },
        { l: 'Growth & Strategy', s: 55 }
      ],
      qw: [
        { t: 'Embed Booking Widget On-Site', d: 'Eliminate external redirect. 30-50% conversion lift.', i: 'h' },
        { t: 'Surface Pricing Near CTAs', d: 'Move pricing from FAQ to service pages.', i: 'h' },
        { t: 'Launch Content Hub', d: 'Zero blog content despite deep expertise. 3-5x traffic in 12mo.', i: 'm' }
      ]
    },
    fiddlers: {
      name: 'Fiddlers Green Farm',
      desc: 'Organic CBD farm and e-commerce store',
      score: 51, grade: 'D',
      link: 'https://davidkimmel.github.io/Fiddlersgreen/',
      dims: [
        { l: 'Content & Messaging', s: 58 },
        { l: 'Conversion', s: 42 },
        { l: 'SEO & Discovery', s: 44 },
        { l: 'Competitive', s: 58 },
        { l: 'Brand & Trust', s: 68 },
        { l: 'Growth & Strategy', s: 38 }
      ],
      qw: [
        { t: 'Remove Stale Holiday Banner', d: 'December banner still showing in March. Immediate trust fix.', i: 'h' },
        { t: 'Add PayPal + Apple Pay + BNPL', d: 'Missing 30%+ of e-commerce payments. $1.5-4K/mo.', i: 'h' },
        { t: 'Fix robots.txt + Link Lab COAs', d: 'Crawl-delay throttling all indexing of 33 products.', i: 'm' }
      ]
    }
  };

  var active = 'resurgent';

  /* --- Scroll animations --- */
  function initAnim() {
    var els = document.querySelectorAll('.anim');
    if (!els.length) return;
    var obs = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) { e.target.classList.add('visible'); obs.unobserve(e.target); }
      });
    }, { threshold: 0.1 });
    els.forEach(function (el) { obs.observe(el); });
  }

  /* --- Nav --- */
  function initNav() {
    var nav = document.querySelector('.nav');
    var ham = document.querySelector('.hamburger');
    var mob = document.querySelector('.mob-menu');
    if (nav) {
      var t = false;
      window.addEventListener('scroll', function () {
        if (!t) { requestAnimationFrame(function () { nav.classList.toggle('scrolled', scrollY > 40); t = false; }); t = true; }
      });
    }
    if (ham && mob) {
      ham.addEventListener('click', function () { ham.classList.toggle('open'); mob.classList.toggle('open'); });
      mob.querySelectorAll('a').forEach(function (a) {
        a.addEventListener('click', function () { ham.classList.remove('open'); mob.classList.remove('open'); });
      });
    }
  }

  /* --- Dashboard Preview --- */
  function sc(s) { return s >= 70 ? 'var(--success)' : s >= 50 ? 'var(--warning)' : 'var(--danger)'; }

  function countUp(el, target, dur) {
    var start = performance.now();
    function tick(now) {
      var p = Math.min((now - start) / dur, 1);
      var e = 1 - Math.pow(1 - p, 3);
      el.textContent = Math.round(e * target);
      if (p < 1) requestAnimationFrame(tick);
    }
    requestAnimationFrame(tick);
  }

  function render(key, anim) {
    var d = DATA[key]; if (!d) return;
    var circ = document.getElementById('g-circle');
    var numEl = document.getElementById('g-num');
    var gradeEl = document.getElementById('g-grade');
    var C = 2 * Math.PI * 52;
    var off = C - (d.score / 100) * C;

    circ.style.stroke = sc(d.score);
    if (anim) {
      circ.style.strokeDashoffset = C;
      void circ.offsetWidth;
      circ.style.strokeDashoffset = off;
      countUp(numEl, d.score, 1500);
    } else {
      circ.style.transition = 'none'; circ.style.strokeDashoffset = off;
      numEl.textContent = d.score; void circ.offsetWidth; circ.style.transition = '';
    }
    gradeEl.textContent = d.grade; gradeEl.style.color = sc(d.score);
    document.getElementById('biz-name').textContent = d.name;
    document.getElementById('biz-desc').textContent = d.desc;

    // Update report link dynamically based on active tab
    var link = document.getElementById('prev-link');
    link.href = d.link;
    link.textContent = 'See the full ' + d.name.split(' ')[0] + ' report \u2192';

    // Bars
    var wrap = document.getElementById('dims'); wrap.innerHTML = '';
    d.dims.forEach(function (dim, i) {
      var row = document.createElement('div'); row.className = 'dim';
      var lb = document.createElement('span'); lb.className = 'dim-label'; lb.textContent = dim.l;
      var tr = document.createElement('div'); tr.className = 'dim-track';
      var fl = document.createElement('div'); fl.className = 'dim-fill'; fl.style.background = sc(dim.s);
      if (anim) { fl.style.width = '0%'; fl.style.transitionDelay = (i * .15) + 's'; }
      tr.appendChild(fl);
      var val = document.createElement('span'); val.className = 'dim-val'; val.style.color = sc(dim.s);
      val.textContent = anim ? '0' : dim.s;
      row.appendChild(lb); row.appendChild(tr); row.appendChild(val); wrap.appendChild(row);
      if (anim) setTimeout(function () { fl.style.width = dim.s + '%'; countUp(val, dim.s, 1200); }, 50);
      else { fl.style.transition = 'none'; fl.style.width = dim.s + '%'; }
    });

    // Quick wins
    var qw = document.getElementById('qws'); qw.innerHTML = '';
    d.qw.forEach(function (q, i) {
      var c = document.createElement('div'); c.className = 'qw';
      if (anim) {
        c.style.opacity = '0'; c.style.transform = 'translateY(16px)';
        c.style.transition = 'opacity .5s,transform .5s'; c.style.transitionDelay = (.6 + i * .15) + 's';
      }
      c.innerHTML = '<div class="qw-n">0' + (i + 1) + '</div><h4>' + q.t + '</h4><p>' + q.d + '</p><span class="tag tag-' + q.i + '">' + (q.i === 'h' ? 'High Impact' : 'Medium Impact') + '</span>';
      qw.appendChild(c);
      if (anim) setTimeout(function () { c.style.opacity = '1'; c.style.transform = 'translateY(0)'; }, 50);
    });
  }

  function initPreview() {
    document.querySelectorAll('.tog').forEach(function (btn) {
      btn.addEventListener('click', function () {
        document.querySelectorAll('.tog').forEach(function (b) { b.classList.remove('active'); });
        btn.classList.add('active');
        active = btn.getAttribute('data-biz');
        render(active, true);
      });
    });
    var card = document.getElementById('prev-card'); if (!card) return;
    var done = false;
    var obs = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting && !done) { done = true; render(active, true); obs.unobserve(e.target); }
      });
    }, { threshold: .15 });
    obs.observe(card);
  }

  /* --- FAQ Accordion --- */
  function initFaq() {
    var items = document.querySelectorAll('.faq-item');
    items.forEach(function (item) {
      var btn = item.querySelector('.faq-q');
      if (!btn) return;
      btn.addEventListener('click', function () {
        var isOpen = item.classList.contains('open');
        // Close all other items
        items.forEach(function (other) { other.classList.remove('open'); other.querySelector('.faq-q').setAttribute('aria-expanded', 'false'); });
        // Toggle clicked item
        if (!isOpen) {
          item.classList.add('open');
          btn.setAttribute('aria-expanded', 'true');
        }
      });
    });
  }

  /* --- Form --- */
  /* --- Tier Toggle --- */
  function initTierToggle() {
    var card = document.getElementById('form-card');
    var btns = document.querySelectorAll('.tier-btn');
    var desc = document.getElementById('tier-desc');
    var tierInput = document.getElementById('tier-input');
    var submitBtn = document.getElementById('f-btn');
    var note = document.getElementById('f-note');
    if (!card || !btns.length) return;

    var descs = {
      free: 'Score + 3 quick wins delivered to your inbox.',
      paid: '6-dimension audit, SEO, competitors, and PDF report.'
    };
    var btnText = {
      free: 'Get My Free Grade \u2192',
      paid: 'Get My Full Audit \u2014 $199 \u2192'
    };
    var noteText = {
      free: 'No credit card required. No sales call. Just your score.',
      paid: 'Payment link will be sent to your email after submission.'
    };

    btns.forEach(function (btn) {
      btn.addEventListener('click', function () {
        var tier = btn.getAttribute('data-tier');
        btns.forEach(function (b) { b.classList.remove('active'); });
        btn.classList.add('active');
        card.setAttribute('data-tier', tier);
        if (tierInput) tierInput.value = tier;
        if (desc) desc.textContent = descs[tier];
        if (submitBtn) submitBtn.textContent = btnText[tier];
        if (note) note.textContent = noteText[tier];
        // Make paid-only fields required when paid tier selected
        var paidFields = card.querySelectorAll('.paid-only input');
        paidFields.forEach(function (f) {
          if (tier === 'paid') f.setAttribute('required', '');
          else f.removeAttribute('required');
        });
      });
    });
  }

  function initForm() {
    var form = document.getElementById('audit-form'); if (!form) return;
    // Pre-fill URL from hero input
    try {
      var saved = sessionStorage.getItem('cg_url');
      if (saved) {
        var urlInput = form.querySelector('[name="website_url"]');
        if (urlInput && !urlInput.value) urlInput.value = saved;
      }
    } catch (ex) { /* private browsing */ }
    var card = document.getElementById('form-card');
    var currentTier = function () { return card ? card.getAttribute('data-tier') : 'free'; };
    var spec = {
      website_url: { r: true, t: 'url', l: 'Website URL' },
      email: { r: true, t: 'email', l: 'Email' },
      business_name: { r: false, l: 'Business name', paid: true },
      industry: { r: false, l: 'Industry', paid: true },
      contact_name: { r: false, l: 'Your name', paid: true }
    };
    function err(n, m) {
      var inp = form.querySelector('[name="' + n + '"]');
      var e = inp ? inp.parentElement.querySelector('.f-err') : null;
      if (inp) inp.classList.add('err');
      if (e) { e.textContent = m; e.classList.add('show'); }
    }
    function clr() {
      form.querySelectorAll('.err').forEach(function (e) { e.classList.remove('err'); });
      form.querySelectorAll('.f-err').forEach(function (e) { e.classList.remove('show'); e.textContent = ''; });
    }
    function vf(n, v) {
      var s = spec[n]; if (!s) return null; var val = v.trim();
      var isPaid = currentTier() === 'paid';
      var isRequired = s.r || (s.paid && isPaid);
      if (isRequired && !val) return s.l + ' is required';
      if (s.t === 'email' && val && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(val)) return 'Enter a valid email';
      if (s.t === 'url' && val) { try { new URL(val.match(/^https?:\/\//) ? val : 'https://' + val); } catch (e) { return 'Enter a valid URL'; } }
      return null;
    }
    function validate() {
      var first = null;
      Object.keys(spec).forEach(function (n) {
        var inp = form.querySelector('[name="' + n + '"]'); if (!inp) return;
        var e = vf(n, inp.value); if (e) { err(n, e); if (!first) first = inp; }
      });
      return first;
    }
    form.addEventListener('input', function (e) {
      if (e.target.classList.contains('err')) {
        e.target.classList.remove('err');
        var er = e.target.parentElement.querySelector('.f-err'); if (er) er.classList.remove('show');
      }
    });
    form.addEventListener('submit', function (e) {
      e.preventDefault(); clr();
      var hp = form.querySelector('[name="company_url"]');
      if (hp && hp.value) { form.style.display = 'none'; document.querySelector('.f-ok').classList.add('show'); return; }
      var first = validate(); if (first) { first.focus(); return; }
      var btn = form.querySelector('.f-btn'); var orig = btn.textContent;
      btn.disabled = true; btn.textContent = 'Submitting...';
      var data = {}; new FormData(form).forEach(function (v, k) { data[k] = v; }); delete data.company_url;
      if (data.website_url && !data.website_url.match(/^https?:\/\//)) data.website_url = 'https://' + data.website_url;
      fetch('/api/submit', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) })
        .then(function (r) { return r.json().then(function (j) { return { ok: r.ok, data: j }; }); })
        .then(function (res) {
          if (res.ok && res.data.success) {
            form.style.display = 'none';
            var note = document.querySelector('.f-note'); if (note) note.style.display = 'none';
            document.querySelector('.f-ok').classList.add('show');
          } else { err('email', res.data.error || 'Something went wrong.'); }
        })
        .catch(function () { err('email', 'Connection error. Please try again.'); })
        .finally(function () { btn.disabled = false; btn.textContent = orig; });
    });
  }

  /* --- Sticky CTA --- */
  function initSticky() {
    var el = document.getElementById('sticky');
    var hero = document.querySelector('.hero');
    var form = document.getElementById('form-section');
    if (!el || !hero || !form) return;
    var show = false;
    var t = false;
    window.addEventListener('scroll', function () {
      if (!t) {
        requestAnimationFrame(function () {
          var hb = hero.getBoundingClientRect().bottom;
          var ft = form.getBoundingClientRect().top;
          var s = hb < 0 && ft > innerHeight;
          if (s !== show) { show = s; el.classList.toggle('vis', s); }
          t = false;
        }); t = true;
      }
    });
  }

  /* --- Hero URL Form --- */
  function initHeroUrl() {
    var form = document.getElementById('hero-url-form');
    if (!form) return;
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var url = document.getElementById('hero-url').value.trim();
      if (!url) return;
      // Store URL for pre-fill
      try { sessionStorage.setItem('cg_url', url); } catch (ex) { /* private browsing */ }
      // Pre-fill the main form
      var mainUrl = document.getElementById('website_url');
      if (mainUrl) mainUrl.value = url;
      // Scroll to form
      var formSection = document.getElementById('form-section');
      if (formSection) formSection.scrollIntoView({ behavior: 'smooth' });
    });
  }

  /* --- Steps progression animation --- */
  function initSteps() {
    var stepsWrap = document.querySelector('.steps');
    var stepEls = document.querySelectorAll('.step');
    if (!stepsWrap || !stepEls.length) return;

    var triggered = false;
    var obs = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting && !triggered) {
          triggered = true;
          obs.unobserve(e.target);
          // Animate the connecting line
          stepsWrap.classList.add('line-animate');
          // Light up each step sequentially
          stepEls.forEach(function (step, i) {
            setTimeout(function () {
              step.classList.add('step-active');
            }, 400 + i * 600);
          });
        }
      });
    }, { threshold: 0.3 });
    obs.observe(stepsWrap);
  }

  /* --- Init --- */
  document.addEventListener('DOMContentLoaded', function () {
    initAnim();
    initNav();
    initHeroUrl();
    initSteps();
    initPreview();
    initFaq();
    initTierToggle();
    initForm();
    initSticky();
  });
})();
