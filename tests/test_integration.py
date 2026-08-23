"""Cross-flavour smoke test: python/go/mojo must compute identical PIM sets.

Runs all three CLIs on one canonical case (TX 2152,1932 / RX 1752,1900,
default 5 MHz bands), collecting each flavour's --output_file JSON and
asserting:

1. every flavour yields the set of IM centre frequencies known for this
   case: IM3 {1712, 1932, 2152, 2372} plus IM5-only {1492, 2592},
2. all flavours agree with each other,
3. full (cf, min, max) rows agree across flavours (band math), and
4. per-flavour row counts match known semantics (python keeps duplicate
   cf rows for distinct TX sources; go dedups by cf value only).

JSON output contract (shared by all flavours, see
python/PIM_Calculator/pim_calc.py::results_to_json):

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
EXPECTED_COUNTS = {"python": (4, 10), "go": (4, 6), "mojo": (4, 10)}


@pytest.fixture(scope="module")
def results(tmp_path_factory: pytest.TempPathFactory) -> dict[str, dict]:
    """Run the three CLIs on the canonical case, parse their JSON output."""
    out = tmp_path_factory.mktemp("integration")

    _run(
        [
            "uv",
            "run",
            "--project",
            ".",
            "PIM_Calculator",
            TX,
            f"--rx_list={RX}",
            f"--output_file={out / 'python.json'}",
        ],
        cwd=ROOT / "python",
    )
    _run(
        [
            "./pim_calc",
            "-tx_band",
            "5,5",
            "-rx_list",
            RX,
            "-rx_band",
            "5,5",
            "-output_file",
            str(out / "go.json"),
            TX,
        ],
        cwd=ROOT / "go",
    )
    _run(
        [
            "uv",
            "run",
            "mojo",
            "run",
            "-I",
            ".",
            "pim_calc.mojo",
            TX,
            "-r",
            RX,
            "--output_file",
            str(out / "mojo.json"),
        ],
        cwd=ROOT / "mojo",
    )

    return {
        path.stem: json.loads(path.read_text()) for path in sorted(out.glob("*.json"))
    }


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
    for name in ("go", "mojo"):
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
