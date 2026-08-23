.PHONY: all test lint format build run-cli clean

all: build

test:
	go test -v -coverpkg=./... -coverprofile=coverage.out ./...
	@go tool cover -func=coverage.out | tail -1

lint:
	go vet ./...

format:
	gofmt -l -w .

build:
	go build -o pim_calc PIM_Calculator.go

run-cli: build
	./pim_calc -tx_band "5,5" 1980,1940

clean:
	rm -f pim_calc

