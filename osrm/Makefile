all: docker

docker:
	@open -a Docker
	@while ! docker info > /dev/null 2>&1; do \
		sleep 1; \
	done
	@docker stop $$(docker ps -a -q)
	@docker compose up --build -d