# Contributing

## Setup

Needs [uv](https://docs.astral.sh/uv/) and Go 1.25+ (`~/.local/go/bin` if
installed by hand). Mojo comes from the pinned `mojo` dependency.

```bash
uv sync --group dev --group web   # dev + streamlit deps
make build-go                     # dist/pim_calc-go
```

Qt GUI needs extra system libs; see the `ImportError` message in
`python/PIM_Calculator/pimQt.py` for the exact apt list.

## Before sending a change

```bash
make lint            # ruff + mypy + bandit (python/tests), go vet, mblack
make test-unit       # python + go + mojo unit suites
make test-integration
make test-python-gui # needs a display or Xvfb
```

`make help` lists every target; `README.md` describes each one and
`docs/ci.md` explains what CI runs.

## Flavour parity rule

The repo ships the same calculator four ways:

| flavour | code |
|---|---|
| python | `python/PIM_Calculator/` |
| go | `go/PIM_Calculator/` |
| mojo pure | `mojo/pim_calc.mojo`, `mojo/cli.mojo` |
| mojo interop | `mojo/*_py.mojo` |

Any change to the maths, CLI flags, or JSON output must land in all flavours
in the same PR, or be documented as a known divergence in
`docs/json-contract.md`. `tests/test_integration.py` is the guardrail: it
runs all CLIs on the same inputs and asserts agreement.

Known go divergences (float32, CF-only dedupe, default RX list, panics on bad
input) are intentional and documented, not bugs. Do not "fix" them without
a separate decision.

## Style

- Python: `ruff format` + `ruff check`, full type annotations on public API.
- Go: default `gofmt`.
- Mojo: `mblack`.
- No dead code, no commented-out blocks.

## Versioning

`VERSION` at the root is the single source of truth; manifests must match it.
Release notes live in the annotated `vX.Y.Z` tag message, not a changelog file.
