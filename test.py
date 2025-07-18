from testing.inputfnc2 import InputFile
from testing.fnc_objects import Node, Function
import logging

if __name__ == "__main__":
    level = logging.DEBUG
    fmt = '[%(levelname)s] %(asctime)s %(message)s'
    logging.basicConfig(level=level, format=fmt)
    # f = InputFile("testing/381-HW#4.fnc")
    # print(f)

    funcs = {
        "F1": "F2",
        "F2": "F3 + F4",
        "F3": "G1",
        "F4": "G1",
        "G1": "F1"
    }

    real_funcs = [Function(k, v) for (k, v) in funcs.items()]
    print(real_funcs)

    first = Node("F1", None, real_funcs)
    print(first)
    print(first.find_max())
    print(first.error_exists())