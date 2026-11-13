#!/bin/zsh
# 依次渲染地图段：./render_q.sh m_open m_p5 ...（名字来自 specs_city.py 写出的 m_*.json）
cd "$(dirname "$0")"; mkdir -p seg; MM=~/.claude/skills/map-motion/scripts
for k in "$@"; do
  uv run -q --offline --with certifi --with pillow python $MM/compile.py $k.json --out $k.timeline.json > seg/$k.log 2>&1 || { echo "✗ compile $k"; continue; }
  MM_GL=metal uv run -q --offline --with playwright==1.63.0 --with certifi --with pillow python $MM/render.py $k.timeline.json --out seg/$k.mp4 >> seg/$k.log 2>&1 && echo "✓ $k" || echo "✗ render $k"
done
