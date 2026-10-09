#!/bin/bash
# one fetch worker per court; two passes to retry stragglers
set -u
S=$(cd "$(dirname "$0")/.." && pwd)
C="$S/scraper/collect.py"
for pass in 1 2; do
  python3 -I "$C" fetch "$S/data/pilot.db" "$S/data/raw" TPD >> "$S/data/fetch_TPD.log" 2>&1 &
  python3 -I "$C" fetch "$S/data/pilot.db" "$S/data/raw" PCD >> "$S/data/fetch_PCD.log" 2>&1 &
  python3 -I "$C" fetch "$S/data/pilot.db" "$S/data/raw" TYD >> "$S/data/fetch_TYD.log" 2>&1 &
  python3 -I "$C" fetch "$S/data/pilot_b.db" "$S/data/raw" TCD >> "$S/data/fetch_TCD.log" 2>&1 &
  python3 -I "$C" fetch "$S/data/pilot_b.db" "$S/data/raw" TND >> "$S/data/fetch_TND.log" 2>&1 &
  python3 -I "$C" fetch "$S/data/pilot_b.db" "$S/data/raw" KSD >> "$S/data/fetch_KSD.log" 2>&1 &
  wait
done
echo ALLDONE > "$S/data/ALLDONE"
