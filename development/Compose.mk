docker/image:		## Docker - Build Image
	DOCKER_BUILDKIT=1 docker build -t librarydevpy.azurecr.io/librarydevpy . -f development/Dockerfiles/Dockerfile
