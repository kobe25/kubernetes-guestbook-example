ps:
	docker-compose ps
.PHONY: ps

down:
	docker-compose down -v --remove-orphans
	docker-compose rm -fv
.PHONY: down

up: down
	docker-compose up -d --build --remove-orphans
.PHONY: up

test: up
	@echo Running tests..
	./test.sh
.PHONY: test

logs_%:
	docker-compose logs -f $*

deploy:
	kubectl apply -f deploy/
.PHONY: deploy
