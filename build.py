"""와이즈영 특허사무소 홈페이지 빌드 스크립트.

src/ 아래의 페이지 조각(HTML)에 공통 머리말·꼬리말을 씌워 dist/ 에 완성된 사이트를 만든다.
표준 라이브러리만 쓰므로 Python 3.10 이상만 있으면 된다.

    python build.py

페이지 조각 첫 줄에는 메타 정보를 JSON으로 적는다.
    <!--meta {"title": "...", "description": "...", "lang": "ko"} -->
칼럼(src/column/*.html)은 date, category, summary 도 적는다.
"""

import html
import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).parent
SRC = ROOT / "src"
DIST = ROOT / "dist"
SITE_URL = "https://wiseyoungip.com"

OFFICE = {
    "phone": "010-9284-2623",
    "phone_href": "tel:01092842623",
    "email": "admin@wiseyoungip.com",
    "address_ko": "서울 서초구 명달로 107, 5층 IP 비즈니스 센터 504호",
    "address_en": "Suite 504, IP Business Center 5F, 107 Myeongdal-ro, Seocho-gu, Seoul, Korea",
}

META_RE = re.compile(r"^\s*<!--meta\s+(\{.*?\})\s*-->\s*", re.S)


def read_page(path: Path):
    text = path.read_text(encoding="utf-8")
    m = META_RE.match(text)
    if not m:
        raise SystemExit(f"메타 정보가 없습니다: {path}")
    return json.loads(m.group(1)), text[m.end():]


# ---------------------------------------------------------------- 공통 조각

LOGO = """<a class="logo" href="{home}" aria-label="{label}">
  <img src="/assets/img/{img}" width="877" height="198" alt="WISE YOUNG 와이즈영 특허사무소">
</a>"""

NAV = {
    "ko": [
        ("변리사 소개", "/attorney.html"),
        ("업무분야", "/#practice"),
        ("업무 방식", "/#process"),
        ("비용 안내", "/fees.html"),
        ("칼럼", "/column/"),
    ],
    "en": [
        ("About", "/en/#about"),
        ("Attorney", "/en/#attorney"),
        ("Practice", "/en/#practice"),
        ("Approach", "/en/#process"),
    ],
}


def header(lang: str, alt_href: str) -> str:
    home = "/" if lang == "ko" else "/en/"
    links = "\n".join(f'<li><a href="{href}">{label}</a></li>' for label, href in NAV[lang])
    cta_label, cta_href = ("상담 신청", "/#contact") if lang == "ko" else ("Contact", "/en/#contact")
    alt_label = "EN" if lang == "ko" else "KO"
    alt_name = "English" if lang == "ko" else "한국어"
    menu = "메뉴" if lang == "ko" else "Menu"
    return f"""<header class="site-header">
  <div class="wrap header-inner">
    {LOGO.format(img="logo.png", home=home, label="와이즈영 특허사무소 홈" if lang == "ko" else "WISEYOUNG IP home")}
    <button class="nav-toggle" aria-expanded="false" aria-controls="site-nav">{menu}</button>
    <nav id="site-nav" class="site-nav" aria-label="{'주 메뉴' if lang == 'ko' else 'Main'}">
      <ul>
        {links}
        <li><a class="lang" href="{alt_href}" lang="{'en' if lang == 'ko' else 'ko'}" aria-label="{alt_name}">{alt_label}</a></li>
        <li><a class="btn btn-small" href="{cta_href}">{cta_label}</a></li>
      </ul>
    </nav>
  </div>
</header>"""


def footer(lang: str) -> str:
    if lang == "ko":
        return f"""<footer class="site-footer">
  <div class="wrap footer-inner">
    <div>
      {LOGO.format(img="logo-white.png", home="/", label="와이즈영 특허사무소 홈")}
      <p class="footer-note">상담부터 등록까지, 조현영 변리사가 직접 맡습니다.</p>
    </div>
    <dl class="footer-info">
      <div><dt>대표 변리사</dt><dd>조현영</dd></div>
      <div><dt>주소</dt><dd>{OFFICE['address_ko']}</dd></div>
      <div><dt>전화</dt><dd><a href="{OFFICE['phone_href']}">{OFFICE['phone']}</a></dd></div>
      <div><dt>이메일</dt><dd><a href="mailto:{OFFICE['email']}">{OFFICE['email']}</a></dd></div>
    </dl>
  </div>
  <div class="wrap footer-bottom">
    <a href="/privacy.html">개인정보처리방침</a>
    <a href="https://blog.naver.com/wiseyoungip" rel="noopener">네이버 블로그</a>
    <span>© 2026 와이즈영 특허사무소</span>
  </div>
</footer>
<div class="quick-contact" aria-label="빠른 연락">
  <a href="{OFFICE['phone_href']}">전화 상담</a>
  <a href="/#contact">사전검토 신청</a>
</div>"""
    return f"""<footer class="site-footer">
  <div class="wrap footer-inner">
    <div>
      {LOGO.format(img="logo-white.png", home="/en/", label="WISEYOUNG IP home")}
      <p class="footer-note">From first consultation to registration, handled by the attorney herself.</p>
    </div>
    <dl class="footer-info">
      <div><dt>Attorney</dt><dd>Hyunyoung Cho</dd></div>
      <div><dt>Address</dt><dd>{OFFICE['address_en']}</dd></div>
      <div><dt>Phone</dt><dd><a href="tel:+821092842623">+82 10-9284-2623</a></dd></div>
      <div><dt>Email</dt><dd><a href="mailto:{OFFICE['email']}">{OFFICE['email']}</a></dd></div>
    </dl>
  </div>
  <div class="wrap footer-bottom">
    <a href="/privacy.html" lang="ko">개인정보처리방침</a>
    <span>© 2026 WISEYOUNG IP</span>
  </div>
</footer>
<div class="quick-contact" aria-label="Quick contact">
  <a href="tel:+821092842623">Call</a>
  <a href="/en/#contact">Send an inquiry</a>
</div>"""


def layout(meta: dict, body: str, url_path: str) -> str:
    lang = meta.get("lang", "ko")
    title = meta["title"]
    full_title = title if meta.get("bare_title") else (
        f"{title} | 와이즈영 특허사무소" if lang == "ko" else f"{title} | WISEYOUNG IP")
    desc = html.escape(meta.get("description", ""), quote=True)
    alt_href = meta.get("alt", "/en/" if lang == "ko" else "/")
    return f"""<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(full_title)}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{SITE_URL}{url_path}">
<meta property="og:type" content="website">
<meta property="og:title" content="{html.escape(full_title, quote=True)}">
<meta property="og:description" content="{desc}">
<meta property="og:image" content="{SITE_URL}/assets/img/profile.jpg">
<meta property="og:url" content="{SITE_URL}{url_path}">
<meta name="theme-color" content="#150578">
<link rel="icon" href="/assets/img/favicon.svg" type="image/svg+xml">
<link rel="preload" href="/assets/fonts/Pretendard-Regular.subset.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/assets/fonts/Pretendard-Bold.subset.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/assets/css/site.css">
{meta.get('head', '')}
</head>
<body class="{meta.get('body_class', '')}">
<a class="skip" href="#main">{'본문으로 건너뛰기' if lang == 'ko' else 'Skip to content'}</a>
{header(lang, alt_href)}
<main id="main">
{body}
</main>
{footer(lang)}
<script src="/assets/js/site.js" defer></script>
</body>
</html>
"""


# ---------------------------------------------------------------- 칼럼

def fmt_date(d: str) -> str:
    y, m, day = d.split("-")
    return f"{y}. {int(m)}. {int(day)}."


def column_card(meta: dict, href: str) -> str:
    return f"""<li class="column-item">
  <a href="{href}">
    <span class="column-meta"><span class="column-cat">{meta['category']}</span><time datetime="{meta['date']}">{fmt_date(meta['date'])}</time></span>
    <span class="column-title">{meta['title']}</span>
    <span class="column-summary">{meta['summary']}</span>
  </a>
</li>"""


def build_columns():
    items = []
    for path in sorted((SRC / "column").glob("*.html")):
        meta, body = read_page(path)
        meta.setdefault("lang", "ko")
        url = f"/column/{path.stem}.html"
        article = f"""<article class="article wrap-narrow">
  <header class="article-head">
    <p class="article-meta"><a href="/column/">칼럼</a><span>{meta['category']}</span><time datetime="{meta['date']}">{fmt_date(meta['date'])}</time></p>
    <h1>{meta['title']}</h1>
    <p class="article-byline">조현영 대표 변리사</p>
  </header>
  <div class="prose">
{body}
  </div>
  <aside class="article-cta">
    <p>지금 우리 기업에 필요한 특허 전략이 궁금하시다면, 조현영 변리사와 이야기 나눠 보세요.</p>
    <a class="btn" href="/#contact">무료 사전검토 신청</a>
  </aside>
</article>"""
        out = DIST / "column" / f"{path.stem}.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(layout({**meta, "description": meta["summary"]}, article, url), encoding="utf-8")
        items.append((meta, url))
    items.sort(key=lambda it: (it[0]["date"], it[0].get("time", "")), reverse=True)
    return items


# ---------------------------------------------------------------- 실행

def main():
    if DIST.exists():
        shutil.rmtree(DIST)
    shutil.copytree(SRC / "assets", DIST / "assets")
    for name in ("robots.txt", "_headers", "CNAME"):
        if (SRC / name).exists():
            shutil.copy(SRC / name, DIST / name)

    columns = build_columns()
    latest = "\n".join(column_card(m, u) for m, u in columns[:3])
    all_cols = "\n".join(column_card(m, u) for m, u in columns)

    urls = [u for _, u in columns]
    for path in sorted((SRC / "pages").rglob("*.html")):
        meta, body = read_page(path)
        body = body.replace("{{latest_columns}}", latest).replace("{{all_columns}}", all_cols)
        for key, value in OFFICE.items():
            body = body.replace("{{" + key + "}}", value)
        rel = path.relative_to(SRC / "pages").as_posix()
        url = "/" + (rel[:-len("index.html")] if rel.endswith("index.html") else rel)
        out = DIST / rel
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(layout(meta, body, url), encoding="utf-8")
        urls.append(url)

    sitemap = "\n".join(f"  <url><loc>{SITE_URL}{u}</loc></url>" for u in sorted(urls))
    (DIST / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{sitemap}\n</urlset>\n", encoding="utf-8")
    print(f"완료: 페이지 {len(urls)}개 -> {DIST}")


if __name__ == "__main__":
    main()
