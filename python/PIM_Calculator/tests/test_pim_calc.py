from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pytest

from PIM_Calculator.pim_calc import PIMCalc, main, results_to_json


@pytest.fixture
def pimc() -> PIMCalc:
    return PIMCalc()


def test_main() -> None:
    sys.argv = ["pim_calc.py", "--help"]
    with pytest.raises(SystemExit):
        main()

    sys.argv = ["pim_calc.py"]
    with pytest.raises(SystemExit):
        main()

    sys.argv = ["pim_calc.py", "1900"]
    with pytest.raises(SystemExit):
        main()

    sys.argv = ["pim_calc.py", "2152,1932"]
    with pytest.raises(SystemExit):
        main()

    sys.argv = ["pim_calc.py", "2152,1932", "--tx_size=5,10"]
    with pytest.raises(SystemExit):
        main()

    sys.argv = ["pim_calc.py", "2152,1932", "--tx_size=5"]
    with pytest.raises(SystemExit):
        main()

    sys.argv = ["pim_calc.py", "1980,1932", "--rx_list=1752", "--rx_size=5,10"]
    with pytest.raises(SystemExit):
        main()

    sys.argv = ["pim_calc.py", "2152,1932", "--rx_list=1752,1900", "--rx_size=5,10"]
    with pytest.raises(SystemExit):
        main()

    sys.argv = ["pim_calc.py", "2152,1932", "--rx_list=1752,1900"]
    with pytest.raises(SystemExit):
        main()

    sys.argv = ["pim_calc.py", "1940,1980", "--rx_list=1752,1900"]
    with pytest.raises(SystemExit):
        main()


def test_calculate(pimc: PIMCalc) -> None:
    tx_list: list[float] = []
    with pytest.raises(TypeError):
        pim_list = pimc.calculate(tx_list)

    tx_list = [1840.0, 1860.0]
    rx_list = [1820.0, 1900.0, 1910.0]

    pim_list = pimc.calculate(tx_list)
    print(type(pim_list))
    assert isinstance(pim_list, tuple) is True

    im3 = pim_list[0]
    im5 = pim_list[1]
    assert isinstance(im3, tuple) is True
    assert isinstance(im5, tuple) is True

    assert isinstance(im3[0], (np.ndarray, np.generic))
    assert isinstance(im5[0], (np.ndarray, np.generic))
    test_im3 = np.array([1820.0, 1840.0, 1860.0, 1880.0])
    test_im5 = np.array(
        [1800.0, 1820.0, 1820.0, 1840.0, 1840.0, 1860.0, 1860.0, 1880.0, 1880.0, 1900.0]
    )

    # IM5 rows keep duplicate centre frequencies when the TX source
    # components differ (np.unique over the full structured row).
    assert np.allclose(test_im3, im3[0]["IM"]) is True
    assert np.allclose(test_im5, im5[0]["IM"]) is True

    im3_hits = pimc.check_rx(rx_list, im3[0])
    im5_hits = pimc.check_rx(rx_list, im5[0])

    assert len(im3_hits) == 1
    assert len(im5_hits) == 4


def test_calculate_3rd_order(pimc: PIMCalc) -> None:
    tx_list = [1840.0, 1860.0]
    tx_band = [10, 5.0]

    pim_list_5 = pimc.calculate(tx_list, tx_band, max_order=5)
    assert len(pim_list_5) == 2
    assert len(pim_list_5[1]) == 2
    assert len(pim_list_5[1][0]) > 0
    assert len(pim_list_5[1][1]) > 0

    pim_list_3 = pimc.calculate(tx_list, tx_band, max_order=3)
    assert len(pim_list_3) == 2
    assert len(pim_list_3[0]) == 2
    assert len(pim_list_3[0][0]) > 0
    assert len(pim_list_3[0][1]) > 0

    # check that 5th order items are empty
    assert len(pim_list_3[1]) == 2
    assert len(pim_list_3[1][0]) == 0
    assert len(pim_list_3[1][1]) == 0

    # compare pim3 with pim3 from two calculations
    im3_table_3 = pim_list_3[0][0]
    im3_table_5 = pim_list_5[0][0]
    for x in [0, 1]:
        assert np.array_equal(pim_list_3[0][x], pim_list_5[0][x]) is True
        # check only for floats with Cf
        if x == 0:
            assert np.allclose(im3_table_3["IM"], im3_table_5["IM"]) is True


def test_calculate_bandwidth_mismatch_fallback(pimc: PIMCalc) -> None:
    """Short bandwidth list: every carrier falls back to the first value."""
    pim_list = pimc.calculate([1840.0, 1860.0, 1880.0], [5.0])
    (im3, im3_full), _ = pim_list

    assert len(im3) > 0
    for i in range(len(im3)):
        width = im3_full[i][1] - im3_full[i][0]
        assert np.allclose(width, 15.0)  # 3 carriers x 5.0 MHz


def test_check_rx_bandwidth_mismatch_fallback(pimc: PIMCalc) -> None:
    """Short rx bandwidth list behaves like the uniform single-band call."""
    (im3, _), _ = pimc.calculate([1840.0, 1860.0])
    rx_list = [1820.0, 1900.0]

    fallback = pimc.check_rx(rx_list, im3, [5.0])
    reference = pimc.check_rx(rx_list, im3, [5.0, 5.0])
    assert len(fallback) == len(reference) > 0


def test_results_to_json_round_trip(pimc: PIMCalc) -> None:
    """JSON contract keys and row shape survive a json.loads round trip."""
    pim_list = pimc.calculate([2152.0, 1932.0])
    payload = json.loads(results_to_json(pim_list, [2152.0, 1932.0], None))

    assert set(payload) == {"tx_list", "rx_list", "IM3", "IM5"}
    assert payload["tx_list"] == [2152.0, 1932.0]
    assert payload["rx_list"] == []

    for order in ("IM3", "IM5"):
        for row in payload[order]:
            assert set(row) == {"cf", "min", "max"}
            assert all(isinstance(v, float) for v in row.values())

    assert len(payload["IM3"]) == len(pim_list[0][0])
    assert len(payload["IM5"]) == len(pim_list[1][0])


def test_main_cli_writes_output_file(
    pimc: PIMCalc, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    out_file = tmp_path / "out.json"
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "PIM_Calculator",
            "2152,1932",
            "--rx_list=1752,1900",
            f"--output_file={out_file}",
        ],
    )
    with pytest.raises(SystemExit) as excinfo:
        main()
    assert excinfo.value.code == 0

    payload = json.loads(out_file.read_text())
    assert set(payload) == {"tx_list", "rx_list", "IM3", "IM5"}
    assert payload["rx_list"] == [1752.0, 1900.0]
