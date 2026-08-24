"""Unit tests for the web engine layer (no streamlit, no browser)."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pytest

import pim_web


def _frame(freqs: list[float | None], bws: list[float]) -> pd.DataFrame:
    return pd.DataFrame({"Frequency": freqs, "Bandwidth": bws})


class TestParseRows:
    def test_basic(self) -> None:
        assert pim_web.parse_rows(_frame([1980.0, 1940.0], [5.0, 10.0])) == (
            [1980.0, 1940.0],
            [5.0, 10.0],
        )

    def test_single_carrier(self) -> None:
        assert pim_web.parse_rows(_frame([2000.0], [5.0])) == ([2000.0], [5.0])

    def test_nan_cell_raises(self) -> None:
        frame = _frame([1980.0, None], [5.0, 5.0])
        with pytest.raises(ValueError, match="Empty cells"):
            pim_web.parse_rows(frame)

    def test_empty_raises(self) -> None:
        with pytest.raises(ValueError, match="at least one"):
            pim_web.parse_rows(pd.DataFrame({"Frequency": [], "Bandwidth": []}))


class TestRxHits:
    ROWS = [
        {"cf": 1900.0, "min": 1897.5, "max": 1902.5},
        {"cf": 2100.0, "min": 2097.5, "max": 2102.5},
    ]

    def test_hit_inside_rx(self) -> None:
        hits = pim_web.rx_hits_for(self.ROWS, [1900.0], [5.0])
        assert len(hits) == 1
        assert hits[0]["cf"] == 1900.0

    def test_partial_overlap_counts(self) -> None:
        # RX band [1899.0, 1903.0] overlaps the first PIM band only.
        hits = pim_web.rx_hits_for(self.ROWS, [1901.0], [4.0])
        assert [h["cf"] for h in hits] == [1900.0]

    def test_clean_when_apart(self) -> None:
        assert pim_web.rx_hits_for(self.ROWS, [1500.0], [5.0]) == []

    def test_touching_edges_hit_inclusively(self) -> None:
        # PIM max == RX min counts as overlap (matches check_rx semantics).
        rows = [{"cf": 1800.0, "min": 1790.0, "max": 1800.0}]
        hits = pim_web.rx_hits_for(rows, [1805.0], [10.0])
        assert [h["cf"] for h in hits] == [1800.0]


class TestCommands:
    def test_go_cmd_mirrors_integration_test(self) -> None:
        cmd = pim_web.go_cmd(
            Path("/tmp/o.json"), "2152,1932", "5,5", "1752,1900", "5,5"
        )
        assert cmd == [
            str(pim_web.ROOT / "dist" / "pim_calc-go"),
            "-tx_band",
            "5,5",
            "-rx_list",
            "1752,1900",
            "-rx_band",
            "5,5",
            "-output_file",
            "/tmp/o.json",
            "2152,1932",
        ]

    def test_mojo_cmd_mirrors_integration_test(self) -> None:
        cmd = pim_web.mojo_cmd(
            Path("/tmp/o.json"), "2152,1932", "1752,1900", "5,5", "5,5"
        )
        assert cmd == [
            "uv",
            "run",
            "mojo",
            "run",
            "-I",
            ".",
            "cli.mojo",
            "2152,1932",
            "--tx_size",
            "5,5",
            "-r",
            "1752,1900",
            "--rx_size",
            "5,5",
            "--output_file",
            "/tmp/o.json",
        ]

    def test_mojo_py_cmd_mirrors_integration_test(self) -> None:
        cmd = pim_web.mojo_py_cmd(
            Path("/tmp/o.json"), "2152,1932", "1752,1900", "5,5", "5,5"
        )
        assert cmd == [
            "uv",
            "run",
            "mojo",
            "run",
            "-I",
            ".",
            "pim_calc_py.mojo",
            "2152,1932",
            "--tx_size",
            "5,5",
            "-r",
            "1752,1900",
            "--rx_size",
            "5,5",
            "--output_file",
            "/tmp/o.json",
        ]


class TestAvailability:
    def test_python_always_available(self, tmp_path: Path) -> None:
        assert pim_web.engine_available("python", tmp_path)

    def test_go_needs_binary(self, tmp_path: Path) -> None:
        assert not pim_web.engine_available("go", tmp_path)
        (tmp_path / "dist").mkdir()
        (tmp_path / "dist" / "pim_calc-go").write_text("")
        assert pim_web.engine_available("go", tmp_path)

    def test_unknown_engine_unavailable(self, tmp_path: Path) -> None:
        assert not pim_web.engine_available("fortran", tmp_path)

    def test_compute_unknown_engine_raises(self, tmp_path: Path) -> None:
        with pytest.raises(ValueError, match="unknown engine"):
            pim_web.compute("fortran", [1980.0], [5.0], [1900.0], [5.0], tmp_path)

    def test_compute_unavailable_engine_raises(self, tmp_path: Path) -> None:
        with pytest.raises(ValueError, match="unavailable"):
            pim_web.compute("go", [1980.0], [5.0], [1900.0], [5.0], tmp_path)


class TestComputePython:
    def test_payload_shape_and_hits_consistent(self) -> None:
        payload = pim_web.compute(
            "python", [1980.0, 1940.0], [5.0, 5.0], [1900.0, 1880.0], [5.0, 5.0]
        )
        assert set(payload) >= {"tx_list", "rx_list", "IM3", "IM5", "engine"}
        assert payload["engine"] == "python"
        for order in ("IM3", "IM5"):
            assert len(payload[order]) > 0
            for row in payload[order]:
                assert row["min"] <= row["cf"] <= row["max"]

    def test_attached_hits_match_overlap_math(self) -> None:
        rx_freqs, rx_bws = [1900.0, 1880.0], [5.0, 5.0]
        payload = pim_web.compute(
            "python", [1980.0, 1940.0], [5.0, 5.0], rx_freqs, rx_bws
        )
        expected = [
            {**h, "order": "IM3"}
            for h in pim_web.rx_hits_for(payload["IM3"], rx_freqs, rx_bws)
        ]
        assert payload["IM3_rx_hits"] == expected
        assert {h["order"] for h in payload["IM5_rx_hits"]} <= {"IM5"}

    def test_json_contract_known_case(self) -> None:
        payload = pim_web.compute(
            "python", [2152.0, 1932.0], [5.0, 5.0], [1752.0, 1900.0], [5.0, 5.0]
        )
        reparsed = json.loads(json.dumps(payload))
        assert {float(r["cf"]) for r in reparsed["IM3"] + reparsed["IM5"]} == {
            1492.0,
            1712.0,
            1932.0,
            2152.0,
            2372.0,
            2592.0,
        }


class TestChartFrame:
    def test_contains_all_kinds(self) -> None:
        payload = pim_web.compute(
            "python", [1980.0, 1940.0], [5.0, 5.0], [1900.0, 1880.0], [5.0, 5.0]
        )
        frame = pim_web.chart_frame(payload, [1900.0, 1880.0], [5.0, 5.0])
        assert set(frame["kind"]) == {"IM3", "IM5", "RX"}
        assert len(frame) > 0

    def test_hump_shape_bounded(self) -> None:
        x, y = pim_web.hump_xy(100.0, 110.0, pim_web.SHAPE_IM, points=50)
        assert x[0] == 100.0 and x[-1] == 110.0
        assert len(x) == len(y) == 50
        assert y.min() >= 0.0 and y.max() <= 1.0


class TestOrderTable:
    def test_hit_flag_per_row(self) -> None:
        rows = [
            {"cf": 1900.0, "min": 1897.5, "max": 1902.5},
            {"cf": 2100.0, "min": 2097.5, "max": 2102.5},
        ]
        table = pim_web.order_table(rows, pim_web.rx_hits_for(rows, [1900.0], [5.0]))
        assert list(table["RX hit"]) == [True, False]
