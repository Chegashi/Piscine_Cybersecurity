# Tor client used to test the service, so the host needs nothing but Docker
FROM debian:trixie-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    tor curl openssh-client netcat-openbsd && rm -rf /var/lib/apt/lists/*

# Start Tor, wait until it is connected, then run the given command
ENTRYPOINT ["sh", "-c", "tor --RunAsDaemon 1 --Log 'notice file /tmp/tor.log' >/dev/null && until grep -q 'Bootstrapped 100' /tmp/tor.log; do sleep 1; done && exec \"$@\"", "--"]
