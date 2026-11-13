import sys,json,time
sys.path.insert(0, __import__('os').path.expanduser('~/.claude/skills/map-motion/scripts'))
import amap
P=json.load(open('data/pois.json'))
L=lambda n:P[n]['loc']
pairs=[("大理凤仪机场","大理古城南门"),("大理站","大理古城南门"),("大理古城南门","龙龛码头"),("龙龛码头","喜洲古镇"),("大理古城南门","喜洲古镇"),("喜洲古镇","双廊古镇"),("大理古城南门","双廊古镇"),("双廊古镇","小普陀"),("小普陀","大理站"),("大理古城南门","苍山感通索道")]
res={}
for a,b in pairs:
    r=amap.get("/v3/direction/driving",origin=L(a),destination=L(b),strategy=0)
    p=r["route"]["paths"][0]; res[f"{a}->{b}"]=(round(int(p["distance"])/1000,1),round(int(p["duration"])/60))
    print(a,"->",b,res[f"{a}->{b}"]); time.sleep(0.4)
json.dump(res,open('data/drive.json','w'),ensure_ascii=False,indent=1)
