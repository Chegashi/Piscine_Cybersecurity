#!/bin/bash

PASS=0
FAIL=0

GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

BIN=./ft_otp
KEY_FILE=ft_otp.key
VALID_KEY_FILE=test_key.hex
BAD_KEY_FILE=test_bad.txt
TEMP_KEY_FILE=_tmp_cmp.hex
MISSING_HEX_FILE=no_such_file.hex
MISSING_KEY_FILE=no_such.key
EXPECTED_KEY_MODE=0o600

COMMAND_OUTPUT=
COMMAND_STATUS=0

pass() {
    printf "%b[PASS]%b %s\n" "$GREEN" "$NC" "$1"
    ((++PASS))
}

fail() {
    printf "%b[FAIL]%b %s\n" "$RED" "$NC" "$1"
    ((++FAIL))
}

run_command() {
    COMMAND_OUTPUT=$("$@" 2>&1)
    COMMAND_STATUS=$?
}

random_hex_key() {
    python3 -c "import os; print(os.urandom(32).hex())"
}

file_mode() {
    python3 -c '
from pathlib import Path
import sys

print(oct(Path(sys.argv[1]).stat().st_mode & 0o777))
' "$1"
}

assert_output_contains() {
    local expected=$1
    local pass_message=$2
    local fail_message=$3

    if [[ "$COMMAND_OUTPUT" == *"$expected"* ]]; then
        pass "$pass_message"
    else
        fail "$fail_message"
    fi
}

assert_output_matches() {
    local pattern=$1
    local pass_message=$2
    local fail_message=$3

    if [[ "$COMMAND_OUTPUT" =~ $pattern ]]; then
        pass "$pass_message"
    else
        fail "$fail_message"
    fi
}

assert_command_failed() {
    local pass_message=$1
    local fail_message=$2

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
    rm -f "$VALID_KEY_FILE" "$BAD_KEY_FILE" "$TEMP_KEY_FILE" "$KEY_FILE"
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
    assert_output_contains \
        "successfully saved" \
        "-g saves valid key" \
        "-g should save valid key"
}

test_creates_key_file() {
    if [ -f "$KEY_FILE" ]; then
        pass "-g creates ft_otp.key"
    else
        fail "-g did not create ft_otp.key"
    fi
}

test_key_file_is_encrypted() {
    local content
    content=$(cat "$KEY_FILE")

    if [ "$content" != "$TEST_KEY" ]; then
        pass "ft_otp.key is not plaintext"
    else
        fail "ft_otp.key should be encrypted"
    fi
}

test_key_file_permissions() {
    local mode
    mode=$(file_mode "$KEY_FILE")

    if [ "$mode" = "$EXPECTED_KEY_MODE" ]; then
        pass "ft_otp.key has owner-only permissions"
    else
        fail "ft_otp.key permissions should be 0600 (got: $mode)"
    fi
}

test_generates_six_digit_otp() {
    run_command "$BIN" -k "$KEY_FILE"
    assert_output_matches \
        "^[0-9]{6}$" \
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

test_matches_oathtool() {
    local otp_ours
    local otp_oath

    otp_ours=$("$BIN" -k "$KEY_FILE" 2>&1)
    otp_oath=$(oathtool --totp "$TEST_KEY" 2>&1)

    if [ "$otp_ours" = "$otp_oath" ]; then
        pass "-k matches oathtool (both: $otp_ours)"
    else
        fail "-k output ($otp_ours) != oathtool ($otp_oath)"
    fi
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

print_comparison_header() {
    printf "\n"
    printf "=== Multi-key comparison: ft_otp vs oathtool ===\n"
    printf "%-66s  %-10s  %-10s  %s\n" "KEY (first 16...last 16)" "ft_otp" "oathtool" "match"
    printf "%s\n" "$(printf '%.0s-' {1..100})"
}

compare_key_with_oathtool() {
    local key=$1
    local otp_ours
    local otp_oath
    local short_key
    local match

    printf "%s\n" "$key" > "$TEMP_KEY_FILE"
    "$BIN" -g "$TEMP_KEY_FILE" > /dev/null 2>&1

    otp_ours=$("$BIN" -k "$KEY_FILE" 2>&1)
    otp_oath=$(oathtool --totp "$key" 2>&1)
    short_key="${key:0:16}...${key: -16}"

    if [ "$otp_ours" = "$otp_oath" ]; then
        match="${GREEN}OK${NC}"
        ((++PASS))
    else
        match="${RED}MISMATCH${NC}"
        ((++FAIL))
    fi

    printf "%-66s  %-10s  %-10s  " "$short_key" "$otp_ours" "$otp_oath"
    printf "%b\n" "$match"
}

run_multi_key_comparison() {
    local keys=(
        "1111111111111111111111111111111111111111111111111111111111111111"
        "abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890"
        "deadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeef"
        "0000000000000000000000000000000000000000000000000000000000000000"
        "ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff"
        "$(random_hex_key)"
        "$(random_hex_key)"
        "$(random_hex_key)"
    )

    print_comparison_header

    for key in "${keys[@]}"; do
        compare_key_with_oathtool "$key"
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
test_matches_oathtool
test_prints_usage_without_args
test_invalid_flag_fails
run_multi_key_comparison
print_summary

[ "$FAIL" -eq 0 ] && exit 0 || exit 1
