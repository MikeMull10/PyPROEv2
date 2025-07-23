from testing.fnc_objects import Function
import timeit

if __name__ == "__main__":
    f1_str = "x1 * x2"
    f2_str = "F1"

    f1 = Function("f1", "x1 * x2", ["x1", "x2"])
    f2 = Function("f2", "f1 ** 2", ["x1", "x2"])

    print(f1)
    print(f2)

    vals = {"x1": 2, "x2": 3}
    print(f1.name, "→", f1(vals))  # 6
    print(f2.name, "→", f2(vals))  # 36