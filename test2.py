from testing.fnc_objects import Function, Constant
import timeit

if __name__ == "__main__":
    f1_str = "x1 * x2"
    f2_str = "F1"

    f1 = Function("f1", "x1 * x2", ["x1", "x2"])
    f2 = Function("f2", "f1 ** 2", ["x1", "x2"])

    c = Constant("c", "sin(1) + cos(0)")
    print(c)

    print(f1)
    print(f2)

    # vals = {"x1": 2, "x2": 3}
    vals = [2, 3]
    print(f1.name, "→", f1(vals))  # 6
    print(f2.name, "→", f2(vals))  # 36