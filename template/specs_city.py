"""大理城市总攻略：平面地图镜头（竖屏 satellite-guide）。坐标一律 GCJ-02（来自 city.json / data/pois.json）。
时长按 voice/ 实际配音定：map 段 = 各句 (配音+0.25) 之和 + 0.35。"""
import json, subprocess
from pathlib import Path

P = Path(__file__).resolve().parent
CITY = json.load(open(P / "city.json"))
POI = {k: [float(x) for x in v["loc"].split(",")] for k, v in json.load(open(P / "data/pois.json")).items()}
POI.update({"感通索道上站": [100.143958, 25.645131], "磻溪S湾": [100.150486, 25.766857], "才村码头": [100.193637, 25.718727],
            "古城北门": [100.158108, 25.702303], "昆明": [102.833, 24.88], "丽江": [100.2527, 26.8105]})
COL = {z["id"]: z["color"] for z in CITY["zones"]}

def vd(n):
    f = P / "voice" / f"s{n:02d}.wav"
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(f)], capture_output=True, text=True).stdout)
def need(*ns): return sum(vd(n) + 0.25 for n in ns) + 0.35

BASIN = {"lng": 100.19, "lat": 25.765, "zoom": 10.75}          # 整个洱海坝子
# 三块示意区（手画，非精确边界）
ZONE_RING = {
    "A": [[100.095, 25.635], [100.175, 25.630], [100.185, 25.675], [100.175, 25.715], [100.12, 25.72], [100.09, 25.68]],
    "B": [[100.175, 25.690], [100.215, 25.692], [100.200, 25.745], [100.170, 25.810], [100.160, 25.870], [100.120, 25.868], [100.130, 25.800], [100.160, 25.730]],
    "C": [[100.175, 25.900], [100.200, 25.935], [100.235, 25.880], [100.255, 25.810], [100.275, 25.720], [100.270, 25.620], [100.240, 25.615], [100.238, 25.700], [100.220, 25.800], [100.195, 25.870]],
}
_ZR = json.load(open(P / "data/zone_rings.json")); ZONE_RING["B"], ZONE_RING["C"] = _ZR["B"], _ZR["C"]
ZONE_LAB = {"A": [100.135, 25.672], "B": [100.150, 25.800], "C": [100.245, 25.770]}
ZNAME = {z["id"]: z["name"] for z in CITY["zones"]}

def spec(shots): return {"size": "portrait", "fps": 30, "style": "satellite-guide", "tail": 0, "attribution": False, "shots": shots}
def view(v, dur, **kw): return {"type": "view", "view": v, "dur": dur, **kw}
def lab(text, at, size=60, delay=0.3, **kw): return {"text": text, "at": at, "size": size, "delay": delay, **kw}
ZLAB_AT = {"A": [100.105, 25.630], "B": [100.105, 25.845], "C": [100.300, 25.715]}
def zone(z, dur, label=True, **kw):
    r = {"type": "area", "name": ZNAME[z], "rings": [ZONE_RING[z]], "smooth": True, "color": COL[z], "dur": dur, "fly": 0,
         "label": "", "view": BASIN, **kw}
    if label: r["labels"] = [lab(ZNAME[z], ZLAB_AT[z], 58, 0.2)]
    return r
def route(a, b, dur, mode="driving", via=None, **kw):
    r = {"type": "route", "from": {"name": a, "at": POI[a]}, "to": {"name": b, "at": POI[b]}, "mode": mode, "dur": dur,
         "odometer": False, "vehicle": "none", **kw}
    if via: r["via"] = [{"name": v, "at": POI[v]} for v in via]
    return r

M = {}
# 句1–2：云南里的大理 → 坝子：苍山 / 洱海 / 古城 → 三块依次上色
t = need(1, 2)
M["m_open"] = spec([
    {"type": "region", "names": ["大理市"], "colors": ["#B04CE0"], "opacity": 0.45, "labels": ["大理"], "dur": 2.6,
     "view": {"lng": 100.25, "lat": 25.72, "zoom": 8.7}, "fly": 0},
    view(BASIN, vd(1) - 2.0, fly=1.0, clear=True, labels=[lab("苍山", [100.085, 25.76], 96, 0.2), lab("洱海", [100.185, 25.885], 96, 0.6),
                                                          lab("古城", [100.160, 25.690], 64, 1.0)]),
    zone("A", 1.6), zone("B", 1.6), zone("C", max(1.6, t - vd(1) - 0.6 - 3.2 - 0.4)),
])
# 句5：昆明、丽江 → 大理站（直线示意，动车）
M["m_p5"] = spec([
    {"type": "pins", "places": [{"name": "大理站", "at": POI["大理站"]}], "labels": ["大理站"], "pin": "dot", "dur": 0.6, "fly": 0,
     "view": {"lng": 101.35, "lat": 26.2, "zoom": 7.15}},
    {"type": "route", "from": {"name": "昆明", "at": POI["昆明"]}, "to": {"name": "大理站", "at": POI["大理站"]}, "mode": "line", "vehicle": "train",
     "dur": 1.4, "fly": 0, "odometer": False, "labels": [lab("昆明", [102.75, 24.95], 52, 0.8)], "view": {"lng": 101.35, "lat": 26.2, "zoom": 7.15}},
    {"type": "route", "from": {"name": "丽江", "at": POI["丽江"]}, "to": {"name": "大理站", "at": POI["大理站"]}, "mode": "line", "vehicle": "train",
     "dur": 1.2, "fly": 0, "odometer": False, "second": True, "view": {"lng": 101.35, "lat": 26.2, "zoom": 7.15}},
])
# 句6：大理站 → 古城（驾车，整句）
M["m_p6"] = spec([
    view(BASIN, 0.6, fly=0, labels=[lab("大理站", POI["大理站"], 56, 0.0), lab("古城", POI["大理古城南门"], 56, 0.0)]),
    route("大理站", "大理古城南门", need(6) - 1.0, fly=0.2),
])
# 句7：机场 → 古城
M["m_p7"] = spec([
    view({"lng": 100.23, "lat": 25.66, "zoom": 10.9}, 0.4, fly=0, labels=[lab("凤仪机场", POI["大理凤仪机场"], 56, 0.0)]),
    route("大理凤仪机场", "大理古城南门", 2.0, fly=0.1),
])
# 句8：怎么动：三块各一种交通
M["m_move"] = spec([
    zone("A", 0.8, label=False), zone("B", 0.8, label=False), zone("C", 0.8, label=False),
    view(BASIN, need(8) - 2.4, fly=0, labels=[lab("古城 · 步行", [100.150, 25.690], 60, 0.3), lab("西岸 · 骑车", [100.150, 25.800], 60, 1.6),
                                               lab("东岸 · 打车", [100.245, 25.770], 60, 3.0)]),
])
# 句9–10：住哪
M["m_stay"] = spec([
    {"type": "pins", "places": [{"name": "古城", "at": POI["大理古城南门"]}, {"name": "才村", "at": POI["才村码头"]}, {"name": "龙龛", "at": POI["龙龛码头"]}],
     "labels": ["古城 · 首选", "才村 · 看日出", "龙龛"], "pin": "dot", "stagger": 1.3, "dur": vd(9) + 0.3, "fly": 0, "view": BASIN},
    {"type": "pins", "places": [{"name": "双廊", "at": POI["双廊古镇"]}], "labels": ["双廊 · 住一晚"], "pin": "dot", "dur": need(10) - 0.1, "fly": 0, "view": BASIN},
])
# 句11：A 区：古城 → 感通索道 → 上站
A_VIEW = {"lng": 100.153, "lat": 25.664, "zoom": 13.0}
M["m_p11"] = spec([
    view(A_VIEW, 0.5, fly=0, labels=[lab("古城", POI["大理古城南门"], 56, 0.0)]),
    route("大理古城南门", "苍山感通索道", 1.6, fly=0, view=A_VIEW, pin_to="dot"),
    {"type": "route", "from": {"name": " ", "at": POI["苍山感通索道"]}, "to": {"name": "上站", "at": POI["感通索道上站"]}, "mode": "line",
     "vehicle": "none", "dur": 1.3, "fly": 0, "odometer": False, "second": True, "view": A_VIEW,
     "labels": [lab("上站 2500多米", [100.1395, 25.6485], 50, 0.9)]},
])
OLD = {"lng": 100.155, "lat": 25.698, "zoom": 14.6}
M["m_p13"] = spec([route("大理古城南门", "古城北门", 1.7, mode="walking", fly=0, view=OLD)])
M["m_p14"] = spec([route("古城北门", "崇圣寺三塔", 1.8, mode="walking", fly=0, view={"lng": 100.151, "lat": 25.701, "zoom": 14.4})])
# B 区
B_VIEW = {"lng": 100.170, "lat": 25.775, "zoom": 11.9}
M["m_p15"] = spec([zone("B", 1.0, label=False, view=B_VIEW),
                   {"type": "pins", "places": [{"name": "龙龛码头", "at": POI["龙龛码头"]}], "labels": ["龙龛码头"], "pin": "dot", "dur": 1.3, "fly": 0, "view": B_VIEW}])
M["m_p17"] = spec([route("龙龛码头", "磻溪S湾", 2.4, mode="bicycling", via=["才村码头"], fly=0, view=B_VIEW)])
M["m_p18"] = spec([route("磻溪S湾", "喜洲古镇", 1.9, mode="bicycling", fly=0, view=B_VIEW)])
# C 区
C_VIEW = {"lng": 100.200, "lat": 25.800, "zoom": 11.2}
M["m_p19"] = spec([zone("C", 0.9, label=False, view=C_VIEW), route("喜洲古镇", "双廊古镇", 1.6, fly=0, view=C_VIEW)])
M["m_p20"] = spec([route("双廊古镇", "小普陀", 1.3, fly=0, view=C_VIEW), route("小普陀", "下关洱海公园", 1.2, fly=0, second=True, view=C_VIEW)])
# 句21–22：组合（行程卡叠层在 build 里画）；句23：收尾
M["m_plan"] = spec([zone("A", 0.7), zone("B", 0.7), zone("C", 0.7), view(BASIN, need(21, 22) - 2.1, fly=0)])
M["m_recap"] = spec([zone("A", 0.6, label=False), zone("B", 0.6, label=False), zone("C", 0.6, label=False),
                     view(BASIN, need(23) + 0.6, fly=0, labels=[lab("先上山", [100.12, 25.70], 80, 0.6), lab("再环湖", [100.21, 25.80], 80, 1.8)])])

if __name__ == "__main__":
    for k, v in M.items(): json.dump(v, open(P / f"{k}.json", "w"), ensure_ascii=False, indent=1)
    print("写了", " ".join(M))
