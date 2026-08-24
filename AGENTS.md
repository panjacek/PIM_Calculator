# AGENTS.md

## Principles

- KISS always. Smallest change that works. No abstractions "for later".
- Do not reinvent the wheel. Use existing libs, tools, targets, patterns already in the repo before writing new ones.
- Match existing conventions per language (python/, go/, mojo/ each have own style).

## Project layout

- `python/` — reference implementation (PIMCalc class, CLI, Qt GUI, pytest)
- `go/` — standalone CLI port
- `mojo/` — pure native port (`pim_calc.mojo`, `cli.mojo`) plus CPython-interop wrapper (`*_py.mojo`); `run-mojo-cli` builds & runs the compiled binary
- `web/` — streamlit UI driving all flavours via shared JSON contract
- `docs/plans/` — implementation plans live here (one md file per plan)
- root `pyproject.toml` — dev env (mojo + editable pim-calculator + pytest/ruff), managed with uv

## Commands

- `make help` — list all targets with descriptions
- Full target reference: `README.md` ("Make targets"), CI details: `docs/ci.md`.
  Update those files when targets change — do not duplicate the list here.
- `uv sync --group dev --group web` — rebuild .venv (dev + streamlit deps)

## Notes

- Default python: 3.14 (pinned via root `.python-version`, honoured by uv)
- Mojo toolchain: install via `uv pip install mojo` (https://mojolang.org/install/), version pinned in pyproject.toml
- Ruff: N999 ignored (module naming), E741 ignored (i,j,k,l,m carrier indices are domain convention)
- Python lint stack: ruff + mypy + bandit (`make lint-python`, `make lint-tests`); mypy config in both pyprojects, PySide6/scipy/qt backends stubs via overrides
- Public python API is fully typed (PEP 695 type aliases in pim_calc.py); keep new code annotated
- All build artifacts land in root `dist/` (gitignored): `pim_calc-go`,
  `pim_calc-mojo-pure`, python wheel + sdist; removed by `make clean`
