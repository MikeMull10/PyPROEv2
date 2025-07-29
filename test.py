from testing.inputfnc2 import InputFile
from testing.fnc_objects import Node, Function
import logging

if __name__ == "__main__":
    level = logging.DEBUG
    fmt = '[%(levelname)s] %(asctime)s %(message)s'
    logging.basicConfig(level=level, format=fmt)
    # f = InputFile("testing/381-HW#4.fnc")
    f = InputFile("testing/Test.fnc")
    print(f)

    for function in f.functions:
        if function.name == "f4":
            print(f"{function.fast_eval({'x1': 1, 'x2': 2, 'x3': 3})=}")
