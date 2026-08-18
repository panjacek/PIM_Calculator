from python import Python


def main():
    sys = Python.import_module("sys")
    sys.path.append("./python")

    pim_calc = Python.import_module("PIM_Calculator.pim_calc")
    pim_calc.main()
