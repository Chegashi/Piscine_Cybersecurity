from __future__ import annotations

import base64
import hashlib
import hmac
import struct
import time
from pathlib import Path

from cryptography.fernet import Fernet, InvalidToken


FERNET_KEY = b"ZnRfb3RwX3NlY3JldF9rZXlfZm9yX2VuY3J5cHRpbyE="
KEY_FILE = Path("ft_otp.key")
MIN_HEX_KEY_LENGTH = 64
TIME_STEP_SECONDS = 30
OTP_DIGITS = 6
KEY_FILE_MODE = 0o600

_HEX_DIGITS = frozenset("0123456789abcdefABCDEF")
INVALID_HEX_KEY_ERROR = "key must be 64 hexadecimal characters."


class OtpError(Exception):
    """Raised for user-facing OTP errors."""


def normalize_hex_key(value: str) -> str:
    key = value.strip()

    if len(key) < MIN_HEX_KEY_LENGTH:
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
    token = Fernet(FERNET_KEY).encrypt(normalize_hex_key(hex_key).encode("ascii"))

    try:
        key_path = Path(path)
        key_path.write_bytes(token)
        key_path.chmod(KEY_FILE_MODE)
    except OSError as exc:
        raise OtpError(str(exc)) from exc


def load_encrypted_key(path: str | Path) -> bytes:
    try:
        token = Path(path).read_bytes().strip()
        decrypted = Fernet(FERNET_KEY).decrypt(token).decode("ascii")
        return bytes.fromhex(normalize_hex_key(decrypted))
    except OSError as exc:
        raise OtpError(str(exc)) from exc
    except (InvalidToken, UnicodeDecodeError, ValueError) as exc:
        raise OtpError("invalid encrypted key file") from exc


def hotp(key: bytes, counter: int) -> str:
    message = struct.pack(">Q", counter)
    digest = hmac.new(key, message, hashlib.sha1).digest()
    offset = digest[-1] & 0x0F
    binary_code = struct.unpack(">I", digest[offset : offset + 4])[0] & 0x7FFFFFFF
    return str(binary_code % (10**OTP_DIGITS)).zfill(OTP_DIGITS)


def totp(key: bytes, timestamp: int | None = None) -> str:
    if timestamp is None:
        timestamp = int(time.time())
    return hotp(key, timestamp // TIME_STEP_SECONDS)


def base32_secret(key: bytes) -> str:
    return base64.b32encode(key).decode("ascii").rstrip("=")
