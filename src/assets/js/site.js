(function () {
  var root = document.documentElement;
  root.classList.add('js');

  // ---------------------------------------------------------------- GA4 이벤트
  // gtag 는 build.py 가 머리말에 넣는다. 측정 ID가 없거나 실제 도메인이 아니면 아무것도 보내지 않는다.
  var pageType = document.body.getAttribute('data-page-type') || 'other';
  function track(name, params) {
    if (typeof window.gtag !== 'function') return;
    var all = {}, base = window.WY_GA_PARAMS || {}, k;
    for (k in base) all[k] = base[k];
    for (k in params || {}) all[k] = params[k];
    window.gtag('event', name, all);
  }
  function clip(s) { return (s || '').replace(/\s+/g, ' ').trim().slice(0, 100); }
  // 클릭이 일어난 화면 위치: header / footer / quick_contact / 섹션 id / hero / body
  function where(el) {
    if (el.closest('.site-header')) return 'header';
    if (el.closest('.site-footer')) return 'footer';
    if (el.closest('.quick-contact')) return 'quick_contact';
    if (el.closest('.article-cta')) return 'article_cta';
    if (el.closest('.hero')) return 'hero';
    var sec = el.closest('section[id]');
    if (sec) return sec.id;
    if (el.closest('.page-head')) return 'page_head';
    return 'body';
  }
  var PRACTICE = { patent: '특허·실용신안', startup: '스타트업 IP 지원', trademark: '상표', design: '디자인', overseas: '해외출원', dispute: '심판·분쟁' };

  document.addEventListener('click', function (e) {
    var a = e.target.closest && e.target.closest('a[href]');
    if (!a) return;
    var href = a.getAttribute('href');
    var head = a.querySelector('h3, .column-title');
    var text = clip((head || a).textContent);
    var loc = where(a);
    var base = { link_text: text, link_location: loc };

    if (href.indexOf('tel:') === 0) { track('click_phone', base); return; }
    if (href.indexOf('mailto:') === 0) { track('click_email', base); return; }
    if (a.classList.contains('lang')) { track('language_switch', { to_language: a.getAttribute('lang') || '', link_location: loc }); return; }

    var url;
    try { url = new URL(a.href, location.href); } catch (err) { return; }
    if (url.hostname !== location.hostname) return; // 외부 링크는 GA4 향상된 측정(outbound click)이 잡는다

    if (url.hash === '#contact') {
      track('cta_click', { cta_type: 'inquiry', link_text: text, link_location: loc, inquiry_field: url.searchParams.get('field') || '' });
      return;
    }
    var m = url.pathname.match(/^\/practice\/([a-z]+)\.html$/);
    if (m) { track('practice_click', { practice_area: PRACTICE[m[1]] || m[1], link_text: text, link_location: loc }); return; }
    if (/^\/column\/[^/]+\.html$/.test(url.pathname)) {
      var titleEl = a.querySelector('.column-title');
      track('column_click', { column_title: clip(titleEl ? titleEl.textContent : text), link_location: loc });
      return;
    }
    if (a.classList.contains('btn')) { track('cta_click', { cta_type: 'navigate', link_text: text, link_location: loc, link_url: url.pathname + url.hash }); return; }
    if (loc === 'header' || loc === 'footer') track('nav_click', { link_text: text, link_location: loc, link_url: url.pathname + url.hash });
  });

  // 메인·영문 메인: 각 구역이 화면 위쪽 절반에 들어오면 한 번씩 기록 (어디까지 내려 읽는지)
  if ('IntersectionObserver' in window && (pageType === 'home' || pageType === 'home_en')) {
    var seen = {};
    var secIo = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        var id = en.target.id;
        if (en.isIntersecting && !seen[id]) {
          seen[id] = true;
          track('section_view', { section_id: id });
          secIo.unobserve(en.target);
        }
      });
    }, { rootMargin: '0px 0px -50% 0px' });
    document.querySelectorAll('main section[id]').forEach(function (s) { secIo.observe(s); });
  }

  // 칼럼 본문: 25·50·75·100% 읽음과 머문 시간
  if (pageType === 'column_article') {
    var prose = document.querySelector('.prose');
    var marks = [25, 50, 75, 100], hit = {}, t0 = Date.now();
    var onScroll = function () {
      if (!prose) return;
      var r = prose.getBoundingClientRect();
      var total = r.height - window.innerHeight * 0.3;
      var pct = total <= 0 ? 100 : Math.min(100, Math.max(0, (window.innerHeight * 0.7 - r.top) / total * 100));
      marks.forEach(function (mk) {
        if (pct >= mk && !hit[mk]) {
          hit[mk] = true;
          track('column_read', { percent_read: mk, engaged_seconds: Math.round((Date.now() - t0) / 1000) });
        }
      });
      if (hit[100]) window.removeEventListener('scroll', onScroll);
    };
    window.addEventListener('scroll', onScroll, { passive: true });
  }

  // 모바일 메뉴 열기
  var navToggle = document.querySelector('.nav-toggle');
  if (navToggle) navToggle.addEventListener('click', function () {
    if (navToggle.getAttribute('aria-expanded') !== 'true') track('mobile_menu_open', {});
  });

  // 모바일 메뉴
  var toggle = document.querySelector('.nav-toggle');
  var nav = document.getElementById('site-nav');
  if (toggle && nav) {
    toggle.addEventListener('click', function () {
      var open = nav.classList.toggle('open');
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
    nav.addEventListener('click', function (e) {
      if (e.target.tagName === 'A') {
        nav.classList.remove('open');
        toggle.setAttribute('aria-expanded', 'false');
      }
    });
  }

  // 점 → 선 → 면 → 입체: 화면에 들어오면 한 번 그린다
  var stages = document.querySelector('.stages');
  if (stages) {
    stages.querySelectorAll('.draw').forEach(function (el) {
      if (el.getTotalLength) el.style.setProperty('--len', Math.ceil(el.getTotalLength()));
    });
    if ('IntersectionObserver' in window) {
      var io = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            stages.classList.add('drawn');
            io.disconnect();
          }
        });
      }, { threshold: 0.35 });
      io.observe(stages);
    } else {
      stages.classList.add('drawn');
    }
  }

  // 상담 폼: Web3Forms로 보내고, 키가 아직 없으면 메일 앱으로 연결
  document.querySelectorAll('form[data-inquiry]').forEach(function (form) {
    var status = form.querySelector('.form-status');
    var en = form.getAttribute('data-lang') === 'en';
    var msg = en
      ? { sending: 'Sending…', ok: 'Thank you. We will reply within one business day.', err: 'Sending failed. Please email admin@wiseyoungip.com directly.', invalid: 'Please fill in the required fields.' }
      : { sending: '보내는 중입니다…', ok: '접수되었습니다. 영업일 기준 1일 안에 연락드리겠습니다.', err: '전송하지 못했습니다. admin@wiseyoungip.com 으로 메일을 보내 주세요.', invalid: '필수 항목을 입력해 주세요.' };

    // 업무 카드의 "사전검토" 링크로 들어오면 상담 분야를 미리 고른다
    var params = new URLSearchParams(location.search);
    var field = params.get('field');
    var select = form.querySelector('select[name="field"]');
    if (field && select) {
      Array.prototype.forEach.call(select.options, function (o) { if (o.value === field) select.value = field; });
    }

    var formLang = en ? 'en' : 'ko';
    var started = false;
    var startForm = function () {
      if (started) return;
      started = true;
      track('form_start', { form_language: formLang, prefilled_field: field || '' });
    };
    form.addEventListener('focusin', startForm);
    form.addEventListener('input', startForm);
    if (select) select.addEventListener('change', function () {
      if (select.value) track('inquiry_field_select', { inquiry_field: select.value, form_language: formLang });
    });

    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var fieldVal = select ? select.value : '';
      if (!form.checkValidity()) {
        var missing = [];
        Array.prototype.forEach.call(form.elements, function (el) { if (el.name && el.willValidate && !el.checkValidity()) missing.push(el.name); });
        track('form_error', { error_type: 'validation', missing_fields: missing.join(',').slice(0, 100), form_language: formLang });
        status.textContent = msg.invalid;
        status.className = 'form-status err';
        form.reportValidity();
        return;
      }
      var data = new FormData(form);
      var key = data.get('access_key');
      if (!key || key.indexOf('YOUR_') === 0) {
        var body = [];
        data.forEach(function (v, k) { if (k !== 'access_key' && k !== 'botcheck' && k !== 'subject' && v) body.push(k + ': ' + v); });
        track('generate_lead', { lead_method: 'mailto', inquiry_field: fieldVal, form_language: formLang, has_company: data.get('company') ? 'yes' : 'no' });
        location.href = 'mailto:admin@wiseyoungip.com?subject=' + encodeURIComponent(data.get('subject') || '상담 문의') + '&body=' + encodeURIComponent(body.join('\n'));
        return;
      }
      status.textContent = msg.sending;
      status.className = 'form-status';
      fetch(form.action, { method: 'POST', body: data, headers: { Accept: 'application/json' } })
        .then(function (r) { return r.json(); })
        .then(function (res) {
          if (res.success) {
            track('generate_lead', { lead_method: 'form', inquiry_field: fieldVal, form_language: formLang, has_company: data.get('company') ? 'yes' : 'no' });
            form.reset();
            status.textContent = msg.ok;
            status.className = 'form-status ok';
          } else { throw new Error(); }
        })
        .catch(function () {
          track('form_error', { error_type: 'send_failed', form_language: formLang });
          status.textContent = msg.err;
          status.className = 'form-status err';
        });
    });
  });
})();
