.PHONY: test test-python test-python-unit test-python-gui test-go test-mojo lint build-go install run-python-cli run-python-gui run-go-cli run-mojo-cli clean

test: test-python test-go test-mojo

lint: lint-python lint-go lint-mojo

lint-python:
	$(MAKE) -C python lint

lint-go:
	$(MAKE) -C go lint

lint-mojo:
	$(MAKE) -C mojo lint

test-python:
	$(MAKE) -C python test

test-python-unit:
	$(MAKE) -C python test-unit

test-python-gui:
	$(MAKE) -C python test-gui

test-go:
	$(MAKE) -C go test

test-mojo:
	$(MAKE) -C mojo test

build-go:
	$(MAKE) -C go build

install:
	$(MAKE) -C python install

run-python-cli:
	$(MAKE) -C python run-cli

run-python-gui:
	$(MAKE) -C python run-gui

run-go-cli:
	$(MAKE) -C go run-cli

run-mojo-cli:
	$(MAKE) -C mojo run-mojo-cli CALC_ARGS=$(CALC_ARGS)

clean:
	$(MAKE) -C python clean
	$(MAKE) -C go clean
	rm -rf .pytest_cache


