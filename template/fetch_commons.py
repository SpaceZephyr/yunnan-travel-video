"""按标题取 Commons 文件信息（授权、作者、尺寸、时长）并下载到 src/，记到 src/commons.json。"""
import json, re, sys, time, urllib.request, urllib.parse
from pathlib import Path
P = Path(__file__).resolve().parent; SRC = P / "src"; H = {"User-Agent": "map-motion/1.0 (wzfh video tool)"}
want = dict(a.split("=", 1) for a in sys.argv[1:])          # 本地名=File:标题
def get(u):
    for k in range(5):
        try: return json.load(urllib.request.urlopen(urllib.request.Request(u, headers=H), timeout=60))
        except Exception as e: print("retry", e, flush=True); time.sleep(8 * (k + 1))
db = json.loads((SRC / "commons.json").read_text()) if (SRC / "commons.json").exists() else []
for local, title in want.items():
    d = get("https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode({"action": "query", "titles": title, "prop": "imageinfo", "iiprop": "url|size|extmetadata|mediatype", "iiurlwidth": int(__import__("os").environ.get("TW", "1920")), "format": "json"}))
    pg = next(iter(d["query"]["pages"].values()))
    if "imageinfo" not in pg: print("✗ 没找到", title); continue
    ii = pg["imageinfo"][0]; m = ii.get("extmetadata", {})
    strip = lambda s: re.sub(r"<[^>]+>", "", s or "").strip()
    rec = {"file": local, "title": title, "url": ii["url"], "license": strip(m.get("LicenseShortName", {}).get("value")), "artist": strip(m.get("Artist", {}).get("value")),
           "w": ii.get("width"), "h": ii.get("height"), "dur": ii.get("duration")}
    out = SRC / local
    dl = ii.get("thumburl") if local.endswith((".jpg", ".png")) and ii.get("thumburl") else ii["url"]   # 大图取 2400px 缩略图，原图常被限流
    if not out.exists():
        for k in range(5):
            try:
                with urllib.request.urlopen(urllib.request.Request(dl, headers=H), timeout=300) as r: out.write_bytes(r.read()); break
            except Exception as e: print("retry dl", e, flush=True); time.sleep(10 * (k + 1))
    db = [x for x in db if x.get("file") != local] + [rec]
    print(f"✓ {local}  {rec['w']}x{rec['h']}  {rec['dur']}s  {rec['license']}  {rec['artist'][:40]}", flush=True); time.sleep(3)
(SRC / "commons.json").write_text(json.dumps(db, ensure_ascii=False, indent=1))
