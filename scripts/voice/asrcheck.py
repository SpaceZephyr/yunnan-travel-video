# 逐句 Whisper 转写，对照稿子看有没有念错：python asrcheck.py <lines.json> <音频目录> [句号,逗号分隔]
import sys, json, glob, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
L = json.load(open(sys.argv[1])); d = sys.argv[2]
for f in sorted(glob.glob(d + "/s*.wav")):
    n = int(os.path.basename(f)[1:3])
    if len(sys.argv) > 3 and str(n) not in sys.argv[3].split(","): continue
    x, sr = rd(f); print(os.path.basename(f), f"{len(x)/sr:.1f}s", asr(x, sr), flush=True)
