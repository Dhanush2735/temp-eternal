#!/usr/bin/env python3
"""Tiny Source RCON client for the local Eternal Engine test server (turn 235).

Usage: python3 worldfill/rcon.py 'ee check all' [more commands...]
Talks to 127.0.0.1:25575 with the password from server.properties (eetest).
"""
import socket
import struct
import sys

HOST, PORT, PW = "127.0.0.1", 25575, "eetest"


def packet(req_id, ptype, body):
    payload = struct.pack("<ii", req_id, ptype) + body.encode() + b"\x00\x00"
    return struct.pack("<i", len(payload)) + payload


def recv(sock):
    data = b""
    while len(data) < 4:
        chunk = sock.recv(4096)
        if not chunk:
            raise EOFError
        data += chunk
    (length,) = struct.unpack("<i", data[:4])
    while len(data) < 4 + length:
        chunk = sock.recv(4096)
        if not chunk:
            raise EOFError
        data += chunk
    req_id, ptype = struct.unpack("<ii", data[4:12])
    return req_id, ptype, data[12:4 + length - 2].decode("utf-8", "replace")


def main():
    commands = sys.argv[1:] or ["list"]
    sock = socket.create_connection((HOST, PORT), timeout=300)
    sock.sendall(packet(1, 3, PW))
    req_id, _, _ = recv(sock)
    if req_id == -1:
        print("RCON auth failed")
        return 1
    for cmd in commands:
        sock.sendall(packet(2, 2, cmd))
        _, _, text = recv(sock)
        print(f"> {cmd}")
        print(text if text else "(no output)")
    sock.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
