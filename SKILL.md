---
name: yunnan-travel-video
description: "云南旅行系列短视频的执行包：一期讲一个目的地（大理、丽江、昆明、西双版纳、腾冲、香格里拉、全省选线），3 分钟内的竖屏攻略，把目的地分成三块，配地图路线、实拍图、3D 地形和行程卡。包里有选题队列、完整工作流、写稿规则、从大理成片抽出来的工程模板和大理全套样例。当用户说「做云南系列下一期」「做丽江攻略视频」「继续云南旅行视频」「城市游玩攻略视频」「按大理那套再做一个城市」时使用。地图引擎用 map-motion，3D 用 map-3d。"
---
# 云南旅行系列视频 yunnan-travel-video
一期 = 一个目的地的 3 分钟内竖屏攻略（1080×1920）。首期大理已成片，是所有后续期数的样板。
## 接手先读
| 顺序 | 文件 | 回答什么 |
|---|---|---|
| 1 | `references/选题队列.md` | 一共几期、做到哪了、下一期是谁 |
| 2 | `references/写稿规则.md` | 口播怎么写、哪些写法禁用、画面要求。和工作流全文冲突时以它为准 |
| 3 | `references/工作流全文.md` | 每一步的细则、质检标准、踩过的坑（第 13、14 节） |
| 4 | `examples/dali/` | 一期做完长什么样：大纲、口播稿、路线卡、事实清单、素材来源 |
## 三个确认点（不能跳，不能替用户确认）
| 确认 | 你交什么 | 用户说了什么才能往下走 |
|---|---|---|
| ① | 观众 + 空间模型（三块怎么分）+ 大纲 | 「可以，写稿」 |
| ② | 完整口播稿 + 路线卡 + 事实来源清单 + 不确定项 | 「可以，开始做」 |
| ③ | 发布预览：标题、正文、话题、封面、要发的平台 | 明确同意发布 |
确认 ② 之后不改稿。非改不可时先说原因。没有确认 ③ 不上传、不发布。
## 环境
| 需要 | 说明 |
|---|---|
| map-motion skill | `~/.claude/skills/map-motion/`（仓库 `zephyrwang6/myskill`），提供 `scripts/compile.py`、`render.py`、`audio.py`、`amap.py` 和 `map-3d/` |
| 高德 Web 服务 key | 环境变量 `AMAP_KEY`，或 `~/.config/map-motion/amap_key` |
| 百炼配音 key | 环境变量 `DASHSCOPE_API_KEY`，或 `~/.config/bailian/env`。请求不走代理 |
| 配音和听写脚本 | 已带在包里：`scripts/voice/clone_bailian.py`（百炼克隆音色）、`asrcheck.py`（逐句听写核对，需要 mlx-audio、numpy、pypinyin 和本地 Whisper 模型，路径用环境变量 `WHISPER_MODEL` 指定） |
| 参考音色 | 工程里的 `ref.wav`。本机可从 `~/Movies/dali-guide/ref.wav` 复制，不进仓库 |
| 背景音乐 | 没带在包里（Mixkit 授权不允许把音乐文件单独再分发）。`build.py` 的 `BGM` 指向本机 space-explainer-video 的 `assets/bgm/smile.mp3`；换机器时自己从 mixkit.co 下一首免费曲子，改 `BGM` 路径。音量 0.07 |
| 音效 | 大理成片只有配音和背景音乐，没有音效。map-motion 的 `audio.py` 自带嗖、啵、叮、快门、脚步五种合成音效，往 `build.py` 里 `audio.mix` 的事件表加 `{"t": 秒, "type": "whoosh"}` 这类条目就能用，但还没在这套模板里接过，接了要重新听一遍响度 |
| 其他 | uv、ffmpeg、Chromium（playwright） |
任何 key 都不打印、不写进文件、不放命令行参数、不进日志。缺 key 就停下来告诉用户缺哪个变量名。
## 流程
### 1. 选期数，做空间模型和大纲（到确认 ①）
1. 从选题队列取第一个没成片的期数。丽江已有草案：`examples/lijiang/大纲草案.md`，先把里面「必须核实」的几项查了再交。
2. 用 `amap.py` 的 `geocode` 和 `route` 查坐标和真实车程（参考 `template/data/drive.py`）。不用直线距离估时间。
3. 把目的地分成三块，配色固定：橙 `#F28C28`、蓝 `#2F80ED`、绿 `#27AE60`。
4. 交「观众 + 空间模型 + 大纲」，等确认 ①。
### 2. 调研、路线卡、口播稿（到确认 ②）
1. 事实逐条查来源，官方渠道优先，写进 `research/facts.md`，记核实日期。票价、预约、开放时间、索道检修、花期和候鸟季都算时效信息。
2. 每一块写一张路线卡：入口、顺序、每站停多久、怎么走、出口。
3. 按 `references/写稿规则.md` 写口播，20–26 句，不超过 950 字，存成 `lines.json`（一句一个字符串）。
4. 交稿，等确认 ②。
### 3. 建工程
```sh
~/.claude/skills/yunnan-travel-video/scripts/new_city.sh lijiang
```
生成 `~/Movies/lijiang-guide`，带模板代码、图标和字体。`city.example.json`、`lines.example.json` 是大理的，照着写本期的 `city.json` 和 `lines.json`。
### 4. 配音和听写核对
1. 建 `tts_alt/lines.json`：和 `lines.json` 一样，只把容易读错的字换成同音字（大理把「磻溪」写成「盘溪」）。把 `ref.wav` 放进 `tts_alt/`。
2. 每句出两版：`python3 ~/.claude/skills/yunnan-travel-video/scripts/voice/clone_bailian.py <工程>/tts_alt seeds=42,7`。
3. 用 `asrcheck.py <工程>/lines.json <工程>/tts_alt/voice_raw` 逐句听写，每句挑读得准的一版，复制成 `voice/sNN.wav`。
4. 配音总长超过 170 秒就回去删稿（要先跟用户说），不靠加速解决。
### 5. 平面地图
1. 改 `specs_city.py` 里的大理专用部分：`POI` 补充点、`BASIN` 总览视角、`ZONE_RING` 三块的范围、`ZLAB_AT` 片区名位置、`M[...]` 每个镜头。镜头时长由配音时长算（`need()`），所以先配音再做地图。
2. `uv run python specs_city.py` 写出 `m_*.json`，再 `./render_q.sh m_open m_p5 ...` 渲染到 `seg/`。
3. 片区范围沿真实的湖岸、河道、山脚画，别手估经纬度。画面里不能出现高德字样（`attribution` 保持 `False`）。
### 6. 3D 地形镜头（每期至少一段）
放在地形起伏最大的那一块，比如丽江的玉龙雪山。读 `~/.claude/skills/map-motion/map-3d/SKILL.md`，用「自由机位 `path`」或「路线 `track`」写 spec，尺寸竖屏。先出静帧检查地名有没有出画，再整段渲染（慢，放后台）。渲好的 mp4 放进 `seg/`，在 `build.py` 的 `EDIT` 表里当一个 `map` 段用。
注意：大理那期没用 3D，这条接法还没在模板里实际跑过。第一次用时先确认分辨率 1080×1920、30 帧，并且段长不短于对应配音。
### 7. 实拍图
1. `commons_search.py` 搜 Wikimedia Commons，`fetch_commons.py` 下载并记录作者和许可到 `src/commons.json`。
2. 只用 CC0、公有领域、CC BY、CC BY-SA。每张图打开看一眼，确认拍的就是口播说的那个地方。确认不了的不加地名字幕，或者干脆不用。
3. `python audit.py` 生成 `footage_audit.md` 和 `pub/素材来源.txt`。
### 8. 合成
1. 改 `build.py` 顶部的大理专用表：`OUT_NAME`、`EDIT`（每句用哪种段：`map` 整段地图、`mix` 地图开头加关键词对齐的照片、`card` 模糊底图加图标清单）、`CHAPTERS` 章节条、`CHECK` 图标清单、`WATERMARK` 巨型地名、两张行程卡。
2. `uv run -q --offline --with pillow python build.py`。
3. 不用冻结帧补时长。
### 9. 质检（全过才算成片）
| 项 | 标准 |
|---|---|
| 时长 | 不超过 180 秒 |
| 规格 | 1080×1920，30 帧 |
| 响度 | -16 LUFS 上下 1 以内（`ebur128`，别加 `-v error`，否则看不到读数） |
| 冻结 | `freezedetect=n=0.001:d=1.2` 结果为 0 段 |
| 画面 | 每 6 秒抽一帧拼成联系表，逐格看字幕遮挡、地名、图文是否对应 |
| 字幕 | 和确认过的口播稿逐字一致 |
结果追加写进工程的 `STATUS.md`（只追加）。
### 10. 封面和交付
1. `cover_pub.py` 出 3:4、9:16、4:3 三张封面。封面字体没有「·」，分隔用「｜」。
2. 成片、封面、制作稿复制到用户笔记库 `3 content/geo-video/`；发布包放 `~/Desktop/待发/<片名>/`，含 `文案.md`、`路线卡.md`、`素材来源.txt`、`发布记录.json`（成片 sha256、时长、平台、`confirmed: false`、发布前要再核的事实）。
3. 改选题队列状态，往笔记库 `5 review/daily_log.jsonl` 追加一行。
4. 给用户发布预览，等确认 ③。
## 硬规则
- 三个确认点不跳过，不自动发布。
- key 不落地（见「环境」）。
- JSONL 和 `STATUS.md` 只追加。
- 图和地点必须对得上，授权必须能说清。
- 不直接复制 `~/Movies/dali-guide` 整个目录，用 `new_city.sh`。
- 用户笔记库顶层只有 7 个目录，视频相关的都放 `3 content/geo-video/`，不新建顶层目录。
- 文字输出不用破折号，不用「不是 X，是 Y」句式，Markdown 段落之间不留空行。
## 这个包目前的局限
- `build.py` 和 `specs_city.py` 是大理的原样代码，镜头表和剪辑表写死了大理的内容，每期要手改，还做不到「一份 `city.json` 自动出全片」。做完第二期后应把两期共用的部分抽成通用模板。
- 3D 镜头和音效都没有在这套模板里跑通过。
- 背景音乐和参考音色不在包里，换机器要自己准备。
- 只有大理一期验证过整条流程。
## 目录
| 路径 | 内容 |
|---|---|
| `references/` | 选题队列、写稿规则、工作流全文 |
| `template/` | 工程代码、图标（Noto Emoji，Apache 2.0）、大理的 `city.json` 和 `lines.json` |
| `scripts/` | `new_city.sh` 建工程，`fetch_fonts.sh` 下载三款 OFL 字体，`voice/` 配音和听写脚本 |
| `examples/dali/` | 大理全套文字产物 |
| `examples/lijiang/` | 丽江大纲草案、坐标和车程 |
