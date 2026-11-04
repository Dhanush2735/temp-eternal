#!/usr/bin/env python3
"""A minimal Minecraft RCON client, for driving the headless test server.

The sandbox has no mcrcon, and the dedicated server does not read a FIFO as stdin through
Gradle's run task, so the commands go over the protocol the server offers for exactly this.

    python3 rcon.py "ee status"
    python3 rcon.py --file commands.txt      one command a line, prints each answer
"""
import os
import select
import socket
import struct
import sys
import time

HOST, PORT = "127.0.0.1", 25575
# The password is whatever the server under test was started with. It is read from the environment
# so a test can point the client at another server without editing the file (board 12).
PASSWORD = os.environ.get("EE_RCON_PASSWORD", "eecheck")


class Rcon:
    def __init__(self, host=HOST, port=PORT, password=PASSWORD, timeout=180.0):
        self.sock = socket.create_connection((host, port), timeout=timeout)
        self.sock.settimeout(timeout)
        self.rid = 0
        self._send(3, password)
        rid, kind, _body = self._recv()
        # Minecraft signals a refused password by answering with request id -1. The first version of
        # this client looked at the packet TYPE only, which is 2 either way, so a wrong password
        # looked like a working connection whose every command answered with an empty string - 212
        # commands "ANSWERED" and not one of them had run (board 12, 2026-10-23).
        if rid == -1:
            raise SystemExit("rcon: wrong password")
        if kind != 2:
            raise SystemExit("rcon: auth failed (packet type %r)" % (kind,))
        # Prove the link carries answers before anything is recorded against it.
        self._send(2, "list")
        _rid, _kind, hello = self._recv()
        if not hello.strip():
            raise SystemExit("rcon: authenticated but the server answers nothing "
                             "(is the password right?)")

    def _send(self, kind, body):
        self.rid += 1
        payload = struct.pack("<ii", self.rid, kind) + body.encode("utf-8") + b"\x00\x00"
        self.sock.sendall(struct.pack("<i", len(payload)) + payload)
        return self.rid

    def _recv(self):
        raw = self._recv_exactly(4)
        (length,) = struct.unpack("<i", raw)
        data = self._recv_exactly(length)
        rid, kind = struct.unpack("<ii", data[:8])
        body = data[8:-2].decode("utf-8", "replace")
        return rid, kind, body

    def _recv_exactly(self, n):
        buf = b""
        while len(buf) < n:
            chunk = self.sock.recv(n - len(buf))
            if not chunk:
                raise SystemExit("rcon: connection closed")
            buf += chunk
        return buf

    def command(self, cmd):
        """One command, the whole answer.

        A long answer (the codex prints thousands of characters) arrives as SEVERAL packets: the
        first version of this client read one packet and left the rest in the socket, which put the
        stream out of step and ended the run at /ee codex chronicle. Read until the socket is quiet.
        """
        self._send(2, cmd)
        parts = []
        while True:
            try:
                ready, _, _ = select.select([self.sock], [], [], 0.35)
            except (OSError, ValueError):
                break
            if not ready and parts:
                break
            _rid, _kind, body = self._recv()
            parts.append(body)
            if not ready and not parts:
                break
        return "".join(parts)

    def close(self):
        self.sock.close()


def main(argv):
    commands = []
    if len(argv) >= 2 and argv[0] == "--file":
        with open(argv[1], encoding="utf-8") as fh:
            commands = [ln.strip() for ln in fh if ln.strip() and not ln.startswith("#")]
    else:
        commands = list(argv)
    rc = Rcon()
    bad = 0
    for cmd in commands:
        started = time.time()
        try:
            answer = rc.command(cmd)
        except SystemExit:
            raise
        except Exception as exc:                      # a command that kills the answer
            answer = "*** %s: %s" % (type(exc).__name__, exc)
            bad += 1
        took = (time.time() - started) * 1000.0
        print(">>> /%s   (%.0f ms)" % (cmd, took))
        print((answer or "(no answer)").rstrip())
        print()
    rc.close()
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
