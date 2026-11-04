#!/usr/bin/env bash
# The probes that run on a plain JDK: the pure-Java registers, with no Minecraft runtime.
# (The others need tools/run_test_server.sh's classpath and are swept when that has run.)
cd /home/user
LIST="probe_step42c.sh probe_step42d.sh probe_step42e.sh probe_step43.sh probe_step43b.sh probe_step43c.sh probe_step43d.sh probe_step44.sh probe_step44c.sh probe_step44d.sh probe_step44e.sh probe_step44f.sh \
probe_step44g.sh probe_step44h.sh probe_step45a.sh probe_step45b.sh probe_step45c.sh probe_step45d.sh probe_step45e.sh probe_step46a.sh probe_step46b.sh probe_step46c.sh probe_step46d.sh probe_step46e.sh \
probe_step46f.sh probe_step46g.sh probe_step47a.sh probe_step47b.sh probe_step47c.sh probe_step47d.sh probe_step47e.sh probe_step47f.sh probe_step47g.sh probe_step47h.sh probe_step47i.sh probe_step47j.sh \
probe_step47k.sh probe_step47l.sh probe_step47m.sh probe_step48a.sh probe_step48b.sh probe_step48c.sh probe_step48d.sh probe_step48e.sh probe_step49a.sh probe_step49b.sh probe_step49c.sh probe_step49d.sh \
probe_step49e.sh probe_step50a.sh probe_step50b.sh probe_step50c.sh probe_step50d.sh probe_step50e.sh probe_step51a.sh probe_step51b.sh probe_step51c.sh probe_step51d.sh probe_step51e.sh probe_step52a.sh \
probe_step52b.sh probe_step52c.sh probe_step52d.sh probe_step52e.sh probe_step52f.sh probe_step53a.sh probe_step53b.sh probe_step53c.sh probe_step53d.sh probe_step53e.sh probe_step54a.sh \
probe_step54b.sh probe_step54c.sh probe_step54d.sh probe_step54e.sh probe_step55a.sh probe_step55b.sh probe_step55c.sh probe_step55d.sh probe_step56a.sh probe_step56b.sh probe_step56c.sh probe_step56d.sh \
probe_step57a.sh probe_step57b.sh probe_step57c.sh probe_step57d.sh probe_step57e.sh probe_step57f.sh probe_step58d.sh probe_step59d.sh probe_step60d.sh probe_step61d.sh probe_span.sh probe_terra.sh probe_tiles.sh probe_sky.sh probe_trade.sh probe_towns.sh \
probe_moneyworld.sh probe_technology.sh probe_culture.sh"
rm -f /tmp/sweep.txt
for s in $LIST; do
  f="worldfill/$s"
  [ -f "$f" ] || { printf '%-34s MISSING\n' "$s" | tee -a /tmp/sweep.txt; continue; }
  out=$(timeout 900 bash "$f" 2>&1)
  line=$(printf '%s\n' "$out" | grep -E "== .*(checks|failed)" | tail -1)
  [ -z "$line" ] && line=$(printf '%s\n' "$out" | tail -1)
  printf '%-30s %s\n' "$s" "$line" | tee -a /tmp/sweep.txt
done
echo "----- green: $(grep -c ' 0 failed' /tmp/sweep.txt) of $(wc -l < /tmp/sweep.txt)"
