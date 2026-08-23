MODULAR_DEBUG=stack-trace-on-error

.PHONY: test lint format run-mojo-cli

test:
	PYTHONPATH=../python uv run mojo run -I . test_pim_calc.mojo

lint:
	uv run mblack --check *.mojo

format:
	uv run mblack *.mojo

run-mojo-cli:
	export MODULAR_DEBUG=$(MODULAR_DEBUG) \
		&& uv run mojo run pim_calc.mojo $(CALC_ARGS)
