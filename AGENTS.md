# AGENTS.md

## Principles

- KISS always. Smallest change that works. No abstractions "for later".
- Do not reinvent the wheel. Use existing libs, tools, targets, patterns already in the repo before writing new ones.
- Match existing conventions per language (python/, go/, mojo/ each have own style).

## Project layout

- `python/` — reference implementation (PIMCalc class, CLI, Qt GUI, pytest)
- `go/` — standalone CLI port
- `mojo/` — Python interop wrapper (calls python lib via CPython bridge)
- `docs/plans/` — implementation plans live here (one md file per plan)
- root `pyproject.toml` — dev env (mojo + editable pim-calculator + pytest/ruff), managed with uv

## Commands

- `make help` — list all targets with descriptions
- Full target reference: `README.md` ("Make targets"), CI details: `docs/ci.md`.
  Update those files when targets change — do not duplicate the list here.
- `uv sync --group dev` — rebuild .venv

## Notes

- Default python: 3.14 (pinned via root `.python-version`, honoured by uv)
- Mojo toolchain: install via `uv pip install mojo` (https://mojolang.org/install/), version pinned in pyproject.toml
- Ruff: N999 ignored (module naming is project convention)
- Go binary `go/pim_calc` is build artifact, gitignored
