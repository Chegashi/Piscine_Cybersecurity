#!/usr/bin/env python3

from __future__ import annotations

import sys

from ft_otp_core import (
    KEY_FILE,
    OtpError,
    load_encrypted_key,
    load_plain_hex_key,
    save_encrypted_key,
    totp,
)


GENERATE_FLAG = "-g"
OTP_FLAG = "-k"
VALID_FLAGS = (GENERATE_FLAG, OTP_FLAG)
USAGE = f"Usage: ./ft_otp {GENERATE_FLAG} <file> | {OTP_FLAG} <key_file>"


def parse_args(args: list[str]) -> tuple[str, str]:
    if len(args) != 2:
        raise OtpError(USAGE)

    flag, path = args

    if flag not in VALID_FLAGS:
        raise OtpError("invalid flag")

    return flag, path


def save_key_from_file(path: str) -> None:
    hex_key = load_plain_hex_key(path)
    save_encrypted_key(hex_key, KEY_FILE)
    print(f"Key was successfully saved in {KEY_FILE}.")


def print_otp_from_key_file(path: str) -> None:
    key = load_encrypted_key(path)
    print(totp(key))


def print_error(error: OtpError) -> None:
    message = str(error)

    if message == USAGE:
        print(message, file=sys.stderr)
    else:
        print(f"./ft_otp: error: {message}", file=sys.stderr)


def main(args: list[str] | None = None) -> int:
    if args is None:
        args = sys.argv[1:]

    try:
        flag, path = parse_args(args)

        if flag == GENERATE_FLAG:
            save_key_from_file(path)
        else:
            print_otp_from_key_file(path)

        return 0
    except OtpError as exc:
        print_error(exc)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
