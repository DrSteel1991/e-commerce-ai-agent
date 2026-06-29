.PHONY: dev stop logs

dev:
	./scripts/dev-start.sh

stop:
	./scripts/dev-stop.sh

logs:
	tail -f logs/gateway.log logs/agent.log logs/rag.log
