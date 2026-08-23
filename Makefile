.PHONY: help build build-go build-mojo build-python test test-unit test-integration test-perf test-python test-python-unit test-python-gui test-go test-mojo lint lint-tests lint-python lint-go lint-mojo format format-python format-mojo format-tests format-go install sync sync-root sync-python sync-go run-python-cli run-python-gui run-go-cli run-mojo-cli run-mojo-py-cli clean

help: ## Show available targets
	@awk -F ':.*?## ' '/^#########/ {printf "\n%s\n", $$0} /^[a-zA-Z_-]+:.*?## / {printf "%-20s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

######### TEST #########

test: test-python test-go test-mojo test-integration test-perf ## Run all suites (unit + integration + perf)

test-unit: test-python-unit test-go test-mojo ## Run all unit suites (python/go/mojo)

test-perf: ## Python pytest-benchmark performance tests
	$(MAKE) -C python test-perf

test-integration: build-go ## Cross-flavour comparison via tests/test_integration.py
	uv run pytest tests/test_integration.py -v

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

######### LINT #########

lint: lint-python lint-go lint-mojo lint-tests ## Run all linters

lint-python: ## Ruff, mypy and bandit on python/
	$(MAKE) -C python lint

lint-go: ## go vet
	$(MAKE) -C go lint

lint-mojo: ## mblack on mojo/
	$(MAKE) -C mojo lint

lint-tests: ## Ruff + mypy on tests/
	uv run ruff check tests
	uv run mypy tests

######### FORMAT #########

format: format-python format-mojo format-tests format-go ## Auto-format all flavours

format-python: ## ruff format on python/
	$(MAKE) -C python format

format-mojo: ## mblack on mojo/
	$(MAKE) -C mojo format

format-tests: ## ruff format on tests/
	uv run ruff format tests

format-go: ## gofmt
	$(MAKE) -C go format

######### SYNC #########

sync: sync-root sync-python sync-go ## Upgrade dep versions & re-sync all flavours

sync-root:
	uv lock --upgrade
	uv sync --group dev

sync-python:
	$(MAKE) -C python sync

sync-go:
	$(MAKE) -C go sync

######### BUILD / INSTALL #########

build: build-go build-mojo build-python ## Build all packages into ./dist (go/mojo CLIs + python wheel/sdist)

build-go: ## Build the go CLI binary (dist/pim_calc-go)
	$(MAKE) -C go build

build-mojo: ## Build the pure Mojo CLI binary (dist/pim_calc-mojo-pure)
	$(MAKE) -C mojo build

build-python: ## Build the python package (wheel + sdist into dist/)
	uv build --project python --out-dir dist

install: ## Editable-install the python package (uv)
	$(MAKE) -C python install

######### RUN #########

run-python-cli: ## Run python CLI: CALC_ARGS="2152,1932 -r 1752,1900"
	$(MAKE) -C python run-cli

run-python-gui: ## Run the Qt GUI
	$(MAKE) -C python run-gui

run-go-cli: ## Build & run the go CLI
	$(MAKE) -C go run-cli CALC_ARGS="$(CALC_ARGS)"

run-mojo-cli: ## Build & run the pure Mojo CLI binary: CALC_ARGS="2152,1932 -r 1752,1900"
	$(MAKE) -C mojo run-mojo-cli CALC_ARGS="$(CALC_ARGS)"

run-mojo-py-cli: ## Run the mojo wrapper CLI (python interop): CALC_ARGS="2152,1932 -r 1752,1900"
	$(MAKE) -C mojo run-mojo-py-cli CALC_ARGS="$(CALC_ARGS)"

######### CLEAN #########

clean: ## Remove build and cache artifacts
	$(MAKE) -C python clean
	$(MAKE) -C go clean
	$(MAKE) -C mojo clean
	rm -rf dist .pytest_cache .ruff_cache .coverage
	rm -rf tests/__pycache__ web/__pycache__ __pycache__
