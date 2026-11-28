# Versioning (Semver) — Exploration

Status: **implemented for `0.4.1`.** Root `VERSION` is the source of truth, all
manifests aligned to it. No changelog file: release notes go in the annotated
`vX.Y.Z` tag message. Tag `v0.4.1` pending (manual, on explicit instruction).

## Current state

| Flavour | Where version lives        | Current value |
|---------|----------------------------|---------------|
| repo    | root `VERSION`             | `0.4.1`       |
| python  | `python/pyproject.toml`    | `0.4.1`       |
| qt gui  | `python/PIM_Calculator/pimQt.py` | `0.4.1` |
| go      | nothing                    | —             |
| mojo    | root `pyproject.toml`¹     | `0.4.1`       |
| tags    | git tags                   | none          |

¹ Root manifest is the dev environment for the mojo wrapper, not really a
product version.

All versioned files are aligned to `0.4.1`, with root `VERSION` as the
single source of truth.

## Questions to answer before implementing

1. **One version or three?**
   - *Single repo version* (`vX.Y.Z` tag covers all flavours): simplest,
     fits a monorepo where flavours ship together. Recommended start.
   - *Per-flavour tags* (`python-v1.2.0`, `go-v0.3.0`, ...): only worth it
     when flavours release on independent cadences.
2. **Where is the source of truth?** Options: a root `VERSION` file read by
   release scripts; the root manifest; per-flavour manifests kept in sync
   manually. One file, one bump command.
3. **What does MAJOR mean per flavour?**
   - python lib: public API change (`PIMCalc`, CLI flags).
   - go: CLI flag/output format change.
   - mojo: wrapper CLI contract change.
4. **Shared-core coupling:** go reimplements the algorithm; mojo calls the
   python lib. If the core math changes behaviour (e.g. band handling),
   every flavour's results change. Does a "math" fix bump all flavours?
   The cross-flavour integration job in CI is exactly the guardrail that
   detects such drift.
5. **Mojo split point:** mojo is planned to become a standalone app next to
   being a wrapper. That is the natural moment to give it its own version.
6. **Automation:** manual `git tag vX.Y.Z` with release notes vs
   release-please / changesets. Manual first, automate when it hurts.
7. **Pre-1.0 policy:** while in `0.x`, semver allows breaking changes in
   MINOR bumps (`0.3.0` may break `0.2.x`). Fine until the python API
   stabilises; going `1.0.0` is a promise, not a milestone party.
8. **Changelog granularity:** single annotated tag message with a "Flavours
   affected:" line per release keeps it KISS.

## Working recommendation (for future decision)

- Single repo version, source of truth = root `VERSION` file.
- Tag `vX.Y.Z`; annotate which flavour(s) changed in the tag message and
  changelog.
- Bump rules: same as standard semver, applied to the union of flavour
  changes (any flavour breaking → MINOR bump while in 0.x).
- Revisit per-flavour versioning when mojo goes standalone.

## First concrete steps (done for `0.4.1`)

1. Manifests use real semver (`0.4.1`), root `VERSION` added.
2. Version bumped by hand in all three places + `uv lock`.
3. Optional CI job later: verify `VERSION`, manifests and latest tag agree.
