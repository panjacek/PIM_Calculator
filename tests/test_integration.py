"""Cross-flavour smoke test: python/go/mojo must compute identical PIM sets.

Runs all four CLIs on several cases, collecting each flavour's
--output_file JSON and asserting:

Canonical case (TX 2152,1932 / RX 1752,1900, default 5 MHz bands):

1. every flavour yields the set of IM centre frequencies known for this
   case: IM3 {1712, 1932, 2152, 2372} plus IM5-only {1492, 2592},
2. all flavours agree with each other,
3. full (cf, min, max) rows agree across flavours (band math), and
4. per-flavour row counts match known semantics (python keeps duplicate
   cf rows for distinct TX sources; go dedups by cf value only).

Additional cases (known divergences asserted explicitly):

- TX echo / RX echo round-trip in the payload,
- no RX given: python/mojo echo [], go injects its default [1900],
- n=3 TX: centres and row sets agree, counts differ by go dedupe,
- single TX: go emits one self-product row, python/mojo emit none.

JSON output contract (shared by all flavours, see
docs/json-contract.md):

    {"tx_list": [...], "rx_list": [...],
     "IM3": [{"cf": .., "min": .., "max": ..}, ...],
     "IM5": [...]}

Run via `make test-integration` (builds the go binary first); needs the
root uv environment (`uv sync --group dev`) plus the go toolchain.
"""

import json
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent

TX = "2152,1932"
RX = "1752,1900"
TX3 = "2152,1932,1980"

EXPECTED = {1492.0, 1712.0, 1932.0, 2152.0, 2372.0, 2592.0}


def _run(cmd: list[str], cwd: Path) -> None:
    proc = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, check=False)
    assert proc.returncode == 0, (
        f"{' '.join(cmd)} failed:\n{proc.stdout}\n{proc.stderr}"
    )


def _centres(payload: dict) -> set[float]:
    return {float(row["cf"]) for row in payload["IM3"] + payload["IM5"]}


Row = tuple[float, float, float]


def _rows(payload: dict, order: str) -> set[Row]:
    """Full (cf, min, max) triples for one IM order."""
    return {(float(r["cf"]), float(r["min"]), float(r["max"])) for r in payload[order]}


# Row counts differ by flavour semantics: python keeps duplicate-cf rows
# when TX source components differ; go dedups by cf value only.
EXPECTED_COUNTS = {
    "python": (4, 10),
    "go": (4, 6),
    "mojo": (4, 10),
    "mojo_pure": (4, 10),
}


def _run_case(tx: str, rx: str | None, out: Path) -> dict[str, dict]:
    """Run all four CLIs on one case, parse their JSON output by flavour."""
    n_tx = len(tx.split(","))
    n_rx = len(rx.split(",")) if rx else 0
    cmds: dict[str, tuple[list[str], Path]] = {
        "python": (
            ["uv", "run", "--project", ".", "PIM_Calculator", tx]
            + ([f"--rx_list={rx}"] if rx else [])
            + [f"--output_file={out / 'python.json'}"],
            ROOT / "python",
        ),
        "go": (
            [str(ROOT / "dist" / "pim_calc-go"), "-tx_band", ",".join(["5"] * n_tx)]
            + (["-rx_list", rx, "-rx_band", ",".join(["5"] * n_rx)] if rx else [])
            + ["-output_file", str(out / "go.json"), tx],
            ROOT,
        ),
        "mojo": (
            ["uv", "run", "mojo", "run", "-I", ".", "pim_calc_py.mojo", tx]
            + (["-r", rx] if rx else [])
            + ["--output_file", str(out / "mojo.json")],
            ROOT / "mojo",
        ),
        "mojo_pure": (
            ["uv", "run", "mojo", "run", "-I", ".", "cli.mojo", tx]
            + (["-r", rx] if rx else [])
            + ["--output_file", str(out / "mojo_pure.json")],
            ROOT / "mojo",
        ),
    }
    for cmd, cwd in cmds.values():
        _run(cmd, cwd)
    return {name: json.loads((out / f"{name}.json").read_text()) for name in cmds}


@pytest.fixture(scope="module")
def results(tmp_path_factory: pytest.TempPathFactory) -> dict[str, dict]:
    """Canonical case: TX 2152,1932 / RX 1752,1900."""
    return _run_case(TX, RX, tmp_path_factory.mktemp("integration"))


@pytest.fixture(scope="module")
def single_tx(tmp_path_factory: pytest.TempPathFactory) -> dict[str, dict]:
    return _run_case("1900", RX, tmp_path_factory.mktemp("single_tx"))


@pytest.fixture(scope="module")
def no_rx(tmp_path_factory: pytest.TempPathFactory) -> dict[str, dict]:
    return _run_case(TX, None, tmp_path_factory.mktemp("no_rx"))


@pytest.fixture(scope="module")
def three_tx(tmp_path_factory: pytest.TempPathFactory) -> dict[str, dict]:
    return _run_case(TX3, RX, tmp_path_factory.mktemp("three_tx"))


def test_matches_known_truth(results: dict[str, dict]) -> None:
    for name, payload in results.items():
        freqs = _centres(payload)
        assert freqs == EXPECTED, (
            f"{name}: missing={sorted(EXPECTED - freqs)} "
            f"unexpected={sorted(freqs - EXPECTED)}"
        )


def test_flavours_agree(results: dict[str, dict]) -> None:
    centres = {name: _centres(p) for name, p in results.items()}
    distinct = {frozenset(c) for c in centres.values()}
    assert len(distinct) == 1, {name: sorted(c) for name, c in centres.items()}


def test_row_values_match_python(results: dict[str, dict]) -> None:
    """Band math must agree per row, not just at centre frequencies."""
    py_rows = {order: _rows(results["python"], order) for order in ("IM3", "IM5")}
    for name in ("go", "mojo", "mojo_pure"):
        for order in ("IM3", "IM5"):
            assert _rows(results[name], order) == py_rows[order], (
                f"{name}/{order} rows differ from python"
            )


def test_row_counts(results: dict[str, dict]) -> None:
    """Duplicate-row regression guard (per-flavour semantics)."""
    for name, payload in results.items():
        counts = (len(payload["IM3"]), len(payload["IM5"]))
        assert counts == EXPECTED_COUNTS[name], (
            f"{name}: rows {counts}, want {EXPECTED_COUNTS[name]}"
        )


def test_tx_rx_echo(results: dict[str, dict]) -> None:
    """Payload echoes the inputs that produced it."""
    for name, payload in results.items():
        assert [float(x) for x in payload["tx_list"]] == [2152.0, 1932.0], name
        assert [float(x) for x in payload["rx_list"]] == [1752.0, 1900.0], name


def test_no_rx_case(no_rx: dict[str, dict]) -> None:
    """No RX given: python/mojo echo [], go injects default [1900] (known).

    Computation must still agree across flavours either way.
    """
    echoes = {
        name: [float(x) for x in payload["rx_list"]] for name, payload in no_rx.items()
    }
    assert echoes == {"python": [], "mojo": [], "mojo_pure": [], "go": [1900.0]}

    distinct = {frozenset(_centres(p)) for p in no_rx.values()}
    assert len(distinct) == 1, {n: sorted(_centres(p)) for n, p in no_rx.items()}


def test_three_tx_case(three_tx: dict[str, dict]) -> None:
    """n=3 TX: centres + row sets agree everywhere, counts differ (go dedupe)."""
    distinct = {frozenset(_centres(p)) for p in three_tx.values()}
    assert len(distinct) == 1, {n: sorted(_centres(p)) for n, p in three_tx.items()}
    assert len(next(iter(distinct))) == 27

    py_rows = {order: _rows(three_tx["python"], order) for order in ("IM3", "IM5")}
    for name in ("go", "mojo", "mojo_pure"):
        for order in ("IM3", "IM5"):
            assert _rows(three_tx[name], order) == py_rows[order], (
                f"{name}/{order} rows differ from python"
            )

    counts = {n: (len(p["IM3"]), len(p["IM5"])) for n, p in three_tx.items()}
    assert counts["python"] == counts["mojo"] == counts["mojo_pure"] == (15, 57)
    assert counts["go"] == (12, 27)


def test_single_tx_case(single_tx: dict[str, dict]) -> None:
    """Single TX: go emits one self-product, python/mojo emit none (known)."""
    counts = {n: (len(p["IM3"]), len(p["IM5"])) for n, p in single_tx.items()}
    assert counts == {
        "python": (0, 0),
        "go": (1, 1),
        "mojo": (0, 0),
        "mojo_pure": (0, 0),
    }
    assert _centres(single_tx["go"]) == {1900.0}
    for name in ("python", "mojo", "mojo_pure"):
        assert _centres(single_tx[name]) == set(), name

    for name, payload in single_tx.items():
        assert [float(x) for x in payload["tx_list"]] == [1900.0], name
        assert [float(x) for x in payload["rx_list"]] == [1752.0, 1900.0], name
