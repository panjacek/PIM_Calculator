# -*- coding: utf-8 -*-
from __future__ import print_function
from PIM_Calculator.pim_calc import PIMCalc
from PIM_Calculator.pim_calc import main
import pytest
import logging
import pprint
import numpy as np
import imp, sys


@pytest.fixture
def pimc():
    return PIMCalc()

@pytest.mark.script_launch_mode('subprocess')
def test_main():
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

def test_calculate(pimc):
    tx_list = []
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
    test_im5 = np.array([1800.0, 1820.0, 1840.0, 1860.0, 1880.0, 1900.0])

    print("compare: {0} vs {1}".format(test_im3, im3[0]["IM"]))
    assert np.array_equal(test_im3, im3[0]["IM"]) is True
    assert np.array_equiv(test_im3, im3[0]["IM"]) is True
    assert np.allclose(test_im3, im3[0]["IM"]) is True
    for x, y in zip(test_im3, im3[0]["IM"]):
        print(x, y)
        assert x == y

    return
    print("compare: {0} vs {1}".format(test_im5, im5[0]["IM"]))
    assert np.array_equal(test_im5, im5[0]["IM"]) is True
    assert np.array_equiv(test_im5, im5[0]["IM"]) is True
    assert np.allclose(test_im5, im5[0]["IM"]) is True
    for x, y in zip(test_im5, im5[0]["IM"]):
        print(x, y)
        assert x == y
    print("IM calc Seems ok..")

    im3_hits = pimc.check_rx(rx_list, im3[1])
    im5_hits = pimc.check_rx(rx_list, im5[1])

    assert len(im3_hits) > 0
    assert len(im5_hits) > 0

    print(im3_hits)
    print(im5_hits)

def test_calculate_3rd_order(pimc):
    tx_list = [1840.0, 1860.0]
    tx_band = [10, 5.0]
    rx_list = [1820.0, 1900.0, 1910.0]

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
    for x in [0, 1]:
        assert np.array_equal(pim_list_3[0][x], pim_list_5[0][x]) is True
        assert np.array_equiv(pim_list_3[0][x], pim_list_5[0][x]) is True
        # check only for floats with Cf
        if x == 0:
            assert np.allclose(pim_list_3[0][x]["IM"], pim_list_5[0][x]["IM"]) is True

        for item_3, item_5 in zip(pim_list_3[0][x], pim_list_5[0][x]):
            if x == 0:
                assert item_3 == item_5
            else:
                assert np.allclose(item_3, item_5) is True
