#!/bin/bash
SOCKS=${SOCKS:-127.0.0.1:9050}
ok() { echo "OK   $1"; }
ko() { echo "FAIL $1"; exit 1; }

[ "$(docker compose ps --services --status running | wc -l)" -eq 3 ] && ok "3 containers running" || ko "containers not running"
docker compose ps --format '{{.Ports}}' | grep -q -- '->' && ko "a host port is published" || ok "no host ports"

ONION=$(docker compose exec -T tor cat /var/lib/tor/hidden_service/hostname)
[[ $ONION =~ ^[a-z2-7]{56}\.onion$ ]] && ok "$ONION" || ko "no onion address"

CODE=$(curl -s -o /dev/null -w '%{http_code}' --max-time 90 --socks5-hostname "$SOCKS" "http://$ONION")
[ "$CODE" = 200 ] && ok "HTTP 200 on port 80 over Tor" || ko "HTTP over Tor (got $CODE)"

ssh -o BatchMode=yes -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ConnectTimeout=90 \
    -o "ProxyCommand=/usr/bin/nc -X 5 -x $SOCKS %h %p" -p 4242 root@"$ONION" true 2>&1 \
    | grep -q 'Permission denied (publickey)' && ok "SSH on 4242 over Tor, root and passwords refused" || ko "SSH over Tor"
