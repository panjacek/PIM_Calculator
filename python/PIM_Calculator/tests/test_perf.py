"""pytest-benchmark performance tests.

Run separately via `make test-perf`.
Default unit suite excludes these with `-m "not benchmark"`.
"""

import pytest

from PIM_Calculator.pim_calc import PIMCalc


def make_tx_list(n):
    """n TX carriers spaced 10 MHz apart around 1900 MHz (5 MHz channels
    stay non-overlapping)."""
    start = 1900.0 - (n // 2) * 10.0
    return [start + 10.0 * i for i in range(n)]


RX_LIST = [1800.0 + 10.0 * i for i in range(10)]


@pytest.fixture
def pimc():
    return PIMCalc()


@pytest.fixture(scope="module")
def im3_pim_table():
    """Precomputed IM3 table, built once, reused by check_rx benchmark."""
    result = PIMCalc().calculate(make_tx_list(8))
    return result[0][0]


@pytest.mark.benchmark(group="calculate-im3")
@pytest.mark.parametrize("n", [4, 8])
def test_benchmark_calculate_im3(benchmark, pimc, n):
    tx_list = make_tx_list(n)
    result = benchmark(pimc.calculate, tx_list, max_order=3)

    im3 = result[0][0]
    assert len(im3) > 0
    assert im3.dtype.names == ("IM", "IM_COMP", "IM_FULL")


@pytest.mark.benchmark(group="calculate-im5")
@pytest.mark.parametrize("n", [3, 4])
def test_benchmark_calculate_im5(benchmark, pimc, n):
    tx_list = make_tx_list(n)
    result = benchmark(pimc.calculate, tx_list)

    im5 = result[1][0]
    assert len(im5) > 0
    assert im5.dtype.names == ("IM", "IM_COMP", "IM_FULL")


@pytest.mark.benchmark(group="check_rx")
def test_benchmark_check_rx(benchmark, pimc, im3_pim_table):
    hits = benchmark(pimc.check_rx, RX_LIST, im3_pim_table)

    assert isinstance(hits, list)
