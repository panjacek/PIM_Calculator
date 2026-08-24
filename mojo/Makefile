MODULAR_DEBUG=stack-trace-on-error

.PHONY: test lint format build run-mojo-cli run-mojo-py-cli clean

test:
	PYTHONPATH=../python uv run mojo run -I . test_pim_calc_py.mojo
	uv run mojo run -I . test_pim_calc.mojo

lint:
	uv run mblack --check *.mojo

format:
	uv run mblack *.mojo

# All build artifacts land in the shared root dist/ directory.
DIST := ../dist
BIN := $(DIST)/pim_calc-mojo-pure
SRC := cli.mojo pim_calc.mojo

build: $(BIN)

$(BIN): $(SRC)
	mkdir -p $(DIST)
	uv run --project .. mojo build -I . cli.mojo -o $@

run-mojo-cli: $(BIN)
	$(BIN) $(CALC_ARGS)

run-mojo-py-cli:
	export MODULAR_DEBUG=$(MODULAR_DEBUG) \
		&& uv run mojo run pim_calc_py.mojo $(CALC_ARGS)

clean:
	rm -rf build $(BIN)
