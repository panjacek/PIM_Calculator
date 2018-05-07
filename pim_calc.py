# -*- coding: utf-8 -*-

import logging
import pprint
import numpy as np
from itertools import cycle


class PIMCalc:
    """ PIM calculator class """
    logger = None

    def __init__(self, **kwargs):
        for k, v in kwargs.iteritems():
            setattr(self, k, v)

        if self.logger is None:
            self.logger = logging.getLogger("test_executor")

    def calculate(self, tx_list, tx_bandwith=None, max_order=5):
        """ Method to calculate PIM based on list of TX carriers.

        Args:
            tx_list: list of tx carriers in MHz
            tx_bandwith: list of tx_carriers size in MHz [5MHz]
        Returns:
            im3, im5: tuple with np.arrays with calculated IM3 and IM5 PIM
        """
        logger = self.logger

        # set default bandwith to 5MHz (LTE5)
        if tx_bandwith is None:
            tx_bandwith = np.array([5 for x in tx_list])

        if len(tx_bandwith) != len(tx_list):
            logger.error("Lenght of tx_list != tx_bandwith!")
            logger.warning("Assuming all of them are same as first")
            tx_bandwith = np.array([tx_bandwith[0] for x in tx_list])

        tx_enum = range(0, len(tx_list))

        # initialize numpy arrays
        im3 = np.array([])
        im5 = np.array([])
        im3_band = np.array([])
        im5_band = np.array([])

        # IM center freq calc
        for i in tx_enum:
            im_order_cnt = 1
            for j in tx_enum:
                for k in tx_enum:
                    im_order_cnt = 3
                    im3 = np.append(im3, tx_list[i] + tx_list[j] - tx_list[k])
                    im3_band_tmp = tx_bandwith[i] + tx_bandwith[j] + tx_bandwith[k]
                    im3_band = np.append(im3_band, im3_band_tmp)
                    if max_order <= im_order_cnt:
                        continue
                    for l in tx_enum:
                        for m in tx_enum:
                            im5 = np.append(
                                    im5,
                                    tx_list[i] +
                                    tx_list[j] +
                                    tx_list[k] -
                                    tx_list[l] -
                                    tx_list[m])
                            im5_band = np.append(
                                    im5_band,
                                    im3_band +
                                    tx_bandwith[l] +
                                    tx_bandwith[m])

        im3_full = np.empty(shape=[len(im3), 2])
        im5_full = np.empty(shape=[len(im5), 2])
        # IM min and max array, IM5 will always be longer..
        im_full_enum = range(0, len(im5)) if len(im5) != 0 else len(im3)
        # IM f0 - band, f0 + band
        for i in im_full_enum:
            if i < len(im3):
                im_tmp = [im3[i] - im3_band[i]/2.0, im3[i] + im3_band[i]/2.0]
                # logger.info(im_tmp)
                im3_full[i] = im_tmp
            if max_order == 5:
                im_tmp = [im5[i] - im5_band[i]/2.0, im5[i] + im5_band[i]/2.0]
                # logger.info(im_tmp)
                im5_full[i] = im_tmp

        im3, im3_full = self._clean_arrays(im3, im3_full)
        im5, im5_full = self._clean_arrays(im5, im5_full)
        return (im3, im3_full), (im5, im5_full)

    def _clean_arrays(self, im, im_full):
        # logger.error(im)
        im_full = im_full[im_full[:, 0].argsort()]
        # logger.debug("IM_FULL:{0}".format(pprint.pformat(im_full)))
        # logger.debug("sorting...")
        # logger.debug(im)
        im = np.sort(np.unique(im))
        im_full = np.unique(im_full, axis=0)
        # logger.warning(len(im))
        # logger.debug(im)
        # logger.debug("IM_FULL:{0}".format(pprint.pformat(im_full)))
        return im, im_full

    def check_rx(self, rx_list, pim_list, rx_bandwith=None):
        """ check if given rx is affected by PIM """

        if rx_bandwith is None:
            rx_bandwith = [5 for x in rx_list]

        if len(rx_bandwith) != len(rx_list):
            logger.error("Lenght of rx_list != rx_bandwith!")
            logger.warning("Assuming all of them are same as first")
            rx_bandwith = np.array([rx_bandwith[0] for x in tx_list])

        im_hits = []
        for x, x_band in zip(rx_list, rx_bandwith):
            rx_min = x - x_band/2.0
            rx_max = x + x_band/2.0
            rx_wide = [rx_min, rx_max]
            self.logger.debug(rx_min)
            self.logger.debug(rx_max)
            for pim in pim_list:
                hit = 0
                self.logger.debug(pim)
                if pim[0] <= rx_min <= pim[1]:
                    hit += 1
                if pim[0] <= rx_max <= pim[1]:
                    hit += 1

                if hit > 0:
                    msg = "RX{0} is affected by {1}".format(rx_wide, pim)
                    im_hits.append((rx_wide, pim))
                    if hit == 2:
                        msg = "".join([msg, " - RX fully covered by PIM"])
                    self.logger.debug(msg)

        return im_hits

    def get_results(self, tx_list, tx_bandwith, rx_list=None, rx_bandwith=None):
        """ Wrapper to calculate PIM and check rx hits in one go
        Args:
            tx_list: List of TX carriers in MHz
            tx_bandwith: List of TX carrier Bandwidth in MHz
            rx_list: List of RX carriers in MHz
            rx_bandwith: List of RX carrier Bandwidth in MHz
        Returns:
            tuple with the following items:
            text_result: text results are produced by the script
            pim_result: tuple with IM name and intermodulation ranges
            rx_result: tuple with IM name and RX hits
        """

        im_result = self.calculate(tx_list, tx_bandwith)
        text_result = []
        im_name = cycle(["IM3", "IM5"]).next

        pim_result = []
        rx_result = []
        for im, im_full in im_result:
            name = im_name()
            self.logger.info(48*"=")
            self.logger.info(im)
            self.logger.info("==== {0}:fmin, fmax ====".format(name))
            self.logger.info(im_full)
            self.logger.info(48*"=")
            text_result.append(48*"=")
            text_result.append("==== {0} ====".format(name))
            text_result.append(str(im))
            text_result.append("==== {0}:fmin, fmax ====".format(name))
            text_result.append(str(im_full))
            text_result.append(48*"=")

            pim_result.append((name, im_full))
            if rx_list is not None:
                self.logger.info("==== RX check ===")
                im_hits = self.check_rx(rx_list, im_full, rx_bandwith)
                if len(im_hits) > 0:
                    self.logger.warning("yey, we've got some {0} PIM".format(name))
                rx_result.append(("{} RX".format(name), im_hits))
                text_result.append(48*"=")
                self.logger.info(48*"=")

        for rx_res in rx_result:
            im_type = rx_res[0]
            self.logger.warning("===== {0} =====".format(im_type))
            text_result.append("===== {0} =====".format(im_type))
            for pim in rx_res[1]:
                self.logger.warning("{0} is inside: {1}".format(pim[0], pim[1]))
                text_result.append("{0} is inside: {1}".format(pim[0], pim[1]))

        return text_result, pim_result, rx_result



# I DONT LIKE UNIT TESTS...
def test_me(logger):
    tx_list = [1840.0, 1860.0]
    rx_list = [1820.0, 1900.0, 1910.0]
    pim_list = pimc.calculate(tx_list)
    logger.debug(type(pim_list))
    assert isinstance(pim_list, tuple) is True

    im3 = pim_list[0]
    im5 = pim_list[1]
    assert isinstance(im3, tuple) is True
    assert isinstance(im5, tuple) is True

    assert isinstance(im3[0], (np.ndarray, np.generic))
    assert isinstance(im5[0], (np.ndarray, np.generic))
    test_im3 = np.array([1820.0, 1840.0, 1860.0, 1880.0])
    test_im5 = np.array([1800.0, 1820.0, 1840.0, 1860.0, 1880.0, 1900.0])

    logger.debug("compare: {0} vs {1}".format(test_im3, im3[0]))
    assert np.array_equal(test_im3, im3[0]) is True
    assert np.array_equiv(test_im3, im3[0]) is True
    assert np.allclose(test_im3, im3[0]) is True
    for x, y in zip(test_im3, im3[0]):
        print x, y
        assert x == y

    logger.debug("compare: {0} vs {1}".format(test_im5, im5[0]))
    assert np.array_equal(test_im5, im5[0]) is True
    assert np.array_equiv(test_im5, im5[0]) is True
    assert np.allclose(test_im5, im5[0]) is True
    for x, y in zip(test_im5, im5[0]):
        print x, y
        assert x == y
    logger.info("IM calc Seems ok..")

    im3_hits = pimc.check_rx(rx_list, im3[1])
    im5_hits = pimc.check_rx(rx_list, im5[1])

    assert len(im3_hits) > 0
    assert len(im5_hits) > 0

    logger.debug(im3_hits)
    logger.debug(im5_hits)


def read_args():
    """ Method to parse the given arguments

    Returns:
        dictionary with the values given by the CLI
    """

    # read CLI args
    parser = argparse.ArgumentParser()
    parser.add_argument("tx_list", help="List of TX Carriers", default="1980,1940")
    parser.add_argument("--tx_size", dest="tx_size", help="List of TX Carriers bands [5MHz]")
    parser.add_argument("-r", "--rx_list", help="List of RX Carriers")
    parser.add_argument("--rx_size", dest="rx_size", help="List of RX Carriers bands [5MHz]")
    parser.add_argument("--log_lvl", dest="log_lvl",
                        help="logger level to display [INFO]", default="INFO")
    parser.add_argument("--test_me", help="flag for self test [False]", action="store_true")

    # args, leftovers = parser.parse_known_args()
    args = parser.parse_args()

    tx_list = None
    if args.tx_list is None:
        print "No TX list is given, How can I calculate PIM ?????"
        parser.print_help()
        raise TypeError

    tx_list = args.tx_list
    if "," in tx_list:
        tx_list = [float(x) for x in tx_list.strip().split(",")]
    else:
        tx_list = [float(tx_list)]

    rx_list = None
    if args.rx_list is not None:
        rx_list = args.rx_list
        if "," in rx_list:
            rx_list = [float(x) for x in rx_list.strip().split(",")]
        else:
            rx_list = [float(rx_list)]

    tx_size = None
    if args.tx_size is None:
        tx_size = [5.0 for x in range(0, len(tx_list))]
    else:
        tx_size = [float(x) for x in args.tx_size.strip().split(",")]

    rx_size = None
    if rx_list is not None:
        if args.rx_size is None:
            rx_size = [5.0 for x in range(0, len(rx_list))]
        else:
            rx_size = [float(x) for x in args.rx_size.strip().split(",")]

    if args.test_me is not None:
        args.log_level = "DEBUG"

    setup_dict = {
            "test_me": args.test_me,
            "tx_list": tx_list,
            "tx_size": tx_size,
            "rx_list": rx_list,
            "rx_size": rx_size,
            "log_lvl": args.log_lvl
        }

    return setup_dict


if __name__ == "__main__":
    import sys
    import argparse

    setup_dict = read_args()

    # setup logger
    console = logging.StreamHandler()
    console.setLevel(setup_dict["log_lvl"])
    logger = logging.getLogger("test_executor")
    logger.addHandler(console)
    logger.setLevel("DEBUG")

    logger.info("==== PIM CALCULATOR: CLI MODE ====")
    pimc = PIMCalc(logger=logger)

    if setup_dict["test_me"]:
        logger.setLevel("DEBUG")
        test_me(logger)
        sys.exit(0)

    tx_list = setup_dict["tx_list"]
    rx_list = setup_dict["rx_list"]
    tx_size = setup_dict["tx_size"]
    rx_size = setup_dict["rx_size"]

    logger.info("Using TX Carriers:{0}".format(tx_list))
    logger.info("Using RX Carriers:{0}".format(tx_size))
    logger.info("Using RX Carriers:{0}".format(rx_list))
    logger.info("Using RX Carriers:{0}".format(rx_size))

    im_name = cycle(["IM3", "IM5"]).next
    im_result = pimc.calculate(tx_list, tx_bandwith=tx_size)
    rx_result = []
    for im, im_full in im_result:
        logger.info(48*"=")
        name = im_name()
        logger.info("==== {0} ====".format(name))
        logger.info(im)
        logger.info("==== {0}:fmin, fmax ====".format(name))
        logger.info(im_full)
        logger.info(48*"=")
        if rx_list is not None:
            logger.info("==== RX check ===")
            im_hits = pimc.check_rx(rx_list, im_full, rx_bandwith=rx_size)
            if len(im_hits) > 0:
                logger.warning("yey, we've got some {0} PIM".format(name))
            rx_result.append((name, im_hits))
            logger.info(48*"=")

    if rx_list is None:
        sys.exit()

    for rx_res in rx_result:
        im_type = rx_res[0]
        logger.warning("===== {0} =====".format(im_type))
        for pim in rx_res[1]:
            logger.warning("{0} is inside: {1}".format(pim[0], pim[1]))

