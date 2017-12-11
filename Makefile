ps:
	docker-compose ps

down:
	docker-compose down -v --remove-orphans
	docker-compose rm -fv

up: down
	docker-compose up -d --build --remove-orphans

test: up
	@echo Running tests..
	./test.sh

logs_%:
	docker-compose logs -f $*

deploy:
	kubectl apply -f deploy/

.PHONY: ps down up test deploy
