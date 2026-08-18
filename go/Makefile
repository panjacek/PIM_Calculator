.PHONY: all test lint build run-cli clean

all: build

test:
	go test -v ./...

lint:
	go vet ./...

build:
	go build -o pim_calc PIM_Calculator.go

run-cli: build
	./pim_calc -tx_band "5,5" 1980,1940

clean:
	rm -f pim_calc

