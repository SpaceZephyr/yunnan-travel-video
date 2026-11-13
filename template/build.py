"""大理城市总攻略 build.py（city-guide 模板首版）。
剪辑段类型：map（整段地图）/ mix（地图开头 + 关键词锚定照片）/ card（虚化实拍底 + 图标清单）。
叠层组件：字幕、照片地名、顶部章节条、图标清单、巨型地名水印、行程卡、片尾署名。
用法：uv run -q --offline --with pillow python build.py"""
import json, re, subprocess, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps

P = Path(__file__).resolve().parent; SEG = P / "seg"; SRC = P / "src"; F = P / "fonts"; ICON = P / "icons"
W, H, FPS = 1080, 1920, 30
MM = Path.home() / ".claude/skills/map-motion/scripts"
LINES = json.loads((P / "lines.json").read_text())
CITY = json.loads((P / "city.json").read_text())
COL = {z["id"]: z["color"] for z in CITY["zones"]}
STICK = str(F / "ZCOOLQingKeHuangYou-Regular.ttf"); BRUSH = str(F / "MaShanZheng-Regular.ttf"); DARK = str(F / "ZCOOLKuaiLe-Regular.ttf")
YEL = (246, 224, 74)
BGM = Path.home() / ".claude/skills/space-explainer-video/assets/bgm/smile.mp3"
LEAD, GAP = 0.15, 0.25
ZOOM = 0.12; FG_CY = 980
OUT_NAME = "大理城市攻略_完整版.mp4"


def sh(*a, **k): return subprocess.run([str(x) for x in a], check=True, **k)
def dur(f): return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(f)], capture_output=True, text=True).stdout)
def vdur(n): return dur(P / "voice" / f"s{n:02d}.wav")
def font(path, size): return ImageFont.truetype(path, size)
def hexc(h): h = h.lstrip("#"); return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def shadow(layer, blur=10, off=(4, 10), alpha=0.45):
    a = layer.split()[3].filter(ImageFilter.GaussianBlur(blur)).point(lambda v: int(v * alpha))
    out = Image.new("RGBA", (layer.width + 60, layer.height + 60), (0, 0, 0, 0))
    s = Image.new("RGBA", layer.size, (20, 14, 4, 255)); s.putalpha(a)
    out.alpha_composite(s, (30 + off[0], 30 + off[1])); out.alpha_composite(layer, (30, 30)); return out


def text_img(text, fpath, size, fill="white", stroke=6, stroke_fill=(25, 20, 10)):
    f = font(fpath, size); b = f.getbbox(text, stroke_width=stroke)
    L = Image.new("RGBA", (b[2] - b[0] + 16, b[3] - b[1] + 16))
    ImageDraw.Draw(L).text((8 - b[0], 8 - b[1]), text, font=f, fill=fill, stroke_width=stroke, stroke_fill=stroke_fill); return L


def brush_img(text):
    f = font(BRUSH, 76 if len(text) <= 6 else 60); b = f.getbbox(text, stroke_width=4)
    L = Image.new("RGBA", (b[2] - b[0] + 20, b[3] - b[1] + 20)); ImageDraw.Draw(L).text((10 - b[0], 10 - b[1]), text, font=f, fill=(255, 251, 232), stroke_width=4, stroke_fill=(40, 30, 10))
    return shadow(L, blur=8, off=(3, 6), alpha=0.6)


def icon(code, size):
    im = Image.open(ICON / f"{code}.png").convert("RGBA"); return im.resize((size, size), Image.LANCZOS)


# ---- 字幕 ----
SHOW = {"两千米": "2000米", "四十分钟": "40分钟", "一个小时": "1个小时", "二十分钟": "20分钟", "下午两点": "下午2点",
        "两千五百多米": "2500多米", "两公里": "2公里", "一千多年": "1000多年", "四十多分钟": "40多分钟",
        "第一天": "第1天", "第二天": "第2天", "两个小时": "2个小时"}
HL = {
    1: ["大理", "环洱海", "苍山", "洱海", "古城"], 2: ["三块", "古城和苍山", "洱海西岸", "洱海东岸", "不走回头路"],
    3: ["防晒霜", "墨镜", "外套", "两千米"], 4: ["索道", "提前在网上订好"], 5: ["动车", "大理站", "昆明", "两个小时", "丽江", "一个半小时起"],
    6: ["下关", "十几公里", "四十分钟"], 7: ["凤仪机场", "一个小时"], 8: ["靠走", "骑车", "打车", "包车"],
    9: ["住古城", "洱海日出", "才村", "龙龛"], 10: ["双廊", "住一晚", "东北角"],
    11: ["古城和苍山", "感通索道", "二十分钟", "下午两点", "早点去"], 12: ["两千五百多米", "清碧溪", "洱海", "古城"],
    13: ["南门", "人民路", "北门", "不要门票"], 14: ["两公里", "崇圣寺三塔", "半小时", "一千多年", "单独买票"],
    15: ["洱海西岸", "龙龛码头", "生态廊道", "不让汽车进", "全天免费"], 16: ["共享单车", "电动车", "拦在外面"],
    17: ["才村", "S湾", "苍山", "洱海"], 18: ["喜洲古镇", "白族", "喜洲粑粑", "十几公里", "半天"],
    19: ["洱海东岸", "四十多分钟", "双廊", "坐一下午"], 20: ["日落前", "小普陀", "苍山", "下关"],
    21: ["两天", "第一天", "古城加苍山", "第二天", "环湖一圈"], 22: ["一天", "上午苍山", "古城和三塔", "龙龛"],
    23: ["收藏", "三块", "先上山", "再环湖"],
}


def show(s):
    for k, v in SHOW.items(): s = s.replace(k, v)
    return s


def say_parts(s):
    parts = [p for p in re.split(r"[，。：、！？；「」]", show(s)) if p.strip()]; return [(p, len(p)) for p in parts]


def sub_img(text, n):
    f = font(STICK, 64); hl = [show(k) for k in HL.get(n, [])]
    if f.getlength(text) > W - 90: f = font(STICK, int(64 * (W - 90) / f.getlength(text)))
    spans, i = [], 0
    while i < len(text):
        m = next((k for k in hl if text.startswith(k, i)), None)
        if m: spans.append((m, True)); i += len(m)
        else:
            if spans and not spans[-1][1]: spans[-1] = (spans[-1][0] + text[i], False)
            else: spans.append((text[i], False))
            i += 1
    tw = sum(f.getlength(s) for s, _ in spans); L = Image.new("RGBA", (W, 130)); d = ImageDraw.Draw(L); x = (W - tw) / 2
    for s, h in spans:
        d.text((x, 65), s, font=f, fill=YEL if h else "white", anchor="lm", stroke_width=6, stroke_fill=(25, 20, 10)); x += f.getlength(s)
    return L


# ---- 画面段 ----
def pipe_out(o):
    return subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                             "-c:v", "libx264", "-crf", "17", "-pix_fmt", "yuv420p", str(o)], stdin=subprocess.PIPE)


def photo_clip(src_path, d, o):
    """整幅显示 + 背景同图虚化，从 1.0 平滑推到 1.12（不平移、不冻结）"""
    im = ImageOps.exif_transpose(Image.open(src_path)).convert("RGB")
    bg = ImageOps.fit(im, (W, H), Image.LANCZOS).filter(ImageFilter.GaussianBlur(40))
    bg = Image.blend(bg, Image.new("RGB", (W, H), (10, 10, 10)), 0.35)
    s0 = min(W / im.width, 1180 / im.height) * (1.0 + ZOOM)
    fg = im.resize((int(im.width * s0), int(im.height * s0)), Image.LANCZOS)
    m = Image.new("L", fg.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, fg.width - 1, fg.height - 1), 18 if fg.width < W else 0, fill=255)
    pr = pipe_out(o); n = int(round(d * FPS)); z0 = 1.0 / (1.0 + ZOOM)
    for i in range(n):
        z = z0 + (1.0 - z0) * i / max(1, n - 1)
        fw, fh = int(fg.width * z), int(fg.height * z); f2 = fg.resize((fw, fh), Image.BILINEAR); m2 = m.resize((fw, fh), Image.BILINEAR)
        cw = min(fw, W); x0 = (fw - cw) // 2; fr = bg.copy()
        if cw < W: fr.paste(f2, (int((W - fw) / 2), FG_CY - fh // 2), m2)
        else: fr.paste(f2.crop((x0, 0, x0 + cw, fh)), ((W - cw) // 2, FG_CY - fh // 2), m2.crop((x0, 0, x0 + cw, fh)))
        pr.stdin.write(fr.tobytes())
    pr.stdin.close(); pr.wait()


def blur_clip(src_path, d, o):
    """card 段底图：整屏铺满、重度虚化压暗，缓慢推近"""
    im = ImageOps.exif_transpose(Image.open(src_path)).convert("RGB")
    big = ImageOps.fit(im, (int(W * 1.1), int(H * 1.1)), Image.LANCZOS).filter(ImageFilter.GaussianBlur(26))
    big = Image.blend(big, Image.new("RGB", big.size, (12, 12, 12)), 0.30)
    pr = pipe_out(o); n = int(round(d * FPS))
    for i in range(n):
        w2, h2 = int(big.width * (1 - 0.08 * i / max(1, n - 1))), int(big.height * (1 - 0.08 * i / max(1, n - 1)))
        x0, y0 = (big.width - w2) // 2, (big.height - h2) // 2
        pr.stdin.write(big.crop((x0, y0, x0 + w2, y0 + h2)).resize((W, H), Image.BILINEAR).tobytes())
    pr.stdin.close(); pr.wait()


def cut(src, d, o):
    """从地图段截 d 秒；不足时整体放慢（不用 tpad 冻结尾帧）"""
    if not Path(src).exists():
        print(f"  ⚠️ {src} 不存在，黑屏占位", flush=True)
        sh("ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", f"color=c=black:s={W}x{H}:d={d:.3f},fps={FPS},format=yuv420p", "-t", f"{d:.3f}", "-c:v", "libx264", "-crf", "18", o); return
    sd = dur(src)
    vf = f"fps={FPS},format=yuv420p" if sd >= d - 0.1 else f"setpts=PTS*{max(1.01, (d + 0.05) / sd):.5f},fps={FPS},format=yuv420p"
    sh("ffmpeg", "-y", "-v", "error", "-i", src, "-an", "-vf", vf, "-t", f"{d:.3f}", "-c:v", "libx264", "-crf", "17", o)


def concat(parts, o):
    lst = o.with_suffix(".txt"); lst.write_text("".join(f"file '{p}'\n" for p in parts))
    sh("ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", lst, "-vf", f"fps={FPS},format=yuv420p", "-c:v", "libx264", "-crf", "17", o)
    lst.unlink(missing_ok=True)
    for p in parts: Path(p).unlink(missing_ok=True)


# ---- 时间 ----
VSTART = {}


def kw_t(n, kw):
    """第 n 句里关键词 kw 的绝对时刻（按字数比例）"""
    text = LINES[n - 1]; i = text.find(kw)
    if i < 0: raise SystemExit(f"第 {n} 句里找不到「{kw}」")
    clean = lambda s: re.sub(r"[，。：、！？；「」\s]", "", s)
    a = VSTART[n]; return a + vdur(n) * len(clean(text[:i])) / max(1, len(clean(text)))


def line_end(n): return VSTART[n] + vdur(n)


# ---- 剪辑表 ----
def ph(file, at=None, cap=None): return {"file": file, "at": at, "cap": cap}
EDIT = [
    {"kind": "map", "lines": [1, 2], "seg": "m_open"},
    {"kind": "card", "lines": [3, 4], "bg": "erhai_cs2.jpg"},
    {"kind": "mix", "lines": [5], "map": "m_p5", "map_dur": 3.2, "photos": [ph("station1.jpg", "大理站", "大理站")]},
    {"kind": "map", "lines": [6], "seg": "m_p6"},
    {"kind": "mix", "lines": [7], "map": "m_p7", "map_dur": 2.0, "photos": [ph("airport1.jpg", "凤仪机场", "凤仪机场")]},
    {"kind": "map", "lines": [8], "seg": "m_move"},
    {"kind": "map", "lines": [9, 10], "seg": "m_stay"},
    {"kind": "mix", "lines": [11], "map": "m_p11", "map_dur": 3.6, "photos": [ph("gantong_low.jpg", "感通索道", "感通索道下站")]},
    {"kind": "mix", "lines": [12], "photos": [ph("cable_view.jpg", None, None), ph("qingbi.jpg", "清碧溪", "清碧溪"), ph("geopark.jpg", "回头看")]},
    {"kind": "mix", "lines": [13], "map": "m_p13", "map_dur": 1.7, "photos": [ph("south_gate.jpg", "南门", "古城南门"), ph("renmin3.jpg", "人民路", "人民路")]},
    {"kind": "mix", "lines": [14], "map": "m_p14", "map_dur": 1.8, "photos": [ph("pagoda1.jpg", "崇圣寺三塔", "崇圣寺三塔"), ph("pagoda_pond.jpg", "一千多年")]},
    {"kind": "mix", "lines": [15], "map": "m_p15", "map_dur": 2.3, "photos": [ph("corr21.jpg", "生态廊道", "洱海生态廊道")]},
    {"kind": "mix", "lines": [16], "photos": [ph("corr19.jpg", None, None)]},
    {"kind": "mix", "lines": [17], "map": "m_p17", "map_dur": 2.4, "photos": [ph("corr01.jpg", "苍山和洱海")]},
    {"kind": "mix", "lines": [18], "map": "m_p18", "map_dur": 1.9, "photos": [ph("xizhou1.jpg", "喜洲古镇", "喜洲古镇"), ph("xizhou4.jpg", "白族"), ph("baba.jpg", "喜洲粑粑", "喜洲粑粑")]},
    {"kind": "mix", "lines": [19], "map": "m_p19", "map_dur": 2.5, "photos": [ph("shuang1.jpg", "双廊", "双廊"), ph("shuang2.jpg", "坐一下午")]},
    {"kind": "mix", "lines": [20], "map": "m_p20", "map_dur": 2.5, "photos": [ph("xpt1.jpg", "小普陀", "小普陀"), ph("erhai_cs.jpg", "太阳落到")]},
    {"kind": "map", "lines": [21, 22], "seg": "m_plan"},
    {"kind": "map", "lines": [23], "seg": "m_recap"},
]
# 章节条：(首句, 末句, 图标, 文字)
CHAPTERS = [(3, 4, "1f9f4", "出发前"), (5, 7, "1f684", "怎么到"), (8, 8, "1f6b2", "怎么动"), (9, 10, "1f3e0", "住哪"), (11, 14, "1f3d4", "古城和苍山"),
            (15, 18, "1f6b2", "洱海西岸"), (19, 20, "1f305", "洱海东岸"), (21, 22, "1f4c5", "怎么组合")]
# 图标清单：(句, 关键词, 图标, 文字)
CHECK = [(3, "防晒霜", "1f9f4", "防晒霜"), (3, "墨镜", "1f576", "墨镜"), (3, "外套", "1f9e5", "一件外套"),
         (3, "海拔", "26f0", "海拔2000米左右"), (4, "索道", "1f6a1", "索道票提前订")]
# 巨型地名水印：(句, 文字, 秒)
WATERMARK = [(11, "苍山", 3.0), (15, "洱海", 2.2), (19, "东岸", 2.3)]


def photos_timeline(photos, n, t0, D):
    """照片在 [t0, t0+D) 内的起止：锚定关键词，每张 ≥2.3s"""
    MIN = 2.3; k = len(photos)
    while k > 1 and D / k < MIN: k -= 1
    photos = photos[:k]; st = [0.0]
    for p in photos[1:]:
        st.append(kw_t(n, p["at"]) - t0 - 0.2 if p.get("at") else None)
    for i in range(1, k):
        if st[i] is None: st[i] = st[i - 1] + (D - st[i - 1]) / (k - i + 1)
        st[i] = min(max(st[i], st[i - 1] + MIN), D - MIN * (k - i))
    return photos, st + [D]


CAPS, OVL = [], []          # CAPS: (起, 止, 图) 照片地名；OVL: (起, 止, 图, (x, y), 动画)


def build_segments():
    t, parts = 0.0, []
    (P / "norm").mkdir(exist_ok=True)
    for i, e in enumerate(EDIT):
        tv = t + LEAD
        for n in e["lines"]: VSTART[n] = tv; tv += vdur(n) + GAP
        need = tv - t + 0.2; o = P / "norm" / f"{i:02d}.mp4"
        if e["kind"] == "map":
            cut(SEG / f"{e['seg']}.mp4", need, o)
        elif e["kind"] == "card":
            blur_clip(SRC / e["bg"], need, o)
        else:
            n = e["lines"][0]; sub = []; md = 0.0
            if e.get("map"):
                md = min(e["map_dur"], need - 2.3); p = o.with_name(f"{i:02d}_map.mp4"); cut(SEG / f"{e['map']}.mp4", md, p); sub.append(p)
            photos, st = photos_timeline(e["photos"], n, t + md, need - md)
            for k, it in enumerate(photos):
                d = st[k + 1] - st[k]; p = o.with_name(f"{i:02d}_{k}.mp4"); photo_clip(SRC / it["file"], d, p); sub.append(p)
                if it.get("cap"): CAPS.append((t + md + st[k] + 0.15, t + md + st[k + 1] - 0.1, brush_img(it["cap"])))
            concat(sub, o)
            e["map_t"] = (t, t + md)
        e["t"] = (t, t + need)
        parts.append(o); print(f"{i:2d} {e['kind']:<5}{str(e['lines']):<9}{t:7.2f}s +{need:5.2f}s", flush=True)
        t += need
    (P / "list.txt").write_text("".join(f"file '{p}'\n" for p in parts))
    base = P / "base.mp4"; sh("ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", P / "list.txt", "-c", "copy", base)
    return base, dur(base)


# ---- 叠层组件 ----
def chapter_bar(ic, text):
    tx = text_img(text, STICK, 62, fill=YEL, stroke=5); ico = icon(ic, 84)
    w = ico.width + tx.width + 70; h = 112
    L = Image.new("RGBA", (w, h)); d = ImageDraw.Draw(L); d.rounded_rectangle((0, 0, w - 1, h - 1), 56, fill=(18, 16, 12, 185))
    L.alpha_composite(ico, (26, (h - ico.height) // 2)); L.alpha_composite(tx, (26 + ico.width + 14, (h - tx.height) // 2 - 2)); return L


def check_row(ic, text):
    tx = text_img(text, STICK, 82, fill=YEL, stroke=7); ico = icon(ic, 128)
    L = Image.new("RGBA", (ico.width + 30 + tx.width, max(ico.height, tx.height))); L.alpha_composite(ico, (0, (L.height - ico.height) // 2))
    L.alpha_composite(tx, (ico.width + 30, (L.height - tx.height) // 2)); return shadow(L, blur=10, off=(3, 8), alpha=0.5)


def watermark(text):
    f = font(DARK, 380); b = f.getbbox(text); L = Image.new("RGBA", (b[2] - b[0] + 40, b[3] - b[1] + 40))
    ImageDraw.Draw(L).text((20 - b[0], 20 - b[1]), text, font=f, fill=(255, 255, 255, 120)); return L


def plan_card(rows, title):
    """行程卡：rows = [(左标签, [(片区id或None, 文字), ...])]"""
    ft, fl, fz = font(STICK, 70), font(STICK, 54), font(DARK, 46)
    w = 960; rh = 116; h = 140 + rh * len(rows) + 30
    L = Image.new("RGBA", (w, h)); d = ImageDraw.Draw(L)
    d.rounded_rectangle((0, 0, w - 1, h - 1), 36, fill=(255, 252, 240, 236))
    d.text((44, 40), title, font=ft, fill=(40, 30, 10))
    for r, (lab, segs) in enumerate(rows):
        y = 150 + r * rh; d.text((44, y + 18), lab, font=fl, fill=(120, 90, 30)); x = 44 + fl.getlength(lab) + 30
        for zid, txt in segs:
            tw = fz.getlength(txt); c = hexc(COL[zid]) if zid else (90, 90, 90)
            d.rounded_rectangle((x, y + 10, x + tw + 40, y + 86), 22, fill=c + (255,)); d.text((x + 20, y + 20), txt, font=fz, fill="white"); x += tw + 56
    return shadow(L, blur=14, off=(4, 12), alpha=0.35)


def build_overlays(total):
    for a, b, ic, txt in CHAPTERS:
        im = chapter_bar(ic, txt); OVL.append((VSTART[a] - LEAD, line_end(b) + GAP, im, ((W - im.width) // 2, 150), "drop"))
    card = next(e for e in EDIT if e["kind"] == "card"); ce = card["t"][1]
    for k, (n, kw, ic, txt) in enumerate(CHECK):
        im = check_row(ic, txt); OVL.append((kw_t(n, kw) - 0.1, ce - 0.05, im, (120, 360 + k * 190), "slide"))
    for n, txt, sec in WATERMARK:
        im = watermark(txt); OVL.append((VSTART[n] + 0.1, VSTART[n] + sec, im, ((W - im.width) // 2, 560), "fade"))
    plan = next(e for e in EDIT if e.get("seg") == "m_plan")
    two = plan_card([("第1天", [("A", "古城 + 苍山")]), ("第2天", [("B", "西岸骑行"), ("C", "东岸日落")])], "玩两天")
    one = plan_card([("上午", [("A", "苍山索道")]), ("下午", [("A", "古城 + 三塔")]), ("傍晚", [("B", "龙龛湖边")])], "只有一天")
    OVL.append((kw_t(21, "玩两天") - 0.1, VSTART[22] - 0.1, two, ((W - two.width) // 2, 330), "slide"))
    OVL.append((VSTART[22] - 0.05, plan["t"][1] - 0.05, one, ((W - one.width) // 2, 330), "slide"))


def place(fr, im, xy, tt, a, b, anim):
    al = max(0.0, min(1.0, (tt - a) / 0.25, (b - tt) / 0.2)); x, y = xy
    if anim == "slide": x += int((1 - al) * -60)
    if anim == "drop": y += int((1 - al) * -40)
    if anim == "fade" and tt - a < 0.6: s = 0.94 + 0.06 * (tt - a) / 0.6; im = im.resize((int(im.width * s), int(im.height * s))); x += (int(im.width / s) - im.width) // 2
    if al < 1: im = im.copy(); im.putalpha(im.split()[3].point(lambda v: int(v * al)))
    fr.alpha_composite(im, (x, y))


def compose():
    base, total = build_segments()
    print(f"\nbase: {total:.1f}s", flush=True)
    voice = sorted((VSTART[n], n, vdur(n)) for n in VSTART)
    subs = []
    for a, n, d in voice:
        ps = say_parts(LINES[n - 1]); tot = sum(k for _, k in ps); s0 = a
        for txt, k in ps: e = s0 + d * k / tot; subs.append((s0, e - 0.03, sub_img(txt, n))); s0 = e
    build_overlays(total)
    cred = Image.new("RGBA", (W, 60)); cf = font(DARK, 24)
    ct = "照片：Wikimedia Commons CC BY / BY-SA / CC0 · 图标：Noto Emoji Apache 2.0（见素材来源.txt）"
    ImageDraw.Draw(cred).text((int((W - cf.getlength(ct)) / 2), 18), ct, font=cf, fill=(170, 170, 170))
    ov = P / "overlay.mov"
    pr = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "qtrle", str(ov)], stdin=subprocess.PIPE)
    for i in range(int(round(total * FPS))):
        tt = i / FPS; fr = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        for a, b, im, xy, anim in OVL:
            if a <= tt < b: place(fr, im, xy, tt, a, b, anim)
        for a, b, im in CAPS:
            if a <= tt < b: place(fr, im, (50, 1360 - im.height), tt, a, b, "none")
        for a, b, im in subs:
            if a <= tt < b: fr.alpha_composite(im, (0, 1530))
        if tt >= total - 3.0: fr.alpha_composite(cred, (0, H - 90))
        pr.stdin.write(fr.tobytes())
    pr.stdin.close(); pr.wait()
    sys.path.insert(0, str(MM)); import audio
    ev = [{"t": round(a, 3), "type": "clip", "path": str(P / "voice" / f"s{n:02d}.wav"), "dur": round(d, 3), "fin": 0.02, "fout": 0.06} for a, n, d in voice]
    wav = P / "mix.wav"; audio.mix(ev, total, wav, {"file": str(BGM), "volume": 0.07})
    out = P / OUT_NAME
    sh("ffmpeg", "-y", "-v", "error", "-i", base, "-i", ov, "-i", wav, "-filter_complex", "[0:v][1:v]overlay=0:0:eof_action=pass,format=yuv420p[v]",
       "-map", "[v]", "-map", "2:a", "-c:v", "libx264", "-crf", "19", "-preset", "medium", "-c:a", "aac", "-b:a", "192k", "-shortest", out)
    json.dump({"vstart": VSTART, "total": total, "edit": [{k: v for k, v in e.items() if k != "photos"} for e in EDIT]},
              open(P / "timeline_used.json", "w"), ensure_ascii=False, indent=1)
    print(f"\n✓ {out}  {total:.1f}s  字幕 {len(subs)}  叠层 {len(OVL)}", flush=True)


if __name__ == "__main__":
    compose()
