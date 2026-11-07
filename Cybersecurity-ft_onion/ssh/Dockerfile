FROM debian:trixie-slim

RUN apt-get update && apt-get upgrade -y --no-install-recommends && \
    apt-get install -y --no-install-recommends openssh-server && \
    rm -rf /var/lib/apt/lists/*

# '*' = no usable password but account not locked (sshd rejects locked accounts)
RUN useradd -m -s /bin/bash onion && usermod -p '*' onion && \
    mkdir -p /home/onion/.ssh /run/sshd

COPY authorized_keys /home/onion/.ssh/authorized_keys
RUN chown -R onion:onion /home/onion/.ssh && \
    chmod 700 /home/onion/.ssh && \
    chmod 600 /home/onion/.ssh/authorized_keys

# Keep only an Ed25519 host key
RUN rm -f /etc/ssh/ssh_host_* && \
    ssh-keygen -t ed25519 -N "" -f /etc/ssh/ssh_host_ed25519_key

COPY sshd_config /etc/ssh/sshd_config
RUN chmod 644 /etc/ssh/sshd_config

EXPOSE 4242
CMD ["/usr/sbin/sshd", "-D", "-e"]
