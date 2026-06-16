#!/bin/bash

PASS=0
FAIL=0

GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'
BIN=./ft_otp

ok()   { echo -e "${GREEN}[PASS]${NC} $1"; ((++PASS)); }
fail() { echo -e "${RED}[FAIL]${NC} $1"; ((++FAIL)); }

# Setup: generate a valid 64-char hex key
TEST_KEY=$(python3 -c "import os; print(os.urandom(32).hex())")
echo "$TEST_KEY" > test_key.hex
echo "NEVER GONNA GIVE YOU UP" > test_bad.txt

cleanup() {
    rm -f test_key.hex test_bad.txt ft_otp.key
}
trap cleanup EXIT

echo "=== ft_otp tests ==="
echo ""

# -g: reject non-hex input
out=$("$BIN" -g test_bad.txt 2>&1)
if echo "$out" | grep -q "key must be 64 hexadecimal characters."; then
    ok "-g rejects non-hex key"
else
    fail "-g should reject non-hex key"
fi

# -g: reject missing file
out=$("$BIN" -g no_such_file.hex 2>&1)
if echo "$out" | grep -q "No such file"; then
    ok "-g rejects missing file"
else
    fail "-g should error on missing file"
fi

# -g: accept valid hex key
out=$("$BIN" -g test_key.hex 2>&1)
if echo "$out" | grep -q "successfully saved"; then
    ok "-g saves valid key"
else
    fail "-g should save valid key"
fi

# -g: creates ft_otp.key
[ -f ft_otp.key ] && ok "-g creates ft_otp.key" || fail "-g did not create ft_otp.key"

# -g: ft_otp.key is not plaintext (encrypted)
content=$(cat ft_otp.key)
if [ "$content" != "$TEST_KEY" ]; then
    ok "ft_otp.key is not plaintext"
else
    fail "ft_otp.key should be encrypted"
fi

# -g: ft_otp.key is readable only by its owner
mode=$(python3 -c "from pathlib import Path; print(oct(Path('ft_otp.key').stat().st_mode & 0o777))")
if [ "$mode" = "0o600" ]; then
    ok "ft_otp.key has owner-only permissions"
else
    fail "ft_otp.key permissions should be 0600 (got: $mode)"
fi

# -k: generates 6-digit OTP
otp=$("$BIN" -k ft_otp.key 2>&1)
if echo "$otp" | grep -qE "^[0-9]{6}$"; then
    ok "-k generates 6-digit OTP"
else
    fail "-k should generate 6-digit OTP (got: $otp)"
fi

# -k: rejects missing file
out=$("$BIN" -k no_such.key 2>&1)
if echo "$out" | grep -q "No such file"; then
    ok "-k rejects missing file"
else
    fail "-k should error on missing file"
fi

# -k vs oathtool: outputs match
otp_ours=$("$BIN" -k ft_otp.key 2>&1)
otp_oath=$(oathtool --totp "$TEST_KEY" 2>&1)
if [ "$otp_ours" = "$otp_oath" ]; then
    ok "-k matches oathtool (both: $otp_ours)"
else
    fail "-k output ($otp_ours) != oathtool ($otp_oath)"
fi

# no args: usage error
out=$("$BIN" 2>&1)
echo "$out" | grep -q "Usage" && ok "no args prints usage" || fail "no args should print usage"

# invalid flag
out=$("$BIN" -x test_key.hex 2>&1)
[ $? -ne 0 ] && ok "invalid flag exits with error" || fail "invalid flag should exit with error"

# multi-key comparison against oathtool
echo ""
echo "=== Multi-key comparison: ft_otp vs oathtool ==="
printf "%-66s  %-10s  %-10s  %s\n" "KEY (first 16...last 16)" "ft_otp" "oathtool" "match"
printf '%s\n' "$(printf '%.0s-' {1..100})"

KEYS=(
    "1111111111111111111111111111111111111111111111111111111111111111"
    "abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890"
    "deadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeef"
    "0000000000000000000000000000000000000000000000000000000000000000"
    "ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff"
    $(python3 -c "import os; print(os.urandom(32).hex())")
    $(python3 -c "import os; print(os.urandom(32).hex())")
    $(python3 -c "import os; print(os.urandom(32).hex())")
)

for key in "${KEYS[@]}"; do
    echo "$key" > _tmp_cmp.hex
    "$BIN" -g _tmp_cmp.hex > /dev/null 2>&1
    otp_ours=$("$BIN" -k ft_otp.key 2>&1)
    otp_oath=$(oathtool --totp "$key" 2>&1)
    short="${key:0:16}...${key: -16}"
    if [ "$otp_ours" = "$otp_oath" ]; then
        match="${GREEN}OK${NC}"
        ((++PASS))
    else
        match="${RED}MISMATCH${NC}"
        ((++FAIL))
    fi
    printf "%-66s  %-10s  %-10s  " "$short" "$otp_ours" "$otp_oath"
    echo -e "$match"
done

rm -f _tmp_cmp.hex

echo ""
echo "=== Results: ${PASS} passed, ${FAIL} failed ==="
[ $FAIL -eq 0 ] && exit 0 || exit 1
