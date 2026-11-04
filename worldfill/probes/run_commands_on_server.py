#!/usr/bin/env python3
"""Run every line of ee_command_list.txt on the HEADLESS server through RCON (gate G5, L4).

Different from CommandSurfaceProbe (board 9): that one drove Minecraft's dispatcher with no world at
all. This one has a real dedicated server with a level, a save, the simulation running and the
mod's own data installed - so commands that need the world can be judged on their success path,
which is exactly what the test plan's L4 line asks for ("212 commands parse on a headless server").

    python3 run_commands_on_server.py [list] [report.tsv]

A command that returns an error sentence is recorded with it; a command that times out is recorded
as TIMEOUT and the run continues.
"""
import sys
import time

sys.path.insert(0, "/home/user/worldfill/probes")
from rcon import Rcon  # noqa: E402

LIST = sys.argv[1] if len(sys.argv) > 1 else "/home/user/eternal/ee_command_list.txt"
REPORT = sys.argv[2] if len(sys.argv) > 2 else "/home/user/testrun/server_commands.tsv"

with open(LIST, encoding="utf-8") as fh:
    lines = [ln.strip() for ln in fh if ln.strip() and not ln.strip().startswith("#")]

rc = Rcon(timeout=240.0)
rows = []
for line in lines:
    cmd = line[1:] if line.startswith("/") else line
    started = time.time()
    try:
        answer = rc.command(cmd)
        verdict = "ANSWERED"
    except Exception as exc:
        answer = "%s: %s" % (type(exc).__name__, exc)
        verdict = "FAILED"
        # a dropped connection means the server died on this command: reconnect and carry on
        try:
            rc.close()
        except Exception:
            pass
        time.sleep(5)
        rc = Rcon(timeout=240.0)
    took = (time.time() - started) * 1000.0
    answer = (answer or "").replace("\t", " ").replace("\r", " ").replace("\n", " / ").strip()
    rows.append((cmd, verdict, "%.0f" % took, answer[:400]))
    print("%-7s %-58s %6.0f ms  %s" % (verdict, "/" + cmd, took, answer[:90]))

rc.close()
with open(REPORT, "w", encoding="utf-8") as fh:
    fh.write("command\tverdict\tms\tanswer\n")
    for r in rows:
        fh.write("\t".join(r) + "\n")
print("\n%d commands on the live server; report: %s" % (len(rows), REPORT))
