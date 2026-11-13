# yunnan-travel-video
云南旅行系列短视频的执行包。一期讲一个目的地，3 分钟内的竖屏攻略：把目的地分成三块，配地图路线、实拍图、3D 地形和行程卡。给 Claude Code、Codex 这类 Agent 直接执行用。
## 怎么用
```sh
git clone https://github.com/SpaceZephyr/yunnan-travel-video ~/.claude/skills/yunnan-travel-video
```
然后让 Agent 读 `SKILL.md`，从 `references/选题队列.md` 里取下一期开始做。
## 依赖
- 地图引擎 map-motion（含 map-3d）：<https://github.com/SpaceZephyr/myskill>
- 高德 Web 服务 key（`AMAP_KEY`）、阿里云百炼 key（`DASHSCOPE_API_KEY`）
- uv、ffmpeg、Chromium
- 自己准备：配音的参考音色 `ref.wav`、一首背景音乐
## 现状
只有大理一期完整跑通过。模板代码是大理工程的原样，每期要手改镜头表和剪辑表；3D 镜头和音效还没在模板里接通。详见 `SKILL.md` 末尾「目前的局限」。
## 素材授权
`template/icons/` 是 Noto Emoji（Apache 2.0）。字体由 `scripts/fetch_fonts.sh` 从 google/fonts 下载（OFL）。样例里引用的照片来自 Wikimedia Commons，作者和许可见 `examples/dali/素材来源.txt`，照片本身不在仓库里。
