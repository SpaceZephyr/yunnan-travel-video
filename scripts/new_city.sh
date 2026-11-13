#!/bin/zsh
# 从模板建一个新城市工程：./new_city.sh lijiang   → ~/Movies/lijiang-guide
set -e; N="${1:?用法 new_city.sh <城市拼音>}"; S="$(cd "$(dirname "$0")/.." && pwd)"; P=~/Movies/$N-guide
[ -e "$P/build.py" ] && { echo "已存在 $P，不覆盖"; exit 1; }
mkdir -p $P/{voice,tts_alt,seg,src,norm,qc,pub,research,data}
cp -n $S/template/*.py $S/template/render_q.sh $P/; cp -Rn $S/template/icons $P/; cp -n $S/template/data/* $P/data/ 2>/dev/null || true
cp -n $S/template/city.json $P/city.example.json; cp -n $S/template/lines.json $P/lines.example.json
chmod +x $P/render_q.sh; "$S/scripts/fetch_fonts.sh" $P
echo "$(date '+%Y-%m-%d %H:%M') INIT from yunnan-travel-video template" >> $P/STATUS.md
echo "建好 $P。下一步：写 city.json 和 lines.json（参考 *.example.json），再改 specs_city.py 和 build.py 里的大理专用表。"
