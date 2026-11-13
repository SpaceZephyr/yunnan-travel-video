"""Commons 搜索：python commons_search.py "关键词" ... → 列出标题/尺寸/授权"""
import json, re, sys, urllib.request, urllib.parse
H = {"User-Agent": "map-motion/1.0 (video tool)"}
import time
def get(p):
    for k in range(6):
        try: return json.load(urllib.request.urlopen(urllib.request.Request("https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode(p), headers=H), timeout=60))
        except Exception as e: time.sleep(15 * (k + 1))
    return {}
for q in sys.argv[1:]:
    d = get({"action": "query", "generator": "search", "gsrsearch": q + " filetype:bitmap", "gsrnamespace": 6, "gsrlimit": 15,
             "prop": "imageinfo", "iiprop": "size|extmetadata", "format": "json"})
    print(f"## {q}", flush=True); time.sleep(4)
    for pg in sorted(d.get("query", {}).get("pages", {}).values(), key=lambda x: x.get("index", 0)):
        ii = pg["imageinfo"][0]; m = ii.get("extmetadata", {})
        lic = re.sub(r"<[^>]+>", "", m.get("LicenseShortName", {}).get("value", ""))
        desc = re.sub(r"<[^>]+>", "", m.get("ImageDescription", {}).get("value", ""))[:70].replace("\n", " ")
        print(f"  {pg['title']} | {ii['width']}x{ii['height']} | {lic} | {desc}")
