.PHONY: dev stop logs setup

setup:
	./scripts/setup-dev-env.sh

dev: setup
	./scripts/dev-start.sh

stop:
	./scripts/dev-stop.sh

logs:
	tail -f logs/gateway.log logs/agent.log logs/rag.log
