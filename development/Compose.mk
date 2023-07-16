docker/compose:		## Docker - Start Container
	docker-compose -f compose.yml up -d

docker/compose/all:		## Docker - Start Container with App
	docker-compose -f compose.yml -f compose-app.yml up

docker/image:		## Docker - Build Image
	DOCKER_BUILDKIT=1 docker build -t $(PACKAGE):latest . -f development/Dockerfiles/Dockerfile