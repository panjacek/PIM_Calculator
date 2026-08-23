.PHONY: help test test-integration test-python test-python-unit test-python-gui test-go test-mojo lint lint-tests lint-python lint-go lint-mojo format format-python format-mojo format-tests format-go build-go install run-python-cli run-python-gui run-go-cli run-mojo-cli clean

help: ## Show available targets
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

test: test-python test-go test-mojo ## Run all unit suites (python/go/mojo)

lint: lint-python lint-go lint-mojo lint-tests ## Run all linters
lint-python: ## Ruff on python/
	$(MAKE) -C python lint

lint-go: ## go vet
	$(MAKE) -C go lint

lint-mojo: ## mblack on mojo/
	$(MAKE) -C mojo lint

lint-tests: ## Ruff on tests/
	uv run ruff check tests

format: format-python format-mojo format-tests format-go ## Auto-format all flavours

format-python: ## ruff format on python/
	$(MAKE) -C python format

format-mojo: ## mblack on mojo/
	$(MAKE) -C mojo format

format-tests: ## ruff format on tests/
	uv run ruff format tests

format-go: ## gofmt
	$(MAKE) -C go format

test-python: ## Python pytest suite (unit only; GUI has own target)
	$(MAKE) -C python test

test-python-unit: ## Python unit tests only (fast)
	$(MAKE) -C python test-unit

test-python-gui: ## Python Qt GUI tests (needs display/xvfb)
	$(MAKE) -C python test-gui

test-go: ## Go test suite
	$(MAKE) -C go test

test-mojo: ## Mojo test suite (needs mojo toolchain)
	$(MAKE) -C mojo test

build-go: ## Build the go CLI binary (go/pim_calc)
	$(MAKE) -C go build

test-integration: build-go ## Cross-flavour comparison via tests/test_integration.py
	uv run pytest tests/test_integration.py -v

install: ## Editable-install the python package (uv)
	$(MAKE) -C python install

run-python-cli: ## Run python CLI: CALC_ARGS="2152,1932 -r 1752,1900"
	$(MAKE) -C python run-cli

run-python-gui: ## Run the Qt GUI
	$(MAKE) -C python run-gui

run-go-cli: ## Build & run the go CLI
	$(MAKE) -C go run-cli

run-mojo-cli: ## Run the mojo wrapper CLI: CALC_ARGS="2152,1932 -r 1752,1900"
	$(MAKE) -C mojo run-mojo-cli CALC_ARGS=$(CALC_ARGS)

clean: ## Remove build and cache artifacts
	$(MAKE) -C python clean
	$(MAKE) -C go clean
	rm -rf .pytest_cache
