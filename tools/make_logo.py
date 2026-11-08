"""흰 배경 로고 PNG를 투명 배경 로고(남색)와 흰색 로고로 만든다.

    python tools/make_logo.py src/assets/img/logo-original.png
"""
import sys
from PIL import Image

src = Image.open(sys.argv[1]).convert("RGB")
w, h = src.size
# 로고 본래 색: 가장 진한 픽셀들의 평균
dark = sorted(src.getdata(), key=sum)[: max(1, w * h // 50)]
navy = tuple(sum(c[i] for c in dark) // len(dark) for i in range(3))
gray = src.convert("L")
lo = min(gray.getdata())
# 밝기를 투명도로: 흰색 = 투명, 가장 진한 곳 = 불투명
alpha = gray.point(lambda v: 0 if v >= 245 else min(255, round((245 - v) * 255 / (245 - lo))))
bbox = alpha.getbbox()
pad = 4
bbox = (max(0, bbox[0] - pad), max(0, bbox[1] - pad), min(w, bbox[2] + pad), min(h, bbox[3] + pad))
for name, color in (("logo.png", navy), ("logo-white.png", (255, 255, 255))):
    out = Image.new("RGBA", (w, h), color + (0,))
    out.putalpha(alpha)
    out = out.crop(bbox)
    out.save(f"src/assets/img/{name}", optimize=True)
    print(name, out.size, "color", "#%02X%02X%02X" % color)
