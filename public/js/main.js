/* ============================================================
   ClearGrade — Landing Page Scripts
   Form handling, scroll animations, counter, hero input
   ============================================================ */

(function () {
  'use strict';

  /* --- Scroll Reveal (Intersection Observer) --- */
  function initReveal() {
    var reveals = document.querySelectorAll('.reveal');
    if (!reveals.length) return;

    var observer = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            entry.target.classList.add('visible');
            observer.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.1, rootMargin: '0px 0px -60px 0px' }
    );

    reveals.forEach(function (el) { observer.observe(el); });
  }

  /* --- Animated Number Counters --- */
  function initCounters() {
    var counters = document.querySelectorAll('.stat-number[data-target]');
    if (!counters.length) return;

    var animated = new Set();

    var observer = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (!entry.isIntersecting) return;
          var el = entry.target;
          if (animated.has(el)) return;
          animated.add(el);

          var target = parseInt(el.getAttribute('data-target'), 10);
          var suffix = el.getAttribute('data-suffix') || '';
          var duration = 1200;
          var start = performance.now();

          function tick(now) {
            var elapsed = now - start;
            var progress = Math.min(elapsed / duration, 1);
            // Ease-out quad
            var eased = 1 - (1 - progress) * (1 - progress);
            var current = Math.round(eased * target);
            el.textContent = current + suffix;

            if (progress < 1) {
              requestAnimationFrame(tick);
            }
          }

          requestAnimationFrame(tick);
        });
      },
      { threshold: 0.5 }
    );

    counters.forEach(function (el) { observer.observe(el); });
  }

  /* --- Navbar scroll state --- */
  function initNav() {
    var nav = document.querySelector('.nav');
    if (!nav) return;

    var ticking = false;
    window.addEventListener('scroll', function () {
      if (!ticking) {
        window.requestAnimationFrame(function () {
          nav.classList.toggle('scrolled', window.scrollY > 40);
          ticking = false;
        });
        ticking = true;
      }
    });
  }

  /* --- Hero URL input -> pre-fill form + scroll --- */
  function initHeroForm() {
    var heroForm = document.getElementById('hero-url-form');
    if (!heroForm) return;

    heroForm.addEventListener('submit', function (e) {
      e.preventDefault();
      var heroInput = document.getElementById('hero-url');
      var urlValue = (heroInput ? heroInput.value : '').trim();

      // Pre-fill the main form's website URL field
      var mainUrlField = document.getElementById('website_url');
      if (mainUrlField && urlValue) {
        mainUrlField.value = urlValue;
        // Trigger visual feedback
        mainUrlField.classList.add('prefilled');
        setTimeout(function () { mainUrlField.classList.remove('prefilled'); }, 1500);
      }

      // Scroll to the main form
      var formSection = document.getElementById('audit-form-section');
      if (formSection) {
        formSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
        // Focus the first empty required field
        setTimeout(function () {
          var firstEmpty = document.querySelector('#audit-form input[required]');
          var fields = document.querySelectorAll('#audit-form input[required]');
          for (var i = 0; i < fields.length; i++) {
            if (!fields[i].value.trim()) {
              fields[i].focus();
              break;
            }
          }
        }, 800);
      }
    });
  }

  /* --- Form Validation & Submission --- */
  function initForm() {
    var form = document.getElementById('audit-form');
    if (!form) return;

    var fields = {
      business_name: { required: true, label: 'Business name' },
      website_url: { required: true, type: 'url', label: 'Website URL' },
      industry: { required: true, label: 'Industry' },
      contact_name: { required: true, label: 'Your name' },
      email: { required: true, type: 'email', label: 'Email' },
    };

    function showError(name, message) {
      var input = form.querySelector('[name="' + name + '"]');
      var errorEl = input
        ? input.parentElement.querySelector('.form-error')
        : null;
      if (input) input.classList.add('error');
      if (errorEl) {
        errorEl.textContent = message;
        errorEl.classList.add('show');
      }
    }

    function clearErrors() {
      form.querySelectorAll('.error').forEach(function (el) { el.classList.remove('error'); });
      form.querySelectorAll('.form-error').forEach(function (el) {
        el.classList.remove('show');
        el.textContent = '';
      });
    }

    function validateField(name, value) {
      var spec = fields[name];
      if (!spec) return null;

      var trimmed = value.trim();
      if (spec.required && !trimmed) {
        return spec.label + ' is required';
      }
      if (spec.type === 'email' && trimmed) {
        var emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailPattern.test(trimmed)) return 'Enter a valid email address';
      }
      if (spec.type === 'url' && trimmed) {
        try {
          var urlStr = trimmed.match(/^https?:\/\//) ? trimmed : 'https://' + trimmed;
          new URL(urlStr);
        } catch (e) {
          return 'Enter a valid website URL';
        }
      }
      return null;
    }

    function validate() {
      var firstError = null;
      var names = Object.keys(fields);
      for (var i = 0; i < names.length; i++) {
        var name = names[i];
        var input = form.querySelector('[name="' + name + '"]');
        if (!input) continue;
        var error = validateField(name, input.value);
        if (error) {
          showError(name, error);
          if (!firstError) firstError = input;
        }
      }
      return firstError;
    }

    // Clear field error on input
    form.addEventListener('input', function (e) {
      var input = e.target;
      if (input.classList.contains('error')) {
        input.classList.remove('error');
        var errorEl = input.parentElement.querySelector('.form-error');
        if (errorEl) errorEl.classList.remove('show');
      }
    });

    form.addEventListener('submit', function (e) {
      e.preventDefault();
      clearErrors();

      // Honeypot check
      var honeypot = form.querySelector('[name="company_fax"]');
      if (honeypot && honeypot.value) return;

      var firstError = validate();
      if (firstError) {
        firstError.focus();
        return;
      }

      var submitBtn = form.querySelector('.form-submit');
      var originalText = submitBtn.textContent;
      submitBtn.disabled = true;
      submitBtn.textContent = 'Submitting...';

      var formData = new FormData(form);
      var data = {};
      formData.forEach(function (value, key) { data[key] = value; });
      // Remove honeypot from payload
      delete data.company_fax;

      // Normalize URL
      if (data.website_url && !data.website_url.match(/^https?:\/\//)) {
        data.website_url = 'https://' + data.website_url;
      }

      fetch('/api/submit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      })
        .then(function (response) {
          return response.json().then(function (result) {
            if (response.ok && result.success) {
              form.style.display = 'none';
              var successEl = document.querySelector('.form-success');
              if (successEl) successEl.classList.add('show');
            } else {
              var message = result.error || 'Something went wrong. Please try again.';
              showError('email', message);
            }
          });
        })
        .catch(function () {
          showError('email', 'Connection error. Please check your internet and try again.');
        })
        .finally(function () {
          submitBtn.disabled = false;
          submitBtn.textContent = originalText;
        });
    });
  }

  /* --- Parallax-lite on hero orbs --- */
  function initParallax() {
    var orbs = document.querySelectorAll('.hero-orb');
    if (!orbs.length) return;

    var ticking = false;
    window.addEventListener('scroll', function () {
      if (!ticking) {
        window.requestAnimationFrame(function () {
          var scrollY = window.scrollY;
          orbs.forEach(function (orb, i) {
            var speed = (i + 1) * 0.08;
            orb.style.transform = 'translateY(' + (scrollY * speed) + 'px)';
          });
          ticking = false;
        });
        ticking = true;
      }
    });
  }

  /* --- Initialize on DOM ready --- */
  document.addEventListener('DOMContentLoaded', function () {
    initReveal();
    initCounters();
    initNav();
    initHeroForm();
    initForm();
    initParallax();
  });
})();
