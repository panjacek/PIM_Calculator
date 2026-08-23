# PIM Calculator

Passive Intermodulation calculator for RF antenna systems. Computes IM3/IM5
mixing products of multiple TX carriers, including their occupied bandwidth,
and checks whether they land inside an RX band (FDD uplink desense).
Implemented in three interchangeable flavours that are kept in lockstep by a
cross-flavour integration test in CI.

[![CI](https://github.com/panjacek/PIM_Calculator/actions/workflows/ci.yml/badge.svg)](https://github.com/panjacek/PIM_Calculator/actions/workflows/ci.yml)

## What is PIM?

[Passive Intermodulation](https://en.wikipedia.org/wiki/Passive_intermodulation):
unwanted mixing products created when multiple strong TX carriers pass through
a non-linear passive component (antenna, connector). Details and formulas:
[`docs/pim.md`](docs/pim.md).

## Flavours

Each flavour is a self-contained implementation of the same calculator —
pick whichever fits your environment; you do **not** need all of them.

| flavour | directory | description | requires |
| ------- | --------- | ----------- | -------- |
| Python  | `python/` | Reference implementation: PIMCalc class, CLI, Qt GUI, pytest suite | [uv](https://docs.astral.sh/uv/) only (Python >= 3.12) |
| Go      | `go/`     | Standalone CLI port, no external dependencies | Go >= 1.25 |
| Mojo    | `mojo/`   | Pure native port plus a wrapper around the Python library via CPython interop | [uv](https://docs.astral.sh/uv/) only (Mojo toolchain comes with the root dev env) |

CI keeps all flavours in lockstep via a cross-flavour integration test, but
locally nothing forces you to build more than one: no Go on your host simply
means you skip the `go/` flavour and its make targets.

## Quick start

```bash
uv sync --group dev                      # root env: python package + mojo toolchain
make run-python-cli CALC_ARGS="2152,1932 -r 1752,1900"
make run-mojo-cli CALC_ARGS="2152,1932 -r 1752,1900"   # pure mojo binary
```

Go flavour (only if you want it):

```bash
make run-go-cli CALC_ARGS="2152,1932 -r 1752,1900"     # builds dist/pim_calc-go first
```

Notes: Python >= 3.14 is pinned via `.python-version` and fetched
automatically by uv. `make test` / `make lint` / `make test-integration`
span every flavour and therefore need all toolchains installed.

## CLI usage

Same arguments for the python and mojo flavours:

```
pim_calc [-h] [--tx_size TX_SIZE] [-r RX_LIST] [--rx_size RX_SIZE]
         [--output_file OUTPUT_FILE] [--log_lvl LOG_LVL]
         tx_list
```

| argument | description |
| -------- | ----------- |
| tx_list (positional) | List of TX carriers, e.g. `2152,1932` |
| --tx_size TX_SIZE | TX carrier bandwidths in MHz [5 per carrier] |
| -r RX_LIST, --rx_list RX_LIST | List of RX carriers |
| --rx_size RX_SIZE | RX carrier bandwidths in MHz [5 per carrier] |
| --output_file PATH | Write results as JSON (schema below) |
| --log_lvl LOG_LVL | logger level to display [INFO] |

The go flavour uses flags instead:
`pim_calc -tx_band "5,5" -rx_list "1752,1900" -rx_band "5,5" 2152,1932`
(band lists are always explicit there — no auto-expansion).

JSON output (identical schema in all flavours):

```json
{
  "tx_list": [2152.0, 1932.0],
  "rx_list": [1752.0, 1900.0],
  "IM3": [{"cf": 1712.0, "min": 1704.5, "max": 1719.5}],
  "IM5": [{"cf": 1492.0, "min": 1479.5, "max": 1504.5}]
}
```

## GUI (optional)

The Qt GUI is an extra — the CLI and library work without it:

```bash
pip install "pim-calculator[gui]"    # users: pulls PySide6, scipy, matplotlib
make run-python-gui                  # dev shortcut (uv sync --extra gui)
```

Core install (`pip install pim-calculator`) needs only numpy.

## Make targets

Run `make help` for the full annotated list. The essentials:

- `make test` - all suites: unit (python/go/mojo) + integration + perf
- `make test-unit` - unit suites only, fast loop
- `make test-perf` - performance benchmarks (`pytest-benchmark`; SVG
  histograms + JSON report land in `python/.benchmarks/`)
- `make lint` / `make format` - linters / auto-format for all flavours
  (python side: ruff + mypy + bandit)
- `make sync` - upgrade dep versions & re-lock/re-sync all flavours
  (root uv env, python/, go/)
- `make test-integration` - cross-flavour comparison (see [`docs/ci.md`](docs/ci.md))
- `make run-python-cli CALC_ARGS="..."`, `make run-go-cli`,
  `make run-mojo-cli CALC_ARGS="..."` (pure Mojo, compiles a native binary
  first; `run-mojo-py-cli` for the python-interop wrapper) - the CLIs
- `make build` - build all packages: go/mojo CLI binaries + python wheel/sdist
  (`make build-go`, `make build-mojo`, `make build-python` for individual
  flavours), `make install`, `make clean`

## Development environment

Root `pyproject.toml` defines a uv-managed dev environment with the Mojo
toolchain, the editable `pim-calculator` package, pytest and ruff:

```bash
uv sync --group dev
```

Mojo toolchain: https://mojolang.org/install/ (installed as the pinned
`mojo==1.0.0` dependency of the root project).

## Documentation

- [`docs/pim.md`](docs/pim.md) - what PIM is, which products are computed,
  how RX hit checks work
- [`docs/ci.md`](docs/ci.md) - CI pipeline: job graph, integration test case,
  local reproduction
- [`docs/versioning.md`](docs/versioning.md) - semver strategy exploration
  for the three flavours
