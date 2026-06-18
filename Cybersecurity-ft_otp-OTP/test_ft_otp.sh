#!/bin/sh

PASS=0
FAIL=0

GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

BIN=./ft_otp
KEY_FILE=ft_otp.key
VECTOR_SCRIPT=pyotp_test.py
VECTOR_MODE=${1:-totp}
VALID_KEY_FILE=test_key.hex
BAD_KEY_FILE=test_bad.txt
MISSING_HEX_FILE=no_such_file.hex
MISSING_KEY_FILE=no_such.key
EXPECTED_KEY_MODE=0o600

COMMAND_OUTPUT=
COMMAND_STATUS=0

if [ -x venv/bin/python3 ]; then
    PYTHON=venv/bin/python3
else
    PYTHON=${PYTHON:-python3}
fi

# Test keys for key comparison
TEST_KEYS=(
    "000102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f"
    "1f1e1d1c1b1a191817161514131211100f0e0d0c0b0a09080706050403020100"
    "2a2b2c2d2e2f303132333435363738393a3b3c3d3e3f40414243444546474849"
    "9f8e7d6c5b4a392817261514131211100f0e0d0c0b0a09080706050403020100"
    "ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff"
    "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"
    "abcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcd"
    "00112233445566778899aabbccddeeff00112233445566778899aabbccddeeff"
    "deadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeef"
    "cafebabecafebabecafebabecafebabecafebabecafebabecafebabecafebabe"
    "1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"
)

pass() {
    printf "%b[PASS]%b %s\n" "$GREEN" "$NC" "$1"
    PASS=$((PASS + 1))
}

fail() {
    printf "%b[FAIL]%b %s\n" "$RED" "$NC" "$1"
    FAIL=$((FAIL + 1))
}

run_command() {
    COMMAND_OUTPUT=$("$@" 2>&1)
    COMMAND_STATUS=$?
}

random_hex_key() {
    "$PYTHON" -c "import os; print(os.urandom(32).hex())"
}

file_mode() {
    "$PYTHON" -c '
from pathlib import Path
import sys

print(oct(Path(sys.argv[1]).stat().st_mode & 0o777))
' "$1"
}

assert_output_contains() {
    expected=$1
    pass_message=$2
    fail_message=$3

    case "$COMMAND_OUTPUT" in
        *"$expected"*) pass "$pass_message" ;;
        *) fail "$fail_message" ;;
    esac
}

assert_six_digit_output() {
    pass_message=$1
    fail_message=$2

    case "$COMMAND_OUTPUT" in
        [0-9][0-9][0-9][0-9][0-9][0-9]) pass "$pass_message" ;;
        *) fail "$fail_message" ;;
    esac
}

assert_command_failed() {
    pass_message=$1
    fail_message=$2

    if [ "$COMMAND_STATUS" -ne 0 ]; then
        pass "$pass_message"
    else
        fail "$fail_message"
    fi
}

setup() {
    TEST_KEY=$(random_hex_key)
    printf "%s\n" "$TEST_KEY" > "$VALID_KEY_FILE"
    printf "NEVER GONNA GIVE YOU UP\n" > "$BAD_KEY_FILE"
}

cleanup() {
    rm -f "$VALID_KEY_FILE" "$BAD_KEY_FILE" "$KEY_FILE"
}

test_rejects_non_hex_key() {
    run_command "$BIN" -g "$BAD_KEY_FILE"
    assert_output_contains \
        "key must be 64 hexadecimal characters." \
        "-g rejects non-hex key" \
        "-g should reject non-hex key"
}

test_rejects_missing_hex_file() {
    run_command "$BIN" -g "$MISSING_HEX_FILE"
    assert_output_contains \
        "No such file" \
        "-g rejects missing file" \
        "-g should error on missing file"
}

test_saves_valid_key() {
    run_command "$BIN" -g "$VALID_KEY_FILE"
    if [ "$COMMAND_STATUS" -eq 0 ]; then
        pass "-g exits 0 on valid key"
    else
        fail "-g should exit 0 on valid key"
    fi
}

assert_command_succeeded() {
    pass_message=$1
    fail_message=$2

    if [ "$COMMAND_STATUS" -eq 0 ]; then
        pass "$pass_message"
    else
        fail "$fail_message"
    fi
}

test_creates_key_file() {
    if [ -f "$KEY_FILE" ]; then
        pass "-g creates ft_otp.key"
    else
        fail "-g did not create ft_otp.key"
    fi
}

test_key_file_is_encrypted() {
    content=$(cat "$KEY_FILE")

    if [ "$content" != "$TEST_KEY" ]; then
        pass "ft_otp.key is not plaintext"
    else
        fail "ft_otp.key should be encrypted"
    fi
}

test_key_file_permissions() {
    mode=$(file_mode "$KEY_FILE")

    if [ "$mode" = "$EXPECTED_KEY_MODE" ]; then
        pass "ft_otp.key has owner-only permissions"
    else
        fail "ft_otp.key permissions should be 0600 (got: $mode)"
    fi
}

test_generates_six_digit_otp() {
    run_command "$BIN" -k "$KEY_FILE"
    assert_six_digit_output \
        "-k generates 6-digit OTP" \
        "-k should generate 6-digit OTP (got: $COMMAND_OUTPUT)"
}

test_rejects_missing_key_file() {
    run_command "$BIN" -k "$MISSING_KEY_FILE"
    assert_output_contains \
        "No such file" \
        "-k rejects missing file" \
        "-k should error on missing file"
}

test_prints_usage_without_args() {
    run_command "$BIN"
    assert_output_contains \
        "Usage" \
        "no args prints usage" \
        "no args should print usage"
}

test_invalid_flag_fails() {
    run_command "$BIN" -x "$VALID_KEY_FILE"
    assert_command_failed \
        "invalid flag exits with error" \
        "invalid flag should exit with error"
}

test_rfc_vectors() {
    run_command "$PYTHON" "$VECTOR_SCRIPT" "$VECTOR_MODE"

    if [ "$COMMAND_STATUS" -eq 0 ]; then
        pass "RFC $VECTOR_MODE vector tests pass"
    else
        printf "%s\n" "$COMMAND_OUTPUT"
        fail "RFC $VECTOR_MODE vector tests should pass"
    fi
}

test_key_comparisons() {
    printf "\n=== Key comparisons (ft_otp vs pyotp vs oathtool) ===\n"
    printf "Index | Hex Key | Base32 | ft_otp | pyotp | oathtool\n"
    printf -- "---:|:--|:--|---:|---:|---:\n"

    idx=1
    for key in "${TEST_KEYS[@]}"; do
        output=$("$PYTHON" "$VECTOR_SCRIPT" "$key" 2>/dev/null)
        if [ $? -eq 0 ]; then
            printf "%s | %s\n" "$idx" "$output"
        else
            printf "%s | [ERROR]\n" "$idx"
        fi
        idx=$((idx + 1))
    done
}

print_summary() {
    printf "\n"
    printf "=== Results: %s passed, %s failed ===\n" "$PASS" "$FAIL"
}

setup
trap cleanup EXIT

printf "=== ft_otp tests ===\n\n"

test_rejects_non_hex_key
test_rejects_missing_hex_file
test_saves_valid_key
test_creates_key_file
test_key_file_is_encrypted
test_key_file_permissions
test_generates_six_digit_otp
test_rejects_missing_key_file
test_prints_usage_without_args
test_invalid_flag_fails
test_rfc_vectors
test_key_comparisons
print_summary

[ "$FAIL" -eq 0 ] && exit 0 || exit 1
