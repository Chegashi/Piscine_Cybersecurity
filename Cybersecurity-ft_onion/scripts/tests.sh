#!/usr/bin/env bash
set -euo pipefail

SOCKS="${SOCKS:-127.0.0.1:9050}"
# System nc supports SOCKS5 (-X); a GNU netcat earlier in PATH does not
NC="${NC:-$( [ -x /usr/bin/nc ] && echo /usr/bin/nc || echo nc)}"

G='\033[0;32m'; R='\033[0;31m'; Y='\033[1;33m'; N='\033[0m'
pass() { echo -e "  ${G}PASS${N} $*"; }
fail() { echo -e "  ${R}FAIL${N} $*"; exit 1; }
warn() { echo -e "  ${Y}WARN${N} $*"; }

echo "[1/6] Containers running"
for c in ft_onion_tor ft_onion_nginx ft_onion_ssh; do
    docker ps --format '{{.Names}}' | grep -qx "$c" && pass "$c" || fail "$c not running"
done

echo "[2/6] No published host ports"
if docker compose ps --format '{{.Ports}}' | grep -q -- '->'; then
    fail "host port published"
else
    pass "none"
fi

echo "[3/6] Onion address"
ONION=$(docker compose exec -T tor cat /var/lib/tor/hidden_service/hostname 2>/dev/null || true)
[[ "$ONION" =~ ^[a-z2-7]{56}\.onion$ ]] && pass "$ONION" || fail "invalid address: '$ONION'"

echo "[4/6] HTTP over Tor (SOCKS $SOCKS)"
CODE=$(curl -s -o /dev/null -w '%{http_code}' --max-time 90 --socks5-hostname "$SOCKS" "http://$ONION" || true)
[ "$CODE" = 200 ] && pass "200 OK" || warn "got '${CODE}' (is a local Tor client running on $SOCKS?)"

echo "[5/6] SSH banner over Tor"
# ssh -v prints the server's version banner; the login itself is expected to fail
BANNER=$(ssh -v -o BatchMode=yes -o ConnectTimeout=60 \
    -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null \
    -o "ProxyCommand=$NC -X 5 -x $SOCKS %h %p" -p 4242 probe@"$ONION" true 2>&1 \
    | grep -o 'remote software version .*' || true)
[ -n "$BANNER" ] && pass "$BANNER" || warn "no SSH banner"

echo "[6/6] SSH hardening"
docker compose exec -T ssh sshd -T | grep -E '^(port|permitrootlogin|passwordauthentication|pubkeyauthentication) '
