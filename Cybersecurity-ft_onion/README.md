# ft_onion

A static page (nginx, port 80) and an SSH server (port 4242), reachable only as a Tor v3 onion service, with no ports opened on the host.

## Files

| File | Role |
| --- | --- |
| [nginx/index.html](nginx/index.html) | The page (an inline snake game, no external resources) |
| [nginx/nginx.conf](nginx/nginx.conf) | Serves `index.html` on port 80 |
| [ssh/sshd_config](ssh/sshd_config) | SSH on port 4242, key login only for user `onion` |
| [tor/torrc](tor/torrc) | The onion service: port 80 → nginx, port 4242 → ssh |
| [docker-compose.yml](docker-compose.yml) | Three containers on a private network, no `ports:` |
| [client/Dockerfile](client/Dockerfile) | Test-only Tor client (curl, ssh), started only by `make ssh` / `make test` |
| [Makefile](Makefile), [scripts/tests.sh](scripts/tests.sh) | Run and check everything |

## Usage

Needs only Docker: no root, no Tor installed on the host.

```bash
make         # create SSH key if missing, build, start, print the .onion address
make ssh     # SSH into the server over Tor (from the client container)
make test    # check: no host ports, web page and SSH reachable over Tor, root refused
make down    # stop (keeps the address)
make fclean  # stop and delete the onion keys (new address next time)
```

`ssh/authorized_keys` is generated from `~/.ssh/ft_onion_key.pub` and is not committed, so always build with `make`.

## Choices

- **No ports open:** Tor only makes outbound connections to Tor relays. Visitors reach the service through those circuits, so Docker publishes nothing on the host.
- **Three containers:** Tor, nginx and sshd are isolated from each other. A compromised web server cannot read the onion keys.
- **Fixed IPs:** `HiddenServicePort` needs an IP address, not a container name.
- **`tor_keys` volume:** keeps the onion keys, so the address survives rebuilds.
- **Tor folder `0700`, owned by `debian-tor`:** Tor refuses to start otherwise.
- **`usermod -p '*'`:** a new user is locked, and sshd refuses locked accounts even with a valid key.
- **SSH:** keys only, no root, only user `onion`, 3 tries, no forwarding.
- **Client container:** tests go through the real Tor network without installing anything on the host. It is not started by `make` and publishes no port.

## Manual checks

```bash
ONION=$(docker compose exec -T tor cat /var/lib/tor/hidden_service/hostname)
docker compose run --rm client curl -sI --socks5-hostname 127.0.0.1:9050 "http://$ONION"   # 200 OK
docker compose ps                                          # no "->" in PORTS
docker compose exec ssh sshd -T | grep -E '^(port|permitrootlogin|passwordauthentication) '
```
