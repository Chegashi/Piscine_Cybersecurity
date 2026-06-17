from __future__ import annotations

import hashlib
import hmac
import struct
import time
from pathlib import Path

from cryptography.fernet import Fernet, InvalidToken


FERNET_KEY = b"ZnRfb3RwX3NlY3JldF9rZXlfZm9yX2VuY3J5cHRpbyE="
KEY_FILE = Path("ft_otp.key")

_HEX_DIGITS = frozenset("0123456789abcdefABCDEF")
INVALID_HEX_KEY_ERROR = "key must be 64 hexadecimal characters."


class OtpError(Exception):
    """Raised for user-facing OTP errors."""


def normalize_hex_key(value: str) -> str:
    key = value.strip()

    if len(key) < 64:
        raise OtpError(INVALID_HEX_KEY_ERROR)
    if len(key) % 2 != 0:
        raise OtpError("key length must be an even number of hexadecimal characters")
    if any(char not in _HEX_DIGITS for char in key):
        raise OtpError(INVALID_HEX_KEY_ERROR)
    return key.lower()


def load_plain_hex_key(path: str | Path) -> str:
    try:
        return normalize_hex_key(Path(path).read_text(encoding="ascii"))
    except UnicodeDecodeError as exc:
        raise OtpError("key file must contain ASCII hexadecimal text") from exc
    except OSError as exc:
        raise OtpError(str(exc)) from exc


def save_encrypted_key(hex_key: str, path: str | Path = KEY_FILE) -> None:
    normalized_key = normalize_hex_key(hex_key).encode("ascii")
    token = Fernet(FERNET_KEY).encrypt(normalized_key)

    try:
        key_path = Path(path)
        key_path.write_bytes(token)
        key_path.chmod(0o600)
    except OSError as exc:
        raise OtpError(str(exc)) from exc


def load_encrypted_key(path: str | Path) -> bytes:
    try:
        token = Path(path).read_bytes().strip()
        decrypted = Fernet(FERNET_KEY).decrypt(token).decode("ascii")
        hex_key = normalize_hex_key(decrypted)
        return bytes.fromhex(hex_key)
    except OSError as exc:
        raise OtpError(str(exc)) from exc
    except (InvalidToken, UnicodeDecodeError, ValueError) as exc:
        raise OtpError("invalid encrypted key file") from exc


def hotp(key: bytes, counter: int) -> str:
    counter_bytes = struct.pack(">Q", counter)
    digest = hmac.new(key, counter_bytes, hashlib.sha1).digest()
    code = _dynamic_truncate(digest)
    return str(code % (10**6)).zfill(6)


def _dynamic_truncate(digest: bytes) -> int:
    """Extract the RFC 4226 31-bit code from an HMAC digest."""
    offset = digest[-1] & 0x0F
    four_bytes = digest[offset : offset + 4]
    return struct.unpack(">I", four_bytes)[0] & 0x7FFFFFFF


def totp(key: bytes, timestamp: int | None = None) -> str:
    if timestamp is None:
        timestamp = int(time.time())
    return hotp(key, timestamp // 30)
