"""Engine layer for the streamlit web UI.

Pure logic, no streamlit imports, so unit tests stay headless and fast.
Every engine (python/go/mojo/mojo_py) is driven through the shared JSON
contract (see python/PIM_Calculator/pim_calc.py::results_to_json):
python runs in-process, the others via their CLIs writing to a temp file
with the same command lines used by tests/test_integration.py
(mojo = pure native cli.mojo port, mojo_py = CPython-interop wrapper).

RX-hit checking is reimplemented here as simple interval overlap because
the shared JSON contract does not yet carry rx_hits (see plan TODO).
"""

from __future__ import annotations

import json
import subprocess
import tempfile
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from PIM_Calculator.pim_calc import PIMCalc, results_to_json

ROOT = Path(__file__).resolve().parent.parent

ENGINE_HINTS = {
    "go": "needs dist/pim_calc-go binary (make build-go)",
    "mojo": "needs mojo toolchain",
    "mojo_py": "needs mojo toolchain",
}

# Pseudo-carrier shapes ported from python/PIM_Calculator/pimQt.py.
SHAPE_IM = np.array(
    [0.2, 0.4, 0.50, 0.55, 0.58, 0.6, 0.6, 0.6, 0.6, 0.6, 0.58, 0.55, 0.50, 0.4, 0.2]
)
SHAPE_CARRIER = np.array(
    [0.2, 0.5, 0.9, 0.99, 1, 1, 1, 1, 1, 1, 1, 0.99, 0.9, 0.5, 0.2]
)

_mojo_cache: bool | None = None


def parse_rows(rows: pd.DataFrame) -> tuple[list[float], list[float]]:
    """Editor dataframe -> (freqs, bandwidths); rejects empty cells."""
    if len(rows) < 1:
        raise ValueError("Need at least one carrier")
    if rows.isna().any().any():
        raise ValueError("Empty cells: fill Frequency/Bandwidth for every row")
    freqs = [float(x) for x in rows["Frequency"]]
    bws = [float(x) for x in rows["Bandwidth"]]
    return freqs, bws


def rx_hits_for(
    order_rows: list[dict[str, float]],
    rx_freqs: list[float],
    rx_bws: list[float],
) -> list[dict[str, Any]]:
    """PIM rows hitting any RX band via plain interval overlap."""
    hits: list[dict[str, Any]] = []
    for row in order_rows:
        for f, bw in zip(rx_freqs, rx_bws):
            rx_min, rx_max = f - bw / 2.0, f + bw / 2.0
            if row["min"] <= rx_max and row["max"] >= rx_min:
                hits.append({**row, "rx": f})
    return hits


def order_table(
    order_rows: list[dict[str, float]], hits: list[dict[str, float]]
) -> pd.DataFrame:
    """Table frame for one IM order with an rx-hit flag per row."""
    hit_keys = {(h["cf"], h["min"], h["max"]) for h in hits}
    return pd.DataFrame(
        [
            {
                "cf": r["cf"],
                "min": r["min"],
                "max": r["max"],
                "RX hit": (r["cf"], r["min"], r["max"]) in hit_keys,
            }
            for r in order_rows
        ]
    )


def engine_available(name: str, root: Path = ROOT) -> bool:
    global _mojo_cache
    if name == "python":
        return True
    if name == "go":
        return (root / "dist" / "pim_calc-go").is_file()
    if name in ("mojo", "mojo_py"):
        if _mojo_cache is None:
            _mojo_cache = _probe_mojo(root)
        return _mojo_cache
    return False


def _probe_mojo(root: Path) -> bool:
    try:
        proc = subprocess.run(
            ["uv", "run", "mojo", "--version"],
            cwd=root / "mojo",
            capture_output=True,
            check=False,
        )
    except OSError:
        return False
    return proc.returncode == 0


def go_cmd(
    out_file: Path,
    tx: str,
    tx_band: str,
    rx: str,
    rx_band: str,
    root: Path = ROOT,
) -> list[str]:
    """Command line mirroring tests/test_integration.py (go flavour)."""
    return [
        str(root / "dist" / "pim_calc-go"),
        "-tx_band",
        tx_band,
        "-rx_list",
        rx,
        "-rx_band",
        rx_band,
        "-output_file",
        str(out_file),
        tx,
    ]


def mojo_cmd(out_file: Path, tx: str, rx: str, tx_band: str, rx_band: str) -> list[str]:
    """Pure native port (cli.mojo), mirroring tests/test_integration.py."""
    return [
        "uv",
        "run",
        "mojo",
        "run",
        "-I",
        ".",
        "cli.mojo",
        tx,
        "--tx_size",
        tx_band,
        "-r",
        rx,
        "--rx_size",
        rx_band,
        "--output_file",
        str(out_file),
    ]


def mojo_py_cmd(
    out_file: Path, tx: str, rx: str, tx_band: str, rx_band: str
) -> list[str]:
    """CPython-interop wrapper (pim_calc_py.mojo), mirroring tests/test_integration.py."""
    return [
        "uv",
        "run",
        "mojo",
        "run",
        "-I",
        ".",
        "pim_calc_py.mojo",
        tx,
        "--tx_size",
        tx_band,
        "-r",
        rx,
        "--rx_size",
        rx_band,
        "--output_file",
        str(out_file),
    ]


def compute(
    engine: str,
    tx_freqs: list[float],
    tx_bws: list[float],
    rx_freqs: list[float],
    rx_bws: list[float],
    root: Path = ROOT,
) -> dict[str, Any]:
    """Run one engine and return its JSON payload with rx_hits attached."""
    if not engine_available(engine, root):
        hint = ENGINE_HINTS.get(engine, "unknown engine")
        raise ValueError(f"{engine} unavailable: {hint}")
    if engine == "python":
        pimc = PIMCalc()
        payload: dict[str, Any] = json.loads(
            results_to_json(
                pimc.calculate(tx_freqs, tx_bws), tx_freqs, rx_freqs or None
            )
        )
    elif engine in ("go", "mojo", "mojo_py"):
        payload = _compute_subprocess(engine, tx_freqs, tx_bws, rx_freqs, rx_bws, root)
    else:
        raise ValueError(f"unknown engine: {engine}")
    for order in ("IM3", "IM5"):
        hits = rx_hits_for(payload[order], rx_freqs, rx_bws)
        for hit in hits:
            hit["order"] = order
        payload[f"{order}_rx_hits"] = hits
    payload["engine"] = engine
    return payload


def _compute_subprocess(
    engine: str,
    tx_freqs: list[float],
    tx_bws: list[float],
    rx_freqs: list[float],
    rx_bws: list[float],
    root: Path,
) -> dict[str, Any]:
    out = tempfile.NamedTemporaryFile(suffix=".json", delete=False)
    out.close()
    out_path = Path(out.name)
    tx = ",".join(str(f) for f in tx_freqs)
    rx = ",".join(str(f) for f in rx_freqs)
    try:
        if engine == "go":
            cmd = go_cmd(
                out_path,
                tx,
                ",".join(str(b) for b in tx_bws),
                rx,
                ",".join(str(b) for b in rx_bws),
                root,
            )
            cwd = root
        elif engine == "mojo_py":
            cmd = mojo_py_cmd(
                out_path,
                tx,
                rx,
                ",".join(str(b) for b in tx_bws),
                ",".join(str(b) for b in rx_bws),
            )
            cwd = root / "mojo"
        else:
            cmd = mojo_cmd(
                out_path,
                tx,
                rx,
                ",".join(str(b) for b in tx_bws),
                ",".join(str(b) for b in rx_bws),
            )
            cwd = root / "mojo"
        proc = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, check=False)
        if proc.returncode != 0:
            raise RuntimeError(f"{engine} failed:\n{proc.stdout}\n{proc.stderr}")
        return json.loads(out_path.read_text())
    finally:
        out_path.unlink(missing_ok=True)


def hump_xy(
    lo: float, hi: float, shape: np.ndarray, points: int = 124
) -> tuple[np.ndarray, np.ndarray]:
    """Sample a pseudo-carrier hump across [lo, hi] (np.interp, no scipy)."""
    x_coarse = np.linspace(lo, hi, num=len(shape))
    x = np.linspace(lo, hi, num=points)
    return x, np.interp(x, x_coarse, shape)


def chart_frame(
    payload: dict[str, Any], rx_freqs: list[float], rx_bws: list[float]
) -> pd.DataFrame:
    """Long-format frame with translucent humps for IM3/IM5 plus RX carriers."""
    rows: list[dict[str, Any]] = []
    for order in ("IM3", "IM5"):
        for r in payload[order]:
            x, y = hump_xy(r["min"], r["max"], SHAPE_IM)
            rows += [{"x": xi, "y": yi, "kind": order} for xi, yi in zip(x, y)]
    for f, bw in zip(rx_freqs, rx_bws):
        x, y = hump_xy(f - bw / 2.0, f + bw / 2.0, SHAPE_CARRIER)
        rows += [{"x": xi, "y": yi, "kind": "RX"} for xi, yi in zip(x, y)]
    return pd.DataFrame(rows)
