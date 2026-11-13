"""从 build.EDIT + src/commons.json 生成 footage_audit.md 和 pub/素材来源.txt"""
import json, sys
sys.argv = ["x"]; import build as B
db = {x["file"]: x for x in json.load(open("src/commons.json"))}
page = lambda t: "https://commons.wikimedia.org/wiki/" + t.replace(" ", "_")
A = ["# footage_audit · 大理城市总攻略", "每句实拍：关键词（at）→ 文件 → Commons 文件页 / 作者 / 授权。地点按 Commons 描述核对；地点不确定的图（索道车厢、廊道泛景、苍山远眺、日落）不加地名字幕。",
     "| 句 | 关键词 | 字幕 | 文件 | 作者 | 授权 | 文件页 |", "|---|---|---|---|---|---|---|"]
T = ["大理城市总攻略 · 素材来源", "地图：高德卫星影像（画面内不显示标识）；路线：高德驾车 / 步行 / 骑行路线规划；片区范围为示意", "图标：Noto Emoji（Google，Apache License 2.0）", "照片均来自 Wikimedia Commons：", ""]
seen = set()
for e in B.EDIT:
    files = list(e.get("photos", [])) + ([{"file": e["bg"], "at": "（清单底图，虚化）"}] if e.get("bg") else [])
    for p in files:
        r = db[p["file"]]
        A.append(f"| {e['lines'][0]} | {p.get('at') or '（顺延）'} | {p.get('cap') or '—'} | {p['file']} | {r['artist']} | {r['license']} | {page(r['title'])} |")
        if p["file"] not in seen: T.append(f"- {r['title'][5:]} — {r['artist']}，{r['license']}，{page(r['title'])}"); seen.add(p["file"])
open("footage_audit.md", "w").write("\n".join(A) + "\n")
open("pub/素材来源.txt", "w").write("\n".join(T) + "\n")
print(len(seen), "张")
