from std.collections.string.string import atof
from std.python import Python, PythonObject
from std.sys import argv

comptime USAGE = """usage: mojo run pim_calc.mojo TX_LIST [--tx_size LIST] [-r RX_LIST]
                              [--rx_size LIST]

  TX_LIST   comma separated TX carriers in MHz, e.g. 1900,1910
  --tx_size TX carrier bandwidths in MHz [5,...]
  -r        RX carriers in MHz, e.g. 1915
  --rx_size RX carrier bandwidths in MHz"""


def to_py_list(raw: String) raises -> PythonObject:
    """'1900,1910' -> Python list of floats"""
    var result = Python.list()
    for part in raw.split(","):
        _ = result.append(atof(String(part)))
    return result


def default_bands(count: Int) raises -> PythonObject:
    """Default bandwidth list of 5 MHz entries."""
    var result = Python.list()
    for _ in range(count):
        _ = result.append(5.0)
    return result


def find_flag(args: List[String], flag: String) -> String:
    """Return value following flag in args list, empty if absent."""
    var i = 0
    while i < len(args):
        if args[i] == flag and i + 1 < len(args):
            return args[i + 1]
        i += 1
    return ""


def main() raises:
    var raw_args = argv()
    var args = List[String]()
    for arg in raw_args:
        _ = args.append(String(arg))
    if len(args) < 2 or args[1] == "-h":
        print(USAGE)
        return

    Python.add_to_path("../python")
    var mod = Python.import_module("PIM_Calculator.pim_calc")

    var tx_list = to_py_list(args[1])
    var tx_raw = find_flag(args, "--tx_size")
    var tx_size = to_py_list(tx_raw) if tx_raw != "" else default_bands(
        len(tx_list)
    )

    var rx_raw = find_flag(args, "-r")
    if rx_raw == "":
        rx_raw = find_flag(args, "--rx_list")

    var calc = mod.PIMCalc()

    if rx_raw != "":
        var rx_list = to_py_list(rx_raw)
        var rx_size_raw = find_flag(args, "--rx_size")
        var rx_size = to_py_list(
            rx_size_raw
        ) if rx_size_raw != "" else default_bands(len(rx_list))
        var result = calc.get_results(tx_list, tx_size, rx_list, rx_size)
        var newline = PythonObject("\n")
        print(newline.join(result[0]))
    else:
        var result = calc.get_results(tx_list, tx_size)
        var newline = PythonObject("\n")
        print(newline.join(result[0]))
