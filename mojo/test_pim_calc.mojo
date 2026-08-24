"""Pure-Mojo test suite for pim_calc.mojo (no Python interop).

Run via: uv run mojo run -I . test_pim_calc.mojo
"""

from pim_calc import (
    calculate,
    check_rx,
    check_rx_im5,
    default_bands,
    results_to_json,
)
from std.testing import (
    TestSuite,
    assert_almost_equal,
    assert_equal,
    assert_true,
)


def _tx() -> List[Float64]:
    var tx: List[Float64] = [1840.0, 1860.0]
    return tx^


def test_calculate_im3_fixture() raises:
    """Same fixture as python tests: tx 1840/1860 gives IM3 rows at
    {1820, 1840, 1860, 1880}; each product spans the SUM of three
    carrier bandwidths -> +-7.5 MHz at the 5 MHz default."""
    var result = calculate(_tx(), default_bands(2))
    assert_equal(len(result[0]), 4)
    var centres: List[Float64] = [1820.0, 1840.0, 1860.0, 1880.0]
    for i in range(4):
        assert_almost_equal(result[0][i].im, centres[i])
        assert_almost_equal(result[0][i].band_min, centres[i] - 7.5)
        assert_almost_equal(result[0][i].band_max, centres[i] + 7.5)


def test_calculate_im5_fixture() raises:
    """IM5 for the same fixture yields the six known centre frequencies
    across 10 unique source-distinguishable rows."""
    var result = calculate(_tx(), default_bands(2))
    assert_equal(len(result[1]), 10)
    var seen = Dict[Float64, Bool]()
    for i in range(len(result[1])):
        seen[result[1][i].im] = True
    for cf in [1800.0, 1820.0, 1840.0, 1860.0, 1880.0, 1900.0]:
        assert_true(cf in seen)


def test_calculate_max_order_3() raises:
    """Max_order=3 must leave IM5 empty."""
    var result = calculate(_tx(), default_bands(2), 3)
    assert_equal(len(result[1]), 0)
    assert_equal(len(result[0]), 4)


def test_bandwidth_mismatch_reuses_first() raises:
    """Mismatched bandwidth list reuses first value (python semantics):
    tx_size=[10.0] with 2 carriers -> all bands 10 -> IM3 width 30."""
    var tx: List[Float64] = [1900.0, 1910.0]
    var mismatched: List[Float64] = [10.0]
    var result = calculate(tx, mismatched, 3)
    # f_i+f_j-f_k with i<=j, k free over {1900,1910}: centres
    # 1890, 1900, 1910, 1920 -> 4 unique rows
    assert_equal(len(result[0]), 4)
    for i in range(len(result[0])):
        var lo = result[0][i].band_min
        var hi = result[0][i].band_max
        assert_almost_equal(hi - lo, 30.0)


def test_single_source_products_dropped() raises:
    """One carrier only: every product has a single distinct TX source and
    must be dropped (<2-distinct rule from python _clean_array)."""
    var single: List[Float64] = [1900.0]
    var result = calculate(single, default_bands(1))
    assert_equal(len(result[0]), 0)
    assert_equal(len(result[1]), 0)


def test_check_rx_hit() raises:
    """RX band overlapping an IM3 edge must produce exactly one hit."""
    var result = calculate(_tx(), default_bands(2))
    var rx: List[Float64] = [1839.0]
    var hits = check_rx(rx, default_bands(1), result[0])
    assert_equal(len(hits), 1)
    assert_almost_equal(hits[0].pim_min, 1832.5)
    assert_almost_equal(hits[0].pim_max, 1847.5)


def test_check_rx_no_hit() raises:
    var result = calculate(_tx(), default_bands(2))
    var rx: List[Float64] = [1700.0]
    var hits = check_rx(rx, default_bands(1), result[0])
    assert_equal(len(hits), 0)


def test_check_rx_im5_hit() raises:
    """Wide PIM band must cover the RX band and register a hit."""
    var wide_bands: List[Float64] = [100.0, 100.0]
    var result = calculate(_tx(), wide_bands)
    var rx: List[Float64] = [1850.0]
    var hits = check_rx_im5(rx, default_bands(1), result[1])
    assert_true(len(hits) > 0)


def test_dedupe_collapses_duplicates() raises:
    """Identical (cf, src, min, max) combos must collapse; distinct-source
    duplicates stay (np.unique(axis=0) semantics)."""
    var result = calculate(_tx(), default_bands(2))
    # brute-force re-check: no two records equal in output
    var im3_rows = result[0].copy()
    for i in range(len(im3_rows)):
        for j in range(i + 1, len(im3_rows)):
            assert_true(im3_rows[i] != im3_rows[j])


def test_results_to_json_contract() raises:
    """JSON string carries contract keys and row shape."""
    var result = calculate(_tx(), default_bands(2))
    var rx: List[Float64] = [1752.0]
    var payload = results_to_json(result[0], result[1], _tx(), rx)
    assert_true(payload.startswith("{"))
    assert_true(payload.endswith("}"))
    assert_true('"tx_list"' in payload)
    assert_true('"rx_list"' in payload)
    assert_true('"IM3"' in payload)
    assert_true('"IM5"' in payload)
    assert_true('"cf"' in payload)
    assert_true('"min"' in payload)
    assert_true('"max"' in payload)


def main() raises:
    TestSuite.discover_tests[__functions_in_module()]().run()
