from testing.inputfnc2 import InputFile
from testing.fnc_objects import Node, Function, prepare_function
import logging

if __name__ == "__main__":
    level = logging.DEBUG
    fmt = '[%(levelname)s] %(asctime)s %(message)s'
    logging.basicConfig(level=level, format=fmt)

    n = 10
    function = f"iSum((x[i] - 1/sqrt({n})) ^ 2, (i, 1, {n}))"
    # print(prepare_function(function))
    # exit()

    # f = InputFile("testing/381-HW#4.fnc")
    # f = InputFile("testing/Test.fnc")
    f = InputFile("testing/ZDT1.fnc")
    print(f)

    for function in f.functions:
        if function.name == "f5":
            print(f"{function.eval({'x1': 1, 'x2': 2, 'x3': 3})=}")
            print(f"{function({'x1': 1, 'x2': 2, 'x3': 3})=}")
