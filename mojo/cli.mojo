"""Pure-Mojo PIM calculator CLI (no Python interop).

Same interface as the wrapper flavour minus --log_lvl:
    mojo run cli.mojo TX_LIST [--tx_size LIST] [-r RX_LIST]
                [--rx_size LIST] [--output_file PATH]
"""

from pim_calc import calculate, default_bands, get_results, results_to_json
from std.collections.string.string import atof
from std.pathlib import Path
from std.sys import argv


comptime USAGE = """usage: mojo run cli.mojo TX_LIST [--tx_size LIST] [-r RX_LIST]
                             [--rx_size LIST] [--output_file PATH]

  TX_LIST   comma separated TX carriers in MHz, e.g. 1900,1910
  --tx_size TX carrier bandwidths in MHz [5,...]
  -r        RX carriers in MHz, e.g. 1915
  --rx_size RX carrier bandwidths in MHz
  --output_file write results as JSON (same schema as python flavour)"""


def find_flag(args: List[String], flag: String) -> String:
    """Return value following flag in args list, empty if absent."""
    var i = 0
    while i < len(args):
        if args[i] == flag and i + 1 < len(args):
            return args[i + 1]
        i += 1
    return ""


def parse_freq_list(raw: String) raises -> List[Float64]:
    """Convert '1900,1910' to a list of floats."""
    var result = List[Float64]()
    for part in raw.split(","):
        result.append(atof(String(part)))
    return result^


def main() raises:
    var raw_args = argv()
    var args = List[String]()
    for arg in raw_args:
        _ = args.append(String(arg))
    if len(args) < 2 or args[1] == "-h":
        print(USAGE)
        return

    var tx_list = parse_freq_list(args[1])
    var tx_raw = find_flag(args, "--tx_size")
    var tx_size = parse_freq_list(tx_raw) if tx_raw != "" else default_bands(
        len(tx_list)
    )

    var rx_raw = find_flag(args, "-r")
    if rx_raw == "":
        rx_raw = find_flag(args, "--rx_list")

    var out_path = find_flag(args, "--output_file")

    if rx_raw != "":
        var rx_list = parse_freq_list(rx_raw)
        var rx_size_raw = find_flag(args, "--rx_size")
        var rx_size = parse_freq_list(
            rx_size_raw
        ) if rx_size_raw != "" else default_bands(len(rx_list))
        for line in get_results(tx_list, tx_size, rx_list, rx_size):
            print(line)
        if out_path != "":
            var result = calculate(tx_list, tx_size)
            Path(out_path).write_text(
                results_to_json(result[0], result[1], tx_list, rx_list)
            )
    else:
        for line in get_results(
            tx_list, tx_size, List[Float64](), List[Float64]()
        ):
            print(line)
        if out_path != "":
            var result = calculate(tx_list, tx_size)
            Path(out_path).write_text(
                results_to_json(result[0], result[1], tx_list, List[Float64]())
            )
