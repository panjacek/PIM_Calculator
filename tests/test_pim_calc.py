# -*- coding: utf-8 -*-

from pim_calc import PIMCalc
from pim_calc import main
import pytest
import logging
import pprint
import numpy as np

@pytest.fixture
def pimc():
    return PIMCalc()

@pytest.mark.script_launch_mode('subprocess')
def test_main():
    import imp, sys
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
    #pimc = PIMCalc()
    pim_list = pimc.calculate(tx_list)
    print type(pim_list)
    assert isinstance(pim_list, tuple) is True

    im3 = pim_list[0]
    im5 = pim_list[1]
    assert isinstance(im3, tuple) is True
    assert isinstance(im5, tuple) is True

    assert isinstance(im3[0], (np.ndarray, np.generic))
    assert isinstance(im5[0], (np.ndarray, np.generic))
    test_im3 = np.array([1820.0, 1840.0, 1860.0, 1880.0])
    test_im5 = np.array([1800.0, 1820.0, 1840.0, 1860.0, 1880.0, 1900.0])

    # logger.debug("compare: {0} vs {1}".format(test_im3, im3[0]))
    print "compare: {0} vs {1}".format(test_im3, im3[0])
    assert np.array_equal(test_im3, im3[0]) is True
    assert np.array_equiv(test_im3, im3[0]) is True
    assert np.allclose(test_im3, im3[0]) is True
    for x, y in zip(test_im3, im3[0]):
        print x, y
        assert x == y

    # logger.debug("compare: {0} vs {1}".format(test_im5, im5[0]))
    print("compare: {0} vs {1}".format(test_im5, im5[0]))
    assert np.array_equal(test_im5, im5[0]) is True
    assert np.array_equiv(test_im5, im5[0]) is True
    assert np.allclose(test_im5, im5[0]) is True
    for x, y in zip(test_im5, im5[0]):
        print x, y
        assert x == y
    print("IM calc Seems ok..")
    # logger.info("IM calc Seems ok..")

    im3_hits = pimc.check_rx(rx_list, im3[1])
    im5_hits = pimc.check_rx(rx_list, im5[1])

    assert len(im3_hits) > 0
    assert len(im5_hits) > 0

    print(im3_hits)
    print(im5_hits)
    # logger.debug(im3_hits)
    # logger.debug(im5_hits)

