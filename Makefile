.PHONY: build

build:
	docker-compose up -d --build
	docker image prune -f
