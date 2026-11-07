KEY   ?= $(HOME)/.ssh/ft_onion_key
SOCKS ?= 127.0.0.1:9050
ONION  = docker compose exec -T tor cat /var/lib/tor/hidden_service/hostname

all: ssh/authorized_keys
	docker compose up -d --build
	@until $(ONION) >/dev/null 2>&1; do sleep 1; done; echo "http://$$($(ONION))"

ssh/authorized_keys:
	@mkdir -p $(dir $(KEY)); test -f $(KEY) || ssh-keygen -t ed25519 -N "" -f $(KEY)
	cp $(KEY).pub $@

ssh:
	ssh -o "ProxyCommand=/usr/bin/nc -X 5 -x $(SOCKS) %h %p" -i $(KEY) -p 4242 onion@$$($(ONION))

test:
	@SOCKS=$(SOCKS) bash scripts/tests.sh

down:
	docker compose down

fclean:
	docker compose down -v --rmi local
	rm -f ssh/authorized_keys

re: fclean all

.PHONY: all ssh test down fclean re
