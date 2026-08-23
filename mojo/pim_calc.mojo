from std.collections.string.string import atof
from std.python import Python, PythonObject
from std.sys import argv

comptime USAGE = """usage: mojo run pim_calc.mojo TX_LIST [--tx_size LIST] [-r RX_LIST]
                              [--rx_size LIST] [--output_file PATH]

  TX_LIST   comma separated TX carriers in MHz, e.g. 1900,1910
  --tx_size TX carrier bandwidths in MHz [5,...]
  -r        RX carriers in MHz, e.g. 1915
  --rx_size RX carrier bandwidths in MHz
  --output_file write results as JSON (same schema as python flavour)"""


def to_py_list(raw: String) raises -> PythonObject:
    """Convert '1900,1910' to a Python list of floats."""
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


def write_output(
    mod: PythonObject,
    calc: PythonObject,
    tx_list: PythonObject,
    tx_size: PythonObject,
    rx_list: PythonObject,
    path: String,
) raises:
    """Write results as JSON using the python lib's shared serializer."""
    var builtins = Python.import_module("builtins")
    var fh = builtins.open(path, "w")
    _ = fh.write(
        mod.results_to_json(calc.calculate(tx_list, tx_size), tx_list, rx_list)
    )
    _ = fh.close()


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
    var out_raw = find_flag(args, "--output_file")

    if rx_raw != "":
        var rx_list = to_py_list(rx_raw)
        var rx_size_raw = find_flag(args, "--rx_size")
        var rx_size = to_py_list(
            rx_size_raw
        ) if rx_size_raw != "" else default_bands(len(rx_list))
        var result = calc.get_results(tx_list, tx_size, rx_list, rx_size)
        var newline = PythonObject("\n")
        print(newline.join(result[0]))
        if out_raw != "":
            write_output(mod, calc, tx_list, tx_size, rx_list, out_raw)
    else:
        var result = calc.get_results(tx_list, tx_size)
        var newline = PythonObject("\n")
        print(newline.join(result[0]))
        if out_raw != "":
            write_output(mod, calc, tx_list, tx_size, Python.list(), out_raw)
