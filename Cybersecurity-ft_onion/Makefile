COMPOSE  = docker compose
KEY     ?= $(HOME)/.ssh/ft_onion_key
SOCKS   ?= 127.0.0.1:9050
HOSTNAME = /var/lib/tor/hidden_service/hostname
# System nc (BSD/OpenBSD) supports SOCKS5 via -X; GNU netcat does not
NC      ?= $(shell test -x /usr/bin/nc && echo /usr/bin/nc || echo nc)
PROXY    = ProxyCommand=$(NC) -X 5 -x $(SOCKS) %h %p

all: up

# Generate the SSH key pair once and copy the public key into the build context
ssh/authorized_keys: | $(KEY)
	cp $(KEY).pub $@

$(KEY):
	@mkdir -p $(dir $(KEY))
	ssh-keygen -t ed25519 -N "" -C "ft_onion" -f $(KEY)

keys: ssh/authorized_keys

up: keys
	$(COMPOSE) up -d --build
	@$(MAKE) --no-print-directory address

down:
	$(COMPOSE) down

# Wait (up to 2 min) for Tor to write the hostname, then print it
address:
	@printf "Waiting for onion address"; \
	for i in $$(seq 1 60); do \
		if $(COMPOSE) exec -T tor test -s $(HOSTNAME) 2>/dev/null; then \
			echo; echo "http://$$($(COMPOSE) exec -T tor cat $(HOSTNAME))"; exit 0; \
		fi; \
		printf "."; sleep 2; \
	done; \
	echo; echo "Timed out. Check: make logs"; exit 1

ssh:
	ssh -o "$(PROXY)" -i $(KEY) -p 4242 onion@$$($(COMPOSE) exec -T tor cat $(HOSTNAME))

test:
	@SOCKS=$(SOCKS) NC=$(NC) bash scripts/tests.sh

ps:
	$(COMPOSE) ps

logs:
	$(COMPOSE) logs -f

clean: down

# Also removes the onion keys volume (next start = new .onion address) and images
fclean:
	$(COMPOSE) down -v --rmi local
	rm -f ssh/authorized_keys

re: fclean all

.PHONY: all keys up down address ssh test ps logs clean fclean re
