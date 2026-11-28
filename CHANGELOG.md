# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.4.0] - Unreleased

Flavours affected: python, go, mojo, web, docs.

### Added
- Root `VERSION` file as the single source of truth (`0.4.0`).
- `docs/json-contract.md` defining the shared `--output_file` JSON schema across all flavours.
- `CHANGELOG.md` and `CONTRIBUTING.md`.
- Go internal tests for `write_results` and `read_args`, plus `-bench . -benchmem` in `go/Makefile`.
- Cross-flavour integration test cases for single TX, no RX, `n=3` TX, and `tx_list`/`rx_list` echo.
- Qt GUI unit tests in `python/PIM_Calculator/tests/test_pimQt.py`.

### Changed
- Aligned version strings to `0.4.0` across `VERSION`, `pyproject.toml`, `python/pyproject.toml`, and `python/PIM_Calculator/pimQt.py`.
- Python CLI now exits non-zero on invalid float arguments or unwritable `--output_file`.
- Updated `README.md`, `docs/ci.md`, `docs/versioning.md`, `docs/pim.md`, and `AGENTS.md`.

### Removed
- Dead code and unused parameters/imports in `pim_calc.py`, `pimQt.py`, and `go/PIM_Calculator/`.
- Obsolete `python/bin/` wrapper scripts and `python/setup.cfg`.
- "Show IM source" checkbox from the Qt GUI.
