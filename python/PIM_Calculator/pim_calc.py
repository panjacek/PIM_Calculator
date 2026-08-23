#!/usr/bin/env python

from __future__ import annotations

import argparse
import json
import logging
import os
import pprint
import sys
from collections.abc import Sequence
from itertools import cycle
from typing import Any

import numpy as np

type PimTable = np.ndarray[tuple[int, ...], np.dtype[Any]]
type FloatArray = np.ndarray[tuple[int, ...], np.dtype[np.floating[Any]]]
type ImHit = tuple[list[float], np.ndarray, np.ndarray]
type CalculateResult = tuple[tuple[PimTable, FloatArray], tuple[PimTable, FloatArray]]

IM3_TABLE_DTYPE = np.dtype(
    [("IM", float), ("IM_COMP", float, (3,)), ("IM_FULL", float, (2,))]
)
IM5_TABLE_DTYPE = np.dtype(
    [("IM", float), ("IM_COMP", float, (5,)), ("IM_FULL", float, (2,))]
)


class PIMCalc:
    """PIM calculator class"""

    logger: logging.Logger = None  # type: ignore[assignment]

    def __init__(self, **kwargs: Any) -> None:
        for k, v in kwargs.items():
            setattr(self, k, v)

        if self.logger is None:
            logging.basicConfig()
            self.logger = logging.getLogger(__name__)

        if os.getenv("USE_MOJO") == "1":
            self.logger.info("USE_MOJO=1 set: Running with Mojo acceleration engine")

    def get_im_full(self, cf: float, pim_size: float) -> list[float]:
        """Get full size if PIM"""
        return [cf - pim_size / 2.0, cf + pim_size / 2.0]

    def get_im(self, tx_list: Sequence[float]) -> float | None:
        """Calculate Center Frequency of intermodulation from given frequencies
        Args:
            tx_list: list of frequencies
        return:
            result of IM3 or IM5 calculation based on lenght of tx_list"""
        if len(tx_list) == 3:
            return tx_list[0] + tx_list[1] - tx_list[2]
        if len(tx_list) == 5:
            return tx_list[0] + tx_list[1] + tx_list[2] - tx_list[3] - tx_list[4]
        return None

    def calculate(
        self,
        tx_list: Sequence[float],
        tx_bandwith: Sequence[float] | None = None,
        max_order: int = 5,
    ) -> CalculateResult:
        """Method to calculate PIM based on list of TX carriers.

        Args:
            tx_list: list of tx carriers in MHz
            tx_bandwith: list of tx_carriers size in MHz [5MHz]
        Returns:
            im3, im5: tuple with np.arrays with calculated IM3 and IM5 PIM
        """
        logger = self.logger

        if tx_list is None or len(tx_list) < 1:
            raise TypeError

        # set default bandwith to 5MHz (LTE5)
        bands = (
            np.array([5.0 for _ in tx_list])
            if tx_bandwith is None
            else np.array(tx_bandwith, dtype=float)
        )
        if len(bands) != len(tx_list):
            logger.error("Lenght of tx_list != tx_bandwith!")
            logger.warning("Assuming all of them are same as first")
            bands = np.array([bands[0] for _ in tx_list])

        # initialize numpy arrays
        im3 = np.zeros(shape=[len(tx_list) ** 3], dtype=IM3_TABLE_DTYPE)
        im5 = np.zeros(shape=[len(tx_list) ** 5], dtype=IM5_TABLE_DTYPE)
        im3_cnt = 0
        im5_cnt = 0

        # IM center freq calc
        for i in range(len(tx_list)):
            im_order_cnt = 1
            for j in range(i, len(tx_list)):
                for k in range(len(tx_list)):
                    im_order_cnt = 3
                    im3_band_tmp = sum([bands[x] for x in [i, j, k]])
                    tx_items = [tx_list[x] for x in [i, j, k]]
                    if len(np.unique(tx_items)) > 0:
                        im3_comp_temp = np.array(tx_items)
                        self.logger.debug(f"{self.get_im(tx_items)} - {im3_comp_temp}")
                        im3[im3_cnt]["IM"] = self.get_im(tx_items)
                        im3[im3_cnt]["IM_COMP"] = im3_comp_temp
                        im3[im3_cnt]["IM_FULL"] = self.get_im_full(
                            im3[im3_cnt]["IM"], im3_band_tmp
                        )
                        im3_cnt += 1
                    # im3 = np.append(im3, [self.get_im(tx_items), im3_comp_temp])
                    if max_order <= im_order_cnt:
                        continue
                    for l in range(j, len(tx_list)):
                        for m in range(k, len(tx_list)):
                            im_order_cnt = 5
                            im5_band_tmp = sum([bands[x] for x in [i, j, k, l, m]])
                            tx_items = [tx_list[x] for x in [i, j, l, k, m]]
                            if len(np.unique(tx_items)) > 1:
                                im5_comp_temp = np.array(tx_items)
                                im5[im5_cnt]["IM"] = self.get_im(tx_items)
                                im5[im5_cnt]["IM_COMP"] = im5_comp_temp
                                im5[im5_cnt]["IM_FULL"] = self.get_im_full(
                                    im5[im5_cnt]["IM"], im5_band_tmp
                                )
                                im5_cnt += 1

        im3 = self._clean_array(im3)
        im5 = self._clean_array(im5)
        return (im3, im3["IM_FULL"]), (im5, im5["IM_FULL"])

    def _clean_array(self, input_arr: PimTable) -> PimTable:
        to_clean: list[int] = []
        self.logger.debug(pprint.pformat(input_arr))
        input_arr = np.unique(input_arr, axis=0)
        self.logger.debug(pprint.pformat(input_arr))

        for e in range(len(input_arr)):
            if len(np.unique(input_arr[e]["IM_COMP"])) < 2:
                to_clean.append(e)

        if len(to_clean) > 0:
            input_arr = np.delete(input_arr, to_clean)

        self.logger.debug(pprint.pformat(input_arr))
        self.logger.debug("====")
        return input_arr

    def _clean_arrays(
        self, im: PimTable, im_full: FloatArray
    ) -> tuple[PimTable, FloatArray]:
        # logger.error(im)
        im_full = im_full[im_full[:, 0].argsort()]
        self.logger.debug(f"IM_FULL:{pprint.pformat(im_full)}")
        self.logger.debug(im)
        self.logger.debug(im["IM"])
        im = np.unique(im, axis=0)
        # im = im[im[:, 0].argsort()]
        # im = np.array([x for x in im if len(x[1]) > 1])
        im_full = np.unique(im_full, axis=0)
        self.logger.debug("-----------------")
        self.logger.debug(im)
        self.logger.debug(f"IM_FULL:{pprint.pformat(im_full)}")
        return im, im_full

    def check_rx(
        self,
        rx_list: Sequence[float],
        pim_list: PimTable,
        rx_bandwith: Sequence[float] | None = None,
    ) -> list[ImHit]:
        """check if given rx is affected by PIM"""

        bands = (
            np.array([5 for _ in rx_list])
            if rx_bandwith is None
            else np.array(rx_bandwith, dtype=float)
        )
        if len(bands) != len(rx_list):
            self.logger.error("Lenght of rx_list != rx_bandwith!")
            self.logger.warning("Assuming all of them are same as first")
            bands = np.array([bands[0] for _ in rx_list])

        im_hits: list[ImHit] = []
        for x, x_band in zip(rx_list, bands):
            rx_min = x - x_band / 2.0
            rx_max = x + x_band / 2.0
            rx_wide = [rx_min, rx_max]
            self.logger.debug(f"RX: {rx_min}-{rx_max}")
            for e in range(len(pim_list)):
                hit = 0
                pim = pim_list[e]["IM_FULL"]
                pim_src = pim_list[e]["IM_COMP"]
                self.logger.debug(pim)
                # check fully inside
                if rx_min <= pim[0] <= rx_max:
                    hit += 1
                if rx_min <= pim[1] <= rx_max:
                    hit += 1
                # check covering from outside fully
                if pim[0] <= rx_min and pim[1] >= rx_max:
                    hit += 1

                if hit > 0:
                    msg = f"RX{rx_wide} is affected by {pim} from: {pim_src}"
                    im_hits.append((rx_wide, pim, pim_src))
                    if hit > 1:
                        msg = f"{msg} - RX fully covered by PIM"
                    self.logger.debug(msg)

        return im_hits

    def get_results(
        self,
        tx_list: Sequence[float],
        tx_bandwith: Sequence[float],
        rx_list: Sequence[float] | None = None,
        rx_bandwith: Sequence[float] | None = None,
        show_src: bool = True,
    ) -> tuple[list[str], list[tuple[str, FloatArray]], list[tuple[str, list[ImHit]]]]:
        """Wrapper to calculate PIM and check rx hits in one go
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
        text_result: list[str] = []
        im_name = cycle(["IM3", "IM5"]).__next__

        pim_result: list[tuple[str, FloatArray]] = []
        rx_result: list[tuple[str, list[ImHit]]] = []
        for im, im_full in im_result:
            name = im_name()
            self.logger.info(48 * "=")
            text_result.append(48 * "=")
            self.logger.info("PIM Cf | f min  | f max  | TX source")
            text_result.append("PIM Cf | f min  | f max  | TX source")
            for pim in range(len(im)):
                out = "{} | {} | {} | {}".format(
                    im["IM"][pim],
                    im["IM_FULL"][pim][0],
                    im["IM_FULL"][pim][1],
                    im["IM_COMP"][pim],
                )
                self.logger.info(out)
                text_result.append(out)
            self.logger.info(48 * "=")
            text_result.append(48 * "=")

            pim_result.append((name, im["IM_FULL"]))
            if rx_list is not None:
                self.logger.info("==== RX check ===")
                im_hits = self.check_rx(rx_list, im, rx_bandwith)
                if len(im_hits) > 0:
                    self.logger.warning(f"yey, we've got some {name} PIM")
                rx_result.append((f"{name} RX", im_hits))
                text_result.append(48 * "=")
                self.logger.info(48 * "=")

        for rx_res in rx_result:
            im_type = rx_res[0]
            self.logger.warning(f"===== {im_type} =====")
            text_result.append(f"===== {im_type} =====")
            for hit in rx_res[1]:
                self.logger.warning(f"{hit[0]} is inside: {hit[1]}, TX src: {hit[2]}")
                text_result.append(f"{hit[0]} is inside: {hit[1]}, TX src: {hit[2]}")

        return text_result, pim_result, rx_result


def results_to_json(
    im_result: CalculateResult,
    tx_list: Sequence[float],
    rx_list: Sequence[float] | None,
) -> str:
    """Serialize PIM calculation results to a JSON string.

    Shared output contract across the python/go/mojo flavours:

        {"tx_list": [...], "rx_list": [...],
         "im3": [{"cf": .., "min": .., "max": ..}, ...],
         "im5": [...]}

    Args:
        im_result: tuple as returned by PIMCalc.calculate()
        tx_list: List of TX carriers in MHz
        rx_list: List of RX carriers in MHz or None
    """
    im_name = cycle(["IM3", "IM5"]).__next__
    tables: dict[str, list[dict[str, float]]] = {}
    for im, im_full in im_result:
        tables[im_name()] = [
            {
                "cf": float(im["IM"][i]),
                "min": float(im_full[i][0]),
                "max": float(im_full[i][1]),
            }
            for i in range(len(im))
        ]
    payload = {
        "tx_list": [float(x) for x in tx_list],
        "rx_list": [float(x) for x in rx_list] if rx_list is not None else [],
        **tables,
    }
    return json.dumps(payload, indent=2)


def _parse_freq_list(raw: str) -> list[float]:
    """Parse a comma-separated CLI frequency/bandwidth list into floats."""
    return [float(x) for x in raw.strip().split(",")] if "," in raw else [float(raw)]


def read_args() -> dict[str, Any]:
    """Method to parse the given arguments

    Returns:
        dictionary with the values given by the CLI
    """

    # read CLI args
    parser = argparse.ArgumentParser()
    parser.add_argument("tx_list", help="List of TX Carriers", default="1980,1940")
    parser.add_argument(
        "--tx_size", dest="tx_size", help="List of TX Carriers bands [5MHz]"
    )
    parser.add_argument("-r", "--rx_list", help="List of RX Carriers")
    parser.add_argument(
        "--rx_size", dest="rx_size", help="List of RX Carriers bands [5MHz]"
    )
    parser.add_argument(
        "--output_file",
        dest="output_file",
        help="Write results table to this file",
    )
    parser.add_argument(
        "--log_lvl",
        dest="log_lvl",
        help="logger level to display [INFO]",
        default="INFO",
    )

    # args, leftovers = parser.parse_known_args()
    args = parser.parse_args()

    tx_list: list[float] = _parse_freq_list(args.tx_list)

    rx_list: list[float] | None = None
    if args.rx_list is not None:
        rx_list = _parse_freq_list(args.rx_list)

    tx_size: list[float]
    if args.tx_size is None:
        tx_size = [5.0 for _ in tx_list]
    else:
        tx_size = _parse_freq_list(args.tx_size)

    rx_size: list[float] | None = None
    if rx_list is not None:
        if args.rx_size is None:
            rx_size = [5.0 for _ in rx_list]
        else:
            rx_size = _parse_freq_list(args.rx_size)

    setup_dict = {
        "tx_list": tx_list,
        "tx_size": tx_size,
        "rx_list": rx_list,
        "rx_size": rx_size,
        "log_lvl": args.log_lvl,
        "output_file": args.output_file,
    }

    return setup_dict


def main() -> None:
    setup_dict = read_args()

    # setup logger
    console = logging.StreamHandler()
    console.setLevel(setup_dict["log_lvl"])
    logger = logging.getLogger(__name__)
    logger.addHandler(console)
    logger.setLevel("DEBUG")

    logger.info("==== PIM CALCULATOR: CLI MODE ====")
    pimc = PIMCalc(logger=logger)

    tx_list = setup_dict["tx_list"]
    rx_list = setup_dict["rx_list"]
    tx_size = setup_dict["tx_size"]
    rx_size = setup_dict["rx_size"]

    logger.info(f"Using TX Carriers:{tx_list}")
    logger.info(f"Using RX Carriers:{tx_size}")
    logger.info(f"Using RX Carriers:{rx_list}")
    logger.info(f"Using RX Carriers:{rx_size}")

    _text_result, _pim_result, _rx_result = pimc.get_results(
        tx_list, tx_size, rx_list, rx_size
    )

    if setup_dict["output_file"]:
        with open(setup_dict["output_file"], "w") as fh:
            fh.write(
                results_to_json(pimc.calculate(tx_list, tx_size), tx_list, rx_list)
                + "\n"
            )

    sys.exit(0)


if __name__ == "__main__":
    main()
