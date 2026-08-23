# Versioning (Semver) — Exploration

Status: **thinking document, no tooling implemented yet.**

## Current state

| Flavour | Where version lives        | Current value |
|---------|----------------------------|---------------|
| python  | `python/pyproject.toml`    | `0.2`         |
| go      | nothing                    | —             |
| mojo    | root `pyproject.toml`¹     | `0.2`         |
| repo    | git tags                   | none          |

¹ Root manifest is the dev environment for the mojo wrapper, not really a
product version.

None of these are proper semver (`X.Y.Z`) yet, and the two `0.2` values are
independent numbers that happen to match.

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
6. **Automation:** manual `git tag vX.Y.Z` + `CHANGELOG.md` entry vs
   release-please / changesets. Manual first, automate when it hurts.
7. **Pre-1.0 policy:** while in `0.x`, semver allows breaking changes in
   MINOR bumps (`0.3.0` may break `0.2.x`). Fine until the python API
   stabilises; going `1.0.0` is a promise, not a milestone party.
8. **Changelog granularity:** single `CHANGELOG.md` with a "Flavours
   affected:" line per release keeps it KISS.

## Working recommendation (for future decision)

- Single repo version, source of truth = root `VERSION` file.
- Tag `vX.Y.Z`; annotate which flavour(s) changed in the tag message and
  changelog.
- Bump rules: same as standard semver, applied to the union of flavour
  changes (any flavour breaking → MINOR bump while in 0.x).
- Revisit per-flavour versioning when mojo goes standalone.

## First concrete steps (when decided)

1. Rename both manifests to real semver (`0.2.0`), add `VERSION` at root.
2. Add `CHANGELOG.md` (Keep a Changelog format).
3. Optional CI job later: verify `VERSION`, manifests and latest tag agree.
