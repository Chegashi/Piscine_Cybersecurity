FROM debian:trixie-slim

RUN apt-get update && apt-get install -y --no-install-recommends tor && \
    rm -rf /var/lib/apt/lists/*

COPY torrc /etc/tor/torrc

# Tor requires its hidden-service directory to be 0700 and owned by its user
RUN mkdir -p /var/lib/tor/hidden_service && \
    chown -R debian-tor:debian-tor /var/lib/tor && \
    chmod 700 /var/lib/tor /var/lib/tor/hidden_service

USER debian-tor
CMD ["tor", "-f", "/etc/tor/torrc"]
