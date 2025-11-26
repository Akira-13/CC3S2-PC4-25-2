.PHONY: dev compose-up compose-down

dev: compose-up

compose-up:
	bash scripts/up.sh

compose-down:
	bash scripts/down.sh
