KEY    ?= $(HOME)/.ssh/ft_onion_key
ONION   = docker compose exec -T tor cat /var/lib/tor/hidden_service/hostname
SSH_OPT = -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR \
          -o "ProxyCommand=nc -X 5 -x 127.0.0.1:9050 %h %p" -p 4242

all: ssh/authorized_keys
	docker compose up -d --build
	@until $(ONION) >/dev/null 2>&1; do sleep 1; done; echo "http://$$($(ONION))"

ssh/authorized_keys:
	@mkdir -p $(dir $(KEY)); test -f $(KEY) || ssh-keygen -t ed25519 -N "" -f $(KEY)
	cp $(KEY).pub $@

ssh:
	docker compose run --rm -v $(KEY):/key:ro client ssh $(SSH_OPT) -i /key onion@$$($(ONION))

test:
	@KEY=$(KEY) SSH_OPT='$(SSH_OPT)' bash scripts/tests.sh

down:
	docker compose down

fclean:
	docker compose --profile client down -v --rmi local
	rm -f ssh/authorized_keys

re: fclean all

.PHONY: all ssh test down fclean re
