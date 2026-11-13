#!/bin/zsh
# 下载三款 OFL 字体到 <工程>/fonts：./fetch_fonts.sh <工程目录>
set -e; F="${1:?用法 fetch_fonts.sh <工程目录>}/fonts"; mkdir -p "$F"; B=https://raw.githubusercontent.com/google/fonts/main/ofl
for p in mashanzheng/MaShanZheng-Regular.ttf zcoolkuaile/ZCOOLKuaiLe-Regular.ttf zcoolqingkehuangyou/ZCOOLQingKeHuangYou-Regular.ttf; do
  f="$F/${p:t}"; [ -s "$f" ] || curl -fsSL --max-time 120 -o "$f" "$B/$p"; echo "✓ ${p:t}"
done
