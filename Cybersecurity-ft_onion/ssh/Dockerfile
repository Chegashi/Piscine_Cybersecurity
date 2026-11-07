FROM debian:trixie-slim

RUN apt-get update && apt-get install -y --no-install-recommends openssh-server && \
    rm -rf /var/lib/apt/lists/* && mkdir -p /run/sshd

# '*' = no password, but account not locked (sshd rejects locked accounts)
RUN useradd -m -s /bin/bash onion && usermod -p '*' onion

COPY authorized_keys /home/onion/.ssh/authorized_keys
RUN chown -R onion:onion /home/onion/.ssh && \
    chmod 700 /home/onion/.ssh && chmod 600 /home/onion/.ssh/authorized_keys

COPY sshd_config /etc/ssh/sshd_config

CMD ["/usr/sbin/sshd", "-D", "-e"]
