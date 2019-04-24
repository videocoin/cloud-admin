
help:
	@echo 'Available commands:'
	@echo
	@echo 'Usage:'
	@echo '    make deps     		Install go deps.'
	@echo '    make build    		Compile the project.'
	@echo '    make build/docker	Restore all build binary and docker image.'
	@echo

test:
	gp trest -v ./...
deps:
	go get -u cmd/main.go

build:
	@echo "Compiling..."
	@mkdir -p ./bin
	@mkdir -p ./compiler
	@go build -tags 'bindatafs' -o compiler/compile compile/main.go
	@go build -tags 'bindatafs' -o bin/admin cmd/main.go
	@echo "Compiled"

build/docker: build
	@docker build -t adminpanel:latest .

vet: ## run go vet
	@test -z "$$(go vet ${PACKAGES} 2>&1 | grep -v '*composite literal uses unkeyed fields|exit status 0)' | tee /dev/stderr)"

ci: vet test

restore:
	@dep ensure
