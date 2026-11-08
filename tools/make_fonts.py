"""Pretendard TTF를 웹용 woff2로 줄인다.

남기는 글자: 영문·숫자·기본 기호, 한글 상용 2,350자(KS X 1001), 사이트 원고에 실제로 쓰인 모든 글자.
새 칼럼에 드문 글자가 들어가면 이 스크립트를 다시 돌린다.

    python tools/make_fonts.py "<Pretendard TTF 폴더>"

필요: pip install fonttools brotli
"""

import sys
from pathlib import Path

from fontTools import subset

SITE = Path(__file__).resolve().parent.parent
OUT = SITE / "src" / "assets" / "fonts"
WEIGHTS = {"Regular": 400, "Medium": 500, "SemiBold": 600, "Bold": 700}


def charset() -> str:
    chars = set(chr(c) for c in range(0x20, 0x7F))
    chars |= set("·–—‘’“”…→←↑↓①②③④⑤⑥⑦⑧⑨⑩©®™※○●■□▶▷「」『』《》〈〉×÷±℃％")
    # KS X 1001 한글 2,350자
    for hi in range(0xB0, 0xC9):
        for lo in range(0xA1, 0xFF):
            try:
                chars.add(bytes([hi, lo]).decode("euc-kr"))
            except UnicodeDecodeError:
                pass
    # 사이트 원고에 쓰인 글자 전부 (한자 포함)
    for path in (SITE / "src").rglob("*.html"):
        chars |= set(path.read_text(encoding="utf-8"))
    chars |= set((SITE / "build.py").read_text(encoding="utf-8"))
    return "".join(sorted(c for c in chars if c.isprintable()))


def main():
    if len(sys.argv) < 2:
        raise SystemExit("사용법: python tools/make_fonts.py <Pretendard TTF 폴더>")
    src = Path(sys.argv[1])
    OUT.mkdir(parents=True, exist_ok=True)
    text = charset()
    for name in WEIGHTS:
        ttf = src / f"Pretendard-{name}.ttf"
        out = OUT / f"Pretendard-{name}.subset.woff2"
        opts = subset.Options()
        opts.flavor = "woff2"
        opts.layout_features = ["*"]
        opts.name_IDs = ["*"]
        opts.notdef_outline = True
        font = subset.load_font(str(ttf), opts)
        s = subset.Subsetter(opts)
        s.populate(text=text)
        s.subset(font)
        subset.save_font(font, str(out), opts)
        print(f"{out.name}: {out.stat().st_size // 1024} KB")


if __name__ == "__main__":
    main()
