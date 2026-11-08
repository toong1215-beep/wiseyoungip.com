(function () {
  var root = document.documentElement;
  root.classList.add('js');

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

    form.addEventListener('submit', function (e) {
      e.preventDefault();
      if (!form.checkValidity()) {
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
        location.href = 'mailto:admin@wiseyoungip.com?subject=' + encodeURIComponent(data.get('subject') || '상담 문의') + '&body=' + encodeURIComponent(body.join('\n'));
        return;
      }
      status.textContent = msg.sending;
      status.className = 'form-status';
      fetch(form.action, { method: 'POST', body: data, headers: { Accept: 'application/json' } })
        .then(function (r) { return r.json(); })
        .then(function (res) {
          if (res.success) {
            form.reset();
            status.textContent = msg.ok;
            status.className = 'form-status ok';
          } else { throw new Error(); }
        })
        .catch(function () {
          status.textContent = msg.err;
          status.className = 'form-status err';
        });
    });
  });
})();
