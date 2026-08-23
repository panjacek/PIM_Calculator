PIM Calculator
==============

Calculate PIM for RF antennas

[![CI](https://github.com/panjacek/PIM_Calculator/actions/workflows/ci.yml/badge.svg)](https://github.com/panjacek/PIM_Calculator/actions/workflows/ci.yml)

## What is PIM?

[Passive Intermodulation](https://en.wikipedia.org/wiki/Passive_intermodulation):
unwanted mixing products created when multiple strong TX carriers pass through
a non-linear passive component (antenna, connector). This tool computes the
IM3/IM5 products and checks if they land inside an RX band (FDD). Details:
[`docs/pim.md`](docs/pim.md).

Three flavours:
===============

| flavour | directory | description |
| ------- | --------- | ----------- |
| Python  | `python/` | Reference implementation: PIMCalc class, CLI, Qt GUI, pytest suite |
| Go      | `go/`     | Standalone CLI port, no external dependencies |
| Mojo    | `mojo/`   | Wrapper around the Python library via CPython interop |

All three share the same core math (see [`docs/pim.md`](docs/pim.md)).

CLI usage (same arguments for python and mojo flavours):
========================================================

**pim_calc** [-h] [--tx_size TX_SIZE] [-r RX_LIST] [--rx_size RX_SIZE]
             [--log_lvl LOG_LVL]
             tx_list

Calculates PIM for RF antennas with FDD

| positional | description |
| ---------- | ----------- |
| tx_list    | List of TX Carriers |


| optional argument | description |
| ----------------- | ----------- |
| -h, --help        | show this help message and exit |
| --tx_size TX_SIZE | List of TX Carriers bands [5MHz] |
| -r RX_LIST, --rx_list RX_LIST | List of RX Carriers |
| --rx_size RX_SIZE | List of RX Carriers bands [5MHz] |
| --log_lvl LOG_LVL | logger level to display [INFO] |

Example:

    make run-python-cli CALC_ARGS="1900,1910 -r 1915"

Makefile Usage:
===============

You can use `make` from the root directory (`make help` lists all targets):

- `make test` - Run all test suites (python/go/mojo)
- `make lint` - Run linters for all flavours (ruff / go vet / mblack)
- `make test-integration` - Cross-flavour comparison (see `docs/ci.md`)
- `make test-python-unit` - Python unit tests (GUI tests excluded)
- `make test-python-gui` - Python Qt GUI tests (needs a display or xvfb-run)
- `make run-python-cli CALC_ARGS="..."` - Execute Python CLI
- `make run-python-gui` - Execute Qt GUI
- `make run-go-cli` - Execute Go CLI
- `make run-mojo-cli CALC_ARGS="..."` - Execute Mojo wrapper CLI
- `make build-go` - Build Go binary
- `make install` - Install the Python package in editable mode using `uv`
- `make clean` - Clean build and cache files

Development environment
=======================

Root `pyproject.toml` defines a uv-managed dev environment with the Mojo
toolchain, the editable `pim-calculator` package, pytest and ruff:

    uv sync --group dev

Mojo toolchain is installed as described in https://mojolang.org/install/
(`uv pip install mojo`, version pinned in `pyproject.toml`).

Documentation
=============

- [`docs/pim.md`](docs/pim.md) - What PIM is, which products are computed,
  how RX hit checks work
- [`docs/ci.md`](docs/ci.md) - CI pipeline: job graph, integration test case,
  how to reproduce locally
- [`docs/versioning.md`](docs/versioning.md) - Semver strategy exploration
  for the three flavours
