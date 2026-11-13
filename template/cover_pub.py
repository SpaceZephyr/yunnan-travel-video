"""发布用封面：三塔洱海铺底 + 贴纸大字（系列视觉一致）。出 3:4 / 9:16 / 4:3。"""
from PIL import Image, ImageOps, ImageDraw, ImageEnhance
import sys
from pathlib import Path
sys.path.insert(0, ".")
import build as B

OUT = Path(__file__).resolve().parent / "pub"


def sticker_img(text, size, fill, tilt=0):
    f = B.font(B.STICK, size)
    b = f.getbbox(text, stroke_width=5)
    L = Image.new("RGBA", (b[2] - b[0] + 20, b[3] - b[1] + 20))
    d = ImageDraw.Draw(L)
    d.text((10 - b[0], 10 - b[1]), text, font=f, fill=fill, stroke_width=5, stroke_fill=(30, 20, 5))
    return B.shadow(L, blur=10, off=(4, 10), alpha=0.5)


def fit_sticker(text, size, fill, max_w, tilt=0):
    """宽度超限时自动缩字号，保证不裁字"""
    im = sticker_img(text, size, fill, tilt)
    while im.width > max_w and size > 40:
        size = int(size * 0.94)
        im = sticker_img(text, size, fill, tilt)
    return im


SIZES = {"封面-3x4.png": (1080, 1440), "封面-9x16.png": (1080, 1920), "封面-4x3.png": (1440, 1080)}

for name, (w, h) in SIZES.items():
    bg = ImageOps.fit(Image.open(B.SRC / "pagoda_lake.jpg").convert("RGB"), (w, h),
                      Image.LANCZOS, centering=(0.12, 0.5)).convert("RGBA")
    bg = ImageEnhance.Brightness(bg).enhance(1.12)

    shade = Image.new("RGBA", (w, h))
    d = ImageDraw.Draw(shade)
    for y in range(h):
        d.line([(0, y), (w, y)], fill=(20, 14, 4, int(125 * max(0, 1 - y / (h * 0.62)))))
    bg.alpha_composite(shade)

    k = h / 1920  # 按高度等比缩放字号
    lines = [
        ("第一次去大理", 200, B.YEL, 0.18),
        ("先看懂这三块", 170, (255, 255, 255), 0.33),
        ("古城苍山｜洱海西岸｜东岸", 96, B.YEL, 0.46),
    ]
    for text, size, fill, yf in lines:
        s = int(size * (k if w <= h else k * 0.9))
        im = fit_sticker(text, s, fill, int(w * 0.9))
        bg.alpha_composite(im, (int(w / 2 - im.width / 2), int(h * yf - im.height / 2)))

    tag = fit_sticker("两天 / 一天怎么排都有", int(76 * (k if w <= h else k * 0.9)), (255, 150, 90), int(w * 0.9))
    bg.alpha_composite(tag, (int(w / 2 - tag.width / 2), int(h * (0.72 if w <= h else 0.76))))

    bg.convert("RGB").save(OUT / name)
    print("OK", name, bg.size)
