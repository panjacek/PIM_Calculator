from pim_calc import default_bands, find_flag, to_py_list
from std.python import Python, PythonObject
from std.testing import (
    TestSuite,
    assert_almost_equal,
    assert_equal,
    assert_true,
)


def load_calc() raises -> PythonObject:
    var mod = Python.import_module("PIM_Calculator.pim_calc")
    return mod.PIMCalc()


def test_to_py_list() raises:
    var values = to_py_list("1900,1910")
    assert_equal(len(values), 2)
    assert_almost_equal(Float64(py=values[0]), 1900.0)
    assert_almost_equal(Float64(py=values[1]), 1910.0)


def test_to_py_list_single() raises:
    var values = to_py_list("1915")
    assert_equal(len(values), 1)
    assert_almost_equal(Float64(py=values[0]), 1915.0)


def test_default_bands() raises:
    var bands = default_bands(3)
    assert_equal(len(bands), 3)
    for i in range(3):
        assert_almost_equal(Float64(py=bands[i]), 5.0)


def test_find_flag_present() raises:
    var args = List[String](["prog", "--tx_size", "5,10", "-r", "1915"])
    assert_equal(find_flag(args, "--tx_size"), "5,10")
    assert_equal(find_flag(args, "-r"), "1915")


def test_find_flag_missing() raises:
    var args = List[String](["prog", "1900,1910"])
    assert_equal(find_flag(args, "--tx_size"), "")
    assert_equal(find_flag(args, "-r"), "")


def test_get_im3() raises:
    var calc = load_calc()
    var im = calc.get_im(Python.list(1900.0, 1910.0, 1920.0))
    assert_almost_equal(Float64(py=im), 1890.0)


def test_get_im5() raises:
    var calc = load_calc()
    var im = calc.get_im(Python.list(1900.0, 1910.0, 1920.0, 1930.0, 1940.0))
    assert_almost_equal(Float64(py=im), 1860.0)


def test_get_im_full() raises:
    var calc = load_calc()
    var full = calc.get_im_full(1900.0, 8.0)
    assert_almost_equal(Float64(py=full[0]), 1896.0)
    assert_almost_equal(Float64(py=full[1]), 1904.0)


def test_calculate_fixture() raises:
    """Same fixture as python tests: tx 1840/1860 gives IM3 [1820..1880]."""
    var calc = load_calc()
    var expected = Python.list(1820.0, 1840.0, 1860.0, 1880.0)
    var pim_list = calc.calculate(Python.list(1840.0, 1860.0))
    var im3 = pim_list[0][0]["IM"]
    assert_equal(len(im3), len(expected))
    for i in range(len(expected)):
        assert_almost_equal(Float64(py=im3[i]), Float64(py=expected[i]))


def test_calculate_max_order_3() raises:
    """Max_order=3 must leave IM5 empty."""
    var calc = load_calc()
    var pim_list = calc.calculate(
        Python.list(1840.0, 1860.0), Python.list(10.0, 5.0), 3
    )
    assert_equal(len(pim_list), 2)
    assert_equal(len(pim_list[1][0]), 0)
    assert_equal(len(pim_list[1][1]), 0)


def test_check_rx_hits() raises:
    """RX inside IM range must produce hits."""
    var calc = load_calc()
    var pim_list = calc.calculate(Python.list(1840.0, 1860.0))
    var hits = calc.check_rx(Python.list(1839.0), pim_list[0][0])
    assert_true(len(hits) > 0)


def main() raises:
    TestSuite.discover_tests[__functions_in_module()]().run()
