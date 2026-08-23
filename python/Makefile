.PHONY: test test-unit test-perf test-gui lint format install sync run-cli run-gui clean

test: test-unit

test-unit:
	uv run --project . pytest -m "not benchmark" -p no:pytest-qt --ignore=PIM_Calculator/tests/test_pimQt.py \
		--cov=PIM_Calculator --cov-report=term-missing --cov-report=xml

test-perf:
	mkdir -p .benchmarks
	uv run --project . pytest -p no:pytest-qt PIM_Calculator/tests/test_perf.py \
		--benchmark-only --benchmark-autosave \
		--benchmark-histogram=.benchmarks/hist \
		--benchmark-json=.benchmarks/report.json \
		-o python_files=test_perf.py

test-gui:
	uv run --project . pytest PIM_Calculator/tests/test_pimQt.py -o python_files=test_pimQt.py

lint:
	uv run ruff check .

format:
	uv run ruff format .

install:
	uv pip install -e .

sync:
	uv lock --project . --upgrade
	uv sync --project . --group dev

run-cli:
ifeq ($(USE_MOJO),1)
	uv run mojo run python/PIM_Calculator/pim_calc.mojo 2152,1932 --rx_list=1752,1900
else
	uv run --project . PIM_Calculator 2152,1932 --rx_list=1752,1900
endif


run-gui:
	uv run --extra gui --project . PIM_GUI_Calculator

run-mojo-cli:
	PYTHONPATH=./python uv run ../.venv/bin/mojo run ../mojo/pim_calc.mojo 2152,1932 --rx_list=1752,1900



clean:

	-rm -rf .pytest_cache .benchmarks *.egg-info build dist
