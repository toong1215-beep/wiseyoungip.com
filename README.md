# 와이즈영 특허사무소 홈페이지

순수 HTML/CSS로 만든 정적 사이트입니다. Python 3만 있으면 빌드할 수 있고, 무료 호스팅에 그대로 올라갑니다.

## 폴더 구성

| 경로 | 내용 |
| --- | --- |
| `src/pages/` | 페이지 본문 (메인, 변리사 소개, 업무분야 6개, 비용, 칼럼 목록, 개인정보처리방침, 영문) |
| `src/column/` | 칼럼 글. 파일 하나가 글 하나 |
| `src/assets/` | 스타일(`css`), 스크립트(`js`), 이미지(`img`) |
| `build.py` | 공통 머리말·꼬리말을 씌워 `dist/` 에 완성본을 만드는 스크립트 |
| `dist/` | 완성된 사이트. 이 폴더를 호스팅에 올립니다 (빌드할 때마다 새로 만들어짐) |

## 빌드와 미리보기

```bash
python build.py
python -m http.server 4321 --directory dist
```

브라우저에서 http://localhost:4321 을 엽니다.

## 칼럼 올리기

`src/column/` 에 새 파일(영문 소문자 파일명, 예: `line.html`)을 만들고 첫 줄에 정보를 적습니다.

```html
<!--meta {"title": "제목", "date": "2026-11-20", "time": "10:00", "category": "칼럼 시리즈", "summary": "목록에 보일 한두 문장"} -->
<p>본문...</p>
```

빌드하면 칼럼 목록, 메인의 최신 칼럼 3개, 사이트맵에 자동으로 들어갑니다. 블로그에는 요약과 홈페이지 링크를 올립니다.

## 오픈 전에 할 일

1. **상담 폼 키 발급**: https://web3forms.com 에서 admin@wiseyoungip.com 으로 무료 키를 받아, `src/pages/index.html` 과 `src/pages/en/index.html` 의 `YOUR_WEB3FORMS_ACCESS_KEY` 를 바꿉니다. 키가 없는 동안에는 폼이 메일 앱을 여는 방식으로 동작합니다.
2. **호스팅 (완료)**: GitHub Pages. 저장소 https://github.com/toong1215-beep/wiseyoungip.com 의 main 에 올리면 `.github/workflows/pages.yml` 이 `python build.py` 를 돌려 자동 배포합니다.
3. **도메인 (완료)**: Squarespace DNS에 A 기록 4개(185.199.108~111.153)와 www CNAME(toong1215-beep.github.io)을 넣었습니다. 메일 기록(MX, SPF, DKIM)은 건드리지 않았습니다.
4. **검색 등록**: 네이버 서치어드바이저, 구글 서치콘솔에 사이트와 `sitemap.xml` 을 등록합니다.

## 나중에 바꿀 것

- 로고: 받은 PNG로 투명 배경(`logo.png`)과 흰색(`logo-white.png`) 버전을 만들어 씁니다. 새 로고 파일이 오면 `python tools/make_logo.py <파일>` 로 다시 만듭니다. 원본 벡터(SVG/AI) 파일이 있으면 더 선명해집니다.
- 프로필 사진: `src/assets/img/profile.jpg` 를 같은 이름으로 바꾸면 모든 페이지에 반영됩니다.
- 카카오톡 채널·인스타그램: 주소가 정해지면 `build.py` 의 꼬리말과 빠른 연락 버튼에 추가합니다.
