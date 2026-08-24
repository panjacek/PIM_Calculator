.PHONY: all test lint format build run-cli sync clean

# All build artifacts land in the shared root dist/ directory.
DIST := ../dist
BIN := $(DIST)/pim_calc-go

all: build

test:
	go test -v -coverpkg=./... -coverprofile=coverage.out ./...
	@go tool cover -func=coverage.out | tail -1

lint:
	go vet ./...

format:
	gofmt -l -w .

build:
	mkdir -p $(DIST)
	go build -o $(BIN) PIM_Calculator.go

sync:
	go get -u ./...
	go mod tidy

run-cli: build
	$(BIN) -tx_band "5,5" 1980,1940

clean:
	rm -f $(BIN)
	rm -f pim_calc

