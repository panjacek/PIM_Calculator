# CI Pipeline

Single workflow: `.github/workflows/ci.yml`. Triggers: push to `main`, PRs to
`main`, manual dispatch. Stale runs on the same ref are cancelled.

## Job graph

```
python-lint (ruff)  ──┬──> python-gui (xvfb, PySide6) ──┐
python-unit (pytest) ─┘                                │
go-lint (go vet) ───────────────────────────┐          │
go-test ────────────────────────────────────┼──────────┼──> integration
mojo-lint (mblack) ──> mojo-test ───────────┘          │    (3 CLIs, one case)
                       (also needs python-lint+unit)   │
```

- `python-lint`, `python-unit`, `go-lint`, `go-test`, `mojo-lint` start
  immediately and run in parallel.
- `mojo-lint` feeds `mojo-unit`: unit tests only run on lint-clean mojo code.
  `mojo-test` additionally waits for the python flavour to be lint-clean and
  unit-green first (mojo wraps the python library).
- `python-gui` waits for the python flavour too (GUI tests are slow).
- `integration` needs all seven jobs green.

## Jobs

| Job         | What it does                                              |
|-------------|-----------------------------------------------------------|
| python-lint | `make lint-python` (ruff)                                 |
| python-unit | `make test-python-unit` (pytest, GUI tests excluded)      |
| python-gui  | `xvfb-run make test-python-gui` (PySide6 under Xvfb)      |
| go-lint     | `make lint-go` (`go vet`)                                 |
| go-test     | `make test-go`                                            |
| mojo-lint   | `make lint-mojo` (mblack)                                 |
| mojo-test   | `make test-mojo` (Mojo TestSuite via CPython interop)     |
| integration | see below                                                 |

### Integration job

Runs all three CLIs on one canonical case:

```
TX = 2152,1932   RX = 1752,1900   bands default (5 MHz)
```

and asserts that each output contains every expected PIM frequency:
`1492 1712 1932 2152 2372 2592` (IM3 set plus IM5-only values).

This is a smoke-level comparison: it catches computation drift between
flavours without parsing each tool's distinct output format.

## Local reproduction

Everything CI runs is a Makefile target:

```bash
uv sync --extra dev        # root env: mojo toolchain + editable pim-calculator
uv sync --project python --group dev       # python env (add --extra gui for GUI)
make lint                  # ruff + go vet + mblack
make test-python-unit      # fast unit tests
make test-python-gui       # GUI tests (needs a display or xvfb-run)
make test-go
make test-mojo
```

Integration case by hand:

```bash
make build-go
( cd python && uv run --project . PIM_Calculator 2152,1932 --rx_list=1752,1900 )
./go/pim_calc -tx_band "5,5" -rx_list "1752,1900" 2152,1932
( cd mojo && uv run mojo run -I . pim_calc.mojo 2152,1932 -r 1752,1900 )
```

All three must print the same IM3/IM5 tables.

## Environment notes

- Python is pinned to **3.14** via root `.python-version`; uv honours it both
  locally and in CI (downloads a managed interpreter if the runner lacks one).
- Root `pyproject.toml` pins the Mojo toolchain (`mojo==1.0.0`) and installs
  `pim-calculator` editable from `python/` — this is what the mojo jobs use.
- `python/` has its own lockfile; CI syncs it per job with uv caching.
- Go version comes from `go/go.mod` via `setup-go`.
- GUI job installs the same X/GL system packages as `python/Dockerfile`
  (gui stage), including `libegl1`/`libgl1` required by PySide6.
