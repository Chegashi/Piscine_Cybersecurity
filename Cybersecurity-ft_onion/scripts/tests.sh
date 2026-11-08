#!/bin/bash
# Run with `make test`. Tor, curl and ssh run in the client container.
ok() { echo "OK   $1"; }
ko() { echo "FAIL $1"; exit 1; }

[ "$(docker compose ps --services --status running | wc -l)" -eq 3 ] && ok "3 containers running" || ko "containers not running"
docker compose ps --format '{{.Ports}}' | grep -q -- '->' && ko "a host port is published" || ok "no host ports"

ONION=$(docker compose exec -T tor cat /var/lib/tor/hidden_service/hostname)
[[ $ONION =~ ^[a-z2-7]{56}\.onion$ ]] && ok "$ONION" || ko "no onion address"

echo "...  starting a Tor client container (about 30s)"
docker compose build -q client >/dev/null 2>&1
read -r HTTP LOGIN ROOT < <(docker compose run --rm -T -v "$KEY":/key:ro client sh -c "
    curl -s -o /dev/null -w '%{http_code} ' --max-time 120 --socks5-hostname 127.0.0.1:9050 http://$ONION
    echo \$(ssh $SSH_OPT -o BatchMode=yes -i /key onion@$ONION whoami 2>/dev/null)
    ssh $SSH_OPT -o BatchMode=yes root@$ONION true 2>&1 | grep -q 'Permission denied' && echo refused
" | tr '\n' ' ')

[ "$HTTP" = 200 ]       && ok "web page on port 80 over Tor"  || ko "web page over Tor (got '$HTTP')"
[ "$LOGIN" = onion ]    && ok "SSH key login on port 4242"    || ko "SSH key login"
[ "$ROOT" = refused ]   && ok "SSH root login refused"        || ko "SSH root login not refused"
