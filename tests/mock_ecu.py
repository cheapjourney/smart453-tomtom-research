#!/usr/bin/env python3
"""Mock ECU + adapter for offline tests of tools/write_config.py.

Speaks the same line protocol an ELM327/STN adapter uses behind a PTY and
answers like the MFD: identity, 6C1C read, 6C1C write. Behaviour is selectable
so every failure path of the write tool can be exercised without a car.

Behaviours:
  positive               identity ok, 0x38 -> write -> 0x78
  nrc                    write answered with 7F 2E 22
  nrc_12                 write answered with 7F 2E 12 (Discussion #1027)
  no_answer_identity     no response to 22 F1 87
  no_answer_readback     write accepted, read-back silent
  disconnect_after_write socket closed right after the write answer
  wrong_identity         22 F1 87 returns a different part number
  current_3a             current value is 0x3A instead of 0x38
  readback_mismatch      write answered 6E 6C 1C, read-back still 0x38
  low_voltage            ATRV reports 11.8 V
  session_ok             10 C0 answered with 50 C0
  session_nrc            10 C0 answered with 7F 10 22
  session_wrong          10 C0 answered with 50 81
  session_ok_write_7f   10 C0 ok, write answered with 7F 2E 7F
  (default)              10 C0 stays silent - suppressPosRspMsgIndicationBit
"""
from __future__ import annotations

import socket
import sys
import threading
import time

IDENT_OK = "62 F1 87 32 35 39 31 35 36 32 34 34 52"
IDENT_WRONG = "62 F1 87 31 31 31 31 31 31 31 31 31 52"


class MockEcu:
    def __init__(self, behavior: str = "positive"):
        self.behavior = behavior
        self.writes = 0
        self.sessions: list[str] = []
        self.commands: list[str] = []
        self._srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._srv.bind(("127.0.0.1", 0))
        self.port = self._srv.getsockname()[1]
        self._srv.listen(1)
        self._srv.settimeout(10)
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._run, daemon=True)

    # -- lifecycle ---------------------------------------------------------
    def start(self):
        self._thread.start()
        return self

    def stop(self):
        self._stop.set()
        try:
            self._srv.close()
        except OSError:
            pass

    # -- protocol ----------------------------------------------------------
    def _answer(self, cmd: str) -> bytes | None:
        up = cmd.upper()
        self.commands.append(up)
        if up in ("ATZ", "ATI"):
            return b"ELM327 v1.5\r\r>"
        if up == "AT@1":
            return b"OBD SOLUTIONS LLC\r\r>"
        if up == "STI":
            return b"STN2255 v5.10.3\r\r>"
        if up == "ATRV":
            volts = "11.8" if self.behavior == "low_voltage" else "12.6"
            return f"{volts}V\r\r>".encode()
        if up.startswith("22F187") or up.startswith("22 F1 87"):
            if self.behavior == "no_answer_identity":
                return b""
            ident = IDENT_WRONG if self.behavior == "wrong_identity" else IDENT_OK
            return (ident + "\r\r>").encode()
        if up.startswith("226C1C") or up.startswith("22 6C 1C"):
            if self.behavior == "no_answer_readback" and self.writes > 0:
                return b""
            if self.writes > 0:
                val = 0x38 if self.behavior == "readback_mismatch" else 0x78
                return ("62 6C 1C %02X\r\r>" % val).encode()
            start = 0x3A if self.behavior == "current_3a" else 0x38
            return ("62 6C 1C %02X\r\r>" % start).encode()
        if up.startswith("10"):
            self.sessions.append(up)
            if up == "10C0":
                if self.behavior in ("session_ok", "session_ok_write_7f"):
                    return b"50 C0\r\r>"
                if self.behavior == "session_nrc":
                    return b"7F 10 22\r\r>"
                if self.behavior == "session_wrong":
                    return b"50 81\r\r>"
            return b""      # suppress bit: keine positive Antwort
        if up.startswith("2E6C1C") or up.startswith("2E 6C 1C"):
            self.writes += 1
            if self.behavior == "nrc":
                return b"7F 2E 22\r\r>"
            if self.behavior == "session_ok_write_7f":
                return b"7F 2E 7F\r\r>"
            if self.behavior == "nrc_12":
                return b"7F 2E 12\r\r>"
            return b"6E 6C 1C\r\r>"
        return b"OK\r\r>"

    def _run(self):
        try:
            conn, _ = self._srv.accept()
        except (OSError, socket.timeout):
            return
        conn.settimeout(0.5)
        buf = b""
        try:
            self._serve(conn)
        finally:
            try:
                conn.close()
            except OSError:
                pass

    def _serve(self, conn):
        buf = b""
        while not self._stop.is_set():
            try:
                chunk = conn.recv(4096)
            except socket.timeout:
                continue
            except OSError:
                return
            if not chunk:
                return
            buf += chunk
            while b"\r" in buf:
                line, buf = buf.split(b"\r", 1)
                cmd = line.decode(errors="replace").strip()
                if not cmd:
                    continue
                reply = self._answer(cmd)
                if reply is None:
                    continue
                if reply:
                    try:
                        conn.sendall(reply)
                    except OSError:
                        return
                if self.behavior == "disconnect_after_write" and cmd.upper().startswith("2E6C1C"):
                    time.sleep(0.1)
                    try:
                        conn.close()
                    except OSError:
                        pass
                    return

if __name__ == "__main__":
    behavior = sys.argv[1] if len(sys.argv) > 1 else "positive"
    m = MockEcu(behavior).start()
    print(f"mock '{behavior}' on 127.0.0.1:{m.port}  (Ctrl-C to stop)")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        m.stop()
