REGISTRY_SERVER?=registry.videocoin.net
REGISTRY_PROJECT?=cloud

NAME=admin
NAME_STATIC=admin-static

VERSION?=$$(git rev-parse HEAD)

IMAGE_TAG=${REGISTRY_SERVER}/${REGISTRY_PROJECT}/${NAME}:${VERSION}
IMAGE_TAG_STATIC=${REGISTRY_SERVER}/${REGISTRY_PROJECT}/${NAME_STATIC}:${VERSION}

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
	helm upgrade -i --wait --timeout 60s --set image.tag="${VERSION}" -n vcn-admin admin ./deploy/helm
