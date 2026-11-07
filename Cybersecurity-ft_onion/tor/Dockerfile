FROM debian:trixie-slim

RUN apt-get update && apt-get upgrade -y --no-install-recommends && \
    apt-get install -y --no-install-recommends tor ca-certificates && \
    rm -rf /var/lib/apt/lists/*

COPY torrc /etc/tor/torrc

# Tor requires 0700 on its data and hidden-service directories
RUN mkdir -p /var/lib/tor/hidden_service && \
    chown -R debian-tor:debian-tor /var/lib/tor && \
    chmod 700 /var/lib/tor /var/lib/tor/hidden_service

USER debian-tor
CMD ["tor", "-f", "/etc/tor/torrc"]
