# Contributing

## Development environment

1. Install [uv](https://docs.astral.sh/uv/).
2. Sync the root environment (includes Mojo toolchain, editable `pim-calculator`, and web dependencies):
   ```bash
   uv sync --group dev --group web
   ```
3. Sync the Python package environment (includes GUI extras):
   ```bash
   uv sync --project python --group dev --extra gui
   ```

## Common Make targets

Run `make help` for the full list, or see `README.md` ("Make targets") and `docs/ci.md`:

- `make lint` — run linters across Python (`ruff`, `mypy`, `bandit`), Go (`go vet`), and Mojo (`mblack`).
- `make test-python-unit` — run Python unit tests.
- `make test-python-gui` — run Qt GUI tests (requires a display or `xvfb-run`).
- `make test-go` — run Go tests and benchmarks.
- `make test-mojo` — run Mojo pure and CPython-interop tests.
- `make test-integration` — run cross-flavour CLI integration tests.
- `make test-web` — run Streamlit unit and Playwright E2E tests.

## Flavour-parity rule

All CLI flavours (`python/`, `go/`, `mojo/` pure and interop) share the same `--output_file` JSON contract documented in `docs/json-contract.md`. Any change to CLI flags, JSON output fields, or core PIM calculation behaviour must be reflected across all flavours and verified with `make test-integration`.
