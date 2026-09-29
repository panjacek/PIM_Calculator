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

# Default for direct `make -C go run-cli`; root Makefile always forwards its own.
# Go needs explicit bands, no auto-expansion (length mismatch panics), and
# flags must precede the positional TX list (the go flag package stops
# parsing at the first non-flag argument).
CALC_ARGS ?= -rx_list 1752,1900 -rx_band 5,5 -tx_band 5,5 2152,1932

run-cli: build
	$(BIN) $(CALC_ARGS)

clean:
	rm -f $(BIN)
	rm -f go

