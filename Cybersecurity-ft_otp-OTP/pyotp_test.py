#!/usr/bin/env python3

from __future__ import annotations

import base64
import sys
from pathlib import Path

# Allow importing ft_otp_core even if cryptography isn't installed
try:
    from cryptography.fernet import Fernet, InvalidToken  # type: ignore
except ModuleNotFoundError:
    import types

    mod = types.ModuleType("cryptography.fernet")

    class Fernet:  # minimal stand-in
        def __init__(self, key: bytes | str | None = None) -> None:
            pass

        def encrypt(self, data: bytes) -> bytes:
            return data

        def decrypt(self, token: bytes) -> bytes:
            return token

    InvalidToken = Exception
    import sys as _sys

    _sys.modules.setdefault("cryptography", types.ModuleType("cryptography"))
    _sys.modules["cryptography.fernet"] = mod
    mod.Fernet = Fernet
    mod.InvalidToken = InvalidToken

from ft_otp_core import hotp, totp
from datetime import datetime, timezone


RFC_HOTP_VECTORS = [
    (0, "755224"), (1, "287082"), (2, "359152"), (3, "969429"), (4, "338314"),
    (5, "254676"), (6, "287922"), (7, "162583"), (8, "399871"), (9, "520489"),
]

RFC_TOTP_VECTORS = [
    (59, "287082"), (1111111109, "081804"), (1111111111, "050471"),
    (1234567890, "005924"), (2000000000, "279037"), (20000000000, "353130"),
]

SECRET = b"12345678901234567890"


def check_vectors(name: str, vectors: list[tuple[int, str]]) -> int:
    failures = 0
    generator = hotp if name == "hotp" else totp
    for value, expected in vectors:
        got = generator(SECRET, value)
        if got != expected:
            print(f"[FAIL] {name}({value}) = {got}, expected {expected}")
            failures += 1
    return failures


def compare_one_key(hex_key: str) -> int:
    import shutil
    import subprocess
    
    try:
        raw = bytes.fromhex(hex_key)
        b32 = base64.b32encode(raw).decode()
    except ValueError:
        print("Error: invalid hex key")
        return 1

    have_pyotp = False
    try:
        import pyotp
        have_pyotp = True
    except ImportError:
        pass

    have_oathtool = shutil.which("oathtool") is not None

    # ft_otp
    ft_code = totp(raw)

    # pyotp
    if have_pyotp:
        py_code = pyotp.TOTP(b32).now()
    else:
        py_code = "(missing)"

    # oathtool
    if have_oathtool:
        now_arg = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')
        proc = subprocess.run(['oathtool', '--totp', '-b', '--now=' + now_arg, b32],
                              capture_output=True, text=True, check=False)
        oat_code = proc.stdout.strip() or "(error)"
    else:
        oat_code = "(missing)"

    print(f"{hex_key} | {b32} | {ft_code} | {py_code} | {oat_code}")
    return 0


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: python3 pyotp_test.py <mode|hex_key>")
        print("  mode: hotp, totp, or all (for RFC vector tests)")
        print("  hex_key: 64-char hex string (for single key comparison)")
        return 1

    arg = sys.argv[1].strip()

    # RFC vector test modes
    if arg in ("hotp", "totp", "all"):
        failures = 0
        if arg in ("hotp", "all"):
            failures += check_vectors("hotp", RFC_HOTP_VECTORS)
        if arg in ("totp", "all"):
            failures += check_vectors("totp", RFC_TOTP_VECTORS)
        return 1 if failures else 0

    # Single key comparison mode
    return compare_one_key(arg)


if __name__ == "__main__":
    raise SystemExit(main())
