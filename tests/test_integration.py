"""Cross-flavour smoke test: python/go/mojo must compute identical PIM sets.

Runs all three CLIs on one canonical case (TX 2152,1932 / RX 1752,1900,
default 5 MHz bands), collecting each flavour's --output_file JSON and
asserting:

1. every flavour yields the set of IM centre frequencies known for this
   case: IM3 {1712, 1932, 2152, 2372} plus IM5-only {1492, 2592}, and
2. all flavours agree with each other.

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


@pytest.fixture(scope="module")
def results(tmp_path_factory: pytest.TempPathFactory) -> dict[str, set[float]]:
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
        path.stem: _centres(json.loads(path.read_text()))
        for path in sorted(out.glob("*.json"))
    }


def test_matches_known_truth(results: dict[str, set[float]]) -> None:
    for name, freqs in results.items():
        assert freqs == EXPECTED, (
            f"{name}: missing={sorted(EXPECTED - freqs)} "
            f"unexpected={sorted(freqs - EXPECTED)}"
        )


def test_flavours_agree(results: dict[str, set[float]]) -> None:
    distinct = {frozenset(freqs) for freqs in results.values()}
    assert len(distinct) == 1, {name: sorted(f) for name, f in results.items()}
