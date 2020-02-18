GOOS?=linux
GOARCH?=amd64

DOCKER_REGISTRY?=gcr.io
NAME=admin
NAME_STATIC=admin-static
GCP_PROJECT=videocoin-network
VERSION=$$(git rev-parse --short HEAD)
IMAGE_TAG=${DOCKER_REGISTRY}/${GCP_PROJECT}/${NAME}:${VERSION}
IMAGE_TAG_STATIC=${DOCKER_REGISTRY}/${GCP_PROJECT}/${NAME_STATIC}:${VERSION}

DBM_MSQLURI=root:@tcp(127.0.0.1:3306)/videocoin?charset=utf8&parseTime=True&loc=Local
ENV?=dev

.PHONY: deploy

default: build

version:
	@echo ${VERSION}

docker-build:
	docker build -t ${IMAGE_TAG} -f Dockerfile .

docker-build-static:
	docker build -t ${IMAGE_TAG_STATIC} -f Dockerfile.static .

docker-push:
	@echo "==> Pushing ${NAME} docker image..."
	docker push ${IMAGE_TAG}

docker-push-static:
	@echo "==> Pushing ${NAME_STATIC} docker image..."
	docker push ${IMAGE_TAG_STATIC}

release: docker-build docker-push docker-build-static docker-push-static

deploy:
	ENV=${ENV} GCP_PROJECT=${GCP_PROJECT} deploy/deploy.sh

lint:
	pylint --rcfile=.pylintrc src/apps/