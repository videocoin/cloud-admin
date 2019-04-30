.NOTPARALLEL:
.EXPORT_ALL_VARIABLES:
.DEFAULT_GOAL := main

GOOS = linux
GOARCH = amd64

SERVICE_NAME = adminpanel
DOCKER_REGISTRY = us.gcr.io

IMAGE_TAG=$(DOCKER_REGISTRY)/${PROJECT_ID}/$(SERVICE_NAME):$(VERSION)
LATEST=$(DOCKER_REGISTRY)/${PROJECT_ID}/$(SERVICE_NAME):latest

VERSION=$$(git rev-parse --short HEAD)

help:
	@echo 'Available commands:'
	@echo
	@echo 'Usage:'
	@echo '    make deps     		Install go deps.'
	@echo '    make build    		Compile the project.'
	@echo '    make docker	        Build docker image.'
	@echo '    make docker/push            Build docker image and push to gcloud.'
	@echo

test:
	go test -v ./...
deps:
	go get -u cmd/main.go

build:
	@echo "Compiing..."
	@mkdir -p ./bin
	@mkdir -p ./compiler
	@go build -tags 'bindatafs' -o compiler/compile compile/main.go
	@go build -tags 'bindatafs' -o bin/admin cmd/main.go
	@echo "Compiled"

docker:
	@docker build -t $(IMAGE_TAG) -t $(LATEST) .

docker/push: docker 
	@docker push $(IMAGE_TAG)
	@docker push $(LATEST)

main: docker/push

vet: ## run go vet
	@test -z "$$(go vet ${PACKAGES} 2>&1 | grep -v '*composite literal uses unkeyed fields|exit status 0)' | tee /dev/stderr)"

ci: vet test

restore:
	@dep ensure
