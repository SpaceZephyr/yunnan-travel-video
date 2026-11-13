# 用阿里云百炼 qwen-audio-3.1-tts-next 克隆声音配音（参考音频随请求上传，不用先建音色）
# 用法（普通 python3 即可，不用 index-tts 环境）：
#   python3 clone_bailian.py <项目> [句号...] [seeds=3,21] [out=voice_raw] [style=像在讲旅行攻略一样自然地说] [rate=1.0] [jobs=4]
# 参考音频：<项目>/ref.wav，没有就用 skill 的 assets/voice/ref.wav；超过 25 秒自动截前 25 秒（接口上限 30 秒）
# Key 放在 ~/.config/bailian/env（DASHSCOPE_API_KEY=...，权限 600），不要写进项目或记忆
# 输出和 clone_index.py 一样：<项目>/<out>/sNN.wav（多个种子时 sNN_<seed>.wav），48 kHz 单声道，首尾静音已切
import os, sys, json, time, base64, subprocess, urllib.request, urllib.error, tempfile
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

URL = "https://dashscope.aliyuncs.com/api/v1/services/audio/tts/SpeechSynthesizer"
urllib.request.install_opener(urllib.request.build_opener(urllib.request.ProxyHandler({})))   # 阿里云国内直连；走系统代理 7890 会 SSL EOF
SKILL = Path(__file__).resolve().parents[2]
P = Path(sys.argv[1]).resolve()
kv = dict(a.split("=", 1) for a in sys.argv[2:] if "=" in a)
KEY = os.environ.get("DASHSCOPE_API_KEY") or dict(l.strip().split("=", 1) for l in open(Path.home() / ".config/bailian/env") if "=" in l)["DASHSCOPE_API_KEY"]
REF = P / "ref.wav" if (P / "ref.wav").exists() else SKILL / "assets/voice/ref.wav"
L = json.loads((P / "lines.json").read_text())
out = P / kv.get("out", "voice_raw"); out.mkdir(exist_ok=True)
idx = [int(a) for a in sys.argv[2:] if a.isdigit()] or range(1, len(L) + 1)
seeds = [int(s) for s in kv.get("seeds", kv.get("seed", "42")).split(",")]
STYLE = kv.get("style", "像在讲旅行攻略一样自然地说")
af = "silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse"

tmp = Path(tempfile.mkdtemp()) / "ref.wav"                    # 参考音频统一成 24 kHz 单声道、最长 25 秒，控制体积
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(REF), "-t", "25", "-ar", "24000", "-ac", "1", str(tmp)], check=True)
REF64 = "data:audio/wav;base64," + base64.b64encode(tmp.read_bytes()).decode()


def one(n, sd):
    name = f"s{n:02d}.wav" if len(seeds) == 1 else f"s{n:02d}_{sd}.wav"; t = time.time()
    body = {"model": "qwen-audio-3.1-tts-next", "input": {"text_prompt": f"用 @voice1 的声音，{STYLE}：“{L[n - 1]}”", "references": [{"audio_data": REF64}],
            "format": "wav", "sample_rate": 48000, "channels": 1, "rate": float(kv.get("rate", 1.0)), "seed": sd}}
    for k in range(8):                                       # 偶发 SSL EOF（网络抖动），多重试几次
        try:
            req = urllib.request.Request(URL, data=json.dumps(body).encode(), headers={"Authorization": "Bearer " + KEY, "Content-Type": "application/json"})
            d = json.load(urllib.request.urlopen(req, timeout=300)); u = d["output"]["audio"]["url"]
            raw = out / (name + ".raw.wav"); raw.write_bytes(urllib.request.urlopen(u, timeout=120).read()); break
        except urllib.error.HTTPError as e:
            msg = e.read()[:300].decode(errors="ignore")
            if e.code in (400, 401, 403, 404): raise SystemExit(f"{name} ✗ {e.code} {msg}")
            print(f"{name} 重试 {e.code} {msg[:120]}", flush=True); time.sleep(3 * (k + 1))
        except Exception as e: print(f"{name} 重试 {e}", flush=True); time.sleep(3 * (k + 1))
    else: return print(f"{name} ✗ 失败", flush=True)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(raw), "-af", af, "-ar", "48000", "-ac", "1", str(out / name)], check=True); raw.unlink()
    d = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(out / name)], capture_output=True, text=True).stdout.strip()
    print(f"{name} {float(d):.1f}s（{time.time() - t:.0f}s）", flush=True)


with ThreadPoolExecutor(int(kv.get("jobs", 4))) as ex:
    for f in [ex.submit(one, n, sd) for n in idx for sd in seeds]: f.result()
