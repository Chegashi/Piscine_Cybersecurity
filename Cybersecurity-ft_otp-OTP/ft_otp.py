#!/usr/bin/env python3

from __future__ import annotations

import base64
import sys

from ft_otp_core import (
    KEY_FILE,
    OtpError,
    load_encrypted_key,
    load_plain_hex_key,
    save_encrypted_key,
    totp,
)


USAGE = "Usage: ./ft_otp -g <file> | -k <key_file>"
SUCCESS_MESSAGE = "Key was successfully saved in ft_otp.key."
PRINT_OTP_B32 = False

def parse_args(args: list[str]) -> tuple[str, str]:
    if len(args) != 2:
        raise OtpError(USAGE)

    flag, path = args

    if flag not in ("-g", "-k"):
        raise OtpError("invalid flag")

    return flag, path


def main(args: list[str] | None = None) -> int:
    if args is None:
        args = sys.argv[1:]

    try:
        flag, path = parse_args(args)

        if flag == "-g":
            hex_key = load_plain_hex_key(path)
            save_encrypted_key(hex_key, KEY_FILE)
            print(SUCCESS_MESSAGE)

            if PRINT_OTP_B32:
                # Optional helper for authenticator import; never store this seed.
                b32 = base64.b32encode(bytes.fromhex(hex_key)).decode()
                print(b32)
        else:
            print(totp(load_encrypted_key(path)))

        return 0
    except OtpError as exc:
        message = str(exc)
        if message == USAGE:
            print(message, file=sys.stderr)
        else:
            print(f"./ft_otp: error: {message}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
