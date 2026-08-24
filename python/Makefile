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
	uv sync --extra gui --project .
	uv run --project . pytest PIM_Calculator/tests/test_pimQt.py -o python_files=test_pimQt.py

lint:
	uv run ruff check .
	uv run mypy PIM_Calculator
	uv run bandit -r PIM_Calculator --exclude PIM_Calculator/tests

format:
	uv run ruff format .

install:
	uv pip install -e .

sync:
	uv lock --project . --upgrade
	uv sync --project . --group dev

run-cli:
	uv run --project . PIM_Calculator 2152,1932 --rx_list=1752,1900


run-gui:
	uv sync --extra gui --project .
	LIBGL_ALWAYS_SOFTWARE=1 ./.venv/bin/PIM_GUI_Calculator



clean:

	-rm -rf .pytest_cache .benchmarks *.egg-info build dist
